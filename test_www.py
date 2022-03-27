import os
import pytest
import types
from invoke import MockContext
import www


def mock_run(self, *args):
    print(*args)


def run_in_dir(self, *args, **kwargs):
    print(*args, 'in', self.cwd)


def test_copy(monkeypatch, capsys):
    monkeypatch.setattr(www, 'home_root', 'home')
    monkeypatch.setattr(www, 'server_root', 'server')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    www.copy(c, 'html,file')
    assert capsys.readouterr().out == ('sudo cp home/html server/html\n'
                                       'sudo cp home/file server/file\n')


def _test_link(monkeypatch, capsys):
    def mock_join(*args):
        return '/'.join(args)
    def mock_readlink(*args):
        return 'link to dest of {}'.format(args[0])
    monkeypatch.setattr(www, 'home_root', 'home')
    monkeypatch.setattr(www, 'server_root', 'server')
    # waarom gaat hier mocken van os nu ineens mis?
    monkeypatch.setattr(os.path, 'join', 'mock_join')
    monkeypatch.setattr(os, 'readlink', 'mock_readlink')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    www.link(c, 'html,file')
    assert capsys.readouterr().out == ('sudo ln -s home/html server\n'
                                       'sudo ln -s home/file server\n')


def test_edit(monkeypatch, capsys):
    monkeypatch.setattr(www, 'home_root', 'home')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    www.edit(c, 'html,file')
    assert capsys.readouterr().out == 'htmledit home/html\nhtmledit home/file\n'


def test_update_sites(monkeypatch, capsys):
    def mock_copy(c, *args):
        print('call copy with args', args)
    monkeypatch.setattr(www, 'copy', mock_copy)
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    www.update_sites(c)
    assert capsys.readouterr().out == ('python check_hosts.py in ~/projects/mydomains\n'
                                       "call copy with args ('sites.html',)\n")


def test_list(monkeypatch, capsys):
    monkeypatch.setattr(www, 'server_root', 'server')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    www.list(c)
    assert capsys.readouterr().out == 'ls -l server\n'


def test_list_apache(monkeypatch, capsys):
    monkeypatch.setattr(www, 'apache_root', 'apache')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    www.list_apache(c)
    assert capsys.readouterr().out == 'ls -l apache\n'


def test_edit_apache(monkeypatch, capsys):
    monkeypatch.setattr(www, 'apache_root', 'apache')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    www.edit_apache(c, 'html,file')
    assert capsys.readouterr().out == ('cp apache/html /tmp/html\npedit /tmp/html\n'
                                       'sudo cp /tmp/html apache/html\ncp apache/file /tmp/file\n'
                                       'pedit /tmp/file\nsudo cp /tmp/file apache/file\n')


def _test_permits(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()


def _test_stage(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()


def _test_startapp(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()



