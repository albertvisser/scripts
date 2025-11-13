"""unittests for ./repo.py
"""
import os
from io import StringIO
import pytest
import types
from invoke import MockContext
import repo as testee


def mock_run(self, *args, **kwargs):
    """stub for invoke.Context.run
    """
    print('called run with args', args, kwargs)


def run_in_dir(self, *args, **kwargs):
    """stub for invoke.Context.run under "with invoke.Contect.cd"
    """
    print('called run with args', args, kwargs, 'in', self.cwd)


class MockCheck(testee.Check):
    """stub for repo.Check object
    """
    def __init__(self, c, *args, **kwargs):
        print('call Check() with args', args, kwargs)
        super().__init__(c, *args, **kwargs)
    def run(self):
        """stub
        """
        print('call Check.run()')


def mock_check_and_run(c, *args):
    """stub
    """
    print('call check_and_run_for_project() with args', args)


def mock_check_ok(self):
    """stub
    """
    print('call Check.run()')
    return True


def mock_check_nok(self):
    """stub
    """
    print('call Check.run()')
    return False


def test_get_repofiles(monkeypatch, capsys):
    """unittest for repo.get_repofiles
    """
    def mock_run(self, *args, **kwargs):
        """stub
        """
        print(*args, 'in', self.cwd)
        return types.SimpleNamespace(stdout='file1\nfile2.py\nfile3.json\nfile4.py\n')
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: 'path/to/repo')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    assert testee.get_repofiles(c, '.') == (os.getcwd(), ['file2.py', 'file4.py'])
    assert capsys.readouterr().out == f'git ls-tree -r --name-only master in {os.getcwd()}\n'

    assert testee.get_repofiles(c, 'x') == ('path/to/repo', ['file2.py', 'file4.py'])
    assert capsys.readouterr().out == 'git ls-tree -r --name-only master in path/to/repo\n'

    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    assert testee.get_repofiles(c, 'x') == ('', [])
    assert capsys.readouterr().out == 'not a code repository\n'


def test_get_branchname(monkeypatch, capsys):
    """unittest for repo.get_branchname
    """
    def mock_run(self, *args, **kwargs):
        """stub
        """
        print(*args, 'in', self.cwd)
        return types.SimpleNamespace(stdout='  master\n* current\n  another\n')
    def mock_run_2(self, *args, **kwargs):
        """stub
        """
        print(*args, 'in', self.cwd)
        return types.SimpleNamespace(stdout='* master\n  another\n')
    def mock_run_3(self, *args, **kwargs):
        """stub
        """
        print(*args, 'in', self.cwd)
        return types.SimpleNamespace(stdout='')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testobj = testee.Check(c)
    assert testobj.get_branchname('path/to/repo') == 'current'
    assert capsys.readouterr().out == 'git branch in path/to/repo\n'
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext(c)
    assert testobj.get_branchname('path/to/repo') == ''
    assert capsys.readouterr().out == 'git branch in path/to/repo\n'
    monkeypatch.setattr(MockContext, 'run', mock_run_3)
    c = MockContext(c)
    assert testobj.get_branchname('path/to/repo') == ''
    assert capsys.readouterr().out == 'git branch in path/to/repo\n'


def test_check_init(monkeypatch):
    """unittest for repo.check_init
    """
    monkeypatch.setattr(testee, 'frozen_repos', ['do-not-process'])
    monkeypatch.setattr(testee, 'all_repos', ['a', 'b'])
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    with pytest.raises(ValueError) as exc:
        testee.Check(c, context='x')
    assert str(exc.value) == 'wrong context for this routine'

    checker = testee.Check(c)
    assert checker.context == 'local'
    assert not checker.push
    assert not checker.verbose
    assert checker.include == ['a', 'b']
    assert checker.exclude == ['do-not-process']
    assert not checker.is_gitrepo
    assert not checker.is_private

    checker = testee.Check(c, context='remote', push=True, verbose=True, include='q,r', exclude='r,s')
    assert checker.context == 'remote'
    assert checker.push
    assert checker.verbose
    assert checker.include == ['q', 'r']
    assert checker.exclude == ['do-not-process', 'r', 's']
    assert not checker.is_gitrepo
    assert not checker.is_private


def test_check_run(monkeypatch, capsys):
    """unittest for repo.check_run

    eigenlijk test op de sturing binnen de run() methode
    """
    monkeypatch.setattr(testee.Check, 'get_locations', lambda *x: ('pwd', 'root'))
    monkeypatch.setattr(testee.Check, 'register_uncommitted', lambda *x: (False, '', ''))
    monkeypatch.setattr(testee.Check, 'register_outgoing', lambda *x: (False, '', ''))
    monkeypatch.setattr(testee, 'all_repos', ['check-it'])
    monkeypatch.setattr(testee, 'git_repos', ['check-it'])
    monkeypatch.setattr(testee, 'private_repos', ['check-it'])
    monkeypatch.setattr(testee, 'TODAY', 'today')
    c = MockContext()
    testee.Check(c).run()
    with open(testee.LOCALCHG) as f:
        data = f.read()
    assert data == 'check local repos on today\n\n'
    assert capsys.readouterr().out == '\nno change details\n'

    testee.Check(c, verbose=True).run()
    with open(testee.LOCALCHG) as f:
        data = f.read()
    assert data == 'check local repos on today\n\n'
    assert capsys.readouterr().out == 'no changes for check-it\n\nno change details\n'

    monkeypatch.setattr(testee.Check, 'register_uncommitted', lambda *x: (True, 'xxx', 'aaa\n'))
    monkeypatch.setattr(testee.Check, 'register_outgoing', lambda *x: (False, '', '\n'))
    testee.Check(c).run()
    with open(testee.LOCALCHG) as f:
        data = f.read()
    assert data == 'check local repos on today\n\naaa\n\n'
    assert capsys.readouterr().out == 'xxx for check-it\n\nfor details see /tmp/repo_local_changes\n'

    monkeypatch.setattr(testee.Check, 'register_uncommitted', lambda *x: (False, '', '\n'))
    monkeypatch.setattr(testee.Check, 'register_outgoing', lambda *x: (True, 'yyy', 'bbb\n'))
    monkeypatch.setattr(testee.Check, 'execute_push', lambda *x: 'ccc')
    testee.Check(c, push=True).run()
    with open(testee.LOCALCHG) as f:
        data = f.read()
    assert data == 'check local repos on today\n\n\nbbb\nccc'
    assert capsys.readouterr().out == ('yyy for check-it\n\n'
                                       'for details see /tmp/repo_local_changes\n')
    monkeypatch.setattr(testee.Check, 'execute_push', lambda *x: '')
    testee.Check(c, push=True).run()
    with open(testee.LOCALCHG) as f:
        data = f.read()
    assert data == 'check local repos on today\n\n\nbbb\n'
    assert capsys.readouterr().out == ('yyy for check-it\n\n'
                                       'for details see /tmp/repo_local_changes\n')

    monkeypatch.setattr(testee.Check, 'register_uncommitted', lambda *x: (True, 'xxx', 'aaa\n'))
    monkeypatch.setattr(testee.Check, 'register_outgoing', lambda *x: (True, 'yyy', 'bbb\n'))
    monkeypatch.setattr(testee, 'all_repos', ['check-it', 'check-not'])
    testee.Check(c, context='remote', exclude='check-not').run()
    with open(testee.REPOCHG) as f:
        data = f.read()
    assert data == 'check remote repos on today\n\naaa\nbbb\n'
    assert capsys.readouterr().out == ('xxx and yyy for check-it\n\n'
                                       'for details see /tmp/repo_changes\n')


def test_get_locations(monkeypatch):
    """unittest for repo.get_locations
    """
    monkeypatch.setattr(testee, 'HOME', 'homedir')
    monkeypatch.setattr(testee, 'git_repos', ['name'])
    monkeypatch.setattr(testee, 'private_repos', {'name': 'same_or_other_name'})
    # monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testobj = testee.Check(c, 'local')
    testobj.is_gitrepo, testobj.is_private = True, True
    assert testobj.get_locations('name') == ('homedir/same_or_other_name', 'homedir')
    testobj.is_gitrepo, testobj.is_private = True, False
    assert testobj.get_locations('name') == ('homedir/projects/name', 'homedir')
    testobj.is_gitrepo, testobj.is_private = False, True
    assert testobj.get_locations('name') == ('homedir/same_or_other_name', 'homedir')
    testobj.is_gitrepo, testobj.is_private = False, False
    assert testobj.get_locations('name') == ('homedir/projects/name', 'homedir')
    c = MockContext()
    testobj = testee.Check(c, 'remote')
    testobj.is_gitrepo, testobj.is_private = True, True
    assert testobj.get_locations('name') == ('homedir/git-repos/name', 'homedir/git-repos')
    testobj.is_gitrepo, testobj.is_private = True, False
    assert testobj.get_locations('name') == ('homedir/git-repos/name', 'homedir/git-repos')
    testobj.is_gitrepo, testobj.is_private = False, True
    assert testobj.get_locations('name') == ('homedir/git-repos/name', 'homedir/git-repos')
    testobj.is_gitrepo, testobj.is_private = False, False
    assert testobj.get_locations('name') == ('homedir/hg_repos/name', 'homedir/hg_repos')


def test_register_changes(monkeypatch, capsys):
    """unittest for repo.register_changes
    """
    def mock_run(c, *args, **kwargs):
        """stub
        """
        print(*args)
        return types.SimpleNamespace(stdout='xxx')
    def mock_run_2(c, *args, **kwargs):
        """stub
        """
        print(*args)
        return types.SimpleNamespace(stdout='')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    monkeypatch.setattr(testee.Check, 'get_branchname', lambda *x: 'master')
    testobj = testee.Check(c)
    testobj.is_gitrepo, testobj.is_private = True, True
    assert testobj.register_uncommitted('pwd') == (True,
            'uncommitted changes (on branch master)',
            '\nuncommitted changes in pwd (on branch master)\nxxx\n')
    assert capsys.readouterr().out == 'git status -uno --short\n'
    testobj.is_gitrepo, testobj.is_private = True, False
    assert testobj.register_uncommitted('pwd') == (True,
            'uncommitted changes (on branch master)',
            '\nuncommitted changes in pwd (on branch master)\nxxx\n')
    assert capsys.readouterr().out == 'git status -uno --short\n'
    testobj.is_gitrepo, testobj.is_private = False, False
    assert testobj.register_uncommitted('pwd') == (True,
            'uncommitted changes',
            '\nuncommitted changes in pwd\nxxx\n')
    assert capsys.readouterr().out == 'hg status --quiet\n'
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    testobj = testee.Check(c)
    testobj.is_gitrepo, testobj.is_private = False, True
    assert testobj.register_uncommitted('pwd') == (False, '', '')
    assert capsys.readouterr().out == 'git status -uno --short\n'


def test_register_outgoing(monkeypatch, capsys):
    """unittest for repo.register_outgoing
    """
    def mock_run(c, *args, **kwargs):
        """stub
        """
        print(*args)
        return types.SimpleNamespace(stdout='xxx', ok=True)
    counter = 0
    def mock_run_2(c, *args, **kwargs):
        """stub
        """
        nonlocal counter
        counter += 1
        print(*args)
        action, filename = args[0].split(None, 1)
        if action == 'touch':
            # with open('/tmp/repochecktest/name_tip', 'w'):
            with open(filename, 'w'):
                pass
        return types.SimpleNamespace(stdout='xxx', ok=True)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testobj = testee.Check(c, 'local')
    testobj.is_gitrepo, testobj.is_private = True, True
    assert testobj.register_outgoing('name', 'root', 'pwd') == ('xxx', 'outgoing changes',
                                                                'outgoing changes for name\nxxx\n')
    assert capsys.readouterr().out == 'git log origin/master..master\n'
    testobj.is_gitrepo, testobj.is_private = False, True
    assert testobj.register_outgoing('name', 'root', 'pwd') == ('xxx', 'outgoing changes',
                                                                'outgoing changes for name\nxxx\n')
    assert capsys.readouterr().out == 'git log origin/master..master\n'
    testobj.is_gitrepo, testobj.is_private = True, False
    assert testobj.register_outgoing('name', 'root', 'pwd') == ('xxx', 'outgoing changes',
                                                                'outgoing changes for name\nxxx\n')
    assert capsys.readouterr().out == 'git log origin/master..master\n'
    testobj.is_gitrepo, testobj.is_private = False, False
    assert testobj.register_outgoing('name', 'root', 'pwd') == (True, 'outgoing changes',
                                                                'outgoing changes for name\nxxx\n')
    assert capsys.readouterr().out == 'hg outgoing\n'
    testobj = testee.Check(c, 'remote')
    testobj.is_gitrepo, testobj.is_private = True, True
    assert testobj.register_outgoing('name', 'root', 'pwd') == ('xxx', 'outgoing changes',
                                                                'outgoing changes for name\nxxx\n')
    assert capsys.readouterr().out == 'git log origin/master..master\n'
    testobj.is_gitrepo, testobj.is_private = True, False
    assert testobj.register_outgoing('name', 'root', 'pwd') == ('xxx', 'outgoing changes',
                                                                'outgoing changes for name\nxxx\n')
    assert capsys.readouterr().out == 'git log origin/master..master\n'
    testobj.is_gitrepo, testobj.is_private = False, True
    assert testobj.register_outgoing('name', 'root', 'pwd') == ('xxx', 'outgoing changes',
                                                                'outgoing changes for name\nxxx\n')
    assert capsys.readouterr().out == 'git log origin/master..master\n'

    if not os.path.exists('/tmp/repochecktest'):
        os.mkdir('/tmp/repochecktest')
    with open('/tmp/repochecktest/name_tip', 'w') as f:
        f.write('x')
    with open('/tmp/name_tip', 'w') as f:
        f.write('x')
    testobj.is_gitrepo, testobj.is_private = False, False
    assert testobj.register_outgoing('name', '/tmp/repochecktest', 'pwd') == (False, '', '')
    assert capsys.readouterr().out == 'hg tip > /tmp/name_tip\n'
    os.remove('/tmp/repochecktest/name_tip')
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    testobj = testee.Check(c, 'remote')
    testobj.is_gitrepo, testobj.is_private = False, False
    # breakpoint()
    assert testobj.register_outgoing('name', '/tmp/repochecktest', 'pwd') == (True,
            'outgoing changes',
            'outgoing changes for name\n-- local:\nx\n-- remote:\n\n')
    assert capsys.readouterr().out == 'touch /tmp/repochecktest/name_tip\nhg tip > /tmp/name_tip\n'


def test_execute_push(monkeypatch, capsys):
    """unittest for repo.execute_push
    """
    def mock_run(c, *args, **kwargs):
        """stub
        """
        print(*args)
        return types.SimpleNamespace(stdout='ready.', ok=True)
    def mock_run_2(c, *args, **kwargs):
        """stub
        """
        print(*args)
        return types.SimpleNamespace(stdout='ready.', ok=False)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testobj = testee.Check(c, 'local')
    testobj.is_gitrepo, testobj.is_private = True, True
    assert testobj.execute_push('name', 'root', 'pwd') == 'ready.\n'
    assert capsys.readouterr().out == 'git push  origin master\n'
    testobj.is_gitrepo, testobj.is_private = False, True
    assert testobj.execute_push('name', 'root', 'pwd') == 'ready.\n'
    assert capsys.readouterr().out == 'git push  origin master\n'
    testobj.is_gitrepo, testobj.is_private = True, False
    assert testobj.execute_push('name', 'root', 'pwd') == 'ready.\n'
    assert capsys.readouterr().out == 'git push  origin master\n'
    testobj.is_gitrepo, testobj.is_private = False, False
    assert testobj.execute_push('name', 'root', 'pwd') == 'ready.\nready.\n'
    assert capsys.readouterr().out == 'hg push\nhg up\n'
    testobj = testee.Check(c, 'remote')
    testobj.is_gitrepo, testobj.is_private = True, True
    assert testobj.execute_push('name', 'root', 'pwd') == 'ready.\n'
    assert capsys.readouterr().out == 'git push -u origin master\n'
    testobj.is_gitrepo, testobj.is_private = False, True
    assert testobj.execute_push('name', 'root', 'pwd') == 'ready.\n'
    assert capsys.readouterr().out == 'git push -u origin master\n'
    testobj.is_gitrepo, testobj.is_private = True, False
    assert testobj.execute_push('name', 'root', 'pwd') == 'ready.\n'
    assert capsys.readouterr().out == 'git push -u origin master\n'
    testobj.is_gitrepo, testobj.is_private = False, False
    assert testobj.execute_push('name', 'root', 'pwd') == 'ready.\n'
    assert capsys.readouterr().out == 'hg push\nhg tip > root/name_tip\n'
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    testobj = testee.Check(c, 'local')
    testobj.is_gitrepo, testobj.is_private = True, True
    assert testobj.execute_push('name', 'root', 'pwd') == ''
    assert capsys.readouterr().out == 'git push  origin master\n'


def test_get_tipfilename():
    """unittest for repo.get_tipfilename
    """
    c = MockContext()
    testobj = testee.Check(c)
    assert testobj.get_tipfilename('root', 'name') == 'root/name_tip'


def test_check_local(monkeypatch, capsys):
    """unittest for repo.check_local
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    monkeypatch.setattr(MockCheck, 'run', mock_check_nok)
    monkeypatch.setattr(testee, 'Check', MockCheck)
    testee.check_local(c)
    assert capsys.readouterr().out == "call Check() with args () {}\ncall Check.run()\n"
    monkeypatch.setattr(testee.Check, 'run', mock_check_ok)
    monkeypatch.setattr(testee, 'Check', MockCheck)
    testee.check_local(c)
    assert capsys.readouterr().out == ("call Check() with args () {}\ncall Check.run()\n"
                                       "use 'check-repo <reponame>' to inspect changes\n"
                                       "    'binfab repo.check-local-changes` (or `repolog`)"
                                       " for log\n"
                                       "    'binfab repo.check-local-notes` for remarks\n")


def test_check_local_changes(monkeypatch, capsys):
    """unittest for repo.check_local_changes
    """
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.check_local_changes(c)
    assert capsys.readouterr().out == ("called run with args"
                                       " ('tview /tmp/repo_local_changes',) {} in ~/projects\n")


def test_check_local_notes(monkeypatch, capsys):
    """unittest for repo.check_local_notes
    """
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    testee.check_local_notes(c)
    assert capsys.readouterr().out == (
            "called run with args ('treedocs projects.trd',) {} in ~/projects\n")


def test_check_remote(monkeypatch, capsys):
    """unittest for repo.check_remote
    """
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    monkeypatch.setattr(testee, 'Check', MockCheck)
    testee.check_remote(c)
    assert capsys.readouterr().out == ("call Check() with args ('remote',) {}\n"
                                       "call Check.run()\n")


def test_push_local(monkeypatch, capsys):
    """unittest for repo.push_local
    """
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    monkeypatch.setattr(testee, 'Check', MockCheck)
    testee.push_local(c)
    assert capsys.readouterr().out == ("call Check() with args () {'push': True, 'exclude': None,"
                                       " 'include': None}\n"
                                       "call Check.run()\n")
    testee.push_local(c, exclude='x,y')
    assert capsys.readouterr().out == ("call Check() with args () {'push': True, 'exclude': 'x,y',"
                                       " 'include': None}\n"
                                       "call Check.run()\n")
    testee.push_local(c, include='x,y')
    assert capsys.readouterr().out == ("call Check() with args () {'push': True, 'exclude': None,"
                                       " 'include': 'x,y'}\n"
                                       "call Check.run()\n")


def test_push_remote(monkeypatch, capsys):
    """unittest for repo.push_remote
    """
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    monkeypatch.setattr(testee, 'Check', MockCheck)
    testee.push_remote(c)
    assert capsys.readouterr().out == ("call Check() with args ('remote',) {'push': True,"
                                       " 'exclude': None, 'include': None}\n"
                                       "call Check.run()\n")
    testee.push_remote(c, exclude='x,y')
    assert capsys.readouterr().out == ("call Check() with args ('remote',) {'push': True,"
                                       " 'exclude': 'x,y', 'include': None}\n"
                                       "call Check.run()\n")
    testee.push_remote(c, include='x,y')
    assert capsys.readouterr().out == ("call Check() with args ('remote',) {'push': True,"
                                       " 'exclude': None, 'include': 'x,y'}\n"
                                       "call Check.run()\n")


def test_overview(monkeypatch, capsys):
    """unittest for repo.overview
    """
    monkeypatch.setattr(testee, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    # testee.overview(c)
    # assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('',"
    #                                    "\"git log --pretty=format:'%ad %s' --date=iso\"\n")
    testee.overview(c, 'name')
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('name',"
                                       " \"git log --pretty=format:'%ad %s' --date=iso\")\n\n")


def test_add2gitweb(monkeypatch, capsys):
    """unittest for repo.add2gitweb
    """
    counter = 0
    def mock_exists(*args):
        """stub
        """
        nonlocal counter
        counter += 1
        if counter < 3:
            return True
        return False
    def mock_exists_2(*args):
        """stub
        """
        nonlocal counter
        counter += 1
        if counter in (1, 3):
            return True
        return False
    counter2 = 0
    def mock_read(*args):
        """stub
        """
        nonlocal counter2
        counter2 += 1
        if counter2 == 1:
            return "Unnamed project"
        return "description"
    def mock_read_2(*args):
        """stub
        """
        nonlocal counter2
        counter2 += 1
        if counter2 == 1:
            return "orig description"
        return "description"
    def mock_get_input(prompt):
        """stub
        """
        print(f'called testee.get_input_from_user with arg `{prompt}`')
        return 'repodesc'
    monkeypatch.setattr(testee, 'get_input_from_user', mock_get_input)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: False)
    testee.add2gitweb(c, 'name')
    assert capsys.readouterr().out == (
        f"called run with args ('touch {testee.GITLOC}/name/.git/git-daemon-export-ok',) {{}}\n"
        'called testee.get_input_from_user with arg `enter short repo description: `\n'
        f'called run with args (\'echo "repodesc" > {testee.GITLOC}/name/.git/description\',) {{}}\n')
    testee.add2gitweb(c, 'name', frozen=True)
    assert capsys.readouterr().out == (
        f"called run with args ('touch {testee.GITLOC}/.frozen/name/.git/git-daemon-export-ok',)"
        " {}\n"
        'called testee.get_input_from_user with arg `enter short repo description: `\n'
        f'called run with args (\'echo "repodesc" > {testee.GITLOC}/.frozen/name/.git/description\',)'
        ' {}\n')
    monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: True)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read)
    testee.add2gitweb(c, 'name')
    assert capsys.readouterr().out == (
        f'called run with args (\'echo "description" > {testee.GITLOC}/name/.git/description\',)'
        ' {}\n')
    counter2 = 0
    monkeypatch.setattr(testee.pathlib.Path, 'exists', mock_exists)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read)
    testee.add2gitweb(c, 'name')
    assert capsys.readouterr().out == (
        'called testee.get_input_from_user with arg `enter short repo description: `\n'
        f'called run with args (\'echo "repodesc" > {testee.GITLOC}/name/.git/description\',)'
        ' {}\n')
    counter = counter2 = 0
    monkeypatch.setattr(testee.pathlib.Path, 'exists', mock_exists)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read_2)
    testee.add2gitweb(c, 'name')
    assert capsys.readouterr().out == ""
    counter = counter2 = 0
    monkeypatch.setattr(testee.pathlib.Path, 'exists', mock_exists_2)
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read_2)
    testee.add2gitweb(c, 'name')
    assert capsys.readouterr().out == (
        f'called run with args (\'echo "orig description" > {testee.GITLOC}/name/.git/description\',)'
        ' {}\n')


def test_get_input_from_user(monkeypatch, capsys):
    """unittest for repo.get_input_from_user
    """
    test_input = StringIO('x\n')
    monkeypatch.setattr('sys.stdin', test_input)
    assert testee.get_input_from_user('prompt') == 'x'


def test_check_and_run(monkeypatch, capsys):
    """unittest for repo.check_and_run
    """
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    c = MockContext()
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    testee.check_and_run_for_project(c, '', 'command-string')
    assert capsys.readouterr().out == 'you are not in a known project directory\n'
    testee.check_and_run_for_project(c, 'name', 'command-string')
    assert capsys.readouterr().out == 'name is not a known project\n'
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: 'path/to/repo')
    testee.check_and_run_for_project(c, 'repo', 'command-string')
    assert capsys.readouterr().out == "called run with args ('command-string',) {} in path/to/repo\n"
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: os.getcwd())
    testee.check_and_run_for_project(c, '', 'command-string')
    assert capsys.readouterr().out == (
            "called run with args ('command-string',) {} in /home/albert/bin\n")


def test_dtree(monkeypatch, capsys):
    """unittest for repo.dtree
    """
    monkeypatch.setattr(testee, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    testee.dtree(c)
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('',"
                                       " '~/projects/doctree/ensure-qt projdocs.trd')\n")
    testee.dtree(c, 'name')
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('name',"
                                       " '~/projects/doctree/ensure-qt projdocs.trd')\n")


def test_rreadme(monkeypatch, capsys):
    """unittest for repo.rreadme
    """
    monkeypatch.setattr(testee, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    testee.rreadme(c)
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('',"
                                       " 'rstview readme.rst')\n")
    testee.rreadme(c, 'name')
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('name',"
                                       " 'rstview readme.rst')\n")


def test_qgit(monkeypatch, capsys):
    """unittest for repo.qgit
    """
    monkeypatch.setattr(testee, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    testee.qgit(c)
    assert capsys.readouterr().out == "call check_and_run_for_project() with args ('', 'qgit')\n"
    testee.qgit(c, 'name')
    assert capsys.readouterr().out == "call check_and_run_for_project() with args ('name', 'qgit')\n"


def test_mee_bezig(monkeypatch, capsys):
    """unittest for repo.mee_bezig
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.mee_bezig(c)
    assert capsys.readouterr().out == (
            "called run with args ('treedocs ~/projects/projects.trd',) {}\n")


def test_preadme(monkeypatch, capsys):
    """unittest for repo.preadme
    """
    monkeypatch.setattr(testee, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    testee.preadme(c)
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('',"
                                       " 'pedit readme.rst')\n")
    testee.preadme(c, 'name')
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('name',"
                                       " 'pedit readme.rst')\n")


def test_predit(monkeypatch, capsys, tmp_path):
    """unittest for repo.predit
    """
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.predit(c, 'testproj', 'testfile')
    assert capsys.readouterr().out == "testproj is not a known project\n"

    (tmp_path / '.rurc').touch()
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: str(tmp_path))
    testee.predit(c, 'testproj', 'testfile')
    assert capsys.readouterr().out == "testproj: testconf is empty\n"

    (tmp_path / '.rurc').write_text("\n[testdir]\ntestdir\n")
    testee.predit(c, 'testproj', 'testfile')
    assert capsys.readouterr().out == "testproj: no testees found\n"

    (tmp_path / '.rurc').write_text("\n\n\n[testees]\ntestfile = testfile.py\ngargl\n")
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: str(tmp_path))
    testee.predit(c, 'testproj', 'testfile')
    assert capsys.readouterr().out == "testproj: no testdir found\n"

    (tmp_path / '.rurc').write_text("[testdir]\ntestdir\n\n\n\n[testees]\ntestfile = testfile.py\n"
                                    "gargl\n")
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: str(tmp_path))
    testee.predit(c, 'testproj', 'testfile')
    assert capsys.readouterr().out == f"called run with args ('pedit {tmp_path}/testfile',) {{}}\n"

    (tmp_path / '.rurc').write_text("[testdir]\ntestdir\n\n\n\n[testees]\n"
                                    "testfile: testdir/testfile.py\ngargl\n")
    testee.predit(c, 'testproj', 'testfile')
    assert capsys.readouterr().out == (
            f"called run with args ('pedit {tmp_path}/testdir/testfile',) {{}}\n")

    (tmp_path / '.rurc').write_text("[testdir]\ntestdir\n\n\n\n[testees]\n"
                                    "testfile - testdir/testfile.py\ngargl\n")
    testee.predit(c, 'testproj', 'testfile')
    assert capsys.readouterr().out == (
            "unsupported delimiter found in line: 'testfile - testdir/testfile.py'\n")


def test_prshell(monkeypatch, capsys):
    """unittest for repo.prshell
    """
    monkeypatch.setattr(testee, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    testee.prshell(c)
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('',"
                                       " 'gnome-terminal --geometry=132x43+4+40')\n")
    testee.prshell(c, 'name')
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ('name',"
                                       " 'gnome-terminal --geometry=132x43+4+40')\n")


def test_rebuild_filenamelist(monkeypatch, capsys, tmp_path):
    """unittest for repo.rebuild_filenamelist
    """
    def mock_get_repofiles(*args):
        """stub
        """
        print(f'called get_repofiles() for `{args[1]}`')
        return 'path_to_repo', ['file2', 'test_file1', 'file1', 'test_file2']
    monkeypatch.setattr(testee, 'FILELIST', str(tmp_path / 'filelist'))
    monkeypatch.setattr(testee, 'all_repos', ['repo1', 'repo2'])
    monkeypatch.setattr(testee, 'frozen_repos', ['repo2'])
    monkeypatch.setattr(testee, 'get_repofiles', mock_get_repofiles)
    c = MockContext()
    testee.rebuild_filenamelist(c, 'prog')
    with open(f'{testee.FILELIST}-prog') as f:
        data = f.read()
    assert data == 'path_to_repo/file1\npath_to_repo/file2\n'
    assert capsys.readouterr().out == 'called get_repofiles() for `repo1`\n'
    testee.rebuild_filenamelist(c, mode='test')
    with open(f'{testee.FILELIST}-test') as f:
        data = f.read()
    assert data == 'path_to_repo/test_file1\npath_to_repo/test_file2\n'
    assert capsys.readouterr().out == 'called get_repofiles() for `repo1`\n'
    testee.rebuild_filenamelist(c, 'x')
    with open(f'{testee.FILELIST}-x') as f:
        data = f.read()
    assert data == ('path_to_repo/file1\npath_to_repo/file2\n'
                    'path_to_repo/test_file1\npath_to_repo/test_file2\n')
    assert capsys.readouterr().out == 'called get_repofiles() for `repo1`\n'


def test_search_p(monkeypatch, capsys):
    """unittest for repo.search_p
    """
    def mock_search(c, *args):
        """stub
        """
        print('called search with args', args)
    monkeypatch.setattr(testee, 'search', mock_search)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.search_p(c, rebuild=True)
    assert capsys.readouterr().out == "called search with args ('', True, 'prog')\n"
    testee.search_p(c, 'find_me')
    assert capsys.readouterr().out == "called search with args ('find_me', False, 'prog')\n"


def test_search_t(monkeypatch, capsys):
    """unittest for repo.search_t
    """
    def mock_search(c, *args):
        """stub
        """
        print('called search with args', args)
    monkeypatch.setattr(testee, 'search', mock_search)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.search_t(c, rebuild=True)
    assert capsys.readouterr().out == "called search with args ('', True, 'test')\n"
    testee.search_t(c, 'find_me')
    assert capsys.readouterr().out == "called search with args ('find_me', False, 'test')\n"


def test_search_all(monkeypatch, capsys):
    """unittest for repo.search_all
    """
    def mock_search(c, *args):
        """stub
        """
        print('called search with args', args)
    monkeypatch.setattr(testee, 'search', mock_search)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.search_all(c, rebuild=True)
    assert capsys.readouterr().out == "called search with args ('', True, 'both')\n"
    testee.search_all(c, 'find_me')
    assert capsys.readouterr().out == "called search with args ('find_me', False, 'both')\n"


def test_search(monkeypatch, capsys, tmp_path):
    """unittest for repo.search
    """
    def mock_rebuild(*args):
        """stub
        """
        print('called rebuild_filenamelist')
    tmpfilelist = tmp_path / 'filelist'
    monkeypatch.setattr(testee, 'FILELIST', str(tmpfilelist))
    monkeypatch.setattr(testee, 'rebuild_filenamelist', mock_rebuild)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.search(c)
    assert capsys.readouterr().out == (
            'called rebuild_filenamelist\n'
            f"called run with args ('afrift -l {tmpfilelist}-both -e py -Q',) {{}}\n")
    testee.search(c, rebuild=True)
    assert capsys.readouterr().out == (
            'called rebuild_filenamelist\n'
            f"called run with args ('afrift -l {tmpfilelist}-both -e py -Q',) {{}}\n")
    testee.search(c, 'name', mode='test')
    assert capsys.readouterr().out == (
            'called rebuild_filenamelist\n'
            f"called run with args ('afrift -l {tmpfilelist}-test -e py -QN -s name',) {{}}\n")
    testee.search(c, 'name', rebuild=True, mode='prog')
    assert capsys.readouterr().out == (
            'called rebuild_filenamelist\n'
            f"called run with args ('afrift -l {tmpfilelist}-prog -e py -QN -s name',) {{}}\n")
    with open(f'{testee.FILELIST}-both', 'w') as f:
        f.write('')
    testee.search(c)
    assert capsys.readouterr().out == (
            f"called run with args ('afrift -l {tmpfilelist}-both -e py -Q',) {{}}\n")
    testee.search(c, rebuild=True)
    assert capsys.readouterr().out == (
            'called rebuild_filenamelist\n'
            f"called run with args ('afrift -l {tmpfilelist}-both -e py -Q',) {{}}\n")
    testee.search(c, 'name')
    assert capsys.readouterr().out == (
            f"called run with args ('afrift -l {tmpfilelist}-both -e py -QN -s name',) {{}}\n")
    testee.search(c, 'name', rebuild=True)
    assert capsys.readouterr().out == (
            'called rebuild_filenamelist\n'
            f"called run with args ('afrift -l {tmpfilelist}-both -e py -QN -s name',) {{}}\n")


def test_runtests(monkeypatch, capsys):
    """unittest for repo.runtests
    """
    monkeypatch.setattr(testee, 'check_and_run_for_project', mock_check_and_run)
    c = MockContext()
    with pytest.raises(TypeError) as exc:
        testee.runtests(c)
    assert str(exc.value) == "runtests() missing 1 required positional argument: 'name'"
    testee.runtests(c, 'name')
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args"
                                       " ('name', 'run_unittests ')\n")
    testee.runtests(c, 'name', 'test')
    assert capsys.readouterr().out == ("call check_and_run_for_project() with args ("
                                       "'name', 'run_unittests test')\n")


def test_find_failing_tests(monkeypatch, capsys):
    """unittest for repo.find_failing_tests
    """
    testee.all_repos = ['xxx', 'yyy', 'zzz']
    testee.frozen_repos = ['yyy']
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.find_failing_tests(c)
    assert capsys.readouterr().out == (
            "=== running tests for xxx\n"
            "called run with args ('run-unittests -p xxx all | grep ^FAILED',) {'warn': True}\n"
            "=== running tests for zzz\n"
            "called run with args ('run-unittests -p zzz all | grep ^FAILED',) {'warn': True}\n")
    testee.find_failing_tests(c, 'xxx')
    assert capsys.readouterr().out == (
            "=== running tests for xxx\n"
            "called run with args ('run-unittests -p xxx all | grep ^FAILED',) {'warn': True}\n")
    testee.find_failing_tests(c, 'xxx,yyy')
    assert capsys.readouterr().out == (
            "=== running tests for xxx\n"
            "called run with args ('run-unittests -p xxx all | grep ^FAILED',) {'warn': True}\n")


def test_find_test_errors(monkeypatch, capsys):
    """unittest for repo.find_test_errors
    """
    testee.all_repos = ['xxx', 'yyy', 'zzz']
    testee.frozen_repos = ['yyy']
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.find_test_errors(c)
    assert capsys.readouterr().out == (
            "=== running tests for xxx\n"
            "called run with args ('run-unittests -p xxx all | grep -B 2 ^ERROR',) {'warn': True}\n"
            "=== running tests for zzz\n"
            "called run with args ('run-unittests -p zzz all | grep -B 2 ^ERROR',) {'warn': True}\n")
    testee.find_test_errors(c, 'xxx')
    assert capsys.readouterr().out == (
            "=== running tests for xxx\n"
            "called run with args ('run-unittests -p xxx all | grep -B 2 ^ERROR',) {'warn': True}\n")
    testee.find_test_errors(c, 'xxx,yyy')
    assert capsys.readouterr().out == (
            "=== running tests for xxx\n"
            "called run with args ('run-unittests -p xxx all | grep -B 2 ^ERROR',) {'warn': True}\n")


def test_find_gui_test_errors(monkeypatch, capsys, tmp_path):
    """unittest for repo.find_test_errors
    """
    # def mock_exists(self):
    #     print(f'called path.exists with arg {self}')
    #     return False
    # def mock_exists(self):
    #     print(f'called path.exists with arg {self}')
    #     return True
    monkeypatch.setattr(testee, 'PROJECTS_BASE', tmp_path)
    monkeypatch.setattr(testee, 'non_web_repos', ['qqq', 'rrr'])
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.find_gui_test_errors(c, 'xxx')
    assert capsys.readouterr().out == "invalid toolkit name\n"
    (tmp_path / 'rrr').mkdir()
    (tmp_path / 'rrr' / '.rurc').touch()
    testee.find_gui_test_errors(c, 'wx')
    assert capsys.readouterr().out == ""
    (tmp_path / 'rrr' / '.rurc').write_text('oink\n\n[testscripts]\ngui_wx\nqt_gui\ntkgui\n\nzz.py')
    testee.find_gui_test_errors(c, 'wx')
    assert capsys.readouterr().out == (
        "=== running tests for rrr gui_wx\n"
        "called run with args ('run-unittests -p rrr gui_wx | grep -B 2 ^ERROR',) {'warn': True}\n"
        "called run with args ('run-unittests -p rrr gui_wx | grep ^FAILED',) {'warn': True}\n")
    (tmp_path / 'qqq').mkdir()
    (tmp_path / 'qqq' / '.rurc') .write_text("oink\n\n[testscripts]\ngui_wx\nqt_gui\ntkgui\n"
                                             "[testees]\ncc.py")
    testee.find_gui_test_errors(c, 'tk')
    assert capsys.readouterr().out == (
        "=== running tests for qqq tkgui\n"
        "called run with args ('run-unittests -p qqq tkgui | grep -B 2 ^ERROR',) {'warn': True}\n"
        "called run with args ('run-unittests -p qqq tkgui | grep ^FAILED',) {'warn': True}\n"
        "=== running tests for rrr tkgui\n"
        "called run with args ('run-unittests -p rrr tkgui | grep -B 2 ^ERROR',) {'warn': True}\n"
        "called run with args ('run-unittests -p rrr tkgui | grep ^FAILED',) {'warn': True}\n")
    testee.find_gui_test_errors(c, 'qt')
    assert capsys.readouterr().out == (
        "=== running tests for qqq qt_gui\n"
        "called run with args ('run-unittests -p qqq qt_gui | grep -B 2 ^ERROR',) {'warn': True}\n"
        "called run with args ('run-unittests -p qqq qt_gui | grep ^FAILED',) {'warn': True}\n"
        "=== running tests for rrr qt_gui\n"
        "called run with args ('run-unittests -p rrr qt_gui | grep -B 2 ^ERROR',) {'warn': True}\n"
        "called run with args ('run-unittests -p rrr qt_gui | grep ^FAILED',) {'warn': True}\n"
        "=== running tests for albumsgui main\n"
        "called run with args"
        " ('run-unittests -p albumsgui main | grep -B 2 ^ERROR',) {'warn': True}\n"
        "called run with args ('run-unittests -p albumsgui main | grep ^FAILED',) {'warn': True}\n"
        "=== running tests for albumsgui matcher\n"
        "called run with args"
        " ('run-unittests -p albumsgui matcher | grep -B 2 ^ERROR',) {'warn': True}\n"
        "called run with args ('run-unittests -p albumsgui matcher | grep ^FAILED',) {'warn': True}\n"
        "=== running tests for albumsgui smallgui\n"
        "called run with args"
        " ('run-unittests -p albumsgui smallgui | grep -B 2 ^ERROR',) {'warn': True}\n"
        "called run with args"
        " ('run-unittests -p albumsgui smallgui | grep ^FAILED',) {'warn': True}\n"
        "=== running tests for scripts check\n"
        "called run with args ('run-unittests -p scripts check | grep -B 2 ^ERROR',) {'warn': True}\n"
        "called run with args ('run-unittests -p scripts check | grep ^FAILED',) {'warn': True}\n")


def test_find_test_stats(monkeypatch, capsys):
    """unittest for repo.find_test_stats
    """
    testee.all_repos = ['xxx', 'yyy', 'zzz']
    testee.frozen_repos = ['yyy']
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.find_test_stats(c)
    assert capsys.readouterr().out == (
            "=== running tests for xxx\n"
            "called run with args ('run-unittests -p xxx all | grep -A 2 ^Name',) {'warn': True}\n"
            "=== running tests for zzz\n"
            "called run with args ('run-unittests -p zzz all | grep -A 2 ^Name',) {'warn': True}\n")
    testee.find_test_stats(c, 'xxx')
    assert capsys.readouterr().out == (
            "=== running tests for xxx\n"
            "called run with args ('run-unittests -p xxx all | grep -A 2 ^Name',) {'warn': True}\n")
    testee.find_test_stats(c, 'xxx,yyy')
    assert capsys.readouterr().out == (
            "=== running tests for xxx\n"
            "called run with args ('run-unittests -p xxx all | grep -A 2 ^Name',) {'warn': True}\n")


def test_list_branches(monkeypatch, capsys):
    """unittest for repo.find_failing_tests
    """
    def mock_get(arg):
        print(f'called get_project_dir with arg {arg}')
        return arg
    testee.all_repos = ['xxx', 'yyy', 'zzz']
    testee.frozen_repos = ['yyy']
    monkeypatch.setattr(MockContext, 'run', run_in_dir)
    monkeypatch.setattr(testee, 'get_project_dir', mock_get)
    c = MockContext()
    testee.list_branches(c)
    assert capsys.readouterr().out == (
            "called get_project_dir with arg xxx\n"
            "branches for project xxx\n"
            "called run with args ('git branch',) {} in xxx\n"
            "called get_project_dir with arg zzz\n"
            "branches for project zzz\n"
            "called run with args ('git branch',) {} in zzz\n")
    testee.list_branches(c, 'xxx')
    assert capsys.readouterr().out == (
            "called get_project_dir with arg xxx\n"
            "branches for project xxx\n"
            "called run with args ('git branch',) {} in xxx\n")
    testee.list_branches(c, 'xxx,yyy')
    assert capsys.readouterr().out == (
            "called get_project_dir with arg xxx\n"
            "branches for project xxx\n"
            "called run with args ('git branch',) {} in xxx\n")


def test_new_predit(monkeypatch, capsys, tmp_path):
    """unittest for repo.predit
    """
    def mock_check(*args):
        print('called check_args with args', args)
        return
    def mock_check_2(*args):
        print('called check_args with args', args)
        (tmp_path / '.sessionrc').write_text("[env]\nmnem1 = xxx yyy\nmnem2 = aaa bbb")
        (tmp_path / '.rurc').write_text("[testdir]\ntestroot\n\n[testscripts]\ntestfile ="
                                        " testfile.py\n[testees]\ntestfile = src/file_to_test.py\n")
        conf = testee.configparser.ConfigParser()
        conf.read(str(tmp_path / '.sessionrc'))
        testconf = testee.configparser.ConfigParser(allow_no_value=True)
        testconf.read(str(tmp_path / '.rurc'))
        return str(tmp_path), 'testroot', conf, testconf
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    monkeypatch.setattr(testee, 'check_args', mock_check)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()

    testee.new_predit(c, 'testproj', 'testfile')
    monkeypatch.setattr(testee, 'check_args', mock_check_2)
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'testfile', False)\n")
    testee.new_predit(c, 'testproj', 'testfile')
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'testfile', False)\n"
            "called run with args ('pedit src/file_to_test.py',) {}\n")

    testee.new_predit(c, 'testproj', 'testfile', True)
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'testfile', True)\n"
            "called run with args ('pedit -r testroot/testfile.py',) {}\n")

    testee.new_predit(c, 'testproj', 'mnem1')
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'mnem1', False)\n"
            "called run with args ('pedit -r xxx yyy',) {}\n")

    testee.new_predit(c, 'testproj', 'mnem2', True)
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'mnem2', True)\n"
            "called run with args ('pedit -r aaa bbb',) {}\n")

    testee.new_predit(c, 'testproj', 'path/to/file')
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'path/to/file', False)\n"
            "called run with args ('pedit path/to/file',) {}\n")


def test_new_prfind(monkeypatch, capsys, tmp_path):
    """unittest for repo.prfind
    """
    def mock_check(*args):
        print('called check_args with args', args)
        return
    def mock_check_2(*args):
        print('called check_args with args', args)
        (tmp_path / '.sessionrc').write_text("[env]\nmnem1 = xxx yyy\nmnem2 = aaa bbb")
        (tmp_path / '.rurc').write_text("[testdir]\ntestroot\n\n[testscripts]\ntestfile ="
                                        " testfile.py\n[testees]\ntestfile = src/file_to_test.py\n")
        conf = testee.configparser.ConfigParser()
        conf.read(str(tmp_path / '.sessionrc'))
        testconf = testee.configparser.ConfigParser(allow_no_value=True)
        testconf.read(str(tmp_path / '.rurc'))
        return str(tmp_path), 'testroot', conf, testconf
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    monkeypatch.setattr(testee, 'check_args', mock_check)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()

    testee.new_prfind(c, 'testproj', 'testfile')
    monkeypatch.setattr(testee, 'check_args', mock_check_2)
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'testfile', False)\n")
    testee.new_prfind(c, 'testproj', 'testfile')
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'testfile', False)\n"
            "called run with args ('afrift -P src/file_to_test.py',) {}\n")

    testee.new_prfind(c, 'testproj', 'testfile', True)
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'testfile', True)\n"
            "called run with args ('afrift -P testroot/testfile.py',) {}\n")

    testee.new_prfind(c, 'testproj', 'mnem1')
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'mnem1', False)\n"
            "called run with args ('afrift -P xxx yyy',) {}\n")

    testee.new_prfind(c, 'testproj', 'mnem2', True)
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'mnem2', True)\n"
            "called run with args ('afrift -P aaa bbb',) {}\n")

    testee.new_prfind(c, 'testproj', 'path/to/file')
    assert capsys.readouterr().out == (
            "called check_args with args ('testproj', 'path/to/file', False)\n"
            "called run with args ('afrift -P path/to/file',) {}\n")


def test_check_args(monkeypatch, capsys, tmp_path):
    """unittest for repo.check_args
    """
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    assert not testee.check_args('testproj', 'testfile', 'x')
    assert capsys.readouterr().out == "testproj is not a known project\n"

    monkeypatch.setattr(testee, 'get_project_dir', lambda x: str(tmp_path))
    assert not testee.check_args('testproj', 'testfile', 'x')
    assert capsys.readouterr().out == "could not find session configuration\n"

    (tmp_path / '.sessionrc').touch()
    assert not testee.check_args('testproj', 'testfile', 'x')
    assert capsys.readouterr().out == "could not find session configuration\n"

    (tmp_path / '.sessionrc').write_text("[env]\n\n[options]")
    assert not testee.check_args('testproj', 'testfile', 'x')
    assert capsys.readouterr().out == "could not find test configuration\n"

    (tmp_path / '.rurc').touch()
    assert not testee.check_args('testproj', 'testfile', 'x')
    assert capsys.readouterr().out == "could not find test configuration\n"
    (tmp_path / '.rurc').write_text("[testscripts]\ntestfile = testfile.py\n"
                                    "[testees]\ntestfile = src/file_to_test.py\n")
    assert not testee.check_args('testproj', 'testfile', 'x')
    assert capsys.readouterr().out == "testdir not configured in test configuration\n"
    (tmp_path / '.rurc').write_text("[testdir]\n\n\n[testscripts]\ntestfile = testfile.py\n"
                                    "[testees]\ntestfile = src/file_to_test.py\n")
    assert not testee.check_args('testproj', 'testfile', 'x')
    assert capsys.readouterr().out == "testdir not configured in test configuration\n"

    (tmp_path / '.sessionrc').write_text("[env]\nmnem1 = xxx yyy\nmnem2 = aaa bbb")
    (tmp_path / '.rurc').write_text("[testdir]\ntestroot\n\n[testscripts]\ntestfile = testfile.py\n"
                                    "[testees]\ntestfile = src/file_to_test.py\n")
    assert not testee.check_args('testproj', '?', 'x')
    assert capsys.readouterr().out == "possible mnemonics are: ['mnem1', 'mnem2', 'testfile']\n"
    result = testee.check_args('testproj', 'testfile', 'x')
    assert result[:2] == (f'{tmp_path}', 'testroot')
    assert isinstance(result[2], testee.configparser.ConfigParser)
    section1 = result[2].sections()[0]
    assert section1 == 'env'
    option1, option2 = result[2].options(section1)
    assert (option1, option2) == ('mnem1', 'mnem2')
    assert result[2][section1][option1] == 'xxx yyy'
    assert result[2][section1][option2] == 'aaa bbb'
    assert isinstance(result[3], testee.configparser.ConfigParser)
    section1, section2, section3 = result[3].sections()
    assert (section1, section2, section3) == ('testdir', 'testscripts', 'testees')
    option = result[3].options(section1)[0]
    assert option == 'testroot'
    assert result[3][section1][option] is None
    option = result[3].options(section2)[0]
    assert option == 'testfile'
    assert result[3][section2][option] == 'testfile.py'
    option = result[3].options(section3)[0]
    assert option == 'testfile'
    assert result[3][section3][option] == 'src/file_to_test.py'

    pwd = os.getcwd()
    os.chdir(tmp_path)
    assert testee.check_args('.', 'testfile', 'x') == result
    os.chdir(pwd)

def test_setgui(monkeypatch, capsys, tmp_path):
    """unittest for repo.setgui
    """
    monkeypatch.setattr(testee, 'get_project_dir', lambda x: '')
    monkeypatch.setattr(MockContext, 'run', mock_run)  # not that we need it
    c = MockContext()

    testee.setgui(c, 'testproj', 'x')
    assert capsys.readouterr().out == "testproj is not a known project\n"

    monkeypatch.setattr(testee, 'get_project_dir', lambda x: str(tmp_path))
    monkeypatch.setattr(testee, 'gui_choices', ['xx', 'yy', '?'])
    testee.setgui(c, 'testproj', 'x')
    assert capsys.readouterr().out == (
            "invalid gui toolkit specification, possible values are ['xx', 'yy', '?']\n")

    (tmp_path / '.rurc').touch()
    testee.setgui(c, 'testproj', '?')
    assert capsys.readouterr().out == "incomplete project configuration\n"

    (tmp_path / 'src').mkdir()
    (tmp_path / '.rurc').write_text("[testscripts]\ntestfile = testfile.py\n"
                                    "[testees]\ntestfile = src/file_to_test.py\n")
    testee.setgui(c, 'testproj', '?')
    assert capsys.readouterr().out == (
            "testproj is not a gui project or does not support toolkit switching\n")

    (tmp_path / 'src' / 'toolkit.py').touch()
    testee.setgui(c, 'testproj', '?')
    assert capsys.readouterr().out == (
            "testproj is not a gui project or does not support toolkit switching\n")

    (tmp_path / 'src' / 'toolkit.py').write_text('\ntoolkit xx\n')
    with pytest.raises(IndexError):
        testee.setgui(c, 'testproj', '?')
    # assert capsys.readouterr().out == "\n"

    (tmp_path / 'src' / 'toolkit.py').write_text("toolkit = 'xx'\n")
    testee.setgui(c, 'testproj', '?')
    assert capsys.readouterr().out == "toolkit for testproj is currently 'xx'\n"

    (tmp_path / 'src' / 'toolkit.py').unlink()
    (tmp_path / 'src' / 'settings.py').touch()
    testee.setgui(c, 'testproj', '?')
    assert capsys.readouterr().out == (
            "testproj is not a gui project or does not support toolkit switching\n")

    (tmp_path / 'src' / 'settings.py').write_text("toolkit = 'xx'\n")
    testee.setgui(c, 'testproj', '?')
    assert capsys.readouterr().out == "toolkit for testproj is currently 'xx'\n"

    testee.setgui(c, 'testproj', 'yy')
    assert capsys.readouterr().out == "changed toolkit for testproj to 'yy'\n"

    oldcwd = os.getcwd()
    os.chdir(tmp_path)
    testee.setgui(c, '.', '?')
    assert capsys.readouterr().out == f"toolkit for {tmp_path.stem} is currently 'yy'\n"
    os.chdir(oldcwd)
