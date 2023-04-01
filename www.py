"""Invoke tasks for managing html stuff in webserver directory
"""
import os
import datetime
from invoke import task
from settings import home_root, server_root, apache_root, webapps


@task(help={'names': 'comma separated list of filenames'})
def copy(c, names):
    "copy indicated file(s) from home_root to server_root"
    for name in names.split(','):
        opt = '-r' if os.path.isdir(f'{home_root}/{name}') else ''
        c.run(f'sudo cp {opt} {home_root}/{name} {server_root}/{name}')


@task(help={'names': 'comma separated list of filenames'})
def link(c, names):
    "copy indicated symlink(s) from ~/www/nginx-root to real nginx root"
    for name in names.split(','):
        dest = os.readlink(os.path.join(home_root, name))
        c.run(f'sudo ln -s {dest} {server_root}')


@task(help={'names': 'comma separated list of filenames'})
def edit(c, names):
    "edit indicated file(s) in ~/www/nginx-root"
    for name in names.split(','):
        ## local('scite {}/{}'.format(home_root, name))
        c.run(f'htmledit {home_root}/{name}')


@task
def update_sites(c):
    "update mydomains database and localhost/sites.html from /etc/hosts"
    with c.cd('~/projects/mydomains'):
        c.run('python check_hosts.py')
    copy(c, 'sites.html')


@task
def list(c):
    "list files in default nginx root"
    c.run(f'ls -l {server_root}')


@task
def list_apache(c):
    "list files in default apache root"
    c.run(f'ls -l {apache_root}')


@task(help={'names': 'comma separated list of filenames'})
def edit_apache(c, names):
    "edit indicated file in apache root as-if edited directly"
    for name in names.split(','):
        c.run(f'cp {apache_root}/{name} /tmp/{name}')
        ## get('{1}/{0} /tmp'.format(name, apache_root))
        c.run(f'pedit /tmp/{name}')
        c.run(f'sudo cp /tmp/{name} {apache_root}/{name}')
        ## put('/tmp/{0} {1}'.format(name, apache_root), use_sudo=True)


@task(help={'name': 'comma separated list of directory names',
            'do-files': 'process files as well as directories'})
def permits(c, name, do_files=False):
    """reset permits for dirs/files under web-accessible root
    """
    path = os.path.abspath(name)
    for file in os.listdir(path):
        fullname = os.path.join(path, file)
        if os.path.isfile(fullname) and do_files:
            rc = c.run(f'chmod 644 {fullname}')
            if rc.failed:
                print(f'chmod failed on file {fullname}')
        elif os.path.isdir(fullname):
            rc = c.run(f'chmod 755 {fullname}')
            if rc.failed:
                print(f'chmod failed on directory {fullname}')
            else:
                permits(c, fullname)


@task(help={'sitename': 'name of site as used in rst2html config',
            'new_only': 'only stage new files',
            'filename': 'only stage this (new) file',
            'list-only': 'do not actually stage, just show the names'})
def stage(c, sitename, new_only=False, filename='', list_only=False):
    """voor site gemaakt met rst2html: zet gewijzigde files in staging en commit

    standaard werking is om alleen gewijzigde documenten te stagen
    met `new-only` is het mogelijk om juist alle nieuwe documenten te stagen
      (handig bij het starten van een nieuwe site);
    met de `filename` optie kan een enkel nieuw document worden toegevoegd
    """
    # bepaal en controleer de mirror locatie
    root = os.path.expanduser(os.path.join('~', 'www', sitename))
    if not os.path.exists(root):
        root = os.path.expanduser(os.path.join('~', 'projects', 'rst2html', 'rst2html-data',
                                               sitename))
    if not os.path.exists(root):
        print(f'no existing mirror location found for `{sitename}`')
        return
    with c.cd(root):
        result = c.run('hg st', hide='out', warn=True)
    if result.failed:
        print('mirror location should be a mercurial repository')
        return

    # bepaal en controleer de te stagen files
    newfiles = [line.split()[1] for line in result.stdout.split('\n') if line and line[0] == '?']
    if filename:
        if not os.path.exists(os.path.join(root, filename)):
            print('no such file')
            return
        if filename not in newfiles:
            print('not a new file')
            return
        files = [filename]
    elif new_only:
        files = newfiles
    else:
        files = [line.split()[1] for line in result.stdout.split('\n') if line and line[0] != '?']
    if not files:
        print('nothing to stage')
        return

    # bij list optie: toon namen en exit
    if list_only:
        for item in files:
            print(item)
        print(f'\n{len(files)} files to be staged')
        return

    # kopieer naar staging locatie
    for item in files:
        dest = os.path.join(root, '.staging', item)
        if not os.path.exists(dest):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
        with c.cd(root):
            result = c.run(f'cp {item} .staging/{item}')
    print(f'{len(files)} files staged')

    # commit de gestagede files zodat ze niet nog een keer geselecteerd worden
    with c.cd(root):
        if filename:
            c.run(f'hg add {filename}')
        elif new_only:
            c.run(f'hg add {" ".join(newfiles)}')
        now = datetime.datetime.today().strftime('%d-%m-%Y %H:%M')
        c.run(f'hg ci -m "staged on {now}"')


@task(help={'name': 'name of webapp to start'})
def startapp(c, name):
    "start webapp created from webpage"
    if name not in webapps:
        print('unknown webapp')
        return
    test = name if webapps[name]['start_server'] == '=' else webapps[name]['start_server']
    if webapps[name]['start_server'] and not os.path.exists(f'/tmp/server-{test}-ok'):
        c.run(f'fabsrv server.start -n {test}')
    if 'appid' in webapps[name]:
        # nieuwe api
        # c.run('/home/albert/.local/share/vivaldi-snapshot/vivaldi-snapshot'
        c.run('/opt/vivaldi/vivaldi'
              f' --profile-directory=Default --app-id={webapps[name]["appid"]}')
    else:
        c.run(f'vivaldi-snapshot --app=http://{webapps[name]["adr"]}'
              f' --class=WebApp-{webapps[name]["profile"]} --user-data-dir=/home/albert/'
              f'.local/share/ice/profiles/{webapps[name]["profile"]}')
