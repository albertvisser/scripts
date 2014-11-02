# server data locations
server_root = '/usr/share/nginx/html'
apache_root = '/var/www'

# repository types
bb_repos = ['actiereg', 'albums', 'apropos', 'bitbucket', 'doctree',
    'filefindr', 'hotkeys', 'htmledit', 'logviewer', 'myprojects', 'notetree',
    'probreg', 'rst2html', 'xmledit']
non_bb_repos = ['cobtools', 'jvsdoe', 'leesjcl']
private_repos = ['bin', 'nginx-config']
all_repos = bb_repos + private_repos + non_bb_repos
# repos die geen locale working versie hebben
non_local_repos = ['absentie', 'doctool', 'magiokis', 'pythoneer']
# django repos hebben een andere local root
django_repos = ['actiereg', 'albums', 'myprojects']
cherrypy_repos = ['logviewer', 'rst2html']
