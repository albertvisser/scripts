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
    def write(self, *args):
        pass
    def get_all_names(self):
        pass
    def add_link(self, *args):
        print('called ScriptLib.add_link with args', args)
    def add_script(self, *args):
        print('called ScriptLib.add_script with args', args)

def test_add(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()
    testee.add(c, 'test', 'symlinks')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called ScriptLib.add_link with args ('test', 'symlinks')\n"
                                       "test successfully added\n")
    testee.add(c, 'test', 'scripts')
    assert capsys.readouterr().out == ("called ScriptLib.__init__\n"
                                       "called ScriptLib.add_script with args ('test', 'scripts')\n"
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



def _test_check_all(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()

def _test_update(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()

def _test_update_all(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()

def _test_ignore(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()

def _test_ignore_all(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'ScriptLib', MockLib)
    c = MockContext()

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
                                       f"called ScriptLib.find with args ({origlib}, 'this')\n")

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
    def mock_find(*args):
        print('called ScriptLib.find with args', args)
        return ''
    monkeypatch.setattr(testee.pathlib.Path, 'readlink', mock_readlink)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_readfile)
    lib = types.SimpleNamespace(find=mock_find, data={'here': {'this': 'old'}})
    assert testee.check_file(lib, 'here') == (None, None)
    assert capsys.readouterr().out == f"called ScriptLib.find with args ({lib}, 'here')\n"

    lib = types.SimpleNamespace(find=lambda *x: 'symlinks', basepath=testee.pathlib.Path('bin'),
                                data={'symlinks': {'here': 'old'}})
    assert testee.check_file(lib, 'here') == ('old', 'called Path.readlink for bin/here')
    assert capsys.readouterr().out == ''

    lib = types.SimpleNamespace(find=lambda *x: 'qqq', basepath=testee.pathlib.Path('bin'),
                                data={'qqq': {'here': 'old'}})
    assert testee.check_file(lib, 'here') == ('old', 'called Path.read_text for bin/here')
    assert capsys.readouterr().out == ""


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
    assert testobj.get_all_names() == ['key1', 'key2', 'key3']

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
    assert testobj.add_script('test', 'scripts2') == 'wrong section'
    monkeypatch.setattr(testee.pathlib.Path, 'is_file', lambda *x: False)
    assert testobj.add_script('test', 'scripts') == 'not a valid file'
    monkeypatch.setattr(testee.pathlib.Path, 'is_file', lambda *x: True)
    monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', lambda *x: True)
    assert testobj.add_script('test', 'scripts') == 'not a valid file'

