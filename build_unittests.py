#! /usr/bin/env python
"""create testscript for a module

builds a test function for each function as well as for methods in each class
arguments: project name, script to test, nickname in .rurc
"""
import sys
import os
import shutil
import configparser

class Main:
    "entry point"
    def __init__(self, project, testee, nickname='', rebuild=False):
        if project in ('bin', 'scripts'):
            root = '~/bin'
        elif project in ('nginx-config', 'server-stuff'):
            root = '~/nginx-config'
        else:
            root = '~/projects/' + project
        root = os.path.expanduser(root)
        testconfig = os.path.join(root, '.rurc')
        if os.path.exists(testconfig):
            conf = configparser.ConfigParser(allow_no_value=True)
            conf.read(testconfig)
            testdir = list(conf["testdir"])[0]
        else:
            conf = None
            testdir = 'unittests'
        testscriptname = self.create_testscript(root, project, testdir, testee)
        if rebuild:
            print(f'`{testscriptname}` in {root}/{testdir} rebuilt')
            return
        create_conf = update_conf = False
        if not conf:
            create_conf = True
            conf = configparser.ConfigParser(allow_no_value=True)
            conf.add_section('testdir')
            conf.set('testdir', testdir)  # conf['testdir'] = testdir
            conf.add_section('testscripts')
            conf.add_section('testees')
        if not nickname in conf['testscripts']:
            update_conf = True
            conf['testscripts'][nickname] = testscriptname
            conf['testees'][nickname] = testee
        if create_conf or update_conf:
            with open(testconfig, 'w') as _out:
                conf.write(_out)
        print(f'created file `{testscriptname}` in {root}/{testdir}')

    def create_testscript(self, root, project, testdir, name):
        """Lees de testee, maak per functie / class / methode een test en schrijf de testmodule
        """
        self.testscriptlines = [f'"""unittests for ./{name}\n"""\n']
        with open(os.path.join(root, name)) as _in:
            data = _in.readlines()
        where, what = os.path.split(name)
        self.testee = what = what.removesuffix('.py')
        for seq, text in enumerate(('qt_gui', 'gui_qt', 'wx_gui', 'gui_wx', 'gtk_gui', 'gui_gtk')):
            if text == what:
                what = ('qtgui', 'qtgui', 'wxgui', 'wxgui', 'gtkgui', 'gtkgui')[seq]
                break
        fromwhere = f"from {where.replace('/', '.')} "  if where else ''
        self.testscriptlines.append(f"{fromwhere}import {self.testee} as testee\n")
        classname = ''
        self.new_class = False
        for line in data:
            if line.startswith('def '):
                self.add_lines_for_function(line)
            elif line.startswith('class '):
                classname = self.add_lines_for_class(line)
            elif line.startswith('    def '):
                self.add_lines_for_method(line, classname)
        testscript = f'test_{what}.py'
        if os.path.exists(testscript):
            shutil.copyfile(testscript, testscript + '~')
        with open(os.path.join(root, testdir, testscript), 'w') as _out:
            _out.writelines(self.testscriptlines)
        return testscript

    def add_lines_for_function(self, line):
        "write unittest for function"
        sig = line[4:].split('#', 1)[0].rstrip().removesuffix(':')
        function_name = sig.split('(', 1)[0]
        self.testscriptlines.extend([
            f'\n\ndef _test_{function_name}(monkeypatch, capsys):\n',
            f'    """unittest for {self.testee}.{function_name}\n    """\n',
            f'    assert testee.{sig} == "expected_result"\n',
            '    assert capsys.readouterr().out == ("")\n'])

    def add_lines_for_class(self, line):
        "write class header for unittests"
        self.new_class = True
        classname = line[6:].rstrip().removesuffix(':')
        classname = classname.split('(', 1)[0]
        self.testscriptlines.extend([
            f'\n\nclass Test{classname}:\n',
            f'    """unittests for {self.testee}.{classname}\n    """\n',
            f'    def setup_testobj(self, monkeypatch, capsys):\n',
            f'        """stub for {self.testee}.{classname} object\n\n',
            '        create the object skipping the normal initialization\n',
            '        intercept messages during creation\n',
            '        return the object so that other methods can be monkeypatched in the caller\n',
            '        """\n',
            '        def mock_init(self, *args):\n            """stub\n            """\n',
            f"            print('called {classname}.__init__ with args', args)\n",
            f"        monkeypatch.setattr(testee.{classname}, '__init__', mock_init)\n",
            f'        testobj = testee.{classname}()\n',
            f"        assert capsys.readouterr().out == 'called {classname}.__init__"
            " with args ()\\n'\n",
            '        return testobj\n'])
        return classname

    def add_lines_for_method(self, line, classname):
        "write unittest for method"
        sig = line[8:].split('#', 1)[0].rstrip().removesuffix(':')
        sig = sig.replace('self, ', '').replace('self', '')
        method_name, args = sig.split('(', 1)
        if self.new_class:
            self.new_class = False
        # else:
        #     self.testscriptlines.append('\n')
        if method_name == '__init__':
            testobj = f'testee.{classname}({args}'
            testmeth_name = 'init'
        else:
            testobj = 'self.setup_testobj(monkeypatch, capsys)'
            testmeth_name = method_name
        self.testscriptlines.extend([
            f"\n    def _test_{testmeth_name}(self, monkeypatch, capsys):\n",
            f'        """unittest for {classname}.{method_name}\n        """\n'
            f'        testobj = {testobj}\n',])
        if method_name != '__init__':
            self.testscriptlines.append(f'        assert testobj.{sig} == "expected_result"\n')
        self.testscriptlines.append('        assert capsys.readouterr().out == ("")\n')

if __name__ == '__main__':
    if not len(sys.argv) == 4:
        sys.exit('usage: [python] build_unittests.py <project-name> <module-to-test>'
                 ' { <nickname-in-testconf> | { -r | --rebuild } }')
    if sys.argv[-1] in ('-r', '--rebuild'):
        Main(*sys.argv[1:-1], rebuild=True)
    else:
        Main(*sys.argv[1:])
