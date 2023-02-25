"""Invoke commands for project/session/ticket management
"""
import os
import shutil
import configparser
import subprocess  # voor die ene die niet met invoke lukt
from invoke import task
from settings import PROJECTS_BASE, SESSIONS, DEVEL, get_project_dir  # , private_repos
# from repo import check_and_run_for_project


def get_project_name(ticket):
    "find_project_by_ticket(number)"
    hgrc = os.path.join(DEVEL, f'_{ticket}', '.hg', 'hgrc')
    conf = configparser.ConfigParser()
    conf.read(hgrc)
    return os.path.basename(conf['paths']['default'])


def get_regfile_name(name):
    "return standard path for ticket registration file"
    test = get_project_dir(name)
    if not test:
        return ''
    return os.path.join(test, '.tickets')


@task(help={'name': 'name for new software project'})
def newproject(c, name):
    """start a new (Python) software project in a standardized way
    """
    loc = os.path.join(PROJECTS_BASE, name)
    if os.path.exists(loc):
        print('sorry, this project name is already in use')
        return
    shutil.copytree(os.path.join(PROJECTS_BASE, 'skeleton'), loc)
    os.rename(os.path.join(loc, 'projectname'), os.path.join(loc, name))


# @task(help={'name': 'name of session file'})
def start_old(c, name):
    """start a programming session using various tools

    expects a session script of the same name in .sessions (subdirectory for now)
    """
    fname = os.path.join(SESSIONS, name)
    c.run(f'/bin/sh {fname}')


@task(help={'name': 'project name'})
def start(c, name):
    """start a programming session for a given repo using various tools

    expects a .sessionrc file in the project directory
    """
    # via run blijven het commando's wachten tot je het afsluit
    # met subprocess.Popen en shebangs in alle scripts werkt het wel
    runcommands = {'term': ['gnome-terminal', '--geometry=132x43+4+40'],
                   'check-repo': ['check-repo'],
                   'predit': ['predit'], 'dtree': ['dtree'], 'prfind': ['prfind']}
    path = get_project_dir(name)
    if not path:
        print('could not determine project location')
        return
    conf = configparser.ConfigParser()
    conf.read(os.path.join(path, '.sessionrc'))
    if not conf.sections():
        print('could not find session configuration')
        return
    myenv = os.environ
    for item in conf['env']:
        print(item)
        myenv[item] = conf['env'][item]
    print(myenv['progs'])
    for item in conf['options']:
        if item in runcommands and str(conf['options'][item]).lower() == 'y':
            subprocess.Popen(runcommands[item], cwd=path, env=myenv)


# @task(help={'name': 'name of session file'})
def edit_old(c, name):
    """define the tools to start a programming session with

    expects a session script of the same name in .sessions (subdirectory for now)
    each line contains a command to be executed
    """
    fname = os.path.join(SESSIONS, name)
    # c.run('scite {}'.format(fname))
    c.run(f'pedit {fname}')


@task(help={'name': 'project name'})
def editconf(c, name):
    """define the variables / tools to use in a session for a given repo

    checks for a .sessionrc file; if not found, provide one from a template
    """
    path = get_project_dir(name)
    if not path:
        print('could not determine project location')
        return
    fname = os.path.join(path, '.sessionrc')
    if not os.path.exists(fname):
        test = input('no file .sessionrc found - create one now (Y/n)?')
        if not test.lower().startswith('y'):
            return
        c.run(f'cp ~/bin/.sessionrc.template {fname}')
    c.run(f'pedit {fname}')


@task(help={'name': 'project name'})
def edittestconf(c, name):
    """define the locations of testscripts and scripts to test for a given repo

    checks for a .rurc file; if not found, provide one from a template
    """
    path = get_project_dir(name)
    if not path:
        print('could not determine project location')
        return
    fname = os.path.join(path, '.rurc')
    if not os.path.exists(fname):
        test = input('no file .rurc found - create one now (Y/n)?')
        if not test.lower().startswith('y'):
            return
        c.run(f'cp ~/bin/.rurc.template {fname}')
    c.run(f'pedit {fname}')


# @task
def list(c):
    """list existing session names"""
    names = sorted(f'    {x}' for x in os.listdir(SESSIONS))
    print("available sessions:")
    print('\n'.join(names))


# @task(help={'ticket': 'ticket number', 'project': 'project name'})
def newticket(c, ticket, project):
    """set up handling of a ticket for a given project

    clones the project repository and builds a session file
    """
    print('building new directory')
    root = '_' + ticket
    with c.cd(DEVEL):
        c.run(f'hg clone {get_project_dir(project)} {root}')
    dest = os.path.join(SESSIONS, ticket)
    settings = os.path.join(DEVEL, root, '.hg', 'hgrc')
    with open(settings) as _in:
        in_section = False
        for line in _in:
            if line.startswith('[paths]'):
                in_section = True
            elif in_section and line.startswith('default'):
                origin = line.split('=')[1].strip()
                break
        else:
            origin = ''
    if origin:
        origin = os.path.basename(origin)
        with open(dest, 'w') as _out:
            first = True
            with open(os.path.join(SESSIONS, origin)) as _in:
                for line in _in:
                    if line.startswith('cd ') and first:
                        line = f'cd {os.path.join(DEVEL, root)}\n'
                        first = False
                    _out.write(line)
                _out.write("a-propos -n 'Mee Bezig' -f mee_bezig.pck &")
    # finally: create a reminder that we have a ticket version of this repo
    regfile = get_regfile_name(project)
    mode = 'a' if os.path.exists(regfile) else 'w'
    with open(regfile, mode) as f:
        print(ticket, file=f)


# @task(help={'project': 'project name'})
def tickets(c, project):
    """list tickets in progress for project
    """
    regfile = get_regfile_name(project)
    if not regfile:
        print('wrong project name')
        return
    if not os.path.exists(regfile):
        ticketlist = 'none'
    else:
        with open(regfile) as f:
            ticketlist = ', '.join([x.strip() for x in f])
    print("tickets I'm working on:", ticketlist)


# @task(help={'ticket': 'ticket number'})
def prep(c, ticket):
    """check before pulling changes made for ticket into project
    """
    project = get_project_name(ticket)
    pull_dest = get_project_dir(project)
    pull_src = os.path.join(DEVEL, '_' + ticket)
    with c.cd(pull_dest):
        c.run(f'hg incoming -v {pull_src}')


# @task(help={'ticket': 'ticket number'})
def pull(c, ticket):
    """pull changes made for ticket into project
    """
    project = get_project_name(ticket)
    pull_dest = get_project_dir(project)
    pull_src = os.path.join(DEVEL, '_' + ticket)
    with c.cd(pull_dest):
        c.run(f'hg pull {pull_src}')
        c.run('hg up')


# @task(help={'ticket': 'ticket number'})
def cleanup(c, ticket):
    """finish handling of a ticket by removing the repo clone and the session file
    """
    project = get_project_name(ticket)
    # remove session file
    os.remove(os.path.join(SESSIONS, ticket))
    # remove repository
    shutil.rmtree(os.path.join(DEVEL, '_' + ticket))
    # remove reference in .tickets file
    regfile = get_regfile_name(project)
    with open(regfile) as f:
        projects = f.read().strip().split('\n')
    try:
        projects.remove(ticket)
    except ValueError:
        return
    if projects:
        with open(regfile, 'w') as f:
            f.write('\n'.join(projects) + '\n')
    else:
        os.remove(regfile)
