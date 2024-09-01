"""unittests for ./jsonp.py
"""
import jsonp as testee

def test_main(monkeypatch, capsys):
    """unittest for jsonp.main
    """
    def mock_check(*args):
        print("called jsonvp.check_usage with args", args)
    def mock_check_2(*args):
        print("called jsonvp.check_usage with args", args)
        return 'xxx'
    def mock_read(filename):
        print(f"called jsonvp.read_json with arg '{filename}'")
    def mock_dump(*args):
        print("called jsonvp.dump_json with args", args)
    monkeypatch.setattr(testee.jsonvp, 'check_usage', mock_check)
    monkeypatch.setattr(testee.jsonvp, 'read_json', mock_read)
    monkeypatch.setattr(testee.jsonvp, 'dump_json', mock_dump)
    testee.main('args')
    assert capsys.readouterr().out == "called jsonvp.check_usage with args ('args', 'jsonp')\n"
    monkeypatch.setattr(testee.jsonvp, 'check_usage', mock_check_2)
    testee.main('args')
    assert capsys.readouterr().out == ("called jsonvp.check_usage with args ('args', 'jsonp')\n"
                                       "called jsonvp.read_json with arg 'xxx'\n"
                                       "called jsonvp.dump_json with args ('xxx_pretty', None)\n")
