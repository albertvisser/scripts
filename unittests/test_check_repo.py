import types
import pathlib
import pytest

import check_repo

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
    # app = setup_app(monkeypatch)
    app = check_repo.Gui(pathlib.Path('base'), 'git')
    capsys.readouterr()  # swallow stdout/stderr
    return app

def setup_app(monkeypatch):
    def mock_init(self, *args):
        print('called QMainWindow.__init__()')
    monkeypatch.setattr(check_repo.qtw, 'QApplication', MockApplication)
    monkeypatch.setattr(check_repo.qtw.QWidget, '__init__', mock_init)
    monkeypatch.setattr(check_repo.qtw, 'QWidget', MockWidget)
    # return check_repo.Gui(MockGui(pathlib.Path('base'), 'git'))
    return check_repo.Gui(pathlib.Path('base'), 'git')

def mock_run(*args):
    print('run with args:', args)

def mock_sp_run(*args, **kwargs):
    print('run with args:', args, kwargs)
    return types.SimpleNamespace(stdout=b'hallo\ndaar\njongens\n')

def mock_setup_visual(self, *args):
    print('called Gui.setup_visual()')
    self.list = MockListWidget()

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
        print('called MockIcon.__init__() for `{}`'.format(args[0]))


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
    def __init__(self, text):
        self.menutext = text
        self.actions = []
    def addAction(self, text, func):
        newaction = MockAction(text, func)
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
        return gui.qtw.QDialog.Accepted
    def setWindowTitle(self, *args):
        print('called dialog.setWindowTitle() with args `{}`'.format(args))
    def setLayout(self, *args):
        print('called dialog.setLayout()')
    def accept(self):
        print('called dialog.accept()')
        return gui.qtw.QDialog.Accepted
    def reject(self):
        print('called dialog.reject()')
        return gui.qtw.QDialog.Rejected


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
    def __init__(self, *args, **kwargs):
        print('called MockComboBox.__init__()')
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
        return 'current text'


class MockPushButton:
    def __init__(self, *args):
        print('called MockPushButton.__init__()')
        self.clicked = MockSignal()
    def setMenu(self, *args):
        print('called QPushButton.setMenu with args', args)
    def setShortcut(self, *args):
        print('called QPushButton.setShortcut with args', args)


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
        print('called list.setFocus()'.format())
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


# --- and now for the actual testing stuff ---
def test_main(monkeypatch, capsys):
    def return_path(*args):
        return pathlib.Path('/tmp')
    def return_true(*args):
        return True
    def return_false_then_true(*args):
        nonlocal counter
        counter += 1
        return False if counter == 1 else True
    def return_false(*args):
        return False
    class MockPath(pathlib.PosixPath):
        def mock_cwd(self):
            return pathlib.Path('/tmp')
        def mock_exists(self):
            return True
    class MockPath2(pathlib.PosixPath):
        def mock_cwd(self):
            return pathlib.Path('/tmp')
        def mock_exists(self):
            nonlocal counter
            counter += 1
            return False if counter == 1 else True
    class MockPath3(pathlib.PosixPath):
        def mock_cwd(self):
            return pathlib.Path('/tmp')
        def mock_exists(self):
            return False
    # monkeypatch.setattr(check_repo.pathlib, 'Path', MockPath)
    monkeypatch.setattr(check_repo.pathlib.Path, 'cwd', return_path)
    monkeypatch.setattr(check_repo.pathlib.Path, 'exists', return_true)
    monkeypatch.setattr(check_repo.qtw, 'QApplication', MockApplication)
    monkeypatch.setattr(check_repo, 'Gui', MockGui)
    monkeypatch.setattr(check_repo, 'HOME', pathlib.Path('/homedir'))
    monkeypatch.setattr(check_repo, 'root', pathlib.Path('/rootdir'))
    monkeypatch.setattr(check_repo.settings, 'private_repos', {'tests': 'testscripts'})
    # breakpoint()
    with pytest.raises(SystemExit):
        check_repo.main(types.SimpleNamespace(project=''))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/tmp'), 'git')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    with pytest.raises(SystemExit):
        check_repo.main(types.SimpleNamespace(project='x'))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/rootdir/x'), 'git')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    with pytest.raises(SystemExit):
        check_repo.main(types.SimpleNamespace(project='tests'))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/homedir/testscripts'), 'git')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    assert capsys.readouterr().out == ''
    with pytest.raises(SystemExit):
        check_repo.main(types.SimpleNamespace(project='.'))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/tmp'), 'git')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    with pytest.raises(SystemExit):
        check_repo.main(types.SimpleNamespace(project='testscripts'))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/homedir/testscripts'), 'git')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    counter = 0
    # monkeypatch.setattr(check_repo.pathlib, 'Path', MockPath2)
    monkeypatch.setattr(check_repo.pathlib.Path, 'exists', return_false_then_true)
    with pytest.raises(SystemExit):
        check_repo.main(types.SimpleNamespace(project=''))
    assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
            "called Gui.__init__() with args (PosixPath('/tmp'), 'hg')\n"
            'called Gui.show()\n'
            'called MockApplication.exec_()\n')
    # monkeypatch.setattr(check_repo.pathlib, 'Path', MockPath3)
    monkeypatch.setattr(check_repo.pathlib.Path, 'exists', return_false)
    assert check_repo.main(types.SimpleNamespace(project='')) == '. is not a repository'
    assert capsys.readouterr().out == ''


class TestGui:
    def _test_init(self, monkeypatch, capsys):
        monkeypatch.setattr(check_repo, 'Gui', get_repofiles)
        monkeypatch.setattr(check_repo.qtw, 'QWidget', MockWidget)

    def _test_setup_visual(self, monkeypatch, capsys):
        pass

    def test_refresh_frame(self, monkeypatch, capsys):
        # wordt aangeroepen in __init__ daarom niet via fixture testen
        # de andere methode in de init en de methoden die deze aanroept wel mocken
        def mock_init(self, *args):
            print('called QMainWindow.__init__()')
        def mock_populate(self):
            print('called Gui.populate_frame()')
        def mock_setfocus():
            print('called list.setFocus()')
        monkeypatch.setattr(check_repo.qtw, 'QApplication', MockApplication)
        monkeypatch.setattr(check_repo.qtw.QWidget, '__init__', mock_init)
        monkeypatch.setattr(check_repo.qtw, 'QWidget', MockWidget)
        monkeypatch.setattr(check_repo.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(check_repo.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(check_repo.Gui, 'populate_frame', mock_populate)
        testobj = check_repo.Gui(pathlib.Path('base'), 'git')
        # monkeypatch.setattr(testobj.list, 'setFocus', mock_setfocus)
        # testobj.refresh_frame()
        assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
                                           'called QMainWindow.__init__()\n'
                                           'called Gui.setup_visual()\n'
                                           'called list.__init__()\n'
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
        testobj = setup_app(monkeypatch)
        assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
                                           'called QMainWindow.__init__()\n'
                                           'called Gui.setup_visual()\n'
                                           'called list.__init__()\n'
                                           'called Gui.refresh_frame()\n')
        testobj.repotype = 'hg'
        testobj.outtype = 'status'
        assert testobj.get_repofiles() == ['hallo', 'daar', 'jongens']
        assert capsys.readouterr().out == ("run with args: (['hg', 'status'],)"
                                           " {'stdout': -1, 'cwd': 'base'}\n")
        testobj.repotype = 'git'
        testobj.outtype = 'status'
        assert testobj.get_repofiles() == ['hallo', 'daar', 'jongens']
        assert capsys.readouterr().out == ("run with args: (['git', 'status', '--short'],)"
                                           " {'stdout': -1, 'cwd': 'base'}\n")
        testobj.repotype = 'hg'
        testobj.outtype = 'repolist'
        assert testobj.get_repofiles() == ['hallo', 'daar', 'jongens']
        assert capsys.readouterr().out == ("run with args: (['hg', 'manifest'],)"
                                           " {'stdout': -1, 'cwd': 'base'}\n")
        testobj.repotype = 'git'
        testobj.outtype = 'repolist'
        assert testobj.get_repofiles() == ['hallo', 'daar', 'jongens']
        assert capsys.readouterr().out == ("run with args: (['git', 'ls-files'],)"
                                           " {'stdout': -1, 'cwd': 'base'}\n")

    def test_populate_frame(self, monkeypatch, capsys):  #, testobj):
        def mock_setWindowTitle(self, *args):
            print('called QWidget.setWindowTitle() with args `{}`'.format(args))
        def mock_setWindowIcon(self, *args):
            print('called QWidget.setWindowIcon()`')
        def resize(self, *args):
            print('called QWidget.resize() with args `{}`'.format(args))
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_sp_run)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'setWindowIcon', mock_setWindowIcon)
        monkeypatch.setattr(check_repo.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(check_repo.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(check_repo.Gui, 'update_branches', mock_update_branches)
        testobj = setup_app(monkeypatch)
        testobj.populate_frame()   # nog een keer om expliciet aan te roepen
        assert capsys.readouterr().out == ('called MockApplication.__init__()\n'
                                           'called QMainWindow.__init__()\n'
                                           'called Gui.setup_visual()\n'
                                           'called list.__init__()\n'
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
            # return 'selected files'
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
        assert testobj.outtype == 'current text'
        assert capsys.readouterr().out == ('called MockComboBox.__init__()\n'
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
        testobj.commit_all()
        assert capsys.readouterr().out == ("run_and_report with args:"
                                           " ['git', 'commit', '-a', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')
        testobj.repotype = 'hg'
        testobj.commit_all()
        assert capsys.readouterr().out == ("run_and_report with args:"
                                           " ['hg', 'commit', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')
        monkeypatch.setattr(check_repo.qtw.QInputDialog, 'getText', mock_gettext_nok)
        testobj.commit_all()
        assert capsys.readouterr().out == ''

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
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n')
        monkeypatch.setattr(check_repo.Gui, 'get_selected_files', mock_get_selected)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run_and_report with args:"
                                           " ['git', 'add', 'file1', 'file2']\n"
                                           "run_and_report with args: ['git',"
                                           " 'commit', 'file1', 'file2', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')
        testobj.repotype = 'hg'
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
                                           'call filter_tracked()\n'
                                           "run_and_report with args: ['hg',"
                                           " 'commit', 'file1', 'file2', '-m', 'commit_message']\n"
                                           'called Gui.refresh_frame()\n')
        monkeypatch.setattr(check_repo.qtw.QInputDialog, 'getText', mock_gettext_nok)
        testobj.commit_selected()
        assert capsys.readouterr().out == ('call get_selected_filenames()\n'
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
                " 'Show annotations for: file1, file2', 'blame\\noutput')\n")
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

