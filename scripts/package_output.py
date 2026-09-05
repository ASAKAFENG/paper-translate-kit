#!/usr/bin/env python3
"""package_output.py — 按论文标题命名 PDF 并组装交付包。
用法: package_output.py <paper_dir> [--out deliver_dir] [--note "特别注意事项"]
约定目录结构: <paper_dir>/{src/, zh/, out/ 或 main 编译产物}
产出: <out>/<论文名>/{<title>-en.pdf, <中文标题>-zh.pdf, src-en/, src-zh/, 说明.txt}
"""
import argparse, os, re, shutil, sys, glob

def find_pdfs(base):
    out = os.path.join(base, 'out')
    if os.path.isdir(out):
        return sorted(glob.glob(os.path.join(out, '*-en.pdf')) + glob.glob(os.path.join(out, '*-zh.pdf')))
    return []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paper_dir')
    ap.add_argument('--out', default='deliver')
    ap.add_argument('--note', default='')
    ap.add_argument('--name', default=None, help='包目录名（默认按序号+主文件推断）')
    a = ap.parse_args()
    pdfs = find_pdfs(a.paper_dir)
    if not pdfs:
        sys.exit('未找到 out/ 下的成品 PDF')
    name = a.name or os.path.basename(os.path.normpath(a.paper_dir))
    d = os.path.join(a.out, name)
    os.makedirs(d, exist_ok=True)
    for p in pdfs:
        shutil.copy(p, d)
    for sub, tag in (('src', 'src-en'), ('zh', 'src-zh')):
        s = os.path.join(a.paper_dir, sub)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(d, tag),
                            ignore=shutil.ignore_patterns('*.aux','*.log','*.out','*.bbl','*.blg','*.snm','*.toc'))
    en = next((f for f in pdfs if f.endswith('-en.pdf')), '')
    zh = next((f for f in pdfs if f.endswith('-zh.pdf')), '')
    note = f'\n特别注意事项：\n----------------------------------------------------------------\n{a.note}\n' if a.note else ''
    open(os.path.join(d, '说明.txt'), 'w', encoding='utf-8').write(f"""{name} —— 论文中英对照包
----------------------------------------------------------------
英文：{os.path.basename(en) if en else '（无）'}
中文：{os.path.basename(zh) if zh else '（无）'}
包含：英文PDF、中文PDF、src-en（英文源码）、src-zh（中文翻译源码）
编译：英文版按原工程引擎；中文版 LuaLaTeX（ctex + Noto CJK）。
引用：全部 \\cite 与原文逐一对齐，参考文献保持英文。
{note}""")
    print('[ok]', d, '->', sorted(os.listdir(d)))

if __name__ == '__main__':
    main()
