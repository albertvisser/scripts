# server data locations
server_root = '/usr/share/nginx/html'
apache_root = '/var/www'

# repository types
cherrypy_repos = ['logviewer', 'rst2html']
# django repos hebben een andere local root
django_repos = ['actiereg', 'albums', 'myprojects']
bb_repos = django_repos + cherrypy_repos + ['apropos', 'bitbucket', 'cssedit',
    'doctree', 'filefindr', 'hotkeys', 'htmledit', 'notetree', 'probreg', 'xmledit']
non_bb_repos = ['cobtools', 'jvsdoe', 'leesjcl']
private_repos = ['bin', 'nginx-config']
all_repos = bb_repos + private_repos + non_bb_repos
# repos die geen locale working versie hebben
non_local_repos = ['absentie', 'doctool', 'magiokis', 'pythoneer']
