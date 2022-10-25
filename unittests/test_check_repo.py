import types
import pathlib
import pytest

import check_repo
from check_repo_tooltips import tooltips

@pytest.fixture
def testobj(monkeypatch, capsys):
    def mock_init(self, *args):
        print('called QMainWindow.__init__()')
    monkeypatch.setattr(check_repo.qtw, 'QApplication', MockApplication)
    monkeypatch.setattr(check_repo.qtw.QWidget, '__init__', mock_init)
    monkeypatch.setattr(check_repo.qtw, 'QWidget', MockWidget)
    monkeypatch.setattr(check_repo.Gui, 'get_repofiles', mock_get_repofiles)
    monkeypatch.setattr(check_repo.Gui, 'setup_visual', mock_setup_visual)
    monkeypatch.setattr(check_repo.Gui, 'refresh_frame', mock_refresh_frame)
    app = check_repo.Gui(pathlib.Path('base'), 'git')
    capsys.readouterr()  # swallow stdout/stderr
    return app

def setup_app(monkeypatch):
    def mock_init(self, *args):
        print('called QMainWindow.__init__()')
    monkeypatch.setattr(check_repo.qtw, 'QApplication', MockApplication)
    monkeypatch.setattr(check_repo.qtw.QWidget, '__init__', mock_init)
    monkeypatch.setattr(check_repo.qtw, 'QWidget', MockWidget)
    return check_repo.Gui(pathlib.Path('base'), 'git')

def mock_run(*args):
    print('run with args:', args)

def mock_sp_run(*args, **kwargs):
    print('run with args:', args, kwargs)
    return types.SimpleNamespace(stdout=b'hallo\ndaar\njongens\n')

def mock_setup_visual(self, *args):
    print('called Gui.setup_visual()')
    self.list = MockListWidget()
    self.cb_branch = MockComboBox()

def mock_refresh_frame(self, *args):
    print('called Gui.refresh_frame()')

def mock_get_repofiles(self):
    print('called Gui.get_repofiles()')
    return 'file1.py', 'file2.py'

def mock_update_branches(self):
    print('called Gui.update_branches()')

# --- redefine gui elements to make testing easier (or possible at all)
class MockApplication:
    def __init__(self, *args):
        print('called MockApplication.__init__()')
    def exec_(self):
        print('called MockApplication.exec_()')


class MockGui:
    def __init__(self, *args):
        self.app = MockApplication()
        print('called Gui.__init__() with args', args)
    def show(self):
        print('called Gui.show()')
    def get_menudata(self):
        pass
    def callback(self):
        pass
    def check_active(self, *args):
        print('called Gui.check_active()')
    def activate_item(self, *args):
        print('called Gui.activate_item() with arg `{}`'.format(args[0]))
    def update(self):
        print('called Gui.update()')


class MockWidget:
    def __init__(self):
        print('called QWidget.__init__()')
    def setWindowTitle(self, *args):
        print('called QWidget.setWindowTitle() with args `{}`'.format(args))
    def setWindowIcon(self, *args):
        print('called QWidget.setWindowIcon()`')
    def resize(self, *args):
        print('called QWidget.resize() with args `{}`'.format(args))


class MockIcon:
    def __init__(self, *args):
        print('called Icon.__init__() for `{}`'.format(args[0]))
    def fromTheme(self, *args):
        print('called Icon.fromTheme() with args', args)


class MockMenuBar:
    def __init__(self):
        self.menus = []
    def clear(self):
        self.menus = []
    def addMenu(self, text):
        newmenu = MockMenu(text)
        self.menus.append(newmenu)
        return newmenu


class MockMenu:
    def __init__(self, text=''):
        self.menutext = text
        self.actions = []
    def addAction(self, newaction):
        if isinstance(newaction, str):
            newaction = MockAction(newaction, None)
        self.actions.append(newaction)
        return newaction
    def addSeparator(self):
        newaction = MockAction('-----', None)
        self.actions.append(newaction)
        return newaction


class MockSignal:
    def __init__(self, *args):
        print('called signal.__init__()')
    def connect(self, *args):
        print('called signal.connect()')


class MockAction:
    triggered = MockSignal()
    def __init__(self, text, func):
        print('create QAction with text `{}`'.format(text))
        self.label = text
        self.callback = func
        self.shortcuts = []
        self.checkable = self.checked = False
        self.statustip = ''
    def setCheckable(self, state):
        self.checkable = state
    def setChecked(self, state):
        self.checked = state
    def setShortcut(self, data):
        print('call action.setShortcut with arg `{}`'.format(data))
    def setShortcuts(self, data):
        self.shortcuts = data
    def setStatusTip(self, data):
        self.statustip = data


class MockStatusBar:
    def showMessage(self, *args):
        print('called statusbar.showMessage({})'.format(args[0]))


class MockDialog:
    def __init__(self, parent, *args):
        self.parent = parent
        print('called dialog.__init()__ with args `{}`'.format(args))
    def exec_(self):
        self.parent.dialog_data = {'x': 'y'}
        return check_repo.qtw.QDialog.Accepted
    def setWindowTitle(self, *args):
        print('called dialog.setWindowTitle() with args `{}`'.format(args))
    def setLayout(self, *args):
        print('called dialog.setLayout()')
    def accept(self):
        print('called dialog.accept()')
        return check_repo.qtw.QDialog.Accepted
    def reject(self):
        print('called dialog.reject()')
        return check_repo.qtw.QDialog.Rejected


class MockVBoxLayout:
    def __init__(self, *args):
        print('called MockVBoxLayout.__init__()')
    def addWidget(self, *args):
        print('called vbox.addWidget()')
    def addLayout(self, *args):
        print('called vbox.addLayout()')
    def addStretch(self, *args):
        print('called vbox.addStretch()')
    def addSpacing(self, *args):
        print('called vbox.addSpacing()')


class MockHBoxLayout:
    def __init__(self, *args):
        print('called MockHBoxLayout.__init__()')
    def addWidget(self, *args):
        print('called hbox.addWidget()')
    def addLayout(self, *args):
        print('called hbox.addLayout()')
    def addStretch(self, *args):
        print('called hbox.addStretch()')
    def insertStretch(self, *args):
        print('called hbox.insertStretch()')


class MockGridLayout:
    def __init__(self, *args):
        print('called MockGridLayout.__init__()')
    def addWidget(self, *args):
        print('called grid.addWidget()')
    def addLayout(self, *args):
        print('called grid.addLayout()')
    def addStretch(self, *args):
        print('called grid.addStretch()')


class MockLabel:
    def __init__(self, *args):
        print('called MockLabel.__init__()')


class MockCheckBox:
    def __init__(self, *args):
        print('called MockCheckBox.__init__()')
        self.checked = None
    def setChecked(self, value):
        print('called check.setChecked({})'.format(value))
        self.checked = value
    def isChecked(self):
        print('called check.isChecked()')
        return self.checked


class MockComboBox:
    currentIndexChanged = MockSignal()
    def __init__(self, *args, **kwargs):
        print('called combo.__init__()')
        self._items = kwargs.get('items', [])
    def clear(self):
        print('called combo.clear()')
    def clearEditText(self):
        print('called combo.clearEditText()')
    def addItems(self, itemlist):
        print('called combo.addItems({})'.format(itemlist))
    def height(self):
        return 100
    def setEditable(self, value):
        print('called combo.setEditable({})'.format(value))
        self.checked = value
    def setCurrentIndex(self, value):
        print('called combo.setCurrentIndex({})'.format(value))
        self.checked = value
    def currentText(self):
        print('called combo.currentText()')
        return 'current'
    def setToolTip(self, value):
        print(f'called combo.setToolTip({value})')


class MockPushButton:
    def __init__(self, *args):
        print('called MockPushButton.__init__()')
        self.clicked = MockSignal()
    def setMenu(self, *args):
        print('called QPushButton.setMenu()')
    def setShortcut(self, *args):
        print('called QPushButton.setShortcut with args', args)
    def setDefault(self, *args):
        print('called QPushButton.setDefault with args', args)
    def setToolTip(self, value):
        print(f'called QPushButton.setToolTip({value})')


class MockLineEdit:
    def __init__(self, *args):
        print('called lineedit.__init__()')
    def setText(self, *args):
        print('called lineedit.settext(`{}`)'.format(args[0]))
    def setMinimumHeight(self, *args):
        print('called lineedit.setMinHeight({})'.format(args[0]))
    def clear(self):
        print('called lineedit.clear()')
    def text(self):
        return 'new seltext'


class MockButtonBox:
    Ok = 1
    Cancel = 2
    accepted = MockSignal()
    rejected = MockSignal()
    def __init__(self, *args):
        print('called buttonbox.__init__(`{}`)'.format(args[0]))


class MockMessageBox:
    Yes = 1
    No = 2
    Cancel = 0
    def __init__(self, *args):
        print('called messagebox.__init__()')
    def setText(self, *args):
        print('called messagebox.setText()')
    def setInformativeText(self, *args):
        print('called messagebox.setInformativeText()')
    def setStandardButtons(self, *args):
        print('called messagebox.setStandardButtons()')
    def setDefaultButton(self, *args):
        print('called messagebox.setDefaultButton()')
    def exec_(self, *args):
        pass


class MockListWidget:
    itemDoubleClicked = MockSignal()
    def __init__(self, *args):
        print('called list.__init__()')
        try:
            self.list = args[0]
        except IndexError:
            self.list = []
    def __len__(self):
        return len(self.list)
    def clear(self):
        print('called list.clear()')
    def setSelectionMode(self, *args):
        print('called list.setSelectionMode()')
    def addItems(self, *args):
        print('called list.addItems() with arg `{}`'.format(args[0]))
    def currentItem(self):
        pass
    def setCurrentRow(self, row):
        print('called list.setCurrentRow with rownumber', row)
    def item(self, *args):
        return self.list[args[0]]
    def setFocus(self):
        print('called list.setFocus()')
    def selectedItems(self):
        print('called list.selectedItems() on `{}`'.format(self.list))
        return [MockListWidgetItem('item 1'), MockListWidgetItem('item 2')]
    def takeItem(self, *args):
        print('called list.takeItem(`{}`) on `{}`'.format(args[0], self.list))
    def row(self, *args):
        print('called list.row() on `{}`'.format(self.list))
        return args[0]
    def addItem(self, *args):
        print('called list.addItem(`{}`) on `{}`'.format(args[0], self.list))
        self.list.append(args[0])


class MockListWidgetItem:
    def __init__(self, *args):
        print('called listitem.__init__()')
        self.name = args[0]
    def text(self):
        return self.name
    def setSelected(self, *args):
        print('called listitem.setSelected({}) for `{}`'.format(args[0], self.name))


class MockScintilla:
    SloppyBraceMatch = True
    PlainFoldStyle = 1
    def __init__(self, *args):
        print('called editor.__init__()')
    def setText(self, data):
        print('called editor.setText with data `{}`'.format(data))
    def setReadOnly(self, value):
        print('called editor.setReadOnly with value `{}`'.format(value))
    def setFont(self, data):
        print('called editor.setFont')
    def setMarginsFont(self, data):
        print('called editor.setMarginsFont')
    def setMarginWidth(self, *args):
        print('called editor.setMarginWidth')
    def setMarginLineNumbers(self, *args):
        print('called editor.setMarginLineNumbers')
    def setMarginsBackgroundColor(self, *args):
        print('called editor.setMarginsBackgroundColor')
    def setBraceMatching(self, *args):
        print('called editor.setBraceMatching')
    def setAutoIndent(self, *args):
        print('called editor.setAutoIndent')
    def setFolding(self, *args):
        print('called editor.setFolding')
    def setCaretLineVisible(self, *args):
        print('called editor.setCaretLineVisible')
    def setCaretLineBackgroundColor(self, *args):
        print('called editor.setCaretLineBackgroundColor')
    def setLexer(self, *args):
        print('called editor.setLexer')


class MockFont:
    def __init__(self, *args):
        print('called font.__init__()')
    def setFamily(self, *args):
        print('called editor.setFamily')
    def setFixedPitch(self, *args):
        print('called editor.setFixedPitch')
    def setPointSize(self, *args):
        print('called editor.setPointSize')


class MockFontMetrics:
    def __init__(self, *args):
        print('called fontmetrics.__init__()')
    def width(self, *args):
        print('called editor.width()')


class MockLexerDiff:
    def __init__(self, *args):
        print('called lexer.__init__()')
    def setDefaultFont(self, *args):
        print('called editor.setDefaultFont')


# -- and now for the actual testing stuff ---
def test_main(monkeypatch, capsys):
    class MockParser:
        def add_argument(self, *args, **kwargs):
            print('call parser.add_argument with args', args, kwargs)
        def parse_args(self):
            print('call parser.parse_args()')
            return 'args'
    def mock_startapp(*args):
        print('call startapp with args:', args)
        return 'results'
    monkeypatch.setattr(check_repo.argparse, 'ArgumentParser', MockParser)
    monkeypatch.setattr(check_repo, 'startapp', mock_startapp)
    check_repo.main()
    assert capsys.readouterr().out == ("call parser.add_argument with args ('project',)"
                                       " {'help': 'name of a software project', 'nargs': '?',"
                                       " 'default': ''}\n"
                                       'call parser.parse_args()\n'
                                       "call startapp with args: ('args',)\n"
                                       'results\n')


def test_startapp(monkeypatch, capsys):
    def return_path(*args):
        return pathlib.Path('/tmp')
    def return_true(*args):
        return True
    def return_false_then_true(*args):
        nonlocal counter
        counter += 1
        return counter != 1
    def return_false(*args):
        return False
    monkeypatch.setattr(check_repo.pathlib.Path, 'cwd', return_path)
    monkeypatch.setattr(check_repo.pathlib.Path, 'exists', return_true)
    monkeypatch.setattr(check_repo.qtw, 'QApplication', MockApplication)
    monkeypatch.setattr(check_repo, 'Gui', MockGui)
    monkeypatch.setattr(check_repo, 'HOME', pathlib.Path('/homedir'))
    monkeypatch.setattr(check_repo, 'root', pathlib.Path('/rootdir'))
    monkeypatch.setattr(check_repo.settings, 'private_repos', {'tests': 'testscripts'})
    with pytest.raises(SystemExit):
        check_repo.startapp(types.SimpleNamespace(project=''))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/tmp'), 'git')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    with pytest.raises(SystemExit):
        check_repo.startapp(types.SimpleNamespace(project='x'))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/rootdir/x'), 'git')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    with pytest.raises(SystemExit):
        check_repo.startapp(types.SimpleNamespace(project='tests'))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/homedir/testscripts'), 'git')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    assert capsys.readouterr().out == ''
    with pytest.raises(SystemExit):
        check_repo.startapp(types.SimpleNamespace(project='.'))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/tmp'), 'git')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    with pytest.raises(SystemExit):
        check_repo.startapp(types.SimpleNamespace(project='testscripts'))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/homedir/testscripts'), 'git')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    counter = 0
    monkeypatch.setattr(check_repo.pathlib.Path, 'exists', return_false_then_true)
    with pytest.raises(SystemExit):
        check_repo.startapp(types.SimpleNamespace(project=''))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/tmp'), 'hg')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    monkeypatch.setattr(check_repo.pathlib.Path, 'exists', return_false)
    assert check_repo.startapp(types.SimpleNamespace(project='')) == '. is not a repository'
    assert capsys.readouterr().out == ''

class TestCheckTextDialog:
    def test_init(self, monkeypatch, capsys):
        def mock_init(self, parent, *args):
            self.parent = parent
            print('called dialog.__init()__ with args `{}`'.format(args))
        def mock_setWindowTitle(self, *args):
            print('called dialog.setWindowTitle() with args `{}`'.format(args))
        def mock_setLayout(self, *args):
            print('called dialog.setLayout()')
        monkeypatch.setattr(check_repo.qtw.QDialog, '__init__', mock_init)
        monkeypatch.setattr(check_repo.qtw.QDialog, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(check_repo.qtw.QDialog, 'setLayout', mock_setLayout)
        monkeypatch.setattr(check_repo.qtw, 'QVBoxLayout', MockVBoxLayout)
        monkeypatch.setattr(check_repo.qtw, 'QHBoxLayout', MockHBoxLayout)
        monkeypatch.setattr(check_repo.qtw, 'QCheckBox', MockCheckBox)
        monkeypatch.setattr(check_repo.qtw, 'QLabel', MockLabel)
        monkeypatch.setattr(check_repo.qtw, 'QLineEdit', MockLineEdit)
        monkeypatch.setattr(check_repo.qtw, 'QPushButton', MockPushButton)
        check_repo.CheckTextDialog('parent', 'title', 'message')
        assert capsys.readouterr().out == (
             'called dialog.__init()__ with args `()`\n'
             "called dialog.setWindowTitle() with args `('title',)`\n"
             'called MockVBoxLayout.__init__()\n'
             'called MockHBoxLayout.__init__()\n'
             'called MockCheckBox.__init__()\n'
             'called hbox.addWidget()\n'
             'called vbox.addLayout()\n'
             'called MockHBoxLayout.__init__()\n'
             'called MockLabel.__init__()\n'
             'called hbox.addWidget()\n'
             'called vbox.addLayout()\n'
             'called MockHBoxLayout.__init__()\n'
             'called lineedit.__init__()\n'
             'called lineedit.settext(`message`)\n'
             'called hbox.addWidget()\n'
             'called vbox.addLayout()\n'
             'called MockHBoxLayout.__init__()\n'
             'called hbox.addStretch()\n'
             'called MockPushButton.__init__()\n'
             'called signal.__init__()\n'
             'called signal.connect()\n'
             'called hbox.addWidget()\n'
             'called MockPushButton.__init__()\n'
             'called signal.__init__()\n'
             'called signal.connect()\n'
             'called hbox.addWidget()\n'
             'called hbox.addStretch()\n'
             'called vbox.addLayout()\n'
             'called dialog.setLayout()\n')

    def test_accept(self, monkeypatch, capsys):
        def mock_accept(self, *args):
            print('called dialog.accept()')
        def mock_init(self, *args):
            print('called dialog.__init__()')
            self._parent = args[0]
        monkeypatch.setattr(check_repo.qtw.QDialog, 'accept', mock_accept)
        monkeypatch.setattr(check_repo.CheckTextDialog, '__init__', mock_init)
        test_obj = check_repo.CheckTextDialog(types.SimpleNamespace(dialog_data=()))
        test_obj.check = MockCheckBox()
        test_obj.text = MockLineEdit()
        test_obj.check.setChecked(True)
        test_obj.text.setText('text')
        test_obj.accept()
        assert test_obj._parent.dialog_data == (True, 'new seltext')
        assert capsys.readouterr().out == (
            'called dialog.__init__()\n'
            'called MockCheckBox.__init__()\n'
            'called lineedit.__init__()\n'
            'called check.setChecked(True)\n'
            'called lineedit.settext(`text`)\n'
            'called check.isChecked()\n'
            'called dialog.accept()\n')

class TestDiffViewDialog:
    def test_init(self, monkeypatch, capsys):
        def mock_init(self, parent, *args):
            self.parent = parent
            print('called dialog.__init()__ with args `{}`'.format(args))
        def mock_setWindowTitle(self, *args):
            print('called dialog.setWindowTitle() with args `{}`'.format(args))
        def mock_resize(self, *args):
            print('called dialog.resize()')
        def mock_setLayout(self, *args):
            print('called dialog.setLayout()')
        def mock_addAction(self, *args):
            print('called dialog.addAction()')
        monkeypatch.setattr(check_repo.qtw.QDialog, '__init__', mock_init)
        monkeypatch.setattr(check_repo.qtw.QDialog, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(check_repo.qtw.QDialog, 'resize', mock_resize)
        monkeypatch.setattr(check_repo.qtw.QDialog, 'setLayout', mock_setLayout)
        monkeypatch.setattr(check_repo.qtw.QDialog, 'addAction', mock_addAction)
        monkeypatch.setattr(check_repo.qtw, 'QVBoxLayout', MockVBoxLayout)
        monkeypatch.setattr(check_repo.qtw, 'QHBoxLayout', MockHBoxLayout)
        monkeypatch.setattr(check_repo.qtw, 'QCheckBox', MockCheckBox)
        monkeypatch.setattr(check_repo.qtw, 'QLabel', MockLabel)
        monkeypatch.setattr(check_repo.sci, 'QsciScintilla', MockScintilla)
        monkeypatch.setattr(check_repo.sci, 'QsciLexerDiff', MockLexerDiff)
        monkeypatch.setattr(check_repo.gui, 'QFont', MockFont)
        monkeypatch.setattr(check_repo.gui, 'QFontMetrics', MockFontMetrics)
        monkeypatch.setattr(check_repo.qtw, 'QPushButton', MockPushButton)
        monkeypatch.setattr(check_repo.qtw, 'QAction', MockAction)
        check_repo.DiffViewDialog('parent', 'title', 'caption')
        assert capsys.readouterr().out == (
            'called dialog.__init()__ with args `()`\n'
            "called dialog.setWindowTitle() with args `('title',)`\n"
            'called dialog.resize()\n'
            'called MockVBoxLayout.__init__()\n'
            'called MockHBoxLayout.__init__()\n'
            'called MockLabel.__init__()\n'
            'called hbox.addWidget()\n'
            'called vbox.addLayout()\n'
            'called MockHBoxLayout.__init__()\n'
            'called editor.__init__()\n'
            'called font.__init__()\n'
            'called editor.setFamily\n'
            'called editor.setFixedPitch\n'
            'called editor.setPointSize\n'
            'called editor.setFont\n'
            'called editor.setMarginsFont\n'
            'called fontmetrics.__init__()\n'
            'called editor.setMarginsFont\n'
            'called editor.width()\n'
            'called editor.setMarginWidth\n'
            'called editor.setMarginLineNumbers\n'
            'called editor.setMarginsBackgroundColor\n'
            'called editor.setBraceMatching\n'
            'called editor.setAutoIndent\n'
            'called editor.setFolding\n'
            'called editor.setCaretLineVisible\n'
            'called editor.setCaretLineBackgroundColor\n'
            'called lexer.__init__()\n'
            'called editor.setDefaultFont\n'
            'called editor.setLexer\n'
            'called editor.setText with data ``\n'
            'called editor.setReadOnly with value `True`\n'
            'called hbox.addWidget()\n'
            'called vbox.addLayout()\n'
            'called MockHBoxLayout.__init__()\n'
            'called MockPushButton.__init__()\n'
            'called signal.__init__()\n'
            'called signal.connect()\n'
            'called QPushButton.setDefault with args (True,)\n'
            'called hbox.addStretch()\n'
            'called hbox.addWidget()\n'
            'called hbox.addStretch()\n'
            'called vbox.addLayout()\n'
            'called dialog.setLayout()\n'
            'create QAction with text `Done`\n'
            'called signal.connect()\n'
            'call action.setShortcut with arg `Esc`\n'
            'called dialog.addAction()\n')

    def _test_setup_text(self, monkeypatch, capsys):
        """geen aparte test, want deze wordt aangeroepen tijdens __init__ en geen idee hoe ik dat kan
        monkeypatchen
        kan misschien door het opzetten van de tekst in een aparte routine te doen maar waarom zou ik
        """

class TestFriendlyReminder:
    def test_init(self, monkeypatch, capsys):
        def mock_init(self, parent, *args):
            self.parent = parent
            print('called dialog.__init()__ with args `{}`'.format(args))
        def mock_setWindowTitle(self, *args):
            print('called dialog.setWindowTitle() with args `{}`'.format(args))
        def mock_setLayout(self, *args):
            print('called dialog.setLayout()')
        monkeypatch.setattr(check_repo.qtw.QDialog, '__init__', mock_init)
        monkeypatch.setattr(check_repo.qtw.QDialog, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(check_repo.qtw.QDialog, 'setLayout', mock_setLayout)
        monkeypatch.setattr(check_repo.qtw, 'QVBoxLayout', MockVBoxLayout)
        monkeypatch.setattr(check_repo.qtw, 'QHBoxLayout', MockHBoxLayout)
        monkeypatch.setattr(check_repo.qtw, 'QCheckBox', MockCheckBox)
        monkeypatch.setattr(check_repo.qtw, 'QPushButton', MockPushButton)
        check_repo.FriendlyReminder('parent')
        assert capsys.readouterr().out == (
             'called dialog.__init()__ with args `()`\n'
             "called dialog.setWindowTitle() with args `('Friendly Reminder',)`\n"
             'called MockVBoxLayout.__init__()\n'
             'called MockHBoxLayout.__init__()\n'
             'called MockCheckBox.__init__()\n'
             'called hbox.addWidget()\n'
             'called vbox.addLayout()\n'
             'called MockHBoxLayout.__init__()\n'
             'called MockCheckBox.__init__()\n'
             'called hbox.addWidget()\n'
             'called vbox.addLayout()\n'
             'called MockHBoxLayout.__init__()\n'
             'called hbox.addStretch()\n'
             'called MockPushButton.__init__()\n'
             'called signal.__init__()\n'
             'called signal.connect()\n'
             'called hbox.addWidget()\n'
             'called MockPushButton.__init__()\n'
             'called signal.__init__()\n'
             'called signal.connect()\n'
             'called hbox.addWidget()\n'
             'called hbox.addStretch()\n'
             'called vbox.addLayout()\n'
             'called dialog.setLayout()\n')

    def test_accept(self, monkeypatch, capsys):
        def mock_accept(self, *args):
            print('called dialog.accept()')
        def mock_init(self, *args):
            print('called dialog.__init__()')
            self._parent = args[0]
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo.qtw.QDialog, 'accept', mock_accept)
        monkeypatch.setattr(check_repo.FriendlyReminder, '__init__', mock_init)
        testobj = check_repo.FriendlyReminder(types.SimpleNamespace(title='title'))
        testobj.linted = MockCheckBox()
        testobj.tested = MockCheckBox()
        assert capsys.readouterr().out == ('called dialog.__init__()\n'
                                           'called MockCheckBox.__init__()\n'
                                           'called MockCheckBox.__init__()\n')
        testobj.linted.setChecked(False)
        testobj.tested.setChecked(False)
        testobj.accept()
        assert capsys.readouterr().out == ('called check.setChecked(False)\n'
                                           'called check.setChecked(False)\n'
                                           'called check.isChecked()\n'
                                           "display message `You didn't tick all the boxes`\n"
                )
        testobj.linted.setChecked(False)
        testobj.tested.setChecked(True)
        testobj.accept()
        assert capsys.readouterr().out == ('called check.setChecked(False)\n'
                                           'called check.setChecked(True)\n'
                                           'called check.isChecked()\n'
                                           "display message `You didn't tick all the boxes`\n")
        testobj.linted.setChecked(True)
        testobj.tested.setChecked(False)
        testobj.accept()
        assert capsys.readouterr().out == ('called check.setChecked(True)\n'
                                           'called check.setChecked(False)\n'
                                           'called check.isChecked()\n'
                                           'called check.isChecked()\n'
                                           "display message `You didn't tick all the boxes`\n")
        testobj.linted.setChecked(True)
        testobj.tested.setChecked(True)
        testobj.accept()
        assert capsys.readouterr().out == ('called check.setChecked(True)\n'
                                           'called check.setChecked(True)\n'
                                           'called check.isChecked()\n'
                                           'called check.isChecked()\n'
                                           'called dialog.accept()\n')


class TestGui:
    def _test_init(self, monkeypatch, capsys):
        """Ik denk dat deze automatisch wordt doorlopen in de testobj fixture
        en ook in de methoden die de routines aangeroepen in __init__ testen
        """

    def test_setup_visual(self, monkeypatch, capsys):
        # wordt aangeroepen in __init__ daarom niet via fixture testen
        # de andere methode in de init en de methoden die deze aanroept wel mocken
        def mock_init(self, *args):
            # self.parent = parent
            print('called widget.__init()__ with args `{}`'.format(args))
        def mock_setWindowTitle(self, *args):
            print('called widget.setWindowTitle() with args `{}`'.format(args))
        def mock_setWindowIcon(self, *args):
            print('called widget.setWindowIcon()')
        def mock_resize(self, *args):
            print('called widget.resize()')
        def mock_setup_stashmenu(self, *args):
            print('called widget.setup_stashmenu()')
        def mock_setLayout(self, *args):
            print('called widget.setLayout()')
        def mock_addAction(self, *args):
            print('called widget.addAction()')
        monkeypatch.setattr(check_repo.qtw, 'QApplication', MockApplication)
        monkeypatch.setattr(check_repo.qtw.QWidget, '__init__', mock_init)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(check_repo.gui, 'QIcon', MockIcon)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'setWindowIcon', mock_setWindowIcon)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'resize', mock_resize)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'setLayout', mock_setLayout)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'addAction', mock_addAction)
        monkeypatch.setattr(check_repo.qtw, 'QVBoxLayout', MockVBoxLayout)
        monkeypatch.setattr(check_repo.qtw, 'QHBoxLayout', MockVBoxLayout)
        monkeypatch.setattr(check_repo.qtw, 'QCheckBox', MockCheckBox)
        monkeypatch.setattr(check_repo.qtw, 'QComboBox', MockComboBox)
        monkeypatch.setattr(check_repo.qtw, 'QListWidget', MockListWidget)
        monkeypatch.setattr(check_repo.qtw, 'QLabel', MockLabel)
        monkeypatch.setattr(check_repo.sci, 'QsciScintilla', MockScintilla)
        monkeypatch.setattr(check_repo.sci, 'QsciLexerDiff', MockLexerDiff)
        monkeypatch.setattr(check_repo.gui, 'QFont', MockFont)
        monkeypatch.setattr(check_repo.gui, 'QFontMetrics', MockFontMetrics)
        monkeypatch.setattr(check_repo.qtw, 'QPushButton', MockPushButton)
        monkeypatch.setattr(check_repo.qtw, 'QMenu', MockMenu)
        monkeypatch.setattr(check_repo.qtw, 'QAction', MockAction)
        monkeypatch.setattr(check_repo.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(check_repo.Gui, 'refresh_frame', mock_refresh_frame)
        monkeypatch.setattr(check_repo.Gui, 'setup_stashmenu', mock_setup_stashmenu)
        check_repo.Gui(pathlib.Path('base'), 'git')
        assert capsys.readouterr().out == (
            'called MockApplication.__init__()\n'
            'called widget.__init()__ with args `()`\n'
            "called widget.setWindowTitle() with args `('Uncommitted changes for `base`',)`\n"
            'called Icon.__init__() for `/home/albert/.icons/task.png`\n'
            'called widget.setWindowIcon()\n'
            'called MockVBoxLayout.__init__()\n'
            'called MockVBoxLayout.__init__()\n'
            'called MockLabel.__init__()\ncalled vbox.addWidget()\n'
            'called combo.__init__()\ncalled combo.setEditable(True)\n'
            f"called combo.setToolTip({tooltips['branch']})\ncalled vbox.addWidget()\n"
            'called MockPushButton.__init__()\ncalled signal.__init__()\ncalled signal.connect()\n'
            f"called QPushButton.setToolTip({tooltips['create']})\n"
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\ncalled signal.connect()\n'
            f"called QPushButton.setToolTip({tooltips['switch']})\n"
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            'called widget.setup_stashmenu()\ncalled QPushButton.setMenu()\n'
            f"called QPushButton.setToolTip({tooltips['stash']})\n"
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\ncalled signal.connect()\n'
            f"called QPushButton.setToolTip({tooltips['merge']})\n"
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\ncalled signal.connect()\n'
            f"called QPushButton.setToolTip({tooltips['delete']})\n"
            'called vbox.addWidget()\n'
            'called vbox.addStretch()\n'
            'called Icon.fromTheme() with args ()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['docs']})\n"
            'create QAction with text `Open project &Docs`\n'
            'called signal.connect()\n'
            'create QAction with text `Open CGit (local repos)`\n'
            'called signal.connect()\n'
            'create QAction with text `Open GitWeb (remote repos)`\n'
            'called signal.connect()\n'
            'called QPushButton.setMenu()\n'
            "called QPushButton.setShortcut with args ('Shift+F6',)\n"
            'called vbox.addWidget()\n'
            'called vbox.addLayout()\n'
            'called MockVBoxLayout.__init__()\ncalled list.__init__()\n'
            'called list.setSelectionMode()\n'
            'called vbox.addWidget()\n'
            'called MockVBoxLayout.__init__()\n'
            'called MockVBoxLayout.__init__()\n'
            'called MockLabel.__init__()\ncalled vbox.addWidget()\n'
            "called combo.__init__()\ncalled combo.addItems(['status', 'repolist'])\n"
            'called signal.connect()\n'
            f"called combo.setToolTip({tooltips['show']})\n"
            'called vbox.addWidget()\n'
            'called vbox.addLayout()\n'
            'called MockLabel.__init__()\ncalled vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['edit']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['diff']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['lint']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['blame']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['commit']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['amend']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['revert']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['track']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['untrack']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['ignore']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockLabel.__init__()\ncalled vbox.addWidget()\n'
            'called vbox.addLayout()\n'
            'called vbox.addLayout()\n'
            'called MockVBoxLayout.__init__()\n'
            'called vbox.addStretch()\n'
            'called MockLabel.__init__()\ncalled vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['diff_all']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['lint_all']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['commit_all']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['recheck']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['history']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called MockPushButton.__init__()\ncalled signal.__init__()\n'
            f"called QPushButton.setToolTip({tooltips['quit']})\n"
            'called signal.connect()\n'
            'called vbox.addWidget()\n'
            'called vbox.addStretch()\n'
            'called vbox.addLayout()\n'
            'called widget.setLayout()\n'
            'create QAction with text `Done`\ncalled signal.connect()\n'
            'call action.setShortcut with arg `Ctrl+Q`\ncalled widget.addAction()\n'
            'called Gui.refresh_frame()\n')

    def test_refresh_frame(self, monkeypatch, capsys):
        # wordt aangeroepen in __init__ daarom niet via fixture testen
        # de andere methode in de init en de methoden die deze aanroept wel mocken
        def mock_init(self, *args):
            print('called QMainWindow.__init__()')
        def mock_populate(self):
            print('called Gui.populate_frame()')
        monkeypatch.setattr(check_repo.qtw, 'QApplication', MockApplication)
        monkeypatch.setattr(check_repo.qtw.QWidget, '__init__', mock_init)
        monkeypatch.setattr(check_repo.qtw, 'QWidget', MockWidget)
        monkeypatch.setattr(check_repo.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(check_repo.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(check_repo.Gui, 'populate_frame', mock_populate)
        check_repo.Gui(pathlib.Path('base'), 'git')
        assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
                                           'called QMainWindow.__init__()\n'
                                           'called Gui.setup_visual()\n'
                                           'called list.__init__()\n'
                                           'called combo.__init__()\n'
                                           'called Gui.get_repofiles()\n'
                                           'called Gui.populate_frame()\n'
                                           'called list.setFocus()\n')


    def test_get_repofiles(self, monkeypatch, capsys):
        # de verschillende varianten uitproberen nadat de klasse is opgezet
        # omdat deze methode daarbij al wordt aangeroepen kan dat niet via de testobj fixture
        def mock_init(self, *args):
            print('called QMainWindow.__init__()')
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_sp_run)
        monkeypatch.setattr(check_repo.qtw, 'QApplication', MockApplication)
        monkeypatch.setattr(check_repo.qtw.QWidget, '__init__', mock_init)
        monkeypatch.setattr(check_repo.qtw, 'QWidget', MockWidget)
        monkeypatch.setattr(check_repo.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(check_repo.Gui, 'refresh_frame', mock_refresh_frame)
        test_obj = setup_app(monkeypatch)
        assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
                                           'called QMainWindow.__init__()\n'
                                           'called Gui.setup_visual()\n'
                                           'called list.__init__()\n'
                                           'called combo.__init__()\n'
                                           'called Gui.refresh_frame()\n')
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

    def test_populate_frame(self, monkeypatch, capsys):  #, testobj):
        def mock_setWindowTitle(self, *args):
            print('called QWidget.setWindowTitle() with args `{}`'.format(args))
        def mock_setWindowIcon(self, *args):
            print('called QWidget.setWindowIcon()`')
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_sp_run)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'setWindowIcon', mock_setWindowIcon)
        monkeypatch.setattr(check_repo.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(check_repo.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(check_repo.Gui, 'update_branches', mock_update_branches)
        test_obj = setup_app(monkeypatch)
        test_obj.populate_frame()   # nog een keer om expliciet aan te roepen
        assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
                                           'called QMainWindow.__init__()\n'
                                           'called Gui.setup_visual()\n'
                                           'called list.__init__()\n'
                                           'called combo.__init__()\n'
                                           'called Gui.get_repofiles()\n'
                                           'called list.clear()\n'
                                           'called list.addItem(`file1.py`) on `[]`\n'
                                           "called list.addItem(`file2.py`) on `['file1.py']`\n"
                                           'called list.setCurrentRow with rownumber 0\n'
                                           'called Gui.update_branches()\n'
                                           'called list.setFocus()\n'
                                           'called list.clear()\n'
                                           "called list.addItem(`file1.py`) on `['file1.py',"
                                           " 'file2.py']`\n"
                                           "called list.addItem(`file2.py`) on `['file1.py',"
                                           " 'file2.py', 'file1.py']`\n"
                                           'called list.setCurrentRow with rownumber 0\n'
                                           'called Gui.update_branches()\n')

    def test_get_selected_files(self, monkeypatch, capsys, testobj):
        def mock_select():
            return MockListWidgetItem('M  item1'), MockListWidgetItem('?? item2')
        monkeypatch.setattr(testobj.list, 'selectedItems', mock_select)
        testobj.outtype = ''
        assert testobj.get_selected_files() == [('', 'M  item1'), ('', '?? item2')]
        assert capsys.readouterr().out == ('called listitem.__init__()\n'
                                           'called listitem.__init__()\n')
        testobj.outtype = 'status'
        assert testobj.get_selected_files() == [['M', 'item1'], ['??', 'item2']]
        assert capsys.readouterr().out == ('called listitem.__init__()\n'
                                           'called listitem.__init__()\n')

    def test_edit_selected(self, monkeypatch, capsys, testobj):
        def mock_just_run(command):
            print('call just_run() for `{}`'.format(command))
        def mock_get_selected():
            return ('', 'file1'), ('' ,'file2')
        monkeypatch.setattr(testobj, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(testobj, 'just_run', mock_just_run)
        testobj.edit_selected()
        assert capsys.readouterr().out == ("call just_run() for `['gnome-terminal', '--profile',"
                                           " 'Code Editor Shell', '--', 'vim', 'file1', 'file2']`\n"
                                           'called Gui.refresh_frame()\n')

    def test_diff_all(self, monkeypatch, capsys, testobj):
        def mock_just_run(command):
            print('call just_run() for `{}`'.format(command))
        def mock_just_run_exc(command):
            raise OSError('run commando gaat fout')
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)

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
        def mock_get_selected():
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_filter_tracked(*args):
            print('call filter_tracked()')
            return list(*args)
        def mock_just_run(command):
            print('call just_run() for `{}`'.format(command))
        def mock_just_run_exc(command):
            print('call just_run() for `{}`'.format(command))
            raise OSError
        def mock_run_and_capture(command):
            print('call run_and_capture() for `{}`'.format(command))
            return ['out', 'put'], []
        def mock_run_and_capture_err(command):
            print('call run_and_capture() for `{}`'.format(command))
            return ['', ''], ['er', 'ror']
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        class MockDiffView:
            def __init__(self, *args):
                print('call DiffViewDialog with args', args[1:])
            def exec_(self):
                print('exec dialog')
        monkeypatch.setattr(testobj, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(testobj, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(testobj, 'just_run', mock_just_run)
        monkeypatch.setattr(testobj, 'run_and_capture', mock_run_and_capture)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo, 'DiffViewDialog', MockDiffView)
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

    def test_add_ignore(self, monkeypatch, capsys, testobj):
        def mock_filter(*args):
            print('called Gui.filter_tracked() for `{}`'.format(args))
            return 'file1', 'file2'
        def mock_get_selected():
            print('called Gui.get_selected_files')
            return ('??', 'file1'), ('', 'file2')

        monkeypatch.setattr(testobj, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(testobj, 'filter_tracked', mock_filter)
        testobj.repotype = 'hg'
        testobj.path = pathlib.Path('/tmp')
        ignorefile = pathlib.Path('/tmp/.hgignore')
        assert not ignorefile.exists()
        testobj.add_ignore()
        assert ignorefile.exists()
        assert capsys.readouterr().out == ('called Gui.get_selected_files\n'
                                           'called Gui.refresh_frame()\n')
        assert ignorefile.read_text() == ('file1\nfile2\n')
        ignorefile.unlink()

        testobj.repotype = 'not hg'
        testobj.path = pathlib.Path('/tmp')
        ignorefile = pathlib.Path('/tmp/.gitignore')
        assert not ignorefile.exists()
        testobj.add_ignore()
        assert ignorefile.exists()
        assert capsys.readouterr().out == ('called Gui.get_selected_files\n'
                                           'called Gui.refresh_frame()\n')
        assert ignorefile.read_text() == ('file1\nfile2\n')
        ignorefile.unlink()

    def test_add_new(self, monkeypatch, capsys, testobj):
        def mock_run(*args):
            print('run_and_report with args:', *args)
        def mock_get_selected():
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
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        def mock_get_selected(self):
            print('called Gui.get_selected_files')
            return ('??', 'file1'), ('', 'file2')

        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
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

    def test_set_outtype(self, monkeypatch, capsys, testobj):
        testobj.cb_list = MockComboBox()
        testobj.set_outtype()
        assert testobj.outtype == 'current'
        assert capsys.readouterr().out == ('called combo.__init__()\n'
                                           'called combo.currentText()\n'
                                           'called Gui.refresh_frame()\n')

    def test_commit_all(self, monkeypatch, capsys, testobj):
        def mock_gettext(*args):
            return 'commit_message', True
        def mock_gettext_nok(*args):
            return '', False
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        monkeypatch.setattr(check_repo.qtw.QInputDialog, 'getText', mock_gettext)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(MockDialog, 'exec_', lambda *x: check_repo.qtw.QDialog.Rejected)
        monkeypatch.setattr(check_repo, 'FriendlyReminder', MockDialog)
        testobj.commit_all()
        assert capsys.readouterr().out == 'called dialog.__init()__ with args `()`\n'
        monkeypatch.setattr(MockDialog, 'exec_', lambda *x: check_repo.qtw.QDialog.Accepted)
        monkeypatch.setattr(check_repo, 'FriendlyReminder', MockDialog)
        testobj.commit_all()
        assert capsys.readouterr().out == ('called dialog.__init()__ with args `()`\n'
                                           "run_and_report with args:"
                                           " ['git', 'commit', '-a', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')
        testobj.repotype = 'hg'
        testobj.commit_all()
        assert capsys.readouterr().out == ('called dialog.__init()__ with args `()`\n'
                                           "run_and_report with args:"
                                           " ['hg', 'commit', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')
        monkeypatch.setattr(check_repo.qtw.QInputDialog, 'getText', mock_gettext_nok)
        testobj.commit_all()
        assert capsys.readouterr().out == 'called dialog.__init()__ with args `()`\n'

    def test_commit_selected(self, monkeypatch, capsys, testobj):
        def mock_get_selected(self):
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_get_selected_none(self):
            print('call get_selected_filenames()')
            return []
        def mock_filter_tracked(self, *args):
            print('call filter_tracked()')
            return list(*args)
        def mock_gettext(*args):
            return 'commit_message', True
        def mock_gettext_nok(*args):
            return '', False
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        monkeypatch.setattr(check_repo.qtw.QInputDialog, 'getText', mock_gettext)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(check_repo.Gui, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected_none)
        monkeypatch.setattr(MockDialog, 'exec_', lambda *x: check_repo.qtw.QDialog.Rejected)
        monkeypatch.setattr(check_repo, 'FriendlyReminder', MockDialog)
        testobj.commit_selected()
        assert capsys.readouterr().out == 'called dialog.__init()__ with args `()`\n'
        monkeypatch.setattr(MockDialog, 'exec_', lambda *x: check_repo.qtw.QDialog.Accepted)
        monkeypatch.setattr(check_repo, 'FriendlyReminder', MockDialog)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('called dialog.__init()__ with args `()`\n'
                                           'call get_selected_filenames()\n'
                                           'call filter_tracked()\n')
        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('called dialog.__init()__ with args `()`\n'
                                           'call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run_and_report with args:"
                                           " ['git', 'add', 'file1', 'file2']\n"
                                           "run_and_report with args: ['git',"
                                           " 'commit', 'file1', 'file2', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')
        testobj.repotype = 'hg'
        testobj.commit_selected()
        assert capsys.readouterr().out == ('called dialog.__init()__ with args `()`\n'
                                           'call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run_and_report with args: ['hg',"
                                           " 'commit', 'file1', 'file2', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')
        monkeypatch.setattr(check_repo.qtw.QInputDialog, 'getText', mock_gettext_nok)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('called dialog.__init()__ with args `()`\n'
                                           'call get_selected_filenames()\n'
                                           'call filter_tracked()\n')

    def test_amend_commit(self, monkeypatch, capsys, testobj):
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        def mock_runc(self, *args):
            print('run_and_capture with args:', *args)
            return (('commit_message', ''), '')
        def mock_get_selected(self):
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_filter_tracked(self, *args):
            print('call filter_tracked()')
            return list(*args)
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        class MockDialog:
            def __init__(self, *args):
                self.parent = args[0]
                print('call CheckTextDialog with args', args[1:])
            def exec_(self):
                self.parent.dialog_data = True, 'commit_message'
                return check_repo.qtw.QDialog.Accepted
        class MockDialog_2:
            def __init__(self, *args):
                self.parent = args[0]
                print('call CheckTextDialog with args', args[1:])
            def exec_(self):
                self.parent.dialog_data = True, 'commit_message'
                return check_repo.qtw.QDialog.Rejected
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_runc)
        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected)
        monkeypatch.setattr(check_repo.Gui, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(check_repo, 'CheckTextDialog', MockDialog)
        testobj.amend_commit()
        assert capsys.readouterr().out == (
                "run_and_capture with args: ['git', 'log', '-1', '--pretty=format:%s']\n"
                "call CheckTextDialog with args ('Uncommitted changes for `base`', 'commit_message')\n"
                "call get_selected_filenames()\n"
                "call filter_tracked()\n"
                "run_and_report with args: ['git', 'add', 'file1', 'file2']\n"
                "run_and_report with args: ['git', 'commit', '--amend', '-m', 'commit_message']\n"
                "called Gui.refresh_frame()\n")
        monkeypatch.setattr(check_repo, 'CheckTextDialog', MockDialog_2)
        testobj.amend_commit()
        assert capsys.readouterr().out == (
                "run_and_capture with args: ['git', 'log', '-1', '--pretty=format:%s']\n"
                "call CheckTextDialog with args ('Uncommitted changes for `base`',"
                " 'commit_message')\n")
        testobj.repotype = 'not git'
        testobj.amend_commit()
        assert capsys.readouterr().out == 'display message `Only implemented for git repos`\n'

    def test_revert_selected(self, monkeypatch, capsys, testobj):
        def mock_get_selected(self):
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_get_selected_none(self):
            print('call get_selected_filenames()')
            return []
        def mock_filter_tracked(self, *args):
            print('call filter_tracked()')
            return list(*args)
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(check_repo.Gui, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected_none)
        testobj.revert_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n')
        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected)
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
        def mock_get_selected(self):
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_get_selected_1(self):
            print('call get_selected_filenames()')
            return ['file1']
        def mock_get_selected_none(self):
            print('call get_selected_filenames()')
            return []
        def mock_filter_tracked(self, *args, **kwargs):
            print('call filter_tracked()')
            return list(*args)
        def mock_run(self, *args):
            print('run with args:', *args)
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        monkeypatch.setattr(check_repo.Gui, 'just_run', mock_run)
        monkeypatch.setattr(check_repo.Gui, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected_none)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        testobj.lint_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           'display message `No tracked files selected`\n')
        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected)
        testobj.lint_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run with args: ['lintergui', '-m', 'permissive',"
                                           " '-l', 'file1', 'file2']\n")
        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected_1)
        testobj.lint_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run with args: ['lintergui', '-m', 'permissive',"
                                           " '-f', 'file1']\n")

    def test_lint_all(self, monkeypatch, capsys, testobj):
        def mock_run(self, *args):
            print('run with args:', *args)
        monkeypatch.setattr(check_repo.Gui, 'just_run', mock_run)
        testobj.lint_all()
        assert capsys.readouterr().out == ("run with args: ['lintergui', '-m', 'permissive', '-d',"
                                           " '.']\n")

    def test_annotate(self, monkeypatch, capsys, testobj):
        def mock_get_selected(self):
            print('call get_selected_filenames()')
            return 'file1', 'file2'
        def mock_get_selected_none(self):
            print('call get_selected_filenames()')
            return []
        def mock_filter_tracked(self, *args, **kwargs):
            print('call filter_tracked()')
            return list(*args)
        def mock_run(self, *args):
            print('run_and_capture with args:', *args)
            return ['blame', 'output'], []
        def mock_run_err(self, *args):
            print('run_and_capture with args:', *args)
            return [], ['blame', 'error']
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        class MockDialog:
            def __init__(self, *args):
                self.parent = args[0]
                print('call DiffViewDialog with args', args[1:])
            def exec_(self):
                self.parent.dialog_data = True, 'commit_message'
                return check_repo.qtw.QDialog.Accepted
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run)
        monkeypatch.setattr(check_repo.Gui, 'filter_tracked', mock_filter_tracked)
        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected_none)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo, 'DiffViewDialog', MockDialog)
        testobj.annotate()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n')

        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected)
        testobj.annotate()
        assert capsys.readouterr().out == (
                'call get_selected_filenames()\n'
                'call filter_tracked()\n'
                "run_and_capture with args: ['git', 'blame', 'file1', 'file2']\n"
                "call DiffViewDialog with args ('Uncommitted changes for `base`',"
                " 'Show annotations for: file1, file2', 'blame\\noutput', (1200, 800))\n")
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run_err)
        testobj.annotate()
        assert capsys.readouterr().out == (
                'call get_selected_filenames()\n'
                'call filter_tracked()\n'
                "run_and_capture with args: ['git', 'blame', 'file1', 'file2']\n"
                'display message `blame\nerror`\n')

    def test_filter_tracked(self, monkeypatch, capsys, testobj):
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        assert testobj.filter_tracked([('?', 'file1'), ('', 'file2'), ('??', 'file3'),
            ('M ', 'file4')]) == ['file2', 'file4']
        assert capsys.readouterr().out == ('display message `file1 not tracked`\n'
                                           'display message `file3 not tracked`\n')
        assert testobj.filter_tracked([('?', 'file1'), ('', 'file2'), ('??', 'file3'),
            ('M ', 'file4')], notify=False) == ['file2', 'file4']

    def test_view_repo(self, monkeypatch, capsys, testobj):
        def mock_run(self, *args):
            print('run with args:', *args)
        monkeypatch.setattr(check_repo.Gui, 'just_run', mock_run)
        testobj.view_repo()
        assert capsys.readouterr().out == "run with args: ['gitg']\n"
        testobj.repotype = 'hg'
        testobj.view_repo()
        assert capsys.readouterr().out == "run with args: ['hg', 'view']\n"

    def test_update_branches(self, monkeypatch, capsys, testobj):
        def mock_run(self, *args):
            print('run_and_capture with args:', *args)
            return ['* branch1'], []
        def mock_run_more(self, *args):
            print('run_and_capture with args:', *args)
            return ['  branch1', '* branch2'], []
        def mock_run_err(self, *args):
            print('run_and_capture with args:', *args)
            return [], ['branch', 'error']
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run_err)
        testobj.update_branches()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'branch']\n"
                                           'display message `branch\nerror`\n')
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run)
        testobj.update_branches()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'branch']\n"
                                           'called combo.clear()\n'
                                           "called combo.addItems(['branch1'])\n"
                                           'called combo.setCurrentIndex(0)\n')
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run_more)
        testobj.update_branches()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'branch']\n"
                                           'called combo.clear()\n'
                                           "called combo.addItems(['branch1', 'branch2'])\n"
                                           'called combo.setCurrentIndex(1)\n')
        testobj.repotype = 'not git'
        testobj.update_branches()
        assert capsys.readouterr().out == ''

    def test_create_branch(self, monkeypatch, capsys, testobj):
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        def mock_find_branch(self):
            print('called find_current_branch()')
            return 'branch'
        def mock_find_branch_same(self):
            print('called find_current_branch()')
            return 'current'
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        def mock_update_branches(self):
            print('called update_branches()')
        monkeypatch.setattr(check_repo.Gui, 'find_current_branch', mock_find_branch)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(check_repo.Gui, 'update_branches', mock_update_branches)
        testobj.create_branch()
        assert capsys.readouterr().out == ('called combo.currentText()\n'
                                           'called find_current_branch()\n'
                                           "run_and_report with args: ['git', 'branch', 'current']\n"
                                           'called update_branches()\n')
        monkeypatch.setattr(check_repo.Gui, 'find_current_branch', mock_find_branch_same)
        testobj.create_branch()
        assert capsys.readouterr().out == ('called combo.currentText()\n'
                                           'called find_current_branch()\n'
                                           'display message `Enter a new branch name in the combobox'
                                           ' first`\n')
        monkeypatch.setattr(testobj.cb_branch, 'currentText', lambda: '')
        testobj.create_branch()
        assert capsys.readouterr().out == ('display message `Enter a new branch name in the combobox'
                                           ' first`\n')

    def test_switch2branch(self, monkeypatch, capsys, testobj):
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        def mock_find_branch(self):
            print('called find_current_branch()')
            return 'branch'
        def mock_find_branch_same(self):
            print('called find_current_branch()')
            return 'current'
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        monkeypatch.setattr(check_repo.Gui, 'find_current_branch', mock_find_branch)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        testobj.switch2branch()
        assert capsys.readouterr().out == ('called combo.currentText()\n'
                                           'called find_current_branch()\n'
                                           "run_and_report with args: ['git', 'checkout', 'current']\n"
                                           'called Gui.refresh_frame()\n')
        monkeypatch.setattr(check_repo.Gui, 'find_current_branch', mock_find_branch_same)
        testobj.switch2branch()
        assert capsys.readouterr().out == ('called combo.currentText()\n'
                                           'called find_current_branch()\n'
                                           'display message `Select a branch different from the'
                                           ' current one first`\n')
        monkeypatch.setattr(testobj.cb_branch, 'currentText', lambda: '')
        testobj.switch2branch()
        assert capsys.readouterr().out == ('display message `Select a branch different from the'
                                           ' current one first`\n')

    def test_merge_branch(self, monkeypatch, capsys, testobj):
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        def mock_question(self, title, message):
            print('display question `{}`'.format(message))
            return 'not_yes'
        def mock_question_yes(self, title, message):
            print('display question `{}`'.format(message))
            return check_repo.qtw.QMessageBox.Yes
        def mock_find_branch(self):
            print('called find_current_branch()')
            return 'branch'
        def mock_find_branch_same(self):
            print('called find_current_branch()')
            return 'current'
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        monkeypatch.setattr(check_repo.Gui, 'find_current_branch', mock_find_branch)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'question', mock_question_yes)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        testobj.merge_branch()
        assert capsys.readouterr().out == ('called combo.currentText()\n'
                                           'called find_current_branch()\n'
                                           'display question `Merge current into branch?`\n'
                                           "run_and_report with args: ['git', 'merge', 'current']\n"
                                           'called Gui.refresh_frame()\n')
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'question', mock_question)
        testobj.merge_branch()
        assert capsys.readouterr().out == ('called combo.currentText()\n'
                                           'called find_current_branch()\n'
                                           'display question `Merge current into branch?`\n')
        monkeypatch.setattr(check_repo.Gui, 'find_current_branch', mock_find_branch_same)
        testobj.merge_branch()
        assert capsys.readouterr().out == ('called combo.currentText()\n'
                                           'called find_current_branch()\n'
                                           'display message `Select a branch different from the'
                                           ' current one first`\n')
        monkeypatch.setattr(testobj.cb_branch, 'currentText', lambda: '')
        testobj.merge_branch()
        assert capsys.readouterr().out == ('called find_current_branch()\n'
                                           'display message `Select a branch different from the'
                                           ' current one first`\n')

    def test_delete_branch(self, monkeypatch, capsys, testobj):
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        monkeypatch.setattr(check_repo.Gui, 'update_branches', mock_update_branches)
        testobj.delete_branch()
        assert capsys.readouterr().out == ('called combo.currentText()\n'
                                           "run_and_report with args: ['git', 'branch', '-d',"
                                           " 'current']\n"
                                           'called Gui.update_branches()\n')

    def test_setup_stashmenu(self, monkeypatch, capsys, testobj):
        monkeypatch.setattr(check_repo.qtw, 'QMenu', MockMenu)
        monkeypatch.setattr(check_repo.qtw, 'QAction', MockAction)
        assert isinstance(testobj.setup_stashmenu(), MockMenu)
        assert capsys.readouterr().out == ('create QAction with text `&New Stash`\n'
                                           'called signal.connect()\n'
                                           'create QAction with text `&Apply Stash`\n'
                                           'called signal.connect()\n'
                                           'create QAction with text `&Remove Stash`\n'
                                           'called signal.connect()\n')

    def test_stash_push(self, monkeypatch, capsys, testobj):
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        testobj.stash_push()
        assert capsys.readouterr().out == ('display message `create stash`\n'
                                           "run_and_report with args: ['git', 'stash', 'push']\n")

    def test_select_stash(self, monkeypatch, capsys, testobj):
        def mock_run(self, *args):
            print('run_and_capture with args:', *args)
            return ['stash'], []
        def mock_run_none(self, *args):
            print('run_and_capture with args:', *args)
            return [], []
        def mock_run_err(self, *args):
            print('run_and_capture with args:', *args)
            return [], ['stash', 'error']
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        def mock_getitem(self, title, message, items):
            print('call InputDialog.getItem()')
            return 'stash-name: ', True
        def mock_getitem_none(self, title, message, items):
            print('call InputDialog.getItem()')
            return '', False
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo.qtw.QInputDialog, 'getItem', mock_getitem)
        assert testobj.select_stash() == 'stash-name'
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'stash', 'list']\n"
                                           'call InputDialog.getItem()\n')
        monkeypatch.setattr(check_repo.qtw.QInputDialog, 'getItem', mock_getitem_none)
        assert not testobj.select_stash()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'stash', 'list']\n"
                                           'call InputDialog.getItem()\n')
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run_none)
        assert not testobj.select_stash()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'stash', 'list']\n"
                                           'display message `No stashes found`\n')
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run_err)
        assert not testobj.select_stash()
        assert capsys.readouterr().out == ("run_and_capture with args: ['git', 'stash', 'list']\n"
                                           'display message `stash\nerror`\n')

    def test_stash_pop(self, monkeypatch, capsys, testobj):
        def mock_select(self):
            print('call select_stash()')
            return 'name'
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        monkeypatch.setattr(check_repo.Gui, 'select_stash', mock_select)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        testobj.stash_pop()
        assert capsys.readouterr().out == ('call select_stash()\n'
                                           "run_and_report with args: ['git', 'stash', 'apply',"
                                           " 'name']\n")

    def test_stash_kill(self, monkeypatch, capsys, testobj):
        def mock_select(self):
            print('call select_stash()')
            return 'name'
        def mock_run(self, *args):
            print('run_and_report with args:', *args)
        monkeypatch.setattr(check_repo.Gui, 'select_stash', mock_select)
        monkeypatch.setattr(check_repo.Gui, 'run_and_report', mock_run)
        testobj.stash_kill()
        assert capsys.readouterr().out == ('call select_stash()\n'
                                           "run_and_report with args: ['git', 'stash', 'drop',"
                                           " 'name']\n")

    def test_open_notes(self, monkeypatch, capsys, testobj):
        def mock_resolve(*args):
            print('call path.resolve()')
            return args[0]
        def mock_run(self, *args):
            print('run_and_continue with args:', *args)
        monkeypatch.setattr(check_repo.pathlib.Path, 'resolve', mock_resolve)
        monkeypatch.setattr(check_repo.Gui, 'run_and_continue', mock_run)
        testobj.path = pathlib.Path('here/this')
        testobj.open_notes()
        assert capsys.readouterr().out == ('call path.resolve()\n'
                                           "run_and_continue with args: ['a-propos', '-n',"
                                           " 'Mee Bezig (This)', '-f', 'mee-bezig']\n")

    def test_open_docs(self, monkeypatch, capsys, testobj):
        def mock_run(self, *args):
            print('run_and_continue with args:', *args)
        def mock_get_dir(*args):
            print('call settings.get_project_dir')
            return args[0]
        monkeypatch.setattr(check_repo.settings, 'get_project_dir', mock_get_dir)
        monkeypatch.setattr(check_repo.Gui, 'run_and_continue', mock_run)
        monkeypatch.setattr(check_repo.sys, 'argv', ['python'])
        monkeypatch.setattr(check_repo.os, 'getcwd', lambda: 'here')
        testobj.open_docs()
        assert capsys.readouterr().out == ("run_and_continue with args:"
                                           " ['treedocs', 'here/projdocs.trd']\n")
        monkeypatch.setattr(check_repo.sys, 'argv', ['python', '.'])
        testobj.open_docs()
        assert capsys.readouterr().out == ("run_and_continue with args:"
                                           " ['treedocs', 'here/projdocs.trd']\n")
        monkeypatch.setattr(check_repo.sys, 'argv', ['python', 'project'])
        testobj.open_docs()
        assert capsys.readouterr().out == ('call settings.get_project_dir\n'
                                           "run_and_continue with args: ['treedocs',"
                                           " 'project/projdocs.trd']\n")

    def test_open_cgit(self, monkeypatch, capsys, testobj):
        def mock_run(self, *args):
            print('run_and_continue with args:', *args)
        monkeypatch.setattr(check_repo.Gui, 'run_and_continue', mock_run)
        testobj.open_cgit()
        assert capsys.readouterr().out == ("run_and_continue with args:"
                                           " ['binfab', 'www.startapp', 'cgit']\n")

    def test_open_gitweb(self, monkeypatch, capsys, testobj):
        def mock_run(self, *args):
            print('run_and_continue with args:', *args)
        monkeypatch.setattr(check_repo.Gui, 'run_and_continue', mock_run)
        testobj.open_gitweb()
        assert capsys.readouterr().out == ("run_and_continue with args:"
                                           " ['binfab', 'www.startapp', 'gitweb']\n")

    def test_find_current_branch(self, monkeypatch, capsys, testobj):
        def mock_run(self, *args):
            print('run_and_capture with args:', *args)
            return ['* current'], []
        def mock_run_2(self, *args):
            print('run_and_capture with args:', *args)
            return ['  branch', '* blarp'], []
        def mock_run_err(self, *args):
            print('run_and_capture with args:', *args)
            return [], ['error']
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run)
        assert testobj.find_current_branch() == 'current'
        assert capsys.readouterr().out == "run_and_capture with args: ['git', 'branch']\n"
        monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run_2)
        assert testobj.find_current_branch() == 'blarp'
        assert capsys.readouterr().out == "run_and_capture with args: ['git', 'branch']\n"
        # deze test niet nodig, git branch gaat nooit fout:
        # monkeypatch.setattr(check_repo.Gui, 'run_and_capture', mock_run_err)
        # assert testobj.find_current_branch() == ''
        # assert capsys.readouterr().out == "run_and_capture with args: ['git', 'branch']\n"

    def test_just_run(self, monkeypatch, capsys, testobj):
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_sp_run)
        testobj.path = pathlib.Path('here')
        testobj.just_run(['command', 'list'])
        assert capsys.readouterr().out == ("run with args: (['command', 'list'],)"
                                           " {'cwd': 'here', 'check': False}\n")

    def test_run_and_continue(self, monkeypatch, capsys, testobj):
        monkeypatch.setattr(check_repo.subprocess, 'Popen', mock_sp_run)
        testobj.path = pathlib.Path('here')
        testobj.run_and_continue(['command', 'list'])
        assert capsys.readouterr().out == "run with args: (['command', 'list'],) {'cwd': 'here'}\n"

    def test_run_and_report(self, monkeypatch, capsys, testobj):
        def mock_run(*args, **kwargs):
            print('run with args:', args, kwargs)
            return types.SimpleNamespace(stdout=b'all\nwent\nwell\n', stderr=None)
        def mock_run_err(*args, **kwargs):
            print('run with args:', args, kwargs)
            return types.SimpleNamespace(stdout=None, stderr=b'got\nan\nerror\n')
        def mock_information(self, title, message):
            print('display message `{}`'.format(message))
        def mock_warning(self, title, message):
            print('display warning `{}`'.format(message))
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_run)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'information', mock_information)
        monkeypatch.setattr(check_repo.qtw.QMessageBox, 'warning', mock_warning)
        testobj.run_and_report(['command', 'list'])
        assert capsys.readouterr().out == ("run with args: (['command', 'list'],) {'stdout': -1,"
                                           " 'stderr': -1, 'cwd': 'base', 'check': False}\n"
                                           'display message `all\nwent\nwell`\n')
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_run_err)
        testobj.run_and_report(['command', 'list'])
        assert capsys.readouterr().out == ("run with args: (['command', 'list'],) {'stdout': -1,"
                                           " 'stderr': -1, 'cwd': 'base', 'check': False}\n"
                                           'display warning `got\nan\nerror`\n')

    def test_run_and_capture(self, monkeypatch, capsys, testobj):
        def mock_run(*args, **kwargs):
            print('run with args:', args, kwargs)
            return types.SimpleNamespace(stdout=b'all\nwent\nwell\n', stderr=None)
        def mock_run_err(*args, **kwargs):
            print('run with args:', args, kwargs)
            return types.SimpleNamespace(stdout=None, stderr=b'got\nan\nerror\n')
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_run)
        assert testobj.run_and_capture(['command', 'list']) == (['all', 'went', 'well'], [])
        assert capsys.readouterr().out == ("run with args: (['command', 'list'],) {'stdout': -1,"
                                           " 'stderr': -1, 'cwd': 'base', 'check': False}\n")
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_run_err)
        assert testobj.run_and_capture(['command', 'list']) == ([], ['got', 'an', 'error'])
        assert capsys.readouterr().out == ("run with args: (['command', 'list'],) {'stdout': -1,"
                                           " 'stderr': -1, 'cwd': 'base', 'check': False}\n")
