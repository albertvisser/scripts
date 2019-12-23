"""Invoke language support stuff
"""
import os
import os.path
from invoke import task
from session import get_project_dir


@task(help={'project': 'project to create language support for', 'language': 'language to use',
            'check': 'check only'})
def init(c, project, check=False, language=''):
    """create directory structure to add language support for ptoject
    """
    # get project location, cancel if project not known
    base = get_project_dir(project)
    print('project root according to session.py:', base)
    if not base:
        print('unknown project')
        return
    if language:
        langs = language.split('.')
    else:
        langs = ['en', 'nl']
    print(language, langs, check)
    return
    # create locale subdirectory
    newpath = os.path,join(base, 'locale')
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
            print(mls)
            continue
        if not test:
            os.mkdir(langpath)
        os.mkdir(os.path.join(langpath, 'LC_MESSAGES'))


@task(help={'sourcefile': 'file to gather texts from (leave empty to check current directory'})
def gettext(c, sourcefile=''):
    """gather strings from file

    verzamel gemarkeerde symbolen in het aangegeven source file
    en schrijf ze weg in een bestand genaamd messages.pot
    """
    if sourcefile == "":
        sourcefile = '.'
    c.run("pygettext {}".format(sourcefile))


@task(help={'language_code': 'designates language to create tanslation for'})
def poedit(c, language_code):
    """edit translations in language file

    bewerkt het aangegeven language file met poedit
    """
    fnaam = "{}.po".format(language_code)
    if not os.path.exists(fnaam):
        c.run('poedit')
    else:
        c.run("poedit {}".format(fnaam))


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


