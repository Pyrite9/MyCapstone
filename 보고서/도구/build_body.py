# 템플릿 견본 문단·요약 상자·표 작성
import json
from hwpx.document import HwpxDocument

ids = json.load(open('ids.json'))
tbf = json.load(open('tbf.json'))
BOX = ids['_BF_BOX'][0]
KW = ids['괄호 키워드'][2]
ASIDE = ids['괄호 보충'][2]

d = HwpxDocument.open('t1.hwpx')


def para(style, *runs, target=None):
    sid, pp, cp = ids[style]
    host = target if target is not None else d
    p = host.add_paragraph('', style_id_ref=sid, para_pr_id_ref=pp, char_pr_id_ref=cp, include_run=False) \
        if target is None else host.add_paragraph('')
    if target is not None:
        p.style_id_ref = sid
        p.para_pr_id_ref = pp
        for r in list(p.runs):
            r.element.getparent().remove(r.element)
    for item in runs:
        text, char = (item, cp) if isinstance(item, str) else item
        p.add_run(text, char_pr_id_ref=char)
    return p


# 1쪽(표지)은 비워 둠. 2쪽부터 견본
para('보고서 제목', '프로젝트 개요서')

# 요약 상자: 1칸 표
box = d.add_table(1, 1, border_fill_id_ref=BOX)
cell = box.cell(0, 0)
first = cell.paragraphs[0]
sid, pp, cp = ids['요약 제목']
first.style_id_ref, first.para_pr_id_ref = sid, pp
for r in list(first.runs):
    r.element.getparent().remove(r.element)
first.add_run('< 요 약 >', char_pr_id_ref=cp)
for line in ['○ 서 비 스: 발자국(조별과제 과정기록·평가지원 웹 서비스)',
             '○ 원    칙: 판단은 사람, 시스템은 근거만',
             '○ 사 용 자: 교수, 조장, 조원']:
    para('요약 본문', line, target=cell)

para('절', '1-1. 서비스 개요')
para('□ 소제목', '□ 종합 기획')
para('○ 본문', '○ ', ('(서비스 정의)', KW), ' 산출물·완료확인의 과정 기록과 기록 근거 기반 동료평가 입력 지원')
para('- 본문', '- 교수의 과제 생성, 조별 조장 지정, 조원의 산출물 업로드·완료확인')
para('· 본문', '· 기록 시각은 서버 기록, 사용자 수정 불가')
para('○ 본문', '○ ', ('(파일 없는 기여)', KW), ' 회의 진행·자료 취합·일정 조율의 기여 항목 등록',
     ('(팀 내부 사전 조사 3명)', ASIDE))
para('※ 주석', '※ 업로드 횟수는 기여도가 아님. 점수는 시스템이 계산하지 않음')

para('표 캡션', '[표 1-1] 사용자별 문제와 제공 가치')
rows = [['사용자', '현행 문제', '제공 가치'],
        ['교수', '평가 시점의 조 내부 진행 과정 확인 곤란', '조별 과정 기록 열람'],
        ['조원', '파일 없는 기여의 평가 미반영', '기여 항목 등록과 타 조원 완료확인']]
R, Cn = len(rows), len(rows[0])
tbl = d.add_table(R, Cn)
tbl.set_column_widths([7000, 20600, 20588])
for r in range(R):
    for c in range(Cn):
        key = '|'.join(['0.4 mm' if r == 0 else '0.12 mm',
                        '0.4 mm' if r == R - 1 else '0.12 mm',
                        'None' if c == 0 else '0.12 mm',
                        'None' if c == Cn - 1 else '0.12 mm',
                        str(r == 0)])
        tbl.set_cell_border_fill(r, c, tbf[key])
        cell = tbl.cell(r, c)
        p = cell.paragraphs[0]
        style = '표 헤더' if r == 0 else '표 본문'
        sid, pp, cp = ids[style]
        p.style_id_ref, p.para_pr_id_ref = sid, pp
        for run in list(p.runs):
            run.element.getparent().remove(run.element)
        bold_first = (c == 0 and r > 0)
        p.add_run(rows[r][c], char_pr_id_ref=ids['표 헤더'][2] if bold_first else cp)

para('그림 캡션', '[그림 1-1] 현행 방식과 제안 방식 비교(수치는 예시)')

d.save_to_path('템플릿.hwpx')
print('saved')
