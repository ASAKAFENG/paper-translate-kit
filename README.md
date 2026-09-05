# paper-translate-kit

**学术论文 LaTeX 精翻工作流套件** —— 把「下载 arXiv 源码 → 英文原版编译 → LaTeX 精翻 → 中文编译 → 质量验收 → 按标题打包交付」的完整流程，封装成 AI 编码智能体（ZCode / DeepSeek Harness）可直接使用的预设插件与脚本库。

English intro: this kit turns the end-to-end workflow of *precision-translating academic LaTeX papers into Chinese and compiling both language versions* into ready-to-use agent assets: a ZCode skill, a DeepSeek Harness (DSH) plugin, and a set of battle-tested shell/python helpers.

## 这套工作流解决了什么

直接让 AI 翻译 `.tex` 论文，通常会在三处翻车：

1. **编译环境**：CVPR/ICML/ECCV/IEEE 模板各不相同，中文需要 ctex，且存在大量坑（`axessibility` 仅支持 pdfLaTeX、cairo 生成的插图 PDF 让 XeTeX 崩溃、XeTeX 的非确定性内部错误、`icml2026.sty` 的 pdfTeX 页寸原语、`bibunits` 需要额外 bibtex、`\input{bbl}` 型论文绝不能跑 bibtex……）。
2. **翻译质量**：公式、`\cite`、`\label/\ref`、实验数字一旦被改动就是事故；术语需要"首次出现括注英文、后文纯中文"的一致约定。
3. **验收标准**：什么算"翻完了、编译对了"必须可检验——引用零警告、残留英文扫描、渲染抽查、命名规范。

本套件把以上全部沉淀为**可复用资产**。

## 仓库结构

```
paper-translate-kit/
├── docs/
│   ├── WORKFLOW.md          # ★ 核心工作流规范（九个阶段，含编译排错手册）
│   ├── TERMINOLOGY.md       # 翻译约定与术语表（含 6D 位姿领域示例词库）
│   └── CHECKLIST.md         # 交付验收清单
├── scripts/                 # 与智能体/人类均可直接使用的工具脚本
│   ├── fetch_arxiv.sh       # 下载并解压 arXiv 源码
│   ├── detect_engine.py     # 识别文档模板 → 推荐编译引擎
│   ├── compile_latex.sh     # 通用编译循环（自动 bibtex / bibunits / bbl-only 检测）
│   ├── setup_chinese.sh     # 从英文源码克隆中文目录并注入 ctex/Noto 适配
│   ├── check_citations.py   # 比对译/原文 \cite \label \ref 完全一致（含顺序）
│   ├── check_untranslated.py# 在编译出的 PDF 文本中扫描残留英文正文
│   └── package_output.py    # 按论文标题命名 PDF 并打包 src-en/src-zh/说明.txt
├── zcode-skill/paper-translate/SKILL.md   # ZCode 技能（复制到 ~/.zcode/skills/ 即用）
├── dsh-plugin/              # DeepSeek Harness 插件（注入 paper_* 系列工具）
│   ├── package.json
│   ├── lib/index.js
│   └── scripts/link-deps.sh
└── examples/terminology-6dpose.md  # 领域术语表示例
```

## 快速开始

### 方式一：ZCode 技能（最简）

```bash
git clone https://github.com/ASAKAFENG/paper-translate-kit.git
mkdir -p ~/.zcode/skills
cp -r paper-translate-kit/zcode-skill/paper-translate ~/.zcode/skills/
# 之后在 ZCode 对话中直接说：
#   「把 arXiv:2403.19527 的论文精翻成中文，中英文都编译，按标题命名打包」
```

技能会引导智能体按 `docs/WORKFLOW.md` 执行，并调用 `scripts/` 下的脚本完成机械性步骤。

### 方式二：DeepSeek Harness 插件

```bash
git clone https://github.com/ASAKAFENG/paper-translate-kit.git
cd paper-translate-kit/dsh-plugin
bash scripts/link-deps.sh          # 软链宿主 peer 依赖（同 dsh-mail-responder 约定）
# 在 DSH 会话内注入：
#   dev_inject_plugin {"dir": "/path/to/paper-translate-kit/dsh-plugin"}
```

注入后智能体获得 `paper_translate_*` 系列工具（抓取源码 / 编译 / 校验 / 打包），
配置文件位于 `~/.dsh/dsh-paper-translate.json`，支持任务完成后向绑定会话派发
followup 提示（可对接你自己的通知链路，如邮件、IM 等）。

### 方式三：不用智能体，纯手工

所有脚本都可以独立运行，`docs/WORKFLOW.md` 同时是一份人类可读的操作手册：

```bash
scripts/fetch_arxiv.sh 2403.19527 work/
scripts/compile_latex.sh work/2403.19527/src main.tex auto
scripts/setup_chinese.sh work/2403.19527/src
scripts/compile_latex.sh work/2403.19527/zh main.tex lualatex
python3 scripts/check_citations.py work/2403.19527/src work/2403.19527/zh
python3 scripts/package_output.py work/2403.19527 --out deliver/
```

## 翻译约定（摘要）

- 专业名词**首次出现**时括注英文原文：`关键点（keypoint）`、`零样本（zero-shot）`；后文直接用中文。
- `\cite{...}`、`\label` / `\ref` 与原文**逐键核对、顺序一致**；参考文献列表保持英文。
- 公式、实验数据、图表编号一律不动；图题、表题、表头、算法注释翻译。
- 交付物：`论文标题-en.pdf`、`论文标题-zh.pdf`、`src-en/`、`src-zh/`、`说明.txt`。

完整规则见 `docs/TERMINOLOGY.md` 与 `docs/CHECKLIST.md`。

## 实战验证

本工作流已在 10 篇论文（CVPR / ICCV / ECCV / ICML / IEEE 期刊五类模板）上完整跑通，
累计修复的兼容性问题记录在 `docs/ENGINE-GUIDE.md`，包括：

- pdfLaTeX 专属宏包（`axessibility`）对 XeLaTeX/LuaLaTeX 的兼容处理
- cairo 生成的插图 PDF 导致 XeTeX `bad native font flag` 崩溃（Ghostscript 转换方案）
- XeTeX 非确定性内部错误 → 切换 LuaLaTeX 的决策规则
- `icml2026.sty` 的 `\pdfpagewidth` 缺失 → LuaLaTeX 兼容垫片
- `bibunits`、`\input{bbl}`、无 `main.bib` 等特殊文献引用形态的编译策略

## License

MIT
