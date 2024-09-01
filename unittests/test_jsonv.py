"""unittests for ./jsonp.py
"""
import jsonv as testee


def test_main(monkeypatch, capsys):
    """unittest for jsonv.main
    """
    def mock_check(*args):
        print("called jsonvp.check_usage with args", args)
    def mock_check_2(*args):
        print("called jsonvp.check_usage with args", args)
        return 'xxx'
    def mock_read(filename):
        print(f"called jsonvp.read_json with arg '{filename}'")
    def mock_mkstemp(**kwargs):
        print('called tempfile.mkstemp with args', kwargs)
        return 'tmp_file', 'tmp_name'
    def mock_dump(*args):
        print("called jsonvp.dump_json with args", args)
    def mock_run(*args):
        print("called subprocess.run with args", args)
    monkeypatch.setattr(testee.jsonvp, 'check_usage', mock_check)
    monkeypatch.setattr(testee.jsonvp, 'read_json', mock_read)
    monkeypatch.setattr(testee.tempfile, 'mkstemp', mock_mkstemp)
    monkeypatch.setattr(testee.jsonvp, 'dump_json', mock_dump)
    monkeypatch.setattr(testee.subprocess, 'run', mock_run)
    testee.main('args')
    assert capsys.readouterr().out == "called jsonvp.check_usage with args ('args', 'jsonv')\n"
    monkeypatch.setattr(testee.jsonvp, 'check_usage', mock_check_2)
    testee.main('args')
    assert capsys.readouterr().out == ("called jsonvp.check_usage with args ('args', 'jsonv')\n"
                                       "called jsonvp.read_json with arg 'xxx'\n"
                                       "called tempfile.mkstemp with args {'suffix': '.json'}\n"
                                       "called jsonvp.dump_json with args ('tmp_file', None)\n"
                                       "called subprocess.run with args (['gnome-terminal',"
                                       " '--geometry=102x54', '--', 'vim', '-R', 'tmp_name',"
                                       " '-c', 'set titlestring=[...]/xxx',"
                                       " '-c', 'set foldmethod=syntax'],)\n")
