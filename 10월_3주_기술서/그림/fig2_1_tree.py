"""그림 2-1 업무 기능도 v0.2 — 양식형(왼쪽 세로줄) 3단계: 영역 > 기능 > 단위 업무
문서 폭 6.5in(468pt)로 그려 글자 pt = 인쇄 pt. 글자 9pt 이상."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tree_form import parse, draw_tree

OUTLINE = """
발자국
  - 회원 관리
    - 회원가입
      - 회원 등록
    - 로그인·로그아웃
      - 로그인·로그아웃
  - 과제 관리
    - 과제 생성
      - 과제 정보 입력
      - 조장 지정
    - 과제 조회
      - 과제 목록 조회
      - 과제 상세 조회
    - 과제 단계 전환
      - 평가 시작
  - 조 운영
    - 조원 초대
      - 초대 링크 발급
      - 링크로 합류
    - 역할 배정
      - 역할 지정
      - 역할 변경
  - 과정 기록
    - 산출물 업로드·열람
      - 산출물 업로드
      - 산출물 열람
      - 산출물 삭제
    - 기여 항목 등록·보고
      - 기여 항목 등록
      - 기여 항목 조회
      - 완료 보고
      - 기여 항목 취소
    - 완료확인
      - 완료확인 등록
      - 확인 취소
      - 확인 이력 조회
    - 진척 시각화
      - 진척 화면 조회
  - 동료평가
    - 근거 패널
      - 근거 기록 조회
    - 동료평가 입력
      - 평가 입력
      - 임시 저장
      - 평가 제출
  - 교수 열람
    - 조별 기록 열람
      - 시간순 기록 조회
    - 평가 결과 열람
      - 제출 현황 확인
      - 평가 결과 조회
"""

if __name__ == "__main__":
    root = parse(OUTLINE)
    n_leaf = sum(len(f["kids"]) for a in root["kids"] for f in a["kids"])
    row_h, box_h = 15, 12
    H = (n_leaf + 1) * row_h + 4
    W = 468
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    draw_tree(ax, root, 2, 2, col_w=(100, 92, 118, 118), box_h=box_h, row_h=row_h, gap=20, fs=9)
    fig.savefig("fig2-1_tree.png", dpi=300)
    print("units", n_leaf, "height mm", round(H / 72 * 25.4, 1))
