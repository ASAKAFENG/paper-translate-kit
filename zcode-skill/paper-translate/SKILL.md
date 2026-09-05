---
name: paper-translate
description: 学术论文 LaTeX 精翻工作流：下载 arXiv 源码、英文原版编译、按术语约定精翻成中文、中文编译、引用一致性校验、渲染验收、按标题命名打包交付。当用户要求"翻译论文 / 精翻 / 中英对照编译 / arXiv 论文翻译"时使用。
---

# 学术论文 LaTeX 精翻

把一篇（或一批）英文 LaTeX 论文翻译为中文，并交付**中英双语编译 PDF + 双语源码包**。
完整规范见套件仓库的 `docs/WORKFLOW.md`（九阶段流程）与 `docs/ENGINE-GUIDE.md`
（编译排错手册）；本文件是执行摘要。

## 前置

- 脚本位置：优先使用本套件仓库 `scripts/` 下的工具（`fetch_arxiv.sh`、
  `detect_engine.py`、`compile_latex.sh`、`setup_chinese.sh`、
  `check_citations.py`、`check_untranslated.py`、`package_output.py`）。
- TeX 环境：pdflatex/xelatex/lualatex/bibtex/latexmk；缺失按 WORKFLOW.md 阶段 0 安装。
- 中文字体：Noto Serif/Sans CJK SC（ctex 用 `fontset=none` 显式指定）。

## 九阶段流程（摘要）

1. **获取**：`fetch_arxiv.sh <id> <workdir>` → `src/`。
2. **勘察**：`detect_engine.py` 定引擎；检查文献形态（标准 bibtex / `\input{bbl}`
   禁止 bibtex / bibunits 需额外 `bibtex bu1`）；插图 PDF 用 `file` 查 Producer，
   cairo 生成的用 `gs -sDEVICE=pdfwrite` 重写。
3. **英文编译**：`compile_latex.sh <src> <main> auto`；验收 = 零错误 + 引用零警告。
4. **翻译**：克隆 `zh/`，逐文件精翻。铁律：
   - `\cite`/`\label`/`\ref` 一个不动；参考文献保持英文；
   - 公式、实验数字、图表编号不动；注释行与 comment 环境原样保留；
   - 术语首现括注英文（`关键点（keypoint）`），全文同译；方法名/数据集名保留英文；
   - 章节标题、图题、表题、表头、算法注释是**最高频漏译点**，逐个过。
5. **中文适配**：`setup_chinese.sh`（注入 ctex+Noto、禁用 axessibility）；
   `\title`/单位译中文，姓名保留拼音；icml2026 需页寸垫片。
6. **中文编译**：`compile_latex.sh <zh> <main> lualatex`（中文版一律优先 LuaLaTeX，
   规避 XeTeX 非确定性崩溃）。
7. **验收**：
   - `check_citations.py <src> <zh>` 必须 ALL MATCH；
   - `pdftotext <zh.pdf> - | check_untranslated.py` 扫残留英文标题/图注；
   - 渲染标题页 + 1 个密集正文页检查重叠/溢出/缺字；
   - 引用零警告（EN/ZH 都要）。
8. **打包**：`package_output.py` → `<标题>-en.pdf`、`<中文标题>-zh.pdf`、
   `src-en/`、`src-zh/`、`说明.txt`（含编译命令与特别注意事项）。
9. **交付**：放到用户指定目录；批量任务附收录清单；完成后按用户要求通知。

## 高频坑速查（详见 ENGINE-GUIDE.md）

| 症状 | 处理 |
|---|---|
| axessibility 报 `\pdfglyphtounicode` 未定义 | 原版用 pdfLaTeX；中文版注释该宏包 |
| 插图 `Unable to load picture`+`Division by 0` | cairo PDF：gs 重写 |
| XeTeX `bad native font flag` | 换 LuaLaTeX，勿重试 |
| icml2026 缺 `\pdfpagewidth`（LuaLaTeX） | 加 `\newdimen\pdfpagewidth \newdimen\pdfpageheight` |
| `IEEEtran.bst` 缺失 | `apt install texlive-publishers` |
| 对 `\input{bbl}` 型论文跑了 bibtex | 从原始 tar 恢复 bbl，之后禁跑 |

## 批量任务

多篇时按 `work/<batch>/<id>/{src,zh,out}` 组织；交付目录只放成品 PDF 与每篇 zip
（或一个总包）；完成后清理全部中间产物。
