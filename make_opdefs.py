"""
XXX
"""

def main(f):
    ops = []
    body = None
    for line in f:
        line = line.rstrip('\n')
        if line == '':
            body = None
        elif line[:1].isspace():
            assert body is not None
            body.append(line)
        else:
            parts = line.split()
            if len(parts) == 1:
                op, arg = parts[0], None
            elif len(parts) == 2:
                op, arg = parts
            else:
                assert False
            body = []
            ops.append((op, arg, body))
    gen_opdefs(ops)

def gen_opdefs(ops):
    opcodes = {name: opcode for opcode, (name, arg, body) in enumerate(ops)}
    with open('opdefs.py', 'w') as f:

        print >>f, 'import re'  # TODO pass this through from 'instructions' file
        print >>f

        print >>f, 'opcodes = %r' % opcodes
        print >>f

        print >>f, 'ops = %r' % [(name, arg) for (name, arg, body) in ops]
        print >>f

        print >>f, 'def step(self):'
        print >>f, '    op = self.code[self.pc]'
        print >>f
        for opcode, (name, param, body) in enumerate(ops):
            print >>f, ('    %sif op == %d:  # %s'
                        % (('' if opcode == 0 else 'el'), opcode, name))
            if param is None:
                print >>f, '        self.pc += 1'
            else:
                print >>f, '        arg = self.code[self.pc+1]'
                print >>f, '        self.pc += 2'
                if param == 'addr':
                    print >>f, '        addr = self.addrs[arg]'
                elif param == 'string':
                    print >>f, '        string = self.strings[arg]'
                elif param != 'arg':
                    print >>f, '        %s = arg' % param
            for line in body:
                print >>f, '    ' + line
            print >>f
        print >>f, '    else:'
        print >>f, '        raise Exception("Unknown opcode: %d" % op)'
        

if __name__ == '__main__':
    with open('instructions') as f:
        main(f)
