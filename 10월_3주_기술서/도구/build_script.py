# 이전 대본(v2.5 모듈형)의 문단 서식을 그대로 복사해 새 대본 docx를 만든다
import copy, re, sys
from docx import Document
sys.path.insert(0, '/home/claude/w10_3')
from script_data import META, TITLE, SUBTITLE, SECTIONS, QA

TPL, OUT = sys.argv[1], sys.argv[2]
d = Document(TPL)
ps = d.paragraphs
S = {'blank': ps[0], 'title': ps[1], 'sub': ps[2], 'meta': ps[4], 'pb': ps[9],
     'sec': ps[10], 'mod': ps[11], 'body': ps[12], 'q': ps[97], 'a': ps[98]}
S = {k: copy.deepcopy(v._p) for k, v in S.items()}
body = d.element.body
sectPr = body.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sectPr')
for el in list(body):
    if el is not sectPr:
        body.remove(el)
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def add(kind, texts=None):
    p = copy.deepcopy(S[kind])
    runs = p.findall(W + 'r')
    if texts is not None:
        for r, t in zip(runs, texts):
            for tt in r.findall(W + 't'):
                r.remove(tt)
            te = r.makeelement(W + 't', {}); te.text = t
            te.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r.append(te)
        for r in runs[len(texts):]:
            p.remove(r)
    sectPr.addprevious(p)
    return p

def add_body(text, kind='body'):
    p = copy.deepcopy(S[kind])
    runs = p.findall(W + 'r')
    base = runs[0]
    for r in runs:
        p.remove(r)
    for i, seg in enumerate(re.split(r'\*\*', text)):
        if not seg:
            continue
        r = copy.deepcopy(base)
        for tt in r.findall(W + 't'):
            r.remove(tt)
        rpr = r.find(W + 'rPr')
        b = rpr.find(W + 'b') if rpr is not None else None
        if i % 2 == 1:
            if b is None:
                rpr.insert(0, rpr.makeelement(W + 'b', {}))
        elif b is not None:
            rpr.remove(b)
        te = r.makeelement(W + 't', {}); te.text = seg
        te.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r.append(te); p.append(r)
    sectPr.addprevious(p)

add('blank')
add('title', [TITLE]); add('sub', [SUBTITLE]); add('blank')
for k, v in META:
    add('meta', [k, '   ' + v])
add('pb')
for sec, mods in SECTIONS:
    add('sec', [sec])
    for head, name, paras in mods:
        add('mod', [head + '  ', name])
        for t in paras:
            add_body(t)
add('sec', ['예상 질문과 답변'])
prev = None
for g, q, a in QA:
    if g != prev:
        add('mod', [g + '  ', '']); prev = g
    add('q', ['Q. ' + q])
    add_body(a, 'a')
d.save(OUT)
print('saved', OUT)
