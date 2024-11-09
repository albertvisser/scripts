"""unittests for ./count_locs.py
"""
import count_locs as testee


def test_main(monkeypatch, capsys):
    """unittest for count_locs.get_locs
    """
    def mock_get(*args):
        print('called get_locs_for_module with args', args)
        return ['x', 'y', 'z']
    def mock_sort(lines):
        print('called sort_locs_by_lineno with arg', lines)
        return lines
    monkeypatch.setattr(testee, 'usage', 'use like this')
    monkeypatch.setattr(testee, 'get_locs_for_module', mock_get)
    monkeypatch.setattr(testee, 'sort_locs_by_lineno', mock_sort)
    testee.sys.argv = ['program']
    testee.main()
    assert capsys.readouterr().out == ("use like this\n")
    testee.sys.argv = ['program', 'filename']
    testee.main()
    assert capsys.readouterr().out == (
            "called get_locs_for_module with args (PosixPath('filename'),"
            f" {testee.pathlib.Path('~/bin').expanduser()!r})\nx\ny\nz\n")
    testee.sys.argv = ['program', 'filename', '']
    testee.main()
    assert capsys.readouterr().out == (
            "called get_locs_for_module with args (PosixPath('filename'),"
            f" {testee.pathlib.Path('~/bin').expanduser()!r})\nx\ny\nz\n")
    testee.sys.argv = ['program', 'filename', 'method']
    testee.main()
    # moet dit niet "invalid output mode" o.i.d. zijn?
    assert capsys.readouterr().out == (
            "called get_locs_for_module with args (PosixPath('filename'),"
            f" {testee.pathlib.Path('~/bin').expanduser()!r})\nx\ny\nz\n")
    testee.sys.argv = ['program', 'filename', '-n']
    testee.main()
    assert capsys.readouterr().out == (
            "called get_locs_for_module with args (PosixPath('filename'),"
            f" {testee.pathlib.Path('~/bin').expanduser()!r})\nx\ny\nz\n")
    testee.sys.argv = ['program', 'filename', '--name']
    testee.main()
    assert capsys.readouterr().out == (
            "called get_locs_for_module with args (PosixPath('filename'),"
            f" {testee.pathlib.Path('~/bin').expanduser()!r})\nx\ny\nz\n")
    testee.sys.argv = ['program', 'filename', '-l']
    testee.main()
    assert capsys.readouterr().out == (
            "called get_locs_for_module with args (PosixPath('filename'),"
            f" {testee.pathlib.Path('~/bin').expanduser()!r})\n"
            "called sort_locs_by_lineno with arg ['x', 'y', 'z']\nx\ny\nz\n")
    testee.sys.argv = ['program', 'filename', '--lineno']
    testee.main()
    assert capsys.readouterr().out == (
            "called get_locs_for_module with args (PosixPath('filename'),"
            f" {testee.pathlib.Path('~/bin').expanduser()!r})\n"
            "called sort_locs_by_lineno with arg ['x', 'y', 'z']\nx\ny\nz\n")
    testee.sys.argv = ['program', '-h']
    testee.main()
    assert capsys.readouterr().out == ("use like this\n")
    testee.sys.argv = ['program', '--help']
    testee.main()
    assert capsys.readouterr().out == ("use like this\n")


def test_ask_input_via_gui(monkeypatch, capsys):
    """unittest for count_locs.sk_input_via_gui
    """
    def mock_askfile():
        print('called FileDialog.askopenfilename')
        return 'fname'
    def mock_askstring(*args):
        nonlocal counter
        print('called SimpleDialog.askstring with args', args)
        counter += 1
        return [None, '', 'bin', 'scripts', 'nginx-config', 'server-stuff', 'anyname'][counter]
    def mock_showerror(message):
        print(f"called MessageBox.showerror with text '{message}'")
    def mock_exp(arg):
        print(f"called path.expanduser with arg '{arg}'")
        return arg
    def mock_rel(*args):
        print("called path.relative_to with args", args)
        return args[0]
    monkeypatch.setattr(testee.fd, 'askopenfilename', mock_askfile)
    monkeypatch.setattr(testee.sd, 'askstring', mock_askstring)
    monkeypatch.setattr(testee.mb, 'showerror', mock_showerror)
    monkeypatch.setattr(testee.pathlib.Path, 'cwd', lambda: testee.pathlib.Path('curdir'))
    monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: True)
    monkeypatch.setattr(testee.pathlib.Path, 'expanduser', mock_exp)
    monkeypatch.setattr(testee.pathlib.Path, 'relative_to', mock_rel)
    counter = 0
    assert testee.ask_input_via_gui() == (testee.pathlib.Path('curdir'), testee.pathlib.Path('fname'))
    assert capsys.readouterr().out == (
            "called FileDialog.askopenfilename\n"
            "called SimpleDialog.askstring with args ('Zoekend naar een import pad',"
            " 'Geef projectnaam op of gebruik huidige')\n"
            "called path.expanduser with arg 'curdir'\n"
            "called path.relative_to with args (PosixPath('fname'), PosixPath('curdir'))\n")
    assert testee.ask_input_via_gui() == (testee.pathlib.Path('~/bin'), testee.pathlib.Path('fname'))
    assert capsys.readouterr().out == (
            "called FileDialog.askopenfilename\n"
            "called SimpleDialog.askstring with args ('Zoekend naar een import pad',"
            " 'Geef projectnaam op of gebruik huidige')\n"
            "called path.expanduser with arg '~/bin'\n"
            "called path.relative_to with args (PosixPath('fname'), PosixPath('~/bin'))\n")
    assert testee.ask_input_via_gui() == (testee.pathlib.Path('~/bin'), testee.pathlib.Path('fname'))
    assert capsys.readouterr().out == (
            "called FileDialog.askopenfilename\n"
            "called SimpleDialog.askstring with args ('Zoekend naar een import pad',"
            " 'Geef projectnaam op of gebruik huidige')\n"
            "called path.expanduser with arg '~/bin'\n"
            "called path.relative_to with args (PosixPath('fname'), PosixPath('~/bin'))\n")
    assert testee.ask_input_via_gui() == (testee.pathlib.Path('~/nginx-config'),
                                          testee.pathlib.Path('fname'))
    assert capsys.readouterr().out == (
            "called FileDialog.askopenfilename\n"
            "called SimpleDialog.askstring with args ('Zoekend naar een import pad',"
            " 'Geef projectnaam op of gebruik huidige')\n"
            "called path.expanduser with arg '~/nginx-config'\n"
            "called path.relative_to with args (PosixPath('fname'), PosixPath('~/nginx-config'))\n")
    assert testee.ask_input_via_gui() == (testee.pathlib.Path('~/nginx-config'),
                                          testee.pathlib.Path('fname'))
    assert capsys.readouterr().out == (
            "called FileDialog.askopenfilename\n"
            "called SimpleDialog.askstring with args ('Zoekend naar een import pad',"
            " 'Geef projectnaam op of gebruik huidige')\n"
            "called path.expanduser with arg '~/nginx-config'\n"
            "called path.relative_to with args (PosixPath('fname'), PosixPath('~/nginx-config'))\n")
    assert testee.ask_input_via_gui() == (testee.pathlib.Path('~/projects/anyname'),
                                          testee.pathlib.Path('fname'))
    assert capsys.readouterr().out == (
            "called FileDialog.askopenfilename\n"
            "called SimpleDialog.askstring with args ('Zoekend naar een import pad',"
            " 'Geef projectnaam op of gebruik huidige')\n"
            "called path.expanduser with arg '~/projects/anyname'\n"
            "called path.relative_to with args (PosixPath('fname'),"
            " PosixPath('~/projects/anyname'))\n")
    counter -= 1
    monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: False)
    assert testee.ask_input_via_gui() == ('', testee.pathlib.Path('fname'))
    assert capsys.readouterr().out == (
            "called FileDialog.askopenfilename\n"
            "called SimpleDialog.askstring with args ('Zoekend naar een import pad',"
            " 'Geef projectnaam op of gebruik huidige')\n"
            "called path.expanduser with arg '~/projects/anyname'\n"
            "called MessageBox.showerror with text 'anyname is geen geldig project'\n"
            "called path.relative_to with args (PosixPath('fname'), '')\n")


def test_get_locs_for_module(monkeypatch, capsys):
    """unittest for count_locs.get_locs_for_module
    """
    def mock_get(*args):
        print('called get_locs with args', args)
        return [('xxx', 0, 2), ('yyy', 1, 5), ('zzz', 2, 7)]
    monkeypatch.setattr(testee, 'HEADING', 'heading')
    monkeypatch.setattr(testee, 'DETAIL', '{} {} {}')
    monkeypatch.setattr(testee, 'get_locs', mock_get)
    assert testee.get_locs_for_module(testee.pathlib.Path('xxx'), testee.pathlib.Path('path')) == [
            'heading', 'xxx', 'yyy 1 5', 'zzz 2 7-8']
    assert capsys.readouterr().out == "called get_locs with args ('xxx', PosixPath('path'))\n"


def test_get_locs(monkeypatch):
    """unittest for count_locs.get_locs
    """
    def mock_get(*args):
        print('called get_locs_for_unit with args', args)
        return 0, 0, 'message'
    tempfile = testee.pathlib.Path('test_get_locs.py')
    doc1 = '\t\"\"\"doc\"\"\"\n'
    doc2 = '\t\"\"\"doc\n\t\"\"\"\n'
    doc3 = '\t\t\"\"\"doc\n\t\t\"\"\"\n'
    if tempfile.exists():
        tempfile.unlink()
    tempfile.write_text(
            "from os.path import split\nfrom invoke import task\n"
            "from datetime import datetime\nimport wx\n\n"
            "def function(arg):\n\tprint('something')\n\treturn arg\n\n\n"
            "@task(help={'arg': 'argument'})\ndef command(c, arg):\n\tprint('something')\n"
            "\treturn arg\n\n\n"
            "class MyClass:\n\tnomethods = True\n\n\n"
            "class AnotherClass:\n\tdef method(self):\n\t\tprint('something')\n\t\treturn arg\n"
            f"\n\ndef function2(arg):\n{doc1}\tprint('something')\n\treturn arg\n\n\n"
            f"@task(help={{'arg': 'argument'}})\ndef command2(c, arg):\n{doc2}\tprint('something')\n"
            "\treturn arg\n\n\n"
            f"class MyClass2:\n{doc1}\tnomethods = True\n\n\n"
            f"class AnotherClass2(AnotherClass):\n{doc1}\n\tdef method2(self):\n{doc3}"
            "\t\tprint('something')\n\t\treturn arg\n"
            "\n\nclass MyEditor(wx.TextCtrl):\n    pass\n")
    assert testee.get_locs('test_get_locs', '') == [('AnotherClass.method', 2, 23),
                                                    ('AnotherClass2.method2', 2, 52),
                                                    ('command (invoke task)', 3, 13),
                                                    ('command2 (invoke task)', 3, 37),
                                                    ('function', 2, 7),
                                                    ('function2', 2, 29)]
    monkeypatch.setattr(testee, 'get_locs_for_unit', mock_get)
    assert testee.get_locs('test_get_locs', '') == [('message', 0, 0), ('message', 0, 0),
                                                    ('message', 0, 1), ('message', -2, 3),
                                                    ('message', 0, 0), ('message', 0, 0)]
    # tempfile.unlink()


def test_get_locs_for_unit_err_1(monkeypatch):
    """unittest for count_locs.get_locs_for_unit geeft TypeError
    """
    def mock_get(arg):
        """stub
        """
        raise TypeError
    monkeypatch.setattr(testee.inspect, 'getsourcelines', mock_get)
    assert testee.get_locs_for_unit('x', 'y') == (0, 0, 'wrong type for getsourcelines'
                                                  ' - skipped: x y')


def test_get_locs_for_unit_err_2(monkeypatch):
    """unittest for count_locs.get_locs_for_unit geeft OSError
    """
    def mock_get(arg):
        """stub
        """
        raise OSError('this')
    monkeypatch.setattr(testee.inspect, 'getsourcelines', mock_get)
    assert testee.get_locs_for_unit('x', 'y') == (0, 0, 'this for x y')


def test_get_locs_for_unit(monkeypatch):
    """unittest for count_locs.get_locs_for_unit
    """
    def mock_get(arg):
        """stub
        """
        return ['line1', 'x', 'y', 'z', 'last line'], 2
    monkeypatch.setattr(testee.inspect, 'getsourcelines', mock_get)
    assert testee.get_locs_for_unit('x', 'y') == (4, 3, '')


def test_sort_locs_by_lineno(monkeypatch):
    """unittest for count_locs.sort_locs_by_lineno
    """
    monkeypatch.setattr(testee, 'HEADING', 'headerstuffing')
    assert testee.sort_locs_by_lineno([
        'headerstuff for `mymodule`', 'headerstuffing for `filename`', '', 'name: 20 lines (1-19)\n',
        'headerstuffing for `filename 2`', '', '\n',
        'headerstuffing for `filename 3`', '', 'name2: 1 lines (20)', 'name3: 20 lines (21-39)\n',
        'name1: 20 lines (1-19)\n']) == ['module: `filename`', '1-19      name (20)', '====',
                                         'module: `filename 3`', '1-19      name1 (20)',
                                         '20        name2 (1)', '21-39     name3 (20)']
