import os
import pytest
import types
from invoke import MockContext
import tasks


def mock_run(self, *args):
    print(*args)


def run_in_dir(self, *args, **kwargs):
    print(*args, 'in', self.cwd)


def _test_listbin(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()


def test_install_scite(monkeypatch, capsys):
    def mock_run_1(c, *args):
        print(*args)
        return types.SimpleNamespace(failed=True)
    def mock_run_2(c, *args):
        print(*args)
        return types.SimpleNamespace(failed=False)
    monkeypatch.setattr(tasks, 'GSCITELOC', '/tmp/scite{}_test')
    fname = tasks.GSCITELOC.format('x')

    try:
        os.remove(fname)
    except FileNotFoundError:
        pass
    c = MockContext()
    tasks.install_scite(c, 'x')
    assert capsys.readouterr().out == '/tmp/scitex_test does not exist\n'

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


def test_build_scite(monkeypatch, capsys):
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
    monkeypatch.setattr(tasks, 'SCITELOC', '/tmp/scite{}_test')
    monkeypatch.setattr(tasks.os.path, 'exists', lambda x: False)
    c = MockContext()
    tasks.build_scite(c, 'x')
    assert capsys.readouterr().out == '/tmp/scitex_test does not exist\n'
    monkeypatch.setattr(tasks.os.path, 'exists', lambda x: True)

    counter = 0
    monkeypatch.setattr(MockContext, 'run', mock_run_1)
    c = MockContext()
    tasks.build_scite(c, 'x')
    assert capsys.readouterr().out == ('tar -zxf /tmp/scitex_test in /tmp\n'
                                       'tar -xf /tmp/scitex_test in /tmp\n'
                                       'make in /tmp/scintilla/gtk\n'
                                       'make scintilla failed, see /tmp/scite_build.log\n')
    with open('/tmp/scite_build.log') as f:
        data = f.read()
    assert data == "results from call 3\nerrors on call 3\n"

    counter = 0
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    tasks.build_scite(c, 'x')
    assert capsys.readouterr().out == ('tar -zxf /tmp/scitex_test in /tmp\n'
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
    assert capsys.readouterr().out == ('tar -zxf /tmp/scitex_test in /tmp\n'
                                       'make in /tmp/scintilla/gtk\n'
                                       'make in /tmp/scite/gtk\n'
                                       'sudo make install in /tmp/scite/gtk\n'
                                       'make install failed, see /tmp/scite_build.log\n')
    with open('/tmp/scite_build.log') as f:
        data = f.read()
    assert data == "results from call 2\nresults from call 3\nresults from call 4\nerrors on call 4\n"

    counter = 0
    monkeypatch.setattr(MockContext, 'run', mock_run_4)
    c = MockContext()
    tasks.build_scite(c, 'x')
    assert capsys.readouterr().out == ('tar -zxf /tmp/scitex_test in /tmp\n'
                                       'make in /tmp/scintilla/gtk\n'
                                       'make in /tmp/scite/gtk\n'
                                       'sudo make install in /tmp/scite/gtk\n'
                                       'ready, see /tmp/scite_build.log\n')
    with open('/tmp/scite_build.log') as f:
        data = f.read()
    assert data == 'results from call 2\nresults from call 3\nresults from call 4\n'


def _test_arcstuff(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()


def _test_chmodrecursive(monkeypatch, capsys):
    def mock_recursive(*args):
        print('entering recursive call')
    def mock_chmod(*args):
        print('changing file permissions for', args[0])
        if args[0] in ('file', 'dir'):
            raise PermissionError
        elif args[0] == 'map':
            monkeypatch.setattr(tasks, 'chmodrecursive', mock_recursive)
    monkeypatch.setattr(tasks.os, 'getcwd', lambda x: 'current_dir')
    monkeypatch.setattr(tasks.os, 'listdir', lambda x: ['file', 'name', '__pycache__', '.hg', 'link',
                                                        'dir', 'map'])
    monkeypatch.setattr(tasks.os.path, 'isfile',
                        lambda x: True if x.endswith('file') or x.endswith('name') else False)
    monkeypatch.setattr(tasks.os.path, 'islink', lambda x: True if x.endswith('link') else False)
    monkeypatch.setattr(tasks.os.path, 'isdir',
                        lambda x: True if x.endswith('dir') or x.endswith('map') else False)
    monkeypatch.setattr(tasks.os, 'chmod', mock_chmod)
    # monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    breakpoint()
    tasks.chmodrecursive(c)
    assert capsys.readouterr().out == ('changing file permissions for current_dir/file\n'
                                       'changing file permissions for current_dir/name\n'
                                       'changing file permissions for current_dir/dir\n'
                                       'changing file permissions for current_dir/map\n'
                                       'entering recursive call')


def test_create_bin_shortcuts(monkeypatch, capsys):
    def mock_chdir(*args):
        print('change to directory:', args[0])
    def mock_symlink(*args):
        print('make symlink from {} to {}'.format(args[0], args[1]))
    monkeypatch.setattr(tasks, 'HERE', '/tmp')
    monkeypatch.setattr(os, 'chdir', mock_chdir)
    monkeypatch.setattr(os, 'symlink', mock_symlink)
    monkeypatch.setattr(tasks.settings, 'symlinks_bin', (('target1', 'path/to/source1'),
                                                         ('target2', 'path/to/source2')))
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks.create_bin_shortcuts(c)
    assert capsys.readouterr().out == ('change to directory: {}\n'
                                       'make symlink from path/to/source1 to target1\n'
                                       'make symlink from path/to/source2 to target2\n').format('/tmp')
