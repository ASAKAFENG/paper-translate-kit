#!/usr/bin/env python3
"""check_untranslated.py — 扫描中文版 PDF 文本中的残留英文正文。
用法: check_untranslated.py <pdf> 或  pdftotext <pdf> - | check_untranslated.py
说明：参考文献列表与图表内烘焙文字为合法英文；本脚本聚焦三类高危漏译：
  章节标题 / 图注 / 表题。输出的每一项都需要人工确认。
"""
import re, sys

LINE = sys.stdin.read() if sys.stdin.isatty() is False else ''
if not LINE:
    sys.exit("用法: pdftotext <pdf> - | check_untranslated.py")

# 高危模式：编号标题 / 图注 / 表题
patterns = [
    (r'^\s*\d+(\.\d+)*\.?\s+[A-Z][a-z]+ [a-z]', '疑似英文章节标题'),
    (r'^(Figure|Fig\.|Table)\s+\d+', '疑似英文图/表题'),
]
hits = []
for line in LINE.split('\n'):
    s = line.strip()
    if not s: continue
    for pat, tag in patterns:
        if re.match(pat, s):
            # 排除含中文的行
            if not re.search(r'[\u4e00-\u9fff]', s):
                hits.append((tag, s[:90]))
# 图注英文段（图 N. 后跟长英文句）
for m in re.finditer(r'(?:图|Figure|Fig\.?|Table|表)\s*\d+[.:]\s*([A-Z][^\n]{30,})', LINE):
    if not re.search(r'[\u4e00-\u9fff]', m.group(1)):
        hits.append(('疑似英文图/表注', m.group(0)[:90]))

if hits:
    print(f'发现 {len(hits)} 处疑似未翻译（需人工确认）:')
    for tag, s in hits:
        print(f'  [{tag}] {s}')
    sys.exit(1)
else:
    print('未发现明显残留英文标题/图注（参考文献与图内文字除外）')
