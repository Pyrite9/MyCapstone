#!/bin/bash
# 사용: ./build.sh <원고.txt> <결과.hwpx>
set -e
cd /home/claude/report
python3 build_report.py /home/claude/템플릿_v7.hwpx "$1" . out.hwpx
rm -rf x && mkdir x && (cd x && unzip -q ../out.hwpx)
python3 /home/claude/tpl/build_box.py x/Contents/section0.xml
rm -f "$2"
(cd x && zip -q -X -D -0 "$2" mimetype && zip -q -X -D -r "$2" . -x mimetype)
echo built "$2"
