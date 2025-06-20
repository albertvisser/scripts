"""settings for fabfile
"""
import os
import pathlib
# server data locations
server_root = '/usr/share/nginx/html'
home_root = os.path.expanduser('~/www/nginx-root')
apache_root = '/var/www/html'

# project/session management
PROJECTS_BASE = os.path.expanduser('~/projects')
GITLOC = os.path.expanduser('~/git-repos')
r2hdata_basedir = os.path.join(PROJECTS_BASE, 'rst2html', 'rst2html-data')

# repository management
cherrypy_repos = ['logviewer', 'rst2html', 'magiokis-cherry']
django_repos = ['actiereg', 'albums', 'myprojects', 'magiokis-django']
fcgi_repos = ['absentie', 'doctool', 'magiokis', 'albums-cgi', 'magiokis-php']
private_repos = {'scripts': 'bin', 'server-stuff': 'nginx-config'}
non_web_repos = ['apropos', 'compare-tool', 'cssedit', 'doctree', 'filefindr', 'hotkeys',
                 'htmledit', 'modreader', 'notetree', 'probreg', 'xmledit', 'albumsgui']
non_deploy_repos = ['cobtools', 'jvsdoe', 'leesjcl', 'pythoneer']
bb_repos = django_repos + cherrypy_repos + non_web_repos + fcgi_repos
sf_repos = ['apropos']
# git_repos = ['mylinter', 'lminstreloc', 'sdvmm', 'mockgui'] + bb_repos
git_repos = ['lintergui', 'lminstreloc', 'sdvmm', 'mockgui'] + bb_repos
non_bb_repos = []  # non_deploy_repos
r2h_repos = {'magiokis-web': 'magiokis', 'magiokis-docs': 'magiokis-docs',
             'magiokis-docs-en': 'magiokis-docs-en'}
all_repos = git_repos + list(private_repos) + non_bb_repos
frozen_repos = fcgi_repos + [cherrypy_repos[-1], django_repos[-1]]
DO_NOT_LINT = frozen_repos + non_deploy_repos  # + private_repos

# VivaldiHooks settings
# vhooks_path = os.path.join('/home', 'albert', 'git_repos', 'VivaldiHooks')
# appdir = 'vivaldi'
# vivaldi_path = os.path.join('/opt', 'vivaldi-snapshot', 'resources')
# vhooks_items = ({'name': 'browser.html', 'is_dir': False, 'backup': True},
#                 {'name': 'jdhooks.js', 'is_dir': False, 'backup': False},
#                 {'name': 'hooks', 'is_dir': True, 'backup': False})

# deze zijn een tijd geleden gemaakt, de api lijkt nu anders te werken
# webapps = {'absenties': {'profile': 'absenties1349', 'adr': 'absenties.lemoncurry.nl',
#                        'start_server': False},
#            'actiereg': {'profile': 'actiereg5092', 'adr': 'actiereg.lemoncurry.nl',
#                        'start_server': '='},
#            'albums': {'profile': 'albums6963', 'adr': 'albums.lemoncurry.nl',
#                      'start_server': '='},
#            'albums-cgi': {'profile': 'albumsold2217', 'adr': 'muziek.lemoncurry.nl',
#                          'start_server': False},
#            'doctool': {'profile': 'doctool8234', 'adr': 'doctool.lemoncurry.nl',
#                       'start_server': False},
#            'logviewer': {'profile': 'logviewer7361', 'adr': 'logviewer.lemoncurry.nl',
#                         'start_server': '='},
#            'magiokis': {'profile': 'magiokis2979', 'adr': 'original.magiokis.nl',
#                        'start_server': False},
#            'magiokis-cherry': {'profile': 'magiokischerrypy4524', 'adr': 'cherrypy.magiokis.nl',
#                               'start_server': '='},
#            'magiokis-db': {'profile': 'magiokisdb9624', 'start_server': False,
#                            'adr': 'original.magiokis.nl/magiokis_launch.html'},
#            'magiokis-django': {'profile': 'magiokisdjango1292', 'adr': 'django.magiokis.nl',
#                               'start_server': 'magiokis'},
#            'magiokis-php': {'profile': 'magiokisphp6376', 'adr': 'php.magiokis.nl',
#                            'start_server': False},
#            'myprojects': {'profile': 'myprojects9887', 'adr': 'myprojects.lemoncurry.nl',
#                          'start_server': '='},
#            'rst2html': {'profile': 'rst2html3926', 'adr': 'rst2html.lemoncurry.nl',
#                        'start_server': 'rst2html_fs'},
#            'rst2html-mongo': {'profile': 'rst2htmlmongo3516', 'start_server': 'rst2html_mongo',
#                               'adr': 'rst2html-mongo.lemoncurry.nl'},
#            'rst2html-postgres': {'profile': 'rst2htmlpostgres7769', 'start_server':
#                                  'rst2html_postgres', 'adr': 'rst2html-pg.lemoncurry.nl'}}
# deze zijn op de nieuwe manier gemaakt (chromium api?)
webapps = {'cgit': {'appid': 'aihbdennncljibneldlcadheboalahee', 'start_server': False},
           'gitweb': {'appid': 'nhlpkodndoiadgldeanohldkpfoeahan', 'start_server': False},
           'tickets': {'appid': 'ddmclccmlegfljocpmghoodmgmmbcneh', 'start_server': 'trac'},
           'magiokis-web': {'appid': 'ccchclgdaokgeepoigdblhenppifabcb',
                            'start_server': 'rst2html_fs'},
           'magiokis-docs': {'appid': 'hbhjmhilnfcgofdnligbbhkkdlfbolai',
                             'start_server': 'rst2html_mongo'},
           'magiokis-docs-en': {'appid': 'hjnlopoojlljlgogkadaimjeopiggaae',
                                'start_server': 'rst2html_postgres'}}


def get_project_root(name, context='local'):
    """find out where a repository lives

    context can be 'local' or 'remote' or a repo type ('sf', 'bb', 'git')
    """
    is_private = name in private_repos
    for value in private_repos.values():
        if value == name:
            is_private = True
            break
    git_repo = name in git_repos
    sf_repo = name in sf_repos
    root = pathlib.Path(PROJECTS_BASE)
    if context == 'local':
        if is_private:
            root = root.parent
    elif is_private:
        where = 'hg_private' if context == 'bb' else 'git-repos'
        root = root.parent / where if context != 'sf' else 'n/a'
    elif git_repo:
        root = root.parent / 'git-repos' if context not in ('sf', 'bb') else 'n/a'
    elif sf_repo:
        root = root.parent / 'sf_repos' if context not in ('bb', 'git') else 'n/a'
    else:
        root = root.parent / 'hg_repos' if context not in ('git', 'sf') else 'n/a'
    return root


def get_project_dir(name):
    "private repos don't live in PROJECTS_BASE"
    if name in os.listdir(r2hdata_basedir):
        return os.path.join(r2hdata_basedir, name)
    base = get_project_root(name)
    # if name in private_repos:
    #     name = private_repos[name]
    name = private_repos.get(name, name)
    test = os.path.join(base, name)
    if os.path.exists(test):
        return test
    return ''
