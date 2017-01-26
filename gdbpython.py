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
        gdb.execute('s', False, True)
        res = gdb.execute('f', False, True)
        output.write(res)
        lines = res.split('\n')
        parts = lines[0].split('/')

        if len(parts) < 2 and in_skip:
            continue

        if len(parts) == 0:
            print('ERROR A----')
        if len(parts[0]) == 0:
            print('ERROR B----')
        if parts[0][-1] == '.':
            break

        path = '/' + '/'.join(parts[1:])
        if path.find('/c++/') != -1:
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

class StdLibFrameSkipperIterator():

    def __init__(self, ii):
        self.input_iterator = ii
        self.already_skipped = False

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            frame = next(self.input_iterator)
            if frame is None:
                return None

            if frame.filename().find('c++') == -1:
                #print('Keep: ', frame.filename())
                return frame
            if not self.already_skipped:
                self.already_skipped = True
                print('**Filter', self.__class__.__name__,
                      'is filtering c++ files**')
            #print('Skip: ', frame.filename())

class FrameFilter():
    def __init__(self):
        print('Init mich frame filter')
        self.name = "Mich frame filter"
        self.priority = 100
        self.enabled = True
        gdb.frame_filters[self.name] = self

    def filter(self, frame_iter):
        return StdLibFrameSkipperIterator(frame_iter)

FrameFilter()
