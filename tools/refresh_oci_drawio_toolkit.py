#!/usr/bin/env python3
"""
refresh_oci_drawio_toolkit — fetch the official Oracle Style Guide for
Draw.io and place its assets under ``kb/diagram/assets/oci-toolkit-drawio/``.

Source (canonical, 2026-04):
  https://docs.oracle.com/iaas/Content/Resources/Assets/OCI-Style-Guide-for-Drawio.zip

The toolkit ships:
  - OCI Architecture Diagram Toolkit v24.2.drawio  (~4.5 MB)
  - OCI Library.xml                                (~1.4 MB — drawio
    shape library, drop into Extras → Edit Library)
  - Read-ME.drawio                                 (style guide)

These are the sources of truth for:
  - Container styles (region/AD/VCN/subnet) — already extracted into
    kb/diagram/oci-toolkit-styles.yaml
  - Service icon stencils — extracted into kb/diagram/oci-icons.json
  - Connector styles — also in kb/diagram/oci-toolkit-styles.yaml

Run this script when:
  - Oracle ships a new version (look for v24.x or v25.x in the zip).
  - You need to rebuild oci-icons.json after editing extraction logic.
"""

from __future__ import annotations

import argparse
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

DEFAULT_URL = "https://docs.oracle.com/iaas/Content/Resources/Assets/OCI-Style-Guide-for-Drawio.zip"
DEFAULT_DEST = Path(__file__).resolve().parent.parent / "kb" / "diagram" / "assets" / "oci-toolkit-drawio"


def fetch_zip(url: str) -> bytes:
    print(f"Fetching {url}", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    parser.add_argument("--source", type=Path, default=None,
                        help="Local path to a pre-downloaded zip (skips network).")
    args = parser.parse_args()

    blob = args.source.read_bytes() if args.source else fetch_zip(args.url)
    args.dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for member in z.namelist():
            if member.endswith("/"):
                continue
            target = args.dest / Path(member).name
            target.write_bytes(z.read(member))
            print(f"  wrote {target.relative_to(args.dest.parent.parent.parent)}", file=sys.stderr)
    print(f"\nToolkit refreshed under {args.dest}", file=sys.stderr)


if __name__ == "__main__":
    main()
