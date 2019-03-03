"""Invoke language support stuff
"""
import os
import os.path
from invoke import task


@task(help={'sourcefile': 'file to gather texts from (leave empty to check current directory'})
def gettext(c, sourcefile=''):
    """internalization: gather strings from file

    verzamel gemarkeerde symbolen in het aangegeven source file
    en schrijf ze weg in een bestand genaamd messages.pot
    """
    if sourcefile == "":
        sourcefile = '.'
    c.run("pygettext {}".format(sourcefile))


@task(help={'language_code': 'designates language to create tanslation for'})
def poedit(c, language_code):
    """internalization: edit translations in language file

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
    """internalization: copy translation(s) into <appname> (at <location>)

    plaats het gecompileerde language file zodat het gebruikt kan worden
    gebruik <locatie> als de c.rune directory niet direct onder de huidige zit
    """
    loc = 'c.rune'
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


