"""
Simple session management for Vivaldi
"""
import os
import shutil

SESSION_HOME = '/home/albert/projects/bookmarks_reorganiseren'
VIVALDI_HOME = '/home/albert/.config/vivaldi-snapshot/Default'
def save(session):
    """
    input: name for the session
    saves current_session and current_tabs to a directory with this name

    note that this saves *all* the tabs in the session, not just one window
    """
    session_dir = os.path.join(SESSION_HOME, session)
    try:
        os.mkdir(session_dir)
    except OSError: # FileExistsError: - remember? no python3 support yet
        print('Aborted - session name already in use')
        return
    for fname in ('Current Session', 'Current Tabs'):
        from_ = os.path.join(VIVALDI_HOME, fname)
        to = os.path.join(session_dir, fname)
        shutil.copyfile(from_, to)

def load(session):
    """
    input: name for the session
    loads current_session and current_tabs from the directory with this name

    note that this is best done before V. is started
    and that it overwrites anything that was previously present
    """
    session_dir = os.path.join(SESSION_HOME, session)
    if not os.path.exists(session_dir):
        print('Aborted - session name unknown')
        return
    for fname in ('Current Session', 'Current Tabs'):
        from_ = os.path.join(session_dir, fname)
        to = os.path.join(VIVALDI_HOME, fname)
        shutil.copyfile(from_, to)

