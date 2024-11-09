"""unittests for ./sort_file.py
"""
import os
import types
import builtins
import sort_file as testee

def test_main(monkeypatch, capsys):
    """unittest for sort_file.main
    """
    def mock_sort(*args):
        """stub
        """
        print('called sort() with args', args)
    monkeypatch.setattr(testee, 'sort', mock_sort)
    testee.main(types.SimpleNamespace(file='filename.ext', output='', column='5'))
    assert capsys.readouterr().out == ("called sort() with args ('filename.ext',"
                                       " 'filename_sorted.ext', '5')\n"
                                       'klaar, output in filename_sorted.ext\n')
    testee.main(types.SimpleNamespace(file='filename', output='', column=5))
    assert capsys.readouterr().out == ("called sort() with args ('filename', 'filename_sorted', 5)\n"
                                       'klaar, output in filename_sorted\n')
    testee.main(types.SimpleNamespace(file='filename', output='other_file', column=''))
    assert capsys.readouterr().out == ("called sort() with args ('filename', 'other_file', '')\n"
                                       'klaar, output in other_file\n')
    monkeypatch.setattr(builtins, 'input', lambda *args, **kwargs: 'somefile')
    testee.main(types.SimpleNamespace(file='', output='', column=''))
    assert capsys.readouterr().out == ("called sort() with args ('somefile', 'somefile_sorted', '')\n"
                                       'klaar, output in somefile_sorted\n')

def test_sort(tmp_path):
    """unittest for sort_file.sort
    """
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
    testee.sort(source, target, '')
    assert os.path.exists(target)
    with open(target) as in_:
        data = in_.readlines()
    assert data == ['dat was het dan\n', 'de eerste\n', 'een regel\n', 'ook een\n', 'volgende\n']

    testee.sort(source, target, '3')
    with open(target) as in_:
        data = in_.readlines()
    assert data == ['ook een\n', 'een regel\n', 'dat was het dan\n', 'de eerste\n', 'volgende\n']
