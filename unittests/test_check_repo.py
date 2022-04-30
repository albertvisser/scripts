import pytest

import check_repo

class MockWidget:
    def __init__(self):
        print('called QWidget.__init__()')
    def setWindowTitle(self.title)
        print('called QWidget.setWindowTitle() with args `{}`'.format(args))
    def setWindowIcon(gui.QIcon('/home/albert/.icons/task.png'))
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
    def setSelectionMode(self, *args):
        print('called list.setSelectionMode()')
    def addItems(self, *args):
        print('called list.addItems() with arg `{}`'.format(args[0]))
    def currentItem(self):
        pass
    def item(self, *args):
        return self.list[args[0]]
    def setFocus(self, *args):
        print('called list.setFocus({})'.format(args[0]))
    def selectedItems(self):
        print('called list.selectedItems() on `{}`'.format(self.list))
        return ['item1', 'item2']
    def takeItem(self, *args):
        print('called list.takeItem(`{}`) on `{}`'.format(args[0], self.list))
    def row(self, *args):
        print('called list.row() on `{}`'.format(self.list))
        return args[0]
    def addItem(self, *args):
        print('called list.addItem(`{}`) on `{}`'.format(args[0], self.list))


class MockListWidgetItem:
    def __init__(self, *args):
        print('called listitem.__init__()')
        self.name = args[0]
    def text(self):
        return self.name
    def setSelected(self, *args):
        print('called listitem.setSelected({}) for `{}`'.format(args[0], self.name))


# --- and now for the actual testing stuff ---
class TestGui:
    def test_init(self, monkeypatch, capsys):
        def mock_get_repofiles(self):
            return file1.py, file2.py
        monkeypatch.setattr(check-repo, 'Gui', get_repofiles)
        monkeypatch.setattr(check-repo.qtw, 'QWidget', MockWidget)

