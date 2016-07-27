#
# gdbpython.py
# Mich, July 216
# Copyright 2016
#

import gdb
import sys

def s(output=sys.stdout):
    """
    Keeps stepping as long as the context is within /usr/include/c++.
    """
    in_skip = False
    while True:
        res = gdb.execute('s', True, True)
        output.write(res)
        lines = res.split('\n')
        parts = lines[0].split('/')

        if len(parts) < 2 and in_skip:
            continue

        if parts[0][-1] == '.':
            break

        path = '/' + '/'.join(parts[1:])
        if path.find('/usr/include/c++') == 0:
            in_skip = True
            continue
        break

def trace(filename):
    """
    Steps forever, printing every output not from /usr/include/c++ to the
    filename provided.
    """
    with open(filename, 'wt') as output:
        try:
            while True:
                s(output)
        except gdb.error as e:
            print(e.args)
