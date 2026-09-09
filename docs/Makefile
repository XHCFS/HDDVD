# Sphinx build for the HD DVD Advanced Content format specification.
# Uses the repo venv if present, else the sphinx-build on PATH.
SPHINXBUILD   ?= $(firstword $(wildcard ../.venv/bin/sphinx-build) sphinx-build)
SOURCEDIR     = .
BUILDDIR      = _build

# `make html`       -> _build/html/index.html
# `make github`     -> copy that site into this directory for GitHub Pages (/docs)
# `make singlehtml` -> _build/singlehtml/index.html (one printable page, print-to-PDF)
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

github: html
	cp -a "$(BUILDDIR)/html/." .
	touch .nojekyll

.PHONY: help github Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
