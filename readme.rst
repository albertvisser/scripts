My scripts
==========

A collection of simple (mostly bash or python) scripts I put in /home/<user>/bin
which I added to the system path for easy access.

Also in this directory are starters for my own applications that are no more than
symlinks to the actual starter in the application dir; as well as short scripts
that pass specific arguments to such a symlink. These are not included in the repo.

**.hgignore**

    indicates which notracked files mercurial is to ignore

**2panefm**

    start Double Commander in workspace 2

**arcstuff.conf.example**

    example ini file for ``fab arcstuff`` command

**binfab**

    execute ``fab`` (fabric) using fabfile in this directory


**bstart**

    start music player (originally Banshee, now Clementine) in workspace 4

**check-repo** (formerly check_local)

    while a script by this name was replaced with a function in the fabfile, my
    creativity failed me in choosing a name for a somewhat similar but visual tool
    that does some things that hgview does, but without needing to step into the
    repo first.

**dosomethingwith.py**

    a general-purpose script that I wrote for use from within Double Commander to
    apply some action on the selected files and/or directories.

**fabfile.py**

    collection of special functions. Currently contains the following:

    a function to upgrade SciTE to the specified version (after downloading).

    a function to (re)build SciTE to the specified version (after downloading).
    I needed this after upgrading my system to 64-bit, since the download binary is
    32-bit.

    a function that reads entries from a config file (called ``arcstuff.ini``,
    example present) to build an archive containing backups of selected data files.

    some functions that can be used to control a mongodb database server

    a function to copy html files into the nginx server root and one to
    subsequently edit it; same for doing this with the apache server root

    a couple of functions to help with the internalization of source files

    a function to set up a Python source tree in a standardized way

    functions replacing the check- and push-scripts mentioned below

**fabsrv**

    execute ``fab`` (fabric) using fabfile in nginx-config directory (for server
    configuration stuff)

**iview**

    starts up IrfanView under Wine.
    Takes one argument, assuming this is the file to view.

**jsonp.py**

    generate pretty-printed version of file with json data

**list2scite**

    a script to take a file with filenames (created by e.g. Double Commander)
    and expand it into a command to start SciTE with all these files open

**lstart**

    start LMMS on workspace 3

**morefromdos.py**

    Python script to change Windows line endings to Unix ones for all Python files
    in a directory. Takes two arguments: a directory name and an extension.
    Without an argument, works in the current working directory.
    Without an extension specified, works on Python source files (extension .py).

**ostart**

    start Opera 12 on workspace 1

**readme.rst**

    this file.

**runwithlog**

    enable logging for an application that reacts to setting a DEBUG environment
    variable

    to use, simply prepend this command to the usual call to the app

**settings.py**

    Configuration values for the fabfile in this directory,
    mostly for the mercurial repo stuff.

**sort_file.py**

    copy of a Python script I wrote on Windows to sort a (text) file from within
    Total Commander.
    Takes one argument: the file to sort.
    Asks for one if you omit it.
    The result is stored in the same directory under a different name,
    but can also be saved in a temporary location if appropriately called

**totalcmd**

    starts up Total Commander under Wine. takes no arguments.
    Uses wmctrl to ensure which workspace it starts up in

**vstart**
    start Vivaldi browser on workspace 1

Requirements
------------

- a Linux/Unix based OS (although the Python scripts should be cross-platform)
- Python
- Fabric (where applicable)
- Mercurial (for the check and push scripts)

Not in this repository:
-----------------------

scripts that were replaced by functions in the fabfile:
.......................................................

**check-local**

    script to check if there are changes to local repositories that aren't synched
    with my central ones (the ones that push to BitBucket). No arguments.
    relies on the *hg* subcommands ``status`` and ``outgoing``

**check-bb**

    script to check if there are changes to central repositories that aren't
    synched with the remote (BitBucket) ones. No arguments.
    Currently this script only checks for uncommitted changes because outgoing
    would be "expensive".
    It should probably be replaced with a working version of ``push-bb``

**check-usb**

    script to check if there are changes to repositories on my USB drive that
    aren't synched with my central ones (the ones that push to BitBucket).
    No arguments.

**chmodrecursive**

    in copying my server trees from Windows the file permissions were fucked up.
    So I wrote this script to set them right.

**permit.py**

    Python script to change file and directory permissions after copying over from
    Windows. Argument works like with ''morefromdos.py'' except for all files
    instead of just .py ones. I wrote and used these scripts when I copied my old
    CGI apps over from Windows to Linux.
    Basically a nicer version of *chmodrecursive.py*.

**push-bb**

    script to check selected central repos for uncommitted changes and push to
    bitbucket when not present and not committed before. Uses `hg tip` to save the
    new tip for comparison.

**push-local**

    script to check local repos for uncommitted changes and push to central when
    not present

**push-usb**

    the same for repose on my usb drive

**pushthru**

    script to push directly from a specified local repo to bitbucket

**rstbb**

    script to update rstblog source and push to central and bitbucket


symlinks or short starter scripts for my own applications:
..........................................................

**afrift**

    starts up my 'Find/Replace in Files' tool. Requires no arguments, but all
    options that can be set in the gui can be set from the command line.

**albums**

    starts up a GUI version of the webapp of the same name

**albumsgui**

    starts my interface to several media file databases

**a-propos**

    starts up my 'apropos' application. I had to rename it because there appeared
    to be a system tool by that name. No arguments.

**comparer**

    starts up my compare tool

**cssedit**

    starts up a standalone version of my css editor

**csvhelper**

    starter for routines to make editing a csv file somewhat easier
    to be used in combination with or started from within a text editor

**diary**

    symlink to ramble

**doctree**

    starts up my docs/notes organiser (QT version) from a standard location.
    No arguments.

**dt_print**

    starts up a program to print the contents of a doctree file

**flarden**

    points notetree to a collection of text snippets

**hotkeys**

    starts my viewer for keyboard shortcuts in various applications. No arguments.

**hotrefs**

    points the same viewer at a collection of application command references

**htmledit**

    starts up my tree-based html editor. Takes one optional argument: the filename.

**lint-all**

    apply pylint or flake8 checks to all my software projects (under construction)

**lintergui**

    GUI frontend as replacement for *lint-this* and *lint-all*

**lint-this**

    apply pylint or flake8 checks to selected files or files in a selected directory

**mdview**

    Viewer for markdown formatted documents.
    Can be used with Double Commander or from within SciTE etc.

**modcompare**

    start doctree with a file for comparing modreader transcripts

**modreader**

    make text transcriptions of music module files

**notetree**

    starts up Doctree's predecessor. No arguments.

**nt2ext**

    show and/or reorganize contents of NoteTree documents

**pfind**

    starts up *afrift* to search in all my Python software projects
    for this it calls it in 'multi' mode using a list file that lives in this
    directory and contains all the paths to be searched.
    can be called up with a search argument or without

**probreg**

    starts up my 'probreg' application from a standard location. Takes no arguments.

**probreg_sql**

    the same for the version using sqlite. Also takes no arguments.

**probreg-jvs**
**probreg-leesjcl**
**probreg-todo**

    starters for *probreg* with a specific data file

**ramble**

    points doctree to a collection of ramblings

**rstview**

    Viewer for ReST formatted documents.
    Can be used with Double Commander or from within SciTE etc.

**scratch_pad**

    start a-propos using a file in /tmp (which is not saved over Linux sessions)

**treedocs**

    symlink to the doctree application. Used by the doctree script (among others)

**viewhtml**

    viewer for HTML formatted documents.
    Can be used with Double Commander or from within SciTE etc.

**xmledit**

    starts up my tree-based xml editor. Takes one (optional) argument: the filename.


other scripts not in repo:

determine_all_project_dirs.py
    script to create the list that containing all directories to search
    as used by the pfind command
determine_all_project_files.py
    a similar script intended to create a list of files
    I have decided I don't really need this when I have a list of directories
reaper
    starts linux version of reaper
rpdb2.py
    used by winpd3, slightly adapted for python 3
search-all-projects
    original version of the `pfind` script
    with an option to recreate the list of files/directories to search by calling
    determine_all_project_dirs.py
winpdb3
    starter for winpdb under python 3
winpdb.py
    symlink to original

