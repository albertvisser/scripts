My scripts
==========

A collection of simple (mostly bash) scripts I put together. Most of these are starters for applications that I put in /home/<user>/bin to have them on the system path.

**afrift**

    starts up my 'Find/Replace in Files' tool. This one requires no arguments.

**afrift_single**

    starts up the former's single file version. So one argument is required: the filename.

**afrift_multi**

    starts up the former's multi file version with arguments taken from a list (like Double Commander provides them)

**arcstuff.conf.example**

    example ini file for ``fab arcstuff`` command

**a-propos**

    starts up my 'apropos' application. I had to rename it because there appeared to be a system tool by that name. No arguments.

**binfab**

    execute ``fab`` (fabric) using fabfile in this directory

**chmodrecursive**

    in copying my server trees from Windows the file permissions were fucked up. So I wrote this script to set them right.

**doctree**

    starts up my docs/notes organiser (QT version) from a standard location. No arguments.

**fabfile.py**

    collection of special functions. Currently contains the following:

    a function to upgrade SciTE to the specified version (after downloading).

    a function to (re)build SciTE to the specified version (after downloading).
    I needed this after upgrading my system to 64-bit, since the download binary is 32-bit.

    a function that reads entries from a config file (called ``arcstuff.ini``,
    example present) to build an archive containing backups of selected data files.

    some functions that can be used to control a mongodb database server

    a function to copy html files into the nginx server root

    a couple of functions to help with the internalization of source files

    functions replacing the check- and push-scripts mentioned below

**fabsrv**

    execute ``fab`` (fabric) using fabfile in nginx-config directory (for server configuration stuff)

**hotkeys**

    starts my viewer for keyboard shortcuts in various applications

**htmledit**

    starts up my tree-based html editor. Takes one argument: the filename.

**iview**

    starts up IrfanView under Wine. takes no arguments.

**morefromdos.py**

    Python script to change Windows line endings to Unix ones for all Python files in a directory. Takes two arguments: a directory name and an extension. Without an argument, works in the current working directory. Without an extension specified, works on Python source files (extension .py).

**notetree**

    starts up Doctree's predecessor

**permit.py**

    Python script to change file and directory permissions after copying over from Windows. Argument works like with ''morefromdos.py'' except for all files instead of just .py ones. I wrote and used these scripts when I copied my old CGI apps over from Windows to Linux.

**probreg**

    starts up my 'probreg' application from a standard location. takes no arguments.

**probreg_sql**

    the same for the version using sqlite. also takes no arguments.

**readme.rst**

    this file

**sort_file.py**

    copy of a Python script I wrote on Windows to sort a (text) file from within Total Commander. Takes one argument: the file to sort.

**totalcmd**

    starts up Total Commander under Wine. takes no arguments.

**xmledit**

    starts up my tree-based xml editor. Takes one argument: the filename.

Requirements
------------

- a Linux/Unix based OS
- Python
- fabric (where applicable)
- Mercurial (for the check and push scripts)


scripts that were replaced by functions in the fabfile:
-------------------------------------------------------

**check-local**

    script to check if there are changes to local repositories that aren't synched with my central ones (the ones that push to BitBucket). No arguments.
    relies on the *hg* subcommands ``status`` and ``outgoing``

**check-bb**

    script to check if there are changes to central repositories that aren't synched with the remote (BitBucket) ones. No arguments.
    Currently this script only checks for uncommitted changes because outgoing would be "expensive".
    It should probably be replaced with a working version of ``push-bb``

**check-usb**

    script to check if there are changes to repositories on my USB drive that aren't synched with my central ones (the ones that push to BitBucket). No arguments.

**push-bb**

    script to check selected central repos for uncommitted changes and push to bitbucket when not present and not committed before. Uses `hg tip` to save the new tip for comparison.

**push-local**

    script to check local repos for uncommitted changes and push to central when not present

**push-usb**

    the same for repose on my usb drive

**pushthru **

    script to push directly from a specified local repo to bitbucket

**rstbb**

    script to update rstblog source and push to central and bitbucket

