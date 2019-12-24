"""Invoke language support stuff
"""
import os
import os.path
from invoke import task
from session import get_project_dir


def get_base_dir(project):
    """get project location, if not possible then default to current directory
    """
    if project:
        return get_project_dir(project)
    return os.getcwd()


@task(help={'project': 'project to create language support for',
            'language': '(comma delimited list of) language(s) to use, if not provided then'
                        ' en,nl is used',
            'check': 'check only'})
def init(c, project, check=False, language=''):
    """create directory structure to add language support for project
    """
    # get project location, cancel if project not known
    base = get_project_dir(project)
    if not base:
        print('unknown project')
        return
    if language:
        langs = language.split(',')
    else:
        langs = ['en', 'nl']
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
        langpath = os.path.join(newpath, lang)
        test = os.path.exists(langpath)
        if check:
            mld = 'language support already' if test else 'no language support'
            mld += ' present for language `{}`'.format(lang)
            print(mld)
            continue
        if not test:
            os.mkdir(langpath)
        os.mkdir(os.path.join(langpath, 'LC_MESSAGES'))


@task(help={'project': 'project name, if not provided then the current directory is used',
            'sourcefile': 'file to gather texts from (do not specify to check the entire project'})
def gettext(c, project='', sourcefile=''):
    """gather strings from file

    verzamel gemarkeerde symbolen in het aangegeven source file
    en schrijf ze weg in een bestand genaamd messages.pot
    """
    base = get_base_dir(project)
    if not base:
        print('unknown project')
        return
    if sourcefile == "":
        sourcefile = '.'
    with c.cd(base):
        c.run("pygettext {}".format(sourcefile))


@task(help={'project': 'project name, if not provided then the current directory is used',
            'language_code': 'designates language to create translation for'})
def poedit(c, project, language_code):
    """edit translations in language file

    bewerkt het aangegeven language file met poedit
    """
    base = get_base_dir(project)
    if not base:
        print('unknown project')
        return
    fnaam = "{}.po".format(language_code)
    command = 'poedit'
    if os.path.exists(fnaam):
        command = ' '.join((command, fnaam))
    with c.cd(base):
        c.run(command)


# TODO: add project name parameter and change behaviour
# 'project': 'project name, if not provided then the current directory is used',
# 'appname': 'name of application to create translation for - defaults to project name ',
@task(help={'language_code': 'designates language to create tanslation for',
            'appname': 'name of application to create translation for',
            'locatie': 'where to put the language file if not below current directory'})
def place(c, language_code, appname, locatie=""):
    """copy translation(s) into <appname> (at <location>)

    plaats het gecompileerde language file zodat het gebruikt kan worden
    gebruik <locatie> als de `locale` directory niet direct onder de huidige zit
    """
    loc = 'locale'
    if locatie:
        loc = os.path.join(locatie, loc)
    loc = os.path.abspath(loc)
    if not os.path.exists(loc):
        os.mkdir(loc)
    loc = os.path.join(loc, language_code)
    if not os.path.exists(loc):
        os.mkdir(loc)
    loc = os.path.join(loc, 'LC_MESSAGES')
    if not os.path.exists(loc):
        os.mkdir(loc)
    c.run('msgfmt {}.po -o {}'.format(language_code, os.path.join(loc, appname + '.mo')))
