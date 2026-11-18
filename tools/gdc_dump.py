import sys, struct, zstandard
def load(path):
    b=open(path,'rb').read()
    assert b[:4]==b'GDSC'; ver,size=struct.unpack_from('<II',b,4)
    d=zstandard.ZstdDecompressor().decompress(b[12:],max_output_size=size) if size else b[12:]
    return ver,d
def parse(d):
    ic,cc,lc,tc=struct.unpack_from('<IIII',d,0); o=16; ids=[]
    for _ in range(ic):
        n,=struct.unpack_from('<I',d,o); o+=4
        ids.append(''.join(chr(struct.unpack_from('<I',bytes(x^0xb6 for x in d[o+4*i:o+4*i+4]))[0]) for i in range(n))); o+=4*n
    consts=[]
    for _ in range(cc):
        t,=struct.unpack_from('<I',d,o); typ=t&0xffff; big=t&(1<<16); o+=4
        if typ==0: consts.append(None)
        elif typ==1: consts.append(bool(struct.unpack_from('<I',d,o)[0])); o+=4
        elif typ==2:
            if big: consts.append(struct.unpack_from('<q',d,o)[0]); o+=8
            else: consts.append(struct.unpack_from('<i',d,o)[0]); o+=4
        elif typ==3:
            if big: consts.append(struct.unpack_from('<d',d,o)[0]); o+=8
            else: consts.append(struct.unpack_from('<f',d,o)[0]); o+=4
        elif typ in (4,21):
            n,=struct.unpack_from('<I',d,o); o+=4; consts.append(d[o:o+n].decode('utf8','replace')); o+=n+((4-n%4)%4)
        else:
            consts.append(f'<variant type {typ}; stopped>'); break
    return ids,consts
if __name__=='__main__':
    for p in sys.argv[1:]:
        ver,d=load(p); ids,consts=parse(d)
        print(f'=== {p} (v{ver}, {len(d)} bytes)'); print('IDS:',' '.join(ids)); print('CONSTS:',consts)
