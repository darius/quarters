#!/usr/bin/env python
"""
Like sketchbook's meta.py, but taking an object file instead of an asm file.
"""

import itertools, re, sys

import obj_format as tags
from obj_format import read_int, read_string
import opdefs

def main(argv):
    trace = False
    if argv[1:2] == ['-trace']:
        trace = True
        del argv[1]
    assert 2 <= len(argv), "usage: %s [-trace] object-file [input-file...]" % argv[0]

    vm = Meta_VM(trace)
    with open(argv[1], 'rb') as f:
        vm.load(f)
    input_text = ''
    if argv[2:]:
        for filename in argv[2:]:
            with open(filename) as f:
                input_text += f.read()
    else:
        input_text += sys.stdin.read()

    sys.stdout.write(vm.run(input_text))
    sys.stdout.flush()
    if vm.poisoned:
        vm.inspect()
    return vm.poisoned

class Meta_VM(object):
    def __init__(self, trace=False):
        self.code = []
        self.labels = []     # n -> name of the nth label
        self.addrs = []      # n -> code address pointed to by the nth label
        self.strings = []
        self.trace = trace

    def load(self, infile):
        while True:
            b = infile.read(1)
            if not b: break
            tag = ord(b)
            if tag == tags.label:
                s = read_string(infile)
                self.labels.append(s)
                self.addrs.append(len(self.code))
            elif tag == tags.string:
                s = read_string(infile)
                self.strings.append(s)
            elif tag == tags.op0:
                opcode = read_int(infile)
                self.code.append(opcode)
            elif tag == tags.op1 or tag == tags.ref:
                opcode = read_int(infile)
                arg = read_int(infile)
                self.code.append(opcode)
                self.code.append(arg)
            else:
                raise Exception("Bad object file")

    def run(self, input_text):
        # Appropriate terminology for a hylomorphism:
        self.feed = input_text
        self.bite = None
        self.poop = ''
        self.win = False
        self.stack = []
        self.calls = [-1, 'start']
        self.gensym = itertools.count().next
        self.poisoned = False
        self.pc = 0
        self.running()
        return self.poop

    def running(self):
        while not self.poisoned and 0 <= self.pc:
            cur_pc = self.pc
            opdefs.step(self)
            if self.trace:
                self.print_instruction(cur_pc, '  ' + self.state_gist())

    def match(self, regex):
        self.feed = self.feed.lstrip()
        m = re.match(regex, self.feed)
        self.win = m is not None
        if m:
            self.bite, self.feed = self.feed[:m.end()], self.feed[m.end():]

    def write(self, string):
        self.poop += string
        self.win = True

    # Debugging/introspection.

    def inspect(self):
        print >>sys.stderr, 'stack:', self.stack
        print >>sys.stderr, 'calls:', ' '.join(self.calls[1::2])
        print >>sys.stderr, 'feed:', repr(self.feed[:40])
        self.list(self.pc-2, self.pc+1)

    def list(self, lo=0, hi=None):
        limit = hi or len(self.code)
        addr = lo
        while addr < limit:
            addr += self.print_instruction(addr)

    def print_instruction(self, addr, suffix=''):
        labels = ' '.join(self.labels[k]
                          for k, v in enumerate(self.addrs) if v == addr)
        if labels:
            print >>sys.stderr, labels + ':'
        op = self.code[addr]
        opname, param = opdefs.ops[op]
        if param is None:
            args = []
        else:
            arg = self.code[addr+1]
            if param == 'string':
                arg = self.strings[arg]
            elif param == 'addr':
                arg = self.labels[arg]
            else:
                arg = '%d' % arg
            args = [arg]
        print >>sys.stderr, ('     %3d %-18s%s'
                             % (addr,
                                opname + ' ' + ''.join(args),
                                suffix))
        return 1 + len(args)

    def state_gist(self):
        calls = ' '.join(self.calls[3::2])
        # TODO show the stack too -- how to format?
        return '%s %-10r %s' % ('-+'[self.win], self.feed[:8], calls)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
