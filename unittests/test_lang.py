import os
import pytest
import types
from invoke import MockContext
import lang


def mock_run(self, *args):
    print(*args)


def run_in_dir(self, *args, **kwargs):
    print(*args, 'in', self.cwd)


def test_get_base_dir(monkeypatch, capsys):
    monkeypatch.setattr(lang, 'get_project_dir', lambda x: 'project_dir for {}'.format(x))
    monkeypatch.setattr(lang.os, 'getcwd', lambda: 'path/to/here')
    assert lang.get_base_dir('.') == 'project_dir for here'
    assert lang.get_base_dir('project') == 'project_dir for project'


def _test_init(monkeypatch, capsys):
    c = MockContext()
    lang.init(c, 'proj', 'lang')
    lang.init(c, 'proj', '.', check=True)


def test_uses_gettext(monkeypatch, capsys, tmp_path):
    fname = str(tmp_path / 'use_gettext_test')
    with pytest.raises(FileNotFoundError):
        lang.uses_gettext(fname)
    with open(fname, 'w') as f:
        f.write('')
    assert not lang.uses_gettext(fname)
    with open(fname, 'w') as f:
        f.write('import\ngettext\n')
    assert not lang.uses_gettext(fname)
    with open(fname, 'w') as f:
        f.write('import   gettext')
    assert lang.uses_gettext(fname)


def test_gettext(monkeypatch, capsys):
    monkeypatch.setattr(lang, 'get_base_dir', lambda x: '')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    lang.gettext(c, 'proj', '.')
    assert capsys.readouterr().out == 'unknown project\n'
    monkeypatch.setattr(lang, 'get_base_dir', lambda x: 'path/to/proj')
    lang.gettext(c, 'proj', '.')
    assert capsys.readouterr().out == ('pygettext . in path/to/proj\n'
                                       'mv messages.pot locale/messages-all.pot in path/to/proj\n'
                                       'created locale/messages-all.pot\nremember'
                                       ' that detection only works in modules that import gettext\n')
    lang.gettext(c, 'proj', 'source.ext')
    assert capsys.readouterr().out == 'source.ext is not a python source file\n'
    monkeypatch.setattr(lang, 'uses_gettext', lambda x: False)
    lang.gettext(c, 'proj', 'sourcefile')
    assert capsys.readouterr().out == 'sourcefile.py does not import gettext\n'
    monkeypatch.setattr(lang, 'uses_gettext', lambda x: True)
    lang.gettext(c, 'proj', 'sourcefile')
    assert capsys.readouterr().out == ('pygettext sourcefile.py in path/to/proj\nmv messages.pot'
                                       ' locale/messages-sourcefile-py.pot in path/to/proj\n'
                                       'created locale/messages-sourcefile-py.pot\nremember'
                                       ' that detection only works in modules that import gettext\n')
    lang.gettext(c, 'proj', 'source.py')
    assert capsys.readouterr().out == ('pygettext source.py in path/to/proj\n'
                                       'mv messages.pot locale/messages-source-py.pot in path/to/proj\n'
                                       'created locale/messages-source-py.pot\nremember'
                                       ' that detection only works in modules that import gettext\n')


def test_merge(monkeypatch, capsys):
    monkeypatch.setattr(lang, 'get_base_dir', lambda x: '')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    lang.merge(c, 'proj', 'lang', '.')
    assert capsys.readouterr().out == 'unknown project\n'
    monkeypatch.setattr(lang, 'get_base_dir', lambda x: 'path/to/proj')
    lang.merge(c, 'proj', 'lang', '.')
    assert capsys.readouterr().out == ('msgmerge -U lang.po messages-all.pot in path/to/proj/locale\n'
                                       'merged.\n')
    lang.merge(c, 'proj', 'lang', 'src')
    assert capsys.readouterr().out == ('msgmerge -U lang.po messages-src.pot in path/to/proj/locale\n'
                                       'merged.\n')


def test_poedit(monkeypatch, capsys):
    monkeypatch.setattr(lang, 'get_base_dir', lambda x: '')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    lang.poedit(c, 'proj', 'lang')
    assert capsys.readouterr().out == 'unknown project\n'
    monkeypatch.setattr(lang, 'get_base_dir', lambda x: 'path/to/proj')
    monkeypatch.setattr(lang.os.path, 'exists', lambda x: False)
    lang.poedit(c, 'proj', 'lang')
    assert capsys.readouterr().out == 'poedit in path/to/proj\n'
    monkeypatch.setattr(lang.os.path, 'exists', lambda x: True)
    lang.poedit(c, 'proj', 'lang')
    assert capsys.readouterr().out == 'poedit locale/lang.po in path/to/proj\n'


def test_place(monkeypatch, capsys):
    monkeypatch.setattr(lang, 'get_base_dir', lambda x: '')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    lang.place(c, 'proj', 'lang', 'appname')
    assert capsys.readouterr().out == 'unknown project\n'

    monkeypatch.setattr(lang, 'get_base_dir', lambda x: 'path/to/project')
    monkeypatch.setattr(lang.os, 'listdir', lambda x: ['file', 'name'])
    lang.place(c, 'proj', 'lang', 'appname')
    assert capsys.readouterr().out == ('file\nname\nmsgfmt lang.po -o lang/LC_MESSAGES/appname.mo'
                                       ' in path/to/project/locale\n')
    lang.place(c, 'proj', 'lang', '*')
    assert capsys.readouterr().out == ('file\nname\nmsgfmt lang.po -o lang/LC_MESSAGES/project.mo'
                                       ' in path/to/project/locale\n')
    lang.place(c, 'proj', 'lang', '!')
    assert capsys.readouterr().out == ('file\nname\nmsgfmt lang.po -o lang/LC_MESSAGES/Project.mo'
                                       ' in path/to/project/locale\n')
    monkeypatch.setattr(lang.os, 'listdir', lambda x: ['file', 'pROjECT.mo'])
    lang.place(c, 'proj', 'lang', 'appname')
    assert capsys.readouterr().out == ('file\npROjECT.mo\nmsgfmt lang.po -o lang/LC_MESSAGES/pROjECT.mo'
                                       ' in path/to/project/locale\n')
