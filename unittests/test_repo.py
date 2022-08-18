import os
import pytest
import types
from invoke import MockContext
import repo


def mock_run(self, *args):
    print(*args)


def run_in_dir(self, *args, **kwargs):
    print(*args, 'in', self.cwd)


def mock_check(c, *args, **kwargs):
    print('call _check() with args', args, kwargs)


def mock_check_and_run(c, *args):
    print('call check_and_run_for_project() with args', args)


def mock_check_ok(c, *args, **kwargs):
    print('call _check() with args', args, kwargs)
    return True


def mock_check_nok(c, *args, **kwargs):
    print('call _check() with args', args, kwargs)
    return False


def test_get_repofiles(monkeypatch, capsys):
    def mock_run(self, *args, **kwargs):
        print(*args, 'in', self.cwd)
        return types.SimpleNamespace(stdout='file1\nfile2.py\nfile3.json\nfile4.py\n')
    monkeypatch.setattr(repo, 'get_project_dir', lambda x: 'path/to/repo')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    assert repo.get_repofiles(c, '.') == (os.getcwd(), ['file2.py', 'file4.py'])
    assert capsys.readouterr().out == 'git ls-tree -r --name-only master in {}\n'.format(os.getcwd())

    assert repo.get_repofiles(c, 'x') == ('path/to/repo', ['file2.py', 'file4.py'])
    assert capsys.readouterr().out == 'git ls-tree -r --name-only master in path/to/repo\n'

    monkeypatch.setattr(repo, 'get_project_dir', lambda x: '')
    assert repo.get_repofiles(c, 'x') == ('', [])
    assert capsys.readouterr().out == 'not a code repository\n'


def test_get_branchname(monkeypatch, capsys):
    def mock_run(self, *args, **kwargs):
        print(*args, 'in', self.cwd)
        return types.SimpleNamespace(stdout='  master\n* current\n  another\n')
    def mock_run_2(self, *args, **kwargs):
        print(*args, 'in', self.cwd)
        return types.SimpleNamespace(stdout='* master\n  another\n')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    assert repo.get_branchname(c, 'path/to/repo') == 'current'
    assert capsys.readouterr().out == 'git branch in path/to/repo\n'
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    assert repo.get_branchname(c, 'path/to/repo') == ''
    assert capsys.readouterr().out == 'git branch in path/to/repo\n'


def test_check(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    repo._check(c, 'x')
    assert capsys.readouterr().out == 'wrong context for this routine\n'


def test_check_local(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    monkeypatch.setattr(repo, '_check', mock_check_nok)
    repo.check_local(c)
    assert capsys.readouterr().out == "call _check() with args () {'dry_run': False}\n"
    monkeypatch.setattr(repo, '_check', mock_check_ok)
    repo.check_local(c)
    assert capsys.readouterr().out == ("call _check() with args () {'dry_run': False}\n"
                                       "use 'check-repo <reponame>' to inspect changes\n"
                                       "    'binfab repo.check-local-notes` for remarks\n")
    monkeypatch.setattr(repo, '_check', mock_check)
    repo.check_local(c, dry_run=True)
    assert capsys.readouterr().out == "call _check() with args () {'dry_run': True}\n"


def test_check_local_changes(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    repo.check_local_changes(c)
    assert capsys.readouterr().out == ('gnome-terminal --geometry=100x40 -- '
                                       'view /tmp/repo_local_changes in ~/projects\n')


def test_check_local_notes(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    repo.check_local_notes(c)
    assert capsys.readouterr().out == 'treedocs projects.trd in ~/projects\n'


def test_check_remote(monkeypatch, capsys):
    monkeypatch.setattr(repo, '_check', mock_check)
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    repo.check_remote(c)
    assert capsys.readouterr().out == "call _check() with args ('remote',) {'dry_run': False}\n"
    repo.check_remote(c, dry_run=True)
    assert capsys.readouterr().out == "call _check() with args ('remote',) {'dry_run': True}\n"


def test_push_local(monkeypatch, capsys):
    monkeypatch.setattr(repo, '_check', mock_check)
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    repo.push_local(c)
    assert capsys.readouterr().out == ("call _check() with args () {'push': 'yes', 'exclude': None,"
                                       " 'dry_run': False}\n")
    repo.push_local(c, dry_run=True)
    assert capsys.readouterr().out == ("call _check() with args () {'push': 'yes', 'exclude': None,"
                                       " 'dry_run': True}\n")


def test_push_remote(monkeypatch, capsys):
    monkeypatch.setattr(repo, '_check', mock_check)
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    repo.push_remote(c)
    assert capsys.readouterr().out == ("call _check() with args ('remote',) {'push': 'yes',"
                                       " 'exclude': None, 'dry_run': False}\n")
    repo.push_remote(c, dry_run=True)
    assert capsys.readouterr().out == ("call _check() with args ('remote',) {'push': 'yes',"
                                       " 'exclude': None, 'dry_run': True}\n")


def test_pushthru(monkeypatch, capsys):
    c = MockContext()
    repo.pushthru(c, 'proj')
    assert capsys.readouterr().out == ('niet uitgevoerd, moet herschreven worden'
                                       ' o.a. naar gebruik van git\n')
    monkeypatch.setattr(repo, 'LOCALCHG', '/tmp/local_changes_test')
    monkeypatch.setattr(repo, 'REPOCHG', '/tmp/repo_changes_test')
    with open(repo.LOCALCHG, 'w') as f:
        f.write('some local change\n')
    with open(repo.REPOCHG, 'w') as f:
        f.write('some other change\n')
    monkeypatch.setattr(repo, '_check', mock_check)
    c = MockContext()
    repo.pushthru(c, '')
    assert capsys.readouterr().out == ("call _check() with args () {'push': 'yes'}\n"
                                       "call _check() with args ('remote',) {'push': 'yes'}\n\n"
                                       "ready, output in /tmp/pushthru_log\n")


def test_overview(monkeypatch, capsys):
    def mock_repo_overzicht(c, *args):
        print('call overzicht met args', args)
        return 'output directory'
    # monkeypatch.setattr(repo.os.path, 'isdir', lambda x: False)
    c = MockContext()
    repo.overview(c, 'proj', 'x') == ''
    assert capsys.readouterr().out == 'wrong spec for output type\n'

    monkeypatch.setattr(repo, 'get_project_root', lambda x: 'project_root')
    monkeypatch.setattr(repo.os, 'listdir', lambda x: ['oink'])
    monkeypatch.setattr(repo, 'repo_overzicht', mock_repo_overzicht)
    repo.overview(c, outtype='txt')
    assert capsys.readouterr().out == ("call overzicht met args ('oink', 'project_root/oink', 'txt')\n"
                                       "output in output directory\n")
    repo.overview(c, 'name,proj', 'csv')
    assert capsys.readouterr().out == ("call overzicht met args ('name', 'project_root/name', 'csv')\n"
                                       "call overzicht met args ('proj', 'project_root/proj', 'csv')\n"
                                       "output in output directory\n")


def test_repo_overzicht(monkeypatch, capsys):
    def mock_repolist_hg(*args):
        print('called make_repolist_hg()')
        return {'.hg': 'outdict_hg'}
    def mock_repolist_git(*args):
        print('called make_repolist_git()')
        return {'.git': 'outdict_git'}
    def mock_repo_ovz(*args):
        print('called make_repo_ovz with args', args)
    def mock_repocsv(*args):
        print('called make_repocsv with args', args)
    monkeypatch.setattr(repo, 'make_repolist_hg', mock_repolist_hg)
    monkeypatch.setattr(repo, 'make_repolist_git', mock_repolist_git)
    monkeypatch.setattr(repo, 'make_repo_ovz', mock_repo_ovz)
    monkeypatch.setattr(repo, 'make_repocsv', mock_repocsv)
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    monkeypatch.setattr(repo.os, 'listdir', lambda x: ['oink'])
    monkeypatch.setattr(repo.os.path, 'isdir', lambda x: False)
    assert repo.repo_overzicht(c, 'name', 'path/to/repo', 'txt') is None
    monkeypatch.setattr(repo.os.path, 'isdir', lambda x: True)
    assert repo.repo_overzicht(c, 'name', 'path/to/repo', 'txt') is None
    # assert capsys.readouterr().out == ""
    monkeypatch.setattr(repo.os, 'listdir', lambda x: ['.hg'])
    assert repo.repo_overzicht(c, 'name', 'path/to/repo', 'txt') == 'path/to/.overzicht'
    assert capsys.readouterr().out == ("called make_repolist_hg()\n"
                                       "called make_repo_ovz with args ({'.hg': 'outdict_hg'},"
                                       " 'path/to/.overzicht/name_repo.ovz')\n")
    monkeypatch.setattr(repo.os, 'listdir', lambda x: ['.git'])
    assert repo.repo_overzicht(c, 'name', 'path/to/repo', 'txt') == 'path/to/.overzicht'
    assert capsys.readouterr().out == ("called make_repolist_git()\n"
                                       "called make_repo_ovz with args ({'.git': 'outdict_git'},"
                                       " 'path/to/.overzicht/name_repo.ovz')\n")
    assert repo.repo_overzicht(c, 'name', 'path/to/repo', 'csv') == 'path/to/.overzicht'
    assert capsys.readouterr().out == ("called make_repolist_git()\n"
                                       "called make_repocsv with args ({'.git': 'outdict_git'},"
                                       " 'path/to/.overzicht/name_repo.csv')\n")


def test_make_repolist_hg(monkeypatch, capsys):
    def mock_run(c, *args, **kwargs):
        print(*args, 'in', c.cwd)
        return types.SimpleNamespace(stdout=("changeset:   01:hash\n"
                                             "user:        author name\n"
                                             "date:        Mon Oct 28 21:36:28 2019 +0100\n"
                                             "description:\n"
                                             "line\n"
                                             "another line\n\n"
                                             "changeset:   02:hash\n"
                                             "user:        author name\n"
                                             "date:        Mon Oct 28 22:36:28 2019 +0100\n"
                                             "files:       file1.py file2.py\n"
                                             "description:\n"
                                             "yet another line\n"))
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    assert repo.make_repolist_hg(c, 'path/to/repo') == {1: {'date': 'Mon Oct 28 2019 21:36:28 +0100',
                                                            'desc': ['line', 'another line']},
                                                        2: {'date': 'Mon Oct 28 2019 22:36:28 +0100',
                                                            'desc': ['yet another line'],
                                                            'files': ['file1.py', 'file2.py']}}
    assert capsys.readouterr().out == "hg log -v in path/to/repo\n"


def test_make_repolist_git(monkeypatch, capsys):
    def mock_run(c, *args, **kwargs):
        print(*args, 'in', c.cwd)
        return types.SimpleNamespace(stdout=(
                "d98e1b0; Sun Jul 24 12:57:55 2022 +0200; tooltips toegevoegd\n"
                "\n"
                " check_repo.py          | 25 +++++++++++++++++++++++++\n"
                " check_repo_tooltips.py | 31 +++++++++++++++++++++++++++++++\n"
                " 2 files changed, 56 insertions(+)\n"
                "7937ac5; Sun Jul 24 12:54:46 2022 +0200; foutje gecorrigeerd\n"
                "\n"
                " list2scite.py | 4 ++--\n"
                " 1 file changed, 2 insertions(+), 2 deletions(-)\n"
                "f89d785; Mon Jun 6 20:50:06 2022 +0200; updated readme, unittests and more\n"
                "\n"
                " 2panefm                        |   1 -\n"
                " bstart                         |   1 -\n"
                " build-bin-scripts              |  70 +++++++++++++++++++++\n"))
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    assert repo.make_repolist_git(c, 'path/to/repo') == {
        "d98e1b0": {'date': "Sun Jul 24 12:57:55 2022 +0200",
                    'description': "tooltips toegevoegd",
                    'files': ['check_repo.py', 'check_repo_tooltips.py']},
        "7937ac5": {'date': "Sun Jul 24 12:54:46 2022 +0200",
                    'description': "foutje gecorrigeerd",
                    'files': ['list2scite.py']},
        "f89d785": {'date': "Mon Jun 6 20:50:06 2022 +0200",
                    'description': "updated readme, unittests and more",
                    'files': ['2panefm', 'bstart', 'build-bin-scripts']}}
    assert capsys.readouterr().out == 'git log --pretty="%h; %ad; %s" --stat in path/to/repo\n'


def test_make_repo_ovz(monkeypatch, capsys):
    filename = '/tmp/repo_ovz_outfile'
    repo.make_repo_ovz({'naam1': {'date': 'ddd', 'desc': ['xx', 'x'], 'files': ['file1', 'file2']},
                        'naam2': {'date': 'eee', 'desc': ['yy', 'y']}}, filename)
    with open(filename) as f:
        data = f.read()
    assert data == ('ddd: xx\nx\n    file1\n    file2\neee: yy\ny\n')


def test_make_repocsv(monkeypatch, capsys):
    monkeypatch.setattr(repo.csv, 'writer', MockWriter)
    filename = '/tmp/repo_ovz_outfile'
    if os.path.exists(filename):
        os.remove(filename)
    repo.make_repocsv({'1': {'date': 'ddd', 'desc': ['x;x', 'x'], 'files': ['file1', 'file2']},
                        '2': {'date': 'eee', 'desc': ['y,y', 'y']}}, filename)
    assert os.path.exists(filename)
    assert capsys.readouterr().out == (
            "create writer to file <_io.TextIOWrapper name='/tmp/repo_ovz_outfile'"
            " mode='w' encoding='UTF-8'>\n"
            r"call writer.writerow for data [' \\ date', 'ddd', 'eee']""\n"
            r"call writer.writerow for data ['filename \\ description',"
            """ '"x;x\\nx"', '"y,y\\ny"']"""
            "\n"
            "call writer.writerow for data ['./file1', '', 'x']\n"
            "call writer.writerow for data ['./file2', '', 'x']\n")

def test_add2gitweb(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    repo.add2gitweb(c, 'name')
    assert capsys.readouterr().out == ('sudo ln -s ~/git_repos/name/.git'
                                       ' /var/lib/git/name.git\n')
    repo.add2gitweb(c, 'name', frozen=True)
    assert capsys.readouterr().out == ('sudo ln -s ~/git_repos/.frozen/name/.git'
                                       ' /var/lib/git/name.git\n')


def test_check_and_run(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    monkeypatch.setattr(repo, 'get_project_dir', lambda x: '')
    repo.check_and_run_for_project(c, '', 'command-string')
    assert capsys.readouterr().out == 'you are not in a known project directory\n'
    repo.check_and_run_for_project(c, 'name', 'command-string')
    assert capsys.readouterr().out == 'name is not a known project\n'
    monkeypatch.setattr(repo, 'get_project_dir', lambda x: 'path/to/repo')
    repo.check_and_run_for_project(c, 'repo', 'command-string')
    assert capsys.readouterr().out == 'command-string in path/to/repo\n'
    monkeypatch.setattr(repo, 'get_project_dir', lambda x: os.getcwd())
    repo.check_and_run_for_project(c, '', 'command-string')
    assert capsys.readouterr().out == 'command-string in /home/albert/bin\n'


def test_dtree(monkeypatch, capsys):
    monkeypatch.setattr(repo, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    repo.dtree(c)
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('',"
                                       " '~/projects/doctree/ensure-qt projdocs.trd')\n")
    repo.dtree(c, 'name')
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('name',"
                                       " '~/projects/doctree/ensure-qt projdocs.trd')\n")


def test_qgit(monkeypatch, capsys):
    monkeypatch.setattr(repo, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    repo.qgit(c)
    assert capsys.readouterr().out == "call check_and_run_for_project() with args ('', 'qgit')\n"
    repo.qgit(c, 'name')
    assert capsys.readouterr().out == "call check_and_run_for_project() with args ('name', 'qgit')\n"


def test_mee_bezig(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    repo.mee_bezig(c)
    assert capsys.readouterr().out == 'treedocs ~/projects/projects.trd\n'


def test_preadme(monkeypatch, capsys):
    monkeypatch.setattr(repo, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    repo.preadme(c)
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('',"
                                       " 'pedit readme.rst')\n")
    repo.preadme(c, 'name')
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('name',"
                                       " 'pedit readme.rst')\n")


def test_prshell(monkeypatch, capsys):
    monkeypatch.setattr(repo, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    repo.prshell(c)
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('',"
                                       " 'gnome-terminal --geometry=132x43+4+40')\n")
    repo.prshell(c, 'name')
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('name',"
                                       " 'gnome-terminal --geometry=132x43+4+40')\n")


def test_rebuild_filenamelist(monkeypatch, capsys):
    def mock_get_repofiles(*args):
        print('called get_repofiles() for `{}`'.format(args[1]))
        return 'path_to_repo', ['file1', 'file2']
    monkeypatch.setattr(repo, 'FILELIST', '/tmp/filelist')
    monkeypatch.setattr(repo, 'all_repos', ['repo1', 'repo2'])
    monkeypatch.setattr(repo, 'frozen_repos', ['repo2'])
    monkeypatch.setattr(repo, 'get_repofiles', mock_get_repofiles)
    c = MockContext()
    repo.rebuild_filenamelist(c)
    with open(repo.FILELIST) as f:
        data = f.read()
    assert data == 'path_to_repo/file1\npath_to_repo/file2\n'
    assert capsys.readouterr().out == 'called get_repofiles() for `repo1`\n'


def test_search(monkeypatch, capsys):
    def mock_rebuild(*args):
        print('called rebuild_filenamelist')
    monkeypatch.setattr(repo, 'FILELIST', '/tmp/filelist')
    monkeypatch.setattr(repo, 'rebuild_filenamelist', mock_rebuild)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    if os.path.exists(repo.FILELIST):
        os.remove(repo.FILELIST)
    repo.search(c)
    assert capsys.readouterr().out == ('called rebuild_filenamelist\n'
                                       'afrift -m multi /tmp/filelist -e py -P\n')
    repo.search(c, rebuild=True)
    assert capsys.readouterr().out == ('called rebuild_filenamelist\n'
                                       'afrift -m multi /tmp/filelist -e py -P\n')
    repo.search(c, 'name')
    assert capsys.readouterr().out == ('called rebuild_filenamelist\n'
                                       'afrift -m multi /tmp/filelist -e py -PN -s name\n')
    repo.search(c, 'name', rebuild=True)
    assert capsys.readouterr().out == ('called rebuild_filenamelist\n'
                                       'afrift -m multi /tmp/filelist -e py -PN -s name\n')
    with open(repo.FILELIST, 'w') as f:
        f.write('')
    repo.search(c)
    assert capsys.readouterr().out == 'afrift -m multi /tmp/filelist -e py -P\n'
    repo.search(c, rebuild=True)
    assert capsys.readouterr().out == ('called rebuild_filenamelist\n'
                                       'afrift -m multi /tmp/filelist -e py -P\n')
    repo.search(c, 'name')
    assert capsys.readouterr().out == 'afrift -m multi /tmp/filelist -e py -PN -s name\n'
    repo.search(c, 'name', rebuild=True)
    assert capsys.readouterr().out == ('called rebuild_filenamelist\n'
                                       'afrift -m multi /tmp/filelist -e py -PN -s name\n')


class MockWriter:
    def __init__(self, filename):
        print('create writer to file', filename)
    def writerow(self, data):
        print('call writer.writerow for data', data)
