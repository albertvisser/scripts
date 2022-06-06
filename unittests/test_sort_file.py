import os
import pytest
import sort_file

def test_main(monkeypatch, capsys):
    "input is een list met minimaal de scriptnaam"
    def mock_sort(*args):
        print('called sort() with args', args)
        return 'filenaam'
    monkeypatch.setattr(sort_file, 'sort', mock_sort)
    sort_file.main(['scriptname', 'filename'])
    assert capsys.readouterr().out == ("called sort() with args ('filename',)\n"
                                       'klaar, output in filenaam\n')
    # TODO: input() monkeypatchen
    # sort_file.main(['scriptname'])
    # assert capsys.readouterr().out == (""
    #                                    'klaar, output in filenaam\n')

def test_sort(monkeypatch, capsys):
    ""
    source = '/tmp/test_sort'
    target = '/tmp/test_sort_sorted'
    if os.path.exists(target):
        os.remove(target)
    with open(source, 'w') as f:
        print('een regel', file=f)
        print('de eerste', file=f)
        print('volgende', file=f)
        print('ook een', file=f)
        print('dat was het dan', file=f)
    sort_file.sort(source)
    assert os.path.exists(target)
    with open(target) as in_:
        data = in_.readlines()
    assert data == ['dat was het dan\n', 'de eerste\n', 'een regel\n', 'ook een\n', 'volgende\n']
    # os.remove(source)
    # os.remove(target)

    # sort_file.sort(source, tmp=True)
