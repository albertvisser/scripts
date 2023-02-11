import os
import pytest
import types
from invoke import MockContext
import session


def mock_run(self, *args):
    print(*args)


def run_in_dir(self, *args, **kwargs):
    print(*args, 'in', self.cwd)


class MockParser(dict):
    def read(self, *args):
        print('called ConfigParser.read() with args', *args)
        self['paths'] = {'default': 'path/to/push_to'}


def test_get_project_name(monkeypatch, capsys):
    monkeypatch.setattr(session, 'DEVEL', 'devpath')
    monkeypatch.setattr(session.configparser, 'ConfigParser', MockParser)
    assert session.get_project_name('111') == 'push_to'
    assert capsys.readouterr().out == 'called ConfigParser.read() with args devpath/_111/.hg/hgrc\n'


def test_get_regfile_name(monkeypatch, capsys):
    monkeypatch.setattr(session, 'get_project_dir', lambda x: '')
    assert session.get_regfile_name('name') == ''
    monkeypatch.setattr(session, 'get_project_dir', lambda x: 'project')
    assert session.get_regfile_name('name') == 'project/.tickets'


def test_newproject(monkeypatch, capsys):
    def mock_copytree(*args):
        print('call copytree for `{}` to `{}`'.format(*args))
    def mock_rename(*args):
        print('call rename of `{}` to `{}`'.format(*args))
    monkeypatch.setattr(session.os.path, 'exists', lambda x: True)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    session.newproject(c, 'name')
    assert capsys.readouterr().out == 'sorry, this project name is already in use\n'
    monkeypatch.setattr(session.os.path, 'exists', lambda x: False)
    monkeypatch.setattr(session.shutil, 'copytree', mock_copytree)
    monkeypatch.setattr(session.os, 'rename', mock_rename)
    session.newproject(c, 'name')
    assert capsys.readouterr().out == ('call copytree for `/home/albert/projects/skeleton`'
                                       ' to `/home/albert/projects/name`\n'
                                       'call rename of `/home/albert/projects/name/projectname`'
                                       ' to `/home/albert/projects/name/name`\n')


def test_start_old(monkeypatch, capsys):
    monkeypatch.setattr(session, 'SESSIONS', 'sessions_location')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    session.start_old(c, 'session_file')
    assert capsys.readouterr().out == '/bin/sh sessions_location/session_file\n'


def test_start(monkeypatch, capsys):
    def mock_run(*args, **kwargs):
        print(*args, kwargs)
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
    monkeypatch.setattr(session.subprocess, 'Popen', mock_run)
    c = MockContext()
    monkeypatch.setattr(session, 'get_project_dir', lambda x: '')
    session.start(c, 'project_name')
    assert capsys.readouterr().out == 'could not determine project location\n'
    monkeypatch.setattr(session, 'get_project_dir', lambda x: 'project')
    monkeypatch.setattr(session.configparser, 'ConfigParser', MockParser)
    session.start(c, 'project_name')
    assert capsys.readouterr().out == ('called ConfigParser.read() with args project/.sessionrc\n'
                                       'could not find session configuration\n')
    monkeypatch.setattr(session.configparser, 'ConfigParser', MockParser2)
    session.start(c, 'project_name')
    newenv = os.environ
    newenv.update({'var': 'value'})
    assert capsys.readouterr().out == ('called ConfigParser.read() with args project/.sessionrc\n'
                                       "['gnome-terminal', '--geometry=132x43+4+40']"
                                       f" {{'cwd': 'project', 'env': {newenv}}}\n")
    monkeypatch.setattr(session.configparser, 'ConfigParser', MockParser3)
    session.start(c, 'project_name')
    assert capsys.readouterr().out == ('called ConfigParser.read() with args project/.sessionrc\n'
                                       f"['predit'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['dtree'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['prfind'] {{'cwd': 'project', 'env': {newenv}}}\n"
                                       f"['check-repo'] {{'cwd': 'project', 'env': {newenv}}}\n")


def test_edit(monkeypatch, capsys):
    monkeypatch.setattr(session, 'SESSIONS', 'sessions_location')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    session.edit(c, 'session_file')
    assert capsys.readouterr().out == 'pedit sessions_location/session_file\n'


def test_list(monkeypatch, capsys):
    monkeypatch.setattr(session.os, 'listdir', lambda x: ['name1', 'name2'])
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    session.list(c)
    assert capsys.readouterr().out == 'available sessions:\n    name1\n    name2\n'


def _test_newticket(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()


def test_tickets(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    monkeypatch.setattr(session, 'get_regfile_name', lambda x: '')
    session.tickets(c, 'project')
    assert capsys.readouterr().out == 'wrong project name\n'
    regfile = tmp_path / 'regfile_test'
    monkeypatch.setattr(session, 'get_regfile_name', lambda x: str(regfile))
    monkeypatch.setattr(session.os.path, 'exists', lambda x: False)
    session.tickets(c, 'project')
    assert capsys.readouterr().out == "tickets I'm working on: none\n"
    monkeypatch.setattr(session.os.path, 'exists', lambda x: True)
    with regfile.open('w') as f:
        f.write("1\n2\n3")
    session.tickets(c, 'project')
    assert capsys.readouterr().out == "tickets I'm working on: 1, 2, 3\n"


def test_prep(monkeypatch, capsys):
    def mock_get_name(*args):
        print('called get_project_name() with args', *args)
        return 'project_name'
    def mock_get_dir(*args):
        print('called get_project_dir() with args', *args)
        return 'project_dir'
    monkeypatch.setattr(session, 'get_project_name', mock_get_name)
    monkeypatch.setattr(session, 'get_project_dir', mock_get_dir)
    monkeypatch.setattr(session, 'DEVEL', 'devpath')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    session.prep(c, '111')
    assert capsys.readouterr().out == ( 'called get_project_name() with args 111\n'
                                        'called get_project_dir() with args project_name\n'
                                        'hg incoming -v devpath/_111 in project_dir\n')


def test_pull(monkeypatch, capsys):
    def mock_get_name(*args):
        print('called get_project_name() with args', *args)
        return 'project_name'
    def mock_get_dir(*args):
        print('called get_project_dir() with args', *args)
        return 'project_dir'
    monkeypatch.setattr(session, 'get_project_name', mock_get_name)
    monkeypatch.setattr(session, 'get_project_dir', mock_get_dir)
    monkeypatch.setattr(session, 'DEVEL', 'devpath')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    session.pull(c, '111')
    assert capsys.readouterr().out == ( 'called get_project_name() with args 111\n'
                                        'called get_project_dir() with args project_name\n'
                                        'hg pull devpath/_111 in project_dir\n'
                                        'hg up in project_dir\n')


def test_cleanup(monkeypatch, capsys):
    def mock_remove(*args):
        print('call remove of `{}`'.format(*args))
    def mock_rmtree(*args):
        print('call rmtree of `{}`'.format(*args))
    monkeypatch.setattr(session, 'get_project_name', lambda x: 'projname')
    monkeypatch.setattr(session.os, 'remove', mock_remove)
    monkeypatch.setattr(session.shutil, 'rmtree', mock_rmtree)
    regfile = '/tmp/session_test_regfile'
    monkeypatch.setattr(session, 'get_regfile_name', lambda x: regfile)
    with open(regfile, 'w') as f:
        f.write('testname1\nprojname\ntestname2\n')
    c = MockContext()
    session.cleanup(c, 'projname')
    assert capsys.readouterr().out == ('call remove of `/home/albert/bin/.sessions/projname`\n'
                                       'call rmtree of `/home/albert/devel/_projname`\n')
    with open(regfile) as f:
        data = f.read()
    assert data == 'testname1\ntestname2\n'
    with open(regfile, 'w') as f:
        f.write('projname\n')
    session.cleanup(c, 'projname')
    assert capsys.readouterr().out == ('call remove of `/home/albert/bin/.sessions/projname`\n'
                                       'call rmtree of `/home/albert/devel/_projname`\n'
                                       'call remove of `/tmp/session_test_regfile`\n')
    with open(regfile, 'w') as f:
        f.write('testname1\ntestname2\n')
    session.cleanup(c, 'projname')
    assert capsys.readouterr().out == ('call remove of `/home/albert/bin/.sessions/projname`\n'
                                       'call rmtree of `/home/albert/devel/_projname`\n')
    with open(regfile) as f:
        data = f.read()
    assert data == 'testname1\ntestname2\n'
