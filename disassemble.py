"""
Object file to assembly
"""

import sys

import obj_format as tags
from obj_format import read_int, read_string
from opdefs import ops, opcodes

def main(infile):
    labels = []
    constants = []
    code = []
    while True:
        b = infile.read(1)
        if not b: break
        tag = ord(b)
        if tag == tags.label:
            s = read_string(infile)
            labels.append(s)
            code.append((tag, s))
        elif tag == tags.string:
            s = read_string(infile)
            constants.append(s)
        elif tag == tags.ref:
            opcode = read_int(infile)
            labelno = read_int(infile)
            code.append((tag, opcode, labelno))
        elif tag == tags.op0:
            opcode = read_int(infile)
            code.append((tag, opcode))
        elif tag == tags.op1:
            opcode = read_int(infile)
            arg = read_int(infile)
            code.append((tag, opcode, arg))
        else:
            raise Exception("Bad object file")
    for chunk in code:
        tag = chunk[0]
        if tag == tags.label:
            _, label = chunk
            print label
        elif tag == tags.ref:
            _, opcode, labelno = chunk
            name, param = ops[opcode]
            print '  ', name, labels[labelno]
        elif tag == tags.op0:
            _, opcode = chunk
            name, param = ops[opcode]
            print '  ', name
        elif tag == tags.op1:
            _, opcode, arg = chunk
            name, param = ops[opcode]
            if param == 'string':
                print '  ', name, '%r' % constants[arg]
            else:
                print '  ', name, arg
        else:
            assert False


if __name__ == '__main__':
    main(sys.stdin)
