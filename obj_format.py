"""
Encode/decode data in object files.
"""

label, string, ref, op0, op1 = range(5)

def encode_int(n):
    assert 0 <= n < 128         # XXX for now
    return bytes(chr(n))

def encode_string(s):
    return encode_int(len(s)) + bytes(s)

def read_int(infile):
    c = infile.read(1)
    assert c
    b = ord(c)
    assert 0 <= b < 128     # TODO encode bigger numbers. can't put this off.
    return b

def read_string(infile):
    n = read_int(infile)
    s = infile.read(n)
    assert len(s) == n
    return s
