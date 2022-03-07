import pytest
from invoke import MockContext
import repo


def mock_run(self, *args):
    print(*args)


def test_add2gitweb(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    repo.add2gitweb(c, 'name')
    assert capsys.readouterr().out == 'sudo ln -s /home/albert/git_repos/name/.git one.git\n'
    repo.add2gitweb(c, 'name', frozen=True)
    assert capsys.readouterr().out == 'sudo ln -s /home/albert/git_repos/.frozen/name/.git name.git\n'


