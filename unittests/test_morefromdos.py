"""unittests for ./morefromdos.py
"""
from types import SimpleNamespace
import morefromdos

def test_main(monkeypatch, capsys):
    """unittest for morefromdos.main

    testen zonder argumenten is niet nodig, kan niet voorkomen
    """
    def mock_fromdos(*args):
        """stub
        """
        print('called fromdos() with args', args)
    monkeypatch.setattr(morefromdos.os, 'getcwd', lambda: 'current_dir')
    monkeypatch.setattr(morefromdos, 'fromdos', mock_fromdos)
    morefromdos.main(['scriptname'])
    assert capsys.readouterr().out == "called fromdos() with args ('current_dir',)\n"
    morefromdos.main(['scriptname', 'dirname'])
    assert capsys.readouterr().out == "called fromdos() with args ('dirname',)\n"
    morefromdos.main(['scriptname', 'dirname', 'fileext'])
    assert capsys.readouterr().out == "called fromdos() with args ('dirname', 'fileext')\n"
    morefromdos.main(['scriptname', 'dirname', 'fileext', 'extra'])
    assert capsys.readouterr().out == 'too many arguments\n'

def test_fromdos_err(monkeypatch):
    """unittest for morefromdos.fromdos_err
    """
    def mock_run_err(*args, **kwargs):
        """stub
        """
        return SimpleNamespace(returncode=1)
    monkeypatch.setattr(morefromdos.sp, 'run', mock_run_err)
    assert morefromdos.fromdos('dirname') == 'please install `fromdos` or `dos2unix`'

def test_fromdos(monkeypatch, capsys):
    """unittest for morefromdos.fromdos
    """
    counter = 0
    def mock_run(*args, **kwargs):
        """stub
        """
        nonlocal counter
        counter += 1
        if counter == 1:
            return SimpleNamespace(returncode=0)
        print('called subprocess.run() with args', args)
    def mock_listdir(*args):
        """stub
        """
        return 'file1.py', 'file2.py', 'file3', 'file4.js'
    monkeypatch.setattr(morefromdos.sp, 'run', mock_run)
    monkeypatch.setattr(morefromdos.os, 'listdir', mock_listdir)
    monkeypatch.setattr(morefromdos.os.path, 'abspath', lambda x: f'abspath/{x}')
    monkeypatch.setattr(morefromdos.os.path, 'isfile', lambda x: True)
    morefromdos.fromdos('dirname')
    assert capsys.readouterr().out == (
            "called subprocess.run() with args (['fromdos', 'abspath/dirname/file1.py'],)\n"
            "called subprocess.run() with args (['fromdos', 'abspath/dirname/file2.py'],)\n")

def test_fromdos_ext(monkeypatch, capsys):
    """unittest for morefromdos.fromdos_ext
    """
    counter = 0
    def mock_run(*args, **kwargs):
        """stub
        """
        nonlocal counter
        counter += 1
        if counter == 1:
            return SimpleNamespace(returncode=0)
        print('called subprocess.run() with args', args)
    def mock_listdir(*args):
        """stub
        """
        return 'file1.py', 'file2.py', 'file3', 'file4.js'
    monkeypatch.setattr(morefromdos.sp, 'run', mock_run)
    monkeypatch.setattr(morefromdos.os, 'listdir', mock_listdir)
    monkeypatch.setattr(morefromdos.os.path, 'abspath', lambda x: f'abspath/{x}')
    monkeypatch.setattr(morefromdos.os.path, 'isfile', lambda x: True)
    morefromdos.fromdos('dirname', 'js')
    assert capsys.readouterr().out == (
            "called subprocess.run() with args (['fromdos', 'abspath/dirname/file4.js'],)\n")
    counter = 0
    morefromdos.fromdos('dirname', '.js')
    assert capsys.readouterr().out == (
            "called subprocess.run() with args (['fromdos', 'abspath/dirname/file4.js'],)\n")

def test_fromdos_noext(monkeypatch, capsys):
    """unittest for morefromdos.fromdos_noext
    """
    counter = 0
    def mock_run(*args, **kwargs):
        """stub
        """
        nonlocal counter
        counter += 1
        if counter == 1:
            return SimpleNamespace(returncode=0)
        print('called subprocess.run() with args', args)
    def mock_listdir(*args):
        """stub
        """
        return 'file1.py', 'file2.py', 'file3', 'file4.js'
    monkeypatch.setattr(morefromdos.sp, 'run', mock_run)
    monkeypatch.setattr(morefromdos.os, 'listdir', mock_listdir)
    monkeypatch.setattr(morefromdos.os.path, 'abspath', lambda x: f'abspath/{x}')
    monkeypatch.setattr(morefromdos.os.path, 'isfile', lambda x: True)
    morefromdos.fromdos('dirname', '')
    assert capsys.readouterr().out == (
            "called subprocess.run() with args (['fromdos', 'abspath/dirname/file3'],)\n")
    counter = 0
    morefromdos.fromdos('dirname', '.')
    assert capsys.readouterr().out == (
            "called subprocess.run() with args (['fromdos', 'abspath/dirname/file3'],)\n")
