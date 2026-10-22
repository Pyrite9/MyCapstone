"""그림 한 장이 들어간 쪽만 가로 구역으로 바꾸고 그림 파일을 교체함 (10.22, 기능도 가로 쪽)
사용: python3 landscape_fig.py <빌드된.hwpx> <결과.hwpx> <그림.png> <그림 캡션 앞부분> <그림 폭 mm>
동작
- 캡션 문단 앞의 그림 문단과 그 앞 소제목 문단을 묶어 새 구역(가로)으로 떼어 냄
- 뒤 내용은 다시 세로 구역으로 시작함. 쪽 번호는 이어지고(startNum page=0), 쪽 번호 위치도 각 구역에 다시 넣음
- 그림 BinData를 새 PNG로 바꾸고 크기 값(sz, orgSz, curSz, imgRect, imgClip, imgDim)을 다시 계산함
- hwpx는 구역마다 sectionN.xml이 따로 있어야 하므로 content.hpf, header.xml(secCnt)도 고침
"""
import re
import sys
import zipfile
from PIL import Image

SRC, DST, PNG, CAP, WMM = sys.argv[1:6]
WMM = float(WMM)
MM = 283.465


def top_paras(body):
    """최상위 hp:p 문단 목록(표 안 문단은 바깥 문단에 포함)"""
    out, depth, start = [], 0, None
    for m in re.finditer(r'<hp:p\s|</hp:p>', body):
        if m.group(0).startswith('<hp:p'):
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                out.append(body[start:m.end()])
    return out


z = zipfile.ZipFile(SRC)
files = {n: z.read(n) for n in z.namelist()}
sec = files['Contents/section0.xml'].decode('utf8')
head_end = sec.find('<hp:p ')
tail_start = sec.rfind('</hs:sec>')
opening, body = sec[:head_end], sec[head_end:tail_start]
paras = top_paras(body)
assert ''.join(paras) == body, '문단 분리 실패'

cap_i = next(i for i, p in enumerate(paras) if CAP in ''.join(re.findall(r'<hp:t>([^<]*)', p)))
pic_i = cap_i - 1
assert '<hp:pic' in paras[pic_i], '캡션 앞 문단이 그림이 아님'
head_i = pic_i - 1  # 소제목
parts = [paras[:head_i], paras[head_i:cap_i + 1], paras[cap_i + 1:]]

# 첫 문단의 secPr, colPr, 쪽 번호 위치를 복사
first = paras[0]
secpr = re.search(r'<hp:secPr .*?</hp:secPr>', first, re.S).group(0)
colpr = re.search(r'<hp:ctrl><hp:colPr [^>]*/></hp:ctrl>', first).group(0)
pagenum = re.search(r'<hp:ctrl><hp:pageNum [^>]*/></hp:ctrl>', first).group(0)
assert 'landscape="WIDELY"' in secpr


def sec_run(landscape):
    s = secpr.replace('landscape="WIDELY"', 'landscape="NARROWLY"') if landscape else secpr
    s = re.sub(r'<hp:startNum [^>]*/>', '<hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/>', s)
    return f'<hp:run charPrIDRef="0">{s}{colpr}{pagenum}</hp:run>'


def open_section(p, landscape):
    p = re.sub(r'pageBreak="1"', 'pageBreak="0"', p, count=1)
    i = p.find('>') + 1  # <hp:p ...> 바로 뒤
    return p[:i] + sec_run(landscape) + p[i:]


parts[1][0] = open_section(parts[1][0], True)
parts[2][0] = open_section(parts[2][0], False)

# 그림 교체와 크기 재계산
pic = parts[1][1]
bin_id = re.search(r'binaryItemIDRef="([^"]+)"', pic).group(1)
im = Image.open(PNG)
pw, ph = im.size
w = round(WMM * MM)
h = round(w * ph / pw)
dw, dh = pw * 75, ph * 75
pic = re.sub(r'<hp:orgSz [^>]*/>', f'<hp:orgSz width="{w}" height="{h}"/>', pic)
pic = re.sub(r'<hp:curSz [^>]*/>', f'<hp:curSz width="{w}" height="{h}"/>', pic)
pic = re.sub(r'(<hp:sz )width="\d+"( [^>]*?)height="\d+"', rf'\1width="{w}"\2height="{h}"', pic)
pic = re.sub(r'centerX="\d+" centerY="\d+"', f'centerX="{w // 2}" centerY="{h // 2}"', pic)
pic = re.sub(r'<hp:imgRect>.*?</hp:imgRect>',
             f'<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="{w}" y="0"/><hc:pt2 x="{w}" y="{h}"/>'
             f'<hc:pt3 x="0" y="{h}"/></hp:imgRect>', pic, flags=re.S)
pic = re.sub(r'<hp:imgClip [^>]*/>', f'<hp:imgClip left="0" right="{dw}" top="0" bottom="{dh}"/>', pic)
pic = re.sub(r'<hp:imgDim [^>]*/>', f'<hp:imgDim dimwidth="{dw}" dimheight="{dh}"/>', pic)
parts[1][1] = pic
bin_name = next(n for n in files if n.startswith('BinData/') and n.split('/')[-1].split('.')[0] == bin_id)
files[bin_name] = open(PNG, 'rb').read()

# 구역 파일 3개
for k, ps in enumerate(parts):
    files[f'Contents/section{k}.xml'] = (opening + ''.join(ps) + '</hs:sec>').encode('utf8')

hpf = files['Contents/content.hpf'].decode('utf8')
item0 = re.search(r'<opf:item id="section0"[^>]*/>', hpf).group(0)
ref0 = re.search(r'<opf:itemref idref="section0"[^>]*/>', hpf).group(0)
items = item0 + ''.join(item0.replace('section0', f'section{k}') for k in (1, 2))
refs = ref0 + ''.join(ref0.replace('section0', f'section{k}') for k in (1, 2))
hpf = hpf.replace(item0, items).replace(ref0, refs)
files['Contents/content.hpf'] = hpf.encode('utf8')
rdf = files['META-INF/container.rdf'].decode('utf8')
d0 = ('<rdf:Description rdf:about=""><ns0:hasPart xmlns:ns0="http://www.hancom.co.kr/hwpml/2016/meta/pkg#" '
      'rdf:resource="Contents/section0.xml"/></rdf:Description><rdf:Description rdf:about="Contents/section0.xml">'
      '<rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#SectionFile"/></rdf:Description>')
assert d0 in rdf, 'container.rdf 형식이 다름'
rdf = rdf.replace(d0, d0 + ''.join(d0.replace('section0', f'section{k}') for k in (1, 2)))
files['META-INF/container.rdf'] = rdf.encode('utf8')
hdr = files['Contents/header.xml'].decode('utf8')
files['Contents/header.xml'] = re.sub(r'secCnt="\d+"', 'secCnt="3"', hdr).encode('utf8')

order = ['mimetype'] + [n for n in z.namelist() if n != 'mimetype']
order += [n for n in files if n not in order]
with zipfile.ZipFile(DST, 'w') as o:
    for n in order:
        ct = zipfile.ZIP_STORED if n == 'mimetype' else zipfile.ZIP_DEFLATED
        o.writestr(zipfile.ZipInfo(n), files[n], compress_type=ct)
print(f'landscape section: paras {head_i}..{cap_i}, picture {w}x{h} HWPUNIT ({WMM}mm), png {pw}x{ph}')
