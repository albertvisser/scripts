#! /usr/bin/env python
"""create testscript for a module

builds a test function for each function as well as for methods in each class
arguments: project name, script to test, nickname in .rurc
"""
import sys
import os
# import shutil
import configparser


def main(*args):
    "build unittests script"
    if len(args) != 3:
        return ('usage: [python] build_unittests.py <project-name> <module-to-test>'
                ' { <nickname-in-testconf> | { -r | --rebuild } }')
    if args[-1] in ('-r', '--rebuild'):
        Main(*args[:-1], rebuild=True)
    else:
        try:
            Main(*args)
        except ValueError as exc:
            return str(exc)
    return ''


class Main:
    "entry point"
    def __init__(self, project, testee, nickname='', rebuild=False):
        root = determine_project_root(project)
        testconfig = os.path.join(root, '.rurc')
        if os.path.exists(testconfig):
            conf = configparser.ConfigParser(allow_no_value=True)
            conf.read(testconfig)
            testdir = list(conf["testdir"])[0]
            if conf.has_option("testscripts", nickname):
                raise ValueError(f"nickname '{nickname}' already used for project '{project}'")
        else:
            conf = None
            testdir = 'unittests'
        testscriptname = self.create_testscript(root, testdir, testee, rebuild)
        if rebuild:
            print(f'{testscriptname} rebuilt')
            return
        # create_conf = update_conf = False
        if not conf:
            conf = configparser.ConfigParser(allow_no_value=True)
            conf.add_section('testdir')
            conf.set('testdir', testdir)  # conf['testdir'] = testdir
            conf.add_section('testscripts')
            conf.add_section('testees')
        conf['testscripts'][nickname] = os.path.basename(testscriptname)
        conf['testees'][nickname] = testee
        with open(testconfig, 'w') as _out:
            conf.write(_out)
        print(f'created file {testscriptname}')

    def create_testscript(self, root, testdir, name, rebuild):
        """Lees de testee, maak per functie / class / methode een test en schrijf de testmodule
        """
        where, what = os.path.split(name)
        # self.testee = what = what.removesuffix('.py')
        # testscript = os.path.join(root, testdir, f'test_{what}.py')
        testscript = os.path.join(root, testdir, f'test_{what}')
        self.testee = what.removesuffix('.py')
        self.oldscriptlines = {}
        if os.path.exists(testscript):
            if rebuild:
                self.oldscriptlines = build_oldversiondict(testscript)
            # shutil.copyfile(testscript, testscript + '~')
            os.rename(testscript, f'{testscript}~')
        with open(os.path.join(root, name)) as _in:
            data = _in.readlines()
        # standaardiseren modulenaam? Maar dit wordt verder niet gebruikt?
        # for seq, text in enumerate(('qt_gui', 'gui_qt', 'wx_gui', 'gui_wx', 'gtk_gui', 'gui_gtk')):
        #     if text == what:
        #         what = ('qtgui', 'qtgui', 'wxgui', 'wxgui', 'gtkgui', 'gtkgui')[seq]
        #         break
        fromwhere = f"from {where.replace('/', '.')} " if where else ''
        key = ('', '')
        if self.oldscriptlines.get(key, []):
            self.testscriptlines = self.oldscriptlines[key]
        else:
            self.testscriptlines = [f'"""unittests for ./{name}\n"""\n']
            self.testscriptlines.append(f"{fromwhere}import {self.testee} as testee\n")
        classname = ''
        self.new_class = False
        for line in data:
            if line.startswith('def '):
                self.process_function(line)
            elif line.startswith('class '):
                classname = self.process_class(line)
            elif line.startswith('    def '):
                self.process_method(classname, line)
        with open(testscript, 'w') as _out:
            _out.writelines(self.testscriptlines)
        return testscript

    def process_function(self, line):
        """what to do when we encounter a function definition
        """
        key = ('', line.split('(')[0])
        self.testscriptlines.append('\n\n')
        if self.oldscriptlines.get(key, []):
            self.add_oldlines(self.oldscriptlines[key])
        else:
            self.add_lines_for_function(line)

    def process_class(self, line):
        """what to do when we encounter a function definition
        """
        self.testscriptlines.append('\n\n')
        classname = get_classname(line)
        self.new_class = True
        key = (classname, '')
        if self.oldscriptlines.get(key, []):
            self.add_oldlines(self.oldscriptlines[key])
        else:
            self.add_lines_for_class(classname)
        return classname

    def process_method(self, classname, line):
        """what to do when we encounter a nethod definition
        """
        self.testscriptlines.append('\n')
        key = (classname, line.split('(')[0])
        if self.oldscriptlines.get(key, []):
            self.add_oldlines(self.oldscriptlines[key])
        else:
            self.add_lines_for_method(line, classname)

    def add_oldlines(self, lines):
        "insert lines from old testscript"
        self.testscriptlines.extend(lines)

    def add_lines_for_function(self, line):
        "write unittest for function"
        sig = line[4:].split('#', 1)[0].rstrip().removesuffix(':')
        function_name = sig.split('(', 1)[0]
        self.testscriptlines.extend([
            f'def _test_{function_name}(monkeypatch, capsys):\n',
            f'    """unittest for {self.testee}.{function_name}\n    """\n',
            f'    assert testee.{sig} == "expected_result"\n',
            '    assert capsys.readouterr().out == ("")\n'])

    def add_lines_for_class(self, classname):
        "write class header for unittests"
        self.testscriptlines.extend([
            f'class Test{classname}:\n',
            f'    """unittests for {self.testee}.{classname}\n    """\n',
            '    def setup_testobj(self, monkeypatch, capsys):\n',
            f'        """stub for {self.testee}.{classname} object\n\n',
            '        create the object skipping the normal initialization\n',
            '        intercept messages during creation\n',
            '        return the object so that other methods can be monkeypatched in the caller\n',
            '        """\n',
            '        def mock_init(self, *args):\n            "stub"\n',
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
            f"    def _test_{testmeth_name}(self, monkeypatch, capsys):\n",
            f'        """unittest for {classname}.{method_name}\n        """\n'
            f'        testobj = {testobj}\n',])
        if method_name != '__init__':
            self.testscriptlines.append(f'        assert testobj.{sig} == "expected_result"\n')
        self.testscriptlines.append('        assert capsys.readouterr().out == ("")\n')


def determine_project_root(project):
    "return the location where the project lives"
    if project in ('bin', 'scripts'):
        root = '~/bin'
    elif project in ('nginx-config', 'server-stuff'):
        root = '~/nginx-config'
    else:
        root = '~/projects/' + project
    root = os.path.expanduser(root)
    return root


def build_oldversiondict(testscript):
    """turn the original script into a dict so that it can be easily searched with dict.get()
    """
    result = {}
    with open(testscript) as oldfile:
        classname, funname = '', ''
        result[(classname, funname)] = []
        for line in oldfile:
            if line.startswith('def test'):
                classname, funname = '', line.replace('test_', '').split('(')[0]
                result[(classname, funname)] = [line]
            elif line.startswith('def _test'):
                classname, funname = '', line.replace('_test_', '').split('(')[0]
                result[(classname, funname)] = [line]
            elif line.startswith('def'):
                classname, funname = '', ''
                result[(classname, funname)].append(line)
            elif line.startswith('class Test'):
                classname, funname = get_classname(line).replace('Test', ''), ''
                result[(classname, funname)] = [line]
            elif line.startswith('class _Test'):
                classname, funname = get_classname(line).replace('_Test', ''), ''
                result[(classname, funname)] = [line]
            elif line.startswith('class'):
                classname, funname = '', ''
                result[(classname, funname)].append(line)
            elif line.startswith('    def test'):
                # breakpoint()
                funname = line.replace('test_', '').split('(')[0]
                if funname == '    def init':
                    funname = '    def __init__'
                result[(classname, funname)] = [line]
            elif line.startswith('    def _test'):
                # breakpoint()
                funname = line.replace('_test_', '').split('(')[0]
                if funname == '    def init':
                    funname = '    def __init__'
                result[(classname, funname)] = [line]
            elif line.startswith('    def'):
                # classname, funname == '', ''
                funname = ''
                result[(classname, funname)].append(line)
            else:
                result[(classname, funname)].append(line)
    for key, value in result.items():
        while not value[-1].strip():
            value = value[:-1]
        result[key] = value
    return result


def get_classname(line):
    "extract the class name from the line and return it"
    classname = line[6:].rstrip().removesuffix(':')
    classname = classname.split('(', 1)[0]
    return classname


if __name__ == '__main__':
    print(main(sys.argv[1:]))
