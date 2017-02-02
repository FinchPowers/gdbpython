#
# gdbpython.py
# Mich, July 216
# Copyright 2016
#

import gdb
import sys
from io import StringIO

def s(print_stdlib_steps=True, output=sys.stdout):
    """
    Keeps stepping as long as the context is within /usr/include/c++.
    """
    in_skip = False
    while True:
        gdb.execute('s', False, True)
        res = gdb.execute('f', False, True)
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
            if print_stdlib_steps:
                if res == '':
                    raise Exception('Empty line a')
                output.write(res)
            in_skip = True
            continue

        break

    output.write(res)

class StepLineGetter(object):
    string = StringIO()

    @staticmethod
    def get_step_line():
        StepLineGetter.string.truncate(0)
        s(False, StepLineGetter.string)
        StepLineGetter.string.seek(0)
        line = StepLineGetter.string.readline()
        if line == '':
            raise Exception('Empty ??')
        return StepLineGetter.string.readline().split(' ')[-1]



# TODO handle end of prog
def trace_write(filename, steps):
    """
    Steps n steps, printing every output not from .../c++/... to the
    filename provided.
    """
    with open(filename, 'wt') as output:
        try:
            for _ in range(steps):
                step_line = StepLineGetter.get_step_line()
                if step_line == '':
                    raise RuntimeError('Empty step line')
                output.write(step_line)
        except gdb.error as e:
            print(e.args)


def trace_compare(filename):
    """
    Opens file filename, and steps as long as the steps are the same as in the
    file or when the end of the file is reached.
    """
    with open(filename, 'rt') as in_file:

        try:
            line_num = 0
            for file_line in in_file:
                line_num += 1
                step_line = StepLineGetter.get_step_line()
                if step_line != file_line:
                    print("Mismatch at file line {}.".format(line_num))
                    print("File step   : " + file_line)
                    print("Current step: " + step_line)
                    break
            else:
                print("No mismatch found, done iterating through file.")

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
