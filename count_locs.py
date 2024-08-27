import sys
import pathlib
import importlib
import contextlib
import inspect
import invoke
import tkinter.simpledialog as sd
import tkinter.filedialog as fd
import tkinter.messagebox as mb
usage = """\
display line count in the form of lines per method / function, not counting
  docstrings but including comments between statements

usage: python count_locs.py [module-filename] [ options ]
options: -n --name      show count by name (default)
         -l --lineno    show count by linenumber

note: this program is meant to be started in the directory
the module is imported into
"""
HEADING = "Lines of code per function / method for `{}`"
DETAIL = '{}: {} lines ({})'

def main():
    """entry point when called as a module
    """
    fname = sys.argv[1] if len(sys.argv) > 1 else ''
    display_type = sys.argv[2] if len(sys.argv) > 2 else ''
    if display_type in ('-n', '--name'):
        display_type = 'by-name'
    elif display_type in ('-l', '--lineno'):
        display_type = 'by-line'
    else:
        display_type = 'by-name'
    if not fname or fname in ('-h', '--help'):
        print(usage)
        return
    path = pathlib.Path.cwd()
    fname = pathlib.Path(fname)
    lines = get_locs_for_module(fname, path)
    if display_type == 'by-line':
        lines = sort_locs_by_lineno(lines)
    for line in lines:
        print(line)


def ask_input_via_gui():
    """Ask for name of file to process
    """
    fname = fd.askopenfilename()
    # print(fname)
    proj = sd.askstring('Zoekend naar een import pad', "Geef projectnaam op of gebruik huidige",)
    if proj in ('bin', 'scripts'):
        path = '~/bin'
    elif proj in ('nginx-config', 'server-stuff'):
        path = '~/nginx-config'
    elif proj:
        path = f'~/projects/{proj}'
    else:
        path = pathlib.Path.cwd()
    path = pathlib.Path(path).expanduser()
    if not path.exists():
        mb.showerror(message=f'{proj} is geen geldig project')
        path = ''
    name = pathlib.Path(fname).relative_to(path)
    return path, name


def get_locs_for_module(name, path):
    "Turn filename into modulename and count locs"
    result = [HEADING.format(name)]
    name = str(name.with_suffix('')).replace('/', '.')
    for x, y, z in get_locs(name, path):
        if y:
            where = f'{z}' if y == 1 else f'{z}-{z + y - 1}'
            result.append(DETAIL.format(x, y, where))
        else:
            result.append(x)
    return result


def get_locs(module, path):
    "get lines of code per function / method"
    sys.path.append(str(path))
    lineslist = []
    moduleobj = importlib.import_module(module)
    for name, subobj in inspect.getmembers(moduleobj):
        # in dit geval retourneert de decorator van de functie een object:
        if isinstance(subobj, invoke.tasks.Task):
            lines, start, text = get_locs_for_unit(name, subobj)
            docstr = subobj.__doc__
            if docstr:
                doclen = len(docstr.split('\n'))
                start += doclen
                lines -= doclen
            lineslist.append((text or f'{name} (invoke task)', lines, start + 1))
        if inspect.isclass(subobj):
            if subobj.__module__ != module:
                continue
            classname = name
            for name2, subsubobj in inspect.getmembers(subobj):
                if inspect.isfunction(subsubobj) or inspect.ismethod(subsubobj):
                    if subsubobj.__module__ != module:
                        print(f'{name2} is not defined in this module')
                        continue
                    if not subsubobj.__qualname__.startswith(classname):
                        print(f'{name2} is not defined in this class')
                        continue
                    lines, start, text = get_locs_for_unit(name, subsubobj)
                    if not text:
                        docstr = subsubobj.__doc__
                        if docstr:
                            doclen = len(docstr.split('\n'))
                            start += doclen
                            lines -= doclen
                    lineslist.append((text or f'{classname}.{name2}', lines, start))
        elif inspect.isfunction(subobj):
            if subobj.__module__ != module:
                continue
            functionname = name
            lines, start, text = get_locs_for_unit(name, subobj)
            if not text:
                docstr = subobj.__doc__
                if docstr:
                    doclen = len(docstr.split('\n'))
                    start += doclen
                    lines -= doclen
            lineslist.append((text or functionname, lines, start))
    sys.path.pop()
    return lineslist


def get_locs_for_unit(name, unit):
    "get the actual number of lines"
    try:
        lines = inspect.getsourcelines(unit)
    except TypeError:
        return 0, 0, f'wrong type for getsourcelines - skipped: {name} {unit}'
    except OSError as e:
        return 0, 0, f'{e} for {name} {unit}'
    # with open('/tmp/test_get_locs', 'a') as f:
    #     # print(lines[0], file=f)  # lineslist.extend(code)
    #     for ix, line in enumerate(lines[0]):
    #         f.write(f'{lines[1] + ix:4} {line}')
    count = len(lines[0]) - 1  # exclude declaration
    start = lines[1] + 1       # exclude declaration
    return count, start, ''


def sort_locs_by_lineno(data):
    "trasformeert de output van aantal-regels-per-routine naar in-regelnummer-volgorde"
    def firstlinenum(x):
        if '-' in x[0]:
            return int(x[0].split('-')[0])
        return int(x[0])
    locsdict = {}
    for line in data:
        line = line.strip()
        if line.startswith(HEADING[:12]):
            filename = line.split('`')[1]
            locsdict[filename] = []
            # print(locsdict)
        elif line and ': ' in line:
            name, rest = line.split(': ', 1)
            count, linenums = rest.split(' lines ')
            locsdict[filename].append((linenums[1:-1], name, count))
    outlist = []
    for name, data in locsdict.items():
        if not data:
            continue
        if outlist:
            outlist.append('====')
        outlist.append(f'module: `{name}`')
        # outlist.extend([f'{x:4}-{y:4} {z} ({a})' for x, y, z, a in sorted(locsdict[name])])
        outlist.extend([f'{f"{x}":9} {y} ({z})' for x, y, z in sorted(data, key=firstlinenum)])
    return outlist

if __name__ == '__main__':
    main()
