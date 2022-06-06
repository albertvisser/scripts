import os.path
import pytest
import xmlp

def test_main_wrng_args(capsys):
    """main krijgt sys.argv binnen, dat is een list van namen die altijd begint met de naam
    van het script zelfi. Andere gegevenstypen testen is dus niet zo nuttig
    """
    xmlp.main(['xmlp.py'])
    assert capsys.readouterr().out == 'usage: python(3) xmlp.py <filename>\n'
    xmlp.main(['xmlp.py', '<filename>', 'another_arg'])
    assert capsys.readouterr().out == 'usage: python(3) xmlp.py <filename>\n'


def test_main(capsys):
    ""
    fname = '/tmp/test_xmlp.xml'
    target = '/tmp/test_xmlp_pretty.xml'
    os.remove(target)
    with open(fname, 'w') as f:
        print('<root><level1><level2>some_text</level2>'
              '<level2_too><level3 attr="x"/></level2_too></level1></root>', file=f)
    xmlp.main(['xmlp.py', fname])
    assert os.path.exists(target)
    with open(target) as o:
        data = o.read()
    assert data == ('<root>\n'
                    '  <level1>\n'
                    '    <level2>some_text</level2>\n'
                    '    <level2_too>\n'
                    '      <level3 attr="x"/>\n'
                    '    </level2_too>\n'
                    '  </level1>\n'
                    '</root>\n')
