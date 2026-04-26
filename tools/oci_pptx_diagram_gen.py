#!/usr/bin/env python3
"""
Native OCI architecture diagrams inside PPTX slides.

This module patches an already-generated deck by appending native PowerPoint
shapes to one or more slides using XML-level edits. The current implementation
targets the architecture slide in OCI Deal Accelerator decks.
"""

import copy
import json
import posixpath
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from pathlib import PurePosixPath

from lxml import etree


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INDEX_PATH = PROJECT_ROOT / "kb" / "diagram" / "oci-pptx-icons-index.json"
DEFAULT_LIBRARY_PATH = PROJECT_ROOT / "kb" / "diagram" / "assets" / "OCI_Icons.pptx"
EMU_PER_INCH = 914400

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"p": P_NS, "a": A_NS, "r": R_NS}

SERVICE_COLORS = {
    "database": "AA643B",
    "data": "AA643B",
    "infrastructure": "2D5967",
    "networking": "2D5967",
    "network": "2D5967",
    "integration": "804998",
    "security": "2B6242",
    "observability": "2D5967",
    "management": "2D5967",
    "default": "2D5967",
}

TYPE_TO_ICON = {
    "adb": ["adb_d"],
    "adb_d": ["adb_d"],
    "adb_s": ["adb_d"],
    "adw": ["adw_d"],
    "adw_d": ["adw_d"],
    "atp_d": ["atp_d"],
    "database": ["database"],
    "database_system": ["database_system"],
    "base_db": ["database_system"],
    "base_database": ["database_system"],
    "data_guard": ["data_guard"],
    "data_safe": ["data_safe"],
    "database_management": ["database_management"],
    "load_balancer": ["load_balancer", "public_load_balancer"],
    "public_load_balancer": ["public_load_balancer", "load_balancer"],
    "lb": ["load_balancer", "public_load_balancer"],
    "virtual_machine": ["virtual_machine", "oci_compute"],
    "vm": ["virtual_machine", "oci_compute"],
    "compute": ["oci_compute", "virtual_machine"],
    "compute_instance": ["oci_compute", "virtual_machine"],
    "instance_pool": ["oci_compute", "virtual_machine"],
    "object_storage": ["object_storage"],
    "oci_object_storage": ["object_storage", "oci_object_storage"],
    "storage": ["object_storage"],
    "bucket": ["object_storage"],
    "internet_gateway": ["internet_gateway"],
    "igw": ["internet_gateway"],
    "service_gateway": ["service_gateway"],
    "sgw": ["service_gateway"],
    "functions": ["oci_functions", "functions"],
    "function": ["oci_functions", "functions"],
    "oci_functions": ["oci_functions", "functions"],
    "monitoring": ["monitoring"],
    "notifications": ["notifications"],
    "notification": ["notifications"],
    "dns": ["dns"],
    "oke": ["oci_container_engine_for_kubernetes", "container_engine_for_kubernetes_cluster"],
    "kubernetes": ["oci_container_engine_for_kubernetes", "container_engine_for_kubernetes_cluster"],
    "exadata": ["oracle_exadata_database_service"],
    "exacs": ["oracle_exadata_database_service"],
    "exadata_dedicated": ["oracle_exadata_database_service"],
    "oracle_exadata_database_service": ["oracle_exadata_database_service"],
    "drg": ["drg"],
    "dynamic_routing_gateway": ["drg"],
    "policies": ["policies"],
    "iam_policies": ["policies"],
    "security_list": ["security_lists", "route_table_and_security_list"],
    "security_lists": ["security_lists", "route_table_and_security_list"],
    "route_table": ["route_table_and_security_list"],
    "route_table_and_security_list": ["route_table_and_security_list", "security_lists"],
    "fastconnect": ["fastconnect"],
    "vpn": ["site_to_site_vpn", "site_to_site_vpn_or_fastconnect"],
    "site_to_site_vpn": ["site_to_site_vpn", "site_to_site_vpn_or_fastconnect"],
    "nat_gateway": ["nat_gateway"],
    "natgw": ["nat_gateway"],
    "block_volume": ["block_volume"],
    "file_storage": ["file_storage"],
    "vault": ["vault"],
    "bastion": ["bastion"],
    "web_application_firewall": ["web_application_firewall", "waf"],
    "waf": ["web_application_firewall", "waf"],
    "network_firewall": ["firewall"],
    "firewall": ["firewall"],
    "block_volume": ["block_storage"],
    "block_storage": ["block_storage"],
    "api_gateway": ["api_gateway"],
    "streaming": ["streaming"],
    "oci_streaming": ["oci_streaming", "streaming"],
    "queue": ["queue"],
    "events_service": ["events_service"],
    "vault_secrets": ["vault"],
    "cloud_guard": ["cloud_guard"],
    "security_zone": ["maximum_security_zone"],
    "maximum_security_zone": ["maximum_security_zone"],
    "data_catalog": ["data_catalog"],
    "data_integration": ["oci_data_integration", "integration"],
    "oci_data_integration": ["oci_data_integration", "integration"],
    "integration": ["integration"],
    "full_stack_disaster_recovery": ["full_stack_disaster_recovery"],
    "fsdr": ["full_stack_disaster_recovery"],
    "goldengate": ["goldengate"],
    "logging": ["logging"],
    "logging_analytics": ["logging_analytics"],
    "tag_namespace": ["tag_namespace"],
    "mysql": ["mysql_heatwave", "mysql_database_system", "mysql"],
    "mysql_heatwave": ["mysql_heatwave", "mysql_database_system", "mysql"],
    "heatwave": ["mysql_heatwave", "mysql_database_system", "mysql"],
    "mysql_database_service": ["mysql_heatwave", "mysql_database_system", "mysql"],
    "autonomous_database": ["oracle_autonomous_database", "adb_d"],
    "oracle_autonomous_database": ["oracle_autonomous_database", "adb_d"],
    "refreshable_clone": ["oracle_autonomous_database", "adb_d"],
    "adb_clone": ["oracle_autonomous_database", "adb_d"],
    "oci_goldengate": ["goldengate"],
    "ogg": ["goldengate"],
    "dynamic_routing_gateway": ["drg"],
    # Proactive aliases — natural-language slugs an SA / agent might
    # reach for, all mapped to the canonical icon. Adding ahead of
    # demand so a freshly-authored spec resolves on first try.
    "atp": ["atp_d"],
    "alb": ["load_balancer", "public_load_balancer"],
    "nlb": ["load_balancer", "public_load_balancer"],
    "apigw": ["api_gateway"],
    "lambda": ["oci_functions", "functions"],
    "kms": ["vault"],
    "secret": ["vault"],
    "secrets_manager": ["vault"],
    "kafka": ["oci_streaming", "streaming"],
    "alarm": ["alarms", "monitoring"],
    "alarms": ["alarms", "monitoring"],
    "email": ["email_delivery"],
    "email_delivery": ["email_delivery"],
    "identity": ["oracle_identity"],
    "identity_domains": ["oracle_identity"],
    "iam": ["oracle_identity"],
    "user_group": ["user_group"],
    "group": ["user_group"],
    "iac": ["resource_manager"],
    "terraform": ["resource_manager"],
    "oac": ["analytics"],
    "oracle_analytics_cloud": ["analytics"],
    "oic": ["integration", "oci_data_integration"],
    "oracle_integration_cloud": ["integration"],
    "process_automation": ["oci_process_automation"],
    "oracle_process_automation": ["oci_process_automation"],
    "language": ["oci_language"],
    "ai_language": ["oci_language"],
    "speech": ["oci_speech"],
    "ai_speech": ["oci_speech"],
    "vision": ["oci_vision"],
    "ai_vision": ["oci_vision"],
    "rpc": ["remote_peering"],
    "remote_peering_connection": ["remote_peering"],
    "remote_peering": ["remote_peering"],
    "lpg": ["local_peering_gateway"],
    "local_peering_gateway": ["local_peering_gateway"],
    "local_peering": ["local_peering_gateway"],
    "health_check": ["health_checks"],
    "health_checks": ["health_checks"],
    "cpe": ["customer_premises_equipment"],
    "customer_premises_equipment": ["customer_premises_equipment"],
    "tag": ["tag_namespace"],
    "tags": ["tag_namespace"],
    "compartment": ["compartment"],
    "compartments": ["compartment"],
    # Newer OCI services not yet in the OCI Toolkit v24.2 / OCI_Icons.pptx —
    # fall back to the generic ``database`` stencil with an explicit
    # ``label:`` carrying the real service name. Oracle's own ref archs
    # (e.g. modernize-app-dev-oci-postgresql-redis-opensearch) embed
    # custom inline SVGs because the toolkit lacks these too — using the
    # canonical generic icon is the closest standardized match.
    "redis": ["database"],
    "oci_cache": ["database"],
    "oci_cache_with_redis": ["database"],
    "cache": ["database"],
    "valkey": ["database"],
    "postgresql": ["database"],
    "postgres": ["database"],
    "oci_postgresql": ["database"],
    "opensearch": ["database_opensearch", "database"],
}

ICON_KEYWORD_HINTS = {
    "virtual machine": ["virtual_machine", "oci_compute"],
    "compute": ["oci_compute", "virtual_machine"],
    "load balancer": ["load_balancer", "public_load_balancer"],
    "object storage": ["object_storage"],
    "internet gateway": ["internet_gateway"],
    "service gateway": ["service_gateway"],
    "functions": ["oci_functions", "functions"],
    "monitoring": ["monitoring"],
    "notifications": ["notifications"],
    "data guard": ["data_guard"],
    "data safe": ["data_safe"],
    "adb": ["adb_d"],
    "adw": ["adw_d"],
    "atp": ["atp_d"],
    "database system": ["database_system"],
    "base database": ["database_system"],
    "exadata": ["oracle_exadata_database_service"],
    "exacs": ["oracle_exadata_database_service"],
    "exadata database service": ["oracle_exadata_database_service"],
    "exadata dedicated": ["oracle_exadata_database_service"],
    "oracle exadata": ["oracle_exadata_database_service"],
    "drg": ["drg"],
    "dynamic routing gateway": ["drg"],
    "policies": ["policies"],
    "policy": ["policies"],
    "security list": ["security_lists", "route_table_and_security_list"],
    "security lists": ["security_lists", "route_table_and_security_list"],
    "route table": ["route_table_and_security_list"],
    "fastconnect": ["fastconnect"],
    "vpn": ["site_to_site_vpn", "site_to_site_vpn_or_fastconnect"],
    "nat gateway": ["nat_gateway"],
    "block volume": ["block_volume"],
    "file storage": ["file_storage"],
    "bastion": ["bastion"],
    "cloud guard": ["cloud_guard"],
    "security zone": ["maximum_security_zone"],
    "vault": ["vault"],
    "api gateway": ["api_gateway"],
    "goldengate": ["goldengate"],
    "data catalog": ["data_catalog"],
    "data integration": ["oci_data_integration", "integration"],
    "streaming": ["oci_streaming", "streaming"],
    "full stack disaster recovery": ["full_stack_disaster_recovery"],
    "cloud guard": ["cloud_guard"],
    "logging": ["logging"],
    "data catalog": ["data_catalog"],
    "network firewall": ["network_firewall"],
    "web application firewall": ["web_application_firewall", "waf"],
    "oke": ["oci_container_engine_for_kubernetes", "container_engine_for_kubernetes_cluster"],
    "kubernetes": ["oci_container_engine_for_kubernetes", "container_engine_for_kubernetes_cluster"],
    "mysql": ["mysql", "database_mysql"],
    "mysql heatwave": ["mysql_heatwave", "mysql_database_system", "mysql"],
    "heatwave": ["mysql_heatwave", "mysql_database_system", "mysql"],
    "mysql database service": ["mysql_heatwave", "mysql_database_system", "mysql"],
}


def _emu(value_in: float) -> int:
    return int(round(value_in * EMU_PER_INCH))


def _slug(text: str) -> str:
    chars = []
    for char in text.lower():
        chars.append(char if char.isalnum() else "_")
    return "_".join(part for part in "".join(chars).split("_") if part)


class NativePPTXDiagramRenderer:
    def __init__(self, index_path: Path | str = DEFAULT_INDEX_PATH, library_path: Path | str = DEFAULT_LIBRARY_PATH):
        self.index_path = Path(index_path)
        self.library_path = Path(library_path)
        with open(self.index_path, "r", encoding="utf-8") as handle:
            self.index = json.load(handle)
        self.tokens = self.index.get("design_tokens", {})
        palette = self.tokens.get("palette", {})
        self.bark = palette.get("bark", "312D2A")
        self.bark_soft = palette.get("bark_soft", "66615C")
        self.white = palette.get("white", "FFFFFF")
        self.connector_style = self.tokens.get("connector_style", {})
        self.shape_library_entries = (self.index.get("shape_library") or {}).get("entries", {})
        self.sample_icon_refs = self._build_sample_icon_refs()
        self._source_rels_cache = {}
        self._current_work_dir = None
        self._current_slide_path = None

    def _build_sample_icon_refs(self) -> dict:
        sample_info = self.index.get("semantic_slides", {}).get("landscape_sample_db_dr")
        if not sample_info:
            return {}
        refs = {}
        with zipfile.ZipFile(self.library_path) as archive:
            root = etree.fromstring(archive.read(sample_info["slide_path"]))
            sp_tree = root.find(".//p:spTree", namespaces=NS)
            if sp_tree is None:
                return refs
            for child_index, child in enumerate(sp_tree):
                tag = etree.QName(child).localname
                if tag not in {"grpSp", "sp"}:
                    continue
                texts = [(node.text or "").strip() for node in child.findall(".//a:t", namespaces=NS) if (node.text or "").strip()]
                if not texts:
                    continue
                label = " ".join(texts)
                slug = _slug(label)
                c_nv_pr = child.find(".//p:cNvPr", namespaces=NS)
                bbox = self._extract_bbox(child)
                refs[slug] = {
                    "display_number": sample_info["display_number"],
                    "slide_path": sample_info["slide_path"],
                    "title": sample_info.get("title", ""),
                    "child_index": child_index,
                    "shape_id": int(c_nv_pr.get("id")) if c_nv_pr is not None and c_nv_pr.get("id", "").isdigit() else None,
                    "shape_name": c_nv_pr.get("name") if c_nv_pr is not None else "",
                    "text": " | ".join(texts),
                    "bbox": bbox,
                }
        return refs

    def apply_jobs(self, deck_path: str | Path, jobs: list[dict]):
        deck_path = Path(deck_path)
        if not jobs:
            return
        with tempfile.TemporaryDirectory(prefix="oci-pptx-native-") as tmp_dir:
            work_dir = Path(tmp_dir) / "deck"
            self._extract(deck_path, work_dir)
            for job in jobs:
                self._apply_job(work_dir, job)
            self._repack(work_dir, deck_path)

    def _extract(self, deck_path: Path, work_dir: Path):
        if work_dir.exists():
            shutil.rmtree(work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(deck_path) as archive:
            archive.extractall(work_dir)

    def _repack(self, work_dir: Path, deck_path: Path):
        temp_output = deck_path.with_suffix(".tmp.pptx")
        if temp_output.exists():
            temp_output.unlink()
        with zipfile.ZipFile(temp_output, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(work_dir.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(work_dir))
        shutil.move(temp_output, deck_path)

    def _resolve_slide_path(self, work_dir: Path, display_number: int) -> Path:
        presentation_xml = work_dir / "ppt" / "presentation.xml"
        rels_xml = work_dir / "ppt" / "_rels" / "presentation.xml.rels"
        pres_root = etree.parse(str(presentation_xml)).getroot()
        rels_root = etree.parse(str(rels_xml)).getroot()
        slide_ids = pres_root.find("p:sldIdLst", namespaces=NS)
        if slide_ids is None:
            raise RuntimeError("presentation.xml has no slide list")
        slide_id = slide_ids.findall("p:sldId", namespaces=NS)[display_number - 1]
        rel_id = slide_id.get(f"{{{R_NS}}}id")
        for rel in rels_root:
            if rel.get("Id") == rel_id:
                return work_dir / "ppt" / rel.get("Target")
        raise RuntimeError(f"Could not resolve slide {display_number}")

    def _apply_job(self, work_dir: Path, job: dict):
        slide_path = self._resolve_slide_path(work_dir, job["slide_number"])
        self._current_work_dir = work_dir
        self._current_slide_path = slide_path
        slide_tree = etree.parse(str(slide_path))
        slide_root = slide_tree.getroot()
        sp_tree = slide_root.find(".//p:spTree", namespaces=NS)
        if sp_tree is None:
            raise RuntimeError(f"{slide_path} has no spTree")
        allocator = self._shape_id_allocator(slide_root)
        for element in self._render_job(job, allocator):
            sp_tree.append(element)
        slide_tree.write(str(slide_path), encoding="UTF-8", xml_declaration=True)
        etree.parse(str(slide_path))
        self._current_work_dir = None
        self._current_slide_path = None

    def _shape_id_allocator(self, slide_root):
        shape_ids = []
        for node in slide_root.findall(".//p:cNvPr", namespaces=NS):
            value = node.get("id")
            if value and value.isdigit():
                shape_ids.append(int(value))
        next_id = max(shape_ids or [1000]) + 1

        def allocate(count: int = 1) -> int:
            nonlocal next_id
            start = next_id
            next_id += count
            return start

        return allocate

    def _render_job(self, job: dict, allocate_id) -> list:
        visual = job.get("visual") or {}
        content = job.get("content_box", {})
        x = int(content["x"])
        y = int(content["y"])
        w = int(content["cx"])
        h = int(content["cy"])
        fragments = []
        service_positions = {}

        on_prem = visual.get("on_prem")
        regions = list(visual.get("regions") or [])
        if visual.get("absolute_layout"):
            # Spec-level geometry validation — same guard the drawio
            # path runs. Catches CONTAINER_TOO_THIN /
            # LABEL_OVERFLOW_PARENT before any XML is emitted.
            try:
                from diagram_spec_validator import validate_spec  # type: ignore
            except ImportError:
                from tools.diagram_spec_validator import validate_spec  # type: ignore
            validate_spec({"absolute_layout": visual["absolute_layout"]},
                          source="absolute_layout (pptx)")
            return self._render_absolute_layout(visual, content, allocate_id)
        if not regions:
            return []

        gap = _emu(0.18)
        region_top = y + _emu(0.05)
        region_height = h - _emu(0.18)

        on_prem_width = _emu(1.55) if on_prem else 0
        if on_prem:
            left_x = x
            left_y = y + region_height - _emu(0.60)
            fragments.append(self._fallback_service_card(
                allocate_id(),
                left_x,
                left_y,
                on_prem_width,
                _emu(0.48),
                on_prem.get("name", "On-Premises"),
                color="70665E",
            ))
            if on_prem.get("connection"):
                fragments.append(self._label_shape(
                    allocate_id(),
                    left_x + on_prem_width + _emu(0.08),
                    left_y + _emu(0.06),
                    _emu(1.1),
                    _emu(0.25),
                    on_prem["connection"],
                    font_size=850,
                    color=self.bark_soft,
                    bold=False,
                    align="l",
                ))

        regions_x = x + on_prem_width + (gap if on_prem else 0)
        regions_width = w - on_prem_width - (gap if on_prem else 0)
        region_frames = self._layout_regions(regions_x, region_top, regions_width, region_height, regions)
        for region, frame in zip(regions, region_frames):
            fragments.extend(self._render_region(region, frame, allocate_id, service_positions))

        for connection in visual.get("connections", []) or []:
            fragments.extend(self._render_connection(connection, service_positions, allocate_id))

        security = visual.get("security_footer")
        if security:
            fragments.append(self._label_shape(
                allocate_id(),
                x,
                y + h - _emu(0.10),
                w,
                _emu(0.25),
                security,
                font_size=760,
                color=self.bark_soft,
                bold=False,
                align="l",
            ))
        return fragments

    def _render_absolute_layout(self, visual: dict, content: dict, allocate_id) -> list:
        layout = visual.get("absolute_layout") or {}
        canvas = layout.get("canvas") or {}
        canvas_w = float(canvas.get("width", 850) or 850)
        canvas_h = float(canvas.get("height", 770) or 770)
        content_x = int(content["x"])
        content_y = int(content["y"])
        content_w = int(content["cx"])
        content_h = int(content["cy"])
        # Geometry scale: canvas px → content_box EMU.
        scale = min(content_w / canvas_w, content_h / canvas_h)
        offset_x = content_x + int((content_w - canvas_w * scale) / 2)
        offset_y = content_y + int((content_h - canvas_h * scale) / 2)

        def sx(value): return offset_x + int(round(float(value) * scale))
        def sy(value): return offset_y + int(round(float(value) * scale))
        def sl(value): return max(1, int(round(float(value) * scale)))

        fragments = []
        service_positions = {}

        for item in layout.get("containers") or []:
            kind = item.get("type", "compartment")
            fill = None
            stroke = "9E9892"
            dashed = False
            rounded = False
            width = 12700
            if kind == "region":
                fill = "F5F4F2"
                rounded = True
            elif kind == "ad":
                fill = "DFDCD8"
                rounded = True
            elif kind in {"vcn", "subnet"}:
                stroke = "AA643B"
                dashed = True
                width = 19050
            fragments.append(self._container_shape(
                allocate_id(), sx(item.get("x", 0)), sy(item.get("y", 0)),
                sl(item.get("w", 100)), sl(item.get("h", 80)),
                stroke_color=stroke, stroke_width=width, dashed=dashed,
                fill=fill, rounded=rounded,
            ))
            label = item.get("label")
            if label:
                color = "AA643B" if kind in {"vcn", "subnet"} else self.bark
                fragments.append(self._label_shape(
                    allocate_id(), sx(item.get("x", 0)) + sl(6), sy(item.get("y", 0)) + sl(4),
                    max(1, sl(item.get("w", 100)) - sl(12)), sl(26),
                    str(label).replace("\\n", "\n"), font_size=int(item.get("fontSize", 820)),
                    color=color, bold=bool(item.get("bold", True)), align=item.get("align", "l"),
                ))

        for item in layout.get("external") or []:
            # Native PPTX currently has no user stencil in the OCI deck; use a
            # compact neutral card instead of importing non-OCI artwork.
            fragments.append(self._fallback_service_card(
                allocate_id(), sx(item.get("x", 0)), sy(item.get("y", 0)),
                sl(item.get("w", 70)), sl(item.get("h", 52)),
                item.get("label", "Users"), color="2D5967",
            ))
            service_positions[item.get("id", _slug(item.get("label", "external")))] = {
                "x": sx(item.get("x", 0)), "y": sy(item.get("y", 0)),
                "cx": sl(item.get("w", 70)), "cy": sl(item.get("h", 52)),
            }

        for item in layout.get("services") or []:
            x = sx(item.get("x", 0))
            y = sy(item.get("y", 0))
            w = sl(item.get("w", 100))
            h = sl(item.get("h", 80))
            fragments.extend(self._render_service(item, x, y, w, h, allocate_id, service_positions))

        for item in layout.get("labels") or []:
            fragments.append(self._label_shape(
                allocate_id(), sx(item.get("x", 0)), sy(item.get("y", 0)),
                sl(item.get("w", 100)), sl(item.get("h", 24)),
                str(item.get("text", "")).replace("\\n", "\n"),
                font_size=int(item.get("fontSize", 780)),
                color=item.get("color", self.bark),
                bold=bool(item.get("bold", False)),
                align=item.get("align", "ctr"),
            ))

        for conn in layout.get("connections") or []:
            source = service_positions.get(conn.get("from"))
            target = service_positions.get(conn.get("to"))
            if not source or not target:
                continue
            points = conn.get("points")
            if points:
                scaled = [(sx(p[0]), sy(p[1])) for p in points]
            else:
                scaled = [
                    (source["x"] + int(source["cx"] / 2), source["y"] + int(source["cy"] / 2)),
                    (target["x"] + int(target["cx"] / 2), target["y"] + int(target["cy"] / 2)),
                ]
            # Render the polyline as a SINGLE native bent connector
            # (OCI_Icons.pptx convention) instead of multiple disjoint
            # straight `line` shapes.
            bent = self._bent_connector_shape(
                allocate_id(), scaled, self.bark,
                width_emu=12700, dashed=bool(conn.get("dashed")), arrow=True,
            )
            if bent is not None:
                fragments.append(bent)
            if conn.get("flow_order"):
                bx = scaled[0][0] + int((scaled[-1][0] - scaled[0][0]) * float(conn.get("badge_t", 0.25))) - sl(9)
                by = scaled[0][1] + int((scaled[-1][1] - scaled[0][1]) * float(conn.get("badge_t", 0.25))) - sl(9)
                fragments.append(self._badge_shape(allocate_id(), bx, by, sl(18), str(conn["flow_order"])))
            if conn.get("label"):
                lx = sx(conn.get("label_x", canvas_w / 2))
                ly = sy(conn.get("label_y", canvas_h / 2))
                fragments.append(self._label_shape(
                    allocate_id(), lx, ly, sl(conn.get("label_w", 100)), sl(conn.get("label_h", 26)),
                    str(conn.get("label", "")), font_size=720, color=self.bark, bold=False, align="ctr",
                ))

        return fragments

    def _layout_regions(self, x: int, y: int, w: int, h: int, regions: list[dict]) -> list[dict]:
        if len(regions) == 1:
            return [{"x": x, "y": y, "cx": w, "cy": h}]
        if len(regions) == 2:
            gap = _emu(0.20)
            primary_w = int((w - gap) * 0.62)
            secondary_w = w - gap - primary_w
            return [
                {"x": x, "y": y, "cx": primary_w, "cy": h},
                {"x": x + primary_w + gap, "y": y, "cx": secondary_w, "cy": h},
            ]
        gap = _emu(0.16)
        total_gap = gap * (len(regions) - 1)
        width = int((w - total_gap) / len(regions))
        frames = []
        current = x
        for _ in regions:
            frames.append({"x": current, "y": y, "cx": width, "cy": h})
            current += width + gap
        return frames

    def _render_region(self, region: dict, frame: dict, allocate_id, service_positions: dict) -> list:
        fragments = []
        region_ref = self.index["stencils"]["groupings"]["oci_region"]
        fragments.append(self._clone_simple_shape(region_ref, lambda: allocate_id(), frame["x"], frame["y"], frame["cx"], frame["cy"], clear_text=True))
        label_parts = [region.get("name", "OCI Region")]
        if region.get("label"):
            label_parts.append(f"[{region['label']}]")
        fragments.append(self._label_shape(
            allocate_id(),
            frame["x"] + _emu(0.12),
            frame["y"] + _emu(0.06),
            frame["cx"] - _emu(0.24),
            _emu(0.22),
            "  ".join(label_parts),
            font_size=900,
            color=self.bark,
            bold=True,
            align="l",
        ))

        inner_x = frame["x"] + _emu(0.12)
        inner_y = frame["y"] + _emu(0.40)
        inner_w = frame["cx"] - _emu(0.24)
        inner_h = frame["cy"] - _emu(0.52)

        if region.get("availability_domains"):
            fragments.extend(self._render_availability_domains(region, inner_x, inner_y, inner_w, inner_h, allocate_id, service_positions))
        elif region.get("vcn"):
            fragments.extend(self._render_vcn(region["vcn"], inner_x, inner_y, inner_w, inner_h, allocate_id, service_positions))
        else:
            services = list(region.get("services") or [])
            fragments.extend(self._render_service_strip(services, inner_x, inner_y, inner_w, inner_h, allocate_id, service_positions))

        details = region.get("details")
        if details:
            fragments.append(self._label_shape(
                allocate_id(),
                inner_x + _emu(0.04),
                frame["y"] + frame["cy"] - _emu(0.28),
                inner_w - _emu(0.08),
                _emu(0.20),
                details,
                font_size=760,
                color=self.bark_soft,
                bold=False,
                align="ctr",
            ))
        return fragments

    def _render_availability_domains(self, region: dict, x: int, y: int, w: int, h: int, allocate_id, service_positions: dict) -> list:
        fragments = []
        ads = list(region.get("availability_domains") or [])
        gap = _emu(0.12)
        total_gap = gap * max(len(ads) - 1, 0)
        width = int((w - total_gap) / max(len(ads), 1))
        current_x = x
        for ad in ads:
            ad_ref = self.index["stencils"]["groupings"]["availability_domain"]
            fragments.append(self._clone_simple_shape(ad_ref, lambda: allocate_id(), current_x, y, width, h, clear_text=True))
            fragments.append(self._label_shape(
                allocate_id(),
                current_x + _emu(0.03),
                y + _emu(0.05),
                width - _emu(0.06),
                _emu(0.20),
                ad.get("name", "Availability Domain"),
                font_size=850,
                color=self.bark,
                bold=True,
                align="ctr",
            ))
            fragments.extend(self._render_vcn(ad.get("vcn", {}), current_x + _emu(0.04), y + _emu(0.28), width - _emu(0.08), h - _emu(0.34), allocate_id, service_positions))
            current_x += width + gap
        return fragments

    def _render_vcn(self, vcn: dict, x: int, y: int, w: int, h: int, allocate_id, service_positions: dict) -> list:
        fragments = []
        fragments.append(self._container_shape(
            allocate_id(),
            x, y, w, h,
            stroke_color="AE562C",
            stroke_width=19050,
            dashed=True,
            fill=None,
            rounded=False,
        ))
        vcn_label = vcn.get("name", "VCN")
        if vcn.get("cidr"):
            vcn_label = f"{vcn_label}  {vcn['cidr']}"
        fragments.append(self._label_shape(
            allocate_id(),
            x + _emu(0.10),
            y + _emu(0.06),
            w - _emu(0.20),
            _emu(0.20),
            vcn_label,
            font_size=840,
            color="AE562C",
            bold=True,
            align="l",
        ))

        subnets = list(vcn.get("subnets") or [])
        if not subnets:
            return fragments
        gap = _emu(0.10)
        subnet_y = y + _emu(0.32)
        available_h = h - _emu(0.40)
        subnet_h = int((available_h - gap * max(len(subnets) - 1, 0)) / max(len(subnets), 1))
        for subnet in subnets:
            fragments.append(self._container_shape(
                allocate_id(),
                x + _emu(0.10), subnet_y, w - _emu(0.20), subnet_h,
                stroke_color="AE562C",
                stroke_width=12700,
                dashed=True,
                fill="FCFBFA",
                rounded=False,
            ))
            subnet_label = subnet.get("name", "Subnet")
            if subnet.get("cidr"):
                subnet_label = f"{subnet_label}  {subnet['cidr']}"
            fragments.append(self._label_shape(
                allocate_id(),
                x + _emu(0.18),
                subnet_y + _emu(0.05),
                w - _emu(0.36),
                _emu(0.18),
                subnet_label,
                font_size=760,
                color="AE562C",
                bold=True,
                align="l",
            ))
            fragments.extend(self._render_service_strip(
                list(subnet.get("services") or []),
                x + _emu(0.16),
                subnet_y + _emu(0.24),
                w - _emu(0.32),
                subnet_h - _emu(0.28),
                allocate_id,
                service_positions,
            ))
            subnet_y += subnet_h + gap
        return fragments

    def _render_service_strip(self, services: list[dict], x: int, y: int, w: int, h: int, allocate_id, service_positions: dict) -> list:
        fragments = []
        if not services:
            return fragments
        count = len(services)
        gap = _emu(0.10)
        cols = count if count <= 4 else 4
        rows = (count + cols - 1) // cols
        cell_w = int((w - gap * max(cols - 1, 0)) / max(cols, 1))
        cell_h = int((h - gap * max(rows - 1, 0)) / max(rows, 1))
        for idx, service in enumerate(services):
            row = idx // cols
            col = idx % cols
            cell_x = x + col * (cell_w + gap)
            cell_y = y + row * (cell_h + gap)
            fragments.extend(self._render_service(service, cell_x, cell_y, cell_w, cell_h, allocate_id, service_positions))
        return fragments

    # AWS / GCP color codes — used by _render_service when a spec passes
    # `cloud_icon: <key>`. The drawio renderer uses native mxgraph shape
    # libraries (mxgraph.aws4.*), but those are drawio-only — PowerPoint
    # has no equivalent native stencil. The pragmatic PPTX fallback is a
    # provider-branded card (correct color + label) rendered at 72% of
    # the spec bbox to match the visual weight of OCI line-art icons.
    CLOUD_ICON_COLORS = {
        # AWS (mxgraph.aws4.* color taxonomy)
        "ec2": "ED7100", "eks": "ED7100", "ecs": "ED7100", "lambda": "ED7100",
        "rds": "C925D1", "aurora": "C925D1", "dynamodb": "C925D1",
        "s3": "3F8624",
        "elb": "8C4FFF", "alb": "8C4FFF", "cloudfront": "8C4FFF",
        "vpc": "8C4FFF", "direct_connect": "8C4FFF", "route53": "8C4FFF",
        "kinesis": "8C4FFF",
        "sqs": "E7157B", "sns": "E7157B", "api_gateway": "E7157B",
        "cloudwatch": "E7157B",
        "cognito": "DD344C", "iam": "DD344C",
        "sagemaker": "01A88D", "bedrock": "01A88D",
        # GCP
        "gce": "4285F4", "gke": "4285F4", "cloud_run": "4285F4",
        "bigquery": "669DF6", "cloud_storage": "AECBFA",
        "cloud_sql": "4285F4",
    }
    CLOUD_ICON_LABELS = {
        "ec2": "AWS EC2", "eks": "AWS EKS", "ecs": "AWS ECS", "lambda": "AWS Lambda",
        "rds": "AWS RDS", "aurora": "AWS Aurora", "dynamodb": "DynamoDB",
        "s3": "AWS S3",
        "elb": "AWS ELB", "alb": "AWS ALB", "cloudfront": "CloudFront",
        "vpc": "AWS VPC", "direct_connect": "Direct Connect", "route53": "Route 53",
        "sqs": "AWS SQS", "sns": "AWS SNS", "kinesis": "Kinesis",
        "api_gateway": "API Gateway", "cognito": "Cognito", "iam": "AWS IAM",
        "cloudwatch": "CloudWatch", "sagemaker": "SageMaker", "bedrock": "Bedrock",
        "gce": "GCE", "gke": "GKE", "cloud_run": "Cloud Run",
        "bigquery": "BigQuery", "cloud_storage": "Cloud Storage", "cloud_sql": "Cloud SQL",
    }

    def _render_service(self, service: dict, x: int, y: int, w: int, h: int, allocate_id, service_positions: dict) -> list:
        fragments = []
        # Multi-cloud support: spec may carry `cloud_icon: ec2` etc. for
        # AWS/GCP components. Render as a provider-branded card scaled
        # to 72% of the bbox so it visually matches the OCI line-art
        # icons next to it (same rule as drawio renderer — Diego's
        # 2026-04-25 feedback "el tamaño del icono queda muy grande").
        cloud_icon = (service.get("cloud_icon") or "").lower()
        if cloud_icon:
            color = self.CLOUD_ICON_COLORS.get(cloud_icon, "ED7100")
            text = service.get("label") or self.CLOUD_ICON_LABELS.get(cloud_icon, cloud_icon.upper())
            visual_scale = 0.72
            rw = int(w * visual_scale)
            rh = int(h * visual_scale)
            rx = x + (w - rw) // 2
            ry = y + (h - rh) // 2
            fragments.append(self._fallback_service_card(
                allocate_id(), rx, ry, rw, rh, text, color=color,
            ))
            sid = service.get("id") or _slug(text)
            service_positions[sid] = {"x": rx, "y": ry, "cx": rw, "cy": rh}
            return fragments
        icon_ref = self._resolve_icon_ref(service)
        service_id = service.get("id") or _slug(service.get("name", service.get("type", "service")))
        if icon_ref:
            # Icon fills the spec's full (w, h) bbox. The earlier
            # aspect-ratio-preserving logic ("fit within w/h") left
            # significant whitespace inside the bbox — Diego flagged
            # 2026-04-25 round 3: "Oracle Exadata lo veo muy chico en
            # el pptx" — and the workaround knobs (0.5 floor, 0.8 floor)
            # never closed the gap because the icon's natural aspect
            # ratio (~1.48 wide) rarely matches the spec's (e.g. 0.9).
            #
            # General rule (now baked in): the spec author owns the
            # bbox, so the icon stretches to fill it. Spec authors who
            # want a specific aspect should size their bbox accordingly.
            target_cx = int(w)
            target_cy = int(h)
            target_x = x + max(int((w - target_cx) / 2), 0)
            target_y = y + max(int((h - target_cy) / 2), 0)
            fragments.append(self._clone_translated_block(
                icon_ref, allocate_id, target_x, target_y,
                target_cx=target_cx, target_cy=target_cy,
            ))
            service_positions[service_id] = {
                "x": target_x,
                "y": target_y,
                "cx": target_cx,
                "cy": target_cy,
            }
            if service.get("caption"):
                fragments.append(self._label_shape(
                    allocate_id(),
                    x,
                    y + h - _emu(0.18),
                    w,
                    _emu(0.16),
                    service["caption"],
                    font_size=720,
                    color=self.bark_soft,
                    bold=False,
                    align="ctr",
                ))
            return fragments

        label = service.get("name") or service.get("label") or service.get("type", "Service")
        color = SERVICE_COLORS.get(service.get("category"), SERVICE_COLORS.get(service.get("type"), SERVICE_COLORS["default"]))
        fragments.append(self._fallback_service_card(allocate_id(), x + _emu(0.04), y + _emu(0.04), w - _emu(0.08), h - _emu(0.08), label, color=color))
        service_positions[service_id] = {
            "x": x + _emu(0.04),
            "y": y + _emu(0.04),
            "cx": w - _emu(0.08),
            "cy": h - _emu(0.08),
        }
        return fragments

    def _render_connection(self, connection: dict, service_positions: dict, allocate_id) -> list:
        source = service_positions.get(connection.get("from"))
        target = service_positions.get(connection.get("to"))
        if not source or not target:
            return []
        sx = source["x"] + int(source["cx"] / 2)
        sy = source["y"] + int(source["cy"] / 2)
        tx = target["x"] + int(target["cx"] / 2)
        ty = target["y"] + int(target["cy"] / 2)
        label = connection.get("label", "")
        dashed = bool(connection.get("style") == "dashed" or connection.get("dashed"))
        width_emu = int(self.connector_style.get("line_width_soft_emu" if dashed else "line_width_emu", 9525 if dashed else 12700))
        fragments = [self._arrow_shape(allocate_id(), sx, sy, tx, ty, self.bark, width_emu=width_emu, dashed=dashed)]
        if label:
            lx = min(sx, tx) + int(abs(tx - sx) / 2) - _emu(0.40)
            ly = min(sy, ty) + int(abs(ty - sy) / 2) - _emu(0.10)
            fragments.append(self._label_shape(
                allocate_id(),
                lx,
                ly,
                _emu(0.80),
                _emu(0.20),
                label,
                font_size=760,
                color=self.bark,
                bold=False,
                align="ctr",
            ))
        return fragments

    def _resolve_icon_ref(self, service: dict) -> dict | None:
        for key in self._candidate_icon_keys(service):
            ref = self._lookup_icon_ref(key)
            if ref:
                return ref
        return None

    def _candidate_icon_keys(self, service: dict) -> list[str]:
        candidates = []
        seen = set()

        def add(value: str | None):
            if not value:
                return
            if value not in seen:
                seen.add(value)
                candidates.append(value)

        service_type = _slug(service.get("type", ""))
        service_name = _slug(service.get("name", ""))
        for key in TYPE_TO_ICON.get(service_type, []):
            add(key)
        add(service_type)
        add(service_name)

        name_text = " ".join(service_name.split("_"))
        type_text = " ".join(service_type.split("_"))
        for phrase, keys in ICON_KEYWORD_HINTS.items():
            if phrase in name_text or phrase in type_text:
                for key in keys:
                    add(key)
        return candidates

    def _lookup_icon_ref(self, key: str) -> dict | None:
        database_icons = (self.index.get("stencils") or {}).get("database_icons") or {}
        if key in database_icons:
            return database_icons[key]
        if key in self.sample_icon_refs:
            return self.sample_icon_refs[key]
        refs = self.shape_library_entries.get(key) or []
        if refs:
            return self._select_preferred_ref(refs)
        return None

    def _select_preferred_ref(self, refs: list[dict]) -> dict | None:
        viable = [
            ref for ref in refs
            if (ref.get("child_index") is not None or ref.get("node_path"))
            and ref.get("slide_path")
            and (ref.get("bbox") or {}).get("cx")
            and ref.get("tag") in {"grpSp", "pic", "sp"}
        ]
        if not viable:
            return refs[0] if refs else None

        # OCI_Icons.pptx ships both a full icon group (tag=grpSp, ~0.7"
        # tall) and a tiny "label strip" (tag=sp, ~0.2" tall) under the
        # same slug for many services. The strip renders as just a text
        # label which makes the diagram look broken next to the drawio
        # version. Prefer the icon group whenever one exists.
        icon_shaped = [
            ref for ref in viable
            if ref.get("tag") in {"grpSp", "pic"}
            or (
                int((ref.get("bbox") or {}).get("cy", 0)) >= _emu(0.4)
                and int((ref.get("bbox") or {}).get("cx", 0)) >= _emu(0.4)
            )
        ]
        if icon_shaped:
            viable = icon_shaped

        preferred_slide_order = {
            29: 0,
            30: 1,
            31: 2,
            32: 3,
            34: 4,
            36: 5,
            37: 6,
        }
        tag_order = {"grpSp": 0, "pic": 1, "sp": 2}

        def score(ref: dict):
            bbox = ref.get("bbox") or {}
            cx = int(bbox.get("cx", 0))
            cy = int(bbox.get("cy", 0))
            return (
                1 if cx > _emu(2.25) or cy > _emu(1.25) else 0,
                preferred_slide_order.get(int(ref.get("display_number", 999)), 999),
                tag_order.get(ref.get("tag"), 9),
                abs(cx - _emu(0.82)) + abs(cy - _emu(0.62)),
            )

        return min(viable, key=score)

    def _extract_bbox(self, element) -> dict | None:
        xfrm = element.find(".//a:xfrm", namespaces=NS)
        if xfrm is None:
            return None
        off = xfrm.find("a:off", namespaces=NS)
        ext = xfrm.find("a:ext", namespaces=NS)
        if off is None or ext is None:
            return None
        return {
            "x": int(off.get("x", "0")),
            "y": int(off.get("y", "0")),
            "cx": int(ext.get("cx", "0")),
            "cy": int(ext.get("cy", "0")),
        }

    def _source_child(self, ref: dict):
        with zipfile.ZipFile(self.library_path) as archive:
            root = etree.fromstring(archive.read(ref["slide_path"]))
            sp_tree = root.find(".//p:spTree", namespaces=NS)
            path = list(ref.get("node_path") or [ref["child_index"]])
            child = sp_tree
            for index in path:
                child = list(child)[int(index)]
            return copy.deepcopy(child)

    def _clone_simple_shape(self, ref: dict, allocate_id, x: int, y: int, cx: int, cy: int, clear_text: bool = False):
        element = self._source_child(ref)
        self._assign_ids(element, allocate_id)
        xfrm = element.find(".//a:xfrm", namespaces=NS)
        if xfrm is not None:
            off = xfrm.find("a:off", namespaces=NS)
            ext = xfrm.find("a:ext", namespaces=NS)
            if off is not None:
                off.set("x", str(x))
                off.set("y", str(y))
            if ext is not None:
                ext.set("cx", str(cx))
                ext.set("cy", str(cy))
            ch_off = xfrm.find("a:chOff", namespaces=NS)
            ch_ext = xfrm.find("a:chExt", namespaces=NS)
            if ch_off is not None:
                ch_off.set("x", str(x))
                ch_off.set("y", str(y))
            if ch_ext is not None:
                ch_ext.set("cx", str(cx))
                ch_ext.set("cy", str(cy))
        if clear_text:
            for node in element.findall(".//a:t", namespaces=NS):
                node.text = ""
        return element

    def _clone_translated_block(self, ref: dict, allocate_id, target_x: int, target_y: int,
                                 target_cx: int | None = None, target_cy: int | None = None):
        """Clone an icon group from the OCI library and place it at
        (target_x, target_y). When target_cx/target_cy are provided,
        the wrapper's <a:ext> is resized to match — children keep their
        chExt-relative geometry, so PowerPoint scales them automatically.

        Without scaling, every cloned icon rendered at its NATURAL bbox
        from the library (e.g. 0.75 inch wide) regardless of the spec's
        w/h. On a wide canvas (1180 px → 0.83x scale), the icon was tiny
        relative to its surroundings; on a small canvas (627 px → 1.7x
        scale), the icon was undersized too. Diego flagged 2026-04-25:
        "el tamaño de los iconos parecieran chicos al menos en pptx".
        """
        element = self._source_child(ref)
        self._assign_ids(element, allocate_id)
        self._copy_media_dependencies(element, ref)
        bbox = ref.get("bbox") or {}
        dx = target_x - int(bbox.get("x", 0))
        dy = target_y - int(bbox.get("y", 0))
        for node in element.findall(".//a:off", namespaces=NS):
            node.set("x", str(int(node.get("x", "0")) + dx))
            node.set("y", str(int(node.get("y", "0")) + dy))
        for node in element.findall(".//a:chOff", namespaces=NS):
            node.set("x", str(int(node.get("x", "0")) + dx))
            node.set("y", str(int(node.get("y", "0")) + dy))
        if target_cx and target_cy:
            # Resize the wrapper extent — keep chExt unchanged so child
            # cells scale automatically via the group transform.
            xfrm = element.find(".//a:xfrm", namespaces=NS)
            if xfrm is not None:
                ext = xfrm.find("a:ext", namespaces=NS)
                if ext is not None:
                    ext.set("cx", str(int(target_cx)))
                    ext.set("cy", str(int(target_cy)))
        return element

    def _copy_media_dependencies(self, element, ref: dict):
        if self._current_work_dir is None or self._current_slide_path is None:
            return
        source_rel_map = self._source_slide_relationships(ref["slide_path"])
        rid_mapping = {}
        for node in element.xpath(".//*[@r:embed]", namespaces=NS):
            old_rid = node.get(f"{{{R_NS}}}embed")
            if not old_rid:
                continue
            new_rid = rid_mapping.get(old_rid)
            if not new_rid:
                target = source_rel_map.get(old_rid)
                if not target:
                    continue
                media_rel = self._copy_media_target(ref["slide_path"], target)
                new_rid = self._add_target_slide_relationship(media_rel)
                rid_mapping[old_rid] = new_rid
            node.set(f"{{{R_NS}}}embed", new_rid)

    def _source_slide_relationships(self, slide_path: str) -> dict:
        if slide_path in self._source_rels_cache:
            return self._source_rels_cache[slide_path]
        slide_name = Path(slide_path).name
        rels_path = f"ppt/slides/_rels/{slide_name}.rels"
        with zipfile.ZipFile(self.library_path) as archive:
            try:
                rels_root = etree.fromstring(archive.read(rels_path))
            except KeyError:
                self._source_rels_cache[slide_path] = {}
                return {}
        rel_map = {}
        for rel in rels_root.findall(f"{{{PKG_REL_NS}}}Relationship"):
            rel_map[rel.get("Id")] = rel.get("Target")
        self._source_rels_cache[slide_path] = rel_map
        return rel_map

    def _copy_media_target(self, source_slide_path: str, rel_target: str) -> str:
        source_slide_dir = PurePosixPath(source_slide_path).parent
        source_media_path = str((source_slide_dir / rel_target).as_posix())
        source_media_path = posixpath.normpath(source_media_path)
        while source_media_path.startswith("../"):
            source_media_path = source_media_path[3:]
        if not source_media_path.startswith("ppt/"):
            source_media_path = posixpath.normpath(f"ppt/{source_media_path}")

        with zipfile.ZipFile(self.library_path) as archive:
            media_bytes = archive.read(source_media_path)

        media_dir = self._current_work_dir / "ppt" / "media"
        media_dir.mkdir(parents=True, exist_ok=True)
        source_name = Path(source_media_path).name
        dest_path = media_dir / source_name
        if dest_path.exists() and dest_path.read_bytes() != media_bytes:
            stem = dest_path.stem
            suffix = dest_path.suffix
            counter = 1
            while True:
                candidate = media_dir / f"{stem}_{counter}{suffix}"
                if not candidate.exists() or candidate.read_bytes() == media_bytes:
                    dest_path = candidate
                    break
                counter += 1
        if not dest_path.exists():
            dest_path.write_bytes(media_bytes)
        # PowerPoint refuses to open the deck (and prompts to "repair" it) if
        # any embedded media extension is missing from [Content_Types].xml's
        # Default list. Some OCI_Icons.pptx icons are SVG-backed, so we must
        # ensure every extension we copy in is declared.
        self._ensure_content_type_default(dest_path.suffix.lstrip(".").lower())
        return f"../media/{dest_path.name}"

    _CONTENT_TYPE_BY_EXT = {
        "svg": "image/svg+xml",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "bmp": "image/bmp",
        "tiff": "image/tiff",
        "tif": "image/tiff",
        "emf": "image/x-emf",
        "wmf": "image/x-wmf",
        "ico": "image/x-icon",
        "webp": "image/webp",
    }

    def _ensure_content_type_default(self, extension: str) -> None:
        if not extension or self._current_work_dir is None:
            return
        content_type = self._CONTENT_TYPE_BY_EXT.get(extension)
        if not content_type:
            return
        ct_path = self._current_work_dir / "[Content_Types].xml"
        if not ct_path.exists():
            return
        ct_tree = etree.parse(str(ct_path))
        ct_root = ct_tree.getroot()
        ns = "http://schemas.openxmlformats.org/package/2006/content-types"
        for default in ct_root.findall(f"{{{ns}}}Default"):
            if (default.get("Extension") or "").lower() == extension:
                return
        new_default = etree.SubElement(ct_root, f"{{{ns}}}Default")
        new_default.set("Extension", extension)
        new_default.set("ContentType", content_type)
        ct_tree.write(str(ct_path), encoding="UTF-8", xml_declaration=True, standalone=True)

    def _add_target_slide_relationship(self, rel_target: str) -> str:
        rels_path = self._target_slide_rels_path()
        if rels_path.exists():
            rels_tree = etree.parse(str(rels_path))
            rels_root = rels_tree.getroot()
        else:
            rels_root = etree.Element(f"{{{PKG_REL_NS}}}Relationships")
            rels_tree = etree.ElementTree(rels_root)
        existing = []
        for rel in rels_root.findall(f"{{{PKG_REL_NS}}}Relationship"):
            rid = rel.get("Id", "")
            if rid.startswith("rId") and rid[3:].isdigit():
                existing.append(int(rid[3:]))
        new_rid = f"rId{max(existing or [0]) + 1}"
        rel = etree.SubElement(rels_root, f"{{{PKG_REL_NS}}}Relationship")
        rel.set("Id", new_rid)
        rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
        rel.set("Target", rel_target)
        rels_tree.write(str(rels_path), encoding="UTF-8", xml_declaration=True)
        return new_rid

    def _target_slide_rels_path(self) -> Path:
        slide_name = self._current_slide_path.name
        rels_dir = self._current_slide_path.parent / "_rels"
        rels_dir.mkdir(parents=True, exist_ok=True)
        return rels_dir / f"{slide_name}.rels"

    def _assign_ids(self, element, allocate_id):
        for node in element.findall(".//p:cNvPr", namespaces=NS):
            node.set("id", str(allocate_id()))

    def _fallback_service_card(self, shape_id: int, x: int, y: int, cx: int, cy: int, label: str, color: str):
        xml = f"""
        <p:sp xmlns:p="{P_NS}" xmlns:a="{A_NS}">
          <p:nvSpPr>
            <p:cNvPr id="{shape_id}" name="Service Card"/>
            <p:cNvSpPr txBox="1"/>
            <p:nvPr/>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
            <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 1800"/></a:avLst></a:prstGeom>
            <a:solidFill><a:srgbClr val="FCFBFA"/></a:solidFill>
            <a:ln w="12700"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:ln>
          </p:spPr>
          <p:txBody>
            <a:bodyPr wrap="square" anchor="ctr" lIns="45720" rIns="45720" tIns="12000" bIns="12000"/>
            <a:lstStyle/>
            <a:p>
              <a:pPr algn="ctr"/>
              <a:r>
                <a:rPr sz="820" b="1">
                  <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                  <a:latin typeface="Oracle Sans"/>
                </a:rPr>
                <a:t>{self._escape_text(label)}</a:t>
              </a:r>
            </a:p>
          </p:txBody>
        </p:sp>
        """
        return etree.fromstring(xml.encode("utf-8"))

    def _container_shape(self, shape_id: int, x: int, y: int, cx: int, cy: int,
                         stroke_color: str, stroke_width: int = 12700,
                         dashed: bool = False, fill: str | None = None,
                         rounded: bool = False):
        fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
        dash_xml = "<a:prstDash val=\"dash\"/>" if dashed else "<a:prstDash val=\"solid\"/>"
        if rounded:
            geom = '<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 1800"/></a:avLst></a:prstGeom>'
        else:
            geom = '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        xml = f"""
        <p:sp xmlns:p="{P_NS}" xmlns:a="{A_NS}">
          <p:nvSpPr>
            <p:cNvPr id="{shape_id}" name="Container"/>
            <p:cNvSpPr/>
            <p:nvPr/>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
            {geom}
            {fill_xml}
            <a:ln w="{stroke_width}">
              <a:solidFill><a:srgbClr val="{stroke_color}"/></a:solidFill>
              {dash_xml}
            </a:ln>
          </p:spPr>
          <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
        </p:sp>
        """
        return etree.fromstring(xml.encode("utf-8"))

    def _label_shape(self, shape_id: int, x: int, y: int, cx: int, cy: int, text: str,
                     font_size: int = 900, color: str = "312D2A", bold: bool = True,
                     align: str = "ctr", bg: str | None = None):
        fill = f'<a:solidFill><a:srgbClr val="{bg}"/></a:solidFill>' if bg else "<a:noFill/>"
        xml = f"""
        <p:sp xmlns:p="{P_NS}" xmlns:a="{A_NS}">
          <p:nvSpPr>
            <p:cNvPr id="{shape_id}" name="Label"/>
            <p:cNvSpPr txBox="1"/>
            <p:nvPr/>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
            <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
            {fill}
            <a:ln><a:noFill/></a:ln>
          </p:spPr>
          <p:txBody>
            <a:bodyPr wrap="square" anchor="ctr" lIns="18000" rIns="18000" tIns="0" bIns="0"/>
            <a:lstStyle/>
            <a:p>
              <a:pPr algn="{align}"/>
              <a:r>
                <a:rPr sz="{font_size}" b="{1 if bold else 0}">
                  <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                  <a:latin typeface="Oracle Sans"/>
                </a:rPr>
                <a:t>{self._escape_text(text)}</a:t>
              </a:r>
            </a:p>
          </p:txBody>
        </p:sp>
        """
        return etree.fromstring(xml.encode("utf-8"))

    def _arrow_shape(self, shape_id: int, x1: int, y1: int, x2: int, y2: int, color: str,
                     width_emu: int = 12700, dashed: bool = False, arrow: bool = True):
        x = min(x1, x2)
        y = min(y1, y2)
        cx = max(abs(x2 - x1), 1)
        cy = max(abs(y2 - y1), 1)
        flip_h = ' flipH="1"' if x2 < x1 else ""
        flip_v = ' flipV="1"' if y2 < y1 else ""
        dash = "<a:prstDash val=\"dash\"/>" if dashed else "<a:prstDash val=\"solid\"/>"
        arrow_xml = '<a:tailEnd type="triangle" w="sm" len="sm"/>' if arrow else ""
        xml = f"""
        <p:cxnSp xmlns:p="{P_NS}" xmlns:a="{A_NS}">
          <p:nvCxnSpPr>
            <p:cNvPr id="{shape_id}" name="Connector"/>
            <p:cNvCxnSpPr/>
            <p:nvPr/>
          </p:nvCxnSpPr>
          <p:spPr>
            <a:xfrm{flip_h}{flip_v}><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
            <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
            <a:ln w="{width_emu}">
              <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
              {dash}
              {arrow_xml}
            </a:ln>
          </p:spPr>
        </p:cxnSp>
        """
        return etree.fromstring(xml.encode("utf-8"))

    def _bent_connector_shape(self, shape_id: int, points: list[tuple[int, int]],
                              color: str, width_emu: int = 12700,
                              dashed: bool = False, arrow: bool = True):
        """Render a polyline as a SINGLE OOXML bent connector.

        OCI_Icons.pptx (the template) uses ``bentConnector2/3/5`` for
        elbow paths, NOT a sequence of separate straight ``line``
        shapes. The latter renders as disjoint segments at the bends —
        what Diego flagged: "la distribucion/forma de las flechas me
        gusta mas como quedo en drawio que en pptx" (2026-04-25).

        We use:
          • 2 points (1 segment)  → straightConnector1 (single line)
          • 3 points (1 elbow)    → bentConnector2 (1 bend)
          • 4 points (2 elbows)   → bentConnector3 (2 bends, S-shape)
          • 5+ points             → bentConnector5 (4 bends)

        ``flipH``/``flipV`` are derived from the path's overall
        direction so the bent connector lays out source→target the way
        the spec authored it.
        """
        if len(points) < 2:
            return None
        x_first, y_first = points[0]
        x_last, y_last = points[-1]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        x = min(xs)
        y = min(ys)
        cx = max(max(xs) - x, 1)
        cy = max(max(ys) - y, 1)
        flip_h = ' flipH="1"' if x_last < x_first else ""
        flip_v = ' flipV="1"' if y_last < y_first else ""
        n = len(points)
        if n == 2:
            prst = "straightConnector1"
        elif n == 3:
            prst = "bentConnector2"
        elif n == 4:
            prst = "bentConnector3"
        else:
            prst = "bentConnector5"
        dash = "<a:prstDash val=\"dash\"/>" if dashed else "<a:prstDash val=\"solid\"/>"
        arrow_xml = '<a:tailEnd type="triangle" w="sm" len="sm"/>' if arrow else ""
        xml = f"""
        <p:cxnSp xmlns:p="{P_NS}" xmlns:a="{A_NS}">
          <p:nvCxnSpPr>
            <p:cNvPr id="{shape_id}" name="Connector"/>
            <p:cNvCxnSpPr/>
            <p:nvPr/>
          </p:nvCxnSpPr>
          <p:spPr>
            <a:xfrm{flip_h}{flip_v}><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
            <a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>
            <a:ln w="{width_emu}">
              <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
              {dash}
              {arrow_xml}
            </a:ln>
          </p:spPr>
        </p:cxnSp>
        """
        return etree.fromstring(xml.encode("utf-8"))

    def _badge_shape(self, shape_id: int, x: int, y: int, size: int, text: str):
        xml = f"""
        <p:sp xmlns:p="{P_NS}" xmlns:a="{A_NS}">
          <p:nvSpPr><p:cNvPr id="{shape_id}" name="Flow Badge"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{size}" cy="{size}"/></a:xfrm>
            <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
            <a:solidFill><a:srgbClr val="70665E"/></a:solidFill>
            <a:ln><a:noFill/></a:ln>
          </p:spPr>
          <p:txBody>
            <a:bodyPr wrap="square" anchor="ctr" lIns="0" rIns="0" tIns="0" bIns="0"/>
            <a:lstStyle/>
            <a:p><a:pPr algn="ctr"/><a:r><a:rPr sz="720" b="1">
              <a:solidFill><a:srgbClr val="FCFBFA"/></a:solidFill>
              <a:latin typeface="Oracle Sans"/>
            </a:rPr><a:t>{self._escape_text(text)}</a:t></a:r></a:p>
          </p:txBody>
        </p:sp>
        """
        return etree.fromstring(xml.encode("utf-8"))

    def _escape_text(self, text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
