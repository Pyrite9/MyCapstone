# 표용 테두리 조합 추가: (위, 아래, 왼, 오, 음영)
import copy, json
from lxml import etree
P='src/Contents/header.xml'
H='http://www.hancom.co.kr/hwpml/2011/head'; C='http://www.hancom.co.kr/hwpml/2011/core'
NS={'hh':H,'hc':C}
t=etree.parse(P); r=t.getroot()
bfs=r.find('.//hh:borderFills',NS); base=bfs.findall('hh:borderFill',NS)[1]  # id=2, fillBrush 포함
out={}
for top in ['0.4 mm','0.12 mm']:
  for bot in ['0.4 mm','0.12 mm']:
    for left in [None,'0.12 mm']:
      for right in [None,'0.12 mm']:
        for shade in [False,True]:
          b=copy.deepcopy(base); i=len(bfs)+1; b.set('id',str(i))
          for side,w in [('topBorder',top),('bottomBorder',bot),('leftBorder',left),('rightBorder',right)]:
            e=b.find('hh:'+side,NS)
            if w: e.set('type','SOLID'); e.set('width',w)
            else: e.set('type','NONE')
          b.find('hh:diagonal',NS).set('type','NONE')
          b.find('.//hc:winBrush',NS).set('faceColor','#D9D9D9' if shade else '#FFFFFFFF')
          bfs.append(b); out['|'.join([top,bot,str(left),str(right),str(shade)])]=i
bfs.set('itemCnt',str(len(bfs)))
t.write(P,xml_declaration=True,encoding='UTF-8',standalone=True)
json.dump(out,open('tbf.json','w'),ensure_ascii=False)
print(len(out))
