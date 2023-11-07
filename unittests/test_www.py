import os
import pytest
import types
from invoke import MockContext
import www as testee


def mock_run(self, *args):
    print(*args)


def run_in_dir(self, *args, **kwargs):
    print(*args, 'in', self.cwd)


def test_copy(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'home_root', 'home')
    monkeypatch.setattr(testee, 'server_root', 'server')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.copy(c, 'html,file')
    assert capsys.readouterr().out == ('sudo cp  home/html server/html\n'
                                       'sudo cp  home/file server/file\n')
    monkeypatch.setattr(os.path, 'isdir', lambda x: True)
    testee.copy(c, 'dir')
    assert capsys.readouterr().out == 'sudo cp -r home/dir server/dir\n'


def test_link(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'home_root', 'home')
    monkeypatch.setattr(testee, 'server_root', 'server')
    monkeypatch.setattr(os, 'readlink', lambda x: 'link to dest of {}'.format(x))
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.link(c, 'html,file')
    assert capsys.readouterr().out == ('sudo ln -s link to dest of home/html server\n'
                                       'sudo ln -s link to dest of home/file server\n')


def test_edit(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'home_root', 'home')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.edit(c, 'html,file')
    assert capsys.readouterr().out == 'htmledit home/html\nhtmledit home/file\n'


def test_update_sites(monkeypatch, capsys):
    def mock_copy(c, *args):
        print('call copy with args', args)
    monkeypatch.setattr(testee, 'copy', mock_copy)
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.update_sites(c)
    assert capsys.readouterr().out == ('python check_hosts.py in ~/projects/mydomains\n'
                                       "call copy with args ('sites.html',)\n")


def test_list_wwwroot(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'server_root', 'server')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.list_wwwroot(c)
    assert capsys.readouterr().out == 'ls -l server\n'


def test_list_apache(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'apache_root', 'apache')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.list_apache(c)
    assert capsys.readouterr().out == 'ls -l apache\n'


def test_edit_apache(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'apache_root', 'apache')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.edit_apache(c, 'html,file')
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
    monkeypatch.setattr(testee.os.path, 'abspath', lambda x: 'abs/{}'.format(x))
    monkeypatch.setattr(testee.os, 'listdir', lambda x: ['name'])
    monkeypatch.setattr(testee.os.path, 'isfile', lambda x: True)
    monkeypatch.setattr(testee.os.path, 'isdir', lambda x: True)
    monkeypatch.setattr(MockContext, 'run', mock_run_fail)
    c = MockContext()
    testee.permits(c, 'here', do_files=True)
    assert capsys.readouterr().out == 'chmod 644 abs/here/name\nchmod failed on file abs/here/name\n'
    testee.permits(c, 'here')
    assert capsys.readouterr().out == ('chmod 755 abs/here/name\n'
                                       'chmod failed on directory abs/here/name\n')
    monkeypatch.setattr(MockContext, 'run', mock_run_ok)
    c = MockContext()
    testee.permits(c, 'here', do_files=True)
    assert capsys.readouterr().out == 'chmod 644 abs/here/name\n'
    monkeypatch.setattr(testee.os, 'listdir', mock_listdir)
    testee.permits(c, 'here')
    assert capsys.readouterr().out == 'chmod 755 abs/here/name\n'


def _test_stage(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()


def test_list_staged(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    mock_base = tmp_path / 'list-staged'
    monkeypatch.setattr(testee, 'R2HBASE', mock_base)
    testee.list_staged(c, 'testsite')
    assert capsys.readouterr().out == 'No existing mirror location found for `testsite`\n'
    (mock_base / 'testsite').mkdir(parents=True)
    testee.list_staged(c, 'testsite')
    assert capsys.readouterr().out == 'No staging directory found for `testsite`\n'
    stagingloc = mock_base / 'testsite' / '.staging'
    stagingloc.mkdir(parents=True)
    testee.list_staged(c, 'testsite')
    assert capsys.readouterr().out == '0 files staged\n'


def test_list_staged_reflinks(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    mock_base = tmp_path / 'list-staged'
    monkeypatch.setattr(testee, 'R2HBASE', mock_base)
    stagingloc = mock_base / 'testsite' / '.staging'
    stagingloc.mkdir(parents=True)
    (stagingloc / 'index.html').touch()
    (stagingloc / 'page2' ).mkdir()
    (stagingloc / 'page2' / 'index.html').touch()
    (stagingloc / 'page2' / 'doc1').mkdir()
    (stagingloc / 'page2' / 'doc1' / 'index.html').touch()
    (stagingloc / 'page2' / 'doc2').mkdir()
    (stagingloc / 'page2' / 'doc2' / 'index.html').touch()
    (stagingloc / 'page2' / 'doc3').mkdir()
    (stagingloc / 'page2' / 'doc3' / 'index.html').touch()
    (stagingloc / 'page3' ).mkdir()
    (stagingloc / 'page3' / 'index.html').touch()
    testee.list_staged(c, 'testsite')
    assert capsys.readouterr().out == 'index\npage2\npage3\n3 files in page2/\n6 files staged\n'
    testee.list_staged(c, 'testsite', full=True)
    assert capsys.readouterr().out == ('index\npage2\npage2/doc1\npage2/doc2\npage2/doc3\npage3\n'
                                       '6 files staged\n')


def test_list_staged_reflinks_false(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    mock_base = tmp_path / 'list-staged'
    monkeypatch.setattr(testee, 'R2HBASE', mock_base)
    stagingloc = mock_base / 'testsite' / '.staging'
    stagingloc.mkdir(parents=True)
    (stagingloc / 'index.html').touch()
    (stagingloc / 'page2.html').touch()
    (stagingloc / 'page3.html').touch()
    (stagingloc / 'page2' ).mkdir()
    (stagingloc / 'page2' / 'doc1.html').touch()
    (stagingloc / 'page2' / 'doc2.html').touch()
    testee.list_staged(c, 'testsite')
    assert capsys.readouterr().out == 'index\npage2\npage3\n2 files in page2/\n5 files staged\n'
    testee.list_staged(c, 'testsite', full=True)
    assert capsys.readouterr().out == ('index\npage2\npage2/doc1\npage2/doc2\npage3\n'
                                       '5 files staged\n')


def test_check_for_seflinks(monkeypatch, capsys):
    class MockDirEntry:
        def __init__(self, name):
            self.name = name
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('index.html')])
    assert testee.has_seflinks_true('x')
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('index.html'),
                                                         MockDirEntry('reflist.html')])
    assert testee.has_seflinks_true('x')
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('index.html'),
                                                         MockDirEntry('gargl.html')])
    assert not testee.has_seflinks_true('x')
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('index.html'),
                                                         MockDirEntry('hi_there!')])
    assert testee.has_seflinks_true('x')
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('index.html'),
                                                         MockDirEntry('gargl.html'),
                                                         MockDirEntry('hi_there!')])
    assert not testee.has_seflinks_true('x')


def test_startapp(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'webapps', [])
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.startapp(c, 'name')
    assert capsys.readouterr().out == 'unknown webapp\n'
    monkeypatch.setattr(testee, 'webapps', {'name': {'profile': 'appname', 'adr': 'domain',
                                                  'start_server': False}})
    testee.startapp(c, 'name')
    assert capsys.readouterr().out == ('vivaldi-snapshot --app=http://domain --class=WebApp-appname '
                                       '--user-data-dir=/home/albert/.local/share/ice/profiles/'
                                       'appname\n')
    monkeypatch.setattr(testee, 'webapps', {'name': {'profile': 'appname', 'adr': 'domain',
                                                  'start_server': '='}})
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: False)
    testee.startapp(c, 'name')
    assert capsys.readouterr().out == ('fabsrv server.start -n name\n'
                                       'vivaldi-snapshot --app=http://domain --class=WebApp-appname '
                                       '--user-data-dir=/home/albert/.local/share/ice/profiles/'
                                       'appname\n')
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: True)
    testee.startapp(c, 'name')
    assert capsys.readouterr().out == ('vivaldi-snapshot --app=http://domain --class=WebApp-appname '
                                       '--user-data-dir=/home/albert/.local/share/ice/profiles/'
                                       'appname\n')
    monkeypatch.setattr(testee, 'webapps', {'name': {'appid': 'appname', 'start_server': False}})
    testee.startapp(c, 'name')
    # assert capsys.readouterr().out == ('/home/albert/.local/share/vivaldi-snapshot/vivaldi-snapshot'
    assert capsys.readouterr().out == ('/opt/vivaldi/vivaldi'
                                       ' --profile-directory=Default --app-id=appname\n')
