# 작업 원고(기호 없음) → 빌드 원고(□ - ※ 기호, 프로젝트명, 차례)
import sys
TOC2 = """TOC
T1 2-1. 업무 영역 구성|1
T2 영역 구분 기준|1
T2 기능 추가와 분리|2
T1 2-2. 업무 기능도|3
T1 2-3. 기능 목록|4"""
PG3 = {'3-1': 1, '3-2': 3, '3-3': 5, '3-4': 7, '3-5': 9, '3-6': 13, '3-7': 15}  # 2026.10.14 한글 화면 확인 값
PGH = {'작성 기준': 1, '공통 업무 규칙': 1, 'MEM-01': 3, 'MEM-02': 4, 'ASG-01': 5, 'ASG-02': 6, 'ASG-03': 6,
       'TEAM-01': 7, 'TEAM-02': 8, 'REC-01': 9, 'REC-02': 10, 'REC-03': 11, 'REC-04': 12,
       'EVAL-01': 13, 'EVAL-02': 14, 'VIEW-01': 15, 'VIEW-02': 16}

def toc3(src):
    t = ["TOC"]; cur = None
    for l in open(src, encoding='utf8'):
        if l.startswith('S '):
            cur = l[2:].strip(); t.append('T1 %s|%d' % (cur, PG3[cur.split('.')[0]]))
        elif l.startswith('H ') and cur:
            h = l[2:].strip(); t.append('T2 %s|%d' % (h, PGH.get(h.split(' ')[0], PGH.get(h, PG3[cur.split('.')[0]]))))
    return '\n'.join(t)

def conv(src, dst, toc):
    out = []
    for l in open(src, encoding='utf8'):
        l = l.rstrip('\n'); tag, _, rest = l.partition(' ')
        if tag == 'COVER': out += [l, '', toc, '']; continue
        if tag == 'SUB': l = 'SUB 프로젝트명: ' + rest
        elif tag == 'H': l = 'H □ ' + rest
        elif tag == 'D': l = 'D - ' + rest
        elif tag == 'N': l = 'N ※ ' + rest
        out.append(l)
    open(dst, 'w', encoding='utf8').write('\n'.join(out) + '\n')

src2, src3 = sys.argv[1], sys.argv[2]
conv(src2, '2_업무기능도_원고_v0.7.txt', TOC2)
conv(src3, '3_업무기술서_원고_v0.7.txt', toc3(src3))
print('converted')
