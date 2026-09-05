# 模板与引擎兼容性指南（实战排错手册）

> 本文档收录在 10 篇论文（CVPR 2024/2025/2026、ICCV 2021、ECCV 2024、ICML 2026、
> IEEE 期刊）的完整翻译编译中实际踩过的坑与解法。按"症状 → 原因 → 对策"组织。

## 1. 编译引擎选择决策树

```
工程里有 00README.json？
├─ 有 → 用其 process.compiler 指定引擎（arXiv 官方结论）
└─ 没有
   ├─ 含中文（src-zh）→ 一律 LuaLaTeX（ctex）
   ├─ 含 \usepackage[accsupp]{axessibility} → 必须 pdfLaTeX
   ├─ icml2026.sty → pdfLaTeX（中文版 LuaLaTeX + 垫片，见 §6）
   ├─ llncs/eccv、IEEEtran、cvpr.sty → pdfLaTeX
   └─ iccv.sty 等老模板 → XeLaTeX 通常也可（但见 §4 崩溃风险）
```

**中文版引擎铁律**：优先 LuaLaTeX。XeTeX 存在 `bad native font flag in
'map_char_to_glyph'` 的**非确定性**内部错误（同一文件时崩时不崩，与截断实验结果矛盾），
实测整篇论文连续 6 次失败而截断版通过，无规律可循。不要在 XeLaTeX 上恋战。

## 2. axessibility 宏包（最高频问题）

- **症状**：XeLaTeX/LuaLaTeX 下 `Undefined control sequence \pdfglyphtounicode`、
  `Missing \begin{document}`、`\pdfoptionpdfminorversion`。
- **原因**：该宏包（CVPR 官方模板自带，"CVPR Request"）依赖 pdfTeX 专属原语；
  它自带的 `accsupp-luatex.def` 同样调用 pdfTeX 原语，LuaLaTeX 下照样崩。
- **对策**：原版编译用 pdfLaTeX 不动它；中文版注释掉该行并加说明：
  ```latex
  % \usepackage[accsupp]{axessibility} % 仅支持 pdfLaTeX，为兼容中文编译已禁用（不影响排版与内容）
  ```
- 该宏包只影响数学公式的 PDF 无障碍复制，禁用不影响排版与内容。

## 3. cairo 插图 PDF 与 XeTeX 不兼容

- **症状**：`! Unable to load picture or PDF file 'xxx.pdf'` 紧跟
  `! Package graphics Error: Division by 0.`——但文件确实存在、pdfinfo 能读。
- **原因**：cairo 1.15+ 输出的 PDF-1.5（交叉引用流/对象流），XeTeX 的内建
  PDF 解析器读不了。
- **诊断**：`pdfinfo xxx.pdf` 能读 + 最小用例（一行 `\includegraphics`）复现。
- **对策**：
  ```bash
  gs -q -o fixed.pdf -sDEVICE=pdfwrite xxx.pdf && mv fixed.pdf xxx.pdf
  ```
  画面不变。建议对 `figures/`、`LaTeX/figures/` 等图目录批量执行。
  pdfLaTeX/LuaLaTeX 不受影响（仅 XeTeX）。

## 4. XeTeX `bad native font flag`（非确定性崩溃）

- **症状**：`! Internal error: bad native font flag in 'map_char_to_glyph'`
  后接 `xdvipdfmx:fatal: File ended prematurely`。
- **特点**：同一文件有时通过有时失败；截断二分的结果互相矛盾（上一次失败的
  最小集，重跑又通过）。与字体选择无关（Fandol/Noto 都触发）、与重跑无关。
- **背景**：XeTeX 官方 bug（SourceForge #89）。
- **对策**：中文版统一 LuaLaTeX。不要试图用重试碰运气。

## 5. 文献引用的四种形态与编译策略

| 形态 | 识别方法 | 编译序列 |
|---|---|---|
| 标准 `\bibliography{main}` + `.bib` | aux 含 `\bibdata` | 引擎 → `bibtex main` → 引擎 ×2 |
| 自带 `.bbl` 且被 `\input{main.bbl}` | 主文有 `\input{main.bbl}` | 引擎 ×2，**禁止 bibtex** |
| 自带 `.bbl`（arXiv 惯例）| 无 `\bibliography` 或有但 bbl 已在 | 引擎 ×2 |
| `bibunits`（附录独立文献） | 有 `\begin{bibunit}[style]...\putbib` | 主 bibtex + `bibtex bu1`（注意 aux 文件名是 `bu1.aux` 不是 `<job>bu1.aux`） |

- ⚠️ **血泪教训**：对 `\input{bbl}` 型论文跑 bibtex 会把自带 bbl 覆盖成 0 字节，
  引用全灭。发现后从原始 tar 包恢复 bbl（务必校验字节数）。
- `.bst` 缺失：`IEEEtran.bst` → `texlive-publishers`；`ieee_fullname.bst`
  （CVPR/ICCV 惯用）**不在** TeX Live 中——若论文只带 bbl 则无需它；要重跑 bibtex
  则需从 CTAN/论文源码获取。
- 收到 bibtex 报 `I found no \bibdata command` 时，先查是不是形态 2。

## 6. icml2026.sty 在 LuaLaTeX 下的垫片

- **症状**：`! Undefined control sequence \pdfpagewidth`（sty 内
  `\setlength{\pdfpagewidth}{8.5in}`）。
- **对策**：在 `\usepackage[accepted]{icml2026}` **之前**（注意顺序，
  放导言区末尾无效）加入：
  ```latex
  % LuaLaTeX 兼容垫片：icml2026.sty 中的 \pdfpagewidth/\pdfpageheight 为 pdfTeX 原语
  \newdimen\pdfpagewidth
  \newdimen\pdfpageheight
  ```
  （article 类默认 letterpaper 8.5×11in，与 sty 要设的值相同，页面尺寸不受影响。）

## 7. 中文适配固定配方

```latex
\usepackage[UTF8,fontset=none]{ctex}
\setCJKmainfont[BoldFont={Noto Serif CJK SC Bold}]{Noto Serif CJK SC}
\setCJKsansfont[BoldFont={Noto Sans CJK SC Bold}]{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans Mono CJK SC}
```

- 为什么 `fontset=none`：Fandol 字体在部分环境缺失/异常，且 `TU/FandolSong` 会报
  bold 形状缺失告警；Noto CJK 各平台稳定可得。
- 为什么不用 `\usepackage{indentfirst}` 之外的中文排版定制：保持与原模板版式一致，
  只换语言。
- ctex 注入位置：hyperref 之前（导言区内任意位置均可，但必须在 hyperref 前）。

## 8. IEEEtran + 中文

- IEEEtran 期刊类 + ctex 可用（LuaLaTeX 验证）；
- `\IEEEpubidadjcol`、`\IEEEmembership`、`\thanks` 均正常；
- `bibunits` 正常工作（附录独立参考文献）；
- 页眉的 `\markboth` 未设置时显示默认标题，属原版行为。

## 9. 翻译替换脚本的三个经典自坑

1. **直弯引号**：源码混用 `object's`（U+2019）与 `"..."`（U+201C/201D），
   精确匹配前把模式里的 `'` 统一替换为弯引号，或用空白自适应正则。
2. **换行不一致**：源码段落在任意位置换行。精确字符串匹配大面积失败时，
   改用 `re.escape(eng).replace('\\ ', '\\s+')` 的空白自适应匹配，
   或"首尾唯一标记 + 切片替换"。
3. **双重转义叠加**：raw 字符串（`r'''\\cite'''`）+ repl 转义
   （`chn.replace('\\','\\\\')`）会让文件里出现 `\\section`（双反斜杠命令）。
   防线：统一用普通字符串写替换文本；或事后全文
   `re.sub(r'\\\\(?=[a-zA-Z])', '\\\\', ...)` 修复——但 `\\`（换行）会被误伤，
   修复公式块需从原文按序还原（见下条）。
4. **公式还原法**：翻译脚本损坏公式里的 `\\` 换行时，按出现顺序提取原文全部
   `\begin{equation}/\begin{align}` 块，与译文文件的块一一对应替换回去。

## 10. 浮动体与排错二分

- `figure*/table*` 跨栏浮动体会改变分页位置；"注释掉某图后编译通过"不代表图是
  元凶——它只是改变了断页。二分时保持浮动体结构不变（用 `\phantom` 占位或
  只删图形不删环境）。
- 定位真正触发错误的文本段：以"段首唯一短语"为锚，逐段累加编译（自动化脚本
  10-15 分钟内可定位到段）。

## 11. 验收自动化

- 引用一致性：解析两侧 tex，剥离注释行后提取 `\cite{}`（拆分逗号）、
  `\label/\ref/\eqref`，比较**有序列表**（顺序也要一致）。
- 残留英文：对编译出的 PDF 跑 `pdftotext`，扫描三类高危位置：
  章节标题（`数字. 英文`）、图注（`图 N. English...`）、表题；
  参考文献列表与图内烘焙文字是合法英文，需排除。
- 渲染抽查：`pdftoppm -png -r 80 -f <页> -l <页>`，标题页 + 密集正文页各一，
  人工或视觉评审代理验收（中文渲染、重叠、溢出、图表完整）。

## 12. 依赖安装速查（Debian/Ubuntu）

```bash
# 基础（覆盖绝大多数 CVPR/ICML/ECCV/IEEE 模板）
sudo apt-get install -y texlive-xetex texlive-latex-recommended texlive-latex-extra \
  texlive-fonts-recommended texlive-lang-chinese texlive-science texlive-bibtex-extra \
  texlive-publishers texlive-luatex latexmk ghostscript

# 按需
sudo apt-get install -y texlive-fonts-extra   # bbm 等冷门宏包（~1.8GB，慎装）
```

省盘技巧：`texlive-fonts-extra` 若只为 bbm.sty 而装，可改手动放置
`bbm-macros` 到 `~/texmf/tex/latex/` 后卸载该套件；`texlive-lang-{japanese,
korean,greek,other}` 是 lang-chinese 的推荐依赖连带，约 500MB 可安全移除；
`/var/cache/apt/archives` 里 1GB+ 的 .deb 用 `apt-get clean` 释放。
