My scripts
==========

A collection of simple (mostly bash or python) scripts I put in /home/<user>/bin
which I added to the system path for easy access.

Also in this directory are starters for my own applications that are no more than
symlinks to the actual starter in the application dir; as well as short scripts
that pass specific arguments to such a symlink. These are not included in the repo.

**.hgignore**

    indicates which non-tracked files mercurial is to ignore

**2panefm**

    start Double Commander in workspace 2

**arcstuff.conf.example**

    example ini file for ``fab arcstuff`` command

**binfab**

    execute ``fab`` (fabric) using fabfile in this directory
    actually `fabric` is now replaced by `invoke` so this now starts ``tasks.py`` 
    and runs under Python 3

**bstart**

    start music player (originally Banshee, now Clementine) in workspace 4

**check-repo** (formerly check_local)

    while a script by this name was replaced with a function in the fabfile, 
    my creativity failed me in choosing a name for a somewhat similar but visual tool 
    that does some things that hgview does (and more), 
    but without needing to step into the repo first.

**db.py**

    `invoke` functions to manage database servers. Currently contains start/restart/stop functions 
    for mongodb and postgres and a repair function for mongodb

**dosomethingwith.py**

    a general-purpose script - or at least meant as such - that I wrote for use from within 
    Double Commander to apply some action on the selected files and/or directories.

**fabsrv**

    execute ``fab`` (fabric) using fabfile in nginx-config directory (for server
    configuration stuff).
    the same applies as for **binfab**

**i18n.py**

    a couple of `invoke` functions to help with the internalization of source files

**iview**

    starts up IrfanView under Wine.
    Takes one argument, assuming this is the file to view.

**jsonp.py**

    generate pretty-printed version of file with json data

**list2scite**

    a script to take a file with filenames (created by e.g. Double Commander)
    and expand it into a command to start SciTE with all these files open

**list2vi** 

    the same for VI in a terminal

**lstart**

    start LMMS on workspace 3

**mee-bezig**

    calls *a-propos* on a file where I can leave notes on what I'm working on. 
    Intended to be used within a project directory, it's also possible to supply the project name
    as a parameter. 

**morefromdos.py**

    Python script to change Windows line endings to Unix ones for all Python files
    in a directory. Takes two arguments: a directory name and an extension.
    Without an argument, works in the current working directory.
    Without an extension specified, works on Python source files (extension .py).

**pedit**
    shortcut for starting up vi in a terminal using the 'Code Editor Shell' profile (100x54,
    green on black)

**peditl**
    starts pedit on the left side of the screen instead of in the middle

**peditr**
    starts pedit on the right side of the screen instead of in the middle

**pfind**

    shortcut for a `binfab` command that starts up *filefindr* to search in all my Python software 
    projects

**predit**

    executing *binfab session-start <project-name>* starts a terminal session for that project
    and sets up an environment variable $files for use with this command to start editing
    the specified (source) files

**prfind**

    uses the same environment variable to start *filefindr* in multiple file mode  

**pycheck**

    syntax check the specified python file(s)

**readme.rst**

    this file.

**repo.py**

    `invoke` functions for managing source repositories, like the replaced check- and push-scripts 
    mentioned below

**runwithlog**

    enable logging for an application that reacts to setting a DEBUG environment
    variable

    to use, simply prepend this command to the usual call to the app

**session.py**

    `invoke` functions for my homemade session- and ticket management
 
**settings.py**

    Configuration values for the fabfile (and the tasks files) in this directory,
    mostly for the mercurial repo stuff.

**sort_file.py**

    copy of a Python script I wrote on Windows to sort a (text) file from within
    Total Commander.
    Takes one argument: the file to sort.
    Asks for one if you omit it.
    The result is stored in the same directory under a different name,
    but can also be saved in a temporary location if appropriately called

**tags.py**

    `invoke` functions to maintain ctags stuff in a source repository

**tasks.py**

    miscellaneous `invoke` functions. Currently contains the following:

    a function to upgrade SciTE to the specified version (after downloading).

    a function to (re)build SciTE to the specified version (after downloading).
    I needed this after upgrading my system to 64-bit, since the download binary is
    32-bit.

    a function that reads entries from a config file (called ``arcstuff.ini``,
    example present) to build an archive containing backups of selected data files.

    a function to set up a Python source tree in a standardized way (really?)
    
**totalcmd**

    starts up Total Commander under Wine. takes no arguments.
    Uses wmctrl to ensure which workspace it starts up in

**vstart**

    start Vivaldi browser on workspace 1

**www.py**

    `invoke` functions to do with plain html sites; mostly local (nginx and apache server root) 
    but also to setup transport to a remote site like magiokis.nl

**xmlp.py**

    generate pretty-printed version of file with xml data

Requirements
------------

- a Linux/Unix based OS (although the Python scripts should be cross-platform)
- Python
- Fabric (where applicable) - the new version uses Invoke instead
- Mercurial and/or Git (for the check and push scripts)

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

**comparer_from_dc**

    a small helper script to start the previous from within Double Commander

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

**hotstuff**

    starts up both hotkeys and hotrefs, since I'm using them simultaneously a lot (especially with
    VI)

**htmledit**

    starts up my tree-based html editor. Takes one optional argument: the filename.

**lint-all**
        
    apply pylint or flake8 checks to all my software projects (under construction?)

**lint_all.py**

    the same but using lintergui

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

**probreg**

    starts up my 'probreg' application. Optional arguments: either the name of an
    XML file or 'sql' optionally followed by a project name. Without arguments:
    presents a file selection dialog. With only 'sql': presents a project selector.

**probreg-sql**

    shortcut for 'probreg sql'. Optional argument: project name.

**probreg-jvs**

    starter for *probreg* with a specific data file

**probreg-leesjcl**

    starter for *probreg* with a specific data file

**probreg-todo**

    starter for *probreg* with a specific data file

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

**webrefs**

    points my hotkeys app to a collection of keyboard shortcuts for web apps

**xmledit**

    starts up my tree-based xml editor. Takes one (optional) argument: the filename.


other scripts not in repo:
..........................

**latest-proprietary-media-future.sh**
**latest-widevine.sh**
    two scripts (not by me) to facilitate viewing proprietary video formats in Vivaldi browser
**reaper**
    starts linux version of reaper
**start-servers**
    calls fabsrv to start all wsgi servers
**stop-servers**
    calls fabsrv to stop all wsgi servers
**t-ed**
    open a terminal in a "code editor" mode I defined
**viref**
    starts vi showing vi documentation
**vless**
    starts vi in a mode that is supposed to resemble the `less` program
**winpdb3**
    starter for winpdb under python 3
**wxdemo**
    starter for the wxPython demo program
