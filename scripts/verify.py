#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = [
    re.compile(r"sk-proj-[A-Za-z0-9_-]{12,}"),
    re.compile(r"gh[opusr]_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".txt"}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if sorted(p.name for p in (ROOT / ".codex-plugin").iterdir()) != ["plugin.json"]:
        fail(".codex-plugin must contain only plugin.json")

    for path in ROOT.rglob("*"):
        if path.is_symlink():
            fail(f"symlink not allowed in package: {path.relative_to(ROOT)}")
        if path.is_dir() and path.name == "__pycache__":
            fail(f"bytecode cache present: {path.relative_to(ROOT)}")
        if path.is_file() and path.suffix == ".pyc":
            fail(f"bytecode present: {path.relative_to(ROOT)}")
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8")
            if chr(0x2014) in text:
                fail(f"forbidden em dash present: {path.relative_to(ROOT)}")
            mac_user_prefix = "/" + "Users" + "/"
            linux_home_pattern = re.compile("/" + r"home/[^<\s]+/")
            if mac_user_prefix in text or linux_home_pattern.search(text):
                fail(f"local absolute user path present: {path.relative_to(ROOT)}")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    fail(f"secret-shaped value present: {path.relative_to(ROOT)}")

    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    skill = ROOT / "skills" / "satisfy-your-agent" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\nname: satisfy-your-agent\ndescription:"):
        fail("SKILL.md frontmatter is malformed")

    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-v"], check=True)
    subprocess.run([sys.executable, str(ROOT / "evals" / "metric_pack" / "satisfy_metric_pack.py"), str(ROOT)], check=True)
    print("VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
