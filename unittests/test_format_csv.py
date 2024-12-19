"""unittests for ./format_csv.py
"""
import format_csv as testee
NARROW = "x,y,z,001,  2,30.0\nx,yyyyy,'z z, z',1,20000,333\n x,yyy,zzz,1/1/1,  02,3\n"
WIDE_1 = ("x,y,z,001,  2,30.0          \n"
          "x,yyyyy,'z z, z',1,20000,333\n"
          " x,yyy,zzz,1/1/1,  02,3     \n")
WIDE_2 = ("x ,y    ,z   ,001  ,  2 ,30.0          \n"
          "x ,yyyyy,'z z, z'  ,1   ,20000         ,333\n"
          " x,yyy  ,zzz ,1/1/1,  02,3             \n")
WIDE_3 = ("x ,y    ,z       ,001  ,  2           ,30.0          \n"
        "x ,yyyyy,'z z, z  ',1    ,20000         ,333           \n"
        " x,yyy  ,zzz     ,1/1/1,  02          ,3             \n")


def test_expand(tmp_path):
    """unittest for format_csv.expand
    """
    filepath = tmp_path / 'test.csv'
    filepath.write_text(NARROW)
    filename = str(filepath)
    testee.expand(filename)
    assert filepath.read_text() == WIDE_1
    testee.expand(filename, sep=',')
    assert filepath.read_text() == WIDE_2
    filepath2 = tmp_path / 'test2.csv'
    filename2 = str(filepath2)
    testee.expand(filename, outfile=filename2, sep=',', quot="'")
    assert filepath2.read_text() == WIDE_3


def test_contract(tmp_path):
    """unittest for format_csv.contract
    """
    filepath = tmp_path / 'test.csv'
    filepath.write_text(WIDE_1)
    filename = str(filepath)
    testee.contract(filename)
    assert filepath.read_text() == NARROW
    filepath.write_text(WIDE_2)
    testee.contract(filename, sep=',')
    assert filepath.read_text() == NARROW
    filepath2 = tmp_path / 'test2.csv'
    filename2 = str(filepath2)
    filepath.write_text(WIDE_3)
    testee.contract(filename, outfile=filename2, sep=',', quot="'")
    assert filepath2.read_text() == NARROW
