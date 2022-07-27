import os
import pytest
import builtins
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
    monkeypatch.setattr(builtins, 'input', lambda *args, **kwargs: 'somefile')
    sort_file.main(['scriptname'])
    assert capsys.readouterr().out == ("called sort() with args ('somefile',)\n"
                                       'klaar, output in filenaam\n')

def test_sort(monkeypatch, capsys):
    ""
    workdir = '/tmp/sorttest'
    if os.path.exists(workdir):
        for file in os.listdir(workdir):
            os.remove(os.path.join(workdir, file))
    else:
        os.mkdir(workdir)
    source = os.path.join(workdir, 'test_sort')
    target = os.path.join(workdir, 'test_sort_sorted')
    target_tmp = '/tmp/test_sort'
    with open(source, 'w') as f:
        print('een regel', file=f)
        print('de eerste', file=f)
        print('volgende', file=f)
        print('ook een', file=f)
        print('dat was het dan', file=f)
    assert sort_file.sort(source) == target
    assert os.path.exists(target)
    assert not os.path.exists(target_tmp)
    with open(target) as in_:
        data = in_.readlines()
    os.remove(target)

    assert sort_file.sort(source, tmp=True) == target_tmp
    assert os.path.exists(target_tmp)
    assert not os.path.exists(target)
    with open(target_tmp) as in_:
        data = in_.readlines()
    assert data == ['dat was het dan\n', 'de eerste\n', 'een regel\n', 'ook een\n', 'volgende\n']
    os.remove(target_tmp)
    os.remove(source)

    # sort_file.sort(source, tmp=True)
