import os
import shutil
import datetime
import pytest
import types
from invoke import MockContext
import tasks
FIXDATE = datetime.datetime(2020,1,1)


def mock_run(self, *args):
    print(*args)


def run_in_dir(self, *args, **kwargs):
    print(*args, 'in', self.cwd)


def test_install_scite(monkeypatch, capsys, tmp_path):
    def mock_run_1(c, *args):
        print(*args)
        return types.SimpleNamespace(failed=True)
    def mock_run_2(c, *args):
        print(*args)
        return types.SimpleNamespace(failed=False)
    monkeypatch.setattr(tasks, 'GSCITELOC', str(tmp_path / 'scite{}_test'))
    fname = tasks.GSCITELOC.format('x')

    c = MockContext()
    tasks.install_scite(c, 'x')
    assert capsys.readouterr().out == f'{fname} does not exist\n'

    with open(fname, 'w') as f:
        f.write('')
    monkeypatch.setattr(MockContext, 'run', mock_run_1)
    c = MockContext()
    tasks.install_scite(c, 'x')
    assert capsys.readouterr().out == ('tar -zxf {0}\ntar -xf {0}\nsudo cp gscite/SciTE /usr/bin\n'
                                       'sudo cp gscite/*.properties /etc/scite\n'
                                       'sudo cp gscite/*.html /usr/share/scite\n'
                                       'sudo cp gscite/*.png /usr/share/scite\n'
                                       'sudo cp gscite/*.jpg /usr/share/scite\nrm gscite -r\n').format(
                                               fname)

    with open(fname, 'w') as f:
        f.write('')
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    tasks.install_scite(c, 'x')
    assert capsys.readouterr().out == ('tar -zxf {}\nsudo cp gscite/SciTE /usr/bin\n'
                                       'sudo cp gscite/*.properties /etc/scite\n'
                                       'sudo cp gscite/*.html /usr/share/scite\n'
                                       'sudo cp gscite/*.png /usr/share/scite\n'
                                       'sudo cp gscite/*.jpg /usr/share/scite\nrm gscite -r\n').format(
                                               fname)


def test_build_scite(monkeypatch, capsys, tmp_path):
    def mock_run_1(c, *args):
        nonlocal counter
        print(*args, 'in', c.cwd)
        counter += 1
        return types.SimpleNamespace(failed=True, stdout='results from call {}'.format(counter),
                                     stderr='errors on call {}'.format(counter))
    def mock_run_2(c, *args):
        nonlocal counter
        print(*args, 'in', c.cwd)
        counter += 1
        if counter > 2:
            return types.SimpleNamespace(failed=True, stdout='results from call {}'.format(counter),
                                         stderr='errors on call {}'.format(counter))
        return types.SimpleNamespace(failed=False, stdout='results from call {}'.format(counter))
    def mock_run_3(c, *args):
        nonlocal counter
        print(*args, 'in', c.cwd)
        counter += 1
        if counter > 3:
            return types.SimpleNamespace(failed=True, stdout='results from call {}'.format(counter),
                                         stderr='errors on call {}'.format(counter))
        return types.SimpleNamespace(failed=False, stdout='results from call {}'.format(counter))
    def mock_run_4(c, *args):
        nonlocal counter
        print(*args, 'in', c.cwd)
        counter += 1
        return types.SimpleNamespace(failed=False, stdout='results from call {}'.format(counter))
    monkeypatch.setattr(tasks, 'SCITELOC', str(tmp_path / 'scite{}_test'))
    fname = tasks.SCITELOC.format('x')
    monkeypatch.setattr(tasks.os.path, 'exists', lambda x: False)
    c = MockContext()
    tasks.build_scite(c, 'x')
    assert capsys.readouterr().out == f'{fname} does not exist\n'
    monkeypatch.setattr(tasks.os.path, 'exists', lambda x: True)

    counter = 0
    monkeypatch.setattr(MockContext, 'run', mock_run_1)
    c = MockContext()
    tasks.build_scite(c, 'x')
    assert capsys.readouterr().out == (f'tar -zxf {fname} in /tmp\n'
                                       f'tar -xf {fname} in /tmp\n'
                                       'make in /tmp/scintilla/gtk\n'
                                       'make scintilla failed, see /tmp/scite_build.log\n')
    with open('/tmp/scite_build.log') as f:
        data = f.read()
    assert data == "results from call 3\nerrors on call 3\n"

    counter = 0
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    tasks.build_scite(c, 'x')
    assert capsys.readouterr().out == (f'tar -zxf {fname} in /tmp\n'
                                       'make in /tmp/scintilla/gtk\n'
                                       'make in /tmp/scite/gtk\n'
                                       'make scite failed, see /tmp/scite_build.log\n')
    with open('/tmp/scite_build.log') as f:
        data = f.read()
    assert data == "results from call 2\nresults from call 3\nerrors on call 3\n"

    counter = 0
    monkeypatch.setattr(MockContext, 'run', mock_run_3)
    c = MockContext()
    tasks.build_scite(c, 'x')
    assert capsys.readouterr().out == (f'tar -zxf {fname} in /tmp\n'
                                       'make in /tmp/scintilla/gtk\n'
                                       'make in /tmp/scite/gtk\n'
                                       'sudo make install in /tmp/scite/gtk\n'
                                       'make install failed, see /tmp/scite_build.log\n')
    with open('/tmp/scite_build.log') as f:
        data = f.read()
    assert data == ("results from call 2\nresults from call 3\n"
                    "results from call 4\nerrors on call 4\n")

    counter = 0
    monkeypatch.setattr(MockContext, 'run', mock_run_4)
    c = MockContext()
    tasks.build_scite(c, 'x')
    assert capsys.readouterr().out == (f'tar -zxf {fname} in /tmp\n'
                                       'make in /tmp/scintilla/gtk\n'
                                       'make in /tmp/scite/gtk\n'
                                       'sudo make install in /tmp/scite/gtk\n'
                                       'ready, see /tmp/scite_build.log\n')
    with open('/tmp/scite_build.log') as f:
        data = f.read()
    assert data == 'results from call 2\nresults from call 3\nresults from call 4\n'


def test_arcstuff(monkeypatch, capsys):
    if os.path.exists('arcstuff.conf'):
        shutil.copyfile('arcstuff.conf', '/tmp/arcstuff.conf')
    with open('arcstuff.conf', 'w') as f:
        print('[hello', file=f)
        print('', file=f)
        print('hello', file=f)
        print('files', file=f)
    if os.path.exists('arcstuff_test.conf'):
        shutil.copyfile('arcstuff_test.conf', '/tmp/arcstuff_test.conf')
    with open('arcstuff_test.conf', 'w') as f:
        print('#hello', file=f)
        print('[hello]', file=f)
        print('hello', file=f)
        print('files', file=f)

    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    monkeypatch.setattr(tasks.os, 'listdir', lambda x: ['test', 'test.conf', 'arcstuff.conf',
                                                        'arcstuff_test.conf'])
    monkeypatch.setattr(tasks.datetime, 'datetime', MockDatetime)
    with pytest.raises(ValueError) as exc:
        tasks.arcstuff(c, 'test,stuff')
    assert str(exc.value) == 'abort: no config file for stuff (arcstuff_stuff.conf does not exist)'
    tasks.arcstuff(c, 'all')
    assert capsys.readouterr().out == (
         'tar -czvf /home/albert/arcstuff/all_20200101000000.tar.gz hello files\n'
         'tar -czvf /home/albert/arcstuff/test_20200101000000.tar.gz hello/hello hello/files\n')
    if os.path.exists('/tmp/arcstuff.conf'):
        shutil.copyfile('/tmp/arcstuff.conf', 'arcstuff.conf')
    else:
        os.remove('arcstuff.conf')
    if os.path.exists('/tmp/arcstuff_test.conf'):
        shutil.copyfile('/tmp/arcstuff_test.conf', 'arcstuff_test.conf')
    else:
        os.remove('arcstuff_test.conf')


def test_chmodrecursive(monkeypatch, capsys):
    counter = 0
    def mock_listdir(*args):
        nonlocal counter
        counter += 1
        if counter > 1:
            print('entering recursive call')
            return []
        return ['file', 'name', '__pycache__', '.hg', 'link', 'dir', 'map']
    def mock_chmod(*args):
        if os.path.basename(args[0]) in ('file', 'dir'):
            print('ignoring PermissionError for', args[0])
            raise PermissionError
        print('changing file permissions for', args[0])
    monkeypatch.setattr(tasks.os, 'getcwd', lambda: 'current_dir')
    monkeypatch.setattr(tasks.os, 'listdir', mock_listdir)
    monkeypatch.setattr(tasks.os.path, 'isfile',
                        lambda x: True if x.endswith('file') or x.endswith('name') else False)
    monkeypatch.setattr(tasks.os.path, 'islink', lambda x: True if x.endswith('link') else False)
    monkeypatch.setattr(tasks.os.path, 'isdir',
                        lambda x: True if x.endswith('dir') or x.endswith('map') else False)
    monkeypatch.setattr(tasks.os, 'chmod', mock_chmod)
    c = MockContext()
    tasks.chmodrecursive(c)
    assert capsys.readouterr().out == ('ignoring PermissionError for current_dir/file\n'
                                       'changing file permissions for current_dir/name\n'
                                       'ignoring PermissionError for current_dir/dir\n'
                                       'changing file permissions for current_dir/map\n'
                                       'entering recursive call\n')


class MockDatetime:
    @classmethod
    def today(cls):
        return FIXDATE
