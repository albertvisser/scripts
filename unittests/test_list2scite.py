import pytest
import list2scite

def test_main(monkeypatch, capsys):
    """geen test nodig op leeg file of file bestaat niet,
    want als deze wordt aangeroepen hebben we per definitie een file met namen
    """
    def mock_run(*args, **kwargs):
        print('call subprocess.run() with args', args, kwargs)
    monkeypatch.setattr(list2scite.subprocess, 'run', mock_run)
    fname = '/tmp/test_list2scite'
    with open(fname, 'w') as f:
        print('name1', file=f)
        print('name2', file=f)
        print('name3', file=f)
    list2scite.main(fname)
    assert capsys.readouterr().out == ("call subprocess.run() with args (['SciTE', 'name1', 'name2',"
                                       " 'name3'],) {'check': False}\n")
