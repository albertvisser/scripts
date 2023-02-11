import os
import types
import pytest
import builtins
import sort_file

def test_main(monkeypatch, capsys):
    def mock_sort(*args):
        print('called sort() with args', args)
    monkeypatch.setattr(sort_file, 'sort', mock_sort)
    sort_file.main(types.SimpleNamespace(file='filename.ext', output='', column='5'))
    assert capsys.readouterr().out == ("called sort() with args ('filename.ext',"
                                       " 'filename_sorted.ext', '5')\n"
                                       'klaar, output in filename_sorted.ext\n')
    sort_file.main(types.SimpleNamespace(file='filename', output='', column=5))
    assert capsys.readouterr().out == ("called sort() with args ('filename', 'filename_sorted', 5)\n"
                                       'klaar, output in filename_sorted\n')
    sort_file.main(types.SimpleNamespace(file='filename', output='other_file', column=''))
    assert capsys.readouterr().out == ("called sort() with args ('filename', 'other_file', '')\n"
                                       'klaar, output in other_file\n')
    monkeypatch.setattr(builtins, 'input', lambda *args, **kwargs: 'somefile')
    sort_file.main(types.SimpleNamespace(file='', output='', column=''))
    assert capsys.readouterr().out == ("called sort() with args ('somefile', 'somefile_sorted', '')\n"
                                       'klaar, output in somefile_sorted\n')

def test_sort(monkeypatch, capsys, tmp_path):
    ""
    workdir = tmp_path / 'sorttest'
    workdir.mkdir()
    source = str(workdir / 'test_sort')
    target = str(workdir / 'test_sort_sorted')
    with open(source, 'w') as f:
        print('een regel', file=f)
        print('de eerste', file=f)
        print('volgende', file=f)
        print('ook een', file=f)
        print('dat was het dan', file=f)
    sort_file.sort(source, target, '')
    assert os.path.exists(target)
    with open(target) as in_:
        data = in_.readlines()
    assert data == ['dat was het dan\n', 'de eerste\n', 'een regel\n', 'ook een\n', 'volgende\n']

    sort_file.sort(source, target, '3')
    with open(target) as in_:
        data = in_.readlines()
    assert data == ['ook een\n', 'een regel\n', 'dat was het dan\n', 'de eerste\n', 'volgende\n']
