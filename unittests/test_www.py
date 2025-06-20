"""unittests for ./www.py
"""
import os
import types
from invoke import MockContext
import www as testee


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def run_in_dir(self, *args, **kwargs):
    """stub for invoke.Context.run under "with invoke.Contect.cd"
    """
    print(*args, 'in', self.cwd)


def test_copy(monkeypatch, capsys):
    """unittest for www.copy
    """
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
    """unittest for www.link
    """
    monkeypatch.setattr(testee, 'home_root', 'home')
    monkeypatch.setattr(testee, 'server_root', 'server')
    monkeypatch.setattr(os, 'readlink', lambda x: f'link to dest of {x}')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.link(c, 'html,file')
    assert capsys.readouterr().out == ('sudo ln -s link to dest of home/html server\n'
                                       'sudo ln -s link to dest of home/file server\n')


def test_edit(monkeypatch, capsys):
    """unittest for www.edit
    """
    monkeypatch.setattr(testee, 'home_root', 'home')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.edit(c, 'html,file')
    assert capsys.readouterr().out == 'htmledit home/html\nhtmledit home/file\n'


def test_update_sites(monkeypatch, capsys):
    """unittest for www.update_sites
    """
    def mock_copy(c, *args):
        """stub
        """
        print('call copy with args', args)
    monkeypatch.setattr(testee, 'copy', mock_copy)
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.update_sites(c)
    assert capsys.readouterr().out == ('python check_hosts.py in ~/projects/mydomains\n'
                                       "call copy with args ('sites.html',)\n")


def test_list_wwwroot(monkeypatch, capsys):
    """unittest for www.list_wwwroot
    """
    monkeypatch.setattr(testee, 'server_root', 'server')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.list_wwwroot(c)
    assert capsys.readouterr().out == 'ls -l server\n'


def test_list_apache(monkeypatch, capsys):
    """unittest for www.list_apache
    """
    monkeypatch.setattr(testee, 'apache_root', 'apache')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.list_apache(c)
    assert capsys.readouterr().out == 'ls -l apache\n'


def test_edit_apache(monkeypatch, capsys):
    """unittest for www.edit_apache
    """
    monkeypatch.setattr(testee, 'apache_root', 'apache')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.edit_apache(c, 'html,file')
    assert capsys.readouterr().out == ('cp apache/html /tmp/html\npedit /tmp/html\n'
                                       'sudo cp /tmp/html apache/html\ncp apache/file /tmp/file\n'
                                       'pedit /tmp/file\nsudo cp /tmp/file apache/file\n')


def test_permits(monkeypatch, capsys):
    """unittest for www.permits
    """
    def mock_run_fail(c, *args):
        """stub
        """
        print(*args)
        return types.SimpleNamespace(failed=True)
    def mock_run_ok(c, *args):
        """stub
        """
        print(*args)
        return types.SimpleNamespace(failed=False)
    counter = 0
    def mock_listdir(*args):
        """stub
        """
        nonlocal counter
        counter += 1
        if counter < 2:
            return ['name']
        return []
    monkeypatch.setattr(testee.os.path, 'abspath', lambda x: f'abs/{x}')
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

    monkeypatch.setattr(testee.os, 'listdir', lambda x: ['name'])
    monkeypatch.setattr(testee.os.path, 'isdir', lambda x: False)
    testee.permits(c, 'here')
    assert capsys.readouterr().out == ''


def test_stage(monkeypatch, capsys, tmp_path):
    """unittest for www.stage
    """
    def mock_run(self, *args, **kwargs):
        """stub
        """
        print('called c.run with args', *args, kwargs)
        if args[0] == 'hg st':
            return types.SimpleNamespace(failed=True)
    def mock_run_2(self, *args, **kwargs):
        """stub
        """
        print('called c.run with args', *args, kwargs)
        if args[0] == 'hg st':
            return types.SimpleNamespace(failed=False, stdout='')
    def mock_run_3(self, *args, **kwargs):
        """stub
        """
        print('called c.run with args', *args, kwargs)
        if args[0] == 'hg st':
            return types.SimpleNamespace(failed=False, stdout='? somefile\n')
        if args[0].startswith('zenity'):
            return types.SimpleNamespace(failed=False, stdout='a message\n')
        return types.SimpleNamespace(failed=False)
    def mock_run_4(self, *args, **kwargs):
        """stub
        """
        print('called c.run with args', *args, kwargs)
        if args[0] == 'hg st':
            return types.SimpleNamespace(failed=False, stdout='M file1\n? file2\n? file3\nM file4\n')
        if args[0].startswith('hg heads'):
            return types.SimpleNamespace(failed=False, stdout='commit message')
        if args[0].startswith('zenity'):
            return types.SimpleNamespace(failed=False, stdout='a message\n')
        return types.SimpleNamespace(failed=False)
    def mock_run_5(self, *args, **kwargs):
        """stub
        """
        print('called c.run with args', *args, kwargs)
        if args[0] == 'hg st':
            return types.SimpleNamespace(failed=False, stdout='M file1\n? file2\n? file3\nM file4\n')
        if args[0].startswith('zenity'):
            return types.SimpleNamespace(failed=True, stdout='')
        return types.SimpleNamespace(failed=False)
    def mock_run_6(self, *args, **kwargs):
        """stub
        """
        print('called c.run with args', *args, kwargs)
        if args[0] == 'hg st':
            return types.SimpleNamespace(failed=False, stdout='M file1\n? file2\n? file3\nM file4\n')
        if args[0].startswith('zenity'):
            return types.SimpleNamespace(failed=False, stdout='commit message')
        if args[0].startswith('hg add'):
            return types.SimpleNamespace(failed=True)
    def mock_run_7(self, *args, **kwargs):
        """stub
        """
        print('called c.run with args', *args, kwargs)
        if args[0] == 'hg st':
            return types.SimpleNamespace(failed=False, stdout='M file1\n? file2\n? file3\nM file4\n')
        if args[0].startswith('zenity'):
            return types.SimpleNamespace(failed=False, stdout='commit message')
        if args[0].startswith('hg add'):
            return types.SimpleNamespace(failed=False)
        if args[0].startswith('hg ci'):
            return types.SimpleNamespace(failed=True)
    def mock_remove(fname):
        print(f'called os.remove with arg {fname}')
    class MockDateTime:
        """stub
        """
        @classmethod
        def today(cls):
            """stub
            """
            return types.SimpleNamespace(strftime=lambda *y: 'today')
    monkeypatch.setattr(testee.datetime, 'datetime', MockDateTime)
    mock_base = tmp_path / 'stagetest'
    monkeypatch.setattr(testee, 'R2HBASE', mock_base)
    c = MockContext()
    monkeypatch.setattr(MockContext, 'run', mock_run)
    testee.stage(c, 'testsite')
    assert capsys.readouterr().out == 'No existing mirror location found for `testsite`\n'
    siteroot = mock_base / 'testsite'
    siteroot.mkdir(parents=True)
    testee.stage(c, 'testsite')
    assert capsys.readouterr().out == ("called c.run with args hg st {'hide': 'out', 'warn': True}\n"
                                       'Mirror location should be a Mercurial repository\n')
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    testee.stage(c, 'testsite')
    assert capsys.readouterr().out == ("called c.run with args hg st {'hide': 'out', 'warn': True}\n"
                                       'Nothing to stage\n')

    testee.stage(c, 'testsite', filename='somefile', list_only=True)
    assert capsys.readouterr().out == ("called c.run with args hg st {'hide': 'out', 'warn': True}\n"
                                       'No such file\n')
    (siteroot / 'somefile').touch()
    testee.stage(c, 'testsite', filename='somefile', list_only=True)
    assert capsys.readouterr().out == ("called c.run with args hg st {'hide': 'out', 'warn': True}\n"
                                       'Not a new file\n')
    monkeypatch.setattr(MockContext, 'run', mock_run_3)
    c = MockContext()
    testee.stage(c, 'testsite', filename='somefile', list_only=True)
    assert capsys.readouterr().out == ("called c.run with args hg st {'hide': 'out', 'warn': True}\n"
                                       'somefile (new)\n\n'
                                       '1 files to be staged\n')
    stagingdir = siteroot / '.staging'
    assert not stagingdir.exists()
    testee.stage(c, 'testsite', filename='somefile')
    assert stagingdir.exists()
    assert capsys.readouterr().out == (
            "called c.run with args hg st {'hide': 'out', 'warn': True}\n"
            'called c.run with args cp somefile .staging/somefile {}\n'
            'called c.run with args zenity --entry --title="Stage: new commit"'
            ' --text="Enter commit message" --entry-text=""'
            " {'hide': True, 'warn': True}\n"
            'called c.run with args hg add somefile {}\n'
            'called c.run with args hg ci somefile  -m "a message" {}\n'
            '1 files staged\n')
    stagingdir.touch()
    monkeypatch.setattr(MockContext, 'run', mock_run_4)
    c = MockContext()
    testee.stage(c, 'testsite', new_only=True)
    assert capsys.readouterr().out == (
            "called c.run with args hg st {'hide': 'out', 'warn': True}\n"
            'called c.run with args cp file2 .staging/file2 {}\n'
            'called c.run with args cp file3 .staging/file3 {}\n'
            'called c.run with args zenity --entry --title="Stage: new commit"'
            ' --text="Enter commit message" --entry-text=""'
            " {'hide': True, 'warn': True}\n"
            'called c.run with args hg add file2 file3 {}\n'
            'called c.run with args hg ci file2 file3  -m "a message" {}\n'
            '2 files staged\n')
    (stagingdir / 'file').touch()
    testee.stage(c, 'testsite', changed_only=True)
    assert capsys.readouterr().out == (
            "called c.run with args hg st {'hide': 'out', 'warn': True}\n"
            'called c.run with args cp file1 .staging/file1 {}\n'
            'called c.run with args cp file4 .staging/file4 {}\n'
            "called c.run with args hg heads -T \"{desc}\" {'hide': True, 'warn': True}\n"
            'called c.run with args zenity --entry --title="Stage: existing commit"'
            ' --text="Enter commit message" --entry-text="commit message"'
            " {'hide': True, 'warn': True}\n"
            'called c.run with args hg ci file1 file4  --amend -m "a message" {}\n'
            '2 files staged\n')
    testee.stage(c, 'testsite')
    assert capsys.readouterr().out == (
            "called c.run with args hg st {'hide': 'out', 'warn': True}\n"
            'called c.run with args cp file2 .staging/file2 {}\n'
            'called c.run with args cp file3 .staging/file3 {}\n'
            'called c.run with args cp file1 .staging/file1 {}\n'
            'called c.run with args cp file4 .staging/file4 {}\n'
            "called c.run with args hg heads -T \"{desc}\" {'hide': True, 'warn': True}\n"
            'called c.run with args zenity --entry --title="Stage: existing commit"'
            ' --text="Enter commit message" --entry-text="commit message"'
            " {'hide': True, 'warn': True}\n"
            'called c.run with args hg add file2 file3 {}\n'
            'called c.run with args hg ci file2 file3 file1 file4  --amend -m "a message" {}\n'
            '4 files staged\n')

    (stagingdir / 'file').unlink()
    monkeypatch.setattr(testee.os, 'remove', mock_remove)
    monkeypatch.setattr(MockContext, 'run', mock_run_5)
    c = MockContext()
    testee.stage(c, 'testsite')
    assert capsys.readouterr().out == (
            "called c.run with args hg st {'hide': 'out', 'warn': True}\n"
            'called c.run with args cp file2 .staging/file2 {}\n'
            'called c.run with args cp file3 .staging/file3 {}\n'
            'called c.run with args cp file1 .staging/file1 {}\n'
            'called c.run with args cp file4 .staging/file4 {}\n'
            'called c.run with args zenity --entry --title="Stage: new commit"'
            ' --text="Enter commit message" --entry-text=""'
            " {'hide': True, 'warn': True}\n"
            'Afgebroken\n'
            f'called os.remove with arg {stagingdir}/file2\n'
            f'called os.remove with arg {stagingdir}/file3\n'
            f'called os.remove with arg {stagingdir}/file1\n'
            f'called os.remove with arg {stagingdir}/file4\n')
    monkeypatch.setattr(MockContext, 'run', mock_run_6)
    c = MockContext()
    testee.stage(c, 'testsite')
    assert capsys.readouterr().out == (
            "called c.run with args hg st {'hide': 'out', 'warn': True}\n"
            'called c.run with args cp file2 .staging/file2 {}\n'
            'called c.run with args cp file3 .staging/file3 {}\n'
            'called c.run with args cp file1 .staging/file1 {}\n'
            'called c.run with args cp file4 .staging/file4 {}\n'
            'called c.run with args zenity --entry --title="Stage: new commit"'
            ' --text="Enter commit message" --entry-text=""'
            " {'hide': True, 'warn': True}\n"
            'called c.run with args hg add file2 file3 {}\n'
            f'called os.remove with arg {stagingdir}/file2\n'
            f'called os.remove with arg {stagingdir}/file3\n'
            f'called os.remove with arg {stagingdir}/file1\n'
            f'called os.remove with arg {stagingdir}/file4\n')
    monkeypatch.setattr(MockContext, 'run', mock_run_7)
    c = MockContext()
    testee.stage(c, 'testsite')
    assert capsys.readouterr().out == (
            "called c.run with args hg st {'hide': 'out', 'warn': True}\n"
            'called c.run with args cp file2 .staging/file2 {}\n'
            'called c.run with args cp file3 .staging/file3 {}\n'
            'called c.run with args cp file1 .staging/file1 {}\n'
            'called c.run with args cp file4 .staging/file4 {}\n'
            'called c.run with args zenity --entry --title="Stage: new commit"'
            ' --text="Enter commit message" --entry-text=""'
            " {'hide': True, 'warn': True}\n"
            'called c.run with args hg add file2 file3 {}\n'
            'called c.run with args hg ci file2 file3 file1 file4  -m "commit message" {}\n'
            f'called os.remove with arg {stagingdir}/file2\n'
            f'called os.remove with arg {stagingdir}/file3\n'
            f'called os.remove with arg {stagingdir}/file1\n'
            f'called os.remove with arg {stagingdir}/file4\n')


def test_list_staged(monkeypatch, capsys, tmp_path):
    """unittest for www.list_staged
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    mock_base = tmp_path / 'list-staged'
    monkeypatch.setattr(testee, 'R2HBASE', mock_base)
    monkeypatch.setattr(testee, 'has_seflinks_true', lambda x: False)
    testee.list_staged(c, 'testsite')
    assert capsys.readouterr().out == 'No existing mirror location found for `testsite`\n'
    (mock_base / 'testsite').mkdir(parents=True)
    testee.list_staged(c, 'testsite')
    assert capsys.readouterr().out == 'No staging area found for `testsite`\n'
    stagingloc = mock_base / 'testsite' / '.staging'
    stagingloc.mkdir(parents=True)
    testee.list_staged(c, 'testsite')
    assert capsys.readouterr().out == '0 file(s) staged\n'
    (stagingloc / 'index.html').touch()
    (stagingloc / 'pic.png').touch()
    (stagingloc / 'extra.html').touch()
    (stagingloc / 'xxx').mkdir()
    (stagingloc / 'xxx/other.html').touch()
    (stagingloc / 'xxx/lalala.png').touch()
    testee.list_staged(c, 'testsite')
    assert capsys.readouterr().out == ("extra.html\n"
                                       "index.html\n"
                                       "pic.png\n"
                                       # "xxx/lalala.png\n"   # deze had hier weggelaten moeten worden
                                       # "xxx/other.html\n"   # deze ook
                                       "2 file(s) in xxx/\n"
                                       "5 file(s) staged\n")
    testee.list_staged(c, 'testsite', full=True)
    assert capsys.readouterr().out == ("extra.html\n"
                                       "index.html\n"
                                       "pic.png\n"
                                       "xxx/lalala.png\n"
                                       "xxx/other.html\n"
                                       "5 file(s) staged\n")
    monkeypatch.setattr(testee, 'has_seflinks_true', lambda x: True)
    # (stagingloc / 'index.html').touch()
    # (stagingloc / 'pic.png').touch()
    (stagingloc / 'extra.html').unlink()
    # (stagingloc / 'xxx').mkdir()
    (stagingloc / 'xxx/index.html').touch()
    # (stagingloc / 'xxx/lalala.png').touch()
    (stagingloc / 'xxx/yyy').mkdir()
    (stagingloc / 'xxx/other.html').unlink()
    (stagingloc / 'xxx/yyy/index.html').touch()
    (stagingloc / 'xxx/yyy/gargl.png').touch()
    (stagingloc / 'xxx/yyy/zzz').mkdir()
    testee.list_staged(c, 'testsite')
    assert capsys.readouterr().out == ("index.html\n"
                                       "pic.png\n"
                                       "xxx/index.html\n"
                                       # "xxx/lalala.png\n"
                                       # "xxx/yyy/gargl.png\n"
                                       # "xxx/yyy/index.html\n"
                                       "4 file(s) in xxx/\n"
                                       "6 file(s) staged\n")
    testee.list_staged(c, 'testsite', full=True)
    assert capsys.readouterr().out == ("index.html\n"
                                       "pic.png\n"
                                       "xxx/index.html\n"
                                       "xxx/lalala.png\n"
                                       "xxx/yyy/gargl.png\n"
                                       "xxx/yyy/index.html\n"
                                       "6 file(s) staged\n")
    monkeypatch.setattr(testee, 'has_seflinks_true', lambda x: True)


# heb ik met de bovenstaande test de volgende twee nog wel nodig?
def _test_list_staged_reflinks(monkeypatch, capsys, tmp_path):
    """unittest for www.list_staged_reflinks
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    mock_base = tmp_path / 'list-staged'
    monkeypatch.setattr(testee, 'R2HBASE', mock_base)
    monkeypatch.setattr(testee, 'has_seflinks_true', lambda x: False)
    stagingloc = mock_base / 'testsite2' / '.staging'
    stagingloc.mkdir(parents=True)
    (stagingloc / 'index.html').touch()
    (stagingloc / 'pic1.png').touch()
    (stagingloc / 'page2').mkdir()
    (stagingloc / 'page2' / 'index.html').touch()
    (stagingloc / 'page2' / 'doc1').mkdir()
    (stagingloc / 'page2' / 'doc1' / 'index.html').touch()
    (stagingloc / 'page2' / 'doc2').mkdir()
    (stagingloc / 'page2' / 'doc2' / 'pic2.png').touch()
    (stagingloc / 'page2' / 'doc2' / 'index.html').touch()
    (stagingloc / 'page2' / 'doc3').mkdir()
    (stagingloc / 'page2' / 'doc3' / 'index.html').touch()
    (stagingloc / 'page3').mkdir()
    (stagingloc / 'page3' / 'pic3.png').touch()
    (stagingloc / 'page3' / 'index.html').touch()
    testee.list_staged(c, 'testsite2')
    assert capsys.readouterr().out == ('index.html\n'
                                       'page2/index.html\n'
                                       'page3/index.html\n'
                                       'pic1.png\n'
                                       '5 file(s) in page2/\n'
                                       '2 file(s) in page3/\n'
                                       '9 file(s) staged\n')
    testee.list_staged(c, 'testsite2', full=True)
    assert capsys.readouterr().out == ('index.html\n'
                                       'page2/doc1/index.html\n'
                                       'page2/doc2/index.html\n'
                                       'page2/doc2/pic2.png\n'
                                       'page2/doc3/index.html\n'
                                       'page2/index.html\n'
                                       'page3/index.html\n'
                                       'page3/pic3.png\n'
                                       'pic1.png\n'
                                       '9 file(s) staged\n')


def _test_list_staged_reflinks_false(monkeypatch, capsys, tmp_path):
    """unittest for www.list_staged_reflinks_false
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    mock_base = tmp_path / 'list-staged'
    monkeypatch.setattr(testee, 'R2HBASE', mock_base)
    stagingloc = mock_base / 'testsite3' / '.staging'
    stagingloc.mkdir(parents=True)
    (stagingloc / 'index.html').touch()
    (stagingloc / 'pic.png').touch()
    (stagingloc / 'page2.html').touch()
    (stagingloc / 'page3.html').touch()
    (stagingloc / 'page2').mkdir()
    (stagingloc / 'page2' / 'doc1.html').touch()
    (stagingloc / 'page2' / 'pic2.png').touch()
    (stagingloc / 'page2' / 'doc2.html').touch()
    testee.list_staged(c, 'testsite3')
    assert capsys.readouterr().out == ('index.html\npage2.html\npage3.html\npic.png\n'
                                       '3 filei(s) in page2/\n7 file(s) staged\n')
    testee.list_staged(c, 'testsite3', full=True)
    assert capsys.readouterr().out == ('index.html\n'
                                       'page2/doc1.html\npage2/doc2.html\npage2/pic2.png\n'
                                       'page2.html\npage3.html\npic.png\n'
                                       '7 file(s) staged\n')


def test_has_seflinks_true(monkeypatch):
    """unittest for www.has_seflinks_true
    """
    class MockDirEntry:
        """stub
        """
        def __init__(self, name):
            self.name = name
    # 1. geen files in staging root -> eigenlijk onbepaald
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [])
    assert testee.has_seflinks_true('x')
    # 2. index.html in staging root -> eigenlijk onbepaald
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('index.html')])
    assert testee.has_seflinks_true('x')
    # 3. index.html en/of reflist.html in staging root -> eigenlijk onbepaald
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('index.html'),
                                                         MockDirEntry('reflist.html')])
    assert testee.has_seflinks_true('x')
    # 4. ook andere html dan index of reflist in staging root -> geen seflinks
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('index.html'),
                                                         MockDirEntry('gargl.html')])
    assert not testee.has_seflinks_true('x')
    # 5. alleen andere html dan index of reflist in staging root -> geen seflinks
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('gargl.html')])
    assert not testee.has_seflinks_true('x')
    # 6. index en ander type -> als 2/3
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('index.html'),
                                                         MockDirEntry('hi_there!')])
    assert testee.has_seflinks_true('x')
    # 7. index, ander html en ander type -> als 4
    monkeypatch.setattr(testee.os, 'scandir', lambda x: [MockDirEntry('index.html'),
                                                         MockDirEntry('gargl.html'),
                                                         MockDirEntry('hi_there!')])
    assert not testee.has_seflinks_true('x')


def test_clear_staged(monkeypatch, capsys, tmp_path):
    """unittest for www.clear_staged
    """
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    mock_base = tmp_path / 'list-staged'
    monkeypatch.setattr(testee, 'R2HBASE', mock_base)
    testee.clear_staged(c, 'testsite')
    assert capsys.readouterr().out == 'No existing mirror location found for `testsite`\n'
    (mock_base / 'testsite').mkdir(parents=True)
    testee.clear_staged(c, 'testsite')
    assert capsys.readouterr().out == 'No staging area found for `testsite`\n'
    (mock_base / 'testsite' / '.staging').mkdir(parents=True)
    testee.clear_staged(c, 'testsite')
    assert capsys.readouterr().out == f"rm -r .staging in {mock_base / 'testsite'}\n"


def test_startapp(monkeypatch, capsys):
    """unittest for www.startapp
    """
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
