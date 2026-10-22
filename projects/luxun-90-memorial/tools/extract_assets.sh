#!/usr/bin/env bash
# 从本地 PDF 复现分镜中用到的老照片（自动生成）。需要 poppler-utils（pdftoppm / pdfimages）。
# 用法: bash tools/extract_assets.sh 鲁迅画传.pdf 鲁迅全集2005.pdf out/
set -euo pipefail
HZ_PDF="$1"; QJ_PDF="$2"; OUT="${3:-out}"; mkdir -p "$OUT/HZ" "$OUT/QJ"
# 《鲁迅画传》是整页扫描：按页渲染 300dpi
for p in 4 6 7 9 10 11 12 13 14 18 24 29 30 31 33 34 40 43 56 61 62 66 71 76 79 81 85 95 97 98 102 103 104 108 112 115 117 120 123 125 131 132 134 136 139 141 146 151 154 160 161 163 170 171 172 175 176 177 178 179 180 181 201 207 208 221 231 232 234; do
  pdftoppm -f "$p" -l "$p" -r 300 -png "$HZ_PDF" "$OUT/HZ/HZ-p$p"
done
# 《鲁迅全集》文前彩插：直接抽取嵌入图片原始数据
for p in 97 101 103 493 496 497 498 855 857 1244 1655 2024 2025 2026 2028 2444 3344 3653 3654 4119 5001 5005 5007 5514 6080 6081 6083 6618 7292 7294 7296 7298; do
  pdfimages -f "$p" -l "$p" -all "$QJ_PDF" "$OUT/QJ/QJ-p$p"
done
echo "done -> $OUT"
