"""tooltips for check_repo collected in a separate file so that the can be edited independent of the
main program
"""
tooltips = {'branch': 'enter or select a branch name',
            'create': 'enter a name in the combo box and hit button to create',
            'switch': 'choose a name in the combo box and hit button to switch',
            'stash': 'hit button and select action',
            'merge': 'choose a name in the combo box and hit button to merge the chosen branch'
                     " into the current one (the one you're on)",
            'delete': 'choose a name in the combo box and hit button to delete',
            'docs': "open the current project's projdocs.trd",
            'show': 'select between showing files reported by `git status` or all tracked files',
            'select': 'note that these options block the gui until you finish them',
            'edit': 'open with vim',
            'diff': 'start meld to show differences with the repo version (only tracked files;\n'
                    'closing meld will automatically start the comparison for the next file)',
            'lint': 'start linter gui with selected Python file(s) (only if tracked)',
            'blame': 'show where changes were introduced (only tracked files)',
            'commit': 'git (add and) commit the selected file(s) (only tracked ones)',
            'amend': 'add changes to the last commit and/or modify commit message',
            'revert': 'remove changes from file(s) (only tracked ones)',
            'track': 'add file(s)',
            'untrack': 'remove files (not physically)',
            'ignore': 'make selected file(s) not show up on this screen anymore',
            'diff_all': 'start meld to show differences with the repo version (all tracked files;\n'
                        'closing meld will automatically start the comparison for the next file)',
            'lint_all': 'start linter gui with all the (Python) files in the repository',
            'commit_all': 'git (add and) commit all the tracked file(s) the have been changed',
            'recheck': 'refresh list on main screen',
            'history': 'open commit history browser',
            'quit': 'exit the app'}
