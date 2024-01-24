"""unittests for ./jsonp.py
"""
import os
import jsonp

def test_main_error(capsys):
    """unittest for jsonp.main_error
    """
    usagemessage = "usage: python(3) jsonp.py <filename>\n"
    jsonp.main([])
    assert capsys.readouterr().out == usagemessage
    jsonp.main(['scriptname'])
    assert capsys.readouterr().out == usagemessage
    jsonp.main(['scriptname', 'filename', 'extra'])
    assert capsys.readouterr().out == usagemessage

def test_main(tmp_path):
    """unittest for jsonp.main
    """
    filename = str(tmp_path / 'test_jsonp.json')
    outname = str(tmp_path / 'test_jsonp_pretty.json')
    with open(filename, 'w') as f:
        f.write('["foo", {"bar": ["baz", null, 1.0, 2]}]')
    jsonp.main(['scriptname', filename])
    assert os.path.exists(outname)
    with open(outname) as f:
        data = f.read()
    assert data == ('[\n'
                    '  "foo",\n'
                    '  {\n'
                    '    "bar": [\n'
                    '      "baz",\n'
                    '      null,\n'
                    '      1.0,\n'
                    '      2\n'
                    '    ]\n'
                    '  }\n'
                    ']')
