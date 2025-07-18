"""Invoke tasks for managing html stuff in webserver directory
"""
import os
import datetime
import contextlib
from invoke import task
from settings import home_root, server_root, apache_root, webapps
R2HBASE = os.path.expanduser(os.path.join('~', 'projects', 'rst2html', 'rst2html-data'))


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
def list_wwwroot(c):
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
def stage(c, sitename, new_only=False, changed_only=False, filename='', list_only=False):
    """voor site gemaakt met rst2html: zet gewijzigde files in staging en commit

    standaard werking is om alleen gewijzigde documenten te stagen
    met `new-only` is het mogelijk om juist alle nieuwe documenten te stagen
      (handig bij het starten van een nieuwe site);
    met de `filename` optie kan een enkel nieuw document worden toegevoegd
    """
    # bepaal en controleer de mirror locatie
    root = os.path.join(R2HBASE, sitename)
    if not os.path.exists(root):
        print(f'No existing mirror location found for `{sitename}`')
        return
    with c.cd(root):
        result = c.run('hg st', hide='out', warn=True)
    if result.failed:
        print('Mirror location should be a Mercurial repository')
        return

    # bepaal en controleer de te stagen files
    newfiles = [line.split()[1] for line in result.stdout.split('\n') if line and line[0] == '?']
    chgfiles = [line.split()[1] for line in result.stdout.split('\n') if line and line[0] == 'M']
    if filename:
        if not os.path.exists(os.path.join(root, filename)):
            print('No such file')
            return
        if filename not in newfiles:
            print('Not a new file')
            return
        files = [filename]
    elif new_only:
        files = newfiles
    elif changed_only:
        files = chgfiles
    else:
        files = newfiles + chgfiles
    if not files:
        print('Nothing to stage')
        return

    # bij list optie: toon namen en exit
    if list_only:
        for item in sorted(files):
            mod = ' (new)' if item in newfiles and not new_only else ''
            print(f'{item}{mod}')
        print(f'\n{len(files)} files to be staged')
        return

    # kopieer naar staging locatie
    staging = os.path.join(root, '.staging')
    amend = os.path.exists(staging) and bool(os.listdir(staging))
    for item in files:
        dest = os.path.join(staging, item)
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
        with c.cd(root):
            result = c.run(f'cp {item} .staging/{item}')

    # commit de gestagede files zodat ze niet nog een keer geselecteerd worden

    with c.cd(root):
        if not amend:
            stage_message = ''  # f"staged on {datetime.datetime.today().strftime('%d-%m-%Y %H:%M')}"
            amendflag = ''
            ctype = 'new'
        else:
            result = c.run('hg heads -T "{desc}"', hide=True, warn=True)
            stage_message = result.stdout.strip()
            amendflag = ' --amend'
            ctype = 'existing'
        result = c.run(f'zenity --entry --title="Stage: {ctype} commit" --text="Enter'
                       f' commit message" --entry-text="{stage_message}"', hide=True, warn=True)
        stage_message = result.stdout.strip()
        failed = False
        if not stage_message:
            failed = True
            print('Afgebroken')
        else:
            to_add = ''
            if filename:
                to_add = " ".join(files)
            elif not changed_only:
                to_add = " ".join(newfiles)
            if to_add:
                result = c.run(f'hg add {to_add}')
                failed = result.failed
            if not failed:
                result = c.run(f'hg ci {' '.join(files)} {amendflag} -m "{stage_message}"')
                failed = result.failed
    if failed:
        for item in files:
            dest = os.path.join(root, '.staging', item)
            os.remove(dest)
    else:
        print(f'{len(files)} files staged')


@task(help={'sitename': 'name of site as used in rst2html config',
            'full': 'also list files in subdirs'})
def list_staged(c, sitename, full=False):
    """voor site gemaakt met rst2html: list staged files
    """
    root = os.path.join(R2HBASE, sitename)
    if not os.path.exists(root):
        print(f'No existing mirror location found for `{sitename}`')
        return
    # seflinks = True: geen twee maar drie levels: root bevat alleen index.html
    stagecount = 0

    if not os.path.exists(os.path.join(root, '.staging')):
        print(f'No staging area found for `{sitename}`')
        return
    # breakpoint()
    filelist = []
    subdirlist = []
    # print(list(os.scandir(os.path.join(root, '.staging'))))
    for item in sorted(os.scandir(os.path.join(root, '.staging')), key=lambda x: x.name):
        if item.is_dir():
            subdircount = 0
            # print(list(os.scandir(item)))
            for subitem in sorted(os.scandir(item), key=lambda x: x.name):
                if subitem.is_dir():
                    # print(list(os.scandir(subitem)))
                    for entry in sorted(os.scandir(subitem), key=lambda x: x.name):
                        if entry.is_file():
                            if full:
                                filelist.append(os.path.join(item.name, subitem.name, entry.name))
                            #     subdircount += 1
                            # filelist.append(os.path.join(item.name, subitem.name, entry.name))
                            subdircount += 1
                        # else:  # currently not possible
                else:  # if subitem.is_file:
                    if full or (has_seflinks_true(sitename)
                                and os.path.splitext(subitem.name)[1] == '.html'):
                        filelist.append(os.path.join(item.name, subitem.name))
                    #     subdircount += 1
                    # filelist.append(os.path.join(item.name, subitem.name))
                    subdircount += 1
            if subdircount and not full:
                subdirlist.append(f'{subdircount} file(s) in {item.name}/')
            stagecount += subdircount
        else:  # if item.is_file():
            filelist.append(item.name)
            stagecount += 1
    for item in filelist:
        print(item)
    for item in subdirlist:
        print(item)
    print(f'{stagecount} file(s) staged')


def has_seflinks_true(sitename):
    """als er geen andere htmls aanwezig zijn dan index en eventueel reflist dan gaan we er van uit
    # dat dit een site is met setting `seflinks` is True
    """
    root = os.path.join(R2HBASE, sitename, '.staging')
    pages_in_root = [x.name for x in os.scandir(root) if os.path.splitext(x.name)[1] == '.html']
    with contextlib.suppress(ValueError):  # allow for file being not present
        pages_in_root.remove('index.html')
    with contextlib.suppress(ValueError):  # allow for file being not present
        pages_in_root.remove('reflist.html')
    return not bool(pages_in_root)


@task(help={'sitename': 'name of site as used in rst2html config'})
def clear_staged(c, sitename):
    """voor site gemaakt met rst2html: clear staging area after copying files to live site
    """
    root = os.path.join(R2HBASE, sitename)
    if not os.path.exists(root):
        print(f'No existing mirror location found for `{sitename}`')
        return
    if not os.path.exists(os.path.join(root, '.staging')):
        print(f'No staging area found for `{sitename}`')
        return
    with c.cd(root):
        c.run('rm -r .staging')


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
