#! /usr/bin/env python
"""scripts to create several symlinks an small scripts

meant to be run in one's personal scripts directory, in my case ~/bin
"""
import os
import stat
import configparser

def main():
    scriptconfig = configparser.ConfigParser()
    scriptconfig.read('bin-scripts.conf')
    for key in scriptconfig['symlinks']:
        dest = os.path.expanduser(scriptconfig['symlinks'][key])
        if not os.path.exists(key):
            os.symlink(dest, key)
    for key in scriptconfig['symlinks-check']:
        dest = os.path.expanduser(scriptconfig['symlinks-check'][key])
        if os.path.exists(dest) and not os.path.exists(key):
            os.symlink(dest, key)
    for key in scriptconfig['scripts']:
        if not os.path.exists(key):
            with open(key, 'w') as f:
                f.write(scriptconfig['scripts'][key])
            os.chmod(key, os.stat(key).st_mode | stat.S_IXUSR)
    for key in scriptconfig['scripts-sh']:
        if not os.path.exists(key):
            with open(key, 'w') as f:
                f.write('#! /bin/sh\n')
                f.write(scriptconfig['scripts-sh'][key])
            os.chmod(key, os.stat(key).st_mode | stat.S_IXUSR)
    for key in scriptconfig['scripts-bash']:
        if not os.path.exists(key):
            with open(key, 'w') as f:
                f.write('#! /bin/bash\n')
                f.write(scriptconfig['scripts-bash'][key])
            os.chmod(key, os.stat(key).st_mode | stat.S_IXUSR)
    for key in scriptconfig['symlinks-last']:
        dest = os.path.expanduser(scriptconfig['symlinks-last'][key])
        if not os.path.exists(key):
            os.symlink(dest, key)

if __name__ == '__main__':
    main()
