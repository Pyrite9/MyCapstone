# 원고(txt) + 템플릿_v3.hwpx → 보고서 hwpx
# 사용: python3 build_report.py <템플릿.hwpx> <원고.txt> <이미지 폴더> <결과.hwpx>
import re, sys, json, os
from lxml import etree
from hwpx.document import HwpxDocument

TPL, SRC, IMG, OUT = sys.argv[1:5]
COVER_DATE = sys.argv[5] if len(sys.argv) > 5 else '2026.10'
d = HwpxDocument.open(TPL)

# 1) 스타일을 이름으로 조회
H = 'http://www.hancom.co.kr/hwpml/2011/head'
import zipfile
hx = etree.fromstring(zipfile.ZipFile(TPL).read('Contents/header.xml'))
ST = {}
for s in hx.iter('{%s}style' % H):
    ST[s.get('name')] = (s.get('id'), s.get('paraPrIDRef'), s.get('charPrIDRef'))
BF = {}  # 테두리 조합: (위,아래,왼,오,음영) → id
for b in hx.iter('{%s}borderFill' % H):
    g = lambda side: b.find('{%s}%s' % (H, side))
    def w(side):
        e = g(side)
        return e.get('width') if e is not None and e.get('type') == 'SOLID' else None
    fill = b.find('.//{http://www.hancom.co.kr/hwpml/2011/core}winBrush')
    shade = fill is not None and fill.get('faceColor') == '#D9D9D9'
    BF.setdefault((w('topBorder'), w('bottomBorder'), w('leftBorder'), w('rightBorder'), shade), b.get('id'))
BOX = BF[('0.4 mm', '0.4 mm', '0.4 mm', '0.4 mm', False)]
KW = ST['괄호 키워드'][2]
EMPH = ST['강조'][2]
BOLD_TBL = ST['표 헤더'][2]

# 2) 견본 제거: 첫 두 문단(구역 설정, 쪽 나눔)만 남김
for p in list(d.paragraphs)[2:]:
    p.remove()


def strip_runs(p):
    for r in list(p.runs):
        r.element.getparent().remove(r.element)


def runs_from(text, base_cp, keyword=True):
    """텍스트를 (내용, 글자모양) 조각으로 나눔: 기호 뒤 첫 괄호 = 괄호 키워드, **굵게** = 강조"""
    out = []
    m = re.match(r'^([○\-·※□] )(\([^)]*\))(.*)$', text) if keyword else None
    if m:
        out += [(m.group(1), base_cp), (m.group(2), KW)]
        text = m.group(3)
    for i, part in enumerate(re.split(r'\*\*', text)):
        if part:
            out.append((part, EMPH if i % 2 else base_cp))
    return out


def para(style, text, keyword=True, target=None):
    sid, pp, cp = ST[style]
    if target is None:
        p = d.add_paragraph('', style_id_ref=sid, para_pr_id_ref=pp, char_pr_id_ref=cp, include_run=False)
    else:
        p = target.add_paragraph('')
        p.style_id_ref, p.para_pr_id_ref = sid, pp
        strip_runs(p)
    for t, c in runs_from(text, cp, keyword):
        p.add_run(t, char_pr_id_ref=c)
    return p


def table(rows, widths=None, bold_first_col=True, header=True, holder=None):
    R, C = len(rows), len(rows[0])
    if holder:
        tbl = d.add_table(R, C, style_id_ref=ST[holder][0], para_pr_id_ref=ST[holder][1], char_pr_id_ref=ST[holder][2])
    else:
        tbl = d.add_table(R, C)
    total = 48188
    if widths is not None and len(widths) != C:
        widths = None
    if widths is None:
        widths = [total // C] * C
        widths[-1] = total - sum(widths[:-1])
    tbl.set_column_widths(widths)
    short_col = [all(len(rows[r][c]) <= 4 for r in range(1 if header else 0, R)) for c in range(C)]
    for r in range(R):
        for c in range(C):
            key = ('0.4 mm' if r == 0 else '0.12 mm', '0.4 mm' if r == R - 1 else '0.12 mm',
                   None if c == 0 else '0.12 mm', None if c == C - 1 else '0.12 mm', r == 0 and header)
            tbl.set_cell_border_fill(r, c, BF[key])
            cell = tbl.cell(r, c)
            style = '표 헤더' if (r == 0 and header) else '표 본문'
            sid, pp, cp = ST[style]
            lines = [x.strip() for x in rows[r][c].split(';;')]
            for k, line in enumerate(lines):
                if k == 0:
                    p = cell.paragraphs[0]
                    p.style_id_ref, p.para_pr_id_ref = sid, pp
                    strip_runs(p)
                else:
                    p = cell.add_paragraph('')
                    p.style_id_ref, p.para_pr_id_ref = sid, pp
                    strip_runs(p)
                bold = (r > 0 or not header) and c == 0 and bold_first_col and k == 0
                if not (r == 0 and header) and short_col[c] and c > 0:   # 짧은 값만 있는 열(○ △ ×, 핵심)은 가운데
                    p.para_pr_id_ref = ST['표 헤더'][1]
                p.add_run(line, char_pr_id_ref=BOLD_TBL if bold else cp)
    return tbl


def figure(fname, caption, width_mm):
    path = os.path.join(IMG, fname)
    from PIL import Image
    w, h = Image.open(path).size
    sid, pp, cp = ST['그림 캡션']
    d.add_picture(open(path, 'rb').read(), 'png', width_mm=width_mm, height_mm=width_mm * h / w,
                  align='CENTER', para_pr_id_ref=ST['표 캡션'][1])
    para('그림 캡션', caption, keyword=False)


# 3) 원고 해석
lines = [l.rstrip('\n') for l in open(SRC, encoding='utf-8')]
cover_start = None
toc_start = toc_end = None
box_lines, i = [], 0
WIDTHS = {
    '[표 1]': [8000, 20000, 20188],
    '[표 2]': [7400, 10900, 9900, 19988],
    '[표 3]': [7400, 10900, 9900, 19988],
    '[표 4]': [7400, 10900, 9900, 19988],
    '[표 5]': [7400, 10900, 9900, 19988],
    '[표 6]': [7400, 10900, 9900, 19988],
    '[표 7]': [7400, 10900, 9900, 19988],

    '[표 1-1]': [9000, 39188], '[표 1-2]': [6500, 20844, 20844], '[표 1-3]': [11000, 18594, 18594],
    '[표 1-4]': [15000, 6896, 6896, 6896, 12500], '[표 1-5]': [4000, 11000, 7000, 20188, 6000],
    '[표 1-6]': [9500, 12896, 12896, 12896], '[표 1-7]': [10000, 38188], '[표 1-8]': [15000, 33188],
    '[표 2-1]': [8000, 5500, 17500, 11000, 6188], '[표 2-2]': [6800, 14500, 12000, 5000, 9888],
    '[표 3-1]': [7500, 9500, 9000, 10594, 11594],
    '[표 3-2]': [7500, 9500, 9000, 10594, 11594],
    '[표 3-3]': [7500, 9500, 9000, 10594, 11594],
    '[표 3-4]': [7500, 9500, 9000, 10594, 11594],
    '[표 3-5]': [7500, 9500, 9000, 10594, 11594],
    '[표 3-6]': [7500, 9500, 9000, 10594, 11594],
}


def flush_box():
    global box_lines
    if not box_lines:
        return
    box = d.add_table(1, 1, border_fill_id_ref=BOX)
    cell = box.cell(0, 0)
    p = cell.paragraphs[0]
    sid, pp, cp = ST['요약 제목']
    p.style_id_ref, p.para_pr_id_ref = sid, pp
    strip_runs(p)
    p.add_run('< 요 약 >', char_pr_id_ref=cp)
    for bl in box_lines:
        para('요약 본문', bl, keyword=False, target=cell)
    box_lines = []


page_marks = []
page_next = False
ref_no = 0
while i < len(lines):
    l = lines[i]
    n_before = len(d.paragraphs)
    if not l.strip() or l.startswith('#'):
        i += 1; continue
    tag, _, rest = l.partition(' ')
    if tag != 'BOX':
        flush_box()
    if tag == 'COVER':
        cover_start = len(d.paragraphs)
        para('표지 과목', '캡스톤디자인', keyword=False)
        para('표지 제목', rest.strip() or '프로젝트 보고서', keyword=False)   # 원고 'COVER 프로젝트 개요서'처럼 표지 제목 지정
        para('표지 부제', '발자국 — 조별과제 과정기록 & 평가지원 서비스', keyword=False)
        para('표지 날짜', COVER_DATE, keyword=False)
        table([['소속/반', '영진전문대학교 컴퓨터정보계열 AI소프트웨어과 2-AB'],
               ['팀명', '결(結)'],
               ['팀원', '김동건 / 김효민 / 양원야 / 윤장현 / 이종민 / 장호진']], widths=[8000, 30000], header=False, holder='표지 표')
        cover_end = len(d.paragraphs)
    elif tag == 'TOC':
        toc_start = len(d.paragraphs)
        para('차례 제목', '차    례', keyword=False)
    elif tag in ('T1', 'T2'):
        name, _, pg = rest.rpartition('|')
        para('차례 1' if tag == 'T1' else '차례 2', name + '\t' + pg, keyword=False)
        toc_end = len(d.paragraphs)
    elif tag == 'TITLE':
        para('보고서 제목', rest, keyword=False)
    elif tag == 'SUB':
        para('요약 제목', rest, keyword=False)
    elif tag == 'BOX':
        box_lines.append(rest)
    elif tag == 'S':
        para('절', rest, keyword=False)
    elif tag == 'H':
        para('□ 소제목', rest, keyword=False)
    elif tag == 'O':
        para('○ 본문', rest)
    elif tag == 'D':
        para('- 본문', rest, keyword=False)
    elif tag == 'P':
        para('· 본문', rest, keyword=False)
    elif tag == 'N':
        para('※ 주석', rest, keyword=False)
    elif tag == 'PAGE':
        page_next = True
    elif tag == 'SRC':
        para('출처', '※ 출처: ' + rest, keyword=False)
    elif tag == 'REF':
        ref_no += 1
        para('참고 문헌', '[%d] ' % ref_no + rest, keyword=False)
    elif tag == 'FIG':
        f, cap, wmm = rest.split('|')
        figure(f, cap, float(wmm))
    elif tag == 'TABLE':
        cap = rest
        para('표 캡션', cap, keyword=False)
        rows = []
        i += 1
        while lines[i].strip() != 'END':
            rows.append([c.strip() for c in lines[i].split(' | ')])
            i += 1
        key = cap.split(']')[0] + ']'
        table(rows, WIDTHS.get(key))
    if tag not in ('PAGE', 'BOX') and page_next and len(d.paragraphs) > n_before:
        page_marks.append(n_before)
        page_next = False
    i += 1
flush_box()

d.save_to_path(OUT)

# 4) 표지를 첫 쪽(쪽 나눔 문단 앞)으로 이동
z = zipfile.ZipFile(OUT)
names = z.namelist()
data = {n: z.read(n) for n in names}
HP = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
sec = etree.fromstring(data['Contents/section0.xml'])
ps = [c for c in sec if c.tag == '{%s}p' % HP]
cover = ps[cover_start:cover_end]
anchor = ps[1]  # 쪽 나눔 + 쪽 번호 1로 시작
for c in cover:
    sec.remove(c)
    anchor.addprevious(c)
TAB_LEADER = '2'   # 차례 점선 채움(한글 화면 확인용 값)
# 차례: 표지 다음 쪽(쪽 번호 1 시작 문단 앞). 쪽 번호는 원고에 적은 값(한글 화면에서 확인한 값)
if toc_start is not None:
    toc = ps[toc_start:toc_end]
    for c in toc:
        sec.remove(c)
        anchor.addprevious(c)
    toc[0].set('pageBreak', '1')
    # 차례 쪽은 쪽 번호 감춤(표지와 같은 방식)
    r0 = toc[0].find('{%s}run' % HP)
    hr = etree.Element('{%s}run' % HP, charPrIDRef=r0.get('charPrIDRef'))
    ctrl = etree.SubElement(hr, '{%s}ctrl' % HP)
    etree.SubElement(ctrl, '{%s}pageHiding' % HP, hideHeader='0', hideFooter='0', hideMasterPage='0', hideBorder='0', hideFill='0', hidePageNum='1')
    r0.addprevious(hr)
    for t in sec.iter('{%s}t' % HP):
        if t.text and '\t' in t.text:
            a, b = t.text.split('\t', 1)
            t.text = a
            tab = etree.SubElement(t, '{%s}tab' % HP, width='4000', leader=TAB_LEADER, type='2')
            tab.tail = b

# 5) 그림 원본 크기(imgDim·imgClip = 픽셀 x 75), 표 쪽 넘김 설정
from PIL import Image
import io
HC = 'http://www.hancom.co.kr/hwpml/2011/core'
bins = {}
for n in names:
    if n.startswith('BinData/'):
        key = os.path.splitext(os.path.basename(n))[0]
        bins[key] = Image.open(io.BytesIO(data[n])).size
for pic in sec.iter('{%s}pic' % HP):
    img = pic.find('{%s}img' % HC)
    w, h = bins[img.get('binaryItemIDRef')]
    W, Hh = w * 75, h * 75
    pic.find('{%s}imgDim' % HP).attrib.update({'dimwidth': str(W), 'dimheight': str(Hh)})
    pic.find('{%s}imgClip' % HP).attrib.update({'left': '0', 'right': str(W), 'top': '0', 'bottom': str(Hh)})
for tbl in sec.iter('{%s}tbl' % HP):
    if tbl.get('rowCnt') == '1' and tbl.get('colCnt') == '1':
        continue                       # 요약 상자는 build_box.py가 처리
    tbl.set('pageBreak', 'NONE')      # 나누지 않음: 쪽에 안 들어가면 통째로 다음 쪽(글자처럼 취급 유지)
    tbl.set('repeatHeader', '1')
    first_tr = tbl.find('{%s}tr' % HP)
    if tbl.find('.//{%s}tc' % HP) is not None and first_tr is not None:
        shaded = True
        for tc in first_tr.findall('{%s}tc' % HP):
            tc.set('header', '1')
    tbl.find('{%s}inMargin' % HP).attrib.update({'left': '567', 'right': '567', 'top': '283', 'bottom': '283'})
    for tc in tbl.iter('{%s}tc' % HP):
        tc.set('hasMargin', '1')
        tc.find('{%s}cellMargin' % HP).attrib.update({'left': '567', 'right': '567', 'top': '283', 'bottom': '283'})

# 7) 표 본문 행 높이 맞춤: 셀 글자 수로 줄 수를 추정해 가장 높은 행에 맞춤(머리행 제외)
import math
ROW_EQUAL = os.environ.get('ROW_EQUAL', '1') != '0'
def text_w(t, pt):                       # 글자 폭 추정(HWPUNIT)
    w = 0
    if ROW_EQUAL:                        # 기존 추정: 한글 1em, 영문·숫자 0.55em, 공백 0.3em
        for ch in t:
            if ch == ' ': w += 0.3
            elif ord(ch) < 0x1100: w += 0.55
            else: w += 1.0
        return w * pt * 100
    # 한글 2018 맑은 고딕 화면 실측(10.14): 한글 1em, 공백 0.5em, 쉼표·가운뎃점 0.33em
    for ch in t:
        if ch == ' ': w += 0.5
        elif ch in ',.·()': w += 0.33
        elif ch == '-': w += 0.4
        elif ch.isupper(): w += 0.65
        elif ord(ch) < 0x1100: w += 0.55
        else: w += 1.0
    return w * pt * 100 + 150
LINE = int(1200 * 1.30)                  # 12pt, 줄 간격 130%
for tbl in sec.iter('{%s}tbl' % HP):
    if tbl.get('rowCnt') == '1' and tbl.get('colCnt') == '1':
        continue
    rows = tbl.findall('{%s}tr' % HP)
    has_header = rows and rows[0].find('{%s}tc' % HP).get('header') == '1'
    body = rows[1:] if has_header else rows
    def need(tr):
        h = 0
        for tc in tr.findall('{%s}tc' % HP):
            w = int(tc.find('{%s}cellSz' % HP).get('width'))
            m = tc.find('{%s}cellMargin' % HP)
            inner = w - int(m.get('left')) - int(m.get('right'))
            lines = 0
            for p in tc.iter('{%s}p' % HP):
                t = ''.join(x.text or '' for x in p.iter('{%s}t' % HP))
                lines += max(1, math.ceil(text_w(t, 12) / (inner * (0.97 if ROW_EQUAL else 1.0))))
            h = max(h, lines * LINE + int(m.get('top')) + int(m.get('bottom')))
        return h
    if not body:
        continue
    H = max(need(tr) for tr in body)
    for tr in body:                      # ROW_EQUAL=0이면 행마다 추정 줄 수에 맞춤(통합본 압축, 10.14)
        h = H if ROW_EQUAL else need(tr)
        for tc in tr.findall('{%s}tc' % HP):
            tc.find('{%s}cellSz' % HP).set('height', str(h))
    total = sum(int(r.find('{%s}tc' % HP).find('{%s}cellSz' % HP).get('height')) for r in rows)
    tbl.find('{%s}sz' % HP).set('height', str(total))

# 6) 쪽 나눔 제어: 블록 묶기(다음 문단과 함께), 문단 보호, 수동 쪽 나누기
HH = 'http://www.hancom.co.kr/hwpml/2011/head'
hdr = etree.fromstring(data['Contents/header.xml'])
pps = hdr.find('.//{%s}paraProperties' % HH)
ppmap = {pp.get('id'): pp for pp in pps}
sname = {v[0]: k for k, v in ST.items()}
BODY = {'○ 본문', '- 본문', '· 본문', '※ 주석', '출처'}
CHILD = {'- 본문', '· 본문', '※ 주석', '출처'}
for name in BODY:                      # 문단 보호: 문단 안 줄을 쪽 사이로 나누지 않음
    ppmap[ST[name][1]].find('{%s}breakSetting' % HH).set('keepLines', '1')
kw_cache = {}
def keep_variant(ppid):
    if ppid not in kw_cache:
        import copy
        n = copy.deepcopy(ppmap[ppid]); nid = str(len(pps)); n.set('id', nid)
        n.find('{%s}breakSetting' % HH).set('keepWithNext', '1')
        pps.append(n); pps.set('itemCnt', str(len(pps))); ppmap[nid] = n; kw_cache[ppid] = nid
    return kw_cache[ppid]
top = [c for c in sec if c.tag == '{%s}p' % HP]
def kind(p):
    if p.find('.//{%s}tbl' % HP) is not None: return 'TABLE'
    if p.find('.//{%s}pic' % HP) is not None: return 'PIC'
    return sname.get(p.get('styleIDRef'), '')
for a, b in zip(top, top[1:]):
    ka, kb = kind(a), kind(b)
    if (ka in BODY and kb in CHILD) or ka == 'PIC' or (ka in ('TABLE', '그림 캡션') and kb in ('※ 주석', '출처')) or (ka == '○ 본문' and kb == '표 캡션'):
        a.set('paraPrIDRef', keep_variant(a.get('paraPrIDRef')))
for idx in page_marks:
    top[idx].set('pageBreak', '1')
# 절(1-2, 1-3 …)은 새 쪽에서 시작. 첫 절(1-1)은 제목·요약 상자와 같은 쪽
# SEC_NEWPAGE=0이면 절도 이어서 배치(기능도·기술서 통합본, 2026.10.14 관리자 지시)
sec_paras = [p for p in top if kind(p) == '절']
if os.environ.get('SEC_NEWPAGE', '1') != '0':
    for p in sec_paras[1:]:
        p.set('pageBreak', '1')
# 절 아래 가로선 밑 여백: 한글은 문단 아래 간격을 테두리 안쪽에 넣으므로(선이 글자에서 멀어짐),
# 절 문단의 아래 간격은 작게 두고 바로 다음 문단의 위 간격을 늘린다(10.01 관리자 지적)
GAP_BELOW_RULE = 16 * 200
gap_cache = {}
for a, b in zip(top, top[1:]):
    if kind(a) != '절':
        continue
    ppid = b.get('paraPrIDRef')
    if ppid not in gap_cache:
        import copy
        n = copy.deepcopy(ppmap[ppid]); nid = str(len(pps)); n.set('id', nid)
        for prev in n.iter('{http://www.hancom.co.kr/hwpml/2011/core}prev'):
            prev.set('value', str(int(prev.get('value')) + GAP_BELOW_RULE))
        pps.append(n); pps.set('itemCnt', str(len(pps))); ppmap[nid] = n; gap_cache[ppid] = nid
    b.set('paraPrIDRef', gap_cache[ppid])
data['Contents/header.xml'] = etree.tostring(hdr, xml_declaration=True, encoding='UTF-8', standalone=True)
data['Contents/section0.xml'] = etree.tostring(sec, xml_declaration=True, encoding='UTF-8', standalone=True)
os.remove(OUT)
with zipfile.ZipFile(OUT, 'w') as zo:
    zo.writestr(zipfile.ZipInfo('mimetype'), data['mimetype'], compress_type=zipfile.ZIP_STORED)
    for n in names:
        if n != 'mimetype' and not n.endswith('/'):
            zo.writestr(n, data[n], compress_type=zipfile.ZIP_DEFLATED)
print('done', OUT, 'paragraphs', len(ps))
