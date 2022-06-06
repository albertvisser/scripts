import os
import pytest
import jsonp

def test_main_error(monkeypatch, capsys):
    usagemessage = "usage: python(3) jsonp.py <filename>\n"
    jsonp.main([])
    assert capsys.readouterr().out == usagemessage
    jsonp.main(['scriptname'])
    assert capsys.readouterr().out == usagemessage
    jsonp.main(['scriptname', 'filename', 'extra'])
    assert capsys.readouterr().out == usagemessage

def test_main(monkeypatch, capsys):
    filename = '/tmp/test_jsonp.json'
    outname = '/tmp/test_jsonp_pretty.json'
    if os.path.exists(outname):
        os.remove(outname)
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
    os.remove(filename)
    os.remove(outname)
