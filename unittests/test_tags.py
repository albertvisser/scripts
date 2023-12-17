import pytest
import types
from invoke import MockContext
import tags


def mock_run(self, *args):
    print(*args)


def run_in_dir(self, *args, **kwargs):
    print(*args, 'in', self.cwd)


def test_list_repofiles(monkeypatch, capsys):
    def mock_get_repofiles(c, *args):
        return 'path', ['file1', 'file2']
    def mock_run(self, *args, **kwargs):
        print(*args, 'in', self.cwd)
        return types.SimpleNamespace(stdout='file.py\nname.py\njust_a_name\n')
    monkeypatch.setattr(tags, 'all_repos', 'name_in_all_repos')
    monkeypatch.setattr(tags, 'get_repofiles', mock_get_repofiles)
    c = MockContext()
    assert tags.list_repofiles(c, 'name_in_all_repos') == ('path', ['file1', 'file2'])
    monkeypatch.setattr(tags, 'DEVEL', 'dev_root')
    monkeypatch.setattr(tags.os.path, 'exists', lambda x: False)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    assert tags.list_repofiles(c, '111') == (None, None)
    monkeypatch.setattr(tags.os, 'listdir', lambda x: ['.git'])
    monkeypatch.setattr(tags.os.path, 'exists', lambda x: True)
    assert tags.list_repofiles(c, '111') == ('dev_root/_111', ['file.py', 'name.py'])
    assert capsys.readouterr().out == 'git ls-tree -r --name-only master in dev_root/_111\n'
    monkeypatch.setattr(tags.os, 'listdir', lambda x: ['.hg'])
    assert tags.list_repofiles(c, '.') == ('.', ['file.py', 'name.py'])
    assert capsys.readouterr().out == 'hg manifest in .\n'
    monkeypatch.setattr(tags.os, 'listdir', lambda x: [''])
    assert tags.list_repofiles(c, '112') == (None, None)


def test_build(monkeypatch, capsys):
    monkeypatch.setattr(tags, 'all_repos', ['name'])
    monkeypatch.setattr(tags, 'list_repofiles', lambda x, y: (y, ['file', 'name']))
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    tags.build(c, '')
    assert capsys.readouterr().out == 'ctags -f .tags file name in name\n'
    tags.build(c, 'repo')
    assert capsys.readouterr().out == 'ctags -f .tags file name in repo\n'


def test_check_changes(monkeypatch, capsys):
    def mock_stat(*args):
        nonlocal counter
        counter += 1
        print('call os.stat for', *args)
        if counter == 1:
            return types.SimpleNamespace(st_mtime=1)
        return types.SimpleNamespace(st_mtime=1)
    def mock_stat_2(*args):
        nonlocal counter
        counter += 1
        print('call os.stat for', *args)
        if counter == 1:
            return types.SimpleNamespace(st_mtime=1)
        return types.SimpleNamespace(st_mtime=2)
    def mock_stat_f(*args):
        raise FileNotFoundError
    monkeypatch.setattr(tags.os, 'stat', mock_stat_f)
    counter = 0
    assert not tags.check_changes('path/to/proj', ['filename'])
    assert capsys.readouterr().out == 'no tags file found\n'
    monkeypatch.setattr(tags.os, 'stat', mock_stat)
    counter = 0
    assert not tags.check_changes('path/to/proj', ['filename'])
    assert capsys.readouterr().out == ('call os.stat for path/to/proj/.tags\n'
                                       'call os.stat for path/to/proj/filename\n')
    monkeypatch.setattr(tags.os, 'stat', mock_stat_2)
    counter = 0
    assert tags.check_changes('path/to/proj', ['filename'])
    assert capsys.readouterr().out == ('call os.stat for path/to/proj/.tags\n'
                                       'call os.stat for path/to/proj/filename\n')


def test_check(monkeypatch, capsys):
    monkeypatch.setattr(tags, 'all_repos', ['name'])
    monkeypatch.setattr(tags, 'list_repofiles', lambda x, y: (y, ['file', 'name']))
    monkeypatch.setattr(tags, 'check_changes', lambda x, y: True)
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    tags.check(c, '')
    assert capsys.readouterr().out == '.tags file rebuild needed for project name\n'
    tags.check(c, 'repo')
    assert capsys.readouterr().out == '.tags file rebuild needed for project repo\n'


def test_update(monkeypatch, capsys):
    monkeypatch.setattr(tags, 'all_repos', ['name'])
    monkeypatch.setattr(tags, 'list_repofiles', lambda x, y: (y, ['file', 'name']))
    monkeypatch.setattr(tags, 'check_changes', lambda x, y: True)
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    tags.update(c, '')
    assert capsys.readouterr().out == ('rebuilding .tags file for project name\n'
                                       'ctags -f .tags file name in name\n')
    tags.update(c, 'repo')
    assert capsys.readouterr().out == ('rebuilding .tags file for project repo\n'
                                       'ctags -f .tags file name in repo\n')
