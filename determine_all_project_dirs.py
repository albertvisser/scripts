"""Create a list containing the names of repository dictionaries

read the manifests for all active repositories and rmember all directories
containing tracked (Python) program sources
"""
# de lijst wordt wat langer dan het handmatig(?) samengestelde origineel
# maar ga er maar vanuit dat het wel klopt
import pathlib
import sys
import subprocess
sys.path.append(str(pathlib.Path.home() / 'bin'))
import settings


def determine_repo_dirs():
    """produce dictionary of files per repo based on manifests
    """
    alldirs = []
    for repo in settings.all_repos:
        if repo in ('bitbucket', 'magiokis-php'):
            continue

        if repo in settings.private_repos:
            path = pathlib.Path.home() / repo
        else:
            path = pathlib.Path.home() / 'projects' / repo

        if repo in settings.git_repos:
            command = ['git', 'ls-files']
        else:
            command = ['hg', 'manifest']
        result = subprocess.run(command,
                                cwd=str(path),
                                stdout=subprocess.PIPE).stdout
        dirs = set()
        for item in (x for x in str(result, encoding='utf-8').split('\n')
                     if x.endswith('.py')):
            try:
                dir, item = item.rsplit('/', 1)
            except ValueError:
                dir = ''
            dirs.add(dir)
        for item in dirs:
            if not item:
                alldirs.append(str(path))
            else:
                alldirs.append(str(path / item))
    return alldirs


def main(outfile):
    "main function"
    dirlist = determine_repo_dirs()
    with open(outfile, 'w') as _out:
        for item in dirlist:
            _out.write(item + '\n')


if __name__ == '__main__':
    ## print(dict2list({'x': ['1', '2'], 'y': ['4', '5', '6']}))
    main(sys.argv[1])
