"""unittests for ./lang.py
"""
import pytest
from invoke import MockContext
import lang


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def run_in_dir(self, *args, **kwargs):
    """stub for invoke.Context.run under "with invoke.Contect.cd"
    """
    print(*args, 'in', self.cwd)


def test_get_base_dir(monkeypatch, capsys):
    """unittest for lang.get_base_dir
    """
    monkeypatch.setattr(lang, 'get_project_dir', lambda x: f'project_dir for {x}')
    monkeypatch.setattr(lang.os, 'getcwd', lambda: 'path/to/here')
    assert lang.get_base_dir('.') == 'project_dir for here'
    assert lang.get_base_dir('project') == 'project_dir for project'


def test_init(monkeypatch, capsys):
    """unittest for lang.init
    """
    def mock_mkdir(path):
        """stub
        """
        print(f'called os.path.mkdir with arg `{path}`')
    counter = 0
    def mock_exists(path):
        """stub
        """
        nonlocal counter
        counter += 1
        if counter > 1:
            return False
        return True
    monkeypatch.setattr(lang, 'get_base_dir', lambda x: '')
    # monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    lang.init(c, 'proj', 'lang')
    assert capsys.readouterr().out == 'unknown project\n'
    monkeypatch.setattr(lang, 'get_base_dir', lambda x: 'base')
    monkeypatch.setattr(lang.os.path, 'exists', lambda x: False)
    monkeypatch.setattr(lang.os, 'mkdir', mock_mkdir)
    lang.init(c, 'proj', 'lang')
    assert capsys.readouterr().out == (
            'called os.path.mkdir with arg `base/locale`\n'
            'called os.path.mkdir with arg `base/locale/lang`\n'
            'called os.path.mkdir with arg `base/locale/lang/LC_MESSAGES`\n'
            'language support initialized for language type `lang`\n')
    lang.init(c, 'proj', '.', check=True)
    assert capsys.readouterr().out == ('language support not present (no `locale` subdirectory)\n')
    monkeypatch.setattr(lang.os.path, 'exists', lambda x: True)
    lang.init(c, 'proj', 'lang')
    assert capsys.readouterr().out == (
            'called os.path.mkdir with arg `base/locale/lang/LC_MESSAGES`\n'
            'language support initialized for language type `lang`\n')
    lang.init(c, 'proj', '.', check=True)
    assert capsys.readouterr().out == ('language support already present for language type `en`\n'
                                       'language support already present for language type `nl`\n')
    monkeypatch.setattr(lang.os.path, 'exists', mock_exists)
    lang.init(c, 'proj', '.', check=True)
    assert capsys.readouterr().out == ('no language support present for language type `en`\n'
                                       'no language support present for language type `nl`\n')


def test_uses_gettext(tmp_path):
    """unittest for lang.uses_gettext
    """
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
    """unittest for lang.gettext
    """
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
    """unittest for lang.merge
    """
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
    """unittest for lang.poedit
    """
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
    """unittest for lang.place
    """
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
