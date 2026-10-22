"""그림 1 업무 기능도 v1.3 — 가로 쪽용 위에서 아래로 내려가는 트리 (SVG 원본 + PNG)
10.15 발표 피드백: 단위 업무를 상자 하나씩 나누지 않고 기능 아래 큰 상자 하나에 모아 표시함.
단위 mm, 글자 9pt. 문서 가로 쪽 본문 폭 257mm 안에 들어가도록 폭 255mm로 그림.
사용: python3 fig2_1_tree_land.py  → fig2-1_tree.svg, fig2-1_tree.png(400dpi)
"""
import asyncio
import os
from PIL import ImageFont
from fig2_1_tree import OUTLINE
from tree_form import parse

HERE = os.path.dirname(os.path.abspath(__file__))
PT = 25.4 / 72                      # 1pt = mm
FS = 9 * PT                         # 글자 9pt
W = 254.2                           # 그림 안 내용 폭(mm), 바깥 선 여유 0.4mm씩 더해 255mm
GAP_COL = 3.5                       # 열 사이
N_COL = 6
COL_W = (W - GAP_COL * (N_COL - 1)) / N_COL
ROOT_W, BOX_H = 40.0, 7.5           # 최상위·영역 상자
FN_H = 6.6                          # 기능 상자 높이
SPINE_IN, FN_IN = 2.5, 5.5          # 세로줄 위치, 기능 상자 들여쓰기
LINK = 1.8                          # 기능 상자와 단위 업무 상자 사이
LEAF_PITCH, LEAF_PAD = 4.5, 1.5     # 단위 업무 줄 간격, 위아래 여백
GROUP_GAP = 3.0                     # 기능 묶음 사이
BUS = 6.0                           # 최상위 상자와 영역 상자 사이
SW_THICK, SW = 0.5, 0.3             # 선 굵기

FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT_B = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'


def text_w(s, bold=False):
    f = ImageFont.truetype(FONT_B if bold else FONT, 1000, index=1)  # index 1 = KR
    return f.getlength(s) / 1000 * FS


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;')


def build():
    root = parse(OUTLINE)
    areas = root['kids']
    assert len(areas) == N_COL
    out, H = [], 0.0

    def rect(x, y, w, h, sw=SW, fill='#FFFFFF'):
        out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
                   f'fill="{fill}" stroke="#000" stroke-width="{sw}"/>')

    def line(x1, y1, x2, y2, sw=SW):
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                   f'stroke="#000" stroke-width="{sw}" stroke-linecap="square"/>')

    def text(x, y, s, anchor='middle', bold=False):
        out.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{FS:.3f}" text-anchor="{anchor}" '
                   f'dominant-baseline="central" font-weight="{700 if bold else 400}">{esc(s)}</text>')

    # 최상위
    rx = (W - ROOT_W) / 2
    rect(rx, 0.3, ROOT_W, BOX_H, SW_THICK)
    text(W / 2, 0.3 + BOX_H / 2, root['name'], bold=True)
    y_bus = 0.3 + BOX_H + BUS / 2
    y_area = 0.3 + BOX_H + BUS
    line(W / 2, 0.3 + BOX_H, W / 2, y_bus)
    xs = [i * (COL_W + GAP_COL) for i in range(N_COL)]
    line(xs[0] + COL_W / 2, y_bus, xs[-1] + COL_W / 2, y_bus)

    worst = 0.0
    for a, x in zip(areas, xs):
        cx = x + COL_W / 2
        line(cx, y_bus, cx, y_area)
        rect(x, y_area, COL_W, BOX_H, SW_THICK, '#E6E6E6')
        text(cx, y_area + BOX_H / 2, a['name'], bold=True)
        worst = max(worst, text_w(a['name'], True) / (COL_W - 2))
        y = y_area + BOX_H + 4.0
        spine_x = x + SPINE_IN
        fx, fw = x + FN_IN, COL_W - FN_IN
        last_mid = None
        for j, f in enumerate(a['kids']):
            if j:
                y += GROUP_GAP
            rect(fx, y, fw, FN_H)
            text(fx + fw / 2, y + FN_H / 2, f['name'])
            worst = max(worst, text_w(f['name']) / (fw - 2))
            line(spine_x, y + FN_H / 2, fx, y + FN_H / 2)
            last_mid = y + FN_H / 2
            y += FN_H
            leaves = ['· ' + k['name'] for k in f['kids']]  # 최하위 항목만 가운뎃점
            line(fx + fw / 2, y, fx + fw / 2, y + LINK)
            y += LINK
            lh = LEAF_PAD * 2 + LEAF_PITCH * len(leaves)
            rect(fx, y, fw, lh)
            for k, s in enumerate(leaves):
                text(fx + 2.2, y + LEAF_PAD + LEAF_PITCH * (k + 0.5), s, anchor='start')
                worst = max(worst, text_w(s) / (fw - 3.2))
            y += lh
        line(spine_x, y_area + BOX_H, spine_x, last_mid)
        H = max(H, y)
    H += 0.4
    assert worst < 1.0, f'글자가 상자보다 넓음 ({worst:.2f})'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W + 0.8}mm" height="{H:.2f}mm" '
           f'viewBox="-0.4 0 {W + 0.8} {H:.2f}" preserveAspectRatio="none" font-family="Noto Sans CJK KR, sans-serif">'
           f'<rect width="100%" height="100%" fill="#FFFFFF"/>' + ''.join(out) + '</svg>')
    return svg, H, worst


async def to_png(svg_path, png_path, w_mm, h_mm, dpi=400):
    from playwright.async_api import async_playwright
    px_w, px_h = round(w_mm / 25.4 * dpi), round(h_mm / 25.4 * dpi)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': px_w, 'height': px_h})
        svg = open(svg_path, encoding='utf8').read().replace(
            f'width="{w_mm}mm" height="{h_mm:.2f}mm"', f'width="{px_w}" height="{px_h}"', 1)
        html = f'<html><body style="margin:0;background:#fff">{svg}</body></html>'
        await pg.set_content(html)
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=png_path, full_page=False)
        await b.close()
    return px_w, px_h


if __name__ == '__main__':
    svg, H, worst = build()
    sp = os.path.join(HERE, 'fig2-1_tree.svg')
    open(sp, 'w', encoding='utf8').write(svg)
    pw, ph = asyncio.run(to_png(sp, os.path.join(HERE, 'fig2-1_tree.png'), W + 0.8, H))
    print(f'size {W + 0.8}x{H:.1f}mm, png {pw}x{ph}, 글자 폭 최대 {worst:.0%}')
