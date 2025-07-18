"""unittests for ./scriptlib.py
"""
import types
import scriptlib as testee
from invoke import MockContext


class MockParser:
    """stub for configparser.ConfigParser
    """
    def __init__(self):
        print('called ConfigParser.__init__')


class MockLib:
    """stub for scriptlib.ScriptLib
    """
    def __init__(self):
        print('called ScriptLib.__init__')
        self.basepath = testee.pathlib.Path('x')
        self.data = testee.ConfigParser()
        self.data.read_dict({'section1': {'key1': 'value1', 'key2': 'value2'},
                             'section2': {'key3': 'value3'}})

    def sections(self):
        "stub"
        print('called Scriptlib.sections')
        return ('section1', 'section2')

    def read_file(self, *args):
        """stub
        """

    def update(self, *args):
        """stub
        """
        print('called ScriptLib.update')

    def clear(self):
        """stub
        """
        for name in self.data.sections():
            self.data.remove_section(name)

    def find(self, name):
        """stub
        """
        print(f'called ScriptLib.find with arg `{name}`')
        if name in ('key1', 'key2'):
            return 'section1'
        if name == 'key3':
            return 'section2'
        return 'section0'

    def get_all_names(self, **kwargs):
        """stub
        """
        print('called ScriptLib.get_all_names with args', kwargs)
        return 'tom', 'dick', 'harry', 'sally'

    def add_link(self, *args):
        """stub
        """
        print('called ScriptLib.add_link with args', args)

    def add_script(self, *args):
        """stub
        """
        print('called ScriptLib.add_script with args', args)

    def list_contents(self):
        """stub
        """
        # voor de commando tests heeft dit niet veel zin omdat het object niet van buiten de functie
        # gelezen kan worden
        contents = []
        for name1 in self.data.sections():
            for name2 in self.data.options(name1):
                contents.append((str(name1), str(name2), self.data.get()))


def test_add(monkeypatch, capsys):
    """unittest for scriptlib.add
    """
    def mock_determine(name):
        print(f'called determine_section with arg {name}')
        return 'section name'
    def mock_read(*args):
        """stub
        """
        print('called path.read_text with args', args)
        return 'harry\nsally'
    def mock_copy(*args):
        """stub
        """
        print('called shutil.copyfile with args', args)
    def mock_write(*args):
        """stub
        """
        print('called path.write_text with args', args)
    monkeypatch.setattr(testee.shutil, 'copyfile', mock_copy)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read)
    monkeypatch.setattr(testee.pathlib.Path, 'write_text', mock_write)
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    monkeypatch.setattr(testee, 'determine_section', mock_determine)
    c = MockContext()
    testee.add(c, 'test')
    assert capsys.readouterr().out == (
            "called ScriptLib.__init__\n"
            "called determine_section with arg test\n"
            "called ScriptLib.add_script with args ('test', 'section name')\n"
            "called ScriptLib.update\n"
            "called path.read_text with args (PosixPath('x/.gitignore'),)\n"
            "called shutil.copyfile with args ('x/.gitignore', 'x/.gitignore~')\n"
            "called path.write_text with args (PosixPath('x/.gitignore'), 'harry\\nsally\\ntest')\n"
            "'test' successfully added to library and .gitignore\n"
            "Don't forget to also add it to readme.rst\n")
    testee.add(c, 'test', 'symlinks')
    assert capsys.readouterr().out == (
            "called ScriptLib.__init__\n"
            "called ScriptLib.add_link with args ('test', 'symlinks')\n"
            "called ScriptLib.update\n"
            "called path.read_text with args (PosixPath('x/.gitignore'),)\n"
            "called shutil.copyfile with args ('x/.gitignore', 'x/.gitignore~')\n"
            "called path.write_text with args (PosixPath('x/.gitignore'), 'harry\\nsally\\ntest')\n"
            "'test' successfully added to library and .gitignore\n"
            "Don't forget to also add it to readme.rst\n")
    testee.add(c, 'test', 'scripts')
    assert capsys.readouterr().out == (
            "called ScriptLib.__init__\n"
            "called ScriptLib.add_script with args ('test', 'scripts')\n"
            "called ScriptLib.update\n"
            "called path.read_text with args (PosixPath('x/.gitignore'),)\n"
            "called shutil.copyfile with args ('x/.gitignore', 'x/.gitignore~')\n"
            "called path.write_text with args (PosixPath('x/.gitignore'), 'harry\\nsally\\ntest')\n"
            "'test' successfully added to library and .gitignore\n"
            "Don't forget to also add it to readme.rst\n")
    monkeypatch.setattr(MockLib, 'add_link', lambda *x: 'error adding link')
    monkeypatch.setattr(MockLib, 'add_script', lambda *x: 'error adding script')
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    testee.add(c, 'test', 'symlinks')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "error adding link\n")
    testee.add(c, 'test', 'scripts')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "error adding script\n")


def test_determine_section(monkeypatch, capsys):
    """unittest for scriptlib.determine_section
    """
    def mock_islink(arg):
        print(f'called path.is_link with arg {arg}')
        return True
    def mock_islink2(arg):
        print(f'called path.is_link with arg {arg}')
        return False
    def mock_read(arg):
        print(f'called path.read_text with arg {arg}')
        return 'bladibla'
    def mock_read2(arg):
        print(f'called path.read_text with arg {arg}')
        return "#! this"
    def mock_read3(arg):
        print(f'called path.read_text with arg {arg}')
        return "#! /this"
    def mock_read4(arg):
        print(f'called path.read_text with arg {arg}')
        return "#! /this/that"
    def mock_read5(arg):
        print(f'called path.read_text with arg {arg}')
        return "#! this/that"
    monkeypatch.setattr(testee.pathlib.Path, 'expanduser',
                        lambda x: testee.pathlib.Path(str(x).replace('~', '/home')))
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', mock_islink)
    assert testee.determine_section('name') == "symlinks"
    assert capsys.readouterr().out == ("called path.is_link with arg /home/bin/name\n")
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', mock_islink2)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read)
    assert testee.determine_section('name') == "scripts"
    assert capsys.readouterr().out == ("called path.is_link with arg /home/bin/name\n"
                                       "called path.read_text with arg /home/bin/name\n")
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read2)
    assert testee.determine_section('name') == "scripts-this"
    assert capsys.readouterr().out == ("called path.is_link with arg /home/bin/name\n"
                                       "called path.read_text with arg /home/bin/name\n")
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read3)
    assert testee.determine_section('name') == "scripts-this"
    assert capsys.readouterr().out == ("called path.is_link with arg /home/bin/name\n"
                                       "called path.read_text with arg /home/bin/name\n")
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read4)
    assert testee.determine_section('name') == "scripts-that"
    assert capsys.readouterr().out == ("called path.is_link with arg /home/bin/name\n"
                                       "called path.read_text with arg /home/bin/name\n")
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read5)
    assert testee.determine_section('name') == "scripts-that"
    assert capsys.readouterr().out == ("called path.is_link with arg /home/bin/name\n"
                                       "called path.read_text with arg /home/bin/name\n")


def test_check(monkeypatch, capsys):
    """unittest for scriptlib.check
    """
    def mock_check(lib, name):
        """stub
        """
        print(f'called check_file with args {type(lib)} {name}')
        return 'in_lib', 'actual'
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    monkeypatch.setattr(testee, 'check_file', mock_check)
    c = MockContext()
    testee.check(c, 'name')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called check_file with args"
                                       " <class 'test_scriptlib.MockLib'> name\n"
                                       "--- library version:\n"
                                       "in_lib\n"
                                       "+++ version in scripts:\n"
                                       "actual\n")
    monkeypatch.setattr(testee, 'check_file', lambda *x: ('equal', 'equal'))
    testee.check(c, 'name')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       'no difference\n')
    monkeypatch.setattr(testee, 'check_file', lambda *x: (None, None))
    testee.check(c, 'name')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       'not found in library\n')


def test_check_all(monkeypatch, capsys):
    """unittest for scriptlib.check_all
    """
    counter = 0
    def mock_check(lib, name):
        """stub
        """
        nonlocal counter
        print(f'called check_file with args {type(lib)} {name}')
        counter += 1
        if counter == 2:
            return 'equal', 'equal'
        return 'in_lib', 'actual'
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    monkeypatch.setattr(testee, 'check_file', mock_check)
    c = MockContext()
    testee.check(c, 'all')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called ScriptLib.get_all_names with args {}\n"
                                       "called check_file with args"
                                       " <class 'test_scriptlib.MockLib'> tom\n"
                                       "called check_file with args"
                                       " <class 'test_scriptlib.MockLib'> dick\n"
                                       "called check_file with args"
                                       " <class 'test_scriptlib.MockLib'> harry\n"
                                       "called check_file with args"
                                       " <class 'test_scriptlib.MockLib'> sally\n"
                                       'verschillen gevonden voor:\n'
                                       'tom\n'
                                       'harry\n'
                                       'sally\n')
    monkeypatch.setattr(testee, 'check_file', lambda *x: ('equal', 'equal'))
    testee.check(c, 'all')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called ScriptLib.get_all_names with args {}\n"
                                       'geen verschillen gevonden\n')


def test_update(monkeypatch, capsys):
    """unittest for scriptlib.update
    """
    def mock_check(lib, name):
        """stub
        """
        print(f'called check_and_update with args {type(lib)} {name}')
        return True
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    monkeypatch.setattr(testee, 'check_and_update', mock_check)
    c = MockContext()
    testee.update(c, 'test')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called check_and_update with args"
                                       " <class 'test_scriptlib.MockLib'> test\n"
                                       "called ScriptLib.update\n"
                                       'verschil gevonden en bijgewerkt\n')
    monkeypatch.setattr(testee, 'check_and_update', lambda *x: False)
    testee.update(c, 'test')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       'geen verschillen gevonden\n')


def test_update_all(monkeypatch, capsys):
    """unittest for scriptlib.update_all
    """
    counter = 0
    def mock_check(lib, name):
        """stub
        """
        nonlocal counter
        print(f'called check_and_update with args {type(lib)} {name}')
        counter += 1
        return counter % 2
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    monkeypatch.setattr(testee, 'check_and_update', mock_check)
    c = MockContext()
    testee.update(c, 'all')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called ScriptLib.get_all_names with args {}\n"
                                       "called check_and_update with args"
                                       " <class 'test_scriptlib.MockLib'> tom\n"
                                       "called check_and_update with args"
                                       " <class 'test_scriptlib.MockLib'> dick\n"
                                       "called check_and_update with args"
                                       " <class 'test_scriptlib.MockLib'> harry\n"
                                       "called check_and_update with args"
                                       " <class 'test_scriptlib.MockLib'> sally\n"
                                       "called ScriptLib.update\n"
                                       'verschillen gevonden en bijgewerkt voor:\n'
                                       'tom\n'
                                       'harry\n')
    monkeypatch.setattr(testee, 'check_and_update', lambda *x: False)
    testee.update(c, 'all')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called ScriptLib.get_all_names with args {}\n"
                                       'geen verschillen gevonden\n')


def test_check_ignore(monkeypatch, capsys):
    """unittest for scriptlib.check_ignore
    """
    def mock_read(*args):
        """stub
        """
        print('called path.read_text with args', args)
        return 'harry\nsally'
    def mock_copy(*args):
        """stub
        """
        print('called shutil.copyfile with args', args)
    def mock_write(*args):
        """stub
        """
        print('called path.write_text with args', args)
    monkeypatch.setattr(testee.shutil, 'copyfile', mock_copy)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read)
    monkeypatch.setattr(testee.pathlib.Path, 'write_text', mock_write)
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.check_ignore(c, 'test')
    assert capsys.readouterr().out == (
            'called ScriptLib.__init__\n'
            "called path.read_text with args (PosixPath('x/.gitignore'),)\n"
            'called ScriptLib.get_all_names with args {}\n' 'not in library\n')
    testee.check_ignore(c, 'dick', list_only=True)
    assert capsys.readouterr().out == (
            'called ScriptLib.__init__\n'
            "called path.read_text with args (PosixPath('x/.gitignore'),)\n"
            'called ScriptLib.get_all_names with args {}\n'
            "`dick` will be added to .gitignore\n")
    testee.check_ignore(c, 'dick')
    assert capsys.readouterr().out == (
            'called ScriptLib.__init__\n'
            "called path.read_text with args (PosixPath('x/.gitignore'),)\n"
            'called ScriptLib.get_all_names with args {}\n'
            "`dick` will be added to .gitignore\n"
            "called shutil.copyfile with args ('x/.gitignore', 'x/.gitignore~')\n"
            "called path.write_text with args (PosixPath('x/.gitignore'), 'harry\\nsally\\ndick')\n"
            "entries are added\n")
    testee.check_ignore(c, 'harry')
    assert capsys.readouterr().out == (
            'called ScriptLib.__init__\n'
            "called path.read_text with args (PosixPath('x/.gitignore'),)\n"
            'called ScriptLib.get_all_names with args {}\n'
            'already present in .gitignore\n')


def test_ignore_all(monkeypatch, capsys):
    """unittest for scriptlib.ignore_all
    """
    def mock_read(*args):
        """stub
        """
        print('called path.read_text with args', args)
        return 'harry\nsally'
    def mock_copy(*args):
        """stub
        """
        print('called shutil.copyfile with args', args)
    def mock_write(*args):
        """stub
        """
        print('called path.write_text with args', args)
    monkeypatch.setattr(testee.shutil, 'copyfile', mock_copy)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read)
    monkeypatch.setattr(testee.pathlib.Path, 'write_text', mock_write)
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.check_ignore(c, 'all')
    assert capsys.readouterr().out == (
            'called ScriptLib.__init__\n'
            "called path.read_text with args (PosixPath('x/.gitignore'),)\n"
            "called ScriptLib.get_all_names with args {'skip_inactive': True}\n"
            "`tom` will be added to .gitignore\n"
            "`dick` will be added to .gitignore\n"
            "called shutil.copyfile with args ('x/.gitignore', 'x/.gitignore~')\n"
            "called path.write_text with args (PosixPath('x/.gitignore'),"
            " 'harry\\nsally\\ntom\\ndick')\n"
            "entries are added\n")


def test_disable(monkeypatch, capsys):
    """unittest for scriptlib.disable
    """
    def mock_init(self):
        """stub
        """
        print('called ScriptLib.__init__')
        self.basepath = testee.pathlib.Path('x')
        self.data = testee.ConfigParser()
        self.data.read_dict({'section1': {'key1': 'value1', 'key2': 'value2'},
                             'section1.disabled': {'key3': 'value3'}})
    def mock_find(self, arg):
        """stub
        """
        print(f'called ScriptLib.find with arg `{arg}`')
        return 'section1.disabled'
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.disable(c, 'key1')
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       'called ScriptLib.find with arg `key1`\n'
                                       'called ScriptLib.update\n'
                                       'key1 disabled\n')
    monkeypatch.setattr(MockLib, '__init__', mock_init)
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.disable(c, 'key1')
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       'called ScriptLib.find with arg `key1`\n'
                                       'called ScriptLib.update\n'
                                       'key1 disabled\n')
    monkeypatch.setattr(MockLib, '__init__', mock_init)
    monkeypatch.setattr(MockLib, 'find', mock_find)
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.disable(c, 'key3')
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       'called ScriptLib.find with arg `key3`\n'
                                       'key3 is already disabled\n')


def test_enable(monkeypatch, capsys):
    """unittest for scriptlib.enable
    """
    def mock_init(self):
        """stub
        """
        print('called ScriptLib.__init__')
        self.basepath = testee.pathlib.Path('x')
        self.data = testee.ConfigParser()
        self.data.read_dict({'section1': {'key1': 'value1', 'key2': 'value2'},
                             'section1.disabled': {'key3': 'value3'}})
    def mock_find(self, arg):
        """stub
        """
        print(f'called ScriptLib.find with arg `{arg}`')
        return 'section1.disabled'
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.enable(c, 'key1')
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       'called ScriptLib.find with arg `key1`\n'
                                       'key1 is not disabled\n')
    monkeypatch.setattr(MockLib, '__init__', mock_init)
    monkeypatch.setattr(MockLib, 'find', mock_find)
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.enable(c, 'key3')
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       'called ScriptLib.find with arg `key3`\n'
                                       'called ScriptLib.update\n'
                                       'key3 enabled\n')


def test_list(monkeypatch, capsys):
    """unittest for scriptlib.list_
    """
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.list_(c)
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called ScriptLib.get_all_names with args"
                                       " {'skip_inactive': True, 'filter': ''}\n"
                                       "tom\n"
                                       "dick\n"
                                       "harry\n"
                                       "sally\n")
    testee.list_(c, 'yoink')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "unknown filter yoink\n")
    testee.list_(c, 'section1')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called ScriptLib.get_all_names with args"
                                       " {'skip_inactive': True, 'filter': 'section1'}\n"
                                       "tom\n"
                                       "dick\n"
                                       "harry\n"
                                       "sally\n")


def test_list_disabled(monkeypatch, capsys):
    """unittest for scriptlib.list_disabled
    """
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.list_disabled(c)
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       "called ScriptLib.get_all_names with args"
                                       " {'skip_active': True}\n"
                                       'tom\n'
                                       'dick\n'
                                       'harry\n'
                                       'sally\n')


def test_check_and_update(monkeypatch, capsys):
    """unittest for scriptlib.check_and_update
    """
    def mock_check(*args):
        """stub
        """
        print('called check_file with args', args)
        return 'old', 'new'
    def mock_check_2(*args):
        """stub
        """
        print('called check_file with args', args)
        return 'old', 'old'
    def mock_find(*args):
        """stub
        """
        print('called ScriptLib.find with args', args)
        return 'here'
    monkeypatch.setattr(testee, 'check_file', mock_check)
    lib = types.SimpleNamespace(find=mock_find, data={'here': {'this': 'old'}})
    origlib = types.SimpleNamespace(find=mock_find, data={'here': {'this': 'old'}})
    testee.check_and_update(lib, 'this')
    assert lib.data == {'here': {'this': 'new'}}
    assert capsys.readouterr().out == (f"called check_file with args ({origlib}, 'this')\n"
                                       f"called ScriptLib.find with args ('this',)\n")

    lib = types.SimpleNamespace(find=mock_find, data={'here': {'this': 'old'}})
    monkeypatch.setattr(testee, 'check_file', mock_check_2)
    testee.check_and_update(lib, 'this')
    assert lib.data == {'here': {'this': 'old'}}
    assert capsys.readouterr().out == f"called check_file with args ({origlib}, 'this')\n"


def test_check_file(monkeypatch, capsys):
    """unittest for scriptlib.check_file
    """
    def mock_readlink(*args):
        """stub
        """
        return f'called Path.readlink for {str(args[0])}'
    def mock_readfile(*args):
        """stub
        """
        return f'called Path.read_text for {str(args[0])}'
    def mock_read_2(self):
        """stub
        """
        print(f'called Path.read_text on {str(self)}')
        return '#! shebang line\n\ncontents'
    def mock_read_error(self):
        """stub
        """
        raise OSError("[Errno 22] Invalid argument: 'here'")
    def mock_find(*args):
        """stub
        """
        print('called ScriptLib.find with args', args)
        return ''
    monkeypatch.setattr(testee.pathlib.Path, 'readlink', mock_readlink)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_readfile)
    lib = types.SimpleNamespace(find=mock_find, data={'here': {'this': 'old'}})
    assert testee.check_file(lib, 'here') == (None, None)
    assert capsys.readouterr().out == "called ScriptLib.find with args ('here',)\n"

    lib = types.SimpleNamespace(find=lambda *x: 'symlinks', basepath=testee.pathlib.Path('bin'),
                                data={'symlinks': {'here': 'old'}})
    assert testee.check_file(lib, 'here') == ('old', 'called Path.readlink for bin/here')
    assert capsys.readouterr().out == ''

    monkeypatch.setattr(testee.pathlib.Path, 'readlink', mock_read_error)
    assert testee.check_file(lib, 'here') == ('old',
                                              'not a symlink:\ncalled Path.read_text for bin/here')
    assert capsys.readouterr().out == ''

    monkeypatch.setattr(testee.pathlib.Path, 'readlink', lambda *x: '../../../absolute_path')
    assert testee.check_file(lib, 'here') == ('old', '/absolute_path')
    assert capsys.readouterr().out == ''

    lib = types.SimpleNamespace(find=lambda *x: 'qqq', basepath=testee.pathlib.Path('bin'),
                                data={'qqq': {'here': 'old'}})
    assert testee.check_file(lib, 'here') == ('old', 'called Path.read_text for bin/here')
    assert capsys.readouterr().out == ""

    lib = types.SimpleNamespace(find=lambda *x: 'qqq', basepath=testee.pathlib.Path('bin'),
                                data={'qqq': {'here': 'old'}})
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read_2)
    assert testee.check_file(lib, 'here') == ('old', 'contents')
    assert capsys.readouterr().out == "called Path.read_text on bin/here\n"

    lib = types.SimpleNamespace(find=lambda *x: 'disabled', basepath=testee.pathlib.Path('bin'),
                                data={'qqq': {'here': 'old'}})
    assert testee.check_file(lib, 'here') == ('ignore', 'ignore')
    assert capsys.readouterr().out == ''


def test_check_readme(monkeypatch, capsys):
    """unittest for scriptlib.check_readme
    """
    def mock_build(path):
        """stub
        """
        print(f'called build_descdict with arg `{path}`')
        return {'dick': ['desc']}
    def mock_build_2(path):
        """stub
        """
        print(f'called build_descdict with arg `{path}`')
        return {'tom': ['desc'], 'dick': [], 'harry': '', 'sally': ''}
    monkeypatch.setattr(testee, 'build_descdict', mock_build)
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.check_readme(c)
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       'called build_descdict with arg `x/readme.rst`\n'
                                       'scriptlets not described in readme.rst:\n'
                                       'called ScriptLib.get_all_names with args {}\n'
                                       'tom\nharry\nsally\n')
    monkeypatch.setattr(testee, 'build_descdict', mock_build_2)
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.check_readme(c)
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       'called build_descdict with arg `x/readme.rst`\n'
                                       'scriptlets not described in readme.rst:\n'
                                       'called ScriptLib.get_all_names with args {}\n')


def test_build_destdict(tmp_path):
    """unittest for scriptlib.build_destdict
    """
    mock_readme = tmp_path / 'scriptlib' / 'readme'
    (tmp_path / 'scriptlib').mkdir()
    # leeg bestand
    mock_readme.touch()
    assert testee.build_descdict(mock_readme) == {}
    # geen scriptnamen
    mock_readme.write_text('tekst\nmeer tekst')
    assert testee.build_descdict(mock_readme) == {}
    # geen beschrijvingen
    mock_readme.write_text('tekst\n**a name**\n**another name**')
    assert testee.build_descdict(mock_readme) == {}
    # geen ingesprongen beschrijving
    mock_readme.write_text('tekst\n**a name**\nnot a description\n**another name**')
    assert testee.build_descdict(mock_readme) == {}
    # wel ingesprongen beschrijving, lege regel
    mock_readme.write_text('tekst\n**a name**\n  a description\n\n**another name**')
    assert testee.build_descdict(mock_readme) == {'a name': ['a description']}
    # twee scripts met beschrijving, multiline beschrijving
    mock_readme.write_text('tekst\n**a name**\n  a description\n  with extra text\n'
                           '**another name**\n  a description\n')
    assert testee.build_descdict(mock_readme) == {'a name': ['a description', 'with extra text'],
                                                  'another name': ['a description']}
    # dubbele naam
    mock_readme.write_text('tekst\n**name / name.py**\n  a description\n  with extra text\n')
    assert testee.build_descdict(mock_readme) == {'name': ['a description', 'with extra text'],
                                                  'name.py': ['a description', 'with extra text']}
    # alles na afsluitende tekst
    mock_readme.write_text('scripts that were replaced\n**a name**\n  a description\n'
                           '**another name**\n  a description\n')
    assert testee.build_descdict(mock_readme) == {}
    # entries voor en na afsluitende tekst
    mock_readme.write_text('**a name**\n  a description\nscripts that were replaced\n'
                           '**another name**\n  a description\n')
    assert testee.build_descdict(mock_readme) == {'a name': ['a description']}


def test_scriptlib_init(monkeypatch, capsys):
    """unittest for scriptlib.ScriptLib.__init__
    """
    def mock_read(*args):
        """stub
        """
        print('called ScriptLib.read')
    monkeypatch.setattr(testee, 'ConfigParser', MockParser)
    monkeypatch.setattr(testee.ScriptLib, 'read', mock_read)
    testobj = testee.ScriptLib()
    assert testobj.basepath == testee.pathlib.Path('~/bin').expanduser()
    assert testobj.libname == 'bin-scripts.conf'
    assert testobj.libpath == testobj.basepath / testobj.libname
    assert isinstance(testobj.data, testee.ConfigParser)
    assert capsys.readouterr().out == ('called ConfigParser.__init__\n'
                                       'called ScriptLib.read\n')


def test_scriptlib_read(monkeypatch, capsys, tmp_path):
    """unittest for scriptlib.ScriptLib.read
    """
    def mock_open(self, *args):
        """stub
        """
        print(f'called {str(self)}.open with args', args)
        return open(str(self), *args)
    def mock_read(file):
        """stub
        """
        print(f'called ConfigParser.read with arg {file.name}')
    monkeypatch.setattr(testee.pathlib.Path, 'open', mock_open)
    monkeypatch.setattr(testee.ScriptLib, '__init__', MockLib.__init__)
    testobj = testee.ScriptLib()
    assert capsys.readouterr().out == 'called ScriptLib.__init__\n'
    mock_lib = tmp_path / 'scriptlib'
    mock_lib.touch(exist_ok=True)
    testobj.libpath = mock_lib
    testobj.data = types.SimpleNamespace(read_file=mock_read)
    testobj.read()
    assert capsys.readouterr().out == (f'called {str(mock_lib)}.open with args ()\n'
                                       f'called ConfigParser.read with arg {str(mock_lib)}\n')


def test_scriptlib_update(monkeypatch, capsys, tmp_path):
    """unittest for scriptlib.ScriptLib,update
    """
    def mock_copy(*args):
        """stub
        """
        print('called shutil.copyfile with args', args)
    def mock_open(self, *args):
        """stub
        """
        print(f'called {str(self)}.open with args', args)
        return open(str(self), *args)
    def mock_write(file):
        """stub
        """
        print(f'called ConfigParser.write with arg {file.name}')
    monkeypatch.setattr(testee.pathlib.Path, 'open', mock_open)
    monkeypatch.setattr(testee.shutil, 'copyfile', mock_copy)
    monkeypatch.setattr(testee.ScriptLib, '__init__', MockLib.__init__)
    testobj = testee.ScriptLib()
    assert capsys.readouterr().out == 'called ScriptLib.__init__\n'
    mock_lib = tmp_path / 'scriptlib'
    mock_lib.touch(exist_ok=True)
    testobj.libpath = mock_lib
    testobj.data = types.SimpleNamespace(write=mock_write)
    testobj.update()
    assert capsys.readouterr().out == ('called shutil.copyfile with args'
                                       f""" ('{str(mock_lib)}', '{str(mock_lib) + "~"}')\n"""
                                       f"called {str(mock_lib)}.open with args ('w',)\n"
                                       f'called ConfigParser.write with arg {str(mock_lib)}\n')


def test_scriptlib_find(monkeypatch, capsys):
    """unittest for scriptlib.ScriptLib.find
    """
    monkeypatch.setattr(testee.ScriptLib, '__init__', MockLib.__init__)
    testobj = testee.ScriptLib()
    assert capsys.readouterr().out == 'called ScriptLib.__init__\n'
    assert testobj.find('key2') == 'section1'
    assert not testobj.find('key4')


def test_scriptlib_get_all_names(monkeypatch, capsys):
    """unittest for scriptlib.ScriptLib.get_all_names
    """
    monkeypatch.setattr(testee.ScriptLib, '__init__', MockLib.__init__)
    testobj = testee.ScriptLib()
    assert capsys.readouterr().out == 'called ScriptLib.__init__\n'
    testobj.data.clear()
    testobj.data.read_dict({'section1': {'key1': 'value1'},
                            'section1.disabled': {'key3': 'value3'},
                            'section2': {'key2': 'value2'},
                            'section2.disabled': {'key4': 'value4'}})
    assert testobj.get_all_names() == ['key1', 'key3', 'key2', 'key4']
    assert testobj.get_all_names(filter='section1') == ['key1']
    assert testobj.get_all_names(skip_inactive=True) == ['key1', 'key2']
    assert testobj.get_all_names(skip_active=True) == ['key3', 'key4']


def test_scriptlib_add_link(monkeypatch, capsys):
    """unittest for scriptlib.ScriptLib.add_link
    """
    def mock_islink(self):
        """stub
        """
        print(f'called path.is_link on {str(self)}')
        return True
    def mock_readlink(self):
        """stub
        """
        print(f'called path.readlink on {str(self)}')
        return 'target'
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', mock_islink)
    monkeypatch.setattr(testee.pathlib.Path, 'readlink', mock_readlink)
    monkeypatch.setattr(testee.ScriptLib, '__init__', MockLib.__init__)
    testobj = testee.ScriptLib()
    assert capsys.readouterr().out == 'called ScriptLib.__init__\n'

    testobj.add_link('test', 'symlinks')
    assert testobj.data.sections() == ['section1', 'section2', 'symlinks']
    assert list(testobj.data['symlinks']) == ['test']
    assert testobj.data['symlinks']['test'] == 'target'
    assert capsys.readouterr().out == ('called path.is_link on x/test\n'
                                       'called path.readlink on x/test\n')

    assert testobj.add_link('test2', 'symlinks') == ''
    assert list(testobj.data['symlinks']) == ['test', 'test2']
    assert testobj.data['symlinks']['test2'] == 'target'
    assert capsys.readouterr().out == ('called path.is_link on x/test2\n'
                                       'called path.readlink on x/test2\n')

    assert testobj.add_link('test', 'symlinks2') == 'wrong section'
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', lambda *x: False)

    assert testobj.add_link('test', 'symlinks') == 'not a valid symlink'


def test_scriptlib_add_script(monkeypatch, capsys):
    """unittest for scriptlib.ScriptLib.add_script
    """
    def mock_isfile(self):
        """stub
        """
        print(f'called path.is_file on {str(self)}')
        return True
    def mock_islink(self):
        """stub
        """
        print(f'called path.is_link on {str(self)}')
        return False
    def mock_read_text(self):
        """stub
        """
        print(f'called path.read_text on {str(self)}')
        return 'contents'
    def mock_read_2(self):
        """stub
        """
        print(f'called path.read_text on {str(self)}')
        return '#! shebang line\n\ncontents'
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', mock_islink)
    monkeypatch.setattr(testee.pathlib.Path, 'is_file', mock_isfile)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read_text)
    monkeypatch.setattr(testee.ScriptLib, '__init__', MockLib.__init__)
    testobj = testee.ScriptLib()
    assert capsys.readouterr().out == 'called ScriptLib.__init__\n'
    testobj.add_script('test', 'scripts')
    assert testobj.data.sections() == ['section1', 'section2', 'scripts']
    assert list(testobj.data['scripts']) == ['test']
    assert testobj.data['scripts']['test'] == 'contents'
    assert capsys.readouterr().out == ('called path.is_file on x/test\n'
                                       'called path.is_link on x/test\n'
                                       'called path.read_text on x/test\n')
    testobj.add_script('test2', 'scripts')
    assert testobj.data['scripts']['test2'] == 'contents'
    assert capsys.readouterr().out == ('called path.is_file on x/test2\n'
                                       'called path.is_link on x/test2\n'
                                       'called path.read_text on x/test2\n')

    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read_2)
    testobj = testee.ScriptLib()
    assert capsys.readouterr().out == 'called ScriptLib.__init__\n'
    testobj.add_script('test', 'scripts-sh')
    assert testobj.data.sections() == ['section1', 'section2', 'scripts-sh']
    assert list(testobj.data['scripts-sh']) == ['test']
    assert testobj.data['scripts-sh']['test'] == 'contents'
    assert capsys.readouterr().out == ('called path.is_file on x/test\n'
                                       'called path.is_link on x/test\n'
                                       'called path.read_text on x/test\n')
    assert testobj.add_script('test', 'scripts2') == 'unknown section name: scripts2'
    monkeypatch.setattr(testee.pathlib.Path, 'is_file', lambda *x: False)
    assert testobj.add_script('test', 'scripts') == 'not a valid file'
    monkeypatch.setattr(testee.pathlib.Path, 'is_file', lambda *x: True)
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', lambda *x: True)
    assert testobj.add_script('test', 'scripts') == 'not a valid file'
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', lambda *x: '')
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', lambda *x: False)
    assert testobj.add_script('test', 'scripts') == 'file is empty'
