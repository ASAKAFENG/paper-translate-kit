# 学术论文 LaTeX 精翻工作流规范（九阶段）

> 本文档是整套套件的核心。任何智能体或人类执行论文精翻任务时，按此流程逐步推进。
> 每个阶段都定义了**输入、动作、产出、验收条件**。跳过阶段或验收不达标都视为未完成。

---

## 阶段 0：任务受理与环境确认

**输入**：用户给出的论文标识（arXiv ID / URL / 本地 tar.gz）与交付要求。

**动作**：
1. 确认本机 TeX 环境：`which pdflatex xelatex lualatex bibtex latexmk`。
   缺失时的 Debian/Ubuntu 安装集：
   ```bash
   sudo apt-get install -y texlive-xetex texlive-latex-recommended texlive-latex-extra \
     texlive-fonts-recommended texlive-lang-chinese texlive-science texlive-bibtex-extra \
     texlive-publishers texlive-luatex latexmk
   ```
   按需追加：`texlive-fonts-extra`（仅当缺 bbm 等冷门宏包，体积 ~1.8GB，慎装）、
   `texlive-luatex`（luatexbase/luatexja）、`gs`（ghostscript，修插图）。
2. 确认中文字体：`fc-list :lang=zh | head`。无 Fandol 时 ctex 用 `fontset=none` + 系统
   Noto CJK（推荐固定如此，见阶段 5）。

**产出**：环境就绪，或安装清单已执行。

---

## 阶段 1：源码获取

```bash
scripts/fetch_arxiv.sh <arxiv_id> <workdir>
```

- 优先 `https://arxiv.org/e-print/<id>`（加 User-Agent，限速，sleep 2-5s）。
- `file` 判断格式：gzip/tar 解压；单文件 gzip 直接解为 `.tex`。
- 产出 `workdir/<id>/src/`，清点：主 tex、文档类/样式文件、图目录、bbl/bib。

**验收**：`ls src` 能看到主 tex 与全部插图。

---

## 阶段 2：结构勘察

**动作**（决定后续所有编译策略，不可跳过）：

1. **编译器**：读 `00README.json` 的 `process.compiler`（arXiv 官方指定）；
   无此文件则看模板：CVPR/ICML/ECCV/IEEE → pdfLaTeX（除非含中文）；
   任何含 `\usepackage[accsupp]{axessibility}` 的工程**必须** pdfLaTeX（原版编译）。
2. **文献形态**（决定是否/如何跑 bibtex）：
   - 有 `\bibliography{xxx}` + 有 `.bib` → 正常 `bibtex main`；
   - 只有 `\input{main.bbl}` / 自带 `.bbl` → **绝不能跑 bibtex**（会把 bbl 清空导致引用全灭）；
   - `bibunits`（`\begin{bibunit}...\putbib`）→ 额外 `bibtex bu1`（aux 名为 `bu1.aux`）；
   - `\bibliographystyle` 引用的 `.bst` 缺失 → 装 `texlive-publishers`（IEEEtran.bst 等）或随包查找。
3. **插图体检**：`file` 检查 PDF 插图 Producer；
   cairo 1.15+ 生成的 PDF-1.5（交叉引用流）会让 XeTeX 报
   `Unable to load picture` / `Division by 0` —— 全部用
   `gs -q -o out.pdf -sDEVICE=pdfwrite in.pdf` 转换后覆盖（画面不变）。
4. **主文件形态**：单文件 or `sec/` 分文件；`\input` 图题（`fig/*.tex`）；
   自定义宏（`\ourmethod` 等，翻译时必须保留）。

**产出**：引擎决策记录（写入 `说明.txt` 草稿）。

---

## 阶段 3：英文原版编译（EN）

```bash
scripts/compile_latex.sh <src_dir> <main.tex> auto   # auto=按阶段2决策
```

编译循环：`引擎 → (bibtex 按需) → 引擎 → 引擎`，然后：

- `grep -c "Warning: Citation" <log>` 必须为 **0**；
- `grep -E "^!" <log>` 必须为空；
- `pdfinfo` 记录页数。

**常见报错与对策**（完整版见 `docs/ENGINE-GUIDE.md`）：

| 症状 | 原因 | 对策 |
|---|---|---|
| `File 'bbm.sty' not found` | 冷门字体宏包 | 装 `texlive-fonts-extra`，或手动放 `~/texmf` |
| `Unable to load picture ... Division by 0` | cairo PDF 与 xetex 不兼容 | gs 重写该插图 |
| `IEEEtran.bst not found` | 缺 publishers 套件 | `apt install texlive-publishers` |
| `Undefined \pdfglyphtounicode`（xelatex/lualatex） | axessibility 仅支持 pdfTeX | 原版用 pdfLaTeX；中文版禁用该宏包 |
| `bad native font flag in map_char_to_glyph`（xelatex） | XeTeX 内部 bug，非确定性 | 改用 LuaLaTeX |
| `File 'luatexbase.sty' not found`（lualatex） | 缺套件 | `apt install texlive-luatex` |
| `Missing \pdfpagewidth`（lualatex + icml2026） | 样式用 pdfTeX 原语 | 导言区加 `\newdimen\pdfpagewidth \newdimen\pdfpageheight` |

**产出**：`<标题>-en.pdf`（标题从 `\title{}` 提取；副标题/宏需展开）。

---

## 阶段 4：中文翻译

**在克隆出的 `zh/` 目录内翻译，`src/` 永远保持原样**（`scripts/setup_chinese.sh` 负责克隆）。

### 4.1 翻译范围

翻译：正文所有散文段落、摘要、`\section/\subsection` 标题、图题 `\caption`、
表题与表头（Method→方法、Prior→先验、Ours→本文、mean→平均……）、
算法伪注释、致谢、关键词。
不翻译：公式、实验数字、`\cite`/`\ref`、参考文献列表、行内命令与宏定义、
作者姓名（拼音保留）、被注释掉的草稿（% 行与 `\begin{comment}` 块原样保留）、
图表内烘焙的英文文字（图片本身改不了，在说明.txt 里注明）。

### 4.2 术语规则（详见 docs/TERMINOLOGY.md）

- 专业名词**首次出现**：`中文（English）`；后文纯中文；
- 方法名/模型名/数据集名保留英文（AG-Pose、REAL275、BOP）；
- "Ours/本文"统一译法；中英文之间留空格由 ctex 自动处理。

### 4.3 引用与标签

`\cite`、`\label`、`\ref` **一个都不能动**。完成后必须跑：

```bash
python3 scripts/check_citations.py <src_dir> <zh_dir>
# 输出 ALL MATCH 才算过；键集合与出现顺序都必须一致
```

### 4.4 工程技巧

- 大文件翻译用"精确字符串替换"时，注意：源码可能混用直引号 `'` 与弯引号 `’`、
  行内换行不一致 → 用空白自适应正则（`\s+` 匹配任意空白串）或首尾标记切片替换；
- 替换脚本的**替换文本**必须转义反斜杠（re.subn 的 repl 中 `\c` 是坏转义）；
  raw 字符串与双重转义叠加会让文件里出现 `\\section` 这类损坏——改完必须全文
  `grep '\\\\[a-zA-Z]'` 自检；
- 浮动体（`figure*`）会改变分页，定位"某段文字触发编译错误"时，先注释浮动体再二分。

**产出**：`zh/` 目录完整翻译版源码。

---

## 阶段 5：中文适配

`scripts/setup_chinese.sh` 自动完成（亦可手工）：

1. 在导言区（hyperref 之前）注入：
   ```latex
   \usepackage[UTF8,fontset=none]{ctex}
   \setCJKmainfont[BoldFont={Noto Serif CJK SC Bold}]{Noto Serif CJK SC}
   \setCJKsansfont[BoldFont={Noto Sans CJK SC Bold}]{Noto Sans CJK SC}
   \setCJKmonofont{Noto Sans Mono CJK SC}
   ```
   （`fontset=none` + 显式系统字体，规避 Fandol 缺失与平台字体差异。）
2. 注释掉仅支持 pdfLaTeX 的宏包：`axessibility`（留一行中文注释说明原因）。
3. 引擎相关垫片：
   - icml2026：在 `\usepackage[accepted]{icml2026}` **之前**加
     `\newdimen\pdfpagewidth \newdimen\pdfpageheight`；
4. `\title` 译为中文（可括注英文原题），作者单位译中文，姓名拼音保留。
5. **引擎选型：中文版一律优先 LuaLaTeX**（ctex 完整支持，且避开 XeTeX 的
   `bad native font flag` 非确定性崩溃；XeLaTeX 仅作备选）。

---

## 阶段 6：中文编译（ZH）

```bash
scripts/compile_latex.sh <zh_dir> <main.tex> lualatex
```

- 循环同阶段 3（含 bibtex 策略，与英文版**保持一致**）；
- 页数通常比英文版多 0-2 页（中文更紧凑或标题换行），正常；
- `pdftotext -f 1 -l 1` 抽首页文本，确认标题/摘要中文正常、无豆腐块；
- 若遇 XeTeX 特有错误且无法定位 → 直接换 LuaLaTeX，不要恋战。

**产出**：`<中文标题>-zh.pdf`。

---

## 阶段 7：质量验收（不可省略）

1. **引用零警告**：`grep -c "Warning: Citation"` == 0（EN 与 ZH 都要）。
2. **引用一致性**：`check_citations.py` 输出 ALL MATCH。
3. **残留英文扫描**：
   ```bash
   pdftotext <zh.pdf> - | python3 scripts/check_untranslated.py
   ```
   重点扫：`\section/\subsection` 标题、`\caption`、`\paragraph` 标题——
   这三处是最高频漏译点（实测经验）。
4. **渲染抽查**：每篇至少渲染 标题页 + 1 个正文密集页（公式/表格）为 PNG，
   人工或评审子代理检查：无重叠、无溢出、无缺字、图表完整、中英混排自然。
   发现问题 → 修复 → 重编译 → 复查该页。
5. **插图内文字**：图片内部烘焙的英文属原素材，无法翻译——在 `说明.txt` 中注明即可。

**产出**：验收通过的 EN/ZH 双 PDF。

---

## 阶段 8：按标题命名与打包

```bash
python3 scripts/package_output.py <paper_dir> --out <deliver_dir>
```

命名规范：`<论文标题>-en.pdf` / `<中文译名>-zh.pdf`（标题取自 `\title{}`，
中文译名由翻译给出；文件名中的 `:` 等字符 Linux 允许，保留原题）。

每个论文包目录结构：

```
<论文名>/
├── <标题>-en.pdf
├── <中文标题>-zh.pdf
├── src-en/          # 英文原始源码（未改动；构建产物清理：aux/log/out/bbl* 等）
├── src-zh/          # 中文翻译源码
└── 说明.txt         # 标题、编译引擎与命令、翻译约定、特别注意事项
```

---

## 阶段 9：交付与通知（可选）

- 将全部论文包放到用户指定目录；批量任务可再汇总一个总包 zip。
- DSH 插件用户可配置 `onDoneFollowupPrompt`：任务完成时向绑定会话派发一条
  followup 消息，由会话里的智能体执行你自己的通知链路（邮件/IM/任意工具）。

---

## 附：多篇批量任务的组织方式

```
work/
├── batch1/  # 每篇一个 <id>/ 目录：{src/, zh/, out/}
└── batch2/
deliver/
├── <论文标题>-en.pdf / <中文标题>-zh.pdf …   # 全部成品
└── 每篇一个 zip（可选）
```

清理规则（交付后）：删除一切中间态（aux/log/out/bbl、渲染 PNG、pkg stage），
仅保留成品 PDF 与总包 zip。
