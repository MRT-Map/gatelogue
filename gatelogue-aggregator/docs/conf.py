# noqa
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from gatelogue_aggregator.__about__ import __version__

project = "gatelogue-aggregator"
copyright = "2024, MRT Mapping Services"  # noqa: A001
author = "MRT Mapping Services"
version = __version__
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_rtd_theme",
    "sphinxcontrib.programoutput",
    "sphinx_codeautolink",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
]
autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "bs4": ("https://www.crummy.com/software/BeautifulSoup/bs4/doc/", None),
    "rustworkx": ("https://www.rustworkx.org/", None),
    "msgspec": ("https://jcristharif.com/msgspec/", None)
}
html_baseurl = "https://mrt-map.github.io/gatelogue/docs"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
