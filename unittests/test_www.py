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
    assert capsys.readouterr().out == ('sudo cp  home/html server/html\n'
                                       'sudo cp  home/file server/file\n')
    monkeypatch.setattr(os.path, 'isdir', lambda x: True)
    www.copy(c, 'dir')
    assert capsys.readouterr().out == 'sudo cp -r home/dir server/dir\n'


def test_link(monkeypatch, capsys):
    monkeypatch.setattr(www, 'home_root', 'home')
    monkeypatch.setattr(www, 'server_root', 'server')
    monkeypatch.setattr(os, 'readlink', lambda x: 'link to dest of {}'.format(x))
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    www.link(c, 'html,file')
    assert capsys.readouterr().out == ('sudo ln -s link to dest of home/html server\n'
                                       'sudo ln -s link to dest of home/file server\n')


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


def test_permits(monkeypatch, capsys):
    def mock_run_fail(c, *args):
        print(*args)
        return types.SimpleNamespace(failed=True)
    def mock_run_ok(c, *args):
        print(*args)
        return types.SimpleNamespace(failed=False)
    counter = 0
    def mock_listdir(*args):
        nonlocal counter
        counter += 1
        if counter < 2:
            return ['name']
        return []
    monkeypatch.setattr(www.os.path, 'abspath', lambda x: 'abs/{}'.format(x))
    monkeypatch.setattr(www.os, 'listdir', lambda x: ['name'])
    monkeypatch.setattr(www.os.path, 'isfile', lambda x: True)
    monkeypatch.setattr(www.os.path, 'isdir', lambda x: True)
    monkeypatch.setattr(MockContext, 'run', mock_run_fail)
    c = MockContext()
    www.permits(c, 'here', do_files=True)
    assert capsys.readouterr().out == 'chmod 644 abs/here/name\nchmod failed on file abs/here/name\n'
    www.permits(c, 'here')
    assert capsys.readouterr().out == ('chmod 755 abs/here/name\n'
                                       'chmod failed on directory abs/here/name\n')
    monkeypatch.setattr(MockContext, 'run', mock_run_ok)
    c = MockContext()
    www.permits(c, 'here', do_files=True)
    assert capsys.readouterr().out == 'chmod 644 abs/here/name\n'
    monkeypatch.setattr(www.os, 'listdir', mock_listdir)
    www.permits(c, 'here')
    assert capsys.readouterr().out == 'chmod 755 abs/here/name\n'


def _test_stage(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()


def test_startapp(monkeypatch, capsys):
    monkeypatch.setattr(www, 'webapps', [])
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    www.startapp(c, 'name')
    assert capsys.readouterr().out == 'unknown webapp\n'
    monkeypatch.setattr(www, 'webapps', {'name': {'profile': 'appname', 'adr': 'domain',
                                                  'start_server': False}})
    www.startapp(c, 'name')
    assert capsys.readouterr().out == ('vivaldi-snapshot --app=http://domain --class=WebApp-appname '
                                       '--user-data-dir=/home/albert/.local/share/ice/profiles/'
                                       'appname\n')
    monkeypatch.setattr(www, 'webapps', {'name': {'profile': 'appname', 'adr': 'domain',
                                                  'start_server': '='}})
    monkeypatch.setattr(www.os.path, 'exists', lambda x: False)
    www.startapp(c, 'name')
    assert capsys.readouterr().out == ('fabsrv server.start -n name\n'
                                       'vivaldi-snapshot --app=http://domain --class=WebApp-appname '
                                       '--user-data-dir=/home/albert/.local/share/ice/profiles/'
                                       'appname\n')
    monkeypatch.setattr(www.os.path, 'exists', lambda x: True)
    www.startapp(c, 'name')
    assert capsys.readouterr().out == ('vivaldi-snapshot --app=http://domain --class=WebApp-appname '
                                       '--user-data-dir=/home/albert/.local/share/ice/profiles/'
                                       'appname\n')
    monkeypatch.setattr(www, 'webapps', {'name': {'appid': 'appname', 'start_server': False}})
    www.startapp(c, 'name')
    # assert capsys.readouterr().out == ('/home/albert/.local/share/vivaldi-snapshot/vivaldi-snapshot'
    assert capsys.readouterr().out == ('/opt/vivaldi/vivaldi'
                                       ' --profile-directory=Default --app-id=appname\n')
