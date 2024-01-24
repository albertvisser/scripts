"""unittests for ./settings.py
"""
import settings


def test_get_project_root(monkeypatch):
    """unittest for settings.get_project_root
    """
    monkeypatch.setattr(settings, 'private_repos', {'name': 'private_name'})
    monkeypatch.setattr(settings, 'git_repos', ['git-repo'])
    monkeypatch.setattr(settings, 'sf_repos', ['sf-repo'])
    monkeypatch.setattr(settings, 'PROJECTS_BASE', 'home/base')
    assert str(settings.get_project_root('name')) == 'home'
    assert str(settings.get_project_root('private_name')) == 'home'
    assert str(settings.get_project_root('git-repo')) == 'home/base'
    assert str(settings.get_project_root('sf-repo')) == 'home/base'
    assert str(settings.get_project_root('hg-repo')) == 'home/base'
    assert str(settings.get_project_root('name', 'remote')) == 'home/git-repos'
    assert str(settings.get_project_root('git-repo', 'remote')) == 'home/git-repos'
    assert str(settings.get_project_root('sf-repo', 'remote')) == 'home/sf_repos'
    assert str(settings.get_project_root('hg-repo', 'remote')) == 'home/hg_repos'
    assert str(settings.get_project_root('name', 'sf')) == 'n/a'
    assert str(settings.get_project_root('git-repo', 'sf')) == 'n/a'
    assert str(settings.get_project_root('sf-repo', 'sf')) == 'home/sf_repos'
    assert str(settings.get_project_root('hg-repo', 'sf')) == 'n/a'
    assert str(settings.get_project_root('name', 'git')) == 'home/git-repos'
    assert str(settings.get_project_root('git-repo', 'git')) == 'home/git-repos'
    assert str(settings.get_project_root('sf-repo', 'git')) == 'n/a'
    assert str(settings.get_project_root('hg-repo', 'git')) == 'n/a'
    assert str(settings.get_project_root('name', 'bb')) == 'home/hg_private'
    assert str(settings.get_project_root('git-repo', 'bb')) == 'n/a'
    assert str(settings.get_project_root('sf-repo', 'bb')) == 'n/a'
    assert str(settings.get_project_root('hg-repo', 'bb')) == 'home/hg_repos'


def test_get_project_dir(monkeypatch):
    """unittest for settings.get_project_dir
    """
    def mock_get_root(name):
        """stub for settings.get_project_root
        """
        return 'path/to'
    monkeypatch.setattr(settings, 'get_project_root', mock_get_root)
    monkeypatch.setattr(settings, 'private_repos', {'name': 'private_name'})
    monkeypatch.setattr(settings.os.path, 'exists', lambda x: True)
    assert settings.get_project_dir('project') == 'path/to/project'
    assert settings.get_project_dir('name') == 'path/to/private_name'
    monkeypatch.setattr(settings.os.path, 'exists', lambda x: False)
    assert settings.get_project_dir('project') == ''
    assert settings.get_project_dir('name') == ''
