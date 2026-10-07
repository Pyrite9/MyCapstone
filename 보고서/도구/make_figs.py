# 개요서 그림 1-1, 1-2 재작성 (축약어 제거, 명사형 문구)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
fm.fontManager.addfont(REG); fm.fontManager.addfont(BOLD)
plt.rcParams['font.family'] = 'Noto Sans CJK JP'  # ttc 공용 이름, 한글 글리프 동일
NAVY, NAVY_D, BROWN, GRID, MUTED = '#3b3a5c', '#2b2a3d', '#9c8b72', '#d9d9de', '#6b6b78'

# ---------- 그림 1-2 ----------
labels = ['무임승차자 경험', '팀 프로젝트 비선호', '한 학기 팀 프로젝트 3개 이상 수행',
          '최대 애로 사항: 업무 배분', '무임승차자에 대한 조치 없음*']
vals = [89, 80, 60, 43, 42]
fig, ax = plt.subplots(figsize=(8.8, 3.96), dpi=200)
y = range(len(vals))[::-1]
ax.barh(list(y), vals, height=0.55, color=NAVY)
for yi, v in zip(y, vals):
    ax.text(v + 1.2, yi, f'{v}%', va='center', fontsize=12.5, color=NAVY_D)
ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=12.5, color=NAVY_D)
ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(['0', '25', '50', '75', '100%'], fontsize=10.5, color=MUTED)
ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ['top', 'right', 'left']:
    ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(GRID)
ax.tick_params(axis='both', length=0)
fig.suptitle('대학생 팀 프로젝트 실태(수도권 4년제 대학생 225명)', fontsize=15, fontweight='bold', color=NAVY_D, x=0.56, y=0.97)
fig.text(0.01, 0.025, '자료: 대학내일20대연구소, 2012.05.31 ~ 2012.06.18 조사   * 무임승차 경험 학생 기준',
         fontsize=10, color=MUTED)
fig.subplots_adjust(left=0.34, right=0.97, top=0.86, bottom=0.14)
fig.savefig('image2.png', facecolor='white')
plt.close(fig)

# ---------- 그림 1-1 ----------
W, H = 16.66, 8.76
fig = plt.figure(figsize=(W / 2, H / 2), dpi=200)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
ax.plot([W / 2, W / 2], [0.4, H - 0.4], ls=(0, (3, 3)), color='#dcd6cd', lw=0.8)


def column(cx, title, boxes, color, text_color, lw, footer, footer_bold):
    ax.text(cx, H - 0.55, title, ha='center', va='center', fontsize=12, fontweight='bold', color=color)
    bw, bh, gap, top = 6.5, 1.15, 0.58, H - 1.15
    ys = []
    for i, (l1, l2) in enumerate(boxes):
        yt = top - i * (bh + gap)
        ax.add_patch(FancyBboxPatch((cx - bw / 2, yt - bh), bw, bh, boxstyle='round,pad=0,rounding_size=0.04',
                                    fc='white', ec=color, lw=lw))
        if l2:
            ax.text(cx, yt - bh * 0.33, l1, ha='center', va='center', fontsize=10.5, color=text_color)
            ax.text(cx, yt - bh * 0.70, l2, ha='center', va='center', fontsize=10.5, color=text_color)
        else:
            ax.text(cx, yt - bh / 2, l1, ha='center', va='center', fontsize=10.5, color=text_color)
        ys.append(yt)
    for a, b in zip(ys, ys[1:]):
        ax.add_patch(FancyArrowPatch((cx, a - bh), (cx, b), arrowstyle='-|>', mutation_scale=11,
                                     color=NAVY_D if color != BROWN else '#7a6a55', lw=1.4))
    fy = ys[-1] - bh - 0.35
    ax.text(cx, fy, footer, ha='center', va='center', fontsize=10,
            fontweight='bold' if footer_bold else 'normal', color=color)


column(W * 0.275, '현행', [('과제 진행', '노션·구글 드라이브·카카오톡에 기록 분산'),
                          ('과제 종료', ''),
                          ('구글 폼·서면에 점수 입력', '근거 없이 기억과 인상에 의존')],
       BROWN, BROWN, 1.2, '파일 없는 기여의 기록 부재', False)
column(W * 0.725, '제안', [('산출물·기여 항목 기록', '파일과 업로드 시각 함께 저장'),
                          ('조원 완료확인', '본인 단독 소급 입력 불가'),
                          ('근거 패널 옆 점수 입력', '평가 대상 조원의 기록 참고'),
                          ('교수 열람', '조별 근거·평가 결과 열람')],
       NAVY_D, NAVY_D, 2.2, '', True)
fig.savefig('image1.png', facecolor='white')
plt.close(fig)
print('saved')
