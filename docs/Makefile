# Sphinx build for the HD DVD Advanced Content format specification.
# Uses the repo venv if present, else the sphinx-build on PATH.
SPHINXBUILD   ?= $(firstword $(wildcard ../.venv/bin/sphinx-build) sphinx-build)
SOURCEDIR     = .
BUILDDIR      = _build

# `make html`       -> _build/html/index.html
# `make singlehtml` -> _build/singlehtml/index.html (one printable page)
# `make epub`       -> _build/epub/HD-DVD-Advanced-Content.epub
# `make github`     -> site + print/ + EPUB for GitHub Pages (/docs)
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

github: html singlehtml epub
	cp -a "$(BUILDDIR)/html/." .
	rm -rf print
	mkdir -p print
	cp -a "$(BUILDDIR)/singlehtml/." print/
	rm -rf print/.doctrees print/.buildinfo
	cp "$(BUILDDIR)/epub/HD-DVD-Advanced-Content.epub" HD-DVD-Advanced-Content.epub
	touch .nojekyll print/.nojekyll

.PHONY: help github Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
