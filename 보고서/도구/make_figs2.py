# v6.3 그림 재작성: 1-1(image3), 1-3(image2), 1-4(image4), 1-6(image7)
# 원칙: 그림 폭 6.5in = 문서 165mm 이므로 글자 pt가 인쇄 크기와 같음(본문 9pt 이상)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle

REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
fm.fontManager.addfont(REG); fm.fontManager.addfont(BOLD)
plt.rcParams['font.family'] = 'Noto Sans CJK JP'
NAVY, NAVY_D, BROWN, GRID, MUTED, LANE = '#3b3a5c', '#2b2a3d', '#9c8b72', '#d9d9de', '#6b6b78', '#f3f0eb'
DPI = 300


def canvas(w, h):
    fig = plt.figure(figsize=(w, h), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, text, fc='white', ec=NAVY_D, tc=NAVY_D, fs=9.5, lw=1.3, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.03', fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, color=tc,
            fontweight='bold' if bold else 'normal', linespacing=1.35)


def arrow(ax, pts, color=NAVY_D, label=None, lpos=None, ls='-'):
    xs, ys = zip(*pts)
    ax.plot(xs[:-1] + (xs[-1],), ys, color=color, lw=1.1, ls=ls, solid_capstyle='butt')
    ax.annotate('', xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle='-|>', color=color, lw=1.1, mutation_scale=9, shrinkA=0, shrinkB=0))
    if label:
        ax.text(*lpos, label, fontsize=8.5, color=BROWN, ha='center', va='bottom')


# ---------- 그림 1-1 사용 흐름 ----------
W, H = 6.5, 4.75
fig, ax = canvas(W, H)
lanes = ['교수', '조장', '조원']
lw_ = W / 3
for k, name in enumerate(lanes):
    ax.add_patch(Rectangle((k * lw_, 0), lw_, H, fc=LANE if k != 1 else 'white', ec='#dcd6cd', lw=0.8))
    ax.text(k * lw_ + lw_ / 2, 0.28, name, ha='center', va='center', fontsize=11, fontweight='bold', color=NAVY_D)
bw, bh = 1.7, 0.46
cx = [lw_ * (k + 0.5) for k in range(3)]
rows = [0.55, 1.18, 1.81, 2.44, 3.07, 3.70, 4.15]
def B(col, row, text):
    box(ax, cx[col] - bw / 2, rows[row], bw, bh, text)
    return cx[col], rows[row]
B(0, 0, '과제 생성, 조장 지정')
B(1, 1, '조원 초대, 역할 배정')
B(1, 2, '기여 항목 등록\n담당자 지정')
B(2, 2, '산출물 업로드')
B(2, 3, '담당자의 완료 보고')
B(2, 4, '다른 조원의 완료확인')
B(2, 5, '동료평가 입력\n근거 패널 참고')
B(0, 6, '근거 기록, 평가 결과 열람')
top = lambda r: rows[r]; bot = lambda r: rows[r] + bh; mid = lambda r: rows[r] + bh / 2
arrow(ax, [(cx[0], bot(0)), (cx[0], mid(1)), (cx[1] - bw / 2, mid(1))])
arrow(ax, [(cx[1], bot(1)), (cx[1], top(2))])
arrow(ax, [(cx[1] + bw / 2, mid(1)), (cx[2], mid(1)), (cx[2], top(2))], label='초대 링크로 합류', lpos=((cx[1] + bw / 2 + cx[2]) / 2, mid(1) - 0.04))
arrow(ax, [(cx[1], bot(2)), (cx[1], mid(3)), (cx[2] - bw / 2, mid(3))])
arrow(ax, [(cx[2], bot(2)), (cx[2], top(3))])
arrow(ax, [(cx[2], bot(3)), (cx[2], top(4))])
arrow(ax, [(cx[2], bot(4)), (cx[2], top(5))])
ax.text(cx[2] - 0.08, (bot(4) + top(5)) / 2, '과제 종료 후', fontsize=8.5, color=BROWN, ha='right', va='center')
arrow(ax, [(cx[2], bot(5)), (cx[2], mid(6)), (cx[0] + bw / 2, mid(6))])
fig.savefig('image3.png', facecolor='white'); plt.close(fig)

# ---------- 그림 1-3 조별과제 실태 ----------
labels = ['무임승차자 경험', '조별과제 비선호', '한 학기 조별과제 3개 이상 수행',
          '가장 어려운 점: 업무 배분', '무임승차자에 대한 조치 없음*']
vals = [89, 80, 60, 43, 42]
fig, ax = plt.subplots(figsize=(6.5, 2.7), dpi=DPI)
y = list(range(len(vals)))[::-1]
ax.barh(y, vals, height=0.55, color=NAVY)
for yi, v in zip(y, vals):
    ax.text(v + 1.2, yi, f'{v}%', va='center', fontsize=9.5, color=NAVY_D)
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=9.5, color=NAVY_D)
ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(['0', '25', '50', '75', '100%'], fontsize=8.5, color=MUTED)
ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ['top', 'right', 'left']:
    ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(GRID); ax.tick_params(axis='both', length=0)
fig.text(0.99, 0.95, '수도권 4년제 대학생 225명, 2012.05.31 ~ 2012.06.18 조사', fontsize=8.5, color=MUTED, ha='right')
fig.text(0.01, 0.02, '* 무임승차자를 경험한 학생 기준', fontsize=8.5, color=MUTED)
fig.subplots_adjust(left=0.36, right=0.96, top=0.88, bottom=0.14)
fig.savefig('image2.png', facecolor='white'); plt.close(fig)

# ---------- 그림 1-4 기록이 근거가 되는 과정 ----------
W, H = 6.5, 2.15
fig, ax = canvas(W, H)
bw, bh = 1.0, 0.52
xs = [0.78, 1.98, 3.18, 4.38]
y1, y2 = 0.35, 1.35
ax.text(0.05, y1 + bh / 2, '산출물', fontsize=10, fontweight='bold', color=BROWN, va='center')
ax.text(0.05, y2 + bh / 2, '기여 항목', fontsize=10, fontweight='bold', color=BROWN, va='center')
top_row = ['업로드 v1', '업로드 v2', '최신 버전 v3\n목록 맨 위 표시']
bot_row = ['조장의 등록\n담당자 지정', '담당자의\n완료 보고', '다른 조원의\n완료확인', '추가 확인\n누적']
for x, t in zip(xs, top_row):
    box(ax, x, y1, bw, bh, t, fs=9)
for x, t in zip(xs, bot_row):
    box(ax, x, y2, bw, bh, t, fs=9)
for a, b, lab in [(0, 1, '다시 업로드'), (1, 2, '다시 업로드')]:
    arrow(ax, [(xs[a] + bw, y1 + bh / 2), (xs[b], y1 + bh / 2)], label=lab, lpos=((xs[a] + bw + xs[b]) / 2, y1 - 0.02))
for a, b, lab in [(0, 1, None), (1, 2, None), (2, 3, None)]:
    arrow(ax, [(xs[a] + bw, y2 + bh / 2), (xs[b], y2 + bh / 2)], label=lab, lpos=((xs[a] + bw + xs[b]) / 2, y2 + bh / 2 - 0.05) if lab else None)
px, pw, ph = 5.55, 0.9, 0.75
py = (y1 + y2 + bh) / 2 - ph / 2
box(ax, px, py, pw, ph, '근거 패널\n종류별 표시', fc=NAVY_D, ec=NAVY_D, tc='white', fs=9.5, bold=True)
jx = 5.4
ax.plot([xs[2] + bw, jx, jx], [y1 + bh / 2, y1 + bh / 2, py + ph / 2], color=NAVY_D, lw=1.1)
ax.plot([xs[3] + bw, jx, jx], [y2 + bh / 2, y2 + bh / 2, py + ph / 2], color=NAVY_D, lw=1.1)
arrow(ax, [(jx, py + ph / 2), (px, py + ph / 2)])
fig.savefig('image4.png', facecolor='white'); plt.close(fig)

# ---------- 그림 1-6 엔티티 관계도 ----------
ENT = {
    '회원': ['id PK', 'email UK(g.yju.ac.kr)', 'name', 'type(학생/교수)', 'password_hash', 'created_at'],
    '과제': ['id PK', 'professor_id FK(회원)', 'title', 'start_date', 'end_date', 'status'],
    '조': ['id PK', 'assignment_id FK(과제)', 'leader_id FK(회원)', 'name', 'invite_code'],
    '산출물': ['id PK', 'team_member_id FK(조 참여)', 'file_name', 'file_key(MinIO)', 'file_size', 'version', 'uploaded_at(서버 시각)'],
    '조 참여': ['id PK', 'team_id FK(조)', 'member_id FK(회원)', 'role_name', 'joined_at', 'UK(team_id, member_id)'],
    '기여 항목': ['id PK', 'team_id FK(조)', 'name', 'assignee_id FK(조 참여)', 'created_by FK(조 참여)', 'reported_at'],
    '평가': ['id PK', 'team_id FK(조)', 'evaluator_id FK(조 참여)', 'target_id FK(조 참여)', 's1~s6 점수(1~5점)', 'comment(선택)', 'submitted_at', 'UK(evaluator_id, target_id)'],
    '완료확인': ['id PK', 'target_type(산출물/기여 항목)', 'target_id', 'confirmer_id FK(조 참여)', 'confirmed_at(서버 시각)'],
}
LATER = {'기여 항목', '완료확인'}
GRIDPOS = {'회원': (0, 0), '과제': (1, 0), '조': (2, 0), '산출물': (0, 1), '조 참여': (1, 1), '기여 항목': (2, 1),
           '평가': (1, 2), '완료확인': (2, 2)}
W = 6.5
cw, gap, x0 = 1.8, 0.45, 0.07
HEAD, LH = 0.27, 0.185
row_y = [0.42, 2.17, 4.07]
rowh = {}
H = 6.95
fig, ax = canvas(W, H)
pos = {}
for name, (c, r) in GRIDPOS.items():
    x = x0 + c * (cw + gap); y = row_y[r]
    h = HEAD + LH * len(ENT[name]) + 0.08
    col = BROWN if name in LATER else NAVY_D
    ax.add_patch(Rectangle((x, y), cw, h, fc='white', ec=col, lw=1.1))
    ax.add_patch(Rectangle((x, y), cw, HEAD, fc=col, ec=col, lw=1.1))
    ax.text(x + 0.08, y + HEAD / 2, name, color='white', fontsize=9.5, fontweight='bold', va='center')
    for k, f in enumerate(ENT[name]):
        ax.text(x + 0.08, y + HEAD + 0.04 + LH * (k + 0.5), f, fontsize=7.8, va='center',
                color=MUTED if f.startswith('UK(') else NAVY_D, fontweight='bold' if f == 'id PK' else 'normal')
    pos[name] = (x, y, cw, h)

def L(pts, label=None, lp=None, ha='left', dashed=False, color=NAVY_D):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=0.9, ls=(0, (3, 2)) if dashed else '-')
    if label:
        ax.text(*lp, label, fontsize=7.3, color=BROWN, ha=ha, va='bottom')

X = lambda n: pos[n][0]; Y = lambda n: pos[n][1]; R = lambda n: pos[n][0] + cw; B_ = lambda n: pos[n][1] + pos[n][3]
# 회원-과제(교수 1:N), 과제-조(1:N)
L([(R('회원'), Y('회원') + 0.6), (X('과제'), Y('과제') + 0.6)], '교수\n1:N', (R('회원') + gap / 2, Y('회원') + 0.58), ha='center')
L([(R('과제'), Y('과제') + 0.6), (X('조'), Y('조') + 0.6)], '1:N', (R('과제') + gap / 2, Y('과제') + 0.58), ha='center')
# 회원-조(조장 1:N): 위쪽으로 우회
L([(X('회원') + 0.4, Y('회원')), (X('회원') + 0.4, 0.2), (X('조') + 0.4, 0.2), (X('조') + 0.4, Y('조'))], '조장 1:N', (X('과제') + cw / 2, 0.19), ha='center')
# 회원-조 참여(1:N)
mx = R('회원') + gap / 2
L([(R('회원'), B_('회원') - 0.2), (mx, B_('회원') - 0.2), (mx, Y('조 참여') + 0.45), (X('조 참여'), Y('조 참여') + 0.45)], '1:N', (mx + 0.04, (B_('회원') + Y('조 참여')) / 2 + 0.05))
# 조-조 참여(1:N)
my = (B_('조') + Y('조 참여')) / 2 + 0.05
L([(X('조') + 0.3, B_('조')), (X('조') + 0.3, my), (X('조 참여') + cw / 2, my), (X('조 참여') + cw / 2, Y('조 참여'))], '1:N', (X('조 참여') + cw / 2 + 0.05, my + 0.17))
# 조-기여 항목(1:N)
L([(X('기여 항목') + 1.3, B_('조')), (X('기여 항목') + 1.3, Y('기여 항목'))], '1:N', (X('기여 항목') + 1.35, Y('기여 항목') - 0.08))
# 조 참여-산출물(담당자 1:N)
L([(X('조 참여'), Y('조 참여') + 0.95), (R('산출물'), Y('조 참여') + 0.95)], '담당자\n1:N', (R('산출물') + gap / 2, Y('조 참여') + 0.93), ha='center')
# 조 참여-기여 항목(담당자 1:N)
L([(R('조 참여'), Y('조 참여') + 0.6), (X('기여 항목'), Y('조 참여') + 0.6)], '담당자\n1:N', (R('조 참여') + gap / 2, Y('조 참여') + 0.58), ha='center')
# 조 참여-평가(평가자·대상 1:N)
L([(X('평가') + 0.6, B_('조 참여')), (X('평가') + 0.6, Y('평가'))], '평가자 1:N', (X('평가') + 0.55, Y('평가') - 0.12), ha='right')
L([(X('평가') + 1.25, B_('조 참여')), (X('평가') + 1.25, Y('평가'))], '대상 1:N', (X('평가') + 1.3, Y('평가') - 0.12))
# 조 참여-완료확인(확인자 1:N)
gx = R('조 참여') + gap / 2
L([(R('조 참여'), B_('조 참여') - 0.15), (gx, B_('조 참여') - 0.15), (gx, Y('완료확인') + 0.6), (X('완료확인'), Y('완료확인') + 0.6)], '확인자 1:N', (gx + 0.05, Y('완료확인') - 0.08))
# 완료확인 대상(점선)
L([(X('완료확인') + 1.3, B_('기여 항목')), (X('완료확인') + 1.3, Y('완료확인'))], '대상 1:N', (X('완료확인') + 1.35, Y('완료확인') - 0.08), dashed=True)
by = max(B_('평가'), B_('완료확인')) + 0.12
L([(X('산출물') + cw / 2, B_('산출물')), (X('산출물') + cw / 2, by), (X('완료확인') + cw / 2, by), (X('완료확인') + cw / 2, B_('완료확인'))], '산출물 1:N 완료확인', (X('평가') + cw / 2, by + 0.2), ha='center', dashed=True)
# 범례: 맨 아래 한 줄
ly = by + 0.45
items = [(NAVY_D, '2026.12.11 시연에 필요한 엔티티', False), (BROWN, '2026.12.12 이후 추가할 엔티티', False),
         (NAVY_D, '완료확인 대상 참조', True), (None, 's1~s6: [표 1-6]의 6개 항목 점수', False)]
for k, (c, t, dash) in enumerate(items):
    lx = 0.07 + (k % 2) * 3.25; yy = ly + (k // 2) * 0.27
    if c is not None:
        if dash:
            ax.plot([lx, lx + 0.25], [yy, yy], color=c, lw=0.9, ls=(0, (3, 2)))
        else:
            ax.add_patch(Rectangle((lx, yy - 0.06), 0.25, 0.12, fc=c, ec=c))
    ax.text(lx + 0.33, yy, t, fontsize=7.8, va='center', color=NAVY_D)
fig.savefig('image7.png', facecolor='white'); plt.close(fig)
print('saved')
