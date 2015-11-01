# server data locations
server_root = '/usr/share/nginx/html'
apache_root = '/var/www'
projects_base = '/home/albert/projects'

# repository types
cherrypy_repos = ['logviewer', 'rst2html', 'magiokis-cherry']
django_repos = ['actiereg', 'albums', 'myprojects', 'magiokis-django']
bb_repos = django_repos[:-1] + cherrypy_repos[:-1] + ['apropos', 'bitbucket',
    'cssedit', 'doctree', 'filefindr', 'hotkeys', 'htmledit', 'notetree', 'probreg',
    'xmledit']
private_repos = ['bin', 'nginx-config']
# repos die geen locale working versie hebben
non_deploy_repos = ['absentie', 'doctool', 'magiokis', 'pythoneer']
non_bb_repos = ['cobtools', 'jvsdoe', 'leesjcl', 'magiokis-php'] + non_deploy_repos

# ik mis nu de repos voor magiokis-cherry, -django en -php omdat er een naam/directory
# verschil is tussen de working en de central repos is
# daarom was ik begonnen met een ander soort mapping in settings_newer.py
# maar dat is best een ingrijpende aanpassing
all_repos = bb_repos + private_repos + non_bb_repos
