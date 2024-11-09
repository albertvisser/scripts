"""unittests for ./tasks.py
"""
import datetime
import pytest
import types
from invoke import MockContext
import tasks as testee
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
    monkeypatch.setattr(testee, 'GSCITELOC', str(tmp_path / 'scite{}_test'))
    fname = testee.GSCITELOC.format('x')

    c = MockContext()
    testee.install_scite(c, 'x')
    assert capsys.readouterr().out == f'{fname} does not exist\n'

    with open(fname, 'w') as f:
        f.write('')
    monkeypatch.setattr(MockContext, 'run', mock_run_1)
    c = MockContext()
    testee.install_scite(c, 'x')
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
    testee.install_scite(c, 'x')
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
    monkeypatch.setattr(testee, 'SCITELOC', str(tmp_path / 'scite{}_test'))
    fname = testee.SCITELOC.format('x')
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: False)
    c = MockContext()
    testee.build_scite(c, 'x')
    assert capsys.readouterr().out == f'{fname} does not exist\n'
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: True)

    counter = 0
    monkeypatch.setattr(MockContext, 'run', mock_run_1)
    c = MockContext()
    testee.build_scite(c, 'x')
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
    testee.build_scite(c, 'x')
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
    testee.build_scite(c, 'x')
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
    testee.build_scite(c, 'x')
    assert capsys.readouterr().out == (f'tar -zxf {fname} in /tmp\n'
                                       'make in /tmp/scintilla/gtk\n'
                                       'make in /tmp/scite/gtk\n'
                                       'sudo make install in /tmp/scite/gtk\n'
                                       'ready, see /tmp/scite_build.log\n')
    with open('/tmp/scite_build.log') as f:
        data = f.read()
    assert data == 'results from call 2\nresults from call 3\nresults from call 4\n'


def test_arcstuff(monkeypatch, capsys, tmp_path):
    """unittest for tasks.arcstuff
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    monkeypatch.setattr(testee.datetime, 'datetime', MockDatetime)
    monkeypatch.setattr(testee, 'HERE', str(tmp_path))
    testee.arcstuff(c, 'all')
    assert capsys.readouterr().out == ""
    with pytest.raises(IndexError) as exc:
        testee.arcstuff(c, '')
    assert str(exc.value) == 'string index out of range'
    with pytest.raises(ValueError) as exc:
        testee.arcstuff(c, 'test,stuff')
    assert str(exc.value) == 'abort: no config file for stuff (arcstuff_stuff.conf does not exist)'
    (tmp_path / 'arcstuff.conf').write_text('[hello\n\nhello\nfiles\n')
    (tmp_path / 'arcstuff_test.conf').write_text('#hello\n[hello]\nhello\nfiles\n')
    (tmp_path / 'test').touch()
    (tmp_path / 'test.conf').touch()
    testee.arcstuff(c, 'all')
    assert capsys.readouterr().out == (
         'tar -czvf /home/albert/arcstuff/all_20200101000000.tar.gz hello files\n'
         'tar -czvf /home/albert/arcstuff/test_20200101000000.tar.gz hello/hello hello/files\n')


class MockDatetime:
    """stub for datetime.DateTime
    """
    @classmethod
    def today(cls):
        """stub
        """
        return FIXDATE
