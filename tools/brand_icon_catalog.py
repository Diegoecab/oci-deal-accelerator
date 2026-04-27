#!/usr/bin/env python3
"""Shared resolver for non-OCI brand icons used by drawio and PPTX.

Policy:
- Prefer officially downloaded vendor assets when committed locally.
- Fall back to vetted local assets only when an official asset is not
  available or practical to automate.
- Never depend on remote URLs at render time.
"""

from __future__ import annotations

import base64
import re
import struct
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "config" / "brand-icons.yaml"
DEFAULT_RESOLUTION_ORDER = (
    "official_svg",
    "official_png",
    "fallback_svg",
    "fallback_png",
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _slug(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


@lru_cache(maxsize=1)
def _load_catalog() -> dict[str, Any]:
    raw = yaml.safe_load(DEFAULT_CATALOG_PATH.read_text(encoding="utf-8")) or {}
    icons = raw.get("icons") or {}
    alias_map: dict[str, str] = {}
    normalized_icons: dict[str, dict[str, Any]] = {}
    for key, entry in icons.items():
        icon_id = _slug(key)
        normalized = dict(entry or {})
        normalized["id"] = icon_id
        normalized_icons[icon_id] = normalized
        alias_map[icon_id] = icon_id
        for alias in normalized.get("aliases") or []:
            alias_map[_slug(alias)] = icon_id
    return {
        "resolution_order": tuple(raw.get("resolution_order") or DEFAULT_RESOLUTION_ORDER),
        "icons": normalized_icons,
        "aliases": alias_map,
    }


def resolve_brand_icon(brand_icon: str | None) -> dict[str, Any] | None:
    slug = _slug(brand_icon)
    if not slug:
        return None
    catalog = _load_catalog()
    icon_id = catalog["aliases"].get(slug)
    if not icon_id:
        return None
    entry = dict(catalog["icons"][icon_id])
    for key in catalog["resolution_order"]:
        rel_path = entry.get(key)
        if not rel_path:
            continue
        path = PROJECT_ROOT / rel_path
        if path.exists():
            suffix = path.suffix.lower()
            return {
                **entry,
                "path": path,
                "resolution_key": key,
                "format": suffix.lstrip("."),
                "mime_type": _mime_type_for_suffix(suffix),
            }
    return None


def available_brand_icons() -> list[str]:
    return sorted(_load_catalog()["icons"].keys())


def brand_icon_data_uri(brand_icon: str | None) -> str | None:
    resolved = resolve_brand_icon(brand_icon)
    if not resolved:
        return None
    data = resolved["path"].read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    # draw.io stores inline image payloads in mxCell styles as
    # image=data:image/<type>,<base64> (without ";base64"). Keeping the
    # payload in that draw.io-native form avoids the semicolon breaking the
    # style parser, which treats ";" as a style key separator.
    return f"data:{resolved['mime_type']},{encoded}"


def brand_icon_size(brand_icon: str | None) -> tuple[int, int] | None:
    resolved = resolve_brand_icon(brand_icon)
    if not resolved:
        return None
    data = resolved["path"].read_bytes()
    fmt = resolved["format"]
    if fmt == "svg":
        return _svg_dimensions(data)
    if fmt == "png":
        return _png_dimensions(data)
    return None


def drawio_icon_entry(brand_icon: str | None) -> dict[str, Any] | None:
    data_uri = brand_icon_data_uri(brand_icon)
    size = brand_icon_size(brand_icon)
    if not data_uri or not size:
        return None
    width, height = size
    cell = (
        f'<mxCell id="1" value="" '
        f'style="shape=image;aspect=fixed;imageAspect=1;image={data_uri};'
        f'strokeColor=none;fillColor=none;html=1;" '
        f'vertex="1" parent="1">'
        f'<mxGeometry x="0" y="0" width="{width}" height="{height}" as="geometry" />'
        f'</mxCell>'
    )
    return {"w": width, "h": height, "cells": [cell]}


def brand_icon_png_bytes(brand_icon: str | None) -> bytes | None:
    resolved = resolve_brand_icon(brand_icon)
    if not resolved:
        return None
    data = resolved["path"].read_bytes()
    if resolved["format"] == "png":
        return data
    if resolved["format"] == "svg":
        import cairosvg

        return cairosvg.svg2png(bytestring=data)
    return None


def brand_icon_media_name(brand_icon: str | None, extension: str = "png") -> str:
    resolved = resolve_brand_icon(brand_icon)
    stem = _slug((resolved or {}).get("id") or brand_icon or "brand-icon")
    return f"{stem}.{extension.lstrip('.')}"


def _mime_type_for_suffix(suffix: str) -> str:
    if suffix == ".svg":
        return "image/svg+xml"
    if suffix == ".png":
        return "image/png"
    return "application/octet-stream"


def _svg_dimensions(svg_bytes: bytes) -> tuple[int, int]:
    root = ET.fromstring(svg_bytes)
    view_box = root.get("viewBox")
    if view_box:
        parts = view_box.replace(",", " ").split()
        if len(parts) == 4:
            width = max(int(round(float(parts[2]))), 1)
            height = max(int(round(float(parts[3]))), 1)
            return width, height
    width = _svg_length(root.get("width"))
    height = _svg_length(root.get("height"))
    if width and height:
        return width, height
    return (24, 24)


def _svg_length(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", value)
    if not match:
        return None
    return max(int(round(float(match.group(1)))), 1)


def _png_dimensions(png_bytes: bytes) -> tuple[int, int]:
    if png_bytes[:8] != PNG_SIGNATURE:
        raise ValueError("Invalid PNG signature")
    if png_bytes[12:16] != b"IHDR":
        raise ValueError("PNG missing IHDR chunk")
    width, height = struct.unpack(">II", png_bytes[16:24])
    return max(int(width), 1), max(int(height), 1)
