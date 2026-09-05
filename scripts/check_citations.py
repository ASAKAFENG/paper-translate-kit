#!/usr/bin/env python3
"""check_citations.py — 比对英文原版与中文翻译源码的 \\cite / \\label / \\ref 完全一致。
用法: check_citations.py <src_dir> <zh_dir>
判定：剥离注释行后，\\cite 键（含顺序）、\\label/\\ref/eqref 键必须完全一致。
输出：每文件比对结果 + 最终 ALL MATCH / DIFFS FOUND。
"""
import re, sys, os
from pathlib import Path

CITE = re.compile(r'\\cite\{([^}]*)\}')
LABEL = re.compile(r'\\(?:label|ref|eqref|autoref|Cref|cref)\{([^}]*)\}')

def strip_comments(t):
    out = []
    for line in t.split('\n'):
        # 保留 \%; 只剥未转义的 %
        i = 0
        while i < len(line):
            if line[i] == '%' and (i == 0 or line[i-1] != '\\'):
                break
            i += 1
        out.append(line[:i])
    return '\n'.join(out)

def cites(t):
    r = []
    for m in CITE.finditer(t):
        r += [k.strip() for k in m.group(1).split(',')]
    return r

def labels(t):
    return LABEL.findall(t)

def tree(d):
    return sorted(str(p) for p in Path(d).rglob('*.tex'))

def main(src, zh):
    ok = True
    sfiles, zfiles = tree(src), tree(zh)
    if len(sfiles) != len(zfiles):
        print(f'文件数不同: src={len(sfiles)} zh={len(zfiles)}')
    smap = {os.path.relpath(p, src): p for p in sfiles}
    zmap = {os.path.relpath(p, zh): p for p in zfiles}
    for rel in sorted(set(smap) | set(zmap)):
        a = read(smap.get(rel, '')) if rel in smap else ''
        b = read(zmap.get(rel, '')) if rel in zmap else ''
        a, b = strip_comments(a), strip_comments(b)
        ca, cb, la, lb = cites(a), cites(b), labels(a), labels(b)
        if ca != cb or la != lb:
            ok = False
            print(f'MISMATCH {rel}')
            if set(ca) - set(cb): print('  cite 缺失:', sorted(set(ca)-set(cb))[:8])
            if set(cb) - set(ca): print('  cite 多出:', sorted(set(cb)-set(ca))[:8])
            if ca != cb and set(ca) == set(cb): print('  cite 顺序不同')
            if set(la) - set(lb): print('  label/ref 缺失:', sorted(set(la)-set(lb))[:8])
            if set(lb) - set(la): print('  label/ref 多出:', sorted(set(lb)-set(la))[:8])
    print('ALL MATCH' if ok else 'DIFFS FOUND')
    sys.exit(0 if ok else 1)

def read(p):
    return open(p, encoding='utf-8', errors='ignore').read() if p else ''

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
