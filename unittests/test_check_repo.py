import types
import pathlib
import pytest

import check_repo


def setup_app(monkeypatch):
    # monkeypatch.setattr(check_repo.qtw, 'QApplication', MockApplication)
    monkeypatch.setattr(check_repo.qtw, 'QWidget', MockWidget)
    # return check_repo.Gui(MockGui(pathlib.Path('base'), 'git'))
    return check_repo.Gui(pathlib.Path('base'), 'git')


def mock_run(*args, **kwargs):
    print('run with args:', args, kwargs)
    return types.SimpleNamespace(stdout=b'hallo\ndaar\njongens\n')


def mock_setup_visual(self, *args):
    print('called Gui.setup_visual()')


def mock_refresh_frame(self, *args):
    print('called Gui.refresh_frame()')


def mock_get_repofiles(self):
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
        self.app = MockApplication()
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
        self._items = []
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

    def test_get_repofiles(self, monkeypatch, capsys):
        def mock_setWindowTitle(self, *args):
            print('called QWidget.setWindowTitle() with args `{}`'.format(args))
        def mock_setWindowIcon(self, *args):
            print('called QWidget.setWindowIcon()`')
        def resize(self, *args):
            print('called QWidget.resize() with args `{}`'.format(args))
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_run)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'setWindowTitle', mock_setWindowTitle)
        monkeypatch.setattr(check_repo.qtw.QWidget, 'setWindowIcon', mock_setWindowIcon)
        # monkeypatch.setattr(check_repo.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(check_repo.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(check_repo.Gui, 'refresh_frame', mock_refresh_frame)
        testobj = setup_app(monkeypatch)
        assert capsys.readouterr().out == ("run with args: (['git', 'status', '--short'],)"
                                           " {'stdout': -1, 'cwd': 'base'}\n"
                                           'called Gui.setup_visual()\n'
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

    def test_populate_frame(self, monkeypatch, capsys):
        def mock_setup_visual(self):
            self.list = MockListWidget()
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_run)
        monkeypatch.setattr(check_repo.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(check_repo.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(check_repo.Gui, 'update_branches', mock_update_branches)
        testobj = setup_app(monkeypatch)
        assert capsys.readouterr().out == ('called list.__init__()\n'
                                           'called list.clear()\n'
                                           'called list.addItem(`file1.py`) on `[]`\n'
                                           "called list.addItem(`file2.py`) on `['file1.py']`\n"
                                           'called list.setCurrentRow with rownumber 0\n'
                                           'called Gui.update_branches()\n'
                                           'called list.setFocus()\n')

    def test_get_selected_files(self, monkeypatch, capsys):
        def mock_setup_visual(self):
            self.list = MockListWidget()
        monkeypatch.setattr(check_repo.subprocess, 'run', mock_run)
        monkeypatch.setattr(check_repo.Gui, 'get_repofiles', mock_get_repofiles)
        monkeypatch.setattr(check_repo.Gui, 'setup_visual', mock_setup_visual)
        monkeypatch.setattr(check_repo.Gui, 'refresh_frame', mock_refresh_frame)
        testobj = setup_app(monkeypatch)
        # monkeypatch.setattr(testobj.list, 'selectedItems()', lambda x: [
        #     MockListWidgetItem('x y'), MockListWidgetItem('q r')])
        assert capsys.readouterr().out == ('called list.__init__()\n'
                                           'called Gui.refresh_frame()\n')
        testobj.outtype = ''
        assert testobj.get_selected_files() == [('', 'item 1'), ('', 'item 2')]
        assert capsys.readouterr().out == ('called list.selectedItems() on `[]`\n'
                                           'called listitem.__init__()\n'
                                           'called listitem.__init__()\n')
        testobj.outtype = 'status'
        assert testobj.get_selected_files() == [['item', '1'], ['item', '2']]
        assert capsys.readouterr().out == ('called list.selectedItems() on `[]`\n'
                                           'called listitem.__init__()\n'
                                           'called listitem.__init__()\n')

