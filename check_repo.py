#! /usr/bin/env python3
"""examine uncommitted changes in source repository and more
"""
import os
import sys
import pathlib
import argparse
import subprocess
import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as gui
# import PyQt6.QtCore as core
import PyQt6.Qsci as sci  # scintilla
import settings
from check_repo_tooltips import tooltips
import count_locs

HOME = pathlib.Path.home()
root = HOME / 'projects'


class CheckTextDialog(qtw.QDialog):
    """dialoog voor het wijzigen van de commit (message en geselecteerde extra files
    """
    def __init__(self, parent, title='', message=''):
        self._parent = parent
        super().__init__(parent)
        self.setWindowTitle(title)
        vbox = qtw.QVBoxLayout()
        hbox = qtw.QHBoxLayout()
        self.check = qtw.QCheckBox('Add selected files to the last commit', self)
        hbox.addWidget(self.check)
        vbox.addLayout(hbox)
        hbox = qtw.QHBoxLayout()
        hbox.addWidget(qtw.QLabel('Modify the commit message if needed:', self))
        vbox.addLayout(hbox)
        hbox = qtw.QHBoxLayout()
        self.text = qtw.QLineEdit(self)
        self.text.setText(message)
        hbox.addWidget(self.text)
        vbox.addLayout(hbox)
        hbox = qtw.QHBoxLayout()
        hbox.addStretch(1)
        ok_button = qtw.QPushButton('&Ok', self)
        ok_button.clicked.connect(self.accept)
        hbox.addWidget(ok_button)
        cancel_button = qtw.QPushButton('&Cancel', self)
        cancel_button.clicked.connect(self.reject)
        hbox.addWidget(cancel_button)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def accept(self):
        "gewijzigde waarden teruggeven aan de aanroeper"
        self._parent.dialog_data = self.check.isChecked(), self.text.text()
        super().accept()


class DiffViewDialog(qtw.QDialog):
    """dialoog voor het tonen van de diff output
    """
    def __init__(self, parent, title='', caption='', data='', size=(600, 400)):
        "create a window with a scintilla text widget and an ok button"
        showlocs = caption.startswith('Show loc-counts')
        self.data = data
        self._parent = parent
        super().__init__(parent)
        self.setWindowTitle(title)
        ## self.setWindowIcon(self._parent._parent.appicon)
        self.resize(size[0], size[1])
        vbox = qtw.QVBoxLayout()
        hbox = qtw.QHBoxLayout()
        hbox.addWidget(qtw.QLabel(caption, self))
        vbox.addLayout(hbox)
        hbox = qtw.QHBoxLayout()
        self.text = sci.QsciScintilla(self)
        self.setup_text()
        self.text.setText(data)
        self.text.setReadOnly(True)
        hbox.addWidget(self.text)
        vbox.addLayout(hbox)
        hbox = qtw.QHBoxLayout()
        if showlocs:
            export_button = qtw.QPushButton('&Copy', self)
            export_button.clicked.connect(self.export)
        ok_button = qtw.QPushButton('&Done', self)
        ok_button.clicked.connect(self.close)
        ok_button.setDefault(True)
        hbox.addStretch()
        if showlocs:
            hbox.addWidget(export_button)
        hbox.addWidget(ok_button)
        hbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        do = gui.QAction('Done', self)
        do.triggered.connect(self.close)
        do.setShortcut('Esc')
        self.addAction(do)
        ## do.setShortCut(core.Qt.Key_Escape)

    def setup_text(self):
        "define the scintilla widget's properties"
        # Set the default font
        font = gui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.text.setFont(font)
        self.text.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = gui.QFontMetrics(font)
        self.text.setMarginsFont(font)
        self.text.setMarginWidth(0, fontmetrics.horizontalAdvance("00000"))
        self.text.setMarginLineNumbers(0, True)
        self.text.setMarginsBackgroundColor(gui.QColor("#cccccc"))

        # Enable brace matching, auto-indent, code-folding
        self.text.setBraceMatching(sci.QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.text.setAutoIndent(True)
        self.text.setFolding(sci.QsciScintilla.FoldStyle.PlainFoldStyle)

        # Current line visible with special background color
        self.text.setCaretLineVisible(True)
        self.text.setCaretLineBackgroundColor(gui.QColor("#ffe4e4"))

        # Set HTML lexer
        lexer = sci.QsciLexerDiff()
        lexer.setDefaultFont(font)
        self.text.setLexer(lexer)

    def export(self):
        "transform output and copy to clipboard"
        outlist = count_locs.sort_locs_by_lineno(self.data.split('\n'))
        clp = qtw.QApplication.clipboard()
        clp.setText('\n'.join(outlist))


class FriendlyReminder(qtw.QDialog):
    """check if we linted and tested
    """
    def __init__(self, parent):
        self._parent = parent
        super().__init__(parent)
        self.setWindowTitle('Friendly Reminder')
        vbox = qtw.QVBoxLayout()
        vbox.addWidget(qtw.QLabel('* Did you lint the files to be committed?'))
        vbox.addSpacing(5)
        vbox.addWidget(qtw.QLabel('* Did you test the files to be committed?'))
        vbox.addSpacing(5)
        self.complete = qtw.QCheckBox("Yes, I know what I'm doing", self)
        vbox.addWidget(self.complete)
        hbox = qtw.QHBoxLayout()
        hbox.addStretch(1)
        ok_button = qtw.QPushButton('&Ok', self)
        ok_button.clicked.connect(self.accept)
        hbox.addWidget(ok_button)
        cancel_button = qtw.QPushButton('&Cancel', self)
        cancel_button.clicked.connect(self.reject)
        hbox.addWidget(cancel_button)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def accept(self):
        "check for ticks"
        if self.complete.isChecked():
            super().accept()
        else:
            qtw.QMessageBox.information(self, self._parent.title, "You didn't tick all the boxes")


class Gui(qtw.QWidget):
    """User interface"""
    def __init__(self, path, repotype):
        self.path = path
        self.repotype = repotype
        self.outtype = 'status'
        # self.filelist = self.get_repofiles() deze zit ook in refresh_frame

        self.project = path.stem
        self.app = qtw.QApplication(sys.argv)
        super().__init__()
        self.title = f'Uncommitted changes for `{self.project}`'
        self.setup_visual()

        # start assuming Meld is present
        self.got_meld = True
        self.refresh_frame()

    def setup_visual(self):
        """definieer het scherm en een aantal andere zaken
        """
        self.setWindowTitle(self.title)
        self.setWindowIcon(gui.QIcon('/home/albert/.icons/task.png'))
        vbox = qtw.QVBoxLayout()

        hbox = qtw.QHBoxLayout()
        hbox.addWidget(qtw.QLabel('Branch:', self))
        self.cb_branch = qtw.QComboBox(self)
        self.cb_branch.setEditable(True)
        self.cb_branch.setToolTip(tooltips['branch'])
        hbox.addWidget(self.cb_branch)

        btn = qtw.QPushButton('Create', self)
        btn.clicked.connect(self.create_branch)
        btn.setToolTip(tooltips['create'])
        hbox.addWidget(btn)
        btn = qtw.QPushButton('Switch To', self)
        btn.clicked.connect(self.switch2branch)
        btn.setToolTip(tooltips['switch'])
        hbox.addWidget(btn)
        btn = qtw.QPushButton('Stash', self)
        btn.setMenu(self.setup_stashmenu())
        btn.setToolTip(tooltips['stash'])
        hbox.addWidget(btn)
        btn = qtw.QPushButton('Merge', self)
        btn.clicked.connect(self.merge_branch)
        btn.setToolTip(tooltips['merge'])
        hbox.addWidget(btn)
        btn = qtw.QPushButton('Delete', self)
        btn.clicked.connect(self.delete_branch)
        btn.setToolTip(tooltips['delete'])
        hbox.addWidget(btn)

        hbox.addStretch()
        btn = qtw.QPushButton(gui.QIcon.fromTheme('document-multiple'), 'Open Extrn', self)
        # btn = qtw.QPushButton('&Open Docs', self)
        btn.setToolTip(tooltips['docs'])
        menu = qtw.QMenu()
        # menu.addAction('Open project &Notes').triggered.connect(self.open_notes)
        menu.addAction('Open project &Docs').triggered.connect(self.open_docs)
        menu.addAction('Open CGit (local repos)').triggered.connect(self.open_cgit)
        menu.addAction('Open GitWeb (remote repos)').triggered.connect(self.open_gitweb)
        # btn.clicked.connect(self.open_docs)
        btn.setMenu(menu)
        btn.setShortcut('Shift+F6')
        hbox.addWidget(btn)

        vbox.addLayout(hbox)

        hbox = qtw.QHBoxLayout()
        self.list = qtw.QListWidget(self)
        self.list.setSelectionMode(qtw.QAbstractItemView.SelectionMode.ExtendedSelection)
        # self.populate_frame()
        hbox.addWidget(self.list)

        vbox2 = qtw.QVBoxLayout()
        # vbox2.addSpacing(10)
        hbox2 = qtw.QHBoxLayout()
        hbox2.addWidget(qtw.QLabel('Show:', self))
        self.cb_list = qtw.QComboBox(self)
        self.cb_list.addItems(['status', 'repolist'])
        self.cb_list.currentIndexChanged.connect(self.set_outtype)
        self.cb_list.setToolTip(tooltips['show'])
        hbox2.addWidget(self.cb_list)
        vbox2.addLayout(hbox2)
        vbox2.addWidget(qtw.QLabel('Select file(s) and', self))
        btn = qtw.QPushButton('&Edit', self)
        btn.setToolTip(tooltips['edit'])
        btn.clicked.connect(self.edit_selected)
        vbox2.addWidget(btn)
        btn = qtw.QPushButton('Count &# Lines', self)
        btn.setToolTip(tooltips['count'])
        btn.clicked.connect(self.count_selected)
        vbox2.addWidget(btn)
        btn = qtw.QPushButton('Show &Diff', self)
        btn.setToolTip(tooltips['diff'])
        btn.clicked.connect(self.diff_selected)
        vbox2.addWidget(btn)
        btn = qtw.QPushButton('&Lint', self)
        btn.setToolTip(tooltips['lint'])
        btn.clicked.connect(self.lint_selected)
        vbox2.addWidget(btn)
        btn = qtw.QPushButton('&Blame', self)
        btn.setToolTip(tooltips['blame'])
        btn.clicked.connect(self.annotate)
        vbox2.addWidget(btn)
        btn = qtw.QPushButton('&Commit', self)
        btn.setToolTip(tooltips['commit'])
        btn.clicked.connect(self.commit_selected)
        vbox2.addWidget(btn)
        btn = qtw.QPushButton('A&mend', self)
        btn.setToolTip(tooltips['amend'])
        btn.clicked.connect(self.amend_commit)
        vbox2.addWidget(btn)
        btn = qtw.QPushButton('Re&vert', self)
        btn.setToolTip(tooltips['revert'])
        btn.clicked.connect(self.revert_selected)
        vbox2.addWidget(btn)
        btn = qtw.QPushButton('Start &Tracking', self)
        btn.setToolTip(tooltips['track'])
        btn.clicked.connect(self.add_new)
        vbox2.addWidget(btn)
        btn = qtw.QPushButton('&Stop Tracking', self)
        btn.setToolTip(tooltips['untrack'])
        btn.clicked.connect(self.forget)
        vbox2.addWidget(btn)
        btn = qtw.QPushButton('Add to &Ignore list', self)
        btn.setToolTip(tooltips['ignore'])
        btn.clicked.connect(self.add_ignore)
        vbox2.addWidget(btn)
        vbox2.addWidget(qtw.QLabel('', self))
        hbox.addLayout(vbox2)
        vbox.addLayout(hbox)

        hbox = qtw.QHBoxLayout()
        hbox.addStretch()
        btn = qtw.QPushButton('C&ount LOCs', self)
        btn.setToolTip(tooltips['count_all'])
        btn.clicked.connect(self.count_all)
        hbox.addWidget(btn)
        btn = qtw.QPushButton('Di&ff all Files', self)
        btn.setToolTip(tooltips['diff_all'])
        btn.clicked.connect(self.diff_all)
        hbox.addWidget(btn)
        btn = qtw.QPushButton('Li&nt all Files', self)
        btn.setToolTip(tooltips['lint_all'])
        btn.clicked.connect(self.lint_all)
        hbox.addWidget(btn)
        btn = qtw.QPushButton('Commit &All changes', self)
        btn.setToolTip(tooltips['commit_all'])
        btn.clicked.connect(self.commit_all)
        hbox.addWidget(btn)
        btn = qtw.QPushButton('&Recheck repo', self)
        btn.setToolTip(tooltips['recheck'])
        btn.clicked.connect(self.refresh_frame)
        hbox.addWidget(btn)
        btn = qtw.QPushButton('View &History', self)
        btn.setToolTip(tooltips['history'])
        btn.clicked.connect(self.view_repo)
        hbox.addWidget(btn)
        btn = qtw.QPushButton('&Quit', self)
        btn.setToolTip(tooltips['quit'])
        btn.clicked.connect(self.close)
        hbox.addWidget(btn)
        hbox.addStretch()
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        do = gui.QAction('Done', self)
        do.triggered.connect(self.close)
        do.setShortcut('Ctrl+Q')
        self.addAction(do)

    def get_repofiles(self):
        """return results of "status" command -- list uncommitted / untracked files
        """
        if self.outtype == 'status':
            command = [self.repotype, 'status']
            if self.repotype == 'git':
                command.append('--short')
        else:  # if self.outtype == 'repolist':  # -- currently the only other possibility
            command = {'hg': ['hg', 'manifest'], 'git': ['git', 'ls-files']}[self.repotype]
        result = subprocess.run(command, stdout=subprocess.PIPE, cwd=str(self.path), check=False)
        return [x for x in str(result.stdout, encoding='utf-8').split('\n') if x]

    def populate_frame(self):
        """(re)populate list"""
        self.list.clear()
        for name in self.filelist:
            self.list.addItem(name)
        self.list.setCurrentRow(0)
        self.update_branches()

    def get_selected_files(self):
        """get a list of the selected filenames"""
        if self.outtype == 'status':
            return [item.text().split(None, 1) for item in self.list.selectedItems()]
        return [('', item.text()) for item in self.list.selectedItems()]

    def edit_selected(self):
        """Open selected files in a text editor"""
        command = [y for x, y in self.get_selected_files()]
        # command.insert(0, 'SciTE')
        command[:0] = ['gnome-terminal', '--profile', 'Code Editor Shell', '--', 'vim']
        self.just_run(command)
        self.refresh_frame()

    def count_all(self):
        """show lines of code for all tracked files
        """
        filenames = self.filter_modules()
        if filenames:
            lines = get_locs_for_modules(filenames, self.path)
            caption = 'Show loc-counts for all tracked modules'
            DiffViewDialog(self, self.title, caption, '\n'.join(lines), (600, 400)).exec()

    def count_selected(self):
        """show lines of code for selected files
        """
        filenames = self.filter_tracked(self.get_selected_files())
        if filenames:
            lines = get_locs_for_modules(filenames, self.path)
            caption = 'Show loc-counts for: ' + ', '.join(filenames)
            DiffViewDialog(self, self.title, caption, '\n'.join(lines), (600, 400)).exec()

    def diff_all(self):
        """show diff for all tracked files
        """
        command = ['meld', '.']
        if self.got_meld:
            try:
                self.just_run(command)
            except OSError:
                self.got_meld = False
        if not self.got_meld:
            qtw.QMessageBox.information(self, self.title, 'Sorry, not possible at this time -'
                                        ' Meld not installed')

    def diff_selected(self):
        """show selected files in diff view"""
        filenames = self.filter_tracked(self.get_selected_files())
        if self.got_meld:
            for name in filenames:
                command = ['meld', name]
                try:
                    self.just_run(command)
                except OSError:
                    self.got_meld = False
                    break
        if not self.got_meld and filenames:
            command = [self.repotype, 'diff'] + filenames
            _out, _err = self.run_and_capture(command)
            if _err:
                qtw.QMessageBox.information(self, self.title, '\n'.join(_err))
                return
            caption = 'Show diffs for: ' + ', '.join(filenames)
            DiffViewDialog(self, self.title, caption, _out).exec()

    def add_ignore(self):
        """add selected file to ignore list"""
        filenames = [x[1] for x in self.get_selected_files()]
        if filenames:
            fname = '.hgignore' if self.repotype == 'hg' else '.gitignore'
            fname = self.path / fname
            with fname.open('a') as _out:
                for name in filenames:
                    print(name, file=_out)
            self.refresh_frame()
        # qtw.QMessageBox.information(self, self.title, 'Added selected files to ignore list.')

    def add_new(self):
        """add selected file(s) to the tracked list"""
        filenames = [y for x, y in self.get_selected_files()]
        self.run_and_report([self.repotype, 'add'] + filenames)
        self.refresh_frame()

    def forget(self):
        """stop tracking selected file(s)"""
        commands = {'hg': ['hg', 'forget'], 'git': ['git', 'rm', '--cached']}
        filenames = [y for x, y in self.get_selected_files()]
        self.run_and_report(commands[self.repotype] + filenames)
        self.refresh_frame()

    def set_outtype(self, *args):
        """register change in selected output format"""
        self.outtype = self.cb_list.currentText()
        self.refresh_frame()

    def refresh_frame(self):
        """recheck repository and update list"""
        self.filelist = self.get_repofiles()
        self.populate_frame()
        self.list.setFocus()

    def commit_all(self):
        """hg commit uitvoeren - vraag om commit message"""
        if FriendlyReminder(self).exec() == qtw.QDialog.DialogCode.Rejected:
            return
        message, ok = qtw.QInputDialog.getText(self, self.title, 'Enter a commit message:')
        if ok:
            commands = {'git': ['git', 'commit', '-a', '-m', message],
                        'hg': ['hg', 'commit', '-m', message]}
            self.run_and_report(commands[self.repotype])
            self.refresh_frame()

    def commit_selected(self):
        """hg commit <selected files> uitvoeren - vraag om commit message"""
        # if FriendlyReminder(self).exec() == qtw.QDialog.DialogCode.Rejected:
        #     return
        # filenames = self.filter_tracked(self.get_selected_files())
        filelist = self.get_selected_files()
        to_commit = [pathlib.Path(x[1]) for x in filelist]
        if ([y for y in to_commit if y.suffix == '.py' and not y.name.startswith('test_')]
                and FriendlyReminder(self).exec() == qtw.QDialog.DialogCode.Rejected):
            return
        filenames = self.filter_tracked(filelist)
        if filenames:
            message, ok = qtw.QInputDialog.getText(self, self.title, 'Enter a commit message:')
            if ok:
                if self.repotype == 'git':
                    self.run_and_report(['git', 'add'] + filenames)
                self.run_and_report([self.repotype, 'commit'] + filenames + ['-m', message])
                self.refresh_frame()

    def amend_commit(self):
        "add files to last commit or change commit message"
        if self.repotype != 'git':
            qtw.QMessageBox.information(self, self.title, 'Only implemented for git repos')
            return
        out = self.run_and_capture(['git', 'status', '-uno'])[0]
        if not 'ahead' in out[1]:
        # if 'up to date' in out[1]:
            qtw.QMessageBox.information(self, self.title,
                                        'Cannot amend: last commit was already pushed')
            return
        message = self.run_and_capture(['git', 'log', '-1', '--pretty=format:%s'])[0][0]
        self.dialog_data = None, None
        if CheckTextDialog(self, self.title, message).exec() != qtw.QDialog.DialogCode.Accepted:
            return
        add_files, commit_message = self.dialog_data
        if add_files:
            filenames = self.filter_tracked(self.get_selected_files())
            if filenames:
                self.run_and_report(['git', 'add'] + filenames)
        self.run_and_report([self.repotype, 'commit', '--amend', '-m', commit_message])
        self.refresh_frame()

    def revert_selected(self):
        """hg revert <selected files> uitvoeren
        """
        filenames = self.filter_tracked(self.get_selected_files())
        if filenames:
            commands = {'git': ['git', 'checkout', '--'], 'hg': ['hg', 'revert']}
            self.run_and_report(commands[self.repotype] + filenames)
            self.refresh_frame()

    def lint_selected(self):
        """execute permissive linting on selected files
        """
        filelist = self.filter_tracked(self.get_selected_files(), notify=False)
        # [name for letter, name in self.get_selected_files() if letter not in ('?', '??')]
        if filelist:
            mode = '-f' if len(filelist) == 1 else '-l'
            self.just_run(['lintergui', '-m', 'permissive', mode] + filelist)
        else:
            qtw.QMessageBox.information(self, self.title, 'No tracked files selected')

    def lint_all(self):
        """execute permissive linting on all files in repository
        """
        self.just_run(['lintergui', '-m', 'permissive', '-r', self.project])

    def annotate(self):
        """show selected files in annotated view"""
        filenames = self.filter_tracked(self.get_selected_files())
        if filenames:
            command = [self.repotype, 'blame'] + filenames
            _out, _err = self.run_and_capture(command)
            if _err:
                qtw.QMessageBox.information(self, self.title, '\n'.join(_err))
                return
            caption = 'Show annotations for: ' + ', '.join(filenames)
            DiffViewDialog(self, self.title, caption, '\n'.join(_out), (1200, 800)).exec()

    def filter_tracked(self, filelist, notify=True):
        """return only the tracked files, optionally (don't) show messages for untracked ones
        """
        filenames = []
        for letter, name in filelist:
            if letter in ('?', '??'):
                if notify:
                    qtw.QMessageBox.information(self, self.title, name + ' not tracked')
            else:
                filenames.append(name)
        return filenames

    def filter_modules(self, include_tests=False):
        "return tracked Python modules, optionally excluding modules with unittests"
        filenames = []
        result_list, errors = self.run_and_capture(['git', 'ls-files'])
        if errors:
            qtw.QMessageBox.information(self, self.title, '\n'.join(errors))
            return []
        for name in result_list:
            if os.path.splitext(name)[1] != '.py':
                continue
            parent = os.path.dirname(name)
            if not include_tests and parent and 'test' in parent:
                continue
            filenames.append(name)
        return filenames

    def view_repo(self):
        """execute hg view"""
        command = {'hg': ['hg', 'view'], 'git': ['gitg']}[self.repotype]
        self.just_run(command)

    def update_branches(self):
        """build a list of branches and update combobox
        """
        if self.repotype != 'git':
            return
        stdout, stderr = self.run_and_capture(['git', 'branch'])
        if stderr:
            qtw.QMessageBox.information(self, self.title, '\n'.join(stderr))
            return
        current, branches = 0, []
        for ix, item in enumerate(stdout):
            test = item.split(None, 1)
            branches.append(test[-1])
            if len(test) > 1 and test[0] == '*':
                current = ix
        self.cb_branch.clear()
        self.cb_branch.addItems(branches)
        self.cb_branch.setCurrentIndex(current)

    def create_branch(self):
        """create a new branch
        """
        branch_name = self.cb_branch.currentText()
        if not branch_name or branch_name == self.find_current_branch():
            qtw.QMessageBox.information(self, self.title,
                                        'Enter a new branch name in the combobox first')
            return
        self.run_and_report(['git', 'branch', branch_name])
        self.update_branches()

    def switch2branch(self):
        """switch to the chosen branch
        """
        branch_name = self.cb_branch.currentText()
        if not branch_name or branch_name == self.find_current_branch():
            qtw.QMessageBox.information(self, self.title,
                                        'Select a branch different from the current one first')
            return
        self.run_and_report(['git', 'checkout', branch_name])
        # self.update_branches()
        self.refresh_frame()

    def merge_branch(self):
        """merge the chosen branch with the current
        """
        branch_name = self.cb_branch.currentText()
        current = self.find_current_branch()
        if not branch_name or branch_name == current:
            qtw.QMessageBox.information(self, self.title,
                                        'Select a branch different from the current one first')
            return
        ok = qtw.QMessageBox.question(self, self.title, f'Merge {branch_name} into {current}?')
        if ok == qtw.QMessageBox.StandardButton.Yes:
            self.run_and_report(['git', 'merge', branch_name])
            # self.update_branches()
            self.refresh_frame()

    def delete_branch(self):
        """delete the chosen branch
        """
        branch_name = self.cb_branch.currentText()
        self.run_and_report(['git', 'branch', '-d', branch_name])
        # als de branch verwijderd kan worden krijg je alleen een melding in de stdout
        self.update_branches()

    def setup_stashmenu(self):
        """define popup menu with options to create and retrieve stashes
        """
        menu = qtw.QMenu()
        for label, callback in (('&New Stash', self.stash_push),
                                ('&Apply Stash', self.stash_pop),
                                ('&Remove Stash', self.stash_kill)):
            action = gui.QAction(label, self)
            action.triggered.connect(callback)
            menu.addAction(action)
        return menu

    def stash_push(self):
        "create a new stash on the current branch"
        qtw.QMessageBox.information(self, self.title, 'create stash')
        self.run_and_report(['git', 'stash', 'push'])

    def select_stash(self):
        """show popup with list of current stashes; return the selected one
        """
        stashes, stderr = self.run_and_capture(['git', 'stash', 'list'])
        if stderr:
            qtw.QMessageBox.information(self, self.title, '\n'.join(stderr))
            return ''
        if not stashes:
            qtw.QMessageBox.information(self, self.title, 'No stashes found')
            return ''
        stash, ok = qtw.QInputDialog.getItem(self, self.title, 'select a stash from the list',
                                             stashes)
        stashid = stash.split(': ')[0] if ok else ''
        return stashid

    def stash_pop(self):
        "apply a stash to the current branch"
        stash_id = self.select_stash()
        if stash_id:
            self.run_and_report(['git', 'stash', 'apply', stash_id])

    def stash_kill(self):
        "delete a shash"
        stash_id = self.select_stash()
        if stash_id:
            self.run_and_report(['git', 'stash', 'drop', stash_id])

    def open_notes(self):
        "open project notities (a-propos bestandje)"
        # self.run_and_continue(['binfab', 'repo.mee-bezig'])
        name = self.path.resolve().name.title()
        self.run_and_continue(['a-propos', '-n', f'Mee Bezig ({name})', '-f', 'mee-bezig'])

    def open_docs(self):
        "open project documentatie (treedocs bestandje)"
        if len(sys.argv) == 1 or sys.argv[1] == '.':
            where = os.getcwd()
        else:
            where = settings.get_project_dir(sys.argv[1])
        self.run_and_continue(['treedocs', f'{where}/projdocs.trd'])

    def open_cgit(self):
        "open CGit server in standalone browser app)"
        self.run_and_continue(['binfab', 'www.startapp', 'cgit'])

    def open_gitweb(self):
        "open GitWeb server in standalone browser app"
        self.run_and_continue(['binfab', 'www.startapp', 'gitweb'])

    def find_current_branch(self):
        "determine the branch we're currently on"
        out = self.run_and_capture(['git', 'branch'])[0]
        return [x[2:] for x in out if x.startswith('* ')][0].strip().split()[-1]

    def just_run(self, command_list):
        "shortcut for call to subprocess (no interest in result"
        subprocess.run(command_list, cwd=str(self.path), check=False)

    def run_and_continue(self, command_list):
        "shortcut for call to subprocess (don't wait for completion)"
        subprocess.Popen(command_list, cwd=str(self.path))

    def run_and_report(self, command_list):
        "shortcut for call to subprocess (reports results from stdout and stderr)"
        result = subprocess.run(command_list, capture_output=True, cwd=str(self.path), check=False)
        if result.stdout is not None:
            text = str(result.stdout, encoding='utf-8').strip('\n')
            if text:
                qtw.QMessageBox.information(self, self.title, text)
        if result.stderr is not None:
            text = str(result.stderr, encoding='utf-8').strip('\n')
            if text:
                qtw.QMessageBox.warning(self, self.title, text)

    def run_and_capture(self, command_list):
        "shortcut for call to subprocess (returns stdout and stderr as lists)"
        result = subprocess.run(command_list, capture_output=True, cwd=str(self.path), check=False)
        ret1, ret2 = [], []
        if result.stdout is not None:
            ret1 = [x for x in str(result.stdout, encoding='utf-8').split('\n') if x]
        if result.stderr is not None:
            ret2 = [x for x in str(result.stderr, encoding='utf-8').split('\n') if x]
        return ret1, ret2


def get_locs_for_modules(namelist, path):
    "turn filenames into modulenames and count locs"
    result = []
    for name in namelist:
        result.extend(['', count_locs.HEADING.format(name), ''])
        name = os.path.splitext(name)[0].replace('/', '.')
        try:
            for x, y, z in count_locs.get_locs(name, path):
                if y:
                    where = f'{z}' if y == 1 else f'{z}-{z + y - 1}'
                    result.append(count_locs.DETAIL.format(x, y, where))
                else:
                    result.append(x)
        except ImportError as e:
            result.extend([f'{name} could not be counted this way because of the following error',
                           f'ImportError: {e}'])
    return result


def startapp(args):
    """do the thing"""
    repotype = ''
    if not args.project:
        args.project = '.'
    if args.project == '.':
        path = pathlib.Path.cwd()  # .resolve()
    elif args.project in settings.r2h_repos:
        path = pathlib.Path(settings.r2hdata_basedir) / settings.r2h_repos[args.project]
    elif args.project in settings.private_repos:
        path = HOME / settings.private_repos[args.project]
    elif args.project in settings.private_repos.values():
        path = HOME / args.project
    else:
        path = root / args.project
    test = path / '.git'
    if test.exists():
        repotype = 'git'
    else:
        test = path / '.hg'
        if test.exists():
            repotype = 'hg'
    if not repotype:
        return args.project + ' is not a repository'
    win = Gui(path, repotype)
    win.show()
    sys.exit(win.app.exec())


def main():
    "parse arguments and go"
    parser = argparse.ArgumentParser()
    parser.add_argument('project', help="name of a software project", nargs='?', default="")
    results = startapp(parser.parse_args())
    if results:
        print(results)


if __name__ == '__main__':
    main()
