"""unittests for ./tasks.py
"""
import os
import shutil
import datetime
import pytest
import types
from invoke import MockContext
import tasks
FIXDATE = datetime.datetime(2020, 1, 1)


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def run_in_dir(self, *args, **kwargs):
    """stub for invoke.Context.run under "with invoke.Contect.cd"
    """
    print(*args, 'in', self.cwd)


def test_install_scite(monkeypatch, capsys, tmp_path):
    """unittest for tasks.install_scite
    """
    def mock_run_1(c, *args):
        """stub for invoke.Context.run succeeding
        """
        print(*args)
        return types.SimpleNamespace(failed=True)
    def mock_run_2(c, *args):
        """stub for invoke.Context.run failing
        """
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
    assert capsys.readouterr().out == (f'tar -zxf {fname}\ntar -xf {fname}\n'
                                       'sudo cp gscite/SciTE /usr/bin\n'
                                       'sudo cp gscite/*.properties /etc/scite\n'
                                       'sudo cp gscite/*.html /usr/share/scite\n'
                                       'sudo cp gscite/*.png /usr/share/scite\n'
                                       'sudo cp gscite/*.jpg /usr/share/scite\nrm gscite -r\n')
    with open(fname, 'w') as f:
        f.write('')
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    tasks.install_scite(c, 'x')
    assert capsys.readouterr().out == (f'tar -zxf {fname}\nsudo cp gscite/SciTE /usr/bin\n'
                                       'sudo cp gscite/*.properties /etc/scite\n'
                                       'sudo cp gscite/*.html /usr/share/scite\n'
                                       'sudo cp gscite/*.png /usr/share/scite\n'
                                       'sudo cp gscite/*.jpg /usr/share/scite\nrm gscite -r\n')


def test_build_scite(monkeypatch, capsys, tmp_path):
    """unittest for tasks.build_scite
    """
    def mock_run_1(c, *args):
        """stub
        """
        nonlocal counter
        print(*args, 'in', c.cwd)
        counter += 1
        return types.SimpleNamespace(failed=True, stdout=f'results from call {counter}',
                                     stderr=f'errors on call {counter}')
    def mock_run_2(c, *args):
        """stub
        """
        nonlocal counter
        print(*args, 'in', c.cwd)
        counter += 1
        if counter > 2:
            return types.SimpleNamespace(failed=True, stdout=f'results from call {counter}',
                                         stderr=f'errors on call {counter}')
        return types.SimpleNamespace(failed=False, stdout=f'results from call {counter}')
    def mock_run_3(c, *args):
        """stub
        """
        nonlocal counter
        print(*args, 'in', c.cwd)
        counter += 1
        if counter > 3:
            return types.SimpleNamespace(failed=True, stdout=f'results from call {counter}',
                                         stderr=f'errors on call {counter}')
        return types.SimpleNamespace(failed=False, stdout=f'results from call {counter}')
    def mock_run_4(c, *args):
        """stub
        """
        nonlocal counter
        print(*args, 'in', c.cwd)
        counter += 1
        return types.SimpleNamespace(failed=False, stdout=f'results from call {counter}')
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
    """unittest for tasks.arcstuff
    """
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


class MockDatetime:
    """stub for datetime.DateTime
    """
    @classmethod
    def today(cls):
        """stub
        """
        return FIXDATE
