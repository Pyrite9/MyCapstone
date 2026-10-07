# 템플릿.hwpx header.xml에 양식 v2 글꼴·글자모양·문단모양·테두리·스타일 추가
import re, copy
from lxml import etree
P='src/Contents/header.xml'
H='http://www.hancom.co.kr/hwpml/2011/head'; C='http://www.hancom.co.kr/hwpml/2011/core'
NS={'hh':H,'hc':C}
t=etree.parse(P); r=t.getroot()
def q(x): return r.find(x,NS)
LANGS=['HANGUL','LATIN','HANJA','JAPANESE','OTHER','SYMBOL','USER']
# 1) 글꼴 추가
FONTS=['휴먼명조','HY헤드라인M','맑은 고딕','한양중고딕']
SUBST={}   # 대체 글꼴이 필요하면 {'글꼴':'대체 글꼴'}
FTYPE={'한양중고딕':'HFT'}   # 한컴 글꼴은 HFT. 목록의 '중고딕'은 파일 안에서 '한양중고딕'(10.01 관리자가 한글에서 적용한 파일로 확인)
fid={}
for ff in r.find('.//hh:fontfaces',NS):
    fonts=ff.findall('hh:font',NS); n=len(fonts)
    for i,name in enumerate(FONTS):
        f=copy.deepcopy(fonts[0]); f.set('id',str(n+i)); f.set('face',name); f.set('type',FTYPE.get(name,'TTF'))
        if name in SUBST:
            sf=etree.Element('{%s}substFont'%H, face=SUBST[name], type='TTF', isEmbedded='0', binaryItemIDRef='')
            f.insert(0,sf)
        ff.append(f); fid[(ff.get('lang'),name)]=n+i
    ff.set('fontCnt',str(n+len(FONTS)))
# 2) 글자 모양
cps=q('.//hh:charProperties'); base=cps.find('hh:charPr',NS)
def charpr(font,pt,bold=False,color=None):
    c=copy.deepcopy(base); i=len(cps); c.set('id',str(i)); c.set('height',str(int(pt*100)))
    if color: c.set('textColor',color)
    fr=c.find('hh:fontRef',NS)
    for l in LANGS: fr.set(l.lower(),str(fid[(l,font)]))
    for b in c.findall('hh:bold',NS): c.remove(b)
    if bold:
        b=etree.SubElement(c,'{%s}bold'%H); 
        # bold must come before underline/strikeout etc.: move after offset
        c.remove(b); c.insert(list(c).index(c.find('hh:offset',NS))+1,b)
    cps.append(c); cps.set('itemCnt',str(len(cps))); return i
# 3) 테두리 (절 아래 굵은 선, 요약 상자)
bfs=q('.//hh:borderFills'); bbase=bfs.find('hh:borderFill',NS)
def borderfill(bottom=None, box=None, top=None):
    b=copy.deepcopy(bbase); i=len(bfs)+1; b.set('id',str(i))
    for side in ['leftBorder','rightBorder','topBorder','bottomBorder']:
        e=b.find('hh:'+side,NS)
        w = box if box else (bottom if side=='bottomBorder' and bottom else (top if side=='topBorder' and top else None))
        if w: e.set('type','SOLID'); e.set('width',w)
    b.find('hh:diagonal',NS).set('type','NONE')
    bfs.append(b); bfs.set('itemCnt',str(len(bfs))); return i
BF_RULE=borderfill(bottom='0.4 mm')
BF_TB=borderfill(top='0.7 mm', bottom='0.4 mm')
# 4) 문단 모양
pps=q('.//hh:paraProperties'); pbase=pps.find('hh:paraPr',NS)
# 차례용 탭: 본문 폭(170mm = 48189 HWPUNIT) 오른쪽 끝, 점선 채움
tabs=q('.//hh:tabProperties')
def tabpr_right(pos=48000, leader='DOT'):
    t=etree.SubElement(tabs,'{%s}tabPr'%H); i=len(tabs)-1; t.set('id',str(i)); t.set('autoTabLeft','0'); t.set('autoTabRight','0')
    HP='http://www.hancom.co.kr/hwpml/2011/paragraph'
    sw=etree.SubElement(t,'{%s}switch'%HP)
    case=etree.SubElement(sw,'{%s}case'%HP); case.set('{%s}required-namespace'%HP,'http://www.hancom.co.kr/hwpml/2016/HwpUnitChar')
    etree.SubElement(case,'{%s}tabItem'%H,pos=str(pos),type='RIGHT',leader=leader,unit='HWPUNIT')
    df=etree.SubElement(sw,'{%s}default'%HP)
    etree.SubElement(df,'{%s}tabItem'%H,pos=str(pos*2),type='RIGHT',leader=leader)
    tabs.set('itemCnt',str(len(tabs))); return i
TAB_TOC=tabpr_right()
def parapr(align='JUSTIFY',left=0,intent=0,prev=0,nxt=0,ls=170,border=None,keep_next=False,word=False,tab=None):
    p=copy.deepcopy(pbase); i=len(pps); p.set('id',str(i))
    if tab is not None: p.set('tabPrIDRef',str(tab))
    p.find('hh:align',NS).set('horizontal',align)
    p.find('hh:breakSetting',NS).set('keepWithNext','1' if keep_next else '0')
    # 한글 줄 나눔: breakNonLatinWord BREAK_WORD = 어절, KEEP_WORD = 글자(한글 2018 화면 확인 10.01)
    p.find('hh:breakSetting',NS).set('breakNonLatinWord','BREAK_WORD' if word else 'KEEP_WORD')
    m=p.find('hh:margin',NS)
    for k,v in dict(intent=intent,left=left,prev=prev,next=nxt).items(): m.find('hc:'+k,NS).set('value',str(v))
    p.find('hh:lineSpacing',NS).set('value',str(ls))
    if border:
        bd=p.find('hh:border',NS); bd.set('borderFillIDRef',str(border)); bd.set('offsetBottom','283')
        if border==BF_TB: bd.set('offsetTop','1134'); bd.set('offsetBottom','1134')
    pps.append(p); pps.set('itemCnt',str(len(pps))); return i
# 5) 스타일
sts=q('.//hh:styles'); sbase=sts.find('hh:style',NS)
def style(name,eng,pp,cp,typ='PARA'):
    s=copy.deepcopy(sbase); i=len(sts)
    s.set('id',str(i)); s.set('type',typ); s.set('name',name); s.set('engName',eng)
    s.set('paraPrIDRef',str(pp)); s.set('charPrIDRef',str(cp)); s.set('nextStyleIDRef',str(i if typ=='PARA' else 0))
    sts.append(s); sts.set('itemCnt',str(len(sts))); return i
# 문단 여백·간격 단위: 1pt = 200 (한글 2018 문단 모양 창으로 확인, 2026.10.01)
# 글자 크기 단위: 1pt = 100
def pt(v): return int(round(v*200))
spec=[
 # name, eng, font, size, bold, paragraph kwargs (left/intent/prev/next는 pt 값)
 ('보고서 제목','Report Title','HY헤드라인M',20,False,dict(align='CENTER',nxt=pt(12),ls=160)),
 ('절','Section','HY헤드라인M',18,False,dict(prev=pt(18),nxt=pt(2),ls=160,border=BF_RULE,keep_next=True)),
 # □: 미확인 추정값(16pt 글꼴, "□ " 폭 약 22pt)
 ('□ 소제목','Heading Box','HY헤드라인M',16,False,dict(left=0,intent=-pt(22.4),prev=pt(10),nxt=pt(2),ls=160,keep_next=True,word=True)),
 # ○ - · ※: 한글 2018 화면에서 둘째 줄 정렬 확인한 값
 ('○ 본문','Body 1','휴먼명조',15,False,dict(left=pt(15),intent=-pt(21),prev=pt(4),ls=170,word=True)),
 ('- 본문','Body 2','휴먼명조',15,False,dict(left=pt(30),intent=-pt(12.5),ls=170,word=True)),
 ('· 본문','Body 3','휴먼명조',15,False,dict(left=pt(45),intent=-pt(19),ls=170,word=True)),
 ('※ 주석','Note','맑은 고딕',12,False,dict(left=pt(36),intent=-pt(15),ls=130,word=True)),
 ('표 캡션','Table Caption','맑은 고딕',12,True,dict(align='CENTER',prev=pt(6),nxt=pt(2),ls=130,keep_next=True)),
 ('표 헤더','Table Header','맑은 고딕',12,True,dict(align='CENTER',ls=130,word=True)),
 ('표 본문','Table Body','맑은 고딕',12,False,dict(align='LEFT',ls=130,word=True)),
 ('그림 캡션','Figure Caption','맑은 고딕',12,True,dict(align='CENTER',prev=pt(2),nxt=pt(6),ls=130)),
 ('요약 제목','Summary Title','HY헤드라인M',15,False,dict(align='CENTER',prev=pt(3),nxt=pt(3),ls=160)),
 # 요약 본문: ○ 폭을 14pt 비율로 환산(21 x 14/15 = 19.6)
 ('요약 본문','Summary Body','휴먼명조',14,False,dict(left=pt(3),intent=-pt(19.6),ls=160,word=True)),
 # 참고 문헌: 12pt, 왼쪽 정렬, "[n] " 번호 폭만큼 22pt 내어쓰기
 # 표지
 ('표지 과목','Cover Course','HY헤드라인M',20,False,dict(align='CENTER',prev=pt(150),nxt=pt(16),ls=160)),
 ('표지 제목','Cover Title','HY헤드라인M',32,False,dict(align='CENTER',ls=150,border=BF_TB)),
 ('표지 부제','Cover Subtitle','휴먼명조',16,False,dict(align='CENTER',prev=pt(22),ls=160)),
 ('표지 날짜','Cover Date','HY헤드라인M',16,False,dict(align='CENTER',prev=pt(150),nxt=pt(30),ls=160)),
 ('표지 표','Cover Table Holder','맑은 고딕',12,False,dict(align='CENTER',ls=130)),
 # 출처: 중고딕(파일 안 이름 한양중고딕) 10pt 녹색(#008000, 10.01 관리자 지정), 왼쪽 정렬, ○ 내용 첫 글자(36pt)에서 시작, "※ " 폭만큼 내어쓰기
 ('출처','Source',('한양중고딕','#008000'),10,False,dict(align='LEFT',left=pt(36),intent=-pt(12.5),nxt=pt(2),ls=130,word=True)),
 ('참고 문헌','Reference','휴먼명조',11,False,dict(align='LEFT',left=0,intent=-pt(20),prev=pt(1.5),ls=130,word=True)),
 # 차례: 절은 HY헤드라인M 14pt, □는 휴먼명조 13pt 들여씀, 쪽 번호는 오른쪽 끝 점선 탭
 ('차례 제목','TOC Title','HY헤드라인M',20,False,dict(align='CENTER',nxt=pt(18),ls=160)),
 ('차례 1','TOC 1','HY헤드라인M',14,False,dict(align='LEFT',prev=pt(8),nxt=pt(1),ls=150,tab=TAB_TOC)),
 ('차례 2','TOC 2','휴먼명조',13,False,dict(align='LEFT',left=pt(16),ls=135,tab=TAB_TOC)),
]
ids={}
for name,eng,font,pt,bold,kw in spec:
    font,color=(font if isinstance(font,tuple) else (font,None))
    cp=charpr(font,pt,bold,color); pp=parapr(**kw); ids[name]=(style(name,eng,pp,cp),pp,cp)
# 글자 스타일
pp0=0
cp=charpr('휴먼명조',15,True); ids['괄호 키워드']=(style('괄호 키워드','Keyword',pp0,cp,'CHAR'),pp0,cp)
cp=charpr('휴먼명조',13,False); ids['괄호 보충']=(style('괄호 보충','Aside',pp0,cp,'CHAR'),pp0,cp)
cp=charpr('휴먼명조',15,True); ids['강조']=(style('강조','Emphasis',pp0,cp,'CHAR'),pp0,cp)
ids['_BF_BOX']=(borderfill(box='0.4 mm'),0,0)
ids['_BF_TBL']=(0,0,0)
t.write(P,xml_declaration=True,encoding='UTF-8',standalone=True)
import json; json.dump(ids,open('ids.json','w'),ensure_ascii=False,indent=0)
print(ids)
