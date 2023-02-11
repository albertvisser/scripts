import pytest
import list2vi

def test_main(monkeypatch, capsys, tmp_path):
    """geen test nodig op leeg file of file bestaat niet,
    want als deze wordt aangeroepen hebben we per definitie een file met namen
    """
    def mock_run(*args, **kwargs):
        print('call subprocess.run() with args', args, kwargs)
    monkeypatch.setattr(list2vi.subprocess, 'run', mock_run)
    fname = tmp_path / 'test_list2vi'
    with fname.open('w') as f:
        print('name1', file=f)
        print('name2', file=f)
        print('name3', file=f)
    list2vi.main(fname)
    assert capsys.readouterr().out == ("call subprocess.run() with args (['gnome-terminal',"
                                       " '--profile', 'Code Editor Shell', '--', 'vim', 'name1',"
                                       " 'name2', 'name3'],) {'check': False}\n")
