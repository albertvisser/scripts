"""unittests for entry point of ./bin/sort_file.py

dit is een test van de verschillende manieren om dit script aan te roepen, het heeft geen zin om hier
naar de coverage te kijken omdat er een leeg invoerbestand gebruikt wordt
misschien is het voldoende om de door argparse gegenereerde helptekst te checken?
"""
import subprocess

def test_sort_file_help():
    """show help / usage info
    """
    result = subprocess.run(['python', 'sort_file.py', '--help'], capture_output=True)
    assert result.returncode == 0
    assert result.stdout.decode() == ("usage: sort_file.py [-h] [-c COLUMN] [-o OUTPUT] file\n\n"
                                      "Simple file sorting program\n\n"
                                      "positional arguments:\n"
                                      "  file                  Name of file to sort\n\n"
                                      "options:\n"
                                      "  -h, --help            show this help message and exit\n"
                                      "  -c COLUMN, --column COLUMN\n"
                                      "                        Column from which to start sorting\n"
                                      "  -o OUTPUT, --output OUTPUT\n"
                                      "                        output filename (default is adding"
                                      " '-sorted' to the input filename\n")
    assert result.stderr.decode() == ''


def test_sort_file_noargs():
    """calling with no arguments at all
    """
    result = subprocess.run(['python', 'sort_file.py'], capture_output=True)
    assert result.returncode == 2
    assert result.stdout.decode() == ''
    assert result.stderr.decode() == ("usage: sort_file.py [-h] [-c COLUMN] [-o OUTPUT] file\n"
                                      'sort_file.py: error: the following arguments are required:'
                                      ' file\n')


def test_sort_file_name(tmp_path):
    """just an input filename
    """
    fname = tmp_path / 'sort_file_test'
    sortedf = tmp_path / 'sort_file_test_sorted'
    fname.touch()
    result = subprocess.run(['python', 'sort_file.py', str(fname)], capture_output=True)
    assert result.returncode == 0
    assert result.stdout.decode() == f'klaar, output in {sortedf}\n'
    assert result.stderr.decode() == ''
    fname.unlink()
    sortedf.unlink()


def test_sort_file_name_out(tmp_path):
    """(input file name and) output filename (-o option)
    """
    fname = tmp_path / 'sort_file_test'
    fname.touch()
    fn_out = tmp_path / 'sort_file_test_out'
    result = subprocess.run(['python', 'sort_file.py', '-o', str(fn_out), str(fname)],
                            capture_output=True)
    assert result.returncode == 0
    assert result.stdout.decode() == f'klaar, output in {fn_out}\n'
    assert result.stderr.decode() == ''
    fname.unlink()
    fn_out.unlink()


def test_sort_file_name_no_out(tmp_path):
    """(input filename and) -o option without filename
    """
    fname = tmp_path / 'sort_file_test'
    fname.touch()
    result = subprocess.run(['python', 'sort_file.py', str(fname), '-o'], capture_output=True)
    assert result.returncode == 2
    assert result.stdout.decode() == ''
    assert result.stderr.decode() == ('usage: sort_file.py [-h] [-c COLUMN] [-o OUTPUT] file\n'
                                      'sort_file.py: error: argument -o/--output:'
                                      ' expected one argument\n')
    fname.unlink()


def test_sort_file_name_col(tmp_path):
    """(input filename and) column to start sorting on (-c option)
    """
    fname = tmp_path / 'sort_file_test'
    fname.touch()
    sortedf = tmp_path / 'sort_file_test_sorted'
    result = subprocess.run(['python', 'sort_file.py', fname, '-c', '15'], capture_output=True)
    assert result.returncode == 0
    assert result.stdout.decode() == f'klaar, output in {sortedf}\n'
    assert result.stderr.decode() == ''
    fname.unlink()
    sortedf.unlink()


def test_sort_file_name_no_col(tmp_path):
    """(input filename and) -c option without column number
    """
    fname = tmp_path / 'sort_file_test'
    fname.touch()
    result = subprocess.run(['python', 'sort_file.py', fname, '-c'], capture_output=True)
    assert result.returncode == 2
    assert result.stdout.decode() == ''
    assert result.stderr.decode() == ('usage: sort_file.py [-h] [-c COLUMN] [-o OUTPUT] file\n'
                                      'sort_file.py: error: argument -c/--column:'
                                      ' expected one argument\n')
    fname.unlink()
