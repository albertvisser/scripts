"""unittests for ./check_repo.py
"""
import types
import pathlib
import pytest
import mockgui.mockqtwidgets as mockqtw
from unittests.output_fixtures import expected_output
import check_repo as testee
from check_repo_tooltips import tooltips

@pytest.fixture
def testobj(monkeypatch, capsys):
    """stub for check_repo.Gui - pytest fixture version
    """
    def mock_init(self, *args):
        """stub
        """
        print('called QMainWindow.__init__()')
    monkeypatch.setattr(testee.qtw, 'QApplication', mockqtw.MockApplication)
    monkeypatch.setattr(testee.qtw.QWidget, '__init__', mock_init)
    monkeypatch.setattr(testee.qtw, 'QWidget', mockqtw.MockWidget)
    monkeypatch.setattr(testee.Gui, 'get_repofiles', mock_get_repofiles)
    monkeypatch.setattr(testee.Gui, 'setup_visual', mock_setup_visual)
    monkeypatch.setattr(testee.Gui, 'refresh_frame', mock_refresh_frame)
    app = testee.Gui(pathlib.Path('base'), 'git')
    capsys.readouterr()  # swallow stdout/stderr
    return app


def setup_app(monkeypatch):
    """stub for check_repo.Gui - deze wordt ook gebruikt
    """
    def mock_init(self, *args):
        """stub
        """
        print('called QMainWindow.__init__()')
    monkeypatch.setattr(testee.qtw, 'QApplication', mockqtw.MockApplication)
    monkeypatch.setattr(testee.qtw.QWidget, '__init__', mock_init)
    monkeypatch.setattr(testee.qtw, 'QWidget', mockqtw.MockWidget)
    return testee.Gui(pathlib.Path('base'), 'git')


def mock_run(*args):
    """generic stub for ... (momenteel overal overridden)
    """
    print('run with args:', args)


def mock_just_run(command):
    """generic stub for Gui.just_run
    """
    print(f'call just_run() for `{command}`')


def mock_sp_run(*args, **kwargs):
    """stub for subprocess.run and subprocess.Popen
    """
    print('run with args:', args, kwargs)
    return types.SimpleNamespace(stdout=b'hallo\ndaar\njongens\n')


def mock_dialog_init(self, parent, *args):
    """stub for PyQt.QWidgets.QDialog method
    """
    self.parent = parent
    print('called dialog.__init()__ with args', args)


def mock_information(self, title, message):
    """stub for PyQt.QWidgets.QDialog.information
    """
    print(f'display message `{message}`')


class MockGui:
    """stub for check_repo.Gui object
    """
    def __init__(self, *args):
        self.app = mockqtw.MockApplication()
        print('called Gui.__init__() with args', args)
    def show(self):
        """stub
        """
        print('called Gui.show()')
    def get_menudata(self):
        """stub
        """
    def callback(self):
        """stub
        """
    def check_active(self, *args):
        """stub
        """
        print('called Gui.check_active()')
    def activate_item(self, *args):
        """stub
        """
        print('called Gui.activate_item() with arg `{args[0]}`')
    def update(self):
        """stub
        """
        print('called Gui.update()')


def mock_setWindowTitle(self, *args):
    """stub for PyQt.QWidgets.QDialog method
    """
    print('called dialog.setWindowTitle() with args', args)


def mock_setLayout(self, *args):
    """stub for PyQt.QWidgets.QDialog method
    """
    print('called dialog.setLayout()')


def mock_setup_visual(self, *args):
    """stub for check_repo.Gui method - waarom niet opgenomen in MockGui?
    """
    print('called Gui.setup_visual()')
    self.list = mockqtw.MockListBox()
    self.cb_branch = mockqtw.MockComboBox()


def mock_refresh_frame(self, *args):
    """stub for check_repo.Gui method
    """
    print('called Gui.refresh_frame()')


def mock_get_repofiles(self):
    """stub for check_repo.Gui method
    """
    print('called Gui.get_repofiles()')
    return 'file1.py', 'file2.py'


def mock_update_branches(self):
    """stub for check_repo.Gui method
    """
    print('called Gui.update_branches()')


# --- actual test routines start here ---
def test_main(monkeypatch, capsys):
    """unittest for check_repo.main
    """
    class MockParser:
        """stub
        """
        def add_argument(self, *args, **kwargs):
            """stub
            """
            print('call parser.add_argument with args', args, kwargs)
        def parse_args(self):
            """stub
            """
            print('call parser.parse_args()')
            return 'args'
    def mock_startapp(*args):
        """stub
        """
        print('call startapp with args:', args)
        return 'results'
    monkeypatch.setattr(testee.argparse, 'ArgumentParser', MockParser)
    monkeypatch.setattr(testee, 'startapp', mock_startapp)
    testee.main()
    assert capsys.readouterr().out == ("call parser.add_argument with args ('project',)"
                                       " {'help': 'name of a software project', 'nargs': '?',"
                                       " 'default': ''}\n"
                                       'call parser.parse_args()\n'
                                       "call startapp with args: ('args',)\n"
                                       'results\n')


def test_startapp(monkeypatch, capsys, tmp_path):
    """unittest for check_repo.startapp
    """
    def return_false_then_true(*args):
        """stub
        """
        nonlocal counter
        counter += 1
        return counter != 1
    monkeypatch.setattr(testee.pathlib.Path, 'cwd', lambda *x: tmp_path)
    monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: True)
    monkeypatch.setattr(testee.qtw, 'QApplication', mockqtw.MockApplication)
    monkeypatch.setattr(testee, 'Gui', MockGui)
    monkeypatch.setattr(testee, 'HOME', pathlib.Path('/homedir'))
    monkeypatch.setattr(testee, 'root', pathlib.Path('/rootdir'))
    monkeypatch.setattr(testee.settings, 'private_repos', {'tests': 'testscripts'})
    with pytest.raises(SystemExit):
        testee.startapp(types.SimpleNamespace(project=''))
    assert capsys.readouterr().out == ('called Application.__init__\n'
            f"called Gui.__init__() with args ({tmp_path!r}, 'git')\n"
            'called Gui.show()\n'
            'called Application.exec_\n')
    with pytest.raises(SystemExit):
        testee.startapp(types.SimpleNamespace(project='x'))
    assert capsys.readouterr().out == ('called Application.__init__\n'
            "called Gui.__init__() with args (PosixPath('/rootdir/x'), 'git')\n"
            'called Gui.show()\n'
            'called Application.exec_\n')
    with pytest.raises(SystemExit):
        testee.startapp(types.SimpleNamespace(project='tests'))
    assert capsys.readouterr().out == ('called Application.__init__\n'
            "called Gui.__init__() with args (PosixPath('/homedir/testscripts'), 'git')\n"
            'called Gui.show()\n'
            'called Application.exec_\n')
    assert capsys.readouterr().out == ''
    with pytest.raises(SystemExit):
        testee.startapp(types.SimpleNamespace(project='.'))
    assert capsys.readouterr().out == ('called Application.__init__\n'
            f"called Gui.__init__() with args ({tmp_path!r}, 'git')\n"
            'called Gui.show()\n'
            'called Application.exec_\n')
    with pytest.raises(SystemExit):
        testee.startapp(types.SimpleNamespace(project='testscripts'))
    assert capsys.readouterr().out == ('called Application.__init__\n'
            "called Gui.__init__() with args (PosixPath('/homedir/testscripts'), 'git')\n"
            'called Gui.show()\n'
            'called Application.exec_\n')
    counter = 0
    monkeypatch.setattr(testee.pathlib.Path, 'exists', return_false_then_true)
    with pytest.raises(SystemExit):
        testee.startapp(types.SimpleNamespace(project=''))
    assert capsys.readouterr().out == ('called Application.__init__\n'
            f"called Gui.__init__() with args ({tmp_path!r}, 'hg')\n"
            'called Gui.show()\n'
            'called Application.exec_\n')
    monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: False)
    assert testee.startapp(types.SimpleNamespace(project='')) == '. is not a repository'
    assert capsys.readouterr().out == ''


def test_get_locs_for_modules(monkeypatch, capsys):
    """unittest for check_repo.get_locs_for_modules
    """
    def mock_get(*args):
        """stub
        """
        print('called get_locs with args', args)
        return ('fun', 15, 2), ('cls.meth', 12, 20), ('oops', 0, 0)
    monkeypatch.setattr(testee, 'get_locs', mock_get)
    assert testee.get_locs_for_modules(['name1.py', 'path/name2'], 'a path') == [
            '', 'lines of code per function / method for `name1.py`', '',
            'fun: 15 lines (2-16)', 'cls.meth: 12 lines (20-31)', 'oops',
            '', 'lines of code per function / method for `path/name2`', '',
            'fun: 15 lines (2-16)', 'cls.meth: 12 lines (20-31)', 'oops']
    assert capsys.readouterr().out == ("called get_locs with args ('name1', 'a path')\n"
                                       "called get_locs with args ('path.name2', 'a path')\n")


def test_get_locs():
    """unittest for check_repo.get_locs
    """
    tempfile = pathlib.Path('test_get_locs.py')
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


def test_get_locs_for_unit_err_1(monkeypatch):
    """unittest for check_repo.get_locs_for_unit geeft TypeError
    """
    def mock_get(arg):
        """stub
        """
        raise TypeError
    monkeypatch.setattr(testee.inspect, 'getsourcelines', mock_get)
    assert testee.get_locs_for_unit('x', 'y') == (0, 0, 'wrong type for getsourcelines'
                                                  ' - skipped: x y')


def test_get_locs_for_unit_err_2(monkeypatch):
    """unittest for check_repo.get_locs_for_unit geeft OSError
    """
    def mock_get(arg):
        """stub
        """
        raise OSError('this')
    monkeypatch.setattr(testee.inspect, 'getsourcelines', mock_get)
    assert testee.get_locs_for_unit('x', 'y') == (0, 0, 'this for x y')


def test_get_locs_for_unit(monkeypatch):
    """unittest for check_repo.get_locs_for_unit
    """
    def mock_get(arg):
        """stub
        """
        return ['line1', 'x', 'y', 'z', 'last line'], 2
    monkeypatch.setattr(testee.inspect, 'getsourcelines', mock_get)
    assert testee.get_locs_for_unit('x', 'y') == (4, 3, '')


class TestCheckTextDialog:
    """unittests for check_repo.CheckTextDialog
    """
    def test_init(self, monkeypatch, capsys, expected_output):
        """unittest for CheckTextDialog.init
        """
        monkeypatch.setattr(testee.qtw.QDialog, '__init__', mock_dialog_init)
        monkeypatch.setattr(testee.qtw.QDialog, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(testee.qtw.QDialog, 'setLayout', mock_setLayout)
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.qtw, 'QLineEdit', mockqtw.MockLineEdit)
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        testobj = testee.CheckTextDialog('parent', 'title', 'message')
        assert capsys.readouterr().out == expected_output['checktextdialog'].format(testobj=testobj)

    def test_accept(self, monkeypatch, capsys):
        """unittest for CheckTextDialog.accept
        """
        def mock_accept(self, *args):
            """stub
            """
            print('called dialog.accept()')
        def mock_init(self, *args):
            """stub
            """
            print('called dialog.__init__()')
            self._parent = args[0]
        monkeypatch.setattr(testee.qtw.QDialog, 'accept', mock_accept)
        monkeypatch.setattr(testee.CheckTextDialog, '__init__', mock_init)
        test_obj = testee.CheckTextDialog(types.SimpleNamespace(dialog_data=()))
        test_obj.check = mockqtw.MockCheckBox()
        test_obj.text = mockqtw.MockLineEdit()
        test_obj.check.setChecked(True)
        test_obj.text.setText('text')
        test_obj.accept()
        assert test_obj._parent.dialog_data == (True, 'text')
        assert capsys.readouterr().out == (
            'called dialog.__init__()\n'
            'called CheckBox.__init__\n'
            'called LineEdit.__init__\n'
            'called CheckBox.setChecked with arg True\n'
            'called LineEdit.setText with arg `text`\n'
            'called CheckBox.isChecked\n'
            'called LineEdit.text\n'
            'called dialog.accept()\n')


class TestDiffViewDialog:
    """unittests for check_repo.DiffViewDialog
    """
    def test_init(self, monkeypatch, capsys, expected_output):
        """unittest for DiffViewDialog.init
        """
        def mock_resize(self, *args):
            """stub
            """
            print('called dialog.resize()')
        def mock_addAction(self, *args):
            """stub
            """
            print('called dialog.addAction()')
        monkeypatch.setattr(testee.qtw.QDialog, '__init__', mock_dialog_init)
        monkeypatch.setattr(testee.qtw.QDialog, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(testee.qtw.QDialog, 'resize', mock_resize)
        monkeypatch.setattr(testee.qtw.QDialog, 'setLayout', mock_setLayout)
        monkeypatch.setattr(testee.qtw.QDialog, 'addAction', mock_addAction)
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.sci, 'QsciScintilla', mockqtw.MockEditorWidget)
        monkeypatch.setattr(testee.sci, 'QsciLexerDiff', mockqtw.MockLexerDiff)
        monkeypatch.setattr(testee.gui, 'QFont', mockqtw.MockFont)
        monkeypatch.setattr(testee.gui, 'QFontMetrics', mockqtw.MockFontMetrics)
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        monkeypatch.setattr(testee.qtw, 'QAction', mockqtw.MockAction)
        monkeypatch.setattr(testee.gui, 'QColor', mockqtw.MockColor)
        caption = 'caption'
        testobj = testee.DiffViewDialog('parent', 'title', caption)
        assert testobj.data == ''
        assert capsys.readouterr().out == expected_output['diffviewdialog'].format(testobj=testobj,
                                                                                   caption=caption)
        caption = 'Show loc-counts caption'
        testobj = testee.DiffViewDialog('parent', 'title', caption, 'data')
        assert testobj.data == 'data'
        assert capsys.readouterr().out == expected_output['diffviewdialog2'].format(testobj=testobj,
                                                                                    caption=caption)

    def _test_setup_text(self, monkeypatch, capsys):
        """stub

        geen aparte test, want deze wordt aangeroepen tijdens __init__ en geen idee hoe ik dat kan
        monkeypatchen
        kan misschien door het opzetten van de tekst in een aparte routine te doen maar waarom zou ik
        """

    def test_export(self, monkeypatch, capsys):
        class MockClipBoard:
            """stub
            """
            def setText(self, text):
                print(f"called QClipBoard.setText with arg '{text}'")
        def mock_clipboard():
            # print('called QApplication.clipboard')
            return MockClipBoard()
        monkeypatch.setattr(testee.DiffViewDialog, '__init__', mock_dialog_init)
        monkeypatch.setattr(testee.qtw.QApplication, 'clipboard', mock_clipboard)
        testobj = testee.DiffViewDialog('parent', 'title', 'caption')
        testobj.data = ('lines of code for `module`\n\n'
                        'method: 1 lines (2)  \nfunction: 10 lines (5-14)\n\n'
                        'lines of code for `other/module`\n\n'
                        'nothing found\n\n'
                        'lines of code for `third/module.py`\n\n'
                        'method: 1 lines (2)  \nfunction: 10 lines (5-14)\n\n')
        testobj.export()
        assert capsys.readouterr().out == (
                "called dialog.__init()__ with args ('title', 'caption')\n"
                "called QClipBoard.setText with arg 'module: `module`\n"
                "2         method (1)\n"
                "5-14      function (10)\n"
                "====\nmodule: `third/module.py`\n"
                "2         method (1)\n"
                "5-14      function (10)'\n")


class TestFriendlyReminder:
    """unittests for check_repo.FriendlyReminder
    """
    def test_init(self, monkeypatch, capsys, expected_output):
        """unittest for FriendlyReminder.init
        """
        monkeypatch.setattr(testee.qtw.QDialog, '__init__', mock_dialog_init)
        monkeypatch.setattr(testee.qtw.QDialog, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(testee.qtw.QDialog, 'setLayout', mock_setLayout)
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        testobj = testee.FriendlyReminder('parent')
        assert capsys.readouterr().out == expected_output['friendlyreminder'].format(testobj=testobj)

    def test_accept(self, monkeypatch, capsys):
        """unittest for FriendlyReminder.accept
        """
        def mock_accept(self, *args):
            """stub
            """
            print('called dialog.accept()')
        def mock_init(self, *args):
            """stub
            """
            print('called dialog.__init__()')
            self._parent = args[0]
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee.qtw.QDialog, 'accept', mock_accept)
        monkeypatch.setattr(testee.FriendlyReminder, '__init__', mock_init)
        testobj = testee.FriendlyReminder(types.SimpleNamespace(title='title'))
        testobj.complete = mockqtw.MockCheckBox()
        testobj.tested = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == ('called dialog.__init__()\n'
                                           'called CheckBox.__init__\n'
                                           'called CheckBox.__init__\n')
        testobj.complete.setChecked(False)
        testobj.accept()
        assert capsys.readouterr().out == ('called CheckBox.setChecked with arg False\n'
                                           'called CheckBox.isChecked\n'
                                           "display message `You didn't tick all the boxes`\n")
        testobj.complete.setChecked(True)
        testobj.accept()
        assert capsys.readouterr().out == ('called CheckBox.setChecked with arg True\n'
                                           'called CheckBox.isChecked\n'
                                           'called dialog.accept()\n')


class TestGui:
    """unittests for check_repo.Gui
    """
    def _test_init(self):
        """stub

        Ik denk dat deze automatisch wordt doorlopen in de testobj fixture
        en ook in de methoden die de routines aangeroepen in __init__ testen
        """

    def test_setup_visual(self, monkeypatch, capsys, expected_output):
        """unittest for Gui.setup_visual
        """
        # wordt aangeroepen in __init__ daarom niet via fixture testen
        # de andere methode in de init en de methoden die deze aanroept wel mocken
        def mock_init(self, *args):
            """stub
            """
            # self.parent = parent
            print('called widget.__init()__ with args', args)
        def mock_setWindowTitle(self, *args):
            """stub
            """
            print('called widget.setWindowTitle() with args', args)
        def mock_setLayout(self, *args):
            """stub
            """
            print('called widget.setLayout()')
        def mock_setWindowIcon(self, *args):
            """stub
            """
            print('called widget.setWindowIcon()')
        def mock_resize(self, *args):
            """stub
            """
            print('called widget.resize()')
        def mock_setup_stashmenu(self, *args):
            """stub
            """
            print('called widget.setup_stashmenu()')
        def mock_addAction(self, *args):
            """stub
            """
            print('called widget.addAction()')
        monkeypatch.setattr(testee.qtw, 'QApplication', mockqtw.MockApplication)
        monkeypatch.setattr(testee.qtw.QWidget, '__init__', mock_init)
        monkeypatch.setattr(testee.qtw.QWidget, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(testee.gui, 'QIcon', mockqtw.MockIcon)
        monkeypatch.setattr(testee.qtw.QWidget, 'setWindowIcon', mock_setWindowIcon)
        monkeypatch.setattr(testee.qtw.QWidget, 'resize', mock_resize)
        monkeypatch.setattr(testee.qtw.QWidget, 'setLayout', mock_setLayout)
        monkeypatch.setattr(testee.qtw.QWidget, 'addAction', mock_addAction)
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        monkeypatch.setattr(testee.qtw, 'QComboBox', mockqtw.MockComboBox)
        monkeypatch.setattr(testee.qtw, 'QListWidget', mockqtw.MockListBox)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.sci, 'QsciScintilla', mockqtw.MockEditorWidget)
        monkeypatch.setattr(testee.sci, 'QsciLexerDiff', mockqtw.MockLexerDiff)
        monkeypatch.setattr(testee.gui, 'QFont', mockqtw.MockFont)
        monkeypatch.setattr(testee.gui, 'QFontMetrics', mockqtw.MockFontMetrics)
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        monkeypatch.setattr(testee.qtw, 'QMenu', mockqtw.MockMenu)
        monkeypatch.setattr(testee.qtw, 'QAction', mockqtw.MockAction)
        monkeypatch.setattr(testee.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(testee.Gui, 'refresh_frame', mock_refresh_frame)
        monkeypatch.setattr(testee.Gui, 'setup_stashmenu', mock_setup_stashmenu)
        testobj = testee.Gui(pathlib.Path('base'), 'git')
        bindings = dict(tooltips.items())
        bindings['testobj'] = testobj
        assert capsys.readouterr().out == expected_output['maingui'].format(**bindings)

    def test_refresh_frame(self, monkeypatch, capsys, expected_output):
        """unittest for Gui.refresh_frame
        """
        # wordt aangeroepen in __init__ daarom niet via fixture testen
        # de andere methode in de init en de methoden die deze aanroept wel mocken
        def mock_init(self, *args):
            """stub
            """
            print('called QMainWindow.__init__()')
        def mock_populate(self):
            """stub
            """
            print('called Gui.populate_frame()')
        monkeypatch.setattr(testee.qtw, 'QApplication', mockqtw.MockApplication)
        monkeypatch.setattr(testee.qtw.QWidget, '__init__', mock_init)
        monkeypatch.setattr(testee.qtw, 'QWidget', mockqtw.MockWidget)
        monkeypatch.setattr(testee.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(testee.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(testee.Gui, 'populate_frame', mock_populate)
        testee.Gui(pathlib.Path('base'), 'git')
        assert capsys.readouterr().out == expected_output['refresh_frame']

    def test_get_repofiles(self, monkeypatch, capsys, expected_output):
        """unittest for Gui.get_repofiles
        """
        # de verschillende varianten uitproberen nadat de klasse is opgezet
        # omdat deze methode daarbij al wordt aangeroepen kan dat niet via de testobj fixture
        def mock_init(self, *args):
            """stub
            """
            print('called QMainWindow.__init__()')
        monkeypatch.setattr(testee.subprocess, 'run', mock_sp_run)
        monkeypatch.setattr(testee.qtw, 'QApplication', mockqtw.MockApplication)
        monkeypatch.setattr(testee.qtw.QWidget, '__init__', mock_init)
        monkeypatch.setattr(testee.qtw, 'QWidget', mockqtw.MockWidget)
        monkeypatch.setattr(testee.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(testee.Gui, 'refresh_frame', mock_refresh_frame)
        test_obj = setup_app(monkeypatch)
        assert capsys.readouterr().out == expected_output['get_repofiles']
        test_obj.repotype = 'hg'
        test_obj.outtype = 'status'
        assert test_obj.get_repofiles() == ['hallo', 'daar', 'jongens']
        assert capsys.readouterr().out == ("run with args: (['hg', 'status'],)"
                                           " {'stdout': -1, 'cwd': 'base', 'check': False}\n")
        test_obj.repotype = 'git'
        test_obj.outtype = 'status'
        assert test_obj.get_repofiles() == ['hallo', 'daar', 'jongens']
        assert capsys.readouterr().out == ("run with args: (['git', 'status', '--short'],)"
                                           " {'stdout': -1, 'cwd': 'base', 'check': False}\n")
        test_obj.repotype = 'hg'
        test_obj.outtype = 'repolist'
        assert test_obj.get_repofiles() == ['hallo', 'daar', 'jongens']
        assert capsys.readouterr().out == ("run with args: (['hg', 'manifest'],)"
                                           " {'stdout': -1, 'cwd': 'base', 'check': False}\n")
        test_obj.repotype = 'git'
        test_obj.outtype = 'repolist'
        assert test_obj.get_repofiles() == ['hallo', 'daar', 'jongens']
        assert capsys.readouterr().out == ("run with args: (['git', 'ls-files'],)"
                                           " {'stdout': -1, 'cwd': 'base', 'check': False}\n")

    def test_populate_frame(self, monkeypatch, capsys, expected_output):
        """unittest for Gui.populate_frame
        """
        def mock_setWindowTitle(self, *args):
            """stub
            """
            print('called QWidget.setWindowTitle() with args', args)
        def mock_setWindowIcon(self, *args):
            """stub
            """
            print('called QWidget.setWindowIcon()`')
        monkeypatch.setattr(testee.subprocess, 'run', mock_sp_run)
        monkeypatch.setattr(testee.qtw.QWidget, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(testee.qtw.QWidget, 'setWindowIcon', mock_setWindowIcon)
        monkeypatch.setattr(testee.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(testee.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(testee.Gui, 'update_branches', mock_update_branches)
        test_obj = setup_app(monkeypatch)
        test_obj.populate_frame()   # nog een keer om expliciet aan te roepen
        assert capsys.readouterr().out == expected_output['populate_frames']

    def test_get_selected_files(self, monkeypatch, capsys, testobj):
        """unittest for Gui.get_selected_files
        """
        def mock_select():
            """stub
            """
            return mockqtw.MockListItem('M  item1'), mockqtw.MockListItem('?? item2')
        monkeypatch.setattr(testobj.list, 'selectedItems', mock_select)
        testobj.outtype = ''
        assert testobj.get_selected_files() == [('', 'M  item1'), ('', '?? item2')]
        assert capsys.readouterr().out == ('called ListItem.__init__\n'
                                           'called ListItem.__init__\n')
        testobj.outtype = 'status'
        assert testobj.get_selected_files() == [['M', 'item1'], ['??', 'item2']]
        assert capsys.readouterr().out == ('called ListItem.__init__\n'
                                           'called ListItem.__init__\n')

    def test_edit_selected(self, monkeypatch, capsys, testobj):
        """unittest for Gui.edit_selected
        """
        def mock_get_selected():
            """stub
            """
            return ('', 'file1'), ('', 'file2')
        monkeypatch.setattr(testobj, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(testobj, 'just_run', mock_just_run)
        testobj.edit_selected()
        assert capsys.readouterr().out == ("call just_run() for `['gnome-terminal', '--profile',"
                                           " 'Code Editor Shell', '--', 'vim', 'file1', 'file2']`\n"
                                           'called Gui.refresh_frame()\n')

    def test_count_all(self, monkeypatch, capsys, testobj):
        """unittest for Gui.count_all
        """
        def mock_filter_modules():
            """stub
            """
            print('called Gui.filter_modules')
            return ['all', 'tracked', 'modules']
        def mock_filter_none():
            """stub
            """
            print('called Gui.filter_modules')
            return []
        def mock_get(*args):
            """stub
            """
            print('called get_locs_for_modules with args', args)
            return ['loc-count-line1', 'loc-count-line2']
        class MockDiffView:
            """stub
            """
            def __init__(self, *args):
                """stub
                """
                print('called DiffViewDialog with args', args[1:])
            def exec_(self):
                """stub
                """
                print('exec dialog')
        monkeypatch.setattr(testobj, 'filter_modules', mock_filter_modules)
        monkeypatch.setattr(testee, 'get_locs_for_modules', mock_get)
        monkeypatch.setattr(testee, 'DiffViewDialog', MockDiffView)
        testobj.count_all()
        assert capsys.readouterr().out == (
                'called Gui.filter_modules\n'
                "called get_locs_for_modules with args (['all', 'tracked', 'modules'],"
                " PosixPath('base'))\n"
                "called DiffViewDialog with args ('Uncommitted changes for `base`',"
                " 'Show loc-counts for all tracked modules', 'loc-count-line1\\nloc-count-line2',"
                " (600, 400))\n"
                'exec dialog\n')
        monkeypatch.setattr(testobj, 'filter_modules', mock_filter_none)
        testobj.count_all()
        assert capsys.readouterr().out == 'called Gui.filter_modules\n'

    def test_count_selected(self, monkeypatch, capsys, testobj):
        """unittest for Gui.count_selected
        """
        def mock_get_selected():
            """stub
            """
            print('called get_selected_filenames')
            return 'file1', 'file2'
        def mock_filter_tracked(*args):
            """stub
            """
            print('called Gui.filter_tracked')
            return list(*args)
        def mock_filter_none(*args):
            """stub
            """
            print('called Gui.filter_tracked')
            return []
        def mock_get(*args):
            """stub
            """
            print('called get_locs_for_modules with args', args)
            return ['loc-count-line1', 'loc-count-line2']
        class MockDiffView:
            """stub
            """
            def __init__(self, *args):
                """stub
                """
                print('called DiffViewDialog with args', args[1:])
            def exec_(self):
                """stub
                """
                print('exec dialog')
        monkeypatch.setattr(testobj, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(testobj, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(testee, 'get_locs_for_modules', mock_get)
        monkeypatch.setattr(testee, 'DiffViewDialog', MockDiffView)
        testobj.count_selected()
        assert capsys.readouterr().out == (
                'called get_selected_filenames\n'
                'called Gui.filter_tracked\n'
                "called get_locs_for_modules with args (['file1', 'file2'], PosixPath('base'))\n"
                "called DiffViewDialog with args ('Uncommitted changes for `base`',"
                " 'Show loc-counts for: file1, file2', 'loc-count-line1\\nloc-count-line2',"
                " (600, 400))\n"
                'exec dialog\n')
        monkeypatch.setattr(testobj, 'filter_tracked', mock_filter_none)
        testobj.count_selected()
        assert capsys.readouterr().out == ('called get_selected_filenames\n'
                                           'called Gui.filter_tracked\n')

    def test_diff_all(self, monkeypatch, capsys, testobj):
        """unittest for Gui.diff_all
        """
        def mock_just_run_exc(command):
            """stub
            """
            raise OSError('run commando gaat fout')
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)

        monkeypatch.setattr(testobj, 'just_run', mock_just_run)
        testobj.got_meld = False
        testobj.diff_all()
        assert capsys.readouterr().out == ('display message `Sorry, not possible at this time'
                                           ' - Meld not installed`\n')

        monkeypatch.setattr(testobj, 'just_run', mock_just_run_exc)
        testobj.got_meld = True
        testobj.diff_all()
        assert capsys.readouterr().out == ('display message `Sorry, not possible at this time'
                                           ' - Meld not installed`\n')

        monkeypatch.setattr(testobj, 'just_run', mock_just_run)
        testobj.got_meld = True
        testobj.diff_all()
        assert capsys.readouterr().out == ("call just_run() for `['meld', '.']`\n")

    def test_diff_selected(self, monkeypatch, capsys, testobj):
        """unittest for Gui.diff_selected
        """
        def mock_get_selected():
            """stub
            """
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_filter_tracked(*args):
            """stub
            """
            print('call filter_tracked()')
            return list(*args)
        def mock_just_run_exc(command):
            """stub
            """
            print(f'call just_run() for `{command}`')
            raise OSError
        def mock_run_and_capture(command):
            """stub
            """
            print(f'call run_and_capture() for `{command}`')
            return ['out', 'put'], []
        def mock_run_and_capture_err(command):
            """stub
            """
            print(f'call run_and_capture() for `{command}`')
            return ['', ''], ['er', 'ror']
        class MockDiffView:
            """stub
            """
            def __init__(self, *args):
                """stub
                """
                print('call DiffViewDialog with args', args[1:])
            def exec_(self):
                """stub
                """
                print('exec dialog')
        monkeypatch.setattr(testobj, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(testobj, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(testobj, 'just_run', mock_just_run)
        monkeypatch.setattr(testobj, 'run_and_capture', mock_run_and_capture)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee, 'DiffViewDialog', MockDiffView)
        testobj.got_meld = False
        testobj.diff_selected()
        assert capsys.readouterr().out == (
                'call get_selected_filenames()\n'
                'call filter_tracked()\n'
                "call run_and_capture() for `['git', 'diff', 'file1', 'file2']`\n"
                "call DiffViewDialog with args ('Uncommitted changes for `base`',"
                " 'Show diffs for: file1, file2', ['out', 'put'])\n"
                'exec dialog\n')
        monkeypatch.setattr(testobj, 'run_and_capture', mock_run_and_capture_err)
        testobj.diff_selected()
        assert capsys.readouterr().out == (
                'call get_selected_filenames()\n'
                'call filter_tracked()\n'
                "call run_and_capture() for `['git', 'diff', 'file1', 'file2']`\n"
                'display message `er\nror`\n')
        testobj.got_meld = True
        testobj.diff_selected()
        assert capsys.readouterr().out == (
                'call get_selected_filenames()\n'
                'call filter_tracked()\n'
                "call just_run() for `['meld', 'file1']`\n"
                "call just_run() for `['meld', 'file2']`\n")
        monkeypatch.setattr(testobj, 'just_run', mock_just_run_exc)
        testobj.diff_selected()
        assert capsys.readouterr().out == (
                'call get_selected_filenames()\n'
                'call filter_tracked()\n'
                "call just_run() for `['meld', 'file1']`\n"
                "call run_and_capture() for `['git', 'diff', 'file1', 'file2']`\n"
                'display message `er\nror`\n')

    def test_add_ignore(self, monkeypatch, capsys, tmp_path, testobj):
        """unittest for Gui.add_ignore
        """
        def mock_filter(*args):
            """stub
            """
            print('called Gui.filter_tracked() with args', args)
            return 'file1', 'file2'
        def mock_get_selected():
            """stub
            """
            print('called Gui.get_selected_files')
            return ('??', 'file1'), ('', 'file2')

        monkeypatch.setattr(testobj, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(testobj, 'filter_tracked', mock_filter)
        testobj.repotype = 'hg'
        testobj.path = tmp_path
        ignorefile = tmp_path / '.hgignore'
        assert not ignorefile.exists()
        testobj.add_ignore()
        assert ignorefile.exists()
        assert capsys.readouterr().out == ('called Gui.get_selected_files\n'
                                           'called Gui.refresh_frame()\n')
        assert ignorefile.read_text() == ('file1\nfile2\n')
        ignorefile.unlink()

        testobj.repotype = 'not hg'
        testobj.path = tmp_path
        ignorefile = tmp_path / '.gitignore'
        assert not ignorefile.exists()
        testobj.add_ignore()
        assert ignorefile.exists()
        assert capsys.readouterr().out == ('called Gui.get_selected_files\n'
                                           'called Gui.refresh_frame()\n')
        assert ignorefile.read_text() == ('file1\nfile2\n')
        ignorefile.unlink()

    def test_add_new(self, monkeypatch, capsys, testobj):
        """unittest for Gui.add_new
        """
        def mock_run(*args):
            """stub
            """
            print('run_and_report with args:', *args)
        def mock_get_selected():
            """stub
            """
            print('called Gui.get_selected_files')
            return ('??', 'file1'), ('', 'file2')

        monkeypatch.setattr(testobj, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(testobj, 'run_and_report', mock_run)
        testobj.add_new()
        assert capsys.readouterr().out == ('called Gui.get_selected_files\n'
                                           "run_and_report with args:"
                                           " ['git', 'add', 'file1', 'file2']\n"
                                           'called Gui.refresh_frame()\n')

    def test_forget(self, monkeypatch, capsys, testobj):
        """unittest for Gui.forget
        """
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        def mock_get_selected(self):
            """stub
            """
            print('called Gui.get_selected_files')
            return ('??', 'file1'), ('', 'file2')

        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        testobj.repotype = 'hg'
        testobj.forget()
        assert capsys.readouterr().out == ('called Gui.get_selected_files\n'
                                           "run_and_report with args:"
                                           " ['hg', 'forget', 'file1', 'file2']\n"
                                           'called Gui.refresh_frame()\n')
        testobj.repotype = 'git'
        testobj.forget()
        assert capsys.readouterr().out == ('called Gui.get_selected_files\n'
                                           "run_and_report with args:"
                                           " ['git', 'rm', '--cached', 'file1', 'file2']\n"
                                           'called Gui.refresh_frame()\n')
        testobj.repotype = 'something else'
        with pytest.raises(KeyError):
            testobj.forget()
        assert capsys.readouterr().out == 'called Gui.get_selected_files\n'

    def test_set_outtype(self, capsys, testobj):
        """unittest for Gui.set_outtype
        """
        testobj.cb_list = mockqtw.MockComboBox()
        testobj.set_outtype()
        assert testobj.outtype == 'current text'
        assert capsys.readouterr().out == ('called ComboBox.__init__\n'
                                           'called ComboBox.currentText\n'
                                           'called Gui.refresh_frame()\n')

    def test_commit_all(self, monkeypatch, capsys, testobj):
        """unittest for Gui.commit_all
        """
        def mock_gettext(*args):
            """stub
            """
            return 'commit_message', True
        def mock_gettext_nok(*args):
            """stub
            """
            return '', False
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        monkeypatch.setattr(testee.qtw.QInputDialog, 'getText', mock_gettext)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(mockqtw.MockDialog, 'exec_', lambda *x: testee.qtw.QDialog.Rejected)
        monkeypatch.setattr(testee, 'FriendlyReminder', mockqtw.MockDialog)
        testobj.commit_all()
        assert capsys.readouterr().out == f'called Dialog.__init__ with args {testobj} () {{}}\n'
        monkeypatch.setattr(mockqtw.MockDialog, 'exec_', lambda *x: testee.qtw.QDialog.Accepted)
        monkeypatch.setattr(testee, 'FriendlyReminder', mockqtw.MockDialog)
        testobj.commit_all()
        assert capsys.readouterr().out == (f'called Dialog.__init__ with args {testobj} () {{}}\n'
                                           "run_and_report with args:"
                                           " ['git', 'commit', '-a', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')
        testobj.repotype = 'hg'
        testobj.commit_all()
        assert capsys.readouterr().out == (f'called Dialog.__init__ with args {testobj} () {{}}\n'
                                           "run_and_report with args:"
                                           " ['hg', 'commit', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')
        monkeypatch.setattr(testee.qtw.QInputDialog, 'getText', mock_gettext_nok)
        testobj.commit_all()
        assert capsys.readouterr().out == f'called Dialog.__init__ with args {testobj} () {{}}\n'

    def test_commit_selected(self, monkeypatch, capsys, testobj):
        """unittest for Gui.commit_selected
        """
        def mock_get_selected(self):
            """stub
            """
            print('call get_selected_filenames()')
            return [('M', 'file1'), ('M', 'file2.py'), ('M', 'test_file3.py')]
        def mock_get_selected_none(self):
            """stub
            """
            print('call get_selected_filenames()')
            return []
        def mock_get_selected_nopy(self):
            """stub
            """
            print('call get_selected_filenames()')
            return [('M', 'file1'), ('M', 'file2')]
        def mock_get_selected_test(self):
            """stub
            """
            print('call get_selected_filenames()')
            return [('M', 'test_file1.py'), ('M', 'test_file2.py')]
        def mock_filter_tracked(self, *args):
            """stub
            """
            print('call filter_tracked()')
            return [x[1] for x in list(*args)]
        def mock_gettext(*args):
            """stub
            """
            return 'commit_message', True
        def mock_gettext_nok(*args):
            """stub
            """
            return '', False
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        monkeypatch.setattr(testee.qtw.QInputDialog, 'getText', mock_gettext)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(testee.Gui, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected_none)
        monkeypatch.setattr(mockqtw.MockDialog, 'exec_', lambda *x: testee.qtw.QDialog.Rejected)
        monkeypatch.setattr(testee, 'FriendlyReminder', mockqtw.MockDialog)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n')

        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected_nopy)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run_and_report with args:"
                                           " ['git', 'add', 'file1', 'file2']\n"
                                           "run_and_report with args: ['git',"
                                           " 'commit', 'file1', 'file2', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')

        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected_test)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run_and_report with args:"
                                           " ['git', 'add', 'test_file1.py', 'test_file2.py']\n"
                                           "run_and_report with args: ['git',"
                                           " 'commit', 'test_file1.py', 'test_file2.py', '-m',"
                                           " 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')

        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           f'called Dialog.__init__ with args {testobj} () {{}}\n')

        monkeypatch.setattr(mockqtw.MockDialog, 'exec_', lambda *x: testee.qtw.QDialog.Accepted)
        # monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           f'called Dialog.__init__ with args {testobj} () {{}}\n'
                                           'call filter_tracked()\n'
                                           "run_and_report with args:"
                                           " ['git', 'add', 'file1', 'file2.py', 'test_file3.py']\n"
                                           "run_and_report with args: ['git', 'commit',"
                                           " 'file1', 'file2.py', 'test_file3.py', '-m',"
                                           " 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')

        testobj.repotype = 'hg'
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           f'called Dialog.__init__ with args {testobj} () {{}}\n'
                                           'call filter_tracked()\n'
                                           "run_and_report with args: ['hg', 'commit', 'file1',"
                                           " 'file2.py', 'test_file3.py', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')

        monkeypatch.setattr(testee.qtw.QInputDialog, 'getText', mock_gettext_nok)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           f'called Dialog.__init__ with args {testobj} () {{}}\n'
                                           'call filter_tracked()\n')

    def test_amend_commit(self, monkeypatch, capsys, testobj):
        """unittest for Gui.amend_commit
        """
        def mock_runc(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return (('commit_message', ''), '')
        def mock_get_selected(self):
            """stub
            """
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_filter_tracked(self, *args):
            """stub
            """
            print('call filter_tracked()')
            return list(*args)
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        class MockDialog:
            """stub
            """
            def __init__(self, *args):
                """stub
                """
                self.parent = args[0]
                print('call CheckTextDialog with args', args[1:])
            def exec_(self):
                """stub
                """
                self.parent.dialog_data = True, 'commit_message'
                return testee.qtw.QDialog.Accepted
        class MockDialog_2:
            """stub
            """
            def __init__(self, *args):
                """stub
                """
                self.parent = args[0]
                print('call CheckTextDialog with args', args[1:])
            def exec_(self):
                """stub
                """
                self.parent.dialog_data = True, 'commit_message'
                return testee.qtw.QDialog.Rejected
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_runc)
        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(testee.Gui, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(testee, 'CheckTextDialog', MockDialog)
        testobj.amend_commit()
        assert capsys.readouterr().out == (
                "run_and_capture with args: ['git', 'log', '-1', '--pretty=format:%s']\n"
                "call CheckTextDialog with args ('Uncommitted changes for `base`', 'commit_message')\n"
                "call get_selected_filenames()\n"
                "call filter_tracked()\n"
                "run_and_report with args: ['git', 'add', 'file1', 'file2']\n"
                "run_and_report with args: ['git', 'commit', '--amend', '-m', 'commit_message']\n"
                "called Gui.refresh_frame()\n")
        monkeypatch.setattr(testee, 'CheckTextDialog', MockDialog_2)
        testobj.amend_commit()
        assert capsys.readouterr().out == (
                "run_and_capture with args: ['git', 'log', '-1', '--pretty=format:%s']\n"
                "call CheckTextDialog with args ('Uncommitted changes for `base`',"
                " 'commit_message')\n")
        testobj.repotype = 'not git'
        testobj.amend_commit()
        assert capsys.readouterr().out == 'display message `Only implemented for git repos`\n'

    def test_revert_selected(self, monkeypatch, capsys, testobj):
        """unittest for Gui.revert_selected
        """
        def mock_get_selected(self):
            """stub
            """
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_get_selected_none(self):
            """stub
            """
            print('call get_selected_filenames()')
            return []
        def mock_filter_tracked(self, *args):
            """stub
            """
            print('call filter_tracked()')
            return list(*args)
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(testee.Gui, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected_none)
        testobj.revert_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n')
        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected)
        testobj.revert_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run_and_report with args: ['git', 'checkout', '--',"
                                           " 'file1', 'file2']\n"
                                           'called Gui.refresh_frame()\n')
        testobj.repotype = 'hg'
        testobj.revert_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run_and_report with args: ['hg', 'revert',"
                                           " 'file1', 'file2']\n"
                                           'called Gui.refresh_frame()\n')

    def test_lint_selected(self, monkeypatch, capsys, testobj):
        """unittest for Gui.lint_selected
        """
        def mock_get_selected(self):
            """stub
            """
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_get_selected_1(self):
            """stub
            """
            print('call get_selected_filenames()')
            return ['file1']
        def mock_get_selected_none(self):
            """stub
            """
            print('call get_selected_filenames()')
            return []
        def mock_filter_tracked(self, *args, **kwargs):
            """stub
            """
            print('call filter_tracked()')
            return list(*args)
        def mock_run(self, *args):
            """stub
            """
            print('run with args:', *args)
        monkeypatch.setattr(testee.Gui, 'just_run', mock_run)
        monkeypatch.setattr(testee.Gui, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected_none)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        testobj.lint_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           'display message `No tracked files selected`\n')
        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected)
        testobj.lint_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run with args: ['lintergui', '-m', 'permissive',"
                                           " '-l', 'file1', 'file2']\n")
        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected_1)
        testobj.lint_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run with args: ['lintergui', '-m', 'permissive',"
                                           " '-f', 'file1']\n")

    def test_lint_all(self, monkeypatch, capsys, testobj):
        """unittest for Gui.lint_all
        """
        def mock_run(self, *args):
            """stub
            """
            print('run with args:', *args)
        monkeypatch.setattr(testee.Gui, 'just_run', mock_run)
        testobj.lint_all()
        assert capsys.readouterr().out == ("run with args: ['lintergui', '-m', 'permissive', '-r',"
                                           " 'base']\n")

    def test_annotate(self, monkeypatch, capsys, testobj):
        """unittest for Gui.annotate
        """
        def mock_get_selected(self):
            """stub
            """
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_get_selected_none(self):
            """stub
            """
            print('call get_selected_filenames()')
            return []
        def mock_filter_tracked(self, *args, **kwargs):
            """stub
            """
            print('call filter_tracked()')
            return list(*args)
        def mock_run(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return ['blame', 'output'], []
        def mock_run_err(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return [], ['blame', 'error']
        class MockDialog:
            """stub
            """
            def __init__(self, *args):
                self.parent = args[0]
                print('call DiffViewDialog with args', args[1:])
            def exec_(self):
                """stub
                """
                self.parent.dialog_data = True, 'commit_message'
                return testee.qtw.QDialog.Accepted
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run)
        monkeypatch.setattr(testee.Gui, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected_none)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee, 'DiffViewDialog', MockDialog)
        testobj.annotate()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n')

        monkeypatch.setattr(testee.Gui, 'get_selected_files', mock_get_selected)
        testobj.annotate()
        assert capsys.readouterr().out == (
                'call get_selected_filenames()\n'
                'call filter_tracked()\n'
                "run_and_capture with args: ['git', 'blame', 'file1', 'file2']\n"
                "call DiffViewDialog with args ('Uncommitted changes for `base`',"
                " 'Show annotations for: file1, file2', 'blame\\noutput', (1200, 800))\n")
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run_err)
        testobj.annotate()
        assert capsys.readouterr().out == (
                'call get_selected_filenames()\n'
                'call filter_tracked()\n'
                "run_and_capture with args: ['git', 'blame', 'file1', 'file2']\n"
                'display message `blame\nerror`\n')

    def test_filter_tracked(self, monkeypatch, capsys, testobj):
        """unittest for Gui.filter_tracked
        """
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        assert testobj.filter_tracked([('?', 'file1'), ('', 'file2'), ('??', 'file3'),
            ('M ', 'file4')]) == ['file2', 'file4']
        assert capsys.readouterr().out == ('display message `file1 not tracked`\n'
                                           'display message `file3 not tracked`\n')
        assert testobj.filter_tracked([('?', 'file1'), ('', 'file2'), ('??', 'file3'),
            ('M ', 'file4')], notify=False) == ['file2', 'file4']

    def test_filter_modules(self, monkeypatch, capsys, testobj):
        """unittest for Gui.filter_modules
        """
        def mock_run(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return ['script', 'file.txt', 'module.py', 'test_module.py'], []
        def mock_run_err(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return [], ['error']
        def mock_dirname(name):
            """stub
            """
            if name.startswith('test'):
                return 'testdir'
            return 'dir'
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run_err)
        assert testobj.filter_modules() == []
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'ls-files']\n"
                                           'display message `error`\n')
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run)
        assert testobj.filter_modules() == ['module.py', 'test_module.py']
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'ls-files']\n")
        monkeypatch.setattr(testee.os.path, 'dirname', mock_dirname)
        assert testobj.filter_modules() == ['module.py']
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'ls-files']\n")
        assert testobj.filter_modules(include_tests=True) == ['module.py', 'test_module.py']
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'ls-files']\n")

    def test_view_repo(self, monkeypatch, capsys, testobj):
        """unittest for Gui.view_repo
        """
        def mock_run(self, *args):
            """stub
            """
            print('run with args:', *args)
        monkeypatch.setattr(testee.Gui, 'just_run', mock_run)
        testobj.view_repo()
        assert capsys.readouterr().out == "run with args: ['gitg']\n"
        testobj.repotype = 'hg'
        testobj.view_repo()
        assert capsys.readouterr().out == "run with args: ['hg', 'view']\n"

    def test_update_branches(self, monkeypatch, capsys, testobj):
        """unittest for Gui.update_branches
        """
        def mock_run(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return ['* branch1'], []
        def mock_run_more(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return ['  branch1', '* branch2'], []
        def mock_run_err(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return [], ['branch', 'error']
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run_err)
        testobj.update_branches()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'branch']\n"
                                           'display message `branch\nerror`\n')
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run)
        testobj.update_branches()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'branch']\n"
                                           'called ComboBox.clear\n'
                                           "called ComboBox.addItems with arg ['branch1']\n"
                                           'called ComboBox.setCurrentIndex with arg `0`\n')
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run_more)
        testobj.update_branches()
        assert capsys.readouterr().out == (
                "run_and_capture with args: ['git', 'branch']\n"
                'called ComboBox.clear\n'
                "called ComboBox.addItems with arg ['branch1', 'branch2']\n"
                'called ComboBox.setCurrentIndex with arg `1`\n')
        testobj.repotype = 'not git'
        testobj.update_branches()
        assert capsys.readouterr().out == ''

    def test_create_branch(self, monkeypatch, capsys, testobj):
        """unittest for Gui.create_branch
        """
        def mock_currenttext():
            """stub
            """
            print('called ComboBox.currentText')
            return 'current'
        def mock_find_branch(self):
            """stub
            """
            print('called find_current_branch()')
            return 'branch'
        def mock_find_branch_same(self):
            """stub
            """
            print('called find_current_branch()')
            return 'current'
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        def mock_update_branches(self):
            """stub
            """
            print('called update_branches()')
        monkeypatch.setattr(testee.Gui, 'find_current_branch', mock_find_branch)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(testee.Gui, 'update_branches', mock_update_branches)
        monkeypatch.setattr(testobj.cb_branch, 'currentText', mock_currenttext)
        testobj.create_branch()
        assert capsys.readouterr().out == (
                'called ComboBox.currentText\n'
                'called find_current_branch()\n'
                "run_and_report with args: ['git', 'branch', 'current']\n"
                'called update_branches()\n')
        monkeypatch.setattr(testee.Gui, 'find_current_branch', mock_find_branch_same)
        testobj.create_branch()
        assert capsys.readouterr().out == (
                'called ComboBox.currentText\n'
                'called find_current_branch()\n'
                'display message `Enter a new branch name in the combobox first`\n')
        monkeypatch.setattr(testobj.cb_branch, 'currentText', lambda: '')
        testobj.create_branch()
        assert capsys.readouterr().out == (
                'display message `Enter a new branch name in the combobox first`\n')

    def test_switch2branch(self, monkeypatch, capsys, testobj):
        """unittest for Gui.switch2branch
        """
        def mock_currenttext():
            """stub
            """
            print('called ComboBox.currentText')
            return 'current'
        def mock_find_branch(self):
            """stub
            """
            print('called find_current_branch()')
            return 'branch'
        def mock_find_branch_same(self):
            """stub
            """
            print('called find_current_branch()')
            return 'current'
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        monkeypatch.setattr(testee.Gui, 'find_current_branch', mock_find_branch)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(testobj.cb_branch, 'currentText', mock_currenttext)
        testobj.switch2branch()
        assert capsys.readouterr().out == (
                'called ComboBox.currentText\n'
                'called find_current_branch()\n'
                "run_and_report with args: ['git', 'checkout', 'current']\n"
                'called Gui.refresh_frame()\n')
        monkeypatch.setattr(testee.Gui, 'find_current_branch', mock_find_branch_same)
        testobj.switch2branch()
        assert capsys.readouterr().out == (
                'called ComboBox.currentText\n'
                'called find_current_branch()\n'
                'display message `Select a branch different from the current one first`\n')
        monkeypatch.setattr(testobj.cb_branch, 'currentText', lambda: '')
        testobj.switch2branch()
        assert capsys.readouterr().out == (
                'display message `Select a branch different from the current one first`\n')

    def test_merge_branch(self, monkeypatch, capsys, testobj):
        """unittest for Gui.merge_branch
        """
        def mock_question(self, title, message):
            """stub
            """
            print(f'display question `{message}`')
            return 'not_yes'
        def mock_question_yes(self, title, message):
            """stub
            """
            print(f'display question `{message}`')
            return testee.qtw.QMessageBox.Yes
        def mock_currenttext():
            """stub
            """
            print('called ComboBox.currentText')
            return 'current'
        def mock_find_branch(self):
            """stub
            """
            print('called find_current_branch()')
            return 'branch'
        def mock_find_branch_same(self):
            """stub
            """
            print('called find_current_branch()')
            return 'current'
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        monkeypatch.setattr(testee.Gui, 'find_current_branch', mock_find_branch)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'question', mock_question_yes)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(testobj.cb_branch, 'currentText', mock_currenttext)
        testobj.merge_branch()
        assert capsys.readouterr().out == ('called ComboBox.currentText\n'
                                           'called find_current_branch()\n'
                                           'display question `Merge current into branch?`\n'
                                           "run_and_report with args: ['git', 'merge', 'current']\n"
                                           'called Gui.refresh_frame()\n')
        monkeypatch.setattr(testee.qtw.QMessageBox, 'question', mock_question)
        testobj.merge_branch()
        assert capsys.readouterr().out == ('called ComboBox.currentText\n'
                                           'called find_current_branch()\n'
                                           'display question `Merge current into branch?`\n')
        monkeypatch.setattr(testee.Gui, 'find_current_branch', mock_find_branch_same)
        testobj.merge_branch()
        assert capsys.readouterr().out == ('called ComboBox.currentText\n'
                                           'called find_current_branch()\n'
                                           'display message `Select a branch different from the'
                                           ' current one first`\n')
        monkeypatch.setattr(testobj.cb_branch, 'currentText', lambda: '')
        testobj.merge_branch()
        assert capsys.readouterr().out == ('called find_current_branch()\n'
                                           'display message `Select a branch different from the'
                                           ' current one first`\n')

    def test_delete_branch(self, monkeypatch, capsys, testobj):
        """unittest for Gui.delete_branch
        """
        def mock_currenttext():
            """stub
            """
            print('called ComboBox.currentText')
            return 'current'
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        monkeypatch.setattr(testobj.cb_branch, 'currentText', mock_currenttext)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(testee.Gui, 'update_branches', mock_update_branches)
        testobj.delete_branch()
        assert capsys.readouterr().out == (
                'called ComboBox.currentText\n'
                "run_and_report with args: ['git', 'branch', '-d', 'current']\n"
                'called Gui.update_branches()\n')

    def test_setup_stashmenu(self, monkeypatch, capsys, testobj):
        """unittest for Gui.setup_stashmenu
        """
        monkeypatch.setattr(testee.qtw, 'QMenu', mockqtw.MockMenu)
        monkeypatch.setattr(testee.qtw, 'QAction', mockqtw.MockAction)
        assert isinstance(testobj.setup_stashmenu(), mockqtw.MockMenu)
        assert capsys.readouterr().out == (
                "called Menu.__init__ with args ()\n"
                f"called Action.__init__ with args ('&New Stash', {testobj})\n"
                f'called Signal.connect with args ({testobj.stash_push},)\n'
                'called Menu.addAction\n'
                f"called Action.__init__ with args ('&Apply Stash', {testobj})\n"
                f'called Signal.connect with args ({testobj.stash_pop},)\n'
                'called Menu.addAction\n'
                f"called Action.__init__ with args ('&Remove Stash', {testobj})\n"
                f'called Signal.connect with args ({testobj.stash_kill},)\n'
                'called Menu.addAction\n')

    def test_stash_push(self, monkeypatch, capsys, testobj):
        """unittest for Gui.stash_push
        """
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        testobj.stash_push()
        assert capsys.readouterr().out == ('display message `create stash`\n'
                                           "run_and_report with args: ['git', 'stash', 'push']\n")

    def test_select_stash(self, monkeypatch, capsys, testobj):
        """unittest for Gui.select_stash
        """
        def mock_run(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return ['stash'], []
        def mock_run_none(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return [], []
        def mock_run_err(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return [], ['stash', 'error']
        def mock_getitem(self, title, message, items):
            """stub
            """
            print('call InputDialog.getItem()')
            return 'stash-name: ', True
        def mock_getitem_none(self, title, message, items):
            """stub
            """
            print('call InputDialog.getItem()')
            return '', False
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee.qtw.QInputDialog, 'getItem', mock_getitem)
        assert testobj.select_stash() == 'stash-name'
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'stash', 'list']\n"
                                           'call InputDialog.getItem()\n')
        monkeypatch.setattr(testee.qtw.QInputDialog, 'getItem', mock_getitem_none)
        assert not testobj.select_stash()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'stash', 'list']\n"
                                           'call InputDialog.getItem()\n')
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run_none)
        assert not testobj.select_stash()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'stash', 'list']\n"
                                           'display message `No stashes found`\n')
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run_err)
        assert not testobj.select_stash()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'stash', 'list']\n"
                                           'display message `stash\nerror`\n')

    def test_stash_pop(self, monkeypatch, capsys, testobj):
        """unittest for Gui.stash_pop
        """
        def mock_select(self):
            """stub
            """
            print('call select_stash()')
            return 'name'
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        monkeypatch.setattr(testee.Gui, 'select_stash', mock_select)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        testobj.stash_pop()
        assert capsys.readouterr().out == ('call select_stash()\n'
                                           "run_and_report with args: ['git', 'stash', 'apply',"
                                           " 'name']\n")

    def test_stash_kill(self, monkeypatch, capsys, testobj):
        """unittest for Gui.stash_kill
        """
        def mock_select(self):
            """stub
            """
            print('call select_stash()')
            return 'name'
        def mock_run(self, *args):
            """stub
            """
            print('run_and_report with args:', *args)
        monkeypatch.setattr(testee.Gui, 'select_stash', mock_select)
        monkeypatch.setattr(testee.Gui, 'run_and_report', mock_run)
        testobj.stash_kill()
        assert capsys.readouterr().out == ('call select_stash()\n'
                                           "run_and_report with args: ['git', 'stash', 'drop',"
                                           " 'name']\n")

    def test_open_notes(self, monkeypatch, capsys, testobj):
        """unittest for Gui.open_notes
        """
        def mock_resolve(*args):
            """stub
            """
            print('call path.resolve()')
            return args[0]
        def mock_run(self, *args):
            """stub
            """
            print('run_and_continue with args:', *args)
        monkeypatch.setattr(testee.pathlib.Path, 'resolve', mock_resolve)
        monkeypatch.setattr(testee.Gui, 'run_and_continue', mock_run)
        testobj.path = pathlib.Path('here/this')
        testobj.open_notes()
        assert capsys.readouterr().out == ('call path.resolve()\n'
                                           "run_and_continue with args: ['a-propos', '-n',"
                                           " 'Mee Bezig (This)', '-f', 'mee-bezig']\n")

    def test_open_docs(self, monkeypatch, capsys, testobj):
        """unittest for Gui.open_docs
        """
        def mock_run(self, *args):
            """stub
            """
            print('run_and_continue with args:', *args)
        def mock_get_dir(*args):
            """stub
            """
            print('call settings.get_project_dir')
            return args[0]
        monkeypatch.setattr(testee.settings, 'get_project_dir', mock_get_dir)
        monkeypatch.setattr(testee.Gui, 'run_and_continue', mock_run)
        monkeypatch.setattr(testee.sys, 'argv', ['python'])
        monkeypatch.setattr(testee.os, 'getcwd', lambda: 'here')
        testobj.open_docs()
        assert capsys.readouterr().out == ("run_and_continue with args:"
                                           " ['treedocs', 'here/projdocs.trd']\n")
        monkeypatch.setattr(testee.sys, 'argv', ['python', '.'])
        testobj.open_docs()
        assert capsys.readouterr().out == ("run_and_continue with args:"
                                           " ['treedocs', 'here/projdocs.trd']\n")
        monkeypatch.setattr(testee.sys, 'argv', ['python', 'project'])
        testobj.open_docs()
        assert capsys.readouterr().out == ('call settings.get_project_dir\n'
                                           "run_and_continue with args: ['treedocs',"
                                           " 'project/projdocs.trd']\n")

    def test_open_cgit(self, monkeypatch, capsys, testobj):
        """unittest for Gui.open_cgit
        """
        def mock_run(self, *args):
            """stub
            """
            print('run_and_continue with args:', *args)
        monkeypatch.setattr(testee.Gui, 'run_and_continue', mock_run)
        testobj.open_cgit()
        assert capsys.readouterr().out == ("run_and_continue with args:"
                                           " ['binfab', 'www.startapp', 'cgit']\n")

    def test_open_gitweb(self, monkeypatch, capsys, testobj):
        """unittest for Gui.open_gitweb
        """
        def mock_run(self, *args):
            """stub
            """
            print('run_and_continue with args:', *args)
        monkeypatch.setattr(testee.Gui, 'run_and_continue', mock_run)
        testobj.open_gitweb()
        assert capsys.readouterr().out == ("run_and_continue with args:"
                                           " ['binfab', 'www.startapp', 'gitweb']\n")

    def test_find_current_branch(self, monkeypatch, capsys, testobj):
        """unittest for Gui.find_current_branch
        """
        def mock_run(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return ['* current'], []
        def mock_run_2(self, *args):
            """stub
            """
            print('run_and_capture with args:', *args)
            return ['  branch', '* blarp'], []
        # def mock_run_err(self, *args):
        #     """stub
        #     """
        #     print('run_and_capture with args:', *args)
        #     return [], ['error']
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run)
        assert testobj.find_current_branch() == 'current'
        assert capsys.readouterr().out == "run_and_capture with args: ['git', 'branch']\n"
        monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run_2)
        assert testobj.find_current_branch() == 'blarp'
        assert capsys.readouterr().out == "run_and_capture with args: ['git', 'branch']\n"
        # deze test niet nodig, git branch gaat nooit fout:
        # monkeypatch.setattr(testee.Gui, 'run_and_capture', mock_run_err)
        # assert testobj.find_current_branch() == ''
        # assert capsys.readouterr().out == "run_and_capture with args: ['git', 'branch']\n"

    def test_just_run(self, monkeypatch, capsys, testobj):
        """unittest for Gui.just_run
        """
        monkeypatch.setattr(testee.subprocess, 'run', mock_sp_run)
        testobj.path = pathlib.Path('here')
        testobj.just_run(['command', 'list'])
        assert capsys.readouterr().out == ("run with args: (['command', 'list'],)"
                                           " {'cwd': 'here', 'check': False}\n")

    def test_run_and_continue(self, monkeypatch, capsys, testobj):
        """unittest for Gui.run_and_continue
        """
        monkeypatch.setattr(testee.subprocess, 'Popen', mock_sp_run)
        testobj.path = pathlib.Path('here')
        testobj.run_and_continue(['command', 'list'])
        assert capsys.readouterr().out == "run with args: (['command', 'list'],) {'cwd': 'here'}\n"

    def test_run_and_report(self, monkeypatch, capsys, testobj):
        """unittest for Gui.run_and_report
        """
        def mock_run(*args, **kwargs):
            """stub
            """
            print('run with args:', args, kwargs)
            return types.SimpleNamespace(stdout=b'all\nwent\nwell\n', stderr=None)
        def mock_run_err(*args, **kwargs):
            """stub
            """
            print('run with args:', args, kwargs)
            return types.SimpleNamespace(stdout=None, stderr=b'got\nan\nerror\n')
        def mock_warning(self, title, message):
            """stub
            """
            print(f'display warning `{message}`')
        monkeypatch.setattr(testee.subprocess, 'run', mock_run)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(testee.qtw.QMessageBox, 'warning', mock_warning)
        testobj.run_and_report(['command', 'list'])
        assert capsys.readouterr().out == ("run with args: (['command', 'list'],) {'capture_output':"
                                           " True, 'cwd': 'base', 'check': False}\n"
                                           'display message `all\nwent\nwell`\n')
        monkeypatch.setattr(testee.subprocess, 'run', mock_run_err)
        testobj.run_and_report(['command', 'list'])
        assert capsys.readouterr().out == ("run with args: (['command', 'list'],) {'capture_output':"
                                           " True, 'cwd': 'base', 'check': False}\n"
                                           'display warning `got\nan\nerror`\n')

    def test_run_and_capture(self, monkeypatch, capsys, testobj):
        """unittest for Gui.run_and_capture
        """
        def mock_run(*args, **kwargs):
            """stub
            """
            print('run with args:', args, kwargs)
            return types.SimpleNamespace(stdout=b'all\nwent\nwell\n', stderr=None)
        def mock_run_err(*args, **kwargs):
            """stub
            """
            print('run with args:', args, kwargs)
            return types.SimpleNamespace(stdout=None, stderr=b'got\nan\nerror\n')
        monkeypatch.setattr(testee.subprocess, 'run', mock_run)
        assert testobj.run_and_capture(['command', 'list']) == (['all', 'went', 'well'], [])
        assert capsys.readouterr().out == ("run with args: (['command', 'list'],) {'capture_output':"
                                           " True, 'cwd': 'base', 'check': False}\n")
        monkeypatch.setattr(testee.subprocess, 'run', mock_run_err)
        assert testobj.run_and_capture(['command', 'list']) == ([], ['got', 'an', 'error'])
        assert capsys.readouterr().out == ("run with args: (['command', 'list'],) {'capture_output':"
                                           " True, 'cwd': 'base', 'check': False}\n")
