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
    "14_markup.md",
):
    shutil.copy(_SPEC / _name, _HERE / _name)

# Standard Content (archival appendix). Its sheets share the base names of the
# Advanced sheets, so they are copied flat with a "std_" prefix and their
# cross-links are rewritten to the flattened docs layout:
#   intra-set links  0N_x.md / INDEX.md      -> std_0N_x.md / std_INDEX.md
#   links to Advanced ../advanced/0N_x.md    -> 0N_x.md (Advanced is flat at root)
#   links to research notes ../clean/*.md    -> plain text (not part of the build)
import re as _re

_STD = Path(__file__).resolve().parents[1] / "spec" / "standard"
_std_names = [
    "INDEX.md",
    "01_volume.md",
    "02_vmgi.md",
    "03_vtsi.md",
    "04_pgc_vm.md",
    "05_evob_nv.md",
    "06_playback.md",
    "07_aacs.md",
    "08_gaps.md",
    "09_references.md",
]
for _name in _std_names:
    _text = (_STD / _name).read_text(encoding="utf-8")
    # 1) prefix intra-set links (not ../, http, #, or already std_)
    _text = _re.sub(r"\]\((?!\.\./|https?:|#|std_)([0-9A-Za-z_]+\.md)", r"](std_\1", _text)
    # 2) flatten links into the Advanced set
    _text = _text.replace("](../advanced/", "](")
    # 3) neutralise links to research notes: [label](../clean/x.md) -> `label`
    _text = _re.sub(r"\[([^\]]+)\]\(\.\./clean/[^)]+\)", r"`\1`", _text)
    (_HERE / f"std_{_name}").write_text(_text, encoding="utf-8")

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
html_css_files = ["overrides.css"]
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

# Rasterise Mermaid to PNG so every builder (HTML, single-page print, EPUB)
# embeds the playback flowcharts as <img>; the SVG/<object> path does not render
# in EPUB readers or print-to-PDF.
mermaid_cmd = sys.executable + " " + str(Path(__file__).resolve().parent / "_mermaid_ink.py")
mermaid_cmd_shell = "False"
mermaid_output_format = "png"

# EPUB packages the RTD theme web fonts, whose mimetypes the epub builder does not
# recognise; the fonts still embed. Silence that cosmetic noise.
suppress_warnings = ["epub.unknown_project_files"]

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
