My scripts
==========

A collection of simple (mostly bash) scripts I put together. Most of these are starters for applications that I put in /home/<user>/bin to have them on the system path.

**afrift**

    starts up my 'Find/Replace in Files' tool. This one requires no arguments.

**afrift_single**

    starts up the former's single file version. So one argument is required: the filename.

**a-propos**

    starts up my 'apropos' application. I had to rename it because there appeared to be a system tool by that name. No arguments.

**check-local**

    script to check if there are changes to local repositories that aren't synched with my central ones (the ones that push to BitBucket). No arguments.
    relies on the `hg` subcommands `status` and `outgoing`

**check-bb**

    script to check if there are changes to central repositories that aren't synched with the remote (BitBucket) ones. No arguments.
    Currently this script only checks for uncommitted changes because outgoing would be "expensive".
    It should probably be replaced with a working version of `push-bb`

**check-usb**

    script to check if there are changes to repositories on my USB drive that aren't synched with my central ones (the ones that push to BitBucket). No arguments.

**doctree**

    starts up my docs/notes organiser (QT version) from a standard location. No arguments.

**fabfile.py**

    collection of special functions. Currently contains the following:

    *install_scite*: upgrade SciTE to the specified version (after downloading). Supposed to replace the bash script that does the same (does a better job taking the calling argument)

    *arcstuff*: reads entries from a config file (called ``arcstuff.ini``, example present) to build an archive containing backups of selected data files.

**htmledit**

    starts up my tree-based html editor. Takes one argument: the filename.

**install-scite**

    script to install SciTE in the location proposed by the docs

**morefromdos.py**

    Python script to change Windows line endings to Unix ones for all Python files in a directory. Takes one argument: the directory name. Without an argument, works in the current working directory.

**notetree**

    starts up Doctree's predecessor

**permit.py**

    Python script to change file and directory permissions after copying over from Windows. Argument works like with ''morefromdos.py'' except for all files instead of just .py ones. I wrote and used these scripts when I copied my old CGI apps over from Windows to Linux.

**probreg**

    starts up my 'probreg' application from a standard location. takes no arguments.

**probreg_sql**

    the same for the version using sqlite. also takes no arguments.

**push-bb**

    script to check selected central repos for uncommitted changes and push to bitbucket when not present and not committed before. Uses `hg tip` to save the new tip for comparison.

**push-local**

    script to check local repos for uncommitted changes and push to central when not present

**push-usb**

    the same for repose on my usb drive

**rstbb**

    script to update rstblog source and push to central and bitbucket

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
