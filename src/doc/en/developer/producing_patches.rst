.. _chapter-mercurial:

================================
Producing Patches with Mercurial
================================

If you are editing or adding to Sage's core library, you will probably
want to share your changes with other users. Mercurial is the tool to
do this. Mercurial is the source control system that is included with
Sage. This chapter provides an overview of how to use Mercurial with
Sage; see http://www.selenic.com/mercurial/ for full documentation on
Mercurial.

All of the Mercurial repositories related to Sage are included with
Sage. Thus the complete change history and setup for doing development
is available in your copy of Sage.

Before using Mercurial, make sure to define your username so the
patches you make are identified as yours. Make a file ``~/.hgrc``
in your home directory like this one:

::

    [ui]
    username = Euclid of Alexandria <euclid@alexandria.edu>


Quick Mercurial tutorial for Sage
=================================

To submit your changes to the Sage development team for refereeing
(and inclusion into Sage if the referee's report is positive), you
should produce patch files using Mercurial. The simplest way is to run
Mercurial from within Sage following the examples below (note: ``Hg``
is the chemical symbol for mercury).

- Type ``hg_sage.status()`` and ``hg_sage.diff()`` to see exactly what
  you have done. Use the command ``q`` to quit the diff.

- If you have added new files, not just edited existing ones, type
  ``hg_sage.add([filenames])`` to add those new files to your
  repository.

  .. warning::

      As noted in :ref:`chapter-cython`, if you have added a Cython
      file, you also need to edit
      ``SAGE_ROOT/devel/sage/module_list.py``. If you have added a
      new directory, you need to edit
      ``SAGE_ROOT/devel/sage/setup.py``.  If you have added something
      other than Python or Cython files, then you might need to add
      entries to the file ``SAGE_ROOT/devel/sage/MANIFEST.in``: this
      records all of the files to include in distributions of the Sage
      library.  Look at the file itself for examples, and see the
      Python documentation
      http://docs.python.org/distutils/sourcedist.html#specifying-the-files-to-distribute
      for all of the details.

- Commit your changes by typing ``hg_sage.commit()`` to commit the
  changes in files to the repository.  If you want to commit only
  specific files, each file must be listed individually with full path
  names, e.g. ``hg_sage.commit('sage/misc/misc.py  sage/all.py')``. If
  no file names are given, all changed files are committed. First, the
  output of ``hg diff`` is displayed: look at it or just enter
  ``q``. Then you are dumped into an editor to type a brief comment on
  the changes. The default editor is vi, so type ``i`` to insert,
  write a one line commit message of the form
  ``trac xxxx: <your-commit-message-here>`` where ``xxxx`` is the Sage
  development tracking system  ticket number (see
  http://trac.sagemath.org). To quit the vi editor and save your
  commit message, hit ``Escape`` and type ``:wq``. (In bash, to make
  emacs the default editor, type ``export EDITOR=emacs``.)

- Now create a patch file using ``hg_sage.export(...)``. This command
  needs a revision number (or list of revision numbers) as an
  argument; use ``hg_sage.export('tip')`` to use the most recent
  revision number or use ``hg_sage.log()`` to see all these
  numbers. An optional second argument to ``hg_sage.export(...)`` is a
  file name for the patch. The default is
  ``(changeset_revision_number).patch``, which is written in what Sage
  considers the current directory (this can be found with the command
  ``os.path.abspath('.')``).

- Then post your patch on the Sage Trac server: see
  :ref:`chapter-trac`.

You can also run Mercurial directly from the command line using the
command ``sage -hg``. Or you can start a very nice web server that
allows you to navigate your repository with a web browser, or pull
patches from it remotely, by typing ``hg_sage.serve()``. Then open
your web browser and point it to http://localhost:8000, which is the
default listening address for Mercurial.

Finally, if you want to apply a patch file (perhaps you have
downloaded a patch from the Trac server for review), use the command
``hg_sage.patch('filename')`` (or ``hg_sage.apply('filename')`` for hg
bundle files).

Before you modify Sage library files, you might want to create a copy
of the Sage library in which to work. Do this by typing
``sage -clone myver``, for example. Then Sage will use Mercurial to
clone the current repository and call the result ``myver``. The new
repository is stored in ``<SAGE_ROOT>/devel/sage-myver``, and when you
clone, the symbolic link ``sage --> sage-myver`` is made.

(You can also do, e.g. ``sage -clone -r 1250 oldver``, to get a clone
of Sage as it was at revision 1250. Of course, dependency issues could
make old versions not work (e.g. maybe an old Sage library would not
compile with the latest Singular library, which is what is installed
elsewhere in ``SAGE_ROOT``). From within Sage, type ``hg_sage.log()``
to see the revision history. Note that if you clone an old version,
all of the Cython code is rebuilt, since there is no easy way to know
which files do and do not need rebuilding.)

Once you have copied the library to a new branch ``myver`` and edited
some files there, you should build the Sage library to incorporate
those changes. Type ``sage -b myver``, or just ``sage -b`` if the
branch ``myver`` is already the current branch, i.e. if
``SAGE_ROOT/devel/sage`` links to ``SAGE_ROOT/devel/sage-myver``. You
can also type ``sage -br myver`` to build the library and then to
immediately run Sage.


Using Mercurial with other Sage repositories
============================================

Sage includes these Mercurial repositories:

- ``SAGE_ROOT/devel/sage-*``: the Sage library source code.

- ``SAGE_ROOT/data/extcode``: external system code, i.e. code included
  with Sage that is written for the systems with which Sage
  interfaces, e.g. GAP, PARI, etc.

- ``SAGE_ROOT/local/bin``: Sage shell scripts.

- ``SAGE_ROOT``: Sage root -- text files in the main Sage directory
  and in ``SAGE_ROOT/spkg``.

The previous section discussed using Mercurial with the Sage library,
via the command ``hg_sage``. There are corresponding commands for each
of the repositories:

- use ``hg_sage`` for the Sage library

- use ``hg_extcode`` for the external system code

- use ``hg_scripts`` for the Sage shell scripts.

- use ``hg_root`` for the Sage root.

Since version 3.4, both the Sage library and documentation
repositories are managed by the command ``hg_sage``.
