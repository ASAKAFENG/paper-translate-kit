#!/usr/bin/env python3
"""detect_engine.py — 识别 LaTeX 工程的模板与推荐编译引擎。
用法: detect_engine.py <src_dir> [main.tex]
输出 JSON: {"engine": "...", "reason": "...", "bibtex": "yes|no|bu1", "notes": [...]}
"""
import json, os, re, sys

def read(p):
    try: return open(p, encoding='utf-8', errors='ignore').read()
    except OSError: return ''

def main(d, main='main.tex'):
    notes = []
    # 1) arXiv 官方指定
    r00 = os.path.join(d, '00README.json')
    if os.path.exists(r00):
        try:
            spec = json.loads(open(r00, encoding='utf-8').read())
            eng = spec.get('process', {}).get('compiler')
            if eng:
                notes.append(f"00README.json 指定 {eng}")
                return json.dumps({"engine": eng, "reason": "00README.json",
                                   "bibtex": "auto", "notes": notes}, ensure_ascii=False)
        except Exception:
            pass
    # 找主文件
    for cand in (main, 'main.tex', 'arXiv.tex', 'example_paper.tex'):
        if os.path.exists(os.path.join(d, cand)):
            main = cand; break
    tex = read(os.path.join(d, main))
    # 汇总所有 \input 的 tex
    blob = tex
    for m in re.finditer(r'\\input\{([^}]+)\}', tex):
        p = m.group(1)
        for suf in ('', '.tex'):
            blob += read(os.path.join(d, p if p.endswith('.tex') else p + '.tex'))
    for extra in ('packages.tex', 'preamble.tex', 'commands.tex'):
        blob += read(os.path.join(d, extra))
    engine, reason = 'pdflatex', '默认（CVPR/ICML/ECCV/IEEE 模板惯例）'
    if 'axessibility' in blob:
        notes.append('含 axessibility：原版必须 pdfLaTeX；中文版需禁用该宏包')
    if 'icml2026' in blob:
        notes.append('icml2026.sty：LuaLaTeX 需在加载前加 \\newdimen\\pdfpagewidth/\\pdfpageheight 垫片')
    if 'bibunits' in blob:
        notes.append('bibunits：需额外 bibtex bu1（aux 名即 bu1.aux）')
    if re.search(r'\\input\{[^}]*\.bbl\}', tex) or ('.bbl' in os.listdir(d) and '\\bibliography{' not in tex):
        notes.append('bbl 直接 \\input：禁止运行 bibtex（会清空 bbl）')
    # 中文工程强制 lualatex
    if 'ctex' in blob or 'CJK' in blob:
        engine, reason = 'lualatex', '含 ctex/CJK：统一 LuaLaTeX（避开 XeTeX 非确定性 bug）'
        notes.append('中文版推荐 fontset=none + 显式 Noto CJK')
    return json.dumps({"engine": engine, "reason": reason, "main": main,
                       "bibtex": "auto", "notes": notes}, ensure_ascii=False, indent=1)

if __name__ == '__main__':
    d = sys.argv[1] if len(sys.argv) > 1 else '.'
    m = sys.argv[2] if len(sys.argv) > 2 else 'main.tex'
    print(main(d, m))
