"""양식형 업무 기능도: 들여쓰기 목록 -> 왼쪽 세로줄 트리 (양식 예시와 같은 흑백 박스형)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, FancyArrowPatch

for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f or "NotoSansCJK-Bold" in f:
        fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK KR"


def parse(text):
    root = None
    stack = []
    for line in text.strip("\n").splitlines():
        if not line.strip():
            continue
        depth = (len(line) - len(line.lstrip(" "))) // 2
        node = {"name": line.strip().lstrip("- ").strip(), "kids": []}
        if depth == 0:
            root = node
            stack = [node]
        else:
            stack = stack[:depth]
            stack[-1]["kids"].append(node)
            stack.append(node)
    return root


def layout(node, depth, rows):
    node["depth"] = depth
    if not node["kids"]:
        node["row"] = rows[0]
        rows[0] += 1
    else:
        for k in node["kids"]:
            layout(k, depth + 1, rows)
        node["row"] = node["kids"][0]["row"]


def draw_tree(ax, root, x0, y0, col_w=(96, 96, 96, 96), box_h=26, row_h=36, gap=22, fs=9.5):
    """root는 맨 위 줄, 자식은 그 아래 줄부터 (양식 예시처럼 왼쪽 세로줄)"""
    xs = [x0]
    for i in range(1, 5):
        xs.append(xs[-1] + col_w[i - 1] * (0.55 if i == 1 else 1) + gap)
    # 루트를 별도 줄에 두고 1단계부터 아래 줄로 시작
    rows = [1]
    for k in root["kids"]:
        layout(k, 1, rows)
    root["depth"], root["row"] = 0, 0

    def pos(n):
        d = n["depth"]
        x = x0 + (0 if d == 0 else col_w[0] * 0.55 + gap + sum(col_w[1:d]) + gap * (d - 1))
        y = y0 + n["row"] * row_h
        return x, y, col_w[d]

    def box(n):
        x, y, w = pos(n)
        ax.add_patch(Rectangle((x, y), w, box_h, fc="white", ec="black", lw=1.1, zorder=2))
        ax.text(x + w / 2, y + box_h / 2, n["name"], fontsize=fs, ha="center", va="center", zorder=3,
                fontweight="bold" if n["depth"] == 0 else "normal")

    def ln(xx, yy):
        ax.plot(xx, yy, color="black", lw=1.0, zorder=1)

    # 루트와 1단계: 루트 아래 왼쪽 세로줄
    rx, ry, rw = pos(root)
    box(root)
    spine = rx + 14
    last = root["kids"][-1]
    ln([spine, spine], [ry + box_h, pos(last)[1] + box_h / 2])

    def walk(n):
        x, y, w = pos(n)
        box(n)
        if n["kids"]:
            cx = x + w + gap / 2
            ln([x + w, cx], [y + box_h / 2, y + box_h / 2])
            ys = [pos(k)[1] + box_h / 2 for k in n["kids"]]
            ln([cx, cx], [min(ys), max(ys)])
            for k, yy in zip(n["kids"], ys):
                ln([cx, pos(k)[0]], [yy, yy])
                walk(k)

    for k in root["kids"]:
        x, y, w = pos(k)
        ln([spine, x], [y + box_h / 2, y + box_h / 2])
        walk(k)
    nrows = rows[0]
    return y0 + nrows * row_h


if __name__ == "__main__":
    OUTLINE = """
발자국
  - 회원 관리
    - 회원가입
      - 인증 메일 발송
      - 회원 등록
    - 로그인
      - 로그인 처리
      - 로그아웃 처리
"""
    W, H = 760, 360
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")

    # 왼쪽: 제출 형식
    ax.text(20, 28, "① 이렇게 써서 제출 (들여쓰기 목록)", fontsize=11, fontweight="bold")
    ax.add_patch(Rectangle((20, 44), 230, 210, fc="#F4F4F4", ec="#999999", lw=0.8))
    for i, line in enumerate(OUTLINE.strip("\n").splitlines()):
        ax.text(32, 66 + i * 23, line, fontsize=10.5, va="center", family="monospace") if False else \
            ax.text(32 + (len(line) - len(line.lstrip())) * 7, 66 + i * 23, line.strip(), fontsize=10.5, va="center")

    ax.add_patch(FancyArrowPatch((262, 150), (300, 150), arrowstyle="-|>", mutation_scale=16, color="black", lw=1.4))

    # 오른쪽: 양식 그림
    ax.text(312, 28, "② 팀 조장이 양식 그림으로 그림", fontsize=11, fontweight="bold")
    root = parse(OUTLINE)
    draw_tree(ax, root, 312, 48, col_w=(96, 86, 86, 104))

    # 아래 규칙
    notes = ["· 한 칸에는 한 가지 일만 씁니다. 무엇을 하는지 짧게 씁니다. 예: 회원 등록, 과제 정보 등록",
             "· 들여쓰기 한 단계는 그림에서 오른쪽 한 칸입니다. 영역, 기능, 세부 동작의 3단계까지만 씁니다.",
             "· 그림은 그리지 않습니다. 목록만 제출하면 팀 조장이 같은 모양으로 그립니다."]
    for i, n in enumerate(notes):
        ax.text(20, 286 + i * 22, n, fontsize=10.5, va="center")
    fig.savefig("예시_업무기능도_회원관리.png", dpi=200)
    print("ok")
