"""scriptlib.py - utilities voor de behandeling van bin-scripts.conf
"""
import pathlib
import shutil
from invoke import task
from configparser import ConfigParser


@task(help={'name': 'name of the script or symlink to add',
            'section': 'name of the section to add the script or symlink into'})
def add(c, name, section):
    "voeg de inhoud van een bestaand scriptlet toe aan de library"
    lib = ScriptLib()
    if section.startswith('symlinks'):
        retval = lib.add_link(name, section)
    else:
        retval = lib.add_script(name, section)
    if retval:
        print(retval)
    else:
        print(f'{name} successfully added')


@task(help={'name': 'name of the script or symlink to compare - use "all" for the entire library'})
def check(c, name):
    "vergelijk de inhoud van een scriptlet met wat er in de library staat"
    lib = ScriptLib()
    if name == 'all':
        diffs = []
        for name in lib.get_all_names():
            in_lib, actual = check_file(lib, name)
            if lib != actual:
                diffs.append(name)
        if diffs:
            print('verschillen gevonden voor:')
            for name in diffs:
                print(name)
    else:
        in_lib, actual = check_file(lib, name)
        if not in_lib:
            print('not found in library')
        elif in_lib == actual:
            print('no difference')
        else:
            print('--- library version:')
            print(in_lib)
            print('+++ version in scripts:')
            print(actual)


@task(help={'name': 'name of the script or symlink to update - use "all" for the entire library'})
def update(c, name):
    "neem een gewijzigd script over in de library"
    lib = ScriptLib()
    if name == 'all':
        for name in lib.get_all_names():
            diff = check_and_update(lib, name)
            if diff:
                diffs.append(name)
        if diffs:
            lib.update()
            print('verschillen gevonden en bijgewerkt voor:')
            for name in diffs:
                print(name)
    else:
        diff = check_and_update(lib, name)
        if diff:
            lib.update()
            print('verschil gevonden en bijgewerkt')


@task(help={'name': ('name of the script or symlink to add to the ignore file'
                     ' - use "all" to check the entire library')})
def ignore(c, name):
    "werk .gitignore bij met de scripts die in scriptlib staan"
    lib = ScriptLib()
    # verwacht elke te negeren script naam op een aparte regel
    ignores = (lib.basepath / '.gitignore').read_text().split('\n')
    not_present = []
    if name == 'all':
        for name in lib.get_all_names():
            if name not in ignores:
                not_present.append(name)
    else:
        if name not in lib.get_all_names():
            print('not in library')
            return
        if name not in ignores:
            not_present.append(name)
    for name in not_present:
        ignores.append(name)
    (lib.basepath / '.gitignore').write_text('\n'.join(ignores))


def check_and_update(lib, name):
    "if the library version and the actual version of a script or symlink differ, replace in library"
    library_version, actual_version = check_file(lib, name)
    if library_version != actual_version:
        section = lib.find(lib, name)
        lib.data[section][name] = actual_version
        return name
    return ''


def check_file(lib, name):
    "get the library version and the actual version of a script or symlink"
    section = lib.find(lib, name)
    if not section:
        return None, None
    library_version = lib.data[section][name]
    path = lib.basepath / name
    if section.startswith('symlinks'):
        actual_version = path.readlink()
    else:
        actual_version = path.read_text()
    return library_version, actual_version


class ScriptLib:
    """Lees en schrijf bin-scripts.conf met behulp van een ConfigParser

    sections in bin-scripts:
        symlinks: naam links verwijst naar target (full path) rechts
        symlinks-check: idem, target existence check in build-bin-scripts
        scripts: naam links, inhoud rechts - multiline (inspringen) mogelijk
        scripts-sh: idem, shebang naar sh toevoegen in build-bin-scripts
        scripts-bash: idem, schebang naar bash toevoegen in build-bin-scripts
        symlinks-last: als eerste sectie, voor symlinks naar scripts
    """
    def __init__(self):
        self.basepath = pathlib.Path('~/bin').expanduser()
        self.libname = 'bin-scripts.conf'
        self.libpath = self.basepath / self.libname
        self.data = ConfigParser()
        self.read()

    def read(self):
        "config lezen"
        with self.libpath.open() as _in:
            self.data.read_file(_in)

    def update(self):
        "config schrijven"
        shutil.copyfile(str(self.libpath), str(self.libpath) + '~')
        with self.libpath.open('w') as _out:
            self.data.write(_out)

    def find(self, name):
        "vind de sectie waar een entry in zit"
        for section in self.data:
            if name in self.data[section]:
                return section
        return None

    def get_all_names(self):
        "maak een lijst van alle script- en symlink namen"
        names = []
        for section in self.data:
            names += list(self.data[section])
        return names

    def add_link(self, name, section):
        "item toevoegen in een symlink sectie"
        path = self.basepath / name
        if not path.is_symlink():
            return 'not a valid symlink'
        if section not in ('symlinks', 'symlinks-check', 'symlinks-last'):
            return 'wrong section'
        target = path.readlink()
        if section not in self.data:
            self.data.add_section(section)
        self.data.set(section, name, target)
        return ''

    def add_script(self, name, section):
        "item toevoegen in een scripts sectie"
        path = self.basepath / name
        if not path.is_file() or path.is_symlink():
            return 'not a valid file'
        if section not in ('scripts', 'scripts-sh', 'scripts-bash'):
            return 'wrong section'
        script = path.read_text()  # .replace('\n', '\n\t'  - )not sure if I need this
        if section not in self.data:
            self.data.add_section(section)
        self.data.set(section, name, script)
        return ''
