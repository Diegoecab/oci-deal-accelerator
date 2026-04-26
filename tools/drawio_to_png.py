#!/usr/bin/env python3
"""
drawio_to_png — render a .drawio file to PNG using drawio.exe (Windows
under WSL) or a Linux drawio binary if available.

Why this matters: the SVG-based fidelity eval uses Oracle's bundled
SVG companion (same source as the official drawio). It validates that
the *verbatim* drawio is byte-identical to the reference, but it does
NOT validate the *rebuilt* drawio (the spec → drawio path). Only by
exporting our generated drawio to PNG and diffing it against the
canonical PNG do we catch bugs introduced by the rebuild — e.g. a
700pt label that the SVG-based fidelity test never sees.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# Order matters: prefer the Windows drawio executable if available
# under WSL; fall back to a Linux binary if installed.
def _candidate_binaries() -> list[Path]:
    """Locate a draw.io binary. The skill is shared, so we *never* probe
    machine-specific WSL paths automatically — that would silently
    activate a Windows-only path on the original developer's box and
    silently disable it everywhere else. Opt-in only via:

      - ``DRAWIO_EXE`` env var (full path to the binary), or
      - a ``drawio`` / ``draw.io`` binary on PATH.
    """
    cands: list[Path] = []
    env_path = os.environ.get("DRAWIO_EXE", "")
    if env_path:
        cands.append(Path(env_path))
    for name in ("drawio", "draw.io"):
        which = shutil.which(name)
        if which:
            cands.append(Path(which))
    return cands


def find_drawio_binary() -> Path | None:
    for p in _candidate_binaries():
        if p.exists():
            return p
    return None


def _to_windows_path(path: Path) -> str:
    """Map a /mnt/c/... path to C:\\... so drawio.exe (running under
    Windows from WSL) can read/write it."""
    abs_path = str(path.resolve())
    if abs_path.startswith("/mnt/"):
        # /mnt/c/Users/... → C:\Users\...
        m = re.match(r"^/mnt/([a-zA-Z])(/.*)?$", abs_path)
        if m:
            drive = m.group(1).upper()
            rest = (m.group(2) or "").replace("/", "\\")
            return f"{drive}:{rest}"
    return abs_path


def _read_page_size(drawio_path: Path) -> tuple[int, int] | None:
    """Read pageWidth/pageHeight from the drawio so we can crop the export
    to the canvas. drawio.exe expands to fit *all* content by default; if a
    cell sits a few pixels outside the page (common for outline edges of
    Oracle stencils) the PNG ends up much wider than the diagram, which
    destroys raster fidelity comparisons.
    """
    try:
        text = Path(drawio_path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    import re as _re
    m = _re.search(r'pageWidth="(\d+)"[^>]*pageHeight="(\d+)"', text)
    if not m:
        m = _re.search(r'pageHeight="(\d+)"[^>]*pageWidth="(\d+)"', text)
        if m:
            return int(m.group(2)), int(m.group(1))
        return None
    return int(m.group(1)), int(m.group(2))


def render(drawio_path: Path, out_png: Path, scale: int = 2,
           binary: Path | None = None,
           crop_to_page: bool = True) -> None:
    binary = binary or find_drawio_binary()
    if binary is None:
        raise RuntimeError(
            "drawio binary not found. Install draw.io for Windows "
            "(/mnt/c/Program Files/draw.io/draw.io.exe) or `dnf install drawio`."
        )
    out_png.parent.mkdir(parents=True, exist_ok=True)

    page_size = _read_page_size(drawio_path) if crop_to_page else None
    width_arg = ["-s", str(scale)]
    # Note: we deliberately use the bare -s scale flag rather than
    # --width/--height. With explicit dimensions, drawio.exe's behavior
    # diverges across versions (some treat them as DPI multipliers),
    # producing renders 3-4x larger than the page. Plain -s consistently
    # yields page_w*scale × page_h*scale.
    is_windows_binary = ".exe" in str(binary)
    if is_windows_binary:
        # drawio.exe under WSL needs Windows-visible paths. Stage to a
        # /mnt/c/-rooted scratch dir if either input or output sits on a
        # WSL-only filesystem.
        project_root = Path(__file__).resolve().parent.parent
        stage_dir = project_root / "tmp" / "drawio-render-stage"
        stage_dir.mkdir(parents=True, exist_ok=True)

        def _stage(p: Path, copy_in: bool) -> Path:
            if str(p).startswith("/mnt/"):
                return p
            staged = stage_dir / p.name
            if copy_in:
                shutil.copy(p, staged)
            return staged

        staged = _stage(drawio_path, copy_in=True)
        staged_out = _stage(out_png, copy_in=False)
        # Note: deliberately NOT passing --crop. With --crop drawio.exe
        # rasterizes the bounding box of all cells, not the page — if a
        # single stencil overflows the canvas by a few pixels (common
        # with Oracle's stenciled icons), the export ends up wider than
        # the canonical PNG and similarity comparisons get destroyed by
        # the aspect-ratio mismatch.
        cmd = [
            str(binary), "-x", "-f", "png",
            *width_arg,
            "-o", _to_windows_path(staged_out),
            _to_windows_path(staged),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not staged_out.exists():
            raise RuntimeError(
                f"drawio.exe failed (rc={result.returncode}): "
                f"stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        if staged_out != out_png:
            shutil.move(staged_out, out_png)
    else:
        cmd = [
            str(binary), "-x", "-f", "png",
            "-s", str(scale),
            "-o", str(out_png),
            str(drawio_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a .drawio file to PNG.")
    parser.add_argument("--drawio", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--scale", type=int, default=2)
    args = parser.parse_args()
    render(args.drawio, args.out, scale=args.scale)
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
