import os.path
# server data locations
server_root = '/usr/share/nginx/html'
apache_root = '/var/www'
projects_base = os.path.expanduser('~/projects')

# repository types
cherrypy_repos = ['logviewer', 'rst2html', 'magiokis-cherry']
django_repos = ['actiereg', 'albums', 'myprojects', 'magiokis-django']
bb_repos = django_repos[:-1] + cherrypy_repos[:-1] + ['apropos', 'bitbucket',
    'cssedit', 'doctree', 'filefindr', 'hotkeys', 'htmledit', 'notetree', 'probreg',
    'xmledit']
private_repos = ['bin', 'nginx-config']
# repos die geen locale working versie hebben
non_deploy_repos = ['absentie', 'doctool', 'magiokis', 'pythoneer']
non_bb_repos = [django_repos[-1], cherrypy_repos[-1]] + ['cobtools', 'jvsdoe',
    'leesjcl', 'magiokis-php'] + non_deploy_repos

all_repos = bb_repos + private_repos + non_bb_repos
