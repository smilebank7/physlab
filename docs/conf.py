"""Sphinx configuration for the physlab API reference."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

project = "physlab"
author = "Jhin"
copyright = "2026, Jhin"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

source_suffix = {
    ".md": "markdown",
}
master_doc = "index"
exclude_patterns = ["_build"]
html_theme = "furo"
html_title = "physlab API"

autodoc_typehints = "description"
autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = True

linkcheck_ignore = [
    r"https://github\.com/.*/actions/workflows/.*",
    r"https://img\.shields\.io/.*",
]
