# 작업 원고(번호 없음) -> 빌드 원고: 번호 범례 1. -> 가. -> 1) -> 가) 자동 부여, 차례 생성
# 사용: python3 conv_num.py <작업원고.txt> <빌드원고.txt> [쪽번호.json]
import sys, json
KO = '가나다라마바사아자차카타파하'
src, dst = sys.argv[1], sys.argv[2]
pages = json.load(open(sys.argv[3], encoding='utf8')) if len(sys.argv) > 3 else {}

lines = [l.rstrip('\n') for l in open(src, encoding='utf8')]
out, toc = [], []
s = h = o = d = 0
for l in lines:
    tag, _, rest = l.partition(' ')
    if tag == 'S':
        s += 1; h = o = d = 0
        t = '%d. %s' % (s, rest); out.append('S ' + t); toc.append(('T1', t))
    elif tag == 'H':
        h += 1; o = d = 0
        t = '%s. %s' % (KO[h - 1], rest); out.append('H ' + t); toc.append(('T2', t))
    elif tag == 'O':
        o += 1; d = 0
        out.append('O %d) %s' % (o, rest))
    elif tag == 'D':
        d += 1
        out.append('D %s) %s' % (KO[d - 1], rest))
    elif tag == 'N':
        out.append('N ※ ' + rest)
    else:
        out.append(l)

# 차례: COVER 바로 뒤에 넣음. 쪽 번호는 한글 화면 확인 값(json)을 쓰고, 없으면 0
res = []
for l in out:
    res.append(l)
    if l.startswith('COVER'):
        res.append('')
        res.append('TOC')
        cur = 0
        for tag, t in toc:
            res.append('%s %s|%d' % (tag, t, pages.get(t, 0)))
        res.append('')
open(dst, 'w', encoding='utf8').write('\n'.join(res) + '\n')
print('converted', len(toc), 'toc lines')
