"""unittests for ./lang.py
"""
import types
import pytest
from invoke import MockContext
import lang as testee


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def run_in_dir(self, *args, **kwargs):
    """stub for invoke.Context.run under "with invoke.Contect.cd"
    """
    print(*args, 'in', self.cwd)


def test_get_base_dir(monkeypatch):
    """unittest for lang.get_base_dir
    """
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: f'project_dir for {x}')
    monkeypatch.setattr(testee.os, 'getcwd', lambda: 'path/to/here')
    assert testee.get_base_dir('.') == 'project_dir for here'
    assert testee.get_base_dir('project') == 'project_dir for project'


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
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: '')
    # monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.init(c, 'proj', 'lang')
    assert capsys.readouterr().out == 'unknown project\n'
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: 'base')
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: False)
    monkeypatch.setattr(testee.os, 'mkdir', mock_mkdir)
    testee.init(c, 'proj', 'lang')
    assert capsys.readouterr().out == (
            'called os.path.mkdir with arg `base/locale`\n'
            'called os.path.mkdir with arg `base/locale/lang`\n'
            'called os.path.mkdir with arg `base/locale/lang/LC_MESSAGES`\n'
            'language support initialized for language type `lang`\n')
    testee.init(c, 'proj', '.', check=True)
    assert capsys.readouterr().out == ('language support not present (no `locale` subdirectory)\n')
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: True)
    testee.init(c, 'proj', 'lang')
    assert capsys.readouterr().out == (
            'called os.path.mkdir with arg `base/locale/lang/LC_MESSAGES`\n'
            'language support initialized for language type `lang`\n')
    testee.init(c, 'proj', '.', check=True)
    assert capsys.readouterr().out == ('language support already present for language type `en`\n'
                                       'language support already present for language type `nl`\n')
    monkeypatch.setattr(testee.os.path, 'exists', mock_exists)
    testee.init(c, 'proj', '.', check=True)
    assert capsys.readouterr().out == ('no language support present for language type `en`\n'
                                       'no language support present for language type `nl`\n')


def test_uses_gettext(tmp_path):
    """unittest for lang.uses_gettext
    """
    fname = str(tmp_path / 'use_gettext_test')
    with pytest.raises(FileNotFoundError):
        testee.uses_gettext(fname)
    with open(fname, 'w') as f:
        f.write('')
    assert not testee.uses_gettext(fname)
    with open(fname, 'w') as f:
        f.write('import\ngettext\n')
    assert not testee.uses_gettext(fname)
    with open(fname, 'w') as f:
        f.write('import   gettext')
    assert testee.uses_gettext(fname)


def test_pyversion_found(monkeypatch, capsys, tmp_path):
    """unittest for lang.pyversion_found
    """
    def mock_run(self, *args, **kwargs):
        """stub for invoke.Context.run under "with invoke.Contect.cd"
        """
        print(*args, 'in', self.cwd)
        return ''
    def mock_run_2(self, *args, **kwargs):
        """stub for invoke.Context.run under "with invoke.Contect.cd"
        """
        print(*args, 'in', self.cwd)
        return types.SimpleNamespace(stdout=f'{tmp_path}/xxx\n')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    monkeypatch.setattr(testee, 'bindir', tmp_path)
    assert not testee.pyversion_found(c, 'xxx')
    assert capsys.readouterr().out == f"readlink xxx in {testee.bindir}\n"

    (tmp_path / 'xxx').touch()
    assert not testee.pyversion_found(c, 'xxx')
    assert capsys.readouterr().out == f"readlink xxx in {testee.bindir}\n"

    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    (tmp_path / 'yyy').symlink_to(tmp_path / 'xxx')
    assert testee.pyversion_found(c, 'yyy')
    assert capsys.readouterr().out == f"readlink yyy in {testee.bindir}\n"


def test_check_symlinks(monkeypatch, capsys):
    """unittest for lang.check_symlinks
    """
    def mock_found(c, name):
        "stub"
        print(f'called pyversion_found with arg {name}')
        return False
    def mock_found_2(c, name):
        "stub"
        print(f'called pyversion_found with arg {name}')
        return True
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    monkeypatch.setattr(testee, 'pydir', 'Tools/i18n')
    monkeypatch.setattr(testee, 'bindir', 'Home/bin')
    monkeypatch.setattr(testee, 'pyversion_found', mock_found)
    testee.check_symlinks(c)
    assert capsys.readouterr().out == ("called pyversion_found with arg pygettext\n"
                                       "~/bin/pygettext is not a symlink or broken\n"
                                       "called pyversion_found with arg pymsgfmt\n"
                                       "~/bin/pymsgfmt is not a symlink or broken\n")
    monkeypatch.setattr(testee, 'pyversion_found', mock_found_2)
    testee.check_symlinks(c)
    assert capsys.readouterr().out == ("called pyversion_found with arg pygettext\n"
                                       "~/bin/pygettext is ok\n"
                                       "called pyversion_found with arg pymsgfmt\n"
                                       "~/bin/pymsgfmt is ok\n")
    testee.check_symlinks(c, check=False, fix=True)
    assert capsys.readouterr().out == (
            f"rm -f pygettext in {testee.bindir}\n"
            f"ln -s {testee.pydir}/pygettext.py pygettext in {testee.bindir}\n"
            f"rm -f pymsgfmt in {testee.bindir}\n"
            f"ln -s {testee.pydir}/msgfmt.py pymsgfmt in {testee.bindir}\n")


def test_gettext(monkeypatch, capsys):
    """unittest for lang.gettext
    """
    def mock_found(c, name):
        "stub"
        print(f'called pyversion_found with arg {name}')
        return False
    def mock_found_2(c, name):
        "stub"
        print(f'called pyversion_found with arg {name}')
        return True
    def mock_determine(name):
        "stub"
        print(f'called determine_sourcedir with arg {name}')
        return ''
    def mock_determine_2(name):
        "stub"
        print(f'called determine_sourcedir with arg {name}')
        return 'xxx'
    monkeypatch.setattr(testee, 'pyversion_found', mock_found)
    monkeypatch.setattr(testee, 'determine_sourcedir', mock_determine)
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: '')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.gettext(c, 'proj', '.')
    assert capsys.readouterr().out == 'unknown project\n'
    # monkeypatch.setattr(testee, 'get_base_dir', lambda x: str(tmp_path))
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: 'base_dir')
    # (tmp_path / '.sessionrc').touch()
    # origdir = testee.os.getcwd()
    # testee.os.chdir(str(tmp_path))
    testee.gettext(c, 'proj', '.')
    assert capsys.readouterr().out == ('called pyversion_found with arg pygettext\n'
                                       'called determine_sourcedir with arg base_dir\n'
                                       'xgettext *.py in base_dir\n'
                                       'mv messages.po locale/messages-all.pot in base_dir\n'
                                       'created locale/messages-all.pot\nremember'
                                       ' that detection only works in modules that import gettext\n')
    # (tmp_path / '.sessionrc').write_text('[env]\nprogs = progdir/xxx\n')
    monkeypatch.setattr(testee, 'determine_sourcedir', mock_determine_2)
    testee.gettext(c, 'proj', '.')
    assert capsys.readouterr().out == ('called pyversion_found with arg pygettext\n'
                                       'called determine_sourcedir with arg base_dir\n'
                                       'xgettext xxx/*.py in base_dir\n'
                                       'mv messages.po locale/messages-all.pot in base_dir\n'
                                       'created locale/messages-all.pot\nremember'
                                       ' that detection only works in modules that import gettext\n')
    # testee.os.chdir(origdir)
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: 'path/to/proj')
    testee.gettext(c, 'proj', 'source.ext')
    assert capsys.readouterr().out == ('called pyversion_found with arg pygettext\n'
                                       'source.ext is not a python source file\n')
    monkeypatch.setattr(testee, 'uses_gettext', lambda x: False)
    testee.gettext(c, 'proj', 'sourcefile')
    assert capsys.readouterr().out == ('called pyversion_found with arg pygettext\n'
                                       'sourcefile.py does not import gettext\n')
    monkeypatch.setattr(testee, 'uses_gettext', lambda x: True)
    testee.gettext(c, 'proj', 'sourcefile')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pygettext\n'
            'xgettext sourcefile.py in path/to/proj\n'
            'mv messages.po locale/messages-sourcefile-py.pot in path/to/proj\n'
            'created locale/messages-sourcefile-py.pot\n'
            'remember that detection only works in modules that import gettext\n')
    testee.gettext(c, 'proj', 'src/sourcefile')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pygettext\n'
            'xgettext src/sourcefile.py in path/to/proj\n'
            'mv messages.po locale/messages-src-sourcefile-py.pot in path/to/proj\n'
            'created locale/messages-src-sourcefile-py.pot\n'
            'remember that detection only works in modules that import gettext\n')
    testee.gettext(c, 'proj', 'source.py')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pygettext\n'
            'xgettext source.py in path/to/proj\n'
            'mv messages.po locale/messages-source-py.pot in path/to/proj\n'
            'created locale/messages-source-py.pot\n'
            'remember that detection only works in modules that import gettext\n')
    monkeypatch.setattr(testee, 'pyversion_found', mock_found_2)
    testee.gettext(c, 'proj', '.')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pygettext\n'
            'called determine_sourcedir with arg path/to/proj\n'
            'pygettext . in path/to/proj\n'
            'mv messages.pot locale/messages-all.pot in path/to/proj\n'
            'created locale/messages-all.pot\n'
            'remember that detection only works in modules that import gettext\n')
    testee.gettext(c, 'proj', 'sourcefile')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pygettext\n'
            'pygettext sourcefile.py in path/to/proj\n'
            'mv messages.pot locale/messages-sourcefile-py.pot in path/to/proj\n'
            'created locale/messages-sourcefile-py.pot\n'
            'remember that detection only works in modules that import gettext\n')
    testee.gettext(c, 'proj', 'source.py')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pygettext\n'
            'pygettext source.py in path/to/proj\n'
            'mv messages.pot locale/messages-source-py.pot in path/to/proj\n'
            'created locale/messages-source-py.pot\n'
            'remember that detection only works in modules that import gettext\n')


def test_determine_sourcedir(tmp_path):
    """unittests for lang.determine_sourcedir
    """
    with pytest.raises(FileNotFoundError):
        testee.determine_sourcedir(tmp_path)
    (tmp_path / '.sessionrc').touch()
    assert not testee.determine_sourcedir(tmp_path)
    (tmp_path / '.sessionrc').write_text('xxx')
    assert not testee.determine_sourcedir(tmp_path)
    (tmp_path / '.sessionrc').write_text('xxx\nprogs = hello.py')
    assert not testee.determine_sourcedir(tmp_path)
    (tmp_path / '.sessionrc').write_text('xxx\nprogs = src/hello.py')
    assert testee.determine_sourcedir(tmp_path) == 'src'
    # possible issue (not realistic):
    (tmp_path / '.sessionrc').write_text('xxx\nprogs = hi.py src/hello.py')
    assert testee.determine_sourcedir(tmp_path) == 'hi.py src'


def test_merge(monkeypatch, capsys):
    """unittest for lang.merge
    """
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: '')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.merge(c, 'proj', 'lang', '.')
    assert capsys.readouterr().out == 'unknown project\n'
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: 'path/to/proj')
    testee.merge(c, 'proj', 'lang', '.')
    assert capsys.readouterr().out == ('msgmerge -U lang.po messages-all.pot in path/to/proj/locale\n'
                                       'merged.\n')
    testee.merge(c, 'proj', 'lang', 'src')
    assert capsys.readouterr().out == ('msgmerge -U lang.po messages-src.pot in path/to/proj/locale\n'
                                       'merged.\n')


def test_poedit(monkeypatch, capsys):
    """unittest for lang.poedit
    """
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: '')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.poedit(c, 'proj', 'lang')
    assert capsys.readouterr().out == 'unknown project\n'
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: 'path/to/proj')
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: False)
    testee.poedit(c, 'proj', 'lang')
    assert capsys.readouterr().out == 'poedit in path/to/proj\n'
    monkeypatch.setattr(testee.os.path, 'exists', lambda x: True)
    testee.poedit(c, 'proj', 'lang')
    assert capsys.readouterr().out == 'poedit locale/lang.po in path/to/proj\n'


def test_place(monkeypatch, capsys):
    """unittest for lang.place
    """
    def mock_found(c, name):
        "stub"
        print(f'called pyversion_found with arg {name}')
        return False
    def mock_found_2(c, name):
        "stub"
        print(f'called pyversion_found with arg {name}')
        return True
    monkeypatch.setattr(testee, 'pyversion_found', mock_found)
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: '')
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.place(c, 'proj', 'lang', 'appname')
    assert capsys.readouterr().out == 'unknown project\n'
    monkeypatch.setattr(testee, 'get_base_dir', lambda x: 'path/to/project')
    monkeypatch.setattr(testee.os, 'listdir', lambda x: ['file', 'name'])
    testee.place(c, 'proj', 'lang', 'appname')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pymsgfmt\n'
            'msgfmt lang.po -o lang/LC_MESSAGES/appname.mo in path/to/project/locale\n')
    testee.place(c, 'proj', 'lang', '*')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pymsgfmt\n'
            'msgfmt lang.po -o lang/LC_MESSAGES/project.mo in path/to/project/locale\n')
    testee.place(c, 'proj', 'lang', '!')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pymsgfmt\n'
            'msgfmt lang.po -o lang/LC_MESSAGES/Project.mo in path/to/project/locale\n')
    monkeypatch.setattr(testee, 'pyversion_found', mock_found_2)
    testee.place(c, 'proj', 'lang', 'appname')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pymsgfmt\n'
            'pymsgfmt -o lang/LC_MESSAGES/appname.mo lang.po in path/to/project/locale\n')
    testee.place(c, 'proj', 'lang', '*')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pymsgfmt\n'
            'pymsgfmt -o lang/LC_MESSAGES/project.mo lang.po in path/to/project/locale\n')
    testee.place(c, 'proj', 'lang', '!')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pymsgfmt\n'
            'pymsgfmt -o lang/LC_MESSAGES/Project.mo lang.po in path/to/project/locale\n')
    monkeypatch.setattr(testee.os, 'listdir', lambda x: ['file', 'pROjECT.mo'])
    monkeypatch.setattr(testee, 'pyversion_found', mock_found)
    testee.place(c, 'proj', 'lang', 'appname')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pymsgfmt\n'
            'msgfmt lang.po -o lang/LC_MESSAGES/pROjECT.mo in path/to/project/locale\n')
    monkeypatch.setattr(testee, 'pyversion_found', mock_found_2)
    testee.place(c, 'proj', 'lang', 'appname')
    assert capsys.readouterr().out == (
            'called pyversion_found with arg pymsgfmt\n'
            'pymsgfmt -o lang/LC_MESSAGES/pROjECT.mo lang.po in path/to/project/locale\n')
