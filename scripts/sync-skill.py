#!/usr/bin/env python3
"""
Sync SKILL.md (root, source of truth) to .agents/skills/oci-deal-accelerator/SKILL.md.

The Codex copy under .agents/ must be byte-identical to the root SKILL.md
except for an auto-generated banner inserted after the YAML frontmatter.

Usage:
    python scripts/sync-skill.py            # write the .agents/ copy
    python scripts/sync-skill.py --check    # exit 1 if out of sync (for CI/lint)
"""

import argparse
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SOURCE = os.path.join(PROJECT_ROOT, "SKILL.md")
TARGET = os.path.join(
    PROJECT_ROOT, ".agents", "skills", "oci-deal-accelerator", "SKILL.md"
)

BANNER = (
    "<!-- AUTO-GENERATED FROM /SKILL.md — do not edit directly. "
    "Run `python scripts/sync-skill.py` to regenerate. -->\n"
)


def render() -> str:
    """Read root SKILL.md and return the .agents/ version with banner injected."""
    with open(SOURCE, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Inject banner after the closing `---` of the YAML frontmatter, if present.
    if content.startswith("---\n"):
        end = content.find("\n---\n", 4)
        if end != -1:
            head = content[: end + len("\n---\n")]
            tail = content[end + len("\n---\n") :]
            return head + "\n" + BANNER + tail

    # No frontmatter — prepend banner.
    return BANNER + content


def cmd_check() -> int:
    expected = render()
    if not os.path.isfile(TARGET):
        print(f"sync-skill: target missing: {TARGET}")
        return 1
    with open(TARGET, "r", encoding="utf-8") as fh:
        actual = fh.read()
    if actual == expected:
        print("sync-skill: OK (in sync)")
        return 0
    print("sync-skill: OUT OF SYNC")
    print(f"  source: {SOURCE}")
    print(f"  target: {TARGET}")
    print("  run: python scripts/sync-skill.py")
    return 1


def cmd_write() -> int:
    expected = render()
    os.makedirs(os.path.dirname(TARGET), exist_ok=True)
    with open(TARGET, "w", encoding="utf-8") as fh:
        fh.write(expected)
    print(f"sync-skill: wrote {os.path.relpath(TARGET, PROJECT_ROOT)} "
          f"({len(expected.splitlines())} lines)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync root SKILL.md to .agents/")
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if out of sync; do not write.")
    args = parser.parse_args()
    return cmd_check() if args.check else cmd_write()


if __name__ == "__main__":
    sys.exit(main())
