"""unittests for ./session.py
"""
import os
import types
from io import StringIO
from invoke import MockContext
import session as testee


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def run_in_dir(self, *args, **kwargs):
    """stub for invoke.Context.run under "with invoke.Contect.cd"
    """
    print(*args, 'in', self.cwd)


class MockParser(dict):
    """stub for configparser.ConfigParser object
    """
    def read(self, *args):
        """stub
        """
        print('called ConfigParser.read() with args', *args)
        self['paths'] = {'default': 'path/to/push_to'}


def test_get_project_name(monkeypatch, capsys):
    """unittest for session.get_project_name
    """
    monkeypatch.setattr(testee, 'DEVEL', 'devpath')
    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser)
    assert testee.get_project_name('111') == 'push_to'
    assert capsys.readouterr().out == 'called ConfigParser.read() with args devpath/_111/.hg/hgrc\n'


def test_get_regfile_name(monkeypatch):
    """unittest for session.get_regfile_name
    """
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    assert testee.get_regfile_name('name') == ''
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: 'project')
    assert testee.get_regfile_name('name') == 'project/.tickets'


def test_newproject(monkeypatch, capsys):
    """unittest for session.newproject
    """
    def mock_copytree(source, target):
        """stub
        """
        print(f'call copytree for `{source}` to `{target}`')
    def mock_rename(source, target):
        """stub
        """
        print(f'call rename of `{source}` to `{target}`')
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


def test_start(monkeypatch, capsys, tmp_path):
    """unittest for session.start
    """
    def mock_run(*args, **kwargs):
        """stub
        """
        print(*args, kwargs)
        return types.SimpleNamespace(pid=12345)
    class MockParser(dict):
        """stub
        """
        def read(self, *args):
            """stub
            """
            print('called ConfigParser.read() with args', *args)
            self['env'] = []
            self['options'] = []
        def sections(self):
            """stub
            """
            return []
    class MockParser2(dict):
        """stub
        """
        def read(self, *args):
            """stub
            """
            print('called ConfigParser.read() with args', *args)
            self['env'] = {'var': 'value'}
            self['options'] = {'term': 'y', 'jansen': 'y', 'prfind': True}
        def sections(self):
            """stub
            """
            return True
    class MockParser3(dict):
        """stub
        """
        def read(self, *args):
            """stub
            """
            print('called ConfigParser.read() with args', *args)
            self['env'] = {}
            self['options'] = {'predit': 'y', 'dtree': 'y', 'prfind': 'y', 'check-repo': 'y'}
        def sections(self):
            """stub
            """
            return True
    class MockParser4(dict):
        """stub
        """
        def read(self, *args):
            """stub
            """
            print('called ConfigParser.read() with args', *args)
            self['env'] = {}
            self['options'] = {'other': 'y'}
        def sections(self):
            """stub
            """
            return True
    class MockParser5(dict):
        """stub
        """
        def read(self, *args):
            """stub
            """
            print('called ConfigParser.read() with args', *args)
            self['env'] = {}
            self['options'] = {'predit': 'n', 'dtree': 'n', 'prfind': 'n', 'check-repo': 'n'}
        def sections(self):
            """stub
            """
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
    assert capsys.readouterr().out == 'you already started a session for this project\n'

    # os.remove(f'{testee.sessionfile_root}/project_name-session-pids-start-at-12345')
    testee.start(c, 'project_name', force=True)
    with open(f'{testee.sessionfile_root}/project_name-session-pids-start-at-12345') as f:
        data = f.read()
    assert data == '12345\n12345\n12345\n12345'
    assert capsys.readouterr().out == ('called ConfigParser.read() with args project/.sessionrc\n'
                                       f"['predit'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['dtree'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['prfind'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['check-repo'] {{'cwd': 'project', 'env': {newenv}}}\n")

    os.remove(f'{testee.sessionfile_root}/project_name-session-pids-start-at-12345')
    testee.start(c, 'project_name', True)
    with open(f'{testee.sessionfile_root}/project_name-session-pids-start-at-12345') as f:
        data = f.read()
    assert data == '12345\n12345\n12345\n12345'
    assert capsys.readouterr().out == ('called ConfigParser.read() with args project/.sessionrc\n'
                                       f"['tredit'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['dtree'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['prfind'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['check-repo'] {{'cwd': 'project', 'env': {newenv}}}\n")

    os.remove(f'{testee.sessionfile_root}/project_name-session-pids-start-at-12345')
    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser4)
    testee.start(c, 'project_name', True)
    assert not os.path.exists(f'{testee.sessionfile_root}/project_name-session-pids-start-at-12345')
    assert capsys.readouterr().out == 'called ConfigParser.read() with args project/.sessionrc\n'

    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser5)
    testee.start(c, 'project_name', True)
    assert not os.path.exists(f'{testee.sessionfile_root}/project_name-session-pids-start-at-12345')
    assert capsys.readouterr().out == 'called ConfigParser.read() with args project/.sessionrc\n'


def test_create(monkeypatch, capsys, tmp_path):
    """unittest for session.create
    """
    def mock_run(*args, **kwargs):
        """stub
        """
        print(*args, kwargs)
        return types.SimpleNamespace(pid=12345)
    class MockParser(dict):
        """stub
        """
        def read(self, *args):
            """stub
            """
            print('called ConfigParser.read() with args', *args)
            self['env'] = []
            self['options'] = []
        def sections(self):
            """stub
            """
            return []
    class MockParser2(dict):
        """stub
        """
        def read(self, *args):
            """stub
            """
            print('called ConfigParser.read() with args', *args)
            self['env'] = {'var': 'value', 'x': 'yy'}
            self['options'] = {'predit': 'y', 'dtree': 'y', 'prfind': 'y', 'check-repo': 'y'}
        def sections(self):
            """stub
            """
            return True
    class MockParser3(dict):
        """stub
        """
        def read(self, *args):
            """stub
            """
            print('called ConfigParser.read() with args', *args)
            self['env'] = {}
            self['options'] = {'other': 'y'}
        def sections(self):
            """stub
            """
            return True
    class MockParser4(dict):
        """stub
        """
        def read(self, *args):
            """stub
            """
            print('called ConfigParser.read() with args', *args)
            self['env'] = {}
            self['options'] = {'predit': 'n', 'dtree': 'n', 'prfind': 'n', 'check-repo': 'n'}
        def sections(self):
            """stub
            """
            return True
    # monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(testee.subprocess, 'Popen', mock_run)
    c = MockContext()
    monkeypatch.setattr(testee, 'sessionfile_root', str(tmp_path))
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    testee.create(c, 'project_name')
    assert capsys.readouterr().out == 'could not determine project location\n'

    monkeypatch.setattr(testee, 'get_project_dir', lambda x: 'project')
    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser)
    testee.create(c, 'project_name')
    assert capsys.readouterr().out == ('called ConfigParser.read() with args project/.sessionrc\n'
                                       'could not find session configuration\n')

    monkeypatch.setattr(testee, 'SESSIONLOC', str(tmp_path))
    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser2)
    testee.create(c, 'project_name')
    assert (tmp_path / 'project_name.session').exists()
    assert (tmp_path / 'project_name.session').read_text() == (
        'wmctrl -r :ACTIVE: -e 0,4,0,1072,808\ncd project\n'
        "export var='value'\nexport x='yy'\npredit &\ndtree &\nprfind &\ncheck-repo &\n")
    assert capsys.readouterr().out == (
            'called ConfigParser.read() with args project/.sessionrc\n'
            'done; start the session using "source project_name.session"\n')

    testee.create(c, 'project_name', True)
    assert (tmp_path / 'project_name.session').read_text() == (
        'wmctrl -r :ACTIVE: -e 0,4,0,1072,808\ncd project\n'
        "export var='value'\nexport x='yy'\ntredit &\ndtree &\nprfind &\ncheck-repo &\n")
    assert capsys.readouterr().out == (
            'called ConfigParser.read() with args project/.sessionrc\n'
            'done; start the session using "source project_name.session"\n')

    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser3)
    testee.create(c, 'project_name')
    assert (tmp_path / 'project_name.session').read_text() == (
        'wmctrl -r :ACTIVE: -e 0,4,0,1072,808\ncd project\n')
    assert capsys.readouterr().out == (
            'called ConfigParser.read() with args project/.sessionrc\n'
            'done; start the session using "source project_name.session"\n')

    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser4)
    testee.create(c, 'project_name')
    assert (tmp_path / 'project_name.session').read_text() == (
        'wmctrl -r :ACTIVE: -e 0,4,0,1072,808\ncd project\n')
    assert capsys.readouterr().out == (
            'called ConfigParser.read() with args project/.sessionrc\n'
            'done; start the session using "source project_name.session"\n')


def test_get_info(monkeypatch, capsys, tmp_path):
    """unittest for session.get_info
    """
    mock_data = [types.SimpleNamespace(pid=1, info={'ppid': 0, 'name': 'x', 'exe': 'xx',
                                                    'cmdline': ['a', 'aa']}),
                 types.SimpleNamespace(pid=12345, info={'ppid': 1, 'name': 'y', 'exe': 'yy',
                                                        'cmdline': ['b', 'bb']}),
                 types.SimpleNamespace(pid=12346, info={'ppid': 1, 'name': 'z', 'exe': 'zz',
                                                        'cmdline': ['c', 'cc']})]
    def mock_iter(*args):
        """stub
        """
        print('called psutil.proc_info with args', args)
        return mock_data
    monkeypatch.setattr(testee, 'sessionfile_root', str(tmp_path))
    monkeypatch.setattr(testee.glob, 'glob',
                        lambda *x, **y: ['project_name-session-pids-start-at-12345'])
    monkeypatch.setattr(testee.psutil, 'process_iter', mock_iter)
    c = MockContext()
    testee.get_info(c)
    assert capsys.readouterr().out == "project_name-session-pids-start-at-12345\n"
    testee.get_info(c, 'project_name')
    with open(f'{testee.sessionfile_root}/project_name-session-info') as f:
        data = f.read()
    assert data == ("12345, 1, y, yy, ['b', 'bb']\n"
                    "12346, 1, z, zz, ['c', 'cc']\n")
    assert capsys.readouterr().out == (
            "called psutil.proc_info with args (['name', 'ppid', 'exe', 'cmdline'],)\n"
            f"info in {testee.sessionfile_root}/project_name-session-info\n")

    mock_data.append(types.SimpleNamespace(pid=12347, info={'ppid': 1, 'name': 'q', 'exe': 'qq',
                                                            'cmdline': ['d', 'dd']}))
    testee.get_info(c, 'project_name')
    with open(f'{testee.sessionfile_root}/project_name-session-info.1') as f:
        data = f.read()
    assert data == ("12345, 1, y, yy, ['b', 'bb']\n"
                    "12346, 1, z, zz, ['c', 'cc']\n"
                    "12347, 1, q, qq, ['d', 'dd']\n")
    assert capsys.readouterr().out == (
            "called psutil.proc_info with args (['name', 'ppid', 'exe', 'cmdline'],)\n"
            f"info in {testee.sessionfile_root}/project_name-session-info.1\n")

    testee.get_info(c, 'project_name')
    with open(f'{testee.sessionfile_root}/project_name-session-info.2') as f:
        data = f.read()
    assert data == ("12345, 1, y, yy, ['b', 'bb']\n"
                    "12346, 1, z, zz, ['c', 'cc']\n"
                    "12347, 1, q, qq, ['d', 'dd']\n")
    assert capsys.readouterr().out == (
            "called psutil.proc_info with args (['name', 'ppid', 'exe', 'cmdline'],)\n"
            f"info in {testee.sessionfile_root}/project_name-session-info.2\n")


def test_delete(monkeypatch, capsys):
    """unittest for session.delete
    """
    def mock_unlink(name):
        """stub
        """
        print(f'called os.unlink with arg `{name}`')
    monkeypatch.setattr(testee.glob, 'glob', lambda *x, **y: ['xx-session-pids-start-at-12345'])
    monkeypatch.setattr(testee.os, 'unlink', mock_unlink)
    c = MockContext()
    testee.delete(c, 'xx')
    assert capsys.readouterr().out == 'called os.unlink with arg `xx-session-pids-start-at-12345`\n'


def test_end(monkeypatch, capsys):
    """unittest for session.end
    """
    class MockProcess:
        """stub
        """
        def __init__(self, pid, name, ppid):
            self.pid = pid
            self.info = {'ppid': ppid, 'name': name}
        def terminate(self):
            """stub
            """
            print('called process.terminate')
        def kill(self):
            """stub
            """
            print('called process.kill')
    def mock_get_pids(*args):
        """stub
        """
        print('called get_start_end_pids with args', args)
        return 1000, 1010
    mock_procs = []
    def mock_iter(*args):
        """stub
        """
        print('called psutil.proc_info with args', args)
        return mock_procs
    def mock_check_kill(*args):
        """stub
        """
        print('called check_process with args', args)
        return False, True, False
    def mock_check_invalid(*args):
        """stub
        """
        print('called check_process with args', args)
        return True, True, False
    def mock_check_nokill(*args):
        """stub
        """
        print('called check_process with args', args)
        return False, False, False
    def mock_wait(procs, timeout):
        """stub
        """
        print(f'called psutil.wait_procs with args {procs}, {timeout}')
        return ([], procs)  # [procs[0]])
    def mock_glob(pattern, root_dir=''):
        """stub
        """
        if root_dir:
            return ['project_name-session-pids-start-at-1001']
        return ['filename']
    def mock_unlink(name):
        """stub
        """
        print(f'called os.unlink with arg `{name}`')
    def mock_select(*args):
        print('called select_name_for_session with args', args)
        return ''
    def mock_select_2(*args):
        print('called select_name_for_session with args', args)
        return 'project_name'
    monkeypatch.setattr(testee.psutil, 'process_iter', mock_iter)
    monkeypatch.setattr(testee.psutil, 'wait_procs', mock_wait)
    monkeypatch.setattr(testee, 'get_start_end_pids', mock_get_pids)
    monkeypatch.setattr(testee, 'check_process', mock_check_kill)
    monkeypatch.setattr(testee.glob, 'glob', lambda *x, **y: ['xx-session-pids-start-at-12345'])
    monkeypatch.setattr(testee.os, 'unlink', mock_unlink)
    c = MockContext()
    monkeypatch.setattr(testee, 'select_name_for_session', mock_select)
    testee.end(c)
    assert capsys.readouterr().out == (f'called select_name_for_session with args ({c},'
                                       " ['xx-session-pids-start-at-12345'])\n")

    monkeypatch.setattr(testee, 'select_name_for_session', mock_select_2)
    testee.end(c)
    assert capsys.readouterr().out == (f'called select_name_for_session with args ({c},'
                                       " ['xx-session-pids-start-at-12345'])\n"
                                       'No session found for this project\n')

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

    mock_procs = [MockProcess(1, 'systemd', 0), MockProcess(1001, 'xx', 1)]
    monkeypatch.setattr(testee, 'check_process', mock_check_nokill)
    testee.end(c, 'project_name')
    assert capsys.readouterr().out == ("called psutil.proc_info with args"
                                       " (['name', 'ppid', 'exe', 'cmdline'],)\n"
                                       f"called check_process with args ({mock_procs[1]}, False)\n"
                                       "No processes to terminate\n")


def test_select_name_for_session(monkeypatch, capsys):
    """unittest for session.test_select_name_for_session
    """
    def mock_run(self, *args, **kwargs):
        print('called context.run with args', args, kwargs)
        return types.SimpleNamespace(stdout='result')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    assert testee.select_name_for_session(c, ['xxx-yyy']) == 'xxx-yyy'
    assert capsys.readouterr().out == ""
    assert testee.select_name_for_session(c, ['xxx-aaa', 'yyy-bbb']) == 'result'
    assert capsys.readouterr().out == ('called context.run with args (\'zenity --list'
                                       ' --title="Choose which session to terminate"'
                                       ' --column="Session name" xxx-aaa yyy-bbb\',)'
                                       ' {\'warn\': True, \'hide\': True}\n')


def test_get_start_end_pids():
    """unittest for session.get_start_end_pids
    """
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


def test_check_process():
    """unittest for session.check_process
    """
    testproc = types.SimpleNamespace(info={'name': 'x'})
    assert testee.check_process(testproc, True) == (False, False, True)
    testproc = types.SimpleNamespace(info={'name': 'x'})
    assert testee.check_process(testproc, False) == (False, False, False)
    testproc = types.SimpleNamespace(info={'name': 'python3', 'cmdline': ['', 'check-repo']})
    assert testee.check_process(testproc, 'x') == (False, True, 'x')
    testproc = types.SimpleNamespace(info={'name': 'python3', 'cmdline': ['', 'afrift']})
    assert testee.check_process(testproc, 'x') == (False, True, 'x')
    testproc = types.SimpleNamespace(info={'name': 'python3', 'cmdline': ['', 'doctree']})
    assert testee.check_process(testproc, 'x') == (False, True, 'x')
    testproc = types.SimpleNamespace(info={'name': 'python3', 'cmdline': ['', 'xx']})
    assert testee.check_process(testproc, 'x') == (True, False, 'x')
    testproc = types.SimpleNamespace(info={'name': 'vim', 'cmdline': ['', 'xx/yy']})
    assert testee.check_process(testproc, 'x') == (False, True, 'x')
    testproc = types.SimpleNamespace(info={'name': 'vim', 'cmdline': ['', '/xx/yy']})
    assert testee.check_process(testproc, 'x') == (True, False, 'x')
    testproc = types.SimpleNamespace(info={'name': 'bash'})
    assert testee.check_process(testproc, True) == (True, False, True)  # niet (False, True, True)
    testproc = types.SimpleNamespace(info={'name': 'bash'})
    assert testee.check_process(testproc, False) == (False, True, True)


def test_get_input_from_user(monkeypatch):
    """unittest for session.get_input_from_user
    """
    test_input = StringIO('x\n')
    monkeypatch.setattr('sys.stdin', test_input)
    assert testee.get_input_from_user('prompt', 'y') == 'x'
    test_input = StringIO('\n')
    monkeypatch.setattr('sys.stdin', test_input)
    assert testee.get_input_from_user('prompt', 'y') == 'y'


def test_editconf(monkeypatch, capsys, tmp_path):
    """unittest for session.editconf
    """
    def mock_get_input(prompt, response):
        """stub
        """
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
    monkeypatch.setattr(testee, 'get_input_from_user', lambda x, y: 'Yes')
    testee.editconf(c, 'projname')
    assert capsys.readouterr().out == ('cp ~/bin/.sessionrc.template testproj/.sessionrc\n'
                                       'pedit testproj/.sessionrc\n'
                                       "Don't forget to (re)create the session script if needed\n")
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: True)
    testee.editconf(c, 'projname')
    assert capsys.readouterr().out == ('pedit testproj/.sessionrc\n'
                                       "Don't forget to (re)create the session script if needed\n")
    orig = testee.os.getcwd()
    projdir = tmp_path / 'testdir'
    projdir.mkdir()
    os.chdir(projdir)
    monkeypatch.setattr(testee, 'all_repos', [])
    testee.editconf(c)
    assert capsys.readouterr().out == "you are not in a (known) repository\n"
    monkeypatch.setattr(testee, 'all_repos', ['testdir'])
    testee.editconf(c)
    assert capsys.readouterr().out == (f"pedit {projdir}/.sessionrc\n"
                                       "Don't forget to (re)create the session script if needed\n")
    os.chdir(orig)


def test_edittestconf(monkeypatch, capsys, tmp_path):
    """unittest for session.edittestconf
    """
    def mock_get_input(prompt, response):
        """stub
        """
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
    monkeypatch.setattr(testee, 'get_input_from_user', lambda x, y: 'Yes')
    testee.edittestconf(c, 'projname')
    assert capsys.readouterr().out == ('cp ~/bin/.rurc.template testproj/.rurc\n'
                                       'pedit testproj/.rurc\n')
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: True)
    testee.edittestconf(c, 'projname')
    assert capsys.readouterr().out == 'pedit testproj/.rurc\n'
    orig = testee.os.getcwd()
    projdir = tmp_path / 'testdir'
    projdir.mkdir()
    os.chdir(projdir)
    monkeypatch.setattr(testee, 'all_repos', [])
    testee.edittestconf(c)
    assert capsys.readouterr().out == "you are not in a (known) repository\n"
    monkeypatch.setattr(testee, 'all_repos', ['testdir'])
    testee.edittestconf(c)
    assert capsys.readouterr().out == f"pedit {projdir}/.rurc\n"
    os.chdir(orig)
