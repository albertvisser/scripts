"""settings for fabfile
"""
import os.path
# server data locations
server_root = '/usr/share/nginx/html'
home_root = os.path.expanduser('~/www/nginx-root')
apache_root = '/var/www/html'

# project/session management
PROJECTS_BASE = os.path.expanduser('~/projects')
SESSIONS = os.path.expanduser('~/bin/.sessions')
DEVEL = os.path.expanduser('~/devel')

# repository management
cherrypy_repos = ['logviewer', 'rst2html', 'magiokis-cherry']
django_repos = ['actiereg', 'albums', 'myprojects', 'magiokis-django']
fcgi_repos = ['absentie', 'doctool', 'magiokis', 'albums-cgi', 'magiokis-php']
private_repos = {'scripts': 'bin', 'server-stuff': 'nginx-config'}
non_web_repos = ['apropos', 'bitbucket', 'compare-tool', 'cssedit', 'doctree',
                 'filefindr', 'hotkeys', 'htmledit', 'modreader', 'notetree',
                 'probreg', 'xmledit', 'albumsgui']
non_web_repos.remove('bitbucket')  # let's forget about this one for now
non_deploy_repos = ['cobtools', 'jvsdoe', 'leesjcl', 'pythoneer']
bb_repos = django_repos + cherrypy_repos + non_web_repos + fcgi_repos
sf_repos = ['apropos']
git_repos = ['mylinter'] + bb_repos
non_bb_repos = []  # non_deploy_repos
all_repos = git_repos + [x for x in private_repos] + non_bb_repos
DO_NOT_LINT = fcgi_repos + non_deploy_repos  # + private_repos

# VivaldiHooks settings
vhooks_path = os.path.join('/home', 'albert', 'git_repos', 'VivaldiHooks')
appdir = 'vivaldi'
vivaldi_path = os.path.join('/opt', 'vivaldi-snapshot', 'resources')
vhooks_items = ({'name': 'browser.html', 'is_dir': False, 'backup': True},
                {'name': 'jdhooks.js', 'is_dir': False, 'backup': False},
                {'name': 'hooks', 'is_dir': True, 'backup': False})


def get_project_root(name, context='local'):
    """find out where a repository lives

    context can be 'local' or 'remote' or a repo type ('sf', 'bb', 'git')
    """
    # TODO: add site repositories like 'bitbucket'
    is_private = name in private_repos
    is_private_value = name in private_repos.values()
    if is_private_value:
        value = name
        for name in private_repos:
            if private_repos[name] == value:
                is_private = True
                break
        else:
            name = ''
    git_repo = name in git_repos
    sf_repo = name in sf_repos
    import pathlib
    root = pathlib.Path(PROJECTS_BASE)
    if context == 'local':
        if is_private:
            root = root.parent
    else:  # if context in ('remote', 'bb'):
        if is_private:
            root = root.parent / 'hg_private'
        elif git_repo and context not in ('sf', 'bb'):
            root = root.parent / 'git-repos'
        elif sf_repo and context == 'sf':
            root = root.parent / 'sf_repos'
        elif context not in ('git', 'sf'):
            root = root.parent / 'hg_repos'
    return root


def get_project_dir(name):
    "private repos don't live in PROJECTS_BASE"
    base = get_project_root(name)
    if name in private_repos:
        name = private_repos[name]
    test = os.path.join(base, name)
    if os.path.exists(test):
        return test
    return ''
