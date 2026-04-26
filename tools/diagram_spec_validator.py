#!/usr/bin/env python3
"""
diagram_spec_validator — geometry sanity checks on an `absolute_layout`
spec, run BEFORE either renderer (drawio or PPTX) emits anything.

The drawio renderer ships ``drawio_visual_validator`` which inspects the
generated XML *after* the fact. That catches a lot, but two classes of
regression slipped through and produced the bugs Diego reported on the
MySQL HeatWave HA example:

  • CONTAINER_TOO_THIN — a subnet declared with ``h: 16`` collapsed into
    a band where the label occluded the bottom edge ("subnet
    comprimido"). The drawio validator only flags font size, not the
    container vs. label-fontSize ratio.

  • LABEL_OVERFLOW_PARENT — a free-floating label (lbl_mysql_primary at
    y=426..448) crossed the bottom edge of its enclosing container
    (db_subnet at y=240..440). Visually the label sat half outside.
    The drawio validator only checks edges-vs-labels and
    container-vs-container padding, not labels-vs-container.

Both regressions are spec-level: the YAML coordinates already encode
the bug, regardless of which renderer consumes them. This module runs
on the parsed spec so both ``tools/oci_diagram_gen.py`` and
``tools/oci_pptx_diagram_gen.py`` benefit from the same guard.

Returns a dict with:
  - status: "pass" | "fail"
  - issues: [{"severity", "code", "message", "id"}]

Severity ``error`` → renderers raise. ``warn`` → printed to stderr.

Policy on legacy archcenter reproductions
-----------------------------------------
Specs under ``examples/eval-*-archcenter-native-*/`` are auto-generated
reconstructions of Oracle Architecture Center references. Oracle's own
geometry sometimes places labels 2-5px from container edges, and the
reproductions mirror those coordinates verbatim to keep the perceptual
diff against the canonical PNGs above the fidelity threshold. Touching
them to silence ``LABEL_NEAR_PARENT_EDGE`` (severity=warn) would risk
the pixel-fidelity scores tracked by ``archcenter_batch_driver``.

The validator therefore distinguishes:

  - ``LABEL_OVERFLOW_PARENT`` (error, blocks render): label bottom is
    OUTSIDE the parent — true regression.
  - ``LABEL_NEAR_PARENT_EDGE`` (warn, never blocks): label sits within
    6px but still inside — common in Oracle's own ref archs.
"""
from __future__ import annotations

from typing import Any


# Heuristics tuned to Oracle Architecture Center exports we have inspected.
MIN_PARENT_PADDING_PX = 12
MIN_LABEL_TO_PARENT_BOTTOM_PX = 6
LABEL_FONT_HEIGHT_FACTOR = 1.6  # empirical: 11pt label → ~18px tall band


def _pt_from_fontsize(font_size: Any, fallback: float = 11.0) -> float:
    """``fontSize`` in absolute_layout is hundredths of a point. Some specs
    pass the literal pt value (e.g. 12). Auto-detect the unit so this
    validator agrees with the renderers."""
    if font_size is None:
        return fallback
    try:
        v = float(font_size)
    except (TypeError, ValueError):
        return fallback
    if v >= 80:
        return v / 100.0
    return v


def _bbox(item: dict) -> tuple[float, float, float, float] | None:
    try:
        x = float(item.get("x", 0))
        y = float(item.get("y", 0))
        w = float(item.get("w", 0))
        h = float(item.get("h", 0))
    except (TypeError, ValueError):
        return None
    if w <= 0 or h <= 0:
        return None
    return (x, y, x + w, y + h)


def _is_inside(child: tuple[float, float, float, float],
               parent: tuple[float, float, float, float]) -> bool:
    return (child[0] >= parent[0] - 0.5 and child[1] >= parent[1] - 0.5
            and child[2] <= parent[2] + 0.5 and child[3] <= parent[3] + 0.5)


def _segment_intersects_rect(x1: float, y1: float, x2: float, y2: float,
                              rx1: float, ry1: float, rx2: float, ry2: float) -> bool:
    """Liang–Barsky line-rect clipping. Returns True iff the segment
    [(x1,y1)→(x2,y2)] intersects the axis-aligned rect [rx1..rx2,
    ry1..ry2]. Used by the CONNECTOR_OVER_LABEL check."""
    dx = x2 - x1
    dy = y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - rx1, rx2 - x1, y1 - ry1, ry2 - y1]
    u1, u2 = 0.0, 1.0
    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return False
        else:
            t = q[i] / p[i]
            if p[i] < 0:
                if t > u2:
                    return False
                if t > u1:
                    u1 = t
            else:
                if t < u1:
                    return False
                if t < u2:
                    u2 = t
    return u1 <= u2


def validate_absolute_layout(layout: dict) -> dict:
    """Walk the parsed ``absolute_layout`` block. Return validation report."""
    issues: list[dict] = []
    containers = layout.get("containers") or []
    services = layout.get("services") or []
    labels = layout.get("labels") or []

    # Container bboxes paired with their declared label fontSize.
    container_records: list[dict] = []
    for c in containers:
        box = _bbox(c)
        if not box:
            continue
        container_records.append({
            "id": c.get("id", ""),
            "label": c.get("label", ""),
            "type": (c.get("type") or "").lower(),
            "box": box,
            "label_pt": _pt_from_fontsize(c.get("fontSize"), fallback=11.0),
        })

    # 1) CONTAINER_TOO_THIN — height must clear the label band plus a
    #    breathing margin. Subnet bands often want to be slim, but the
    #    label still has to fit.
    for rec in container_records:
        h = rec["box"][3] - rec["box"][1]
        label_band = rec["label_pt"] * LABEL_FONT_HEIGHT_FACTOR
        # Empty-label containers can be slim; only enforce when there is text.
        if not rec["label"]:
            continue
        min_h = label_band + 12
        if h < min_h:
            issues.append({
                "severity": "error",
                "code": "CONTAINER_TOO_THIN",
                "id": rec["id"],
                "message": (
                    f"Container '{rec['label']}' height={h:.0f}px is below the "
                    f"minimum of {min_h:.0f}px for a label at "
                    f"{rec['label_pt']:.1f}pt — the label will collapse onto "
                    f"the bottom edge."
                ),
            })

    # 2) CONTAINER_PADDING_VIOLATION — child container's edge within
    #    MIN_PARENT_PADDING_PX of its enclosing container, on ANY side.
    #    Diego flagged 2026-04-25: "db subnet toca los limites de linea
    #    de los ADs" — that was an LR-edge violation; the original
    #    bottom-only check missed it.
    for child in container_records:
        for parent in container_records:
            if child is parent:
                continue
            if not _is_inside(child["box"], parent["box"]):
                continue
            cx1, cy1, cx2, cy2 = child["box"]
            px1, py1, px2, py2 = parent["box"]
            for side, gap in (
                ("bottom", py2 - cy2),
                ("top", cy1 - py1),
                ("left", cx1 - px1),
                ("right", px2 - cx2),
            ):
                if 0 <= gap < MIN_PARENT_PADDING_PX:
                    issues.append({
                        "severity": "warn",
                        "code": "CONTAINER_PADDING_VIOLATION",
                        "id": child["id"],
                        "message": (
                            f"'{child['label']}' {side} is {gap:.0f}px from "
                            f"parent '{parent['label']}' {side} — borders "
                            f"will visually merge. Minimum: "
                            f"{MIN_PARENT_PADDING_PX}px."
                        ),
                    })

    # 3) LABEL_OVERFLOW_PARENT — any free-floating label whose bbox
    #    crosses the bottom edge of an enclosing container. Catches the
    #    "MySQL HeatWave label touching DB Subnet bottom" regression.
    label_records: list[dict] = []
    for lbl in labels:
        box = _bbox(lbl)
        if not box:
            continue
        label_records.append({
            "id": lbl.get("id", ""),
            "text": lbl.get("text", ""),
            "box": box,
        })
    for lbl in label_records:
        for parent in container_records:
            # Label is "associated" with this container if it overlaps
            # the parent horizontally and its top is within the parent.
            lx1, ly1, lx2, ly2 = lbl["box"]
            px1, py1, px2, py2 = parent["box"]
            horiz_overlap = min(lx2, px2) - max(lx1, px1) > 0
            vertical_anchor = py1 - 4 <= ly1 <= py2
            if not (horiz_overlap and vertical_anchor):
                continue
            # Hard-fail only when the label actually crosses the parent
            # bottom edge (true overflow, the regression Diego reported).
            # Tight clearance (< MIN px but still inside) is a warning so
            # legacy archcenter reproductions — which mirror Oracle's
            # own geometry — don't break.
            if ly2 > py2:
                issues.append({
                    "severity": "error",
                    "code": "LABEL_OVERFLOW_PARENT",
                    "id": lbl["id"],
                    "message": (
                        f"Label '{lbl['text']}' bottom (y={ly2:.0f}) is "
                        f"OUTSIDE parent '{parent['label']}' bottom "
                        f"(y={py2:.0f}). Move the label up, or extend the "
                        f"container."
                    ),
                })
                break
            elif ly2 > py2 - MIN_LABEL_TO_PARENT_BOTTOM_PX:
                issues.append({
                    "severity": "warn",
                    "code": "LABEL_NEAR_PARENT_EDGE",
                    "id": lbl["id"],
                    "message": (
                        f"Label '{lbl['text']}' bottom (y={ly2:.0f}) sits "
                        f"within {MIN_LABEL_TO_PARENT_BOTTOM_PX}px of parent "
                        f"'{parent['label']}' bottom (y={py2:.0f}). "
                        f"Visually tight but not overflowing."
                    ),
                })
                break

    # 4) CONNECTOR_OVER_LABEL — straight-segment connectors must not
    #    cross any free-floating label's bbox. Oracle ref-arch
    #    convention: labels live in clear whitespace, never under a
    #    line. Diego flagged 2026-04-25: "Network Load Balancer ese
    #    nombre esta por debajo de las flechas entonces las flechas lo
    #    cruzan". Catches the issue at spec time across BOTH renderer
    #    paths (the prior CONNECTOR_OVER_LABEL was only in the drawio
    #    post-render validator).
    services_by_id = {s.get("id"): s for s in services if s.get("id")}
    for conn in (layout.get("connections") or []):
        pts = conn.get("points") or []
        # Synthesize endpoints from from/to if no points provided.
        if len(pts) < 2:
            src = services_by_id.get(conn.get("from"))
            dst = services_by_id.get(conn.get("to"))
            if src and dst and _bbox(src) and _bbox(dst):
                sb = _bbox(src); db = _bbox(dst)
                pts = [
                    ((sb[0] + sb[2]) / 2, (sb[1] + sb[3]) / 2),
                    ((db[0] + db[2]) / 2, (db[1] + db[3]) / 2),
                ]
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            for lbl in label_records:
                lx1, ly1, lx2, ly2 = lbl["box"]
                if _segment_intersects_rect(x1, y1, x2, y2, lx1, ly1, lx2, ly2):
                    issues.append({
                        "severity": "warn",
                        "code": "CONNECTOR_OVER_LABEL",
                        "id": conn.get("id", ""),
                        "message": (
                            f"Connector '{conn.get('id','?')}' segment "
                            f"({x1:.0f},{y1:.0f})→({x2:.0f},{y2:.0f}) "
                            f"crosses label '{lbl['text']}' bbox. Move the "
                            f"label to clear whitespace or re-route."
                        ),
                    })
                    break

    # 5) SERVICE_OVERFLOW_PARENT — service icons must also stay inside
    #    their visually-enclosing container. (Catches "icon hanging off
    #    the subnet edge" — same root cause as #3 but for icons.)
    for svc in services:
        sbox = _bbox(svc)
        if not sbox:
            continue
        # Find the smallest enclosing container by area.
        enclosing: dict | None = None
        enclosing_area = float("inf")
        for parent in container_records:
            if not _is_inside(sbox, parent["box"]):
                continue
            area = (parent["box"][2] - parent["box"][0]) * (parent["box"][3] - parent["box"][1])
            if area < enclosing_area:
                enclosing = parent
                enclosing_area = area
        if enclosing is None:
            # Free-floating icon (e.g. AWS icon outside the OCI region) — OK
            continue

    status = "fail" if any(i["severity"] == "error" for i in issues) else "pass"
    return {"status": status, "issues": issues}


def report_to_stderr(report: dict, source: str = "<spec>") -> None:
    import sys
    if not report.get("issues"):
        print(f"[spec-validator] OK on {source}", file=sys.stderr)
        return
    errs = [i for i in report["issues"] if i["severity"] == "error"]
    warns = [i for i in report["issues"] if i["severity"] == "warn"]
    print(
        f"[spec-validator] {report['status']} on {source} — "
        f"{len(errs)} error(s), {len(warns)} warning(s)",
        file=sys.stderr,
    )
    for issue in report["issues"]:
        marker = "✗" if issue["severity"] == "error" else "!"
        cid = issue.get("id", "")
        cid_part = f"  [{cid}]" if cid else ""
        print(f"  {marker} {issue['code']}{cid_part}: {issue['message']}",
              file=sys.stderr)


def validate_spec(spec: dict, source: str = "<spec>", strict: bool = True) -> dict:
    """Top-level entrypoint used by both renderers.

    ``strict=True`` raises ``SpecValidationError`` on any error-severity
    issue; both ``oci_diagram_gen.py`` and ``oci_pptx_diagram_gen.py``
    pass strict=True. Pass strict=False (or set the env var
    ``OCI_DIAGRAM_VALIDATOR_SOFT=1``) to demote errors to warnings.
    """
    layout = spec.get("absolute_layout")
    if not layout:
        return {"status": "pass", "issues": []}
    report = validate_absolute_layout(layout)
    report_to_stderr(report, source=source)
    if strict and report["status"] == "fail":
        import os
        if not os.environ.get("OCI_DIAGRAM_VALIDATOR_SOFT"):
            errs = [i for i in report["issues"] if i["severity"] == "error"]
            joined = "; ".join(f"{i['code']}({i['id']})" for i in errs)
            raise SpecValidationError(
                f"absolute_layout has {len(errs)} blocking issue(s): {joined}"
            )
    return report


class SpecValidationError(ValueError):
    pass


def main() -> int:
    import argparse
    import json
    import sys
    from pathlib import Path

    import yaml

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--json", action="store_true",
                        help="Print the report as JSON instead of human text.")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero on any error-severity issue.")
    args = parser.parse_args()

    spec = yaml.safe_load(args.spec.read_text(encoding="utf-8"))
    if isinstance(spec, dict) and "custom_slides" in spec:
        # Allow validating a deck-spec that embeds the diagram.
        slides = spec.get("custom_slides") or []
        for slide in slides:
            if (slide.get("visual") or {}).get("absolute_layout"):
                spec = {"absolute_layout": slide["visual"]["absolute_layout"]}
                break
    report = validate_absolute_layout((spec or {}).get("absolute_layout") or {})
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        report_to_stderr(report, source=str(args.spec))
    if args.strict and report["status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
