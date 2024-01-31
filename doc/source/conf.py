# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
# sys.path.insert(0, os.path.abspath(os.path.join("..", "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))
import ddsurveys

os.environ.setdefault("SPHINX_DOC_BUILD", "1")

# -- Project information -----------------------------------------------------

project = 'DDSurveys'
copyright = '2023, Lev Velykoivanenko, Stefan Teofanovic, Kévin Huguenin, Bertil Chapuis'
author = 'Lev Velykoivanenko, Stefan Teofanovic, Kévin Huguenin, Bertil Chapuis'

# The full version, including alpha/beta/rc tags
release = ddsurveys.__version__
version = release  # Variable to be used in .rst templates

# Semantic version
# semantic_ver = semantic_version.Version(ddsurveys.__version__)

# The short X.Y version
# version = f"{semantic_ver.major}.{semantic_ver.minor}.{semantic_ver.patch}"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',  # Core library for html generation from docstrings
    'sphinx.ext.autosummary',  # Create neat summary tables
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'myst_parser',
    'sphinx_pyreverse'
]
autosummary_generate = True  # Turn on sphinx.ext.autosummary

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
