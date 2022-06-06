import pytest
import list2vi

def test_main(monkeypatch, capsys):
    """geen test nodig op leeg file of file bestaat niet,
    want als deze wordt aangeroepen hebben we per definitie een file met namen
    """
    def mock_run(*args):
        print('call subprocess.run() with args', args)
    monkeypatch.setattr(list2vi.subprocess, 'run', mock_run)
    fname = '/tmp/test_list2vi'
    with open(fname, 'w') as f:
        print('name1', file=f)
        print('name2', file=f)
        print('name3', file=f)
    list2vi.main(fname)
    assert capsys.readouterr().out == ("call subprocess.run() with args (['gnome-terminal',"
            " '--profile', 'Code Editor Shell', '--', 'vim', 'name1', 'name2', 'name3'],)\n")
