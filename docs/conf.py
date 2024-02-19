# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import importlib.metadata

project = "Trelliscope-py"
copyright = "2024, Scott Burton, Ryan Hafen"
author = "Scott Burton, Ryan Hafen"
# The full version, including alpha/beta/rc tags.
release: str = importlib.metadata.version("trelliscope")
# The short X.Y version.
version: str = ".".join(release.split(".")[:2])


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",  # to include markdown files in docs directly
    "nbsphinx",  # to render notebooks as docs pages
    "sphinx.ext.napoleon",  # to autodocument google-style docstrings
    "sphinx.ext.githubpages",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Napoleon settings
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_static_path = ["_static"]

# html_favicon = 'favicon.svg'
html_title = project + " version " + release
html_theme = "sphinx_rtd_theme"
html_theme_options = {}

# Autodoc
autodoc_member_order = "bysource"
