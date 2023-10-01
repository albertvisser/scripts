import types
import copy
import contextlib
import pytest
import scriptlib as testee
from invoke import MockContext

class MockParser:
    def __init__(self):
        print('called ConfigParser.__init__')

class MockLib:
    def __init__(self):
        print('called ScriptLib.__init__')
        self.basepath = testee.pathlib.Path('x')
        self.data = testee.ConfigParser()
        self.data.read_dict({'section1': {'key1': 'value1', 'key2': 'value2'},
                             'section2': {'key3': 'value3'}})
    def read_file(self, *args):
        pass
    def update(self, *args):
        print('called ScriptLib.update')
    def clear(self):
        for name in self.data.sections():
            self.data.remove_section(name)
    def find(self, name):
        print(f'called ScriptLib.find with arg `{name}`')
        if name in ('key1', 'key2'):
            return 'section1'
        elif name == 'key3':
            return 'section2'
        else:
            return 'section0'
    def get_all_names(self, **kwargs):
        print('called ScriptLib.get_all_names with args', kwargs)
        return 'tom', 'dick', 'harry', 'sally'
    def add_link(self, *args):
        print('called ScriptLib.add_link with args', args)
    def add_script(self, *args):
        print('called ScriptLib.add_script with args', args)
    def list_contents(self):
        # voor de commando tests heeft dit niet veel zin omdat het object niet van buiten de functie
        # gelezen kan worden
        contents = []
        for name1 in self.data.sections():
            for name2 in self.data.options(nname1):
                contents.append(i(str(name), str(name2), self.data.get()))


def test_add(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.add(c, 'test', 'symlinks')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called ScriptLib.add_link with args ('test', 'symlinks')\n"
                                       "called ScriptLib.update\n"
                                       "test successfully added\n")
    testee.add(c, 'test', 'scripts')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called ScriptLib.add_script with args ('test', 'scripts')\n"
                                       "called ScriptLib.update\n"
                                       "test successfully added\n")
    monkeypatch.setattr(MockLib, 'add_link', lambda *x: 'error adding link')
    monkeypatch.setattr(MockLib, 'add_script', lambda *x: 'error adding script')
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    testee.add(c, 'test', 'symlinks')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "error adding link\n")
    testee.add(c, 'test', 'scripts')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "error adding script\n")

def test_check(monkeypatch, capsys):
    def mock_check(lib, name):
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
    counter = 0
    def mock_check(lib, name):
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
    def mock_check(lib, name):
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
    counter = 0
    def mock_check(lib, name):
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

def test_ignore(monkeypatch, capsys):
    def mock_read(*args):
        print('called path.read_text with args', args)
        return 'harry\nsally'
    def mock_copy(*args):
        print('called shutil.copyfile with args', args)
    def mock_write(*args):
        print('called path.write_text with args', args)
    monkeypatch.setattr(testee.shutil, 'copyfile', mock_copy)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read)
    monkeypatch.setattr(testee.pathlib.Path, 'write_text', mock_write)
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.ignore(c, 'test')
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       "called path.read_text with args"
                                       " (PosixPath('x/.gitignore'),)\n"
                                       'called ScriptLib.get_all_names with args {}\n'
                                       'not in library\n')
    testee.ignore(c, 'dick')
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       "called path.read_text with args"
                                       " (PosixPath('x/.gitignore'),)\n"
                                       'called ScriptLib.get_all_names with args {}\n'
                                       'called shutil.copyfile with args'
                                       " ('x/.gitignore', 'x/.gitignore~')\n"
                                       "called path.write_text with args"
                                       " (PosixPath('x/.gitignore'), 'harry\\nsally\\ndick')\n")
    testee.ignore(c, 'harry')
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       "called path.read_text with args"
                                       " (PosixPath('x/.gitignore'),)\n"
                                       'called ScriptLib.get_all_names with args {}\n'
                                       'already present in .gitignore\n')

def test_ignore_all(monkeypatch, capsys):
    def mock_read(*args):
        print('called path.read_text with args', args)
        return 'harry\nsally'
    def mock_copy(*args):
        print('called shutil.copyfile with args', args)
    def mock_write(*args):
        print('called path.write_text with args', args)
    monkeypatch.setattr(testee.shutil, 'copyfile', mock_copy)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read)
    monkeypatch.setattr(testee.pathlib.Path, 'write_text', mock_write)
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.ignore(c, 'all')
    assert capsys.readouterr().out == ('called ScriptLib.__init__\n'
                                       "called path.read_text with args"
                                       " (PosixPath('x/.gitignore'),)\n"
                                       "called ScriptLib.get_all_names with args"
                                       " {'skip_inactive': True}\n"
                                       'called shutil.copyfile with args'
                                       " ('x/.gitignore', 'x/.gitignore~')\n"
                                       "called path.write_text with args"
                                       " (PosixPath('x/.gitignore'),"
                                       " 'harry\\nsally\\ntom\\ndick')\n")

def test_disable(monkeypatch, capsys):
    def mock_init(self):
        print('called ScriptLib.__init__')
        self.basepath = testee.pathlib.Path('x')
        self.data = testee.ConfigParser()
        self.data.read_dict({'section1': {'key1': 'value1', 'key2': 'value2'},
                             'section1.disabled': {'key3': 'value3'}})
    def mock_find(self, arg):
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
    def mock_init(self):
        print('called ScriptLib.__init__')
        self.basepath = testee.pathlib.Path('x')
        self.data = testee.ConfigParser()
        self.data.read_dict({'section1': {'key1': 'value1', 'key2': 'value2'},
                             'section1.disabled': {'key3': 'value3'}})
    def mock_find(self, arg):
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

def test_list_disabled(monkeypatch, capsys):
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
    def mock_check(*args):
        print('called check_file with args', args)
        return 'old', 'new'
    def mock_check_2(*args):
        print('called check_file with args', args)
        return 'old', 'old'
    def mock_find(*args):
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
    def mock_readlink(*args):
        return f'called Path.readlink for {str(args[0])}'
    def mock_readfile(*args):
        return f'called Path.read_text for {str(args[0])}'
    def mock_read_2(self):
        print(f'called Path.read_text on {str(self)}')
        return '#! shebang line\n\ncontents'
    def mock_read_error(self):
        raise OSError("[Errno 22] Invalid argument: 'here'")
    def mock_find(*args):
        print('called ScriptLib.find with args', args)
        return ''
    monkeypatch.setattr(testee.pathlib.Path, 'readlink', mock_readlink)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_readfile)
    lib = types.SimpleNamespace(find=mock_find, data={'here': {'this': 'old'}})
    assert testee.check_file(lib, 'here') == (None, None)
    assert capsys.readouterr().out == f"called ScriptLib.find with args ('here',)\n"

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


def test_scriptlib_init(monkeypatch, capsys):
    def mock_read(*args):
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
    def mock_open(self, *args):
        print(f'called {str(self)}.open with args', args)
        return open(str(self), *args)
    def mock_read(file):
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
    def mock_copy(*args):
        print('called shutil.copyfile with args', args)
    def mock_open(self, *args):
        print(f'called {str(self)}.open with args', args)
        return open(str(self), *args)
    def mock_write(file):
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
    monkeypatch.setattr(testee.ScriptLib, '__init__', MockLib.__init__)
    testobj = testee.ScriptLib()
    assert capsys.readouterr().out == 'called ScriptLib.__init__\n'
    assert testobj.find('key2') == 'section1'
    assert not testobj.find('key4')

def test_scriptlib_get_all_names(monkeypatch, capsys):
    monkeypatch.setattr(testee.ScriptLib, '__init__', MockLib.__init__)
    testobj = testee.ScriptLib()
    assert capsys.readouterr().out == 'called ScriptLib.__init__\n'
    testobj.data.clear()
    testobj.data.read_dict({'section1': {'key1': 'value1'},
                            'section1.disabled': {'key3': 'value3'},
                            'section2': {'key2': 'value2'},
                            'section2.disabled': {'key4': 'value4'}})
    assert testobj.get_all_names() == ['key1', 'key3', 'key2', 'key4']
    assert testobj.get_all_names(skip_inactive=True) == ['key1', 'key2']
    assert testobj.get_all_names(skip_active=True) == ['key3', 'key4']

def test_scriptlib_add_link(monkeypatch, capsys, tmp_path):
    def mock_islink(self):
        print(f'called path.is_link on {str(self)}')
        return True
    def mock_readlink(self):
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
    assert testobj.add_link('test', 'symlinks2') == 'wrong section'
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', lambda *x: False)
    assert testobj.add_link('test', 'symlinks') == 'not a valid symlink'

def test_scriptlib_add_script(monkeypatch, capsys, tmp_path):
    def mock_isfile(self):
        print(f'called path.is_file on {str(self)}')
        return True
    def mock_islink(self):
        print(f'called path.is_link on {str(self)}')
        return False
    def mock_read_text(self):
        print(f'called path.read_text on {str(self)}')
        return 'contents'
    def mock_read_2(self):
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
    assert testobj.add_script('test', 'scripts2') == 'wrong section'
    monkeypatch.setattr(testee.pathlib.Path, 'is_file', lambda *x: False)
    assert testobj.add_script('test', 'scripts') == 'not a valid file'
    monkeypatch.setattr(testee.pathlib.Path, 'is_file', lambda *x: True)
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', lambda *x: True)
    assert testobj.add_script('test', 'scripts') == 'not a valid file'
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', lambda *x: '')
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', lambda *x: False)
    assert testobj.add_script('test', 'scripts') == 'file is empty'
