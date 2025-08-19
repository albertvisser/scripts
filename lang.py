"""Invoke language support stuff
"""
# in commit b58dc6b2 van 1 juni 2025 heb ik wijzigingen vastgelegd voor het gebruik van xgettext
# in plaats van pygettext, omdat ik die niet meer kon aanroepen
# maar het script pygettext.py bestaat nog wel, namelijk in /usr/lib/Tools/i17n/pygettext.py
# ik heb deze gesymlinkt in ~/bin als pygettext
# gelijksoortig heb ik msgfmt gesymlinkt als pymsgfmt
# dus ik zou de oorspronkelijke code die dit gebruikt terug kunnen ztten
# ik heb in elk geval een routine gemaakt die controleert of de symlinks (bestaan en) correct zijn
import os
import os.path
import sys
from invoke import task
from session import get_project_dir

pydir = f'/usr/{sys.platlibdir}/python{sys.version_info[0]}.{sys.version_info[1]}'
bindir = os.path.expanduser('~/bin')


def get_base_dir(project):
    """get project location, if not possible then default to current directory
    """
    if project == '.':
        project = os.path.basename(os.getcwd())
    return get_project_dir(project)


@task(help={'project': 'project to create language support for',
            'language': '(comma delimited list of) language(s) to use;'
                        ' specify "." to use the default languages `en` and `nl` ',
            'check': 'check only'})
def init(c, project, language, check=False):
    """create directory structure to add language support for project
    """
    # get project location, cancel if project not known
    base = get_base_dir(project)
    if not base:
        print('unknown project')
        return
    langs = ['en', 'nl'] if language == '.' else language.split(',')
    # print(project, language, langs, check)
    # create locale subdirectory
    newpath = os.path.join(base, 'locale')
    if not os.path.exists(newpath):
        if check:
            print('language support not present (no `locale` subdirectory)')
            return
        os.mkdir(newpath)
    # for each language, create LC_MESSAGES subdirectory
    for lang in langs:
        mld = 'language support'
        langpath = os.path.join(newpath, lang)
        test = os.path.exists(langpath)
        if check:
            if test:
                mld += ' already'
            else:
                mld = 'no ' + mld
            mld += ' present'
        else:
            if not test:
                os.mkdir(langpath)
            os.mkdir(os.path.join(langpath, 'LC_MESSAGES'))
            mld += ' initialized'
        mld += f' for language type `{lang}`'
        print(mld)


def uses_gettext(filename):
    "determine if a project has gettext support"
    use_gettext = False
    with open(filename) as f:
        for line in f:
            if 'import' in line and 'gettext' in line:
                use_gettext = True
                break
    return use_gettext


@task(help={'check': 'check only', 'fix': 'fix only'})
def check_symlinks(c, check=True, fix=False):
    """check and/or build symlinks to the scripts in Tools/i18n
    """
    scriptnames = {'pygettext': 'pygettext.py', 'pymsgfmt': 'msgfmt.py'}
    if check:
        for name in scriptnames:
            result = pyversion_found(c, name)
            if not result:
                print(f'~/bin/{name} is not a symlink or broken')
            else:
                print(f'~/bin/{name} is ok')
    if fix:
        for name, origin in scriptnames.items():
            with c.cd(bindir):
                c.run(f'rm -f {name}')  # nog controleren op resultaat?
                c.run(f'ln -s {pydir}/{origin} {name}')


def pyversion_found(c, name):
    """can we work witn pygettext scripts?
    """
    with c.cd(bindir):
        result = c.run(f'readlink {name}', hide=True)
    if result:
        result = os.path.exists(result.stdout.strip())
    return result


@task(help={'project': 'project name',
            'source': 'file to gather texts from (specify "." to check the entire project'})
def gettext(c, project, source):
    """gather strings from file

    verzamel gemarkeerde symbolen in het aangegeven source file
    en schrijf ze weg in een bestand genaamd messages.pot
    """
    base = get_base_dir(project)
    if not base:
        print('unknown project')
        return
    use_pyversion = pyversion_found(c, 'pygettext')
    if source == '.':
        sourcedir = determine_sourcedir(base)
    else:
        suffix = os.path.splitext(source)[1]
        if not suffix:
            source += '.py'
        elif suffix != '.py':
            print(f'{source} is not a python source file')
            return
        if not uses_gettext(source):
            print(f'{source} does not import gettext')
            return
    with c.cd(base):
        out = 'all' if source == '.' else source.replace('.', '-').replace('/', '-')
        outfile = f'locale/messages-{out}.pot'
        if use_pyversion:
            c.run(f"pygettext {source}")
            c.run(f'mv messages.pot {outfile}')
        else:
            toscan = source if source != '.' else sourcedir + '/*.py' if sourcedir else '*.py'
            c.run(f"xgettext {toscan}")
            c.run(f'mv messages.po {outfile}')
        print(f'created {outfile}')
        print('remember that detection only works in modules that import gettext')


def determine_sourcedir(base):
    """try to discover where the source files live
    """
    with open(os.path.join(base, '.sessionrc')) as f:
        for line in f:
            if line.startswith('progs'):
                data = line.split(' = ')[1]
                sourcedir = data.split('/')[0] if '/' in data else ''
                break
        else:
            sourcedir = ''
    return sourcedir


@task(help={'project': 'project name',
            'language': 'language to update translation for',
            'source': 'source file for catalog (specify "." if it is for the entire project)'})
def merge(c, project, language, source):
    """merge new strings from catalog into language file
    """
    base = get_base_dir(project)
    if not base:
        print('unknown project')
        return
    source = 'all' if source == '.' else source.replace('.', '-').replace('/', '-')
    with c.cd(os.path.join(base, 'locale')):
        langfile = f"{language}.po"
        catfile = f'messages-{source}.pot'
        c.run(f'msgmerge -U {langfile} {catfile}')
        print('merged.')


@task(help={'project': 'project name',
            'language': 'designates language to create translation for'})
def poedit(c, project, language):
    """edit translations in language file

    bewerkt het language file voor het aangegeven project en de aangegeven taal met poedit
    """
    base = get_base_dir(project)
    if not base:
        print('unknown project')
        return
    fnaam = os.path.join('locale', f"{language}.po")
    command = 'poedit'
    if os.path.exists(os.path.join(base, fnaam)):
        command = f'{command} {fnaam}'
    with c.cd(base):
        c.run(command)


@task(help={'project': 'project name',
            'language': 'designates language to create translation for',
            'appname': 'application name if different from project name, otherwise use "*"'})
def place(c, project, language, appname):
    """copy translation(s) into <appname> (* = equal to project, ! = project starting with capital)

    plaats het gecompileerde language file zodat het gebruikt kan worden
    """
    base = get_base_dir(project)
    if not base:
        print('unknown project')
        return
    use_pyversion = pyversion_found(c, 'pymsgfmt')
    if appname == '*':
        appname = os.path.basename(base)
    elif appname == '!':
        appname = os.path.basename(base).title()
    fromname = language + '.po'
    loc = os.path.join(language, 'LC_MESSAGES')
    for name in os.listdir(os.path.join(base, 'locale', loc)):
        if os.path.splitext(name)[1] == '.mo':
            toname = os.path.join(loc, name)
            break
    else:
        toname = os.path.join(loc, appname + '.mo')
    if use_pyversion:
        command = f'pymsgfmt -o {toname} {fromname}'
    else:
        command = f'msgfmt {fromname} -o {toname}'
    with c.cd(os.path.join(base, 'locale')):
        c.run(command)
