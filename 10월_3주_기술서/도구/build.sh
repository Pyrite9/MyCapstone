#!/bin/bash
# 사용: ./build.sh <원고.txt> <결과.hwpx>   (10월_3주_기술서 작업 폴더 기준)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE"
SEC_NEWPAGE=0 ROW_EQUAL=0 python3 build_report.py "$HERE/템플릿_v8.hwpx" "$1" "$HERE" out.hwpx 2026.10
rm -rf x && mkdir x && (cd x && unzip -q ../out.hwpx)
python3 "$HERE/build_box.py" x/Contents/section0.xml
OUT="$HERE/$2"; rm -f "$OUT"
(cd x && zip -q -X -D -0 "$OUT" mimetype && zip -q -X -D -r "$OUT" . -x mimetype)
rm -rf x out.hwpx
echo built "$2"
