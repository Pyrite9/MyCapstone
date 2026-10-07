#!/bin/bash
# 템플릿 재생성: 관리자 원본(템플릿.hwpx, 쪽 설정만 된 파일) → 템플릿_vN.hwpx
# 사용: ./make_template.sh <원본.hwpx> <결과.hwpx>
set -e
SRC_HWPX="$1"; OUT_HWPX="$2"
cd "$(dirname "$0")"
rm -rf src out t1.hwpx tmp_body.hwpx
mkdir src && (cd src && unzip -q "$SRC_HWPX")
python3 build_header.py
python3 build_tbf.py
(cd src && zip -q -X -D -0 ../t1.hwpx mimetype && zip -q -X -D -r ../t1.hwpx . -x mimetype)
python3 build_body.py            # t1.hwpx → 템플릿.hwpx(작업용 이름)
mkdir out && (cd out && unzip -q ../템플릿.hwpx)
python3 build_box.py out/Contents/section0.xml
rm -f "$OUT_HWPX"
(cd out && zip -q -X -D -0 "$OUT_HWPX" mimetype && zip -q -X -D -r "$OUT_HWPX" . -x mimetype)
echo "done: $OUT_HWPX"
