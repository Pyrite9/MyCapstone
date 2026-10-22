"""그림 1 업무 기능도 v1.3 — 가로 쪽용 위에서 아래로 내려가는 트리 (SVG 원본 + PNG)
- 10.15 발표 피드백: 단위 업무는 상자 하나씩 나누지 않고 기능 아래 한 상자에 모아 가운뎃점으로 표시
- 10.22 관리자: 이 그림에 한해 문서 디자인 제한(흑백 등)을 풀고 가독성 요소를 넣음
  영역별 색, 기능 카드(머리: 기능 이름·기능 ID·구현 단계 배지, 몸: 단위 업무), 단계 범례
- 기능 ID와 구현 단계는 작업 원고 [표 1]에서 읽음(그림과 표가 어긋나지 않게)
단위 mm. 사용: python3 fig2_1_tree_land.py [작업원고.txt]  → fig2-1_tree.svg, fig2-1_tree.png(400dpi)
"""
import asyncio
import glob
import os
import sys
from PIL import ImageFont
from fig2_1_tree import OUTLINE
from tree_form import parse

HERE = os.path.dirname(os.path.abspath(__file__))
PT = 25.4 / 72
FS = 9 * PT            # 기능·단위 업무
FS_AREA = 9.5 * PT     # 영역
FS_META = 7.5 * PT     # 기능 ID, 배지, 범례
W = 254.2              # 내용 폭, 바깥 여유 0.4mm씩 더해 255mm
GAP_COL, N_COL = 3.5, 6
COL_W = (W - GAP_COL * (N_COL - 1)) / N_COL
ROOT_W, ROOT_H, AREA_H, BUS = 44.0, 8.5, 8.0, 6.0
SPINE_IN, CARD_IN = 2.6, 5.6
HEAD_H = 9.8                      # 카드 머리(이름 줄 + ID·배지 줄)
LEAF_PITCH, LEAF_PAD = 4.2, 1.6
GROUP_GAP, TOP_GAP = 2.8, 3.5
R = 1.3                            # 모서리
INK, SUB = '#1F2328', '#5B6470'

# 영역 색(진한 색: 영역 머리·선·카드 테두리 / 연한 색: 카드 머리)
PALETTE = {
    '회원 관리': ('#3E5C86', '#E3EAF4'),
    '과제 관리': ('#2F7566', '#DFEFEA'),
    '조 운영':   ('#946A1E', '#F5ECDA'),
    '과정 기록': ('#A1452E', '#F6E2DC'),
    '동료평가':  ('#6B4C93', '#ECE5F4'),
    '교수 열람': ('#4F5B66', '#E6E9EC'),
}
# 기능은 1단계지만 단위 업무만 뒤 단계인 것([표 1] ※ 둘째 줄과 같게 유지)
LEAF_STAGE = {'역할 변경': '2단계', '산출물 삭제': '2단계', '임시 저장': '2단계'}
STAGE_TEXT = {'1단계': '2026.12.11', '2단계': '2026.12.12 ~ 2027.02', '3단계': '2027.03 최종 종료'}

F = {k: f'/usr/share/fonts/opentype/noto/NotoSansCJK-{k}.ttc' for k in ('Regular', 'Medium', 'Bold')}
WEIGHT = {'Regular': 400, 'Medium': 500, 'Bold': 700}


def text_w(s, size, face='Regular'):
    return ImageFont.truetype(F[face], 1000, index=1).getlength(s) / 1000 * size


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;')


def read_table1(path):
    """작업 원고 [표 1]: 기능 이름 → (기능 ID, 구현 단계)"""
    lines = open(path, encoding='utf8').read().splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith('TABLE [표 1]')) + 2
    out = {}
    while lines[i].strip() != 'END':
        c = [x.strip() for x in lines[i].split(' | ')]
        out[c[1]] = (c[0], c[4])
        i += 1
    return out


def build(table1):
    root = parse(OUTLINE)
    areas = root['kids']
    assert len(areas) == N_COL
    out, worst = [], 0.0

    def fit(s, size, face, room):
        nonlocal worst
        worst = max(worst, text_w(s, size, face) / room)

    def rect(x, y, w, h, fill='none', stroke='none', sw=0.3, rx=R, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" '
                   f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def top_round(x, y, w, h, fill):
        out.append(f'<path d="M{x:.2f},{y + h:.2f} V{y + R:.2f} Q{x:.2f},{y:.2f} {x + R:.2f},{y:.2f} '
                   f'H{x + w - R:.2f} Q{x + w:.2f},{y:.2f} {x + w:.2f},{y + R:.2f} V{y + h:.2f} Z" fill="{fill}"/>')

    def line(x1, y1, x2, y2, color=INK, sw=0.35):
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                   f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')

    def text(x, y, s, size=FS, face='Regular', color=INK, anchor='middle'):
        out.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size:.3f}" font-weight="{WEIGHT[face]}" '
                   f'fill="{color}" text-anchor="{anchor}" dominant-baseline="central">{esc(s)}</text>')

    def badge(x_right, cy, stage, color, w=10.2, h=3.7):
        x = x_right - w
        if stage == '1단계':
            rect(x, cy - h / 2, w, h, fill=color, rx=h / 2)
            text(x + w / 2, cy, stage, FS_META, 'Bold', '#FFFFFF')
        else:
            rect(x, cy - h / 2, w, h, fill='#FFFFFF', stroke=color, sw=0.3, rx=h / 2,
                 dash='0.9 0.6' if stage == '3단계' else None)
            text(x + w / 2, cy, stage, FS_META, 'Medium', color)

    # 최상위와 연결선
    rx0 = (W - ROOT_W) / 2
    rect(rx0, 0.3, ROOT_W, ROOT_H, fill=INK, rx=R)
    text(W / 2, 0.3 + ROOT_H / 2, root['name'], 10.5 * PT, 'Bold', '#FFFFFF')
    y_bus = 0.3 + ROOT_H + BUS / 2
    y_area = 0.3 + ROOT_H + BUS
    xs = [i * (COL_W + GAP_COL) for i in range(N_COL)]
    line(W / 2, 0.3 + ROOT_H, W / 2, y_bus, sw=0.45)
    line(xs[0] + COL_W / 2, y_bus, xs[-1] + COL_W / 2, y_bus, sw=0.45)

    bottoms = []
    for a, x in zip(areas, xs):
        dark, light = PALETTE[a['name']]
        cx = x + COL_W / 2
        line(cx, y_bus, cx, y_area, sw=0.45)
        rect(x, y_area, COL_W, AREA_H, fill=dark)
        text(cx, y_area + AREA_H / 2, a['name'], FS_AREA, 'Bold', '#FFFFFF')
        fit(a['name'], FS_AREA, 'Bold', COL_W - 3)

        y = y_area + AREA_H + TOP_GAP
        sx, cxl, cw = x + SPINE_IN, x + CARD_IN, COL_W - CARD_IN
        last_mid = None
        for j, f in enumerate(a['kids']):
            if j:
                y += GROUP_GAP
            fid, stage = table1[f['name']]
            leaves = ['· ' + k['name'] for k in f['kids']]
            body_h = LEAF_PAD * 2 + LEAF_PITCH * len(leaves)
            card_h = HEAD_H + body_h
            rect(cxl, y, cw, card_h, fill='#FFFFFF')
            top_round(cxl, y, cw, HEAD_H, light)
            line(cxl, y + HEAD_H, cxl + cw, y + HEAD_H, dark, 0.25)
            rect(cxl, y, cw, card_h, stroke=dark, sw=0.35)
            text(cxl + 2.0, y + 3.3, f['name'], FS, 'Bold', dark, 'start')
            fit(f['name'], FS, 'Bold', cw - 3.5)
            text(cxl + 2.0, y + 7.3, fid, FS_META, 'Medium', SUB, 'start')
            badge(cxl + cw - 1.6, y + 7.3, stage, dark)
            for k, s in enumerate(leaves):
                ly_ = y + HEAD_H + LEAF_PAD + LEAF_PITCH * (k + 0.5)
                late = LEAF_STAGE.get(s[2:])
                text(cxl + 2.2, ly_, s, FS, 'Regular', SUB if late else INK, 'start')
                if late:
                    badge(cxl + cw - 1.6, ly_, late, dark, w=9.2, h=3.3)
                fit(s, FS, 'Regular', cw - 3.4 - (11 if late else 0))
            line(sx, y + 3.3, cxl, y + 3.3, dark, 0.35)
            last_mid = y + 3.3
            y += card_h
        line(sx, y_area + AREA_H, sx, last_mid, dark, 0.35)
        bottoms.append(y)

    # 범례: 가장 짧은 두 열이 이어진 자리(동료평가·교수 열람)
    lx = xs[4]
    lw = COL_W * 2 + GAP_COL
    ly = max(bottoms[4], bottoms[5]) + 7.0
    lh = 3 * 5.0 + 7.2
    rect(lx, ly, lw, lh, fill='#FAFAFA', stroke='#B8BEC6', sw=0.25)
    text(lx + 2.5, ly + 3.6, '구현 단계', FS_META + 0.2, 'Bold', INK, 'start')
    for k, st in enumerate(('1단계', '2단계', '3단계')):
        cy = ly + 8.6 + 5.0 * k
        badge(lx + 2.5 + 10.2, cy, st, INK)
        text(lx + 15.5, cy, STAGE_TEXT[st], FS_META + 0.3, 'Regular', INK, 'start')
    H = max(max(bottoms), ly + lh) + 0.4
    assert worst < 1.0, f'글자가 상자보다 넓음 ({worst:.2f})'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W + 0.8}mm" height="{H:.2f}mm" '
           f'viewBox="-0.4 0 {W + 0.8} {H:.2f}" font-family="Noto Sans CJK KR, sans-serif">'
           f'<rect x="-0.4" y="0" width="{W + 0.8}" height="{H:.2f}" fill="#FFFFFF"/>' + ''.join(out) + '</svg>')
    return svg, H, worst


async def to_png(svg_path, png_path, w_mm, h_mm, dpi=400):
    from playwright.async_api import async_playwright
    px_w, px_h = round(w_mm / 25.4 * dpi), round(h_mm / 25.4 * dpi)
    svg = open(svg_path, encoding='utf8').read().replace(
        f'width="{w_mm}mm" height="{h_mm:.2f}mm"', f'width="{px_w}" height="{px_h}"', 1)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': px_w, 'height': px_h})
        await pg.set_content(f'<html><body style="margin:0;background:#fff">{svg}</body></html>')
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=png_path)
        await b.close()
    return px_w, px_h


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else sorted(
        glob.glob(os.path.join(HERE, '..', '원고', '기능도기술서_작업원고_v*.txt')))[-1]
    svg, H, worst = build(read_table1(src))
    sp = os.path.join(HERE, 'fig2-1_tree.svg')
    open(sp, 'w', encoding='utf8').write(svg)
    pw, ph = asyncio.run(to_png(sp, os.path.join(HERE, 'fig2-1_tree.png'), W + 0.8, H))
    print(f'원고 {os.path.basename(src)}, size {W + 0.8:.1f}x{H:.1f}mm, png {pw}x{ph}, 글자 폭 최대 {worst:.0%}')
