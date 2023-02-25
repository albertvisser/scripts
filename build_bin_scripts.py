"""scripts to create several symlinks an small scripts

meant to be run in one's personal scripts directory, in my case ~/bin
"""
import os
import stat
import configparser

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
            # for line in scriptconfig['scripts'][key]:
            #     print(line, file=f)
            f.write(scriptconfig['scripts'][key])
        os.chmod(key, os.stat(key).st_mode | stat.S_IXUSR)
for key in scriptconfig['symlinks-last']:
    dest = os.path.expanduser(scriptconfig['symlinks-last'][key])
    if not os.path.exists(key):
        os.symlink(dest, key)
