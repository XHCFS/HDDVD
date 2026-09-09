# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path
import shutil

_SPEC = Path(__file__).resolve().parents[1] / "spec" / "advanced"
_HERE = Path(__file__).resolve().parent
for _name in (
    "01_volume.md",
    "02_discid.md",
    "03_playlist.md",
    "04_aca.md",
    "05_manifest_hdi.md",
    "06_vti.md",
    "07_map.md",
    "08_evo.md",
    "09_aacs.md",
    "10_playback.md",
    "11_gaps.md",
    "12_hdi_scripting_abi.md",
    "13_references.md",
):
    shutil.copy(_SPEC / _name, _HERE / _name)

project = "HD DVD Advanced Content"
copyright = "Working specification"
author = "HD DVD Advanced Content"
release = "0.1"
version = "0.1"

extensions = [
    "myst_parser",
    "sphinxcontrib.mermaid",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "strikethrough",
]
myst_heading_anchors = 3

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "search.html",
    "genindex.html",
    "print",
    "_mermaid_ink.py",
]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = "HD DVD Advanced Content"
html_show_sphinx = True
html_show_sourcelink = True
html_copy_source = True

html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "includehidden": True,
    "titles_only": False,
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
}

html_context = {
    "display_github": False,
}

# Rasterise Mermaid so EPUB and print HTML keep the playback flowcharts.
mermaid_cmd = sys.executable + " " + str(Path(__file__).resolve().parent / "_mermaid_ink.py")
mermaid_cmd_shell = True
mermaid_output_format = "svg"

epub_basename = "HD-DVD-Advanced-Content"
epub_title = "HD DVD-Video Advanced Content Format Specification"
epub_author = "HD DVD Advanced Content"
epub_publisher = "HD DVD Advanced Content"
epub_language = "en"
epub_theme = "epub"
epub_show_urls = "footnote"
epub_tocdepth = 3
epub_tocdup = False
epub_use_index = False
