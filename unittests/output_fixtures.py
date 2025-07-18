"""construe expected output for gui test functions (mostly in bin/check_repo.py)
"""
import pytest

check_text = """\
called dialog.__init()__ with args ()
called dialog.setWindowTitle() with args ('title',)
called VBox.__init__
called HBox.__init__
called CheckBox.__init__ with text 'Add selected files to the last commit'
called HBox.addWidget with arg MockCheckBox
called VBox.addLayout with arg MockHBoxLayout
called HBox.__init__
called Label.__init__ with args ('Modify the commit message if needed:', {testobj})
called HBox.addWidget with arg MockLabel
called VBox.addLayout with arg MockHBoxLayout
called HBox.__init__
called LineEdit.__init__
called LineEdit.setText with arg `message`
called HBox.addWidget with arg MockLineEdit
called VBox.addLayout with arg MockHBoxLayout
called HBox.__init__
called HBox.addStretch
called PushButton.__init__ with args ('&Ok', {testobj}) {{}}
called Signal.connect with args ({testobj.accept},)
called HBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('&Cancel', {testobj}) {{}}
called Signal.connect with args ({testobj.reject},)
called HBox.addWidget with arg MockPushButton
called HBox.addStretch
called VBox.addLayout with arg MockHBoxLayout
called dialog.setLayout()
"""
diffview_start = """\
called dialog.__init()__ with args ()
called dialog.setWindowTitle() with args ('title',)
called dialog.resize()
called VBox.__init__
called HBox.__init__
called Label.__init__ with args ('{caption}', {testobj})
called HBox.addWidget with arg MockLabel
called VBox.addLayout with arg MockHBoxLayout
called HBox.__init__
called Editor.__init__ with args ({testobj},)
called Font.__init__
called Font.setFamily
called Font.setFixedPitch with arg `True`
called Font.setPointSize
called Editor.setFont
called Editor.setMarginsFont
called Fontmetrics.__init__()
called Editor.setMarginsFont
called Editor.horizontalAdvance()
called Editor.setMarginWidth with args (0, None)
called Editor.setMarginLineNumbers with args (0, True)
called Editor.setMarginsBackgroundColor with arg 'color #cccccc'
called Editor.setBraceMatching with arg `2`
called Editor.setAutoIndent with arg `True`
called Editor.setFolding with arg `3`
called Editor.setCaretLineVisible with arg `True`
called Editor.setCaretLineBackgroundColor with arg 'color #ffe4e4'
called Lexer.__init__()
called Editor.setDefaultFont
called Editor.setLexer
called Editor.setText with arg `{testobj.data}`
called Editor.setReadOnly with arg `True`
called HBox.addWidget with arg MockEditorWidget
called VBox.addLayout with arg MockHBoxLayout
called HBox.__init__
"""
dv_copy1 = """\
called PushButton.__init__ with args ('&Copy', {testobj}) {{}}
called Signal.connect with args ({testobj.export},)
"""
diffview_middle = """\
called PushButton.__init__ with args ('&Done', {testobj}) {{}}
called Signal.connect with args ({testobj.close},)
called PushButton.setDefault with arg `True`
called HBox.addStretch
"""
dv_copy2 = """\
called HBox.addWidget with arg MockPushButton
"""
diffview_end = """\
called HBox.addWidget with arg MockPushButton
called HBox.addStretch
called VBox.addLayout with arg MockHBoxLayout
called dialog.setLayout()
called Action.__init__ with args ('Done', {testobj})
called Signal.connect with args ({testobj.close},)
called Action.setShortcut with arg `Esc`
called dialog.addAction()
"""
friendly_reminder = """\
called dialog.__init()__ with args ()
called dialog.setWindowTitle() with args ('Friendly Reminder',)
called VBox.__init__
called Label.__init__ with args ('* Did you lint the files to be committed?',)
called VBox.addWidget with arg MockLabel
called VBox.addSpacing
called Label.__init__ with args ('* Did you test the files to be committed?',)
called VBox.addWidget with arg MockLabel
called VBox.addSpacing
called CheckBox.__init__ with text 'Yes, I know what I'm doing'
called VBox.addWidget with arg MockCheckBox
called HBox.__init__
called HBox.addStretch
called PushButton.__init__ with args ('&Ok', {testobj}) {{}}
called Signal.connect with args ({testobj.accept},)
called HBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('&Cancel', {testobj}) {{}}
called Signal.connect with args ({testobj.reject},)
called HBox.addWidget with arg MockPushButton
called HBox.addStretch
called VBox.addLayout with arg MockHBoxLayout
called dialog.setLayout()
"""
main_gui = """\
called Application.__init__
called widget.__init()__ with args ()
called widget.setWindowTitle() with args ('Uncommitted changes for `base`',)
called Icon.__init__ with arg `/home/albert/.icons/task.png`
called widget.setWindowIcon()
called VBox.__init__
called VBox.__init__
called Label.__init__ with args ('Branch:', {testobj})
called VBox.addWidget with arg MockLabel
called ComboBox.__init__
called ComboBox.setEditable with arg `True`
called ComboBox.setToolTip({branch})
called VBox.addWidget with arg MockComboBox
called PushButton.__init__ with args ('Create', {testobj}) {{}}
called Signal.connect with args ({testobj.create_branch},)
called PushButton.setToolTip with arg `{create}`
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Switch To', {testobj}) {{}}
called Signal.connect with args ({testobj.switch2branch},)
called PushButton.setToolTip with arg `{switch}`
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Stash', {testobj}) {{}}
called widget.setup_stashmenu()
called PushButton.setMenu()
called PushButton.setToolTip with arg `{stash}`
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Merge', {testobj}) {{}}
called Signal.connect with args ({testobj.merge_branch},)
called PushButton.setToolTip with arg `{merge}`
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Delete', {testobj}) {{}}
called Signal.connect with args ({testobj.delete_branch},)
called PushButton.setToolTip with arg `{delete}`
called VBox.addWidget with arg MockPushButton
called VBox.addStretch
called Icon.fromTheme with args ()
called PushButton.__init__ with args (None, 'Open Extrn', {testobj}) {{}}
called PushButton.setToolTip with arg `{docs}`
called Menu.__init__ with args ()
called Menu.addAction with args `Open project &Docs` None
called Action.__init__ with args ('Open project &Docs', None)
called Signal.connect with args ({testobj.open_docs},)
called Menu.addAction with args `Open CGit (local repos)` None
called Action.__init__ with args ('Open CGit (local repos)', None)
called Signal.connect with args ({testobj.open_cgit},)
called Menu.addAction with args `Open GitWeb (remote repos)` None
called Action.__init__ with args ('Open GitWeb (remote repos)', None)
called Signal.connect with args ({testobj.open_gitweb},)
called PushButton.setMenu()
called PushButton.setShortcut with args ('Shift+F6',)
called VBox.addWidget with arg MockPushButton
called VBox.addLayout with arg MockVBoxLayout
called VBox.__init__
called List.__init__
called List.setSelectionMode
called VBox.addWidget with arg MockListBox
called VBox.__init__
called VBox.__init__
called Label.__init__ with args ('Show:', {testobj})
called VBox.addWidget with arg MockLabel
called ComboBox.__init__
called ComboBox.addItems with arg ['status', 'repolist']
called Signal.connect with args ({testobj.set_outtype},)
called ComboBox.setToolTip({show})
called VBox.addWidget with arg MockComboBox
called VBox.addLayout with arg MockVBoxLayout
called Label.__init__ with args ('Select file(s) and', {testobj})
called VBox.addWidget with arg MockLabel
called PushButton.__init__ with args ('&Edit', {testobj}) {{}}
called PushButton.setToolTip with arg `{edit}`
called Signal.connect with args ({testobj.edit_selected},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Count &# Lines', {testobj}) {{}}
called PushButton.setToolTip with arg `{count}`
called Signal.connect with args ({testobj.count_selected},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Show &Diff', {testobj}) {{}}
called PushButton.setToolTip with arg `{diff}`
called Signal.connect with args ({testobj.diff_selected},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('&Lint', {testobj}) {{}}
called PushButton.setToolTip with arg `{lint}`
called Signal.connect with args ({testobj.lint_selected},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('&Blame', {testobj}) {{}}
called PushButton.setToolTip with arg `{blame}`
called Signal.connect with args ({testobj.annotate},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('&Commit', {testobj}) {{}}
called PushButton.setToolTip with arg `{commit}`
called Signal.connect with args ({testobj.commit_selected},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('A&mend', {testobj}) {{}}
called PushButton.setToolTip with arg `{amend}`
called Signal.connect with args ({testobj.amend_commit},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Re&vert', {testobj}) {{}}
called PushButton.setToolTip with arg `{revert}`
called Signal.connect with args ({testobj.revert_selected},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Start &Tracking', {testobj}) {{}}
called PushButton.setToolTip with arg `{track}`
called Signal.connect with args ({testobj.add_new},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('&Stop Tracking', {testobj}) {{}}
called PushButton.setToolTip with arg `{untrack}`
called Signal.connect with args ({testobj.forget},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Add to &Ignore list', {testobj}) {{}}
called PushButton.setToolTip with arg `{ignore}`
called Signal.connect with args ({testobj.add_ignore},)
called VBox.addWidget with arg MockPushButton
called Label.__init__ with args ('', {testobj})
called VBox.addWidget with arg MockLabel
called VBox.addLayout with arg MockVBoxLayout
called VBox.addLayout with arg MockVBoxLayout
called VBox.__init__
called VBox.addStretch
called PushButton.__init__ with args ('C&ount LOCs', {testobj}) {{}}
called PushButton.setToolTip with arg `{count_all}`
called Signal.connect with args ({testobj.count_all},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Di&ff all Files', {testobj}) {{}}
called PushButton.setToolTip with arg `{diff_all}`
called Signal.connect with args ({testobj.diff_all},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Li&nt all Files', {testobj}) {{}}
called PushButton.setToolTip with arg `{lint_all}`
called Signal.connect with args ({testobj.lint_all},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('Commit &All changes', {testobj}) {{}}
called PushButton.setToolTip with arg `{commit_all}`
called Signal.connect with args ({testobj.commit_all},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('&Recheck repo', {testobj}) {{}}
called PushButton.setToolTip with arg `{recheck}`
called Signal.connect with args ({testobj.refresh_frame},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('View &History', {testobj}) {{}}
called PushButton.setToolTip with arg `{history}`
called Signal.connect with args ({testobj.view_repo},)
called VBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('&Quit', {testobj}) {{}}
called PushButton.setToolTip with arg `{quit}`
called Signal.connect with args ({testobj.close},)
called VBox.addWidget with arg MockPushButton
called VBox.addStretch
called VBox.addLayout with arg MockVBoxLayout
called widget.setLayout()
called Action.__init__ with args ('Done', {testobj})
called Signal.connect with args ({testobj.close},)
called Action.setShortcut with arg `Ctrl+Q`
called widget.addAction()
called Gui.refresh_frame()
"""
setup_app = """\
called Application.__init__
called QMainWindow.__init__()
called Gui.setup_visual()
called List.__init__
called ComboBox.__init__
"""
refresh = setup_app + """\
called Gui.get_repofiles()
called Gui.populate_frame()
called List.setFocus
"""
getrepofiles = setup_app + """\
called Gui.refresh_frame()
"""
populate = setup_app + """\
called Gui.get_repofiles()
called List.clear
called List.addItem with arg `file1.py`
called List.addItem with arg `file2.py`
called List.setCurrentRow with arg 0
called Gui.update_branches()
called List.setFocus
called List.clear
called List.addItem with arg `file1.py`
called List.addItem with arg `file2.py`
called List.setCurrentRow with arg 0
called Gui.update_branches()
"""

@pytest.fixture
def expected_output():
    """output expectations for check_repo gui functions
    """
    return {'checktextdialog': check_text,
            'diffviewdialog': diffview_start + diffview_middle + diffview_end,
            'diffviewdialog2': diffview_start + dv_copy1 + diffview_middle + dv_copy2 + diffview_end,
            'friendlyreminder': friendly_reminder,
            'maingui': main_gui,
            'refresh_frame': refresh,
            'get_repofiles': getrepofiles,
            'populate_frames': populate}
