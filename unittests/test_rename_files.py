import os
import pytest
import rename_files

def test_main(monkeypatch, capsys, tmp_path):
    """testen op een leeg of niet bestaand file is niet nodig, kan per definitie niet
    """
    def mock_rename(*args):
        print('called path.rename() with args', [str(x) for x in args])
    tempfile = tmp_path / 'test_rename_files'
    with open(tempfile, 'w') as f:
        f.write('dir/naam_zonder_spatie\nlong/dir/naam_met 1_spatie\nnaam met 2_spaties')
    monkeypatch.setattr(rename_files.pathlib.Path, 'rename', mock_rename)
    rename_files.main(tempfile)
    assert capsys.readouterr().out == (
            "called path.rename() with args ['long/dir/naam_met 1_spatie',"
            " 'long/dir/1_spatie, naam_met']\n"
            "called path.rename() with args ['naam met 2_spaties', '2_spaties, naam met']\n")

