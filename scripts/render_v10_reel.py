#!/usr/bin/env python3
"""Backward-compatibility alias forwarding to canonical scripts.render_reel."""
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from scripts.render_reel import *

if __name__ == "__main__":
    main()
