"""unittests for ./build_unittests.py
"""
import build_unittests as testee
import pytest

def test_main(monkeypatch, capsys):
    """unittests for build_unittests.main function
    """
    class MockMain:
        "stub"
        def __init__(self, *args, **kwargs):
            print('called Main.__init__ with args', args, kwargs)
    class MockMain2:
        "stub with error"
        def __init__(self, *args, **kwargs):
            print('called Main.__init__ with args', args, kwargs)
            raise ValueError('Something went wrong')
    usagetext = ('usage: [python] build_unittests.py <project-name> <module-to-test>'
                 ' { <nickname-in-testconf> | { -r | --rebuild } }')
    monkeypatch.setattr(testee, 'Main', MockMain)
    assert testee.main() == usagetext
    assert capsys.readouterr().out == ''
    assert testee.main('project') == usagetext
    assert capsys.readouterr().out == ''
    assert testee.main('project', 'testee') == usagetext
    assert capsys.readouterr().out == ''
    assert testee.main('project', 'testee', 'nickname') == ''
    assert capsys.readouterr().out == (
            "called Main.__init__ with args ('project', 'testee', 'nickname') {}\n")
    assert testee.main('project', 'testee', '-r') == ''
    assert capsys.readouterr().out == (
            "called Main.__init__ with args ('project', 'testee') {'rebuild': True}\n")
    assert testee.main('project', 'testee', '--rebuild') == ""
    assert capsys.readouterr().out == (
            "called Main.__init__ with args ('project', 'testee') {'rebuild': True}\n")
    assert testee.main('project', 'testee', 'nickname', 'x') == usagetext
    assert capsys.readouterr().out == ''
    monkeypatch.setattr(testee, 'Main', MockMain2)
    assert testee.main('project', 'testee', 'nickname') == 'Something went wrong'
    assert capsys.readouterr().out == (
            "called Main.__init__ with args ('project', 'testee', 'nickname') {}\n")


class TestMain:
    """unittests for build_unittests.Main class
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for build_unittests.Main object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called Main.__init__ with args', args)
        monkeypatch.setattr(testee.Main, '__init__', mock_init)
        testobj = testee.Main()
        assert capsys.readouterr().out == 'called Main.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys, tmp_path):
        """unittest for Main.__init__
        """
        def mock_determine(arg):
            print(f"called determine_project_root with arg '{arg}'")
            return str(tmp_path)
        def mock_create(*args):
            print("called Main.create_testscript with args", args)
            return str(tmp_path / 'xxxx')
        monkeypatch.setattr(testee, 'determine_project_root', mock_determine)
        monkeypatch.setattr(testee.Main, 'create_testscript', mock_create)
        # we testen alleen de mogelijkheden die main() doorgeeft
        # nickname - geen config, geen script
        testobj = testee.Main('project', 'testee', 'nickname')
        assert (tmp_path / '.rurc').read_text() == ("[testdir]\nunittests\n\n"
                                                    "[testscripts]\nnickname = xxxx\n\n"
                                                    "[testees]\nnickname = testee\n\n")
        assert capsys.readouterr().out == (
                "called determine_project_root with arg 'project'\n"
                "called Main.create_testscript with args"
                f" ({testobj}, '{tmp_path}', 'unittests', 'testee', False)\n"
                f"created file {tmp_path}/xxxx\n")
        # nickname - wel config, geen script - nickname niet in config
        (tmp_path / '.rurc').write_text("[testdir]\nunittests\n\n"
                                        "[testscripts]\nneckname = yyyy\n\n"
                                        "[testees]\nneckname = yoink\n\n")
        testobj = testee.Main('project', 'testee', 'nickname')
        assert (tmp_path / '.rurc').read_text() == (
                "[testdir]\nunittests\n\n"
                "[testscripts]\nneckname = yyyy\nnickname = xxxx\n\n"
                "[testees]\nneckname = yoink\nnickname = testee\n\n")
        assert capsys.readouterr().out == (
                "called determine_project_root with arg 'project'\n"
                "called Main.create_testscript with args"
                f" ({testobj}, '{tmp_path}', 'unittests', 'testee', False)\n"
                f"created file {tmp_path}/xxxx\n")
        # nickname - wel config, geen script - nickname al in config
        # (tmp_path / '.rurc').write_text('...')
        with pytest.raises(ValueError) as exc:
            testobj = testee.Main('project', 'testee', 'nickname')
        assert str(exc.value) == "nickname 'nickname' already used for project 'project'"
        assert capsys.readouterr().out == ("called determine_project_root with arg 'project'\n")
        # nickname - wel config, wel script - nickname al in config
        (tmp_path / 'xxxx').write_text('...')
        with pytest.raises(ValueError) as exc:
            testobj = testee.Main('project', 'testee', 'nickname')
        assert str(exc.value) == "nickname 'nickname' already used for project 'project'"
        assert capsys.readouterr().out == ("called determine_project_root with arg 'project'\n")
        # nickname - wel config, wel script - nickname niet in config
        (tmp_path / '.rurc').write_text("[testdir]\nunittests\n\n"
                                        "[testscripts]\nneckname = yyyy\n\n"
                                        "[testees]\nneckname = yoink\n\n")
        testobj = testee.Main('project', 'testee', 'nickname')
        assert (tmp_path / '.rurc').read_text() == (
                "[testdir]\nunittests\n\n"
                "[testscripts]\nneckname = yyyy\nnickname = xxxx\n\n"
                "[testees]\nneckname = yoink\nnickname = testee\n\n")
        assert capsys.readouterr().out == (
                "called determine_project_root with arg 'project'\n"
                "called Main.create_testscript with args"
                f" ({testobj}, '{tmp_path}', 'unittests', 'testee', False)\n"
                f"created file {tmp_path}/xxxx\n")
        # nickname - geen config, wel script
        (tmp_path / '.rurc').unlink()
        testobj = testee.Main('project', 'testee', 'nickname')
        assert (tmp_path / '.rurc').read_text() == (
                "[testdir]\nunittests\n\n"
                "[testscripts]\nnickname = xxxx\n\n"
                "[testees]\nnickname = testee\n\n")
        assert capsys.readouterr().out == (
                "called determine_project_root with arg 'project'\n"
                "called Main.create_testscript with args"
                f" ({testobj}, '{tmp_path}', 'unittests', 'testee', False)\n"
                f"created file {tmp_path}/xxxx\n")
        # rebuild - geen config, geen script
        (tmp_path / '.rurc').unlink()
        (tmp_path / 'xxxx').unlink()
        testobj = testee.Main('project', 'testee', rebuild=True)
        assert not (tmp_path / '.rurc').exists()
        assert capsys.readouterr().out == (
                "called determine_project_root with arg 'project'\n"
                "called Main.create_testscript with args"
                f" ({testobj}, '{tmp_path}', 'unittests', 'testee', True)\n"
                f"{tmp_path}/xxxx rebuilt\n")
        # rebuild - wel config, geen script
        (tmp_path / '.rurc').write_text("[testdir]\nunittests\n\n"
                                        "[testscripts]\nnickname = xxxx\n\n"
                                        "[testees]\nnickname = testee\n\n")
        testobj = testee.Main('project', 'testee', rebuild=True)
        assert (tmp_path / '.rurc').read_text() == ("[testdir]\nunittests\n\n"
                                                    "[testscripts]\nnickname = xxxx\n\n"
                                                    "[testees]\nnickname = testee\n\n")
        assert capsys.readouterr().out == (
                "called determine_project_root with arg 'project'\n"
                "called Main.create_testscript with args"
                f" ({testobj}, '{tmp_path}', 'unittests', 'testee', True)\n"
                f"{tmp_path}/xxxx rebuilt\n")
        # rebuild - wel config, wel script
        (tmp_path / 'xxxx').write_text('...')
        testobj = testee.Main('project', 'testee', rebuild=True)
        assert (tmp_path / '.rurc').read_text() == ("[testdir]\nunittests\n\n"
                                                    "[testscripts]\nnickname = xxxx\n\n"
                                                    "[testees]\nnickname = testee\n\n")
        assert capsys.readouterr().out == (
                "called determine_project_root with arg 'project'\n"
                "called Main.create_testscript with args"
                f" ({testobj}, '{tmp_path}', 'unittests', 'testee', True)\n"
                f"{tmp_path}/xxxx rebuilt\n")
        # rebuild - geen config, wel script
        (tmp_path / '.rurc').unlink()
        testobj = testee.Main('project', 'testee', rebuild=True)
        assert capsys.readouterr().out == (
                "called determine_project_root with arg 'project'\n"
                "called Main.create_testscript with args"
                f" ({testobj}, '{tmp_path}', 'unittests', 'testee', True)\n"
                f"{tmp_path}/xxxx rebuilt\n")

    def test_determine_project_root(self):
        """unittest for Main.determine_project_root
        """
        expand = testee.os.path.expanduser
        assert testee.determine_project_root('bin') == expand('~/bin')
        assert testee.determine_project_root('scripts') == expand('~/bin')
        assert testee.determine_project_root('nginx-config') == expand('~/nginx-config')
        assert testee.determine_project_root('server-stuff') == expand('~/nginx-config')
        assert testee.determine_project_root('xxx') == expand('~/projects/xxx')

    def test_create_testscript(self, monkeypatch, capsys, tmp_path):
        """unittest for Main.create_testscript
        """
        def mock_rename(*args):
            print('called os.rename with args', args)
        def mock_build(arg):
            print(f"called build_oldversiondict with arg '{arg}'")
            return {}
        def mock_build_2(arg):
            print(f"called build_oldversiondict with arg '{arg}'")
            return {('', ''): ['xxx\n', 'yyy\n']}
        def mock_process_f(arg):
            print(f"called Main.process_function with arg '{arg}'")
        def mock_process_c(arg):
            print(f"called Main.process_class with arg '{arg}'")
            return 'ClassName'
        def mock_process_m(*args):
            print("called Main.process_method with args", args)
        monkeypatch.setattr(testee, 'build_oldversiondict', mock_build)
        monkeypatch.setattr(testee.os, 'rename', mock_rename)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.process_function = mock_process_f
        testobj.process_class = mock_process_c
        testobj.process_method = mock_process_m
        rootdir = tmp_path / 'project'
        rootdir.mkdir()
        pyfile = rootdir / 'file.py'
        pyfile.touch()   # python source
        (rootdir / 'testdir').mkdir()

        result = testobj.create_testscript(str(rootdir), 'testdir', str(pyfile), False)
        assert result == str(tmp_path / 'project' / 'testdir' / 'test_file.py')
        assert testobj.testee == 'file'
        assert testobj.oldscriptlines == {}
        modpath = str(rootdir).replace('/', '.')
        assert (rootdir / 'testdir' / 'test_file.py').read_text() == (
                f'"""unittests for ./{rootdir}/file.py\n"""\n'
                f'from {modpath} import file as testee\n')
        assert capsys.readouterr().out == ("")

        pyfile.write_text('def xxxx\nclass yyyy\n    def zzz\nother\n')
        result = testobj.create_testscript(str(rootdir), 'testdir', str(pyfile), False)
        assert result == str(tmp_path / 'project' / 'testdir' / 'test_file.py')
        assert testobj.testee == 'file'
        assert testobj.oldscriptlines == {}
        assert (rootdir / 'testdir' / 'test_file.py').read_text() == (
                f'"""unittests for ./{rootdir}/file.py\n"""\n'
                f'from {modpath} import file as testee\n')
        assert capsys.readouterr().out == (
                "called os.rename with args"
                f" ('{rootdir}/testdir/test_file.py', '{rootdir}/testdir/test_file.py~')\n"
                "called Main.process_function with arg 'def xxxx\n'\n"
                "called Main.process_class with arg 'class yyyy\n'\n"
                "called Main.process_method with args ('ClassName', '    def zzz\\n')\n")

        monkeypatch.setattr(testee, 'build_oldversiondict', mock_build_2)
        result = testobj.create_testscript(str(rootdir), 'testdir', str(pyfile), True)
        assert result == str(tmp_path / 'project' / 'testdir' / 'test_file.py')
        assert testobj.testee == 'file'
        assert testobj.oldscriptlines == {('', ''): ['xxx\n', 'yyy\n']}
        assert (rootdir / 'testdir' / 'test_file.py').read_text() == 'xxx\nyyy\n'
        assert capsys.readouterr().out == (
                f"called build_oldversiondict with arg '{rootdir}/testdir/test_file.py'\n"
                "called os.rename with args"
                f" ('{rootdir}/testdir/test_file.py', '{rootdir}/testdir/test_file.py~')\n"
                "called Main.process_function with arg 'def xxxx\n'\n"
                "called Main.process_class with arg 'class yyyy\n'\n"
                "called Main.process_method with args ('ClassName', '    def zzz\\n')\n")

    def test_process_function(self, monkeypatch, capsys):
        """unittest for Main.process_function
        """
        def mock_old(*args):
            print('called Main.add_oldscriptlines with args', args)
        def mock_new(*args):
            print('called Main.add_lines_for_function with args', args)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.testscriptlines = []
        testobj.add_oldlines = mock_old
        testobj.add_lines_for_function = mock_new
        testobj.oldscriptlines = {}
        testobj.process_function('def fun():\n')
        assert testobj.testscriptlines == ['\n\n']
        assert capsys.readouterr().out == (
                "called Main.add_lines_for_function with args ('def fun():\\n',)\n")
        testobj.oldscriptlines = {('', 'def fun'): ['xxx', 'yyy']}
        testobj.process_function('def fun():\n')
        assert capsys.readouterr().out == (
                "called Main.add_oldscriptlines with args (['xxx', 'yyy'],)\n")

    def test_process_class(self, monkeypatch, capsys):
        """unittest for Main.process_class
        """
        def mock_get(arg):
            print(f"called Main.get_classname with arg '{arg}'")
            return 'AClass'
        def mock_old(*args):
            print('called Main.add_oldscriptlines with args', args)
        def mock_new(*args):
            print('called Main.add_lines_for_class with args', args)
        monkeypatch.setattr(testee, 'get_classname', mock_get)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.testscriptlines = []
        testobj.new_class = False
        testobj.add_oldlines = mock_old
        testobj.add_lines_for_class = mock_new
        testobj.oldscriptlines = {}
        assert testobj.process_class('xxxxx') == "AClass"
        assert testobj.testscriptlines == ['\n\n']
        assert testobj.new_class
        assert capsys.readouterr().out == (
                "called Main.get_classname with arg 'xxxxx'\n"
                "called Main.add_lines_for_class with args ('AClass',)\n")
        testobj.testscriptlines = []
        testobj.oldscriptlines = {('AClass', ''): ['xxx', 'yyy']}
        assert testobj.process_class('xxxxx') == "AClass"
        assert testobj.testscriptlines == ['\n\n']
        assert testobj.new_class
        assert capsys.readouterr().out == (
                "called Main.get_classname with arg 'xxxxx'\n"
                "called Main.add_oldscriptlines with args (['xxx', 'yyy'],)\n")

    def test_process_mwthod(self, monkeypatch, capsys):
        """unittest for Main.process_mwthod
        """
        def mock_old(*args):
            print('called Main.add_oldscriptlines with args', args)
        def mock_new(*args):
            print('called Main.add_lines_for_method with args', args)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.testscriptlines = []
        testobj.add_oldlines = mock_old
        testobj.add_lines_for_method = mock_new
        testobj.oldscriptlines = {}
        testobj.process_method('ClassName', '    def method(self):\n')
        assert testobj.testscriptlines == ['\n']
        assert capsys.readouterr().out == (
                "called Main.add_lines_for_method with args"
                " ('    def method(self):\\n', 'ClassName')\n")
        testobj.testscriptlines = []
        testobj.oldscriptlines = {('ClassName', '    def method'): ['xxx', 'yyy']}
        testobj.process_method('ClassName', '    def method(self):\n')
        assert testobj.testscriptlines == ['\n']
        assert capsys.readouterr().out == (
                "called Main.add_oldscriptlines with args (['xxx', 'yyy'],)\n")

    def test_add_oldlines(self, monkeypatch, capsys):
        """unittest for Main.add_oldlines
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.testscriptlines = []
        testobj.add_oldlines([])
        assert testobj.testscriptlines == []
        testobj.add_oldlines(['lines'])
        assert testobj.testscriptlines == ['lines']

    def test_add_lines_for_function(self, monkeypatch, capsys):
        """unittest for Main.add_lines_for_function
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.testscriptlines = []
        testobj.testee = 'a_module'
        testobj.add_lines_for_function('def a_function():\n')
        assert testobj.testscriptlines == [
                'def _test_a_function(monkeypatch, capsys):\n',
                '    """unittest for a_module.a_function\n    """\n',
                '    assert testee.a_function() == "expected_result"\n',
                '    assert capsys.readouterr().out == ("")\n']
        testobj.testscriptlines = []
        testobj.add_lines_for_function('def a_function(*args):\n')
        assert testobj.testscriptlines == [
                'def _test_a_function(monkeypatch, capsys):\n',
                '    """unittest for a_module.a_function\n    """\n',
                '    assert testee.a_function(*args) == "expected_result"\n',
                '    assert capsys.readouterr().out == ("")\n']
        testobj.testscriptlines = []
        testobj.add_lines_for_function('def a_function(arg1, arg2):\n')
        assert testobj.testscriptlines == [
                'def _test_a_function(monkeypatch, capsys):\n',
                '    """unittest for a_module.a_function\n    """\n',
                '    assert testee.a_function(arg1, arg2) == "expected_result"\n',
                '    assert capsys.readouterr().out == ("")\n']

    def test_add_lines_for_class(self, monkeypatch, capsys):
        """unittest for Main.add_lines_for_class
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.testee = 'a_module'
        testobj.testscriptlines = []
        assert testobj.add_lines_for_class('AClass') == 'AClass'
        assert testobj.testscriptlines == [
            'class TestAClass:\n',
            '    """unittests for a_module.AClass\n    """\n',
            '    def setup_testobj(self, monkeypatch, capsys):\n',
            '        """stub for a_module.AClass object\n\n',
            '        create the object skipping the normal initialization\n',
            '        intercept messages during creation\n',
            '        return the object so that other methods can be monkeypatched in the caller\n',
            '        """\n',
            '        def mock_init(self, *args):\n            "stub"\n',
            "            print('called AClass.__init__ with args', args)\n",
            "        monkeypatch.setattr(testee.AClass, '__init__', mock_init)\n",
            '        testobj = testee.AClass()\n',
            "        assert capsys.readouterr().out == 'called AClass.__init__ with args ()\\n'\n",
            '        return testobj\n']

    def test_add_lines_for_method(self, monkeypatch, capsys):
        """unittest for Main.add_lines_for_method
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.testee = 'a_module'
        testobj.testscriptlines = []
        testobj.new_class = True
        testobj.add_lines_for_method('    def __init__(self):', 'AClass')
        assert not testobj.new_class
        assert testobj.testscriptlines == [
            '    def _test_init(self, monkeypatch, capsys):\n',
            '        """unittest for AClass.__init__\n        """\n'  # NB: impliciete concat
            '        testobj = testee.AClass()\n',                    # dit hoort bij hetzelfde item
            '        assert capsys.readouterr().out == ("")\n']
        testobj.testscriptlines = []
        testobj.add_lines_for_method('    def a_method(self, *args):', 'AClass')
        assert not testobj.new_class
        assert testobj.testscriptlines == [
                '    def _test_a_method(self, monkeypatch, capsys):\n',
                '        """unittest for AClass.a_method\n        """\n'       # NB impliciete concat
                '        testobj = self.setup_testobj(monkeypatch, capsys)\n',  # hoort bij hetzelfde
                '        assert testobj.a_method(*args) == "expected_result"\n',
                '        assert capsys.readouterr().out == ("")\n']
        testobj.testscriptlines = []
        testobj.add_lines_for_method('    def a_method(self, arg1, arg2):', 'AClass')
        assert not testobj.new_class
        assert testobj.testscriptlines == [
                '    def _test_a_method(self, monkeypatch, capsys):\n',
                '        """unittest for AClass.a_method\n        """\n'       # NB impliciete concat
                '        testobj = self.setup_testobj(monkeypatch, capsys)\n',  # hoort bij hetzelfde
                '        assert testobj.a_method(arg1, arg2) == "expected_result"\n',
                '        assert capsys.readouterr().out == ("")\n']
        testobj.testscriptlines = []


def test_build_oldversiondict(tmp_path):
    """unittest for build_unittests.build_oldversiondict
    """
    testfile = tmp_path / 'testfile'
    testfile.write_text("# comment line\njunk line\n\n\n"
                        "def new_function(*args):\n    xxxxx\nyyyyy\n\n\n"
                        "def test_existing_function(*args):\n    aaa\nbbb\n\n\n"
                        "def _test_function():\n    itgygu\n\n\n"
                        "class TestClass:\n    'docstring'\n"
                        "    def setup(self):\n        iijyrfv\n\n"
                        "    def test_init(self):\n        ytfhooi\n\n"
                        "    def test_method(self, *args):\n        ijouyug\n\n"
                        "    def helper(self, *args):\n        'docstring'\n\n\n"
                        "class _TestClass2:\n    'docstring'\n"
                        "    def _setup(self):\n        iijyrfv\n\n"
                        "    def _test_init(self):\n        ytfhooi\n\n"
                        "    def _test_method(self, *args):\n        ijouyug\n\n"
                        "    def helper(self, *args):\n        'docstring'\n\n\n"
                        "class NewClass:\n    'docstring'\n\n"
                        "    def __init__(self):\n        xxxxxxxxx\n\n"
                        "    def method(*args):\n        yyyyyyyy\n\n\n"
                        "if __name__ == '__main__':\n    main()\n")
    result = testee.build_oldversiondict(str(testfile))
    assert result == {
        ('', ''): ['# comment line\n', 'junk line\n', '\n', '\n',
                   'def new_function(*args):\n', '    xxxxx\n', 'yyyyy\n', '\n', '\n',
                   'class NewClass:\n', "    'docstring'\n", '\n',
                   '    def __init__(self):\n', '        xxxxxxxxx\n', '\n',
                   '    def method(*args):\n', '        yyyyyyyy\n', '\n', '\n',
                   "if __name__ == '__main__':\n", '    main()\n'],
        ('', 'def existing_function'): [
            'def test_existing_function(*args):\n', '    aaa\n', 'bbb\n'],
        ('', 'def function'): ['def _test_function():\n', '    itgygu\n'],
        ('Class', ''): ['class TestClass:\n', "    'docstring'\n",
                        '    def setup(self):\n', '        iijyrfv\n', '\n',
            '    def helper(self, *args):\n', "        'docstring'\n"],
        ('Class', '    def __init__'): ['    def test_init(self):\n', '        ytfhooi\n'],
        ('Class', '    def method'): [
            '    def test_method(self, *args):\n', '        ijouyug\n',],
        ('Class2', ''): ['class _TestClass2:\n', "    'docstring'\n",
                         '    def _setup(self):\n', '        iijyrfv\n', '\n',
                         '    def helper(self, *args):\n', "        'docstring'\n"],
        ('Class2', '    def __init__'): ['    def _test_init(self):\n', '        ytfhooi\n'],
        ('Class2', '    def method'): [
            '    def _test_method(self, *args):\n', '        ijouyug\n',]}


def test_get_classname():
    """unittest for build_unittests.get_classname
    """
    assert testee.get_classname('') == ''
    assert testee.get_classname('xxxxx') == ''
    assert testee.get_classname('xyzabcdef') == 'def'
    assert testee.get_classname('class Xyz:\n') == 'Xyz'
    assert testee.get_classname('class Xyz(Abc):\n') == 'Xyz'
