"""unittests for ./xmlp.py
"""
import xmlp

def test_main_wrng_args(capsys):
    """unittest for xmlp.main_wrng_args

    main krijgt sys.argv binnen, dat is een list van namen die altijd begint met de naam
    van het script zelfi. Andere gegevenstypen testen is dus niet zo nuttig
    """
    xmlp.main(['xmlp.py'])
    assert capsys.readouterr().out == 'usage: python(3) xmlp.py <filename>\n'
    xmlp.main(['xmlp.py', '<filename>', 'another_arg'])
    assert capsys.readouterr().out == 'usage: python(3) xmlp.py <filename>\n'


def test_main(tmp_path):
    """unittest for xmlp.main
    """
    fname = tmp_path / 'test_xmlp.xml'
    target = tmp_path / 'test_xmlp_pretty.xml'
    with fname.open('w') as f:
        print('<root><level1><level2>some_text</level2>'
              '<level2_too><level3 attr="x"/></level2_too></level1></root>', file=f)
    xmlp.main(['xmlp.py', str(fname)])
    assert target.exists()
    assert target.read_text() == ('<root>\n'
                                  '  <level1>\n'
                                  '    <level2>some_text</level2>\n'
                                  '    <level2_too>\n'
                                  '      <level3 attr="x"/>\n'
                                  '    </level2_too>\n'
                                  '  </level1>\n'
                                  '</root>\n')
