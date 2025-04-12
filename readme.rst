My scripts
==========

A collection of simple (mostly bash or python) scripts I put in /home/<user>/bin
which I added to the system path for easy access.

Also in this directory are starters for my own applications that are no more than
symlinks to the actual starter in the application dir; as well as short scripts
that pass specific arguments to such a symlink. These are not directly included in the repo,
but in the form of a script that generates these symlinks and invocations.

**.gitignore**

    indicates which non-tracked files ``git`` is to ignore

**.rurc / .rurc.template**

    configuration used by ``run-unittests``. The former is what I actually use for this repo; 
    the latter is as the name implies a template, containing an explanation of how it works

**.sessionrc.template**

    sample configuration used by the ``binfab session start`` command. 
    Also with explanatory comments.

**arcstuff.conf.example**

    example config file for ``binfab arcstuff`` command

**binfab**

    execute ``invoke`` tasks for this directory (through ``tasks.py``). The "fab" part of the name
    stems from the former use of ``fabric``.

**bin-scripts.conf / bin-scripts-conf.example**

    "library" of short scripts and starters, used by ``build-bin-scripts`` and the
    ``binfab scriptlib`` commands. 
    Replaces adding all these short snippets directly to the repo.   

**build-bin-scripts / build_bin_scripts.py**

    a script to build additional short scripts by making symlinks and echoing commands into files.
    Intended to run when reinstalling the system. See below for details.

**build-unittests / build_unittests.py**

    a script to generate a collection of unittest templates for a given module. 
    Also updates the ``.rurc`` test configuration.

**check-repo / check-repo.py / check_repo_tooltips.py**

    (formerly check_local)
    while a script by this name was replaced with a function in the fabfile, 
    my creativity failed me in choosing a name for a somewhat similar but visual tool 
    that makes it possible to start several basic repo management tasks from a gui
    and without needing to step into the repo first.

**count-locs / count_locs.py**

    simple lines-of-code counter based on importlib / inspect.
    Output can be shown sorted by function / method name or by line number. 
    Used by ``check-repo`` but can be run by itself. 

**covtest**

    script to launch unittests and analyse testcoverage (using pytest and coverage.py).
    Used by ``run-unittests``.

**db.py**

    ``invoke`` functions to manage database servers. Currently contains start/restart/stop functions 
    for mongodb and postgres and a repair function for mongodb. Also added: simple backup/restore
    actions.

**dtree**

    starts up ``treedocs`` for repo-related documentation (through a binfab command)
    Intended to be used within a project directory, it's also possible to supply the project name
    as a parameter. 

**fabsrv**

    execute ``invoke`` tasks in nginx-config directory (for server configuration stuff).
    the same applies as for **binfab**

**jsonp / jsonp.py**

    generate pretty-printed version of file with json data

**jsonv / jsonv.py**

    view pretty-printed version of file with json data without copying it

**lang.py**

    a couple of ``invoke`` functions to help with the internalization of Python source files

**list2scite / list2scite.py**

    a script to take a file with filenames (created by e.g. Double Commander)
    and expand it into a command to start SciTE with all these files open

**list2vi / list2vi.py**

    the same for VI(m) in a terminal

**mee-bezig**

    starts up ``treedocs`` with a file in my projects directory where I keep all kinds of notes 
    about my collection of projects as a whole 

**morefromdos.py**

    Python script to change Windows line endings to Unix ones for all Python files
    in a directory. Takes two arguments: a directory name and an extension.
    Without an argument, works in the current working directory.
    Without an extension specified, works on Python source files (extension .py).

**pedit**

    shortcut for starting up vi(m) in a terminal using the 'Code Editor Shell' profile (100x54,
    green on black) at different positions of the screen dependent on a startup parameter, 
    making it possible to edit programs side-by-side

**predit**

    executing ``binfab session-start <project-name>`` starts a terminal session for that project
    and sets up an environment variable $files (and others) for use with this command to start editing
    the specified (source) files

**prfind**

    uses the same environment variable to start ``filefindr`` in multiple file mode  

**pytest.ini**

    local config file to make pytest suppress depreciation warnings

**readme.rst**

    this file.

**rename-files / rename_files.py**

    like list2vi/list2scite, apply some action on the selected files and/or directories: 
    take the first word and put it at the end to improve sortability.

**repo.py**

    ``invoke`` functions for managing source repositories, like the replaced check- and push-scripts 
    mentioned below (at the end of this file)

**run-unittests / run_unittests**

    script to run unittests for a project, either for all the modules or for a specified one.
    uses a config file (.rurc) to figure out the combination of tester - testee

**runwithlog**

    enable logging for an application that reacts to setting a DEBUG environment variable.
    to use, simply prepend this command to the usual call to the app

**scriptlib.py**

    ``invoke`` functions for working with my scriptlet collection, a.k.a. my attempt to keep all my
    short scripts version-controlled without having to add them each to the repo individually

**session.py**

    ``invoke`` functions for my homemade session- and ticket management
 
**settings.py**

    Configuration values for the the tasks files in this directory,
    mostly for the mercurial repo stuff.

**setup-nginx**

    script to setup my server environment, to be used when installing a new system. 
    It's a work in progress, updating whenever I have to actually use it.

**sort_file.py**

    copy of a Python script I wrote on Windows to sort a (text) file from within Total Commander.
    Takes one argument: the file to sort.
    Asks for one if you omit it.
    The result is stored in the same directory under a different name,
    but can also be saved in a temporary location if appropriately called

**tags.py**

    ``invoke`` functions to maintain ctags stuff in a source repository

**tasks.py**

    miscellaneous ``invoke`` functions. Currently contains the following:

    a function to upgrade SciTE to the specified version (after downloading).

    a function to (re)build SciTE to the specified version (after downloading).
    I needed this after upgrading my system to 64-bit, since the download binary is 32-bit.

    a function that reads entries from a config file (called ``arcstuff.ini``,
    example present) to build an archive containing backups of selected data files.

**tedit**

    like ``pedit``, but with a white background. One might say p is for programs and t is for text
    
**unittests/**

    the scripts in this directory contain the unit tests for the invoke scripts and check-repo.py
    (as registered in .rurc)

**www.py**

    ``invoke`` functions to do with plain html sites; mostly local (nginx and apache server root) 
    but also to setup transport to a remote site like magiokis.nl

**xmlp.py**

    generate pretty-printed version of file with xml data

Requirements
------------

- a Linux/Unix based OS (although the Python scripts should be cross-platform)
- Python
- Invoke where applicable
- PyQt(5) for check-repo
- Git and/or Mercurial (for the check and push scripts)


Extra scripts to be created using ``build-bin-scripts``:
------------------------------------------------------

This script creates the following symlinks and short starter scripts for my own applications:

**afrift**
    starts up my 'Find/Replace in Files' tool. Requires no arguments, but all
    options that can be set in the gui can be set from the command line.
**albums**
    starts up a GUI version of the webapp of the same name
**albumsgui**
    starts my interface to several media file databases
**a-propos**
    starts up my ``apropos`` application. I had to rename it because there appeared
    to be a system tool by that name. No arguments.
**comparer**
    starts up my compare tool
**comparer_from_dc**
    the same, but from within Double Commander
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
**end-session**
    slightly simpler way to say "binfab session.end"
**flarden**
    points notetree to a collection of text snippets
**gamestuff**
    starts a treedocs file with information for games I play
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
**lintergui**
    GUI frontend as replacement for ``lint-this`` and ``lint-all``. Used by my ``check-repo`` tool.
**lint-this**
    apply pylint or flake8 checks to selected files or files in a selected directory
**lminstreloc**
    starts up my LMMS Instrument Relocation program
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
    start one of the "search in all repos" commands depending on first argument (-a/-p/-t).
    Basically a comprehension of the following three scriptlets.
**pfind-all**
    shortcut for a ``binfab`` command that starts up *filefindr* to search in all my Python software 
    projects
**pfind-prog**
    shortcut for a ``binfab`` command that starts up *filefindr* to search in all my Python software 
    projects' program modules
**pfind-test**
    shortcut for a ``binfab`` command that starts up *filefindr* to search in all my Python software 
    projects unittest modules
**popup**
    show some text in a popup
**probreg**
    starts up my 'probreg' application. Optional arguments: either the name of an
    XML file or 'sql' optionally followed by a project name. Without arguments:
    presents a file selection dialog. With only 'sql': presents a project selector.
**ramble**
    points doctree to a collection of ramblings
**readme**
    starts op both preadme and rreadme
**repocheck**
    shortcut for ``binfab repo.check-local``, to check for changes in local repos
**repolog**
    shortcut for ``binfab repo.check-local-changes``, to view the extended output of the previous
**repopush**
    shortcut for ``binfab repo.push-local push-remote``, to migrate all committed changes 
**repotesterr**
    shortcut for ``binfab repo.find-test-errors`` to report on all tests that have errors.
**repotestfail**
    shortcut for ``binfab repo.find-failing-tests`` to show only the failing unittests.
**repoteststats**
    shortcut for ``binfab repo.find-test-stats`` to show unittest coverage for a given repo.
    If no repo given, do all. The previous two work similarly. 
**rreadme**
    ``binfab`` command to view the ven HTML rendering of a project's readme file
**rstview**
    Viewer for ReST formatted documents.
    Can be used with Double Commander or from within SciTE etc.
**scratch_pad**
    start a-propos using a file in /tmp (which is not saved over Linux sessions)
**sdv-modman**
    starts up my Stardew Valley Mod Manager
**start-session**
    slightly simpler way to start a programming session for a project
**tickets**
    starts probreg as my issue tracker, replacing trac.lemoncurry.nl
**treedocs**
    symlink to the doctree application. Used by the doctree script (among others)
**treedocsp**
    symlink to the doctree application's print utility..
**tview**
    readonly version of tedit, without position options
**viewhtml**
    viewer for HTML formatted documents.
    Can be used with Double Commander or from within SciTE etc.
**viewxml**
    viewer for XML formatted documents.
    Can be used with Double Commander or from within SciTE etc.
**webrefs**
    points my hotkeys app to a collection of keyboard shortcuts for web apps
**xmledit** 
    starts up my tree-based xml editor. Takes one (optional) argument: the filename.

It also creates starters for various other programs:

**2panefm**
    start Double Commander in workspace 2
**appstart**
    starts a "webapp" created with vivaldi (standard chromium functionality?)
**bigterm**
    starts up VI in a bigger window. Can be called with the name of a repo to start ``prshell``
**bstart**
    start music player (originally Banshee, then Clementine, now Strawberry) in workspace 4
**calc**
    symlink to gnome-calculator
**cgit**
    start cgit repository browser for local repositories in a separate window
**dc4sdv**
    starts Double Commander with Stardew Valley mods downloads directory on the one side
    and game mods directory on the other
**gitweb**
    start gitweb repository browser for "central" repositories in a separate window
**iview**
    starts up IrfanView under Wine.
    Takes one argument, assuming this is the file to view.
**leo**
    (if installed) starts up Leo editor
**lstart**
    start LMMS on workspace 3
**mdi**
    symlink to ``mdi.py`` which is a modified version of the pyqt mdi demo (using scintilla controls)
**open-reader**
    start up Calibre's ebook viewer on workspace 1
**peditl**
    starts pedit (i.e. VIm) on the left side of the screen instead of in the middle
**peditlr**
    starts pedit two times side by side 
**peditml**
    starts pedit at a position next to where it would be using peditl           
**peditmr**
    starts pedit at a position next to where it would be using peditr           
**peditr**
    starts pedit on the right side of the screen instead of in the middle
**preadme**
    edit readme file in a given repo
**prshell**
    opens a terminal in a given repo with an enlarged window
**pycheck**
    syntax check the specified python file(s) (using py_compile)
**qtdemo**
    starts up the Qt5 demo program, if available
**reaper**
    starts linux version of reaper
**sdl-ball**
    starts a game
**start-gaming**
    starts Steam on workspace 3
**start-gaming-native**
    starts Steam on workspace 3 using native package
**start-mc**
    (if installed) start Midnight Commander in a larger than default terminal
**start-servers**
    calls fabsrv to start selected wsgi servers
**stop-servers**
    calls fabsrv to stop all wsgi servers
**t-ed**
    open a terminal in a "code editor" mode I defined (replaced by tedit)
**teditl**
    starts tedit on the left side of the screen instead of in the middle
**teditlr**
    starts tedit two times side by side 
**teditml**
    starts tedit at a position next to where it would be using peditl           
**teditmr**
    starts tedit at a position next to where it would be using peditr           
**teditr**
    starts tedit on the right side of the screen instead of in the middle
**totalcmd**
    starts up Total Commander under Wine. takes no arguments.
    Uses wmctrl to ensure it starts up in workspace 2 
**vi-get-runtime**
    Get the current VI(M) version. Used by my Hotkeys plugin(s) for VI
**viref**
    starts vi(m) showing quick reference
**vless**
    starts vi(m) in a mode that is supposed to resemble the ``less`` program
**vstable**
    start Vivaldi browser (stable version) on workspace 1
**vstart**
    start Vivaldi (snapshot) browser on workspace 1
**widevi**
    takes two or three filenames and starts vi(m) practically full screen to edit the files
    side-by-side
**wing**
    (if installed) starts up WING editor which I sometimes use for GUI debugging
**wstart**
    launch ghostwriter in fourth workspace
**wxdemo**
    starter for the wxPython demo program (if available)


scripts that were replaced by functions in the fabfile:
-------------------------------------------------------
(not present in this working directory either)

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
    bitbucket when not present and not committed before. Uses ``hg tip`` to save the
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


