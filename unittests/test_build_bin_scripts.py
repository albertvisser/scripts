"""unittests for ./build_bin_scripts.py
"""
import build_bin_scripts as testee


def test_main(monkeypatch, capsys, tmp_path):
    """unittest for build_bin_scripts.main
    """
    class MockParser(dict):
        "stub for configparser.ConfigParser"
        def __init__(self):
            print('called ConfigParser.__init__')
        def read(self, filename):
            print(f"called ConfigParser.read with arg '{filename}'")
            self['symlinks'] = {}
            self['symlinks-check'] = {}
            self['scripts'] = {}
            self['scripts-sh'] = {}
            self['scripts-bash'] = {}
            self['symlinks-last'] = {}
    def mock_read(self, filename):
        print(f"called ConfigParser.read with arg '{filename}'")
        self['symlinks'] = {str(dummyfile): 'xx'}
        self['symlinks-check'] = {str(dummyfile): 'xx'}
        self['scripts'] = {str(dummyfile): 'xx'}
        self['scripts-sh'] = {str(dummyfile): 'xx'}
        self['scripts-bash'] = {str(dummyfile): 'xx'}
        self['symlinks-last'] = {str(dummyfile): 'xx'}
    def mock_read2(self, filename):
        print(f"called ConfigParser.read with arg '{filename}'")
        self['symlinks'] = {str(symlink1): str(dummyfile)}
        self['symlinks-check'] = {str(symlink2): str(dummyfile)}
        self['scripts'] = {str(script1): 'xx'}
        self['scripts-sh'] = {str(script2): 'xx'}
        self['scripts-bash'] = {str(script3): 'xx'}
        self['symlinks-last'] = {str(symlink3): str(dummyfile)}
    def mock_link(*args):
        print('called os.symlink with args', args)
    def mock_chmod(*args):
        print('called os.chmod with args', args)
    monkeypatch.setattr(testee.configparser, 'ConfigParser', MockParser)
    testee.main()
    assert capsys.readouterr().out == ("called ConfigParser.__init__\n"
                                       "called ConfigParser.read with arg 'bin-scripts.conf'\n")
    dummyfile = tmp_path / 'yy'
    dummyfile.touch()
    monkeypatch.setattr(MockParser, 'read', mock_read)
    testee.main()
    assert capsys.readouterr().out == ("called ConfigParser.__init__\n"
                                       "called ConfigParser.read with arg 'bin-scripts.conf'\n")
    symlink1 = tmp_path / 'symlink1'
    symlink2 = tmp_path / 'symlink2'
    script1 = tmp_path / 'script1'
    script2 = tmp_path / 'script2'
    script3 = tmp_path / 'script3'
    symlink3 = tmp_path / 'symlink3'
    monkeypatch.setattr(MockParser, 'read', mock_read2)
    # monkeypatch.setattr(testee.os, 'symlink', mock_link)
    monkeypatch.setattr(testee.os, 'chmod', mock_chmod)
    testee.main()
    assert symlink1.is_symlink()
    assert symlink1.readlink() == dummyfile
    assert symlink2.is_symlink()
    assert symlink2.readlink() == dummyfile
    assert script1.read_text() == 'xx'
    assert script2.read_text() == '#! /bin/sh\nxx'
    assert script3.read_text() == '#! /bin/bash\nxx'
    assert symlink3.is_symlink()
    assert symlink3.readlink() == dummyfile
    assert capsys.readouterr().out == ("called ConfigParser.__init__\n"
                                       "called ConfigParser.read with arg 'bin-scripts.conf'\n"
                                       f"called os.chmod with args ('{script1}', 33252)\n"
                                       f"called os.chmod with args ('{script2}', 33252)\n"
                                       f"called os.chmod with args ('{script3}', 33252)\n")
