# 원고의 ○ - · 문단 줄바꿈을 근사 계산해 마지막 줄이 짧은 문단(외톨이 단어)을 찾는다
import sys
EM=15  # pt
def cw(c):
    o=ord(c)
    if c==' ': return SP
    if 0xAC00<=o<=0xD7A3 or 0x3130<=o<=0x318F or c in '□○※「」': return 1.0
    if c in '·': return 0.5
    if c in ',.()%~:;\'"': return 0.33
    if c.isdigit(): return 0.55
    if c.isupper(): return 0.75
    return 0.6   # 휴먼명조 영문은 넓음(한글 화면 확인)
STY={'O':(15,21,'○ '),'D':(30,12.5,'- '),'P':(45,19,'· ')}
W=482.5  # 본문 폭 pt(한글 화면 줄바꿈으로 보정, 공백 0.5em)
def lines(tag,text):
    left,hang,pre=STY[tag]
    words=(pre+text).split(' ')
    out=[];cur='';first=True
    for w in words:
        cand=(cur+' '+w) if cur else w
        width=sum(cw(c) for c in cand)*EM
        lim=W-left if first else W-left-hang
        if width>lim and cur:
            out.append(cur); cur=w; first=False
        else: cur=cand
    out.append(cur); return out
if __name__=='__main__':
    SP=float(sys.argv[2]) if len(sys.argv)>2 else 0.3
    for n,l in enumerate(open(sys.argv[1],encoding='utf-8'),1):
        tag,_,rest=l.rstrip('\n').partition(' ')
        if tag not in STY: continue
        if tag=='D' and rest.startswith('- '): rest=rest[2:]
        if tag=='O': pass
        L=lines(tag,rest)
        last=L[-1]
        if len(L)>1 and (len(last.split())<=1 or len(last.replace(' ',''))<=5):
            print(f'{n}: [{len(L)}줄] 마지막 줄 "{last}"  | {rest[:40]}')

def stretch_report(path, sp=0.5, thr=1.0):
    """양쪽 정렬에서 공백이 크게 벌어지는 줄(공백 하나당 추가 폭 thr em 이상)을 찾는다"""
    global SP; SP=sp
    for n,l in enumerate(open(path,encoding='utf-8'),1):
        tag,_,rest=l.rstrip('\n').partition(' ')
        if tag not in STY: continue
        L=lines(tag,rest); left,hang,_=STY[tag]
        for k,line in enumerate(L[:-1]):
            lim=(W-left if k==0 else W-left-hang)/EM
            used=sum(cw(c) for c in line); gaps=line.count(' ')
            if gaps and (lim-used)/gaps>=thr:
                print(f'{n}: {k+1}줄 공백당 +{(lim-used)/gaps:.1f}em | {line}  // 다음: {L[k+1].split()[0]}')
