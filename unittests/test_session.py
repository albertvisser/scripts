import os
import pytest
import types
from invoke import MockContext
import session as testee


def mock_run(self, *args):
    print(*args)


def run_in_dir(self, *args, **kwargs):
    print(*args, 'in', self.cwd)


class MockParser(dict):
    def read(self, *args):
        print('called ConfigParser.read() with args', *args)
        self['paths'] = {'default': 'path/to/push_to'}


def test_get_project_name(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'DEVEL', 'devpath')
    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser)
    assert testee.get_project_name('111') == 'push_to'
    assert capsys.readouterr().out == 'called ConfigParser.read() with args devpath/_111/.hg/hgrc\n'


def test_get_regfile_name(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    assert testee.get_regfile_name('name') == ''
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: 'project')
    assert testee.get_regfile_name('name') == 'project/.tickets'


def test_newproject(monkeypatch, capsys):
    def mock_copytree(*args):
        print('call copytree for `{}` to `{}`'.format(*args))
    def mock_rename(*args):
        print('call rename of `{}` to `{}`'.format(*args))
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: True)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.newproject(c, 'name')
    assert capsys.readouterr().out == 'sorry, this project name is already in use\n'
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: False)
    monkeypatch.setattr(testee.shutil, 'copytree', mock_copytree)
    monkeypatch.setattr(testee.os, 'rename', mock_rename)
    testee.newproject(c, 'name')
    assert capsys.readouterr().out == ('call copytree for `/home/albert/projects/skeleton`'
                                       ' to `/home/albert/projects/name`\n'
                                       'call rename of `/home/albert/projects/name/projectname`'
                                       ' to `/home/albert/projects/name/name`\n')


def test_start_old(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'SESSIONS', 'sessions_location')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.start_old(c, 'session_file')
    assert capsys.readouterr().out == '/bin/sh sessions_location/session_file\n'


def test_start(monkeypatch, capsys, tmp_path):
    def mock_run(*args, **kwargs):
        print(*args, kwargs)
        return types.SimpleNamespace(pid=12345)
    class MockParser(dict):
        def read(self, *args):
            print('called ConfigParser.read() with args', *args)
            self['env'] = []
            self['options'] = []
        def sections(self):
            return []
    class MockParser2(dict):
        def read(self, *args):
            print('called ConfigParser.read() with args', *args)
            self['env'] = {'var': 'value'}
            self['options'] = {'term': 'y', 'jansen': 'y', 'prfind': True}
        def sections(self):
            return True
    class MockParser3(dict):
        def read(self, *args):
            print('called ConfigParser.read() with args', *args)
            self['env'] = {}
            self['options'] = {'predit': 'y', 'dtree': 'y', 'prfind': 'y', 'check-repo': 'y'}
        def sections(self):
            return True
    # monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(testee.subprocess, 'Popen', mock_run)
    c = MockContext()
    monkeypatch.setattr(testee, 'sessionfile_root', str(tmp_path))
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    testee.start(c, 'project_name')
    assert capsys.readouterr().out == 'could not determine project location\n'
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: 'project')
    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser)
    testee.start(c, 'project_name')
    assert capsys.readouterr().out == ('called ConfigParser.read() with args project/.sessionrc\n'
                                       'could not find session configuration\n')
    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser2)
    testee.start(c, 'project_name')
    with open(f'{testee.sessionfile_root}/project_name-session-pids-start-at-12345') as f:
        data = f.read()
    assert data == '12345'
    newenv = os.environ
    newenv.update({'var': 'value'})
    assert capsys.readouterr().out == ('called ConfigParser.read() with args project/.sessionrc\n'
                                       "['gnome-terminal', '--geometry=132x43+4+40']"
                                       f" {{'cwd': 'project', 'env': {newenv}}}\n")
    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser3)
    testee.start(c, 'project_name')
    assert capsys.readouterr().out =='you already started a session for this project\n'
    os.remove(f'{testee.sessionfile_root}/project_name-session-pids-start-at-12345')
    testee.start(c, 'project_name')
    with open(f'{testee.sessionfile_root}/project_name-session-pids-start-at-12345') as f:
        data = f.read()
    assert data == '12345\n12345\n12345\n12345'
    assert capsys.readouterr().out == ('called ConfigParser.read() with args project/.sessionrc\n'
                                       f"['predit'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['dtree'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['prfind'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['check-repo'] {{'cwd': 'project', 'env': {newenv}}}\n")


def test_get_info(monkeypatch, capsys, tmp_path):
    mock_data = [types.SimpleNamespace(pid=1, info={'ppid': 0, 'name': 'x', 'exe': 'xx',
                                                    'cmdline': ['a', 'aa']}),
                 types.SimpleNamespace(pid=12345, info={'ppid': 1, 'name': 'y', 'exe': 'yy',
                                                        'cmdline': ['b', 'bb']}),
                 types.SimpleNamespace(pid=12346, info={'ppid': 1, 'name': 'z', 'exe': 'zz',
                                                        'cmdline': ['c', 'cc']})]
    def mock_iter(*args):
        print('called psutil.proc_info with args', args)
        return mock_data
    monkeypatch.setattr(testee, 'sessionfile_root', str(tmp_path))
    monkeypatch.setattr(testee.glob, 'glob',
                        lambda *x, **y: ['project_name-session-pids-start-at-12345'])
    monkeypatch.setattr(testee.psutil, 'process_iter', mock_iter)
    c = MockContext()
    testee.get_info(c, 'project_name')
    with open(f'{testee.sessionfile_root}/project_name-session-info') as f:
        data = f.read()
    assert data == ("12345, 1, y, yy, ['b', 'bb']\n"
                    "12346, 1, z, zz, ['c', 'cc']\n")
    assert capsys.readouterr().out == ("called psutil.proc_info with args"
                                       " (['name', 'ppid', 'exe', 'cmdline'],)\n")

    mock_data.append(types.SimpleNamespace(pid=12347, info={'ppid': 1, 'name': 'q', 'exe': 'qq',
                                                            'cmdline': ['d', 'dd']}))
    testee.get_info(c, 'project_name')
    with open(f'{testee.sessionfile_root}/project_name-session-info.1') as f:
        data = f.read()
    assert data == ("12345, 1, y, yy, ['b', 'bb']\n"
                    "12346, 1, z, zz, ['c', 'cc']\n"
                    "12347, 1, q, qq, ['d', 'dd']\n")
    assert capsys.readouterr().out == ("called psutil.proc_info with args"
                                       " (['name', 'ppid', 'exe', 'cmdline'],)\n")

    testee.get_info(c, 'project_name')
    with open(f'{testee.sessionfile_root}/project_name-session-info.2') as f:
        data = f.read()
    assert data == ("12345, 1, y, yy, ['b', 'bb']\n"
                    "12346, 1, z, zz, ['c', 'cc']\n"
                    "12347, 1, q, qq, ['d', 'dd']\n")
    assert capsys.readouterr().out == ("called psutil.proc_info with args"
                                       " (['name', 'ppid', 'exe', 'cmdline'],)\n")


def test_end(monkeypatch, capsys, tmp_path):
    class MockProcess:
        def __init__(self, pid, name, ppid):
            self.pid = pid
            self.info = {'ppid': ppid, 'name': name}
        def terminate(self):
            print('called process.terminate')
        def kill(self):
            print('called process.kill')
    def mock_get_pids(*args):
        print('called get_start_end_pids with args', args)
        return 1000, 1010
    mock_procs = []
    def mock_iter(*args):
        print('called psutil.proc_info with args', args)
        return mock_procs
    def mock_check_kill(*args):
        print('called check_process with args', args)
        return False, True, False
    def mock_check_invalid(*args):
        print('called check_process with args', args)
        return True, True, False
    def mock_term(*args):
        print('called process.terminate with args', args)
    def mock_kill(*args):
        print('called process.kill with args', args)
    def mock_wait(procs, timeout):
        print(f'called psutil.wait_procs with args {procs}, {timeout}')
        return ([], procs)  # [procs[0]])
    def mock_glob(pattern, root_dir=''):
        if root_dir:
            return ['project_name-session-pids-start-at-1001']
        else:
            return ['filename']
    def mock_unlink(name):
        print(f'called os.unlink with arg `{name}`')
    monkeypatch.setattr(testee.psutil, 'process_iter', mock_iter)
    monkeypatch.setattr(testee.psutil, 'wait_procs', mock_wait)
    monkeypatch.setattr(testee, 'get_start_end_pids', mock_get_pids)
    monkeypatch.setattr(testee, 'check_process', mock_check_kill)
    monkeypatch.setattr(testee.glob, 'glob', lambda *x, **y: ['xx-session-pids-start-at-12345'])
    monkeypatch.setattr(testee.os, 'unlink', mock_unlink)
    c = MockContext()
    testee.end(c, 'project_name')
    assert capsys.readouterr().out == 'No session found for this project\n'

    monkeypatch.setattr(testee.glob, 'glob', mock_glob)
    mock_procs = [types.SimpleNamespace(pid=1, info={'ppid': 0, 'name': 'systemd'}),
                  types.SimpleNamespace(pid=1001, info={'ppid': 1, 'name': 'binfab'}),
                  types.SimpleNamespace(pid=1002, info={'ppid': 1, 'name': 'inv'}),
                  types.SimpleNamespace(pid=1005, info={'ppid': 1, 'name': 'gnome-terminal-server'}),
                  types.SimpleNamespace(pid=1008, info={'ppid': 1, 'name': 'xdg-desktop-portal'}),
                  types.SimpleNamespace(pid=1018, info={'ppid': 1, 'name': 'x'})]
    testee.end(c, 'project_name')
    assert capsys.readouterr().out == ("called get_start_end_pids with args"
                                       " (['project_name-session-pids-start-at-1001'],"
                                       " 'project_name')\n"
                                       "called psutil.proc_info with args"
                                       " (['name', 'ppid', 'exe', 'cmdline'],)\n"
                                       "No processes to terminate\n")

    mock_procs = [types.SimpleNamespace(pid=1, info={'ppid': 0, 'name': 'systemd'}),
                  types.SimpleNamespace(pid=1001, info={'ppid': 1, 'name': 'binfab'}),
                  types.SimpleNamespace(pid=1018, info={'ppid': 1, 'name': 'x'})]
    monkeypatch.setattr(testee, 'get_start_end_pids', lambda *x: (1000, 0))
    monkeypatch.setattr(testee, 'check_process', mock_check_invalid)
    testee.end(c, 'project_name')
    assert capsys.readouterr().out == ("called psutil.proc_info with args"
                                       " (['name', 'ppid', 'exe', 'cmdline'],)\n"
                                       "called check_process with args (namespace(pid=1018,"
                                       " info={'ppid': 1, 'name': 'x'}), False)\n"
                                       "No processes to terminate\n")

    mock_procs = [MockProcess(1, 'systemd', 0), MockProcess(1001, 'xx', 1)]
    monkeypatch.setattr(testee, 'check_process', mock_check_kill)
    testee.end(c, 'project_name')
    assert capsys.readouterr().out == ("called psutil.proc_info with args"
                                       " (['name', 'ppid', 'exe', 'cmdline'],)\n"
                                       f"called check_process with args ({mock_procs[1]}, False)\n"
                                       "called process.terminate\n"
                                       f"called psutil.wait_procs with args [{mock_procs[1]}], 3\n"
                                       "called process.kill\n"
                                       "called os.unlink with arg `filename`\n")


def test_get_start_end_pids(monkeypatch, capsys):
    assert testee.get_start_end_pids(['project-session-pids-start-at-10000'], 'project') == (10000, 0)
    assert testee.get_start_end_pids(['project-session-pids-start-at-10000'], 'praject') == (-1, 0)
    assert testee.get_start_end_pids(['first-session-pids-start-at-10000',
                                      'next-session-pids-start-at-12000'], 'first') == (10000, 12000)
    assert testee.get_start_end_pids(['first-session-pids-start-at-10000',
                                      'next-session-pids-start-at-12000'], 'next') == (12000, 0)
    assert testee.get_start_end_pids(['first-session-pids-start-at-10000',
                                      'next-session-pids-start-at-12000'], 'none') == (-1, 0)
    assert testee.get_start_end_pids(['first-session-pids-start-at-10000',
                                      'middle-session-pids-start-at-11000',
                                      'next-session-pids-start-at-12000'], 'first') == (10000, 11000)
    assert testee.get_start_end_pids(['first-session-pids-start-at-10000',
                                      'middle-session-pids-start-at-11000',
                                      'next-session-pids-start-at-12000'], 'middle') == (11000, 12000)
    assert testee.get_start_end_pids(['first-session-pids-start-at-10000',
                                      'middle-session-pids-start-at-11000',
                                      'next-session-pids-start-at-12000'], 'next') == (12000, 0)
    assert testee.get_start_end_pids(['first-session-pids-start-at-10000',
                                      'middle-session-pids-start-at-11000',
                                      'next-session-pids-start-at-12000'], 'none') == (-1, 0)


def test_check_process(monkeypatch, capsys):
    testee.check_process(types.SimpleNamespace(info={'name': 'x'}), True) == (False, False, True)
    testee.check_process(types.SimpleNamespace(info={'name': 'x'}), False) == (False, False, False)
    testee.check_process(types.SimpleNamespace(info={'name': 'python3',
                                                     'cmdline': ['', 'check-repo']}),
                         'x') == (False, True, 'x')
    testee.check_process(types.SimpleNamespace(info={'name': 'python3', 'cmdline': ['', 'afrift']}),
                         'x') == (False, True, 'x')
    testee.check_process(types.SimpleNamespace(info={'name': 'python3', 'cmdline': ['', 'doctree']}),
                         'x') == (False, True, 'x')
    testee.check_process(types.SimpleNamespace(info={'name': 'python3', 'cmdline': ['', 'xx']}),
                         'x') == (True, False, 'x')
    testee.check_process(types.SimpleNamespace(info={'name': 'vim', 'cmdline': ['', 'xx/yy']}),
                         'x') == (False, True, 'x')
    testee.check_process(types.SimpleNamespace(info={'name': 'vim', 'cmdline': ['', '/xx/yy']}),
                         'x') == (True, False, 'x')
    testee.check_process(types.SimpleNamespace(info={'name': 'bash'}), True) == (False, True, True)
    testee.check_process(types.SimpleNamespace(info={'name': 'bash'}), False) == (False, True, True)


def test_edit_old(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'SESSIONS', 'sessions_location')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.edit_old(c, 'session_file')
    assert capsys.readouterr().out == 'pedit sessions_location/session_file\n'


def test_editconf(monkeypatch, capsys):
    def mock_get_input(prompt):
        print(f'called input(`{prompt}`)')
        return 'No'
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    c = MockContext()
    testee.editconf(c, 'projname')
    assert capsys.readouterr().out == 'could not determine project location\n'
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: 'testproj')
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: False)
    monkeypatch.setattr(testee, 'get_input_from_user', mock_get_input)
    testee.editconf(c, 'projname')
    assert capsys.readouterr().out == ('called input(`no file .sessionrc found'
                                       ' - create one now (Y/n)?`)\n')
    monkeypatch.setattr(testee, 'get_input_from_user', lambda x: 'Yes')
    testee.editconf(c, 'projname')
    assert capsys.readouterr().out == ('cp ~/bin/.sessionrc.template testproj/.sessionrc\n'
                                       'pedit testproj/.sessionrc\n')
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: True)
    testee.editconf(c, 'projname')
    assert capsys.readouterr().out == 'pedit testproj/.sessionrc\n'


def test_edittestconf(monkeypatch, capsys):
    def mock_get_input(prompt):
        print(f'called input(`{prompt}`)')
        return 'No'
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    c = MockContext()
    testee.edittestconf(c, 'projname')
    assert capsys.readouterr().out == 'could not determine project location\n'
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: 'testproj')
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: False)
    monkeypatch.setattr(testee, 'get_input_from_user', mock_get_input)
    testee.edittestconf(c, 'projname')
    assert capsys.readouterr().out == ('called input(`no file .rurc found'
                                       ' - create one now (Y/n)?`)\n')
    monkeypatch.setattr(testee, 'get_input_from_user', lambda x: 'Yes')
    testee.edittestconf(c, 'projname')
    assert capsys.readouterr().out == ('cp ~/bin/.rurc.template testproj/.rurc\n'
                                       'pedit testproj/.rurc\n')
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: True)
    testee.edittestconf(c, 'projname')
    assert capsys.readouterr().out == 'pedit testproj/.rurc\n'


def _test_list(monkeypatch, capsys):
    monkeypatch.setattr(testee.os, 'listdir', lambda x: ['name1', 'name2'])
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.list(c)
    assert capsys.readouterr().out == 'available sessions:\n    name1\n    name2\n'


def _test_newticket(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()


def _test_tickets(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    monkeypatch.setattr(testee, 'get_regfile_name', lambda x: '')
    testee.tickets(c, 'project')
    assert capsys.readouterr().out == 'wrong project name\n'
    regfile = tmp_path / 'regfile_test'
    monkeypatch.setattr(testee, 'get_regfile_name', lambda x: str(regfile))
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: False)
    testee.tickets(c, 'project')
    assert capsys.readouterr().out == "tickets I'm working on: none\n"
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: True)
    with regfile.open('w') as f:
        f.write("1\n2\n3")
    testee.tickets(c, 'project')
    assert capsys.readouterr().out == "tickets I'm working on: 1, 2, 3\n"


def _test_prep(monkeypatch, capsys):
    def mock_get_name(*args):
        print('called get_project_name() with args', *args)
        return 'project_name'
    def mock_get_dir(*args):
        print('called get_project_dir() with args', *args)
        return 'project_dir'
    monkeypatch.setattr(testee, 'get_project_name', mock_get_name)
    monkeypatch.setattr(testee, 'get_project_dir', mock_get_dir)
    monkeypatch.setattr(testee, 'DEVEL', 'devpath')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.prep(c, '111')
    assert capsys.readouterr().out == ( 'called get_project_name() with args 111\n'
                                        'called get_project_dir() with args project_name\n'
                                        'hg incoming -v devpath/_111 in project_dir\n')


def _test_pull(monkeypatch, capsys):
    def mock_get_name(*args):
        print('called get_project_name() with args', *args)
        return 'project_name'
    def mock_get_dir(*args):
        print('called get_project_dir() with args', *args)
        return 'project_dir'
    monkeypatch.setattr(testee, 'get_project_name', mock_get_name)
    monkeypatch.setattr(testee, 'get_project_dir', mock_get_dir)
    monkeypatch.setattr(testee, 'DEVEL', 'devpath')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.pull(c, '111')
    assert capsys.readouterr().out == ( 'called get_project_name() with args 111\n'
                                        'called get_project_dir() with args project_name\n'
                                        'hg pull devpath/_111 in project_dir\n'
                                        'hg up in project_dir\n')


def _test_cleanup(monkeypatch, capsys, tmp_path):
    def mock_remove(*args):
        print('call remove of `{}`'.format(*args))
    def mock_rmtree(*args):
        print('call rmtree of `{}`'.format(*args))
    monkeypatch.setattr(testee, 'get_project_name', lambda x: 'projname')
    monkeypatch.setattr(testee.os, 'remove', mock_remove)
    monkeypatch.setattr(testee.shutil, 'rmtree', mock_rmtree)
    regfile = tmp_path / 'session.test_regfile'
    monkeypatch.setattr(testee, 'get_regfile_name', lambda x: str(regfile))
    regfile.write_text('testname1\nprojname\ntestname2\n')
    c = MockContext()
    testee.cleanup(c, 'projname')
    assert capsys.readouterr().out == ('call remove of `/home/albert/bin/.sessions/projname`\n'
                                       'call rmtree of `/home/albert/devel/_projname`\n')
    data = regfile.read_text()
    assert data == 'testname1\ntestname2\n'
    regfile.write_text('projname\n')
    testee.cleanup(c, 'projname')
    assert capsys.readouterr().out == ('call remove of `/home/albert/bin/.sessions/projname`\n'
                                       'call rmtree of `/home/albert/devel/_projname`\n'
                                       f'call remove of `{regfile}`\n')
    regfile.write_text('testname1\ntestname2\n')
    testee.cleanup(c, 'projname')
    assert capsys.readouterr().out == ('call remove of `/home/albert/bin/.sessions/projname`\n'
                                       'call rmtree of `/home/albert/devel/_projname`\n')
    data = regfile.read_text()
    assert data == 'testname1\ntestname2\n'
