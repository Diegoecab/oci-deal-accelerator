#!/usr/bin/env python3
"""
Refresh the bundled OCI_Icons.pptx asset and regenerate its structured index.

The generated files are:
- kb/diagram/oci-pptx-icons-manifest.yaml
- kb/diagram/oci-pptx-icons-index.json

The index intentionally stores stable references to shapes inside the deck
instead of raw XML snippets. This keeps the index compact and lets future
renderers re-extract the exact shape block from the source deck.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "pptx-icon-library.yaml"

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"p": P_NS, "a": A_NS, "r": R_NS}
SHAPE_TAGS = {"sp", "grpSp", "cxnSp", "pic"}


def _project_path(value: str) -> Path:
    path = Path(os.path.expanduser(value))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _flatten_text(shape: ET.Element) -> list[str]:
    values = []
    for node in shape.findall(".//a:t", NS):
        text = (node.text or "").strip()
        if text:
            values.append(text)
    return values


def _joined_text(lines: list[str]) -> str:
    return " | ".join(lines)


def _extract_bbox(shape: ET.Element) -> dict[str, int] | None:
    xfrm = shape.find(".//a:xfrm", NS)
    if xfrm is None:
        return None
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    out: dict[str, int] = {}
    for attr, key in (("x", "x"), ("y", "y")):
        value = off.attrib.get(attr)
        if value is not None:
            out[key] = int(value)
    for attr, key in (("cx", "cx"), ("cy", "cy")):
        value = ext.attrib.get(attr)
        if value is not None:
            out[key] = int(value)
    return out or None


def _shape_identity(shape: ET.Element) -> tuple[str | None, str | None]:
    c_nv_pr = shape.find(".//p:cNvPr", NS)
    if c_nv_pr is None:
        return None, None
    return c_nv_pr.attrib.get("id"), c_nv_pr.attrib.get("name")


def _shape_record(shape: ET.Element, child_index: int, node_path: list[int] | None = None) -> dict[str, Any]:
    shape_id, shape_name = _shape_identity(shape)
    lines = _flatten_text(shape)
    shape_xml = ET.tostring(shape, encoding="utf-8")
    return {
        "child_index": child_index,
        "node_path": list(node_path or [child_index]),
        "shape_id": int(shape_id) if shape_id and shape_id.isdigit() else shape_id,
        "shape_name": shape_name,
        "tag": _local_name(shape.tag),
        "text_lines": lines,
        "text": _joined_text(lines),
        "bbox": _extract_bbox(shape),
        "block_sha256": _sha256_bytes(shape_xml),
    }


def _shape_ref(slide: dict[str, Any], shape: dict[str, Any]) -> dict[str, Any]:
    return {
        "display_number": slide["display_number"],
        "slide_path": slide["slide_path"],
        "title": slide["title"],
        "shape_id": shape["shape_id"],
        "shape_name": shape["shape_name"],
        "child_index": shape["child_index"],
        "node_path": shape.get("node_path") or [shape["child_index"]],
        "tag": shape["tag"],
        "text": shape["text"],
        "bbox": shape["bbox"],
        "block_sha256": shape["block_sha256"],
    }


def _top_colors(xml_bytes: bytes, limit: int = 12) -> list[dict[str, Any]]:
    counter = Counter()
    for elem in ET.fromstring(xml_bytes).findall(".//a:srgbClr", NS):
        value = elem.attrib.get("val")
        if value:
            counter[value.upper()] += 1
    return [{"hex": color, "count": count} for color, count in counter.most_common(limit)]


def _collect_nested_library_shapes(shape: ET.Element, node_path: list[int], out: list[dict[str, Any]]) -> None:
    children = list(shape)
    for child_offset, child in enumerate(children):
        if _local_name(child.tag) not in SHAPE_TAGS:
            continue
        child_path = [*node_path, child_offset]
        record = _shape_record(child, node_path[0], child_path)
        if record.get("text_lines"):
            out.append(record)
        _collect_nested_library_shapes(child, child_path, out)


def inspect_pptx(pptx_path: Path) -> dict[str, Any]:
    slides: list[dict[str, Any]] = []
    with zipfile.ZipFile(pptx_path) as archive:
        presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
        relationships = ET.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))
        rel_map = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in relationships.findall("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
        }
        slide_ids = presentation.find("p:sldIdLst", NS)
        if slide_ids is None:
            raise RuntimeError("ppt/presentation.xml has no slide list")

        for display_number, slide_id in enumerate(slide_ids.findall("p:sldId", NS), start=1):
            rel_id = slide_id.attrib.get(f"{{{R_NS}}}id")
            target = rel_map.get(rel_id or "")
            if not target:
                continue
            slide_path = f"ppt/{target}"
            xml_bytes = archive.read(slide_path)
            root = ET.fromstring(xml_bytes)
            sp_tree = root.find(".//p:spTree", NS)
            if sp_tree is None:
                continue
            shapes = []
            library_shapes = []
            for child_index, child in enumerate(list(sp_tree)):
                if _local_name(child.tag) not in SHAPE_TAGS:
                    continue
                record = _shape_record(child, child_index, [child_index])
                shapes.append(record)
                if record.get("text_lines"):
                    library_shapes.append(record)
                _collect_nested_library_shapes(child, [child_index], library_shapes)
            slide_text = []
            for shape in shapes:
                slide_text.extend(shape["text_lines"])
            title = ""
            for shape in shapes:
                if shape["shape_name"] and "title" in shape["shape_name"].lower() and shape["text_lines"]:
                    title = " ".join(shape["text_lines"])
                    break
            if not title and slide_text:
                title = slide_text[0]
            slides.append(
                {
                    "display_number": display_number,
                    "slide_path": slide_path,
                    "title": title,
                    "text_lines": slide_text,
                    "text_sample": _joined_text(slide_text[:24]),
                    "shape_counts": dict(Counter(shape["tag"] for shape in shapes)),
                    "shape_count": len(shapes),
                    "colors": _top_colors(xml_bytes),
                    "slide_sha256": _sha256_bytes(xml_bytes),
                    "shapes": shapes,
                    "library_shapes": library_shapes,
                }
            )

    return {
        "slide_count": len(slides),
        "slides": slides,
    }


def _normalize_text(text: str) -> str:
    cleaned = []
    for char in text.lower():
        cleaned.append(char if char.isalnum() else " ")
    return " ".join("".join(cleaned).split())


def _slide_matches(slide: dict[str, Any], markers: dict[str, Any]) -> bool:
    title = _normalize_text(slide.get("title", ""))
    text = _normalize_text(slide.get("text_sample", ""))
    title_contains = markers.get("title_contains")
    if title_contains and _normalize_text(str(title_contains)) not in title:
        return False
    for phrase in markers.get("all_text", []) or []:
        if _normalize_text(str(phrase)) not in text:
            return False
    any_text = markers.get("any_text", []) or []
    if any_text and not any(_normalize_text(str(phrase)) in text for phrase in any_text):
        return False
    return True


def detect_semantic_slides(slides: list[dict[str, Any]], config: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    semantic_slides: dict[str, Any] = {}
    warnings: list[str] = []
    for key, markers in (config.get("semantic_markers") or {}).items():
        match = next((slide for slide in slides if _slide_matches(slide, markers or {})), None)
        if match is None:
            warnings.append(f"Semantic slide '{key}' was not detected.")
            continue
        semantic_slides[key] = {
            "display_number": match["display_number"],
            "slide_path": match["slide_path"],
            "title": match["title"],
            "slide_sha256": match["slide_sha256"],
            "text_sample": match["text_sample"],
        }
    return semantic_slides, warnings


def _first_shape_with_text(slide: dict[str, Any], expected_text: str) -> dict[str, Any] | None:
    expected = _normalize_text(expected_text)
    for shape in slide["shapes"]:
        text = _normalize_text(shape.get("text", ""))
        if text == expected:
            return shape
    for shape in slide["shapes"]:
        text = _normalize_text(shape.get("text", ""))
        if expected and expected in text:
            return shape
    return None


def _slug(text: str) -> str:
    chars = []
    for ch in text.lower():
        if ch.isalnum():
            chars.append(ch)
        else:
            chars.append("_")
    return "_".join(part for part in "".join(chars).split("_") if part)


def _grouping_refs(slide: dict[str, Any], labels: list[str]) -> dict[str, Any]:
    refs: dict[str, Any] = {}
    for label in labels:
        shape = _first_shape_with_text(slide, label)
        if shape is not None:
            refs[_slug(label)] = _shape_ref(slide, shape)
    return refs


def _database_icon_refs(slide: dict[str, Any], labels: list[str]) -> dict[str, Any]:
    refs: dict[str, Any] = {}
    for label in labels:
        shape = _first_shape_with_text(slide, label)
        if shape is not None:
            ref = _shape_ref(slide, shape)
            ref["label"] = label
            refs[_slug(label)] = ref
    return refs


def _connector_refs(slide: dict[str, Any]) -> dict[str, Any]:
    connectors = [
        _shape_ref(slide, shape)
        for shape in slide["shapes"]
        if shape["tag"] == "cxnSp"
    ]
    annotations = [
        _shape_ref(slide, shape)
        for shape in slide["shapes"]
        if shape["tag"] in {"sp", "grpSp"}
        and (
            "arrowhead" in _normalize_text(shape["text"])
            or "bark" in _normalize_text(shape["text"])
            or "solid-line" in _normalize_text(shape["text"])
            or "dashed-line" in _normalize_text(shape["text"])
        )
    ]
    return {
        "connector_count": len(connectors),
        "connectors": connectors,
        "annotations": annotations,
    }


def _is_noise_line(text: str, config: dict[str, Any]) -> bool:
    raw = (text or "").strip()
    if not raw:
        return True
    norm = _normalize_text(raw)
    if not norm:
        return True
    if re.fullmatch(r"\d+", norm):
        return True
    if re.fullmatch(r"\d+ \d+ \d{4}", norm):
        return True
    index_cfg = config.get("instruction_index") or {}
    for snippet in index_cfg.get("noise_contains", []) or []:
        if _normalize_text(str(snippet)) in norm:
            return True
    for exact in index_cfg.get("noise_exact", []) or []:
        if _normalize_text(str(exact)) == norm:
            return True
    return False


def _instruction_lines(slide: dict[str, Any], config: dict[str, Any]) -> list[str]:
    seen: set[str] = set()
    lines: list[str] = []
    for line in slide.get("text_lines", []) or []:
        if _is_noise_line(line, config):
            continue
        key = line.strip()
        if key in seen:
            continue
        seen.add(key)
        lines.append(key)
    return lines


def _classify_slide(slide: dict[str, Any], semantic_keys: list[str]) -> str:
    title = _normalize_text(slide.get("title", ""))
    text = _normalize_text(slide.get("text_sample", ""))
    display = int(slide.get("display_number", 0))
    if display == 1:
        return "cover"
    if "table of contents" in text:
        return "table_of_contents"
    if "template" in title or "template" in text:
        return "template"
    if "sample" in title:
        return "sample"
    if "connector" in title or "connector" in text:
        return "connector_guidance"
    if "grouping" in title or "location canvas" in text:
        return "grouping_guidance"
    if semantic_keys:
        return "semantic_reference"
    if slide.get("shape_counts", {}).get("grpSp", 0) >= 8:
        return "icon_catalog"
    return "reference"


def _keywords_from_lines(lines: list[str], limit: int = 10) -> list[str]:
    keywords: list[str] = []
    for line in lines:
        slug = _slug(line)
        if slug and slug not in keywords:
            keywords.append(slug)
        if len(keywords) >= limit:
            break
    return keywords


def _slide_catalog(slides: list[dict[str, Any]], semantic_slides: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    semantic_by_number: dict[int, list[str]] = {}
    for key, ref in semantic_slides.items():
        semantic_by_number.setdefault(int(ref["display_number"]), []).append(key)

    catalog: list[dict[str, Any]] = []
    for slide in slides:
        semantic_keys = semantic_by_number.get(int(slide["display_number"]), [])
        instruction_lines = _instruction_lines(slide, config)
        text_shapes = [
            _shape_ref(slide, shape)
            for shape in slide["shapes"]
            if shape.get("text_lines")
        ]
        catalog.append(
            {
                "display_number": slide["display_number"],
                "slide_path": slide["slide_path"],
                "title": slide["title"],
                "kind": _classify_slide(slide, semantic_keys),
                "semantic_keys": semantic_keys,
                "shape_count": slide["shape_count"],
                "shape_counts": slide["shape_counts"],
                "color_palette": slide["colors"],
                "instruction_lines": instruction_lines,
                "instruction_line_count": len(instruction_lines),
                "keywords": _keywords_from_lines([slide["title"], *instruction_lines]),
                "text_sample": slide["text_sample"],
                "text_shapes": text_shapes,
                "non_text_shape_count": max(slide["shape_count"] - len(text_shapes), 0),
                "slide_sha256": slide["slide_sha256"],
            }
        )
    return catalog


def _instruction_catalog(slide_catalog: list[dict[str, Any]]) -> dict[str, Any]:
    slides_with_instructions = [
        {
            "display_number": slide["display_number"],
            "slide_path": slide["slide_path"],
            "title": slide["title"],
            "kind": slide["kind"],
            "semantic_keys": slide["semantic_keys"],
            "instruction_lines": slide["instruction_lines"],
            "keywords": slide["keywords"],
        }
        for slide in slide_catalog
        if slide["instruction_lines"]
    ]
    return {
        "slide_count_with_instructions": len(slides_with_instructions),
        "slides": slides_with_instructions,
    }


def _shape_library(slides: list[dict[str, Any]]) -> dict[str, Any]:
    entries: dict[str, list[dict[str, Any]]] = {}
    total = 0
    for slide in slides:
        for shape in slide.get("library_shapes") or slide["shapes"]:
            if not shape.get("text_lines"):
                continue
            key = _slug(shape.get("text", ""))
            if not key:
                continue
            entries.setdefault(key, []).append(_shape_ref(slide, shape))
            total += 1
    return {
        "unique_labels": len(entries),
        "entry_count": total,
        "entries": entries,
    }


def build_outputs(asset_path: Path, config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    inspection = inspect_pptx(asset_path)
    slides = inspection["slides"]
    semantic_slides, warnings = detect_semantic_slides(slides, config)

    slides_by_key: dict[str, dict[str, Any]] = {}
    for key, info in semantic_slides.items():
        slide = next(
            (candidate for candidate in slides if candidate["display_number"] == info["display_number"]),
            None,
        )
        if slide is not None:
            slides_by_key[key] = slide

    grouping_refs = {}
    grouping_slide = slides_by_key.get("grouping")
    if grouping_slide is not None:
        grouping_refs = _grouping_refs(
            grouping_slide,
            list((config.get("extracted_shapes") or {}).get("grouping_labels", []) or []),
        )

    database_icon_refs = {}
    database_slide = slides_by_key.get("database_icons")
    if database_slide is not None:
        database_icon_refs = _database_icon_refs(
            database_slide,
            list((config.get("extracted_shapes") or {}).get("database_icon_labels", []) or []),
        )

    connector_stencils = {}
    connectors_slide = slides_by_key.get("connectors_logical")
    if connectors_slide is not None:
        connector_stencils["logical"] = _connector_refs(connectors_slide)

    label_slide = slides_by_key.get("connector_labels")
    if label_slide is not None:
        connector_stencils["labels"] = {
            "display_number": label_slide["display_number"],
            "slide_path": label_slide["slide_path"],
            "title": label_slide["title"],
        }

    slide_catalog = _slide_catalog(slides, semantic_slides, config)
    instruction_catalog = _instruction_catalog(slide_catalog)
    shape_library = _shape_library(slides)

    bundle_rel = asset_path.resolve().relative_to(PROJECT_ROOT).as_posix()
    bundle_sha = _file_sha256(asset_path)
    modified = datetime.fromtimestamp(asset_path.stat().st_mtime, tz=timezone.utc)
    generated = datetime.now(timezone.utc)

    index = {
        "generated_at": generated.isoformat(),
        "library": {
            "relative_path": bundle_rel,
            "sha256": bundle_sha,
            "size_bytes": asset_path.stat().st_size,
            "modified_utc": modified.isoformat(),
            "slide_count": inspection["slide_count"],
        },
        "design_tokens": config.get("design_tokens") or {},
        "semantic_slides": semantic_slides,
        "slide_catalog": slide_catalog,
        "instruction_catalog": instruction_catalog,
        "shape_library": shape_library,
        "stencils": {
            "connectors": connector_stencils,
            "groupings": grouping_refs,
            "database_icons": database_icon_refs,
        },
        "warnings": warnings,
    }

    manifest = {
        "last_verified": generated.date().isoformat(),
        "description": "Derived manifest for the bundled OCI_Icons.pptx asset used by native PPTX diagram generation.",
        "source": "Oracle OCI_Icons.pptx asset inspected by tools/refresh_pptx_icon_index.py",
        "asset": {
            "relative_path": bundle_rel,
            "sha256": bundle_sha,
            "size_bytes": asset_path.stat().st_size,
            "slide_count": inspection["slide_count"],
            "modified_utc": modified.isoformat(),
        },
        "semantic_slides": semantic_slides,
        "coverage": {
            "catalogued_slides": len(slide_catalog),
            "slides_with_instructions": instruction_catalog["slide_count_with_instructions"],
            "unique_text_shape_labels": shape_library["unique_labels"],
            "text_shape_entries": shape_library["entry_count"],
        },
        "extracted_shapes": {
            "groupings": sorted(grouping_refs.keys()),
            "database_icons": sorted(database_icon_refs.keys()),
        },
        "warnings": warnings,
    }
    return index, manifest


def discover_candidate_assets(config: dict[str, Any]) -> list[dict[str, Any]]:
    asset_cfg = config.get("asset") or {}
    seen: set[str] = set()
    candidates: list[dict[str, Any]] = []
    for pattern in asset_cfg.get("search_globs", []) or []:
        expanded = os.path.expanduser(str(pattern))
        if not os.path.isabs(expanded):
            expanded = str(PROJECT_ROOT / expanded)
        for match in glob.glob(expanded):
            path = Path(match).resolve()
            if not path.is_file():
                continue
            key = str(path)
            if key in seen:
                continue
            seen.add(key)
            stat = path.stat()
            candidates.append(
                {
                    "path": path,
                    "size_bytes": stat.st_size,
                    "mtime": stat.st_mtime,
                    "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                }
            )
    candidates.sort(key=lambda item: item["mtime"], reverse=True)
    return candidates


def select_source_asset(config: dict[str, Any], explicit_source: str | None) -> tuple[Path, list[dict[str, Any]], str]:
    asset_cfg = config.get("asset") or {}
    env_var = asset_cfg.get("env_var")
    if explicit_source:
        path = _project_path(explicit_source)
        if not path.is_file():
            raise FileNotFoundError(f"Explicit source not found: {path}")
        return path, [], "explicit"
    if env_var and os.getenv(env_var):
        path = _project_path(os.environ[env_var])
        if not path.is_file():
            raise FileNotFoundError(f"{env_var} points to a missing file: {path}")
        return path, [], f"env:{env_var}"
    candidates = discover_candidate_assets(config)
    if candidates:
        return candidates[0]["path"], candidates, "discovered"
    bundled = _project_path(asset_cfg["bundled_path"])
    if bundled.is_file():
        return bundled, [], "bundled"
    raise FileNotFoundError("No OCI_Icons.pptx candidate was found.")


def sync_bundled_asset(source: Path, config: dict[str, Any], *, dry_run: bool = False) -> Path:
    asset_cfg = config.get("asset") or {}
    bundled = _project_path(asset_cfg["bundled_path"])
    bundled.parent.mkdir(parents=True, exist_ok=True)
    sync_enabled = bool((config.get("refresh") or {}).get("sync_discovered_asset_into_bundle", True))
    if dry_run or not sync_enabled or source.resolve() == bundled.resolve():
        return bundled if bundled.exists() else source
    shutil.copy2(source, bundled)
    return bundled


def write_outputs(index: dict[str, Any], manifest: dict[str, Any], config: dict[str, Any], *, dry_run: bool = False) -> tuple[Path, Path]:
    asset_cfg = config.get("asset") or {}
    index_path = _project_path(asset_cfg["index_path"])
    manifest_path = _project_path(asset_cfg["manifest_path"])
    if dry_run:
        return index_path, manifest_path
    index_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    with open(manifest_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(manifest, handle, sort_keys=False, allow_unicode=True)
    return index_path, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh the bundled OCI_Icons.pptx asset and regenerate its structured index."
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help=f"Config YAML path (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--source",
        help="Optional explicit OCI_Icons.pptx source. If omitted, the tool discovers the newest candidate.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect and report, but do not copy the asset or write the manifest/index files.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    source, discovered, source_kind = select_source_asset(config, args.source)
    bundled = sync_bundled_asset(source, config, dry_run=args.dry_run)
    asset_for_index = bundled if bundled.is_file() else source
    index, manifest = build_outputs(asset_for_index, config)
    index_path, manifest_path = write_outputs(index, manifest, config, dry_run=args.dry_run)

    print(f"Source asset: {source}")
    print(f"Resolution: {source_kind}")
    if discovered:
        print(f"Discovered candidates: {len(discovered)}")
        for item in discovered[:5]:
            print(f"  - {item['path']} ({item['mtime_utc']})")
    print(f"Bundled asset: {asset_for_index}")
    print(f"SHA256: {index['library']['sha256']}")
    print(f"Slides: {index['library']['slide_count']}")
    print(f"Semantic slides: {', '.join(sorted(index['semantic_slides']))}")
    print(f"Grouping refs: {len(index['stencils']['groupings'])}")
    print(f"Database icon refs: {len(index['stencils']['database_icons'])}")
    print(f"Index path: {index_path}")
    print(f"Manifest path: {manifest_path}")
    if index["warnings"]:
        print("Warnings:")
        for warning in index["warnings"]:
            print(f"  - {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
