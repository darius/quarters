"""
Assembly to object file
"""

import sys

import obj_format as tags
from obj_format import encode_int, encode_string
from opdefs import ops, opcodes

def main(f, out):
    code = []
    labels = []
    label_nums = {}
    nstrings = 0
    for line in f:
        line = line.rstrip()
        if not line:
            pass
        elif line[0].isspace():
            parts = line.split(None, 1)
            if len(parts) == 1:
                opname, arg = parts[0], None
            elif len(parts) == 2:
                opname, arg = parts
            else:
                assert False
            assert opname in opcodes, "Bad op: %r" % opname
            opcode = opcodes[opname]
            _, param = ops[opcode]
            assert (param is None) == (arg is None)
            if param is None:
                code.append((tags.op0, opcode))
            elif param == 'addr':
                label = arg
                code.append((tags.ref, opcode, label))
            elif param == 'string':
                code.append((tags.string, decode_literal(arg)))
                code.append((tags.op1, opcode, nstrings))
                nstrings += 1
            else:
                code.append((tags.op1, opcode, arg))
        else:
            assert len(line.split()) == 1
            label = line
            assert label not in labels, "Duplicate label: " + label
            label_nums[label] = len(labels)
            labels.append(label)
            code.append((tags.label, label))

    for record in code:
        tag = record[0]
        if tag == tags.ref:
            _, op, label = record
            out.write(encode_int(tag) + encode_int(op) + encode_int(label_nums[label]))
        elif tag == tags.label or tag == tags.string:
            _, string = record
            out.write(encode_int(tag) + encode_string(string))
        else:
            out.write(''.join(map(encode_int, record)))

def decode_literal(arg):
    assert arg[:1] == "'" == arg[-1:]
    return arg[1:-1]


if __name__ == '__main__':
    main(sys.stdin, sys.stdout)
