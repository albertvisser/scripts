"""unittests for ./list2scite.py
"""
import list2scite

def test_main(monkeypatch, capsys, tmp_path):
    """unittest for list2scite.main

    geen test nodig op leeg file of file bestaat niet,
    want als deze wordt aangeroepen hebben we per definitie een file met namen
    """
    def mock_run(*args, **kwargs):
        """stub
        """
        print('call subprocess.run() with args', args, kwargs)
    monkeypatch.setattr(list2scite.subprocess, 'run', mock_run)
    fname = tmp_path / 'test_list2scite'
    with fname.open('w') as f:
        print('name1', file=f)
        print('name2', file=f)
        print('name3', file=f)
    list2scite.main(fname)
    assert capsys.readouterr().out == ("call subprocess.run() with args (['SciTE', 'name1', 'name2',"
                                       " 'name3'],) {'check': False}\n")
