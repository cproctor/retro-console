"""Sphinx configuration for retro-console documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "Retro Console"
author = "Chris Proctor"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

html_theme = "sphinx_rtd_theme"
html_static_path = []
