"""核对引文：在《鲁迅全集》(2005修订版) PDF 抽取的文本中逐条精确匹配。
用法: pdftotext 全集.pdf qj.txt && python3 verify_quotes.py qj.txt quotes_src.tsv quotes_checked.tsv
匹配前去除空白与注释角标 [n]；输出状态与 PDF 页码。"""
import re, csv, sys, bisect
txt, src, dst = sys.argv[1:4]
pages = open(txt, encoding='utf-8').read().split('\f')
flat = [re.sub(r'\s+', '', p) for p in pages]
joined = ''.join(flat); starts = []; c = 0
for p in flat: starts.append(c); c += len(p)
buf, mapping = [], []
for m in re.finditer(r'\[\d+\]|.', joined, re.S):
    if m.group().startswith('[') and m.group().endswith(']') and len(m.group()) > 1: continue
    buf.append(m.group()); mapping.append(m.start())
jn = ''.join(buf); out = []
for row in csv.reader(open(src, encoding='utf-8'), delimiter='\t'):
    q = re.sub(r'\s+', '', row[1]); k = jn.find(q)
    status = '✅ 原文一致' if k >= 0 else '❌ 未找到'
    page = bisect.bisect_right(starts, mapping[k]) if k >= 0 else ''
    out.append(row + [status, str(page)]); print(row[0], status, page)
csv.writer(open(dst, 'w', encoding='utf-8'), delimiter='\t').writerows(out)
