"""Invoke language support stuff
"""
import os
import os.path
from invoke import task
from session import get_project_dir


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
    if language == '.':
        langs = ['en', 'nl']
    else:
        langs = language.split(',')
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
    with open(filename) as f:  # TODO: vervangen door nette test met importlib en inspect?
        for line in f:
            if 'import' in line and 'gettext' in line:
                use_gettext = True
                break
    return use_gettext


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
    if source != '.':
        name, suffix = os.path.splitext(source)
        if not suffix:
            source += '.py'
        elif suffix != '.py':
            print(f'{source} is not a python source file')
            return
        if not uses_gettext(source):
            print(f'{source} does not import gettext')
            return
    with c.cd(base):
        c.run(f"pygettext {source}")
        if source == '.':
            source = 'all'
        else:
            source = source.replace('.', '-').replace('/', '-')
        outfile = f'locale/messages-{source}.pot'
        c.run(f'mv messages.pot {outfile}')
        print(f'created {outfile}')
        print('remember that detection only works in modules that import gettext')


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
    if source == '.':
        source = 'all'
    else:
        source = source.replace('.', '-').replace('/', '-')
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
        command = ' '.join((command, fnaam))
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
    if appname == '*':
        appname = os.path.basename(base)
    elif appname == '!':
        appname = os.path.basename(base).title()
    fromname = language + '.po'
    toname = os.path.join(language, 'LC_MESSAGES', appname + '.mo')
    # kijken of er al een werkend .mo file bestaat, voor het geval die eigenlijk in mixed-case is
    # helaas werkt dit nog niet  waarschijnlijk omdat ik de hele splitext uitvroeg i.p.v. deel 2
    loc = os.path.join(language, 'LC_MESSAGES')
    for name in os.listdir(os.path.join(base, 'locale', loc)):
        print(name)
        if os.path.splitext(name)[1] == '.mo':
            toname = os.path.join(loc, name)
            break
    command = f'msgfmt {fromname} -o {toname}'
    with c.cd(os.path.join(base, 'locale')):
        c.run(command)
