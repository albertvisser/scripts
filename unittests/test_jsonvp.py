"""unittests for ./jsonvp.py
"""
import jsonvp as testee


def test_check_usage(capsys):
    """unittest for jsonvp.check_usage
    """
    usagemessage = "usage: python {} <filename>\n"
    testee.check_usage([], '')
    assert capsys.readouterr().out == usagemessage.format('')
    testee.check_usage(['python', 'x', 'y'], 'z')
    assert capsys.readouterr().out == usagemessage.format('z')
    assert testee.check_usage(['python', 'file name'], '') == 'file name'
    assert capsys.readouterr().out == ''
    assert testee.check_usage(['python', 'file\\ name'], '') == 'file name'
    assert capsys.readouterr().out == ''
    assert testee.check_usage(['python', 'file\\name'], '') == 'file\\name'
    assert capsys.readouterr().out == ''


def test_read_json(monkeypatch, capsys, tmp_path):
    """unittest for jsonvp.read_json
    """
    def mock_load(arg):
        print(f'json.load with arg {arg}')
        return 'data'
    fname = tmp_path / 'testfile.json'
    fname.touch()
    monkeypatch.setattr(testee.json, 'load', mock_load)
    assert testee.read_json(fname) == 'data'
    assert capsys.readouterr().out == (
            f"json.load with arg <_io.TextIOWrapper name='{fname}' mode='r' encoding='utf-8'>\n")


def test_dump_json(monkeypatch, capsys, tmp_path):
    """unittest for jsonvp.dump_json
    """
    def mock_dump(*args, **kwargs):
        print('json.dump with args', args, kwargs)
    monkeypatch.setattr(testee.json, 'dump', mock_dump)
    fname = tmp_path / 'testfile.json'
    testee.dump_json(fname, 'data')
    assert capsys.readouterr().out == (
            f"json.dump with args ('data', <_io.TextIOWrapper name='{fname}' mode='w'"
            " encoding='utf-8'>) {'indent': 4}\n")
