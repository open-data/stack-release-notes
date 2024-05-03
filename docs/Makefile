# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# NOTE: you may need to run `export LC_ALL=C` before building

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Build HTML files without caches.
dev:
	rm -rfv "$(BUILDDIR)/doctrees"
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	rm -rfv "$(BUILDDIR)/doctrees"
	rm -fv "$(BUILDDIR)/html/genindex.html"
	rm -fv "$(BUILDDIR)/html/search.html"
	rm -fv "$(BUILDDIR)/html/searchindex.js"

.PHONY: dev Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	rm -fv "$(BUILDDIR)/html/genindex.html"
	rm -fv "$(BUILDDIR)/html/search.html"
	rm -fv "$(BUILDDIR)/html/searchindex.js"
