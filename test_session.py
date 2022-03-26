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


def _test_newproject(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()


def test_start(monkeypatch, capsys):
    monkeypatch.setattr(session, 'SESSIONS', 'sessions_location')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    session.start(c, 'session_file')
    assert capsys.readouterr().out == '/bin/sh sessions_location/session_file\n'


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


def test_tickets(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    monkeypatch.setattr(session, 'get_regfile_name', lambda x: '')
    session.tickets(c, 'project')
    assert capsys.readouterr().out == 'wrong project name\n'
    monkeypatch.setattr(session, 'get_regfile_name', lambda x: '/tmp/regfile_test')
    monkeypatch.setattr(session.os.path, 'exists', lambda x: False)
    session.tickets(c, 'project')
    assert capsys.readouterr().out == "tickets I'm working on: none\n"
    monkeypatch.setattr(session.os.path, 'exists', lambda x: True)
    with open('/tmp/regfile_test', 'w') as f:
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


def _test_cleanup(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()

