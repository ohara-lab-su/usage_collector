"""Sphinx shared configuration for English and Japanese documentation."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
project = "usage_collector"
author = "Ohara Lab"
extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.autosummary", "sphinx.ext.napoleon", "sphinx.ext.viewcode"]
autosummary_generate = True
html_theme = "sphinx_rtd_theme"
html_static_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
master_doc = "index"
html_title = "usage_collector"
