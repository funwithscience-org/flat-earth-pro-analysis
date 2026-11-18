import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
from gdc_dump import load
T = """EMPTY ANNOTATION IDENTIFIER LITERAL < <= > >= == != and or not && || ! & | ~ ^ << >> + - * ** / %
= += -= *= **= /= %= <<= >>= &= |= ^= if elif else for while break continue pass return match when
as assert await breakpoint class class_name const enum extends func in is namespace preload self signal static super trait var void yield
[ ] { } ( ) , ; . .. ... : $ -> _ NEWLINE INDENT DEDENT PI TAU INF NAN VCS ` ? ERROR EOF""".split()
def variants(d, o, cc):
    out=[]
    for _ in range(cc):
        t,=struct.unpack_from('<I',d,o); typ=t&0xffff; big=t&(1<<16); o+=4
        if typ==0: out.append('null')
        elif typ==1: out.append('true' if struct.unpack_from('<I',d,o)[0] else 'false'); o+=4
        elif typ==2:
            if big: out.append(str(struct.unpack_from('<q',d,o)[0])); o+=8
            else: out.append(str(struct.unpack_from('<i',d,o)[0])); o+=4
        elif typ==3:
            if big: v=struct.unpack_from('<d',d,o)[0]; o+=8
            else: v=struct.unpack_from('<f',d,o)[0]; o+=4
            s=repr(v); out.append(s if ('.' in s or 'e' in s or 'n' in s) else s+'.0')
        elif typ in (4,21):
            n,=struct.unpack_from('<I',d,o); o+=4; s=d[o:o+n].decode('utf8','replace'); o+=n+((4-n%4)%4)
            out.append(('&' if typ==21 else '')+'"'+s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n').replace('\t','\\t')+'"')
        else: raise ValueError(f'variant type {typ}')
    return out,o
def decomp(path):
    ver,d=load(path)
    ic,cc,lc,tc=struct.unpack_from('<IIII',d,0); o=16; ids=[]
    for _ in range(ic):
        n,=struct.unpack_from('<I',d,o); o+=4
        ids.append(''.join(chr(struct.unpack_from('<I',bytes(x^0xb6 for x in d[o+4*i:o+4*i+4]))[0]) for i in range(n))); o+=4*n
    consts,o=variants(d,o,cc)
    lmap={}; cmap={}
    for i in range(lc):
        a,b=struct.unpack_from('<II',d,o+8*i); lmap[a]=b
    o+=lc*8
    for i in range(lc):
        a,b=struct.unpack_from('<II',d,o+8*i); cmap[a]=b
    o+=lc*8
    ti=-1; lastline=0
    lines=[]; cur=[]; indent=0; prev=None
    def flush():
        nonlocal cur
        lines.append(' '*indent+''.join(cur).strip()); cur=[]
    while o<len(d):
        ti+=1
        if ti in lmap and (cur or lines or True):
            if cur: flush()
            if lmap[ti]-lastline>1 and lines: lines.append('')
            lastline=lmap[ti]; indent=max(0,cmap.get(ti,1)-1)
        if d[o]&0x80:
            w,=struct.unpack_from('<I',d,o); typ=w&0x7f; idx=w>>8; o+=8
        else:
            typ=d[o]; idx=None; o+=5
        name=T[typ] if typ<len(T) else f'<T{typ}>'
        if name=='NEWLINE': flush(); continue
        if name=='INDENT': indent+=1; continue
        if name=='DEDENT': indent=max(0,indent-1); continue
        if name=='EOF': break
        if name in ('IDENTIFIER','ANNOTATION'): txt=ids[idx]
        elif name in ('LITERAL','ERROR'): txt=consts[idx]
        else: txt=name
        tight_before = txt in (')',']',',','.',':','(','[') or prev in ('(','[','.','$','!','~') 
        if txt=='(' and prev in ('if','elif','while','return','and','or','not','in','=','+','-','*','/',',','==','!=','<','>','<=','>=','+=','-=','*=','/=','match','await','else'): tight_before=False
        if txt=='[' and prev in ('=','in','return',',','+','(' ) : tight_before = prev=='('
        cur.append(('' if tight_before or not cur else ' ')+txt); prev=txt
    if cur: flush()
    return '\n'.join(lines)
if __name__=='__main__':
    src,dst=sys.argv[1],sys.argv[2]
    ok=bad=0
    for root,_,files in os.walk(src):
        for f in files:
            if f.endswith('.gdc'):
                p=os.path.join(root,f); q=os.path.join(dst,os.path.relpath(p,src))[:-1]
                os.makedirs(os.path.dirname(q),exist_ok=True)
                try: open(q,'w').write(decomp(p)+'\n'); ok+=1
                except Exception as e: bad+=1; print('FAIL',p,e)
    print('ok',ok,'bad',bad)
