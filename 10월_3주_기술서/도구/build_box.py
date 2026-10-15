# 요약 상자 마무리: 셀 높이·안쪽 여백 지정, 셀 안 문단 줄 배치 캐시(lineseg) 추가
# 표 크기·여백 단위: HWPUNIT(1mm = 283.465)
import re, sys
p = sys.argv[1] if len(sys.argv) > 1 else 'out/Contents/section0.xml'
s = open(p, encoding='utf-8').read()
import re as _re
m = _re.search(r'<hp:tbl [^>]*rowCnt="1" colCnt="1"[^>]*>', s)
i = m.start(); j = s.index('</hp:tbl>', i) + 9; t = s[i:j]
H = 4000  # 최소 높이: 한글이 내용에 맞춰 늘림(요약 상자를 찾아 처리하도록 10월 3주 수정)
t = re.sub(r'(<hp:sz width="\d+" widthRelTo="ABSOLUTE" height=")\d+', r'\g<1>%d' % H, t, count=1)
t = re.sub(r'<hp:cellSz width="(\d+)" height="\d+"/>', r'<hp:cellSz width="\1" height="%d"/>' % H, t)
t = re.sub(r'<hp:inMargin [^>]*/>', '<hp:inMargin left="1134" right="1134" top="567" bottom="567"/>', t)
t = t.replace('hasMargin="0"', 'hasMargin="1"')
t = re.sub(r'<hp:cellMargin [^>]*/>', '<hp:cellMargin left="1134" right="1134" top="567" bottom="567"/>', t)
# 문단별 (글자 높이 HWPUNIT, 줄 간격 %, 위 간격, 아래 간격)  — 위아래 간격은 lineseg용 HWPUNIT
paras = re.findall(r'<hp:p [^>]*>', t)
first_pp = re.search(r'paraPrIDRef="(\d+)"', paras[0]).group(1)
y = [0]

def add(m):
    para = m.group(0)
    if '<hp:linesegarray>' in para:
        return para
    pp = re.search(r'paraPrIDRef="(\d+)"', para).group(1)
    h, ls, prev, nxt = (1500, 160, 300, 300) if pp == first_pp else (1400, 160, 0, 0)
    y[0] += prev
    sp = int(h * (ls - 100) / 100)
    seg = (f'<hp:linesegarray><hp:lineseg textpos="0" vertpos="{y[0]}" vertsize="{h}" textheight="{h}" '
           f'baseline="{int(h*0.85)}" spacing="{sp}" horzpos="0" horzsize="45922" flags="393216"/></hp:linesegarray>')
    y[0] += h + sp + nxt
    return para.replace('</hp:p>', seg + '</hp:p>')

t = re.sub(r'<hp:p [^>]*>.*?</hp:p>', add, t)
s = s[:i] + t + s[j:]
open(p, 'w', encoding='utf-8').write(s)
print('box done', y[0])
