import os.path
# server data locations
server_root = '/usr/share/nginx/html'
apache_root = '/var/www'
projects_base = os.path.expanduser('~/projects')

# repository types
cherrypy_repos = ['logviewer', 'rst2html', 'magiokis-cherry']
django_repos = ['actiereg', 'albums', 'myprojects', 'magiokis-django']
fcgi_repos = ['absentie', 'doctool', 'magiokis', 'albums-cgi', 'magiokis-php']
private_repos = ['bin', 'nginx-config']
non_web_repos = ['apropos', 'bitbucket', 'compare-tool', 'cssedit', 'doctree',
    'filefindr', 'hotkeys', 'htmledit', 'modreader', 'notetree', 'probreg',
    'xmledit']
non_deploy_repos = ['cobtools', 'jvsdoe', 'leesjcl',  'pythoneer']
bb_repos = django_repos + cherrypy_repos + non_web_repos + fcgi_repos
non_bb_repos = non_deploy_repos

all_repos = bb_repos + private_repos + non_bb_repos
