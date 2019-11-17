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
private_repos = ['bin', 'nginx-config']
non_web_repos = ['apropos', 'bitbucket', 'compare-tool', 'cssedit', 'doctree',
                 'filefindr', 'hotkeys', 'htmledit', 'modreader', 'notetree',
                 'probreg', 'xmledit', 'albumsgui']
non_web_repos.remove('bitbucket')  # let's forget about this one for now
non_deploy_repos = ['cobtools', 'jvsdoe', 'leesjcl', 'pythoneer']
bb_repos = django_repos + cherrypy_repos + non_web_repos + fcgi_repos
sf_repos = ['apropos']
git_repos = ['mylinter'] + bb_repos
non_bb_repos = []  # non_deploy_repos
all_repos = bb_repos + private_repos + non_bb_repos + git_repos[:1]
DO_NOT_LINT = fcgi_repos + non_deploy_repos  # + private_repos

# VivaldiHooks settings
vhooks_path = os.path.join('/home', 'albert', 'git_repos', 'VivaldiHooks')
appdir = 'vivaldi'
vivaldi_path = os.path.join('/opt', 'vivaldi-snapshot', 'resources')
vhooks_items = ({'name': 'browser.html', 'is_dir': False, 'backup': True},
                {'name': 'jdhooks.js', 'is_dir': False, 'backup': False},
                {'name': 'hooks', 'is_dir': True, 'backup': False})
