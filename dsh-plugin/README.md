# dsh-paper-translate

DeepSeek Harness (DSH) 插件：把学术论文 LaTeX 精翻工作流的机械性步骤
封装为 `paper_translate_*` 工具注入会话。智能体负责翻译本身（见套件
`docs/WORKFLOW.md`），工具负责可脚本化的部分。

## 安装

```bash
cd dsh-plugin
bash scripts/link-deps.sh     # 软链宿主 peer 依赖（同 dsh-mail-responder 约定）
# 在 DSH 会话内：
dev_inject_plugin {"dir": "/path/to/paper-translate-kit/dsh-plugin"}
```

## 配置

`~/.dsh/dsh-paper-translate.json`（与 schemastery 默认值合并，改后 `dev_reload_package` 生效）：

```jsonc
{
  "scriptsDir": "~/paper-translate-kit/scripts",   // 套件脚本目录
  "workDir": "~/paper-translate-work",             // 每篇论文的工作目录
  "outDir": "~/paper-translate-deliver",           // 成品交付目录
  "engine": "auto",                                // 英文版引擎覆盖
  "zhEngine": "lualatex",                          // 中文版引擎（默认固定）
  "targetSessionId": "",                           // 完成通知的绑定会话（可选）
  "onDoneFollowupPrompt": ""                       // 非空时，打包成功后向绑定会话派发
                                                   // 该提示 + 完成摘要（可对接邮件/IM 通知）
}
```

## 工具

### paper_translate_run

| step | args | 作用 |
|---|---|---|
| fetch | `[arxiv_id]` | 下载并解压 arXiv 源码到 workDir |
| detect | `[src_dir]` | 识别模板与推荐编译引擎 |
| compile_en | `[paper_dir, main.tex]` | 英文版编译循环（含 bibtex/bibunits 策略） |
| compile_zh | `[paper_dir, main.tex]` | 中文版编译循环（LuaLaTeX） |
| check_citations | `[src_dir, zh_dir]` | \cite/\label/\ref 一致性比对（ALL MATCH 才过） |
| check_untranslated | `[zh_pdf]` | 编译出的 PDF 中扫描残留英文标题/图注 |
| package | `[paper_dir]` | 按论文标题命名 PDF、组装 src-en/src-zh/说明.txt；成功后触发 onDoneFollowup |

### paper_translate_status

检查 pdflatex/xelatex/lualatex/bibtex/latexmk/gs 与中文字体是否就绪。

## 翻译本身由智能体完成

工具只覆盖可脚本化步骤。翻译质量来自智能体遵循套件的翻译约定
（`docs/TERMINOLOGY.md`：术语首现括注英文、`\cite` 零改动、公式数据不动、
标题/图题/表头翻译），以及 `docs/CHECKLIST.md` 的验收清单。
