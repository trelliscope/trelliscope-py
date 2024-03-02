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
    "sphinx.ext.extlinks",
    "sphinx.ext.napoleon",  # to autodocument google-style docstrings
    "sphinx.ext.githubpages",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Napoleon settings
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
# napoleon_use_admonition_for_notes = False
# napoleon_use_admonition_for_references = False
# napoleon_use_ivar = False
# napoleon_use_param = True
# napoleon_use_rtype = True
# napoleon_preprocess_types = False
# napoleon_type_aliases = None
# napoleon_attr_annotations = True

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
}
autoclass_content = "class"
autodoc_typehints = "signature"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_static_path = ["_static"]

# html_favicon = 'favicon.svg'
html_title = project + " version " + release
# html_theme = "sphinx_rtd_theme"
html_theme = "sphinx_book_theme"
html_theme_options = {
    "show_toc_level": 3  # depth of right-sidebar toc
}

# pygments_style, pygments_dark_style = "sphinx", "monokai"

nbsphinx_execute = "always"  # set this to 'never' or 'auto' for local development.
# nbsphinx_execute = "never"  # set this to 'never' or 'auto' for local development.
nbsphinx_kernel_name = "python3"

intersphinx_mapping = {
    "plotly": ("https://plotly.com/python-api-reference/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "python": ("https://docs.python.org/3", None),
    "packaging": ("https://packaging.pypa.io/en/latest", None),
}
