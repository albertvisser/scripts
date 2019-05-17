import os
from invoke import task
from settings import home_root, server_root, apache_root

@task(help={'names': 'comma separated list of filenames'})
def copy(c, names):
    "copy indicated file(s) from home_root to server_root"
    for name in names.split(','):
        c.run('sudo cp {1}/{0} {2}/{0}'.format(name, home_root, server_root))


@task(help={'names': 'comma separated list of filenames'})
def link(c, names):
    "copy indicated symlink(s) from ~/www/nginx-root to real nginx root"
    for name in names.split(','):
        dest = os.readlink(os.path.join(home_root, name))
        c.run('sudo ln -s {} {}'.format(dest, server_root))


@task(help={'names': 'comma separated list of filenames'})
def edit(c, names):
    "edit indicated file(s) in ~/www/nginx-root"
    for name in names.split(','):
        ## local('scite {}/{}'.format(home_root, name))
        c.run('htmledit {}/{}'.format(home_root, name))


@task
def update_sites(c):
    "update mydomains database and localhost/sites.html from /etc/hosts"
    with c.cd('~/www/django/mydomains'):
        c.run('python check_hosts.py')
    wwwcopy('sites.html')


@task
def list(c):
    "list files in default nginx root"
    c.run('ls -l {}'.format(server_root))


@task
def list_apache(c):
    "list files in default apache root"
    c.run('ls -l {}'.format(apache_root))


@task(help={'names': 'comma separated list of filenames'})
def edit_apache(c, names):
    "edit indicated file in apache root as-if edited directly"
    for name in names.split(','):
        c.run('cp {1}/{0} /tmp/{0}'.format(name, apache_root))
        ## get('{1}/{0} /tmp'.format(name, apache_root))
        c.run('scite /tmp/{0}'.format(name))
        c.run('sudo cp /tmp/{0} {1}/{0}'.format(name, apache_root))
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
            rc = c.run('chmod 644 {}'.format(fullname))
            if rc.failed:
                print('chmod failed on file {}'.format(fullname))
        elif os.path.isdir(fullname):
            rc = c.run('chmod 755 {}'.format(fullname))
            if rc.failed:
                print('chmod failed on directory {}'.format(fullname))
            else:
                permits(c, fullname)
