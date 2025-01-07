# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Project information
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from importlib.metadata import version as _version


project = "license_tools"
copyright = "stefan6419846"
author = "stefan6419846"
release = _version("license_tools")

# General configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

nitpicky = True


# Options for HTML output
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

master_doc = "index"
html_theme = "furo"
html_static_path = ["_static"]


# Options for cross-referencing.

autoclass_content = "both"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "fontTools": ("https://fonttools.readthedocs.io/en/latest/", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
}
