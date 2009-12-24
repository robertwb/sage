import sys, os, re
SAGE_ROOT = os.environ['SAGE_ROOT']
SAGE_DOC = os.path.join(SAGE_ROOT, 'devel/sage/doc')

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#sys.path.append(os.path.abspath('.'))

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc']

if 'SAGE_DOC_JSMATH' in os.environ:
    extensions.append('sphinx.ext.jsmath')
else:
    extensions.append('sphinx.ext.pngmath')
jsmath_path = 'jsmath_sage.js'

# Add any paths that contain templates here, relative to this directory.
templates_path = [os.path.join(SAGE_DOC, 'common/templates'), 'templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u""
copyright = u'2005--2009, The Sage Development Team'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
from sage.version import version
release = version

#version = '3.1.2'
# The full version, including alpha/beta/rc tags.
#release = '3.1.2'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = ['.build']

# The reST default role (used for this markup: `text`) to use for all documents.
default_role = 'math'

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.  NOTE:
# This overrides a HTML theme's corresponding setting (see below).
pygments_style = 'sphinx'


# Options for HTML output
# -----------------------

# HTML theme (e.g., 'default', 'sphinxdoc').  We use a custom Sage
# theme to set a Pygments style, stylesheet, and insert jsMath macros.
html_theme = 'sage'

# Theme options are theme-specific and customize the look and feel of
# a theme further.  For a list of options available for each theme,
# see the documentation.
html_theme_options = {}

if 'SAGE_DOC_JSMATH' in os.environ:
    from sage.misc.latex_macros import sage_jsmath_macros_easy
    html_theme_options['jsmath_macros'] = sage_jsmath_macros_easy

    from sage.misc.package import is_package_installed
    html_theme_options['jsmath_image_fonts'] = is_package_installed('jsmath-image-fonts')

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = [os.path.join(SAGE_DOC, 'common/themes')]

# HTML style sheet NOTE: This overrides a HTML theme's corresponding
# setting.
#html_style = 'default.css'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (within the static path) to place at the top of
# the sidebar.
#html_logo = 'sagelogo-word.ico'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = 'favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [os.path.join(SAGE_DOC, 'common/static'), 'static']

# If we're using jsMath, we prepend its location to the static path
# array.  We can override / overwrite selected files by putting them
# in the remaining paths.
if 'SAGE_DOC_JSMATH' in os.environ:
    from pkg_resources import Requirement, working_set
    sagenb_path = working_set.find(Requirement.parse('sagenb')).location
    jsmath_static = os.path.join(sagenb_path, 'sagenb', 'data', 'jsmath')
    html_static_path.insert(0, jsmath_static)

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_use_modindex = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
html_split_index = True

# If true, the reST sources are included in the HTML build as _sources/<name>.
#html_copy_source = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = ''

# Output file base name for HTML help builder.
#htmlhelp_basename = ''


# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
#latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = []

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = 'sagelogo-word.png'

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''
latex_preamble = '\usepackage{amsmath}\n\usepackage{amsfonts}\n'

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_use_modindex = True

#####################################################
# add LaTeX macros for Sage

from sage.misc.latex_macros import sage_latex_macros

try:
    pngmath_latex_preamble  # check whether this is already defined
except NameError:
    pngmath_latex_preamble = ""

for macro in sage_latex_macros:
    # used when building latex and pdf versions
    latex_preamble += macro + '\n'
    # used when building html version
    pngmath_latex_preamble += macro + '\n'

#####################################################

def process_docstring_aliases(app, what, name, obj, options, docstringlines):
    """
    Change the docstrings for aliases to point to the original object.
    """
    basename = name.rpartition('.')[2]
    if hasattr(obj, '__name__') and obj.__name__ != basename:
        docstringlines[:] = ['See :obj:`%s`.' % name]

def process_directives(app, what, name, obj, options, docstringlines):
    """
    Remove 'nodetex' and other directives from the first line of any
    docstring where they appear.
    """
    if len(docstringlines) == 0:
        return
    first_line = docstringlines[0]
    directives = [ d.lower() for d in first_line.split(',') ]
    if 'nodetex' in directives:
        docstringlines.pop(0)

def process_docstring_cython(app, what, name, obj, options, docstringlines):
    """
    Remove Cython's filename and location embedding.
    """
    if len(docstringlines) <= 1:
        return

    first_line = docstringlines[0]
    if first_line.startswith('File:') and '(starting at' in first_line:
        #Remove the first two lines
        docstringlines.pop(0)
        docstringlines.pop(0)

def process_docstring_module_title(app, what, name, obj, options, docstringlines):
    """
    Removes the first line from the beginning of the module's docstring.  This
    corresponds to the title of the module's documentation page.
    """
    if what != "module":
        return

    #Remove any additional blank lines at the beginning
    title_removed = False
    while len(docstringlines) > 1 and not title_removed:
        if docstringlines[0].strip() != "":
            title_removed = True
        docstringlines.pop(0)

    #Remove any additional blank lines at the beginning
    while len(docstringlines) > 1:
        if docstringlines[0].strip() == "":
            docstringlines.pop(0)
        else:
            break

def skip_NestedClass(app, what, name, obj, skip, options):
    """
    Don't include the docstring for any class/function/object in
    sage.misc.misc whose ``name`` contains "MainClass.NestedClass".
    (This is to avoid some Sphinx warnings when processing
    sage.misc.misc.)  Otherwise, abide by Sphinx's decision.
    """
    skip_nested = str(obj).find("sage.misc.misc") != -1 and name.find("MainClass.NestedClass") != -1
    return skip or skip_nested

def process_dollars(app, what, name, obj, options, docstringlines):
    r"""
    Replace dollar signs with backticks.

    More precisely, do a regular expression search.  Replace a plain
    dollar sign ($) by a backtick (`).  Replace an escaped dollar sign
    (\$) by a dollar sign ($).  Don't change a dollar sign preceded or
    followed by a backtick (`$ or $`), because of strings like
    "``$HOME``".  Don't make any changes on lines starting with
    spaces, because those are indented and hence part of a block of
    code or examples.

    This also doesn't replaces dollar signs enclosed in curly braces,
    to avoid nested math environments, such as ::

      $f(n) = 0 \text{ if $n$ is prime}$

    Thus the above line would get changed to

      `f(n) = 0 \text{ if $n$ is prime}`
    """
    s = "\n".join(docstringlines)
    if s.find("$") == -1:
        return
    # Indices will be a list of pairs of positions in s, to search between.
    # If the following search has no matches, then indices will be (0, len(s)).
    indices = [0]
    # This searches for "$blah$" inside a pair of curly braces --
    # don't change these, since they're probably coming from a nested
    # math environment.  So for each match, search to the left of its
    # start and to the right of its end, but not in between.
    for m in re.finditer(r"{[^{}$]*\$([^{}$]*)\$[^{}$]*}", s):
        indices[-1] = (indices[-1], m.start())
        indices.append(m.end())
    indices[-1] = (indices[-1], len(s))

    # regular expression for $ (not \$, `$, $`, and only on a line
    # with no leading whitespace).
    dollar = re.compile(r"""^ # beginning of line
                            ([^\s] # non whitespace
                            .*?)? # non-greedy match any non-newline characters
                            (?<!`|\\)\$(?!`) # $ with negative lookbehind and lookahead
                            """, re.M | re.X)
    # regular expression for \$
    slashdollar = re.compile(r"\\\$")
    for start, end in indices:
        while dollar.search(s, start, end):
            m = dollar.search(s, start, end)
            s = s[:m.end()-1] + "`" + s[m.end():]
        while slashdollar.search(s, start, end):
            m = slashdollar.search(s, start, end)
            s = s[:m.start()] + "$" + s[m.end():]
    # now save results in docstringlines
    lines = s.split("\n")
    for i in range(len(lines)):
        docstringlines[i] = lines[i]

from sage.misc.sageinspect import sage_getargspec
autodoc_builtin_argspec = sage_getargspec

def setup(app):
    app.connect('autodoc-process-docstring', process_docstring_cython)
    app.connect('autodoc-process-docstring', process_directives)
    app.connect('autodoc-process-docstring', process_docstring_module_title)
    app.connect('autodoc-process-docstring', process_dollars)
    app.connect('autodoc-skip-member', skip_NestedClass)
