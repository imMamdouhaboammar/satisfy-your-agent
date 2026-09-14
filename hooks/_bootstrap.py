from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def load_core():
    plugin_root = Path(os.environ.get("PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
    core_path = plugin_root / "skills" / "satisfy-your-agent" / "scripts" / "sya_core.py"
    spec = importlib.util.spec_from_file_location("sya_core", core_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runtime core from {core_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["sya_core"] = module
    spec.loader.exec_module(module)
    return module
