/**
 * dsh-paper-translate — 学术论文 LaTeX 精翻工作流的 DSH 插件。
 *
 * 把「arXiv 源码抓取 → 编译引擎识别 → 英文/中文编译循环 → 引用一致性校验 →
 * 残留英文扫描 → 按标题打包」封装为 paper_translate_* 系列工具，
 * 供绑定会话里的智能体在执行翻译任务时直接调用；脚本本体来自本套件
 * 仓库的 scripts/ 目录（亦可被智能体按 docs/WORKFLOW.md 手工编排）。
 *
 * 任务完成时可选向绑定会话派发 followup 提示（onDoneFollowupPrompt），
 * 由会话智能体接续用户自己的通知链路（邮件 / IM / 任意工具）。
 *
 * 注入方式（DSH 会话内）：
 *   dev_inject_plugin {"dir": "/path/to/paper-translate-kit/dsh-plugin"}
 * 配置覆盖层：~/.dsh/dsh-paper-translate.json，改后 dev_reload_package 生效。
 */
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { homedir } from "node:os";
import { join } from "node:path";
import { existsSync } from "node:fs";
import z from "@deepseek-ai/schemastery";
import { createUserMessage } from "@deepseek-ai/dsh-llm";
import { defineTool } from "@deepseek-ai/dsh-tools";

const run = promisify(execFile);

export const name = "paper-translate";
export const inject = ["tools"];

/* ─────────────────────────── 配置 schema ─────────────────────────── */

export const Config = z.object({
  /** 套件仓库 scripts/ 目录（含 fetch_arxiv.sh 等）。 */
  scriptsDir: z.string().default(join(homedir(), "paper-translate-kit", "scripts")),
  /** 工作根目录：每篇论文一个 <workdir>/<id>/ 子目录。 */
  workDir: z.string().default(join(homedir(), "paper-translate-work")),
  /** 成品交付目录。 */
  outDir: z.string().default(join(homedir(), "paper-translate-deliver")),
  /** 编译引擎覆盖（auto=由 detect_engine.py 决策）。 */
  engine: z.string().default("auto"),
  /** 中文版引擎（固定 LuaLaTeX，除非用户显式修改）。 */
  zhEngine: z.string().default("lualatex"),
  /** 单步命令超时（毫秒）。 */
  timeoutMs: z.number().default(600_000),
  /** 绑定会话（任务完成 followup 用）：精确 sessionId 优先。 */
  targetSessionId: z.string().default(""),
  /** 绑定会话：按标题子串匹配（次优先）。 */
  targetSessionTitle: z.string().default(""),
  /** 任务成功完成且 package 步骤执行后，向绑定会话派发的提示（空=不派发）。 */
  onDoneFollowupPrompt: z.string().default(""),
});

/* ─────────────────────────── 工具实现 ─────────────────────────── */

async function sh(ctx, cfg, script, args) {
  const bin = join(cfg.scriptsDir, script);
  if (!existsSync(bin)) throw new Error(`脚本不存在: ${bin}（检查 scriptsDir 配置）`);
  const { stdout, stderr } = await run(bin, args, {
    cwd: cfg.workDir,
    timeout: cfg.timeoutMs,
    maxBuffer: 16 * 1024 * 1024,
  });
  return (stdout || "") + (stderr ? `\n[stderr]\n${stderr}` : "");
}

function resolveAgent(ctx, cfg) {
  let agents;
  try {
    agents = ctx.get("agents");
  } catch {
    return null;
  }
  if (!agents) return null;
  for (const agent of agents) {
    if (cfg.targetSessionId && agent.session?.id === cfg.targetSessionId) return agent;
  }
  for (const agent of agents) {
    if (cfg.targetSessionTitle && (agent.session?.title ?? "").includes(cfg.targetSessionTitle)) {
      return agent;
    }
  }
  return null;
}

function notifyDone(ctx, cfg, summary) {
  if (!cfg.onDoneFollowupPrompt) return;
  const agent = resolveAgent(ctx, cfg);
  if (!agent) {
    (ctx.logger ?? console).warn("[paper-translate] 未找到绑定会话，跳过 followup");
    return;
  }
  const message = createUserMessage({
    content: [{ type: "text", text: `${cfg.onDoneFollowupPrompt}\n\n${summary}` }],
    source: { kind: "user" },
  });
  agent.followup(message);
}

/* ─────────────────────────── 插件入口 ─────────────────────────── */

export function apply(ctx, config) {
  const logger = ctx.logger ?? console;

  ctx.effect(() =>
    ctx.tools.register(
      defineTool({
        name: "paper_translate_run",
        description:
          "执行论文翻译工作流的一个步骤。step 可选：" +
          "fetch（抓取 arXiv 源码，args=[arxiv_id]）/" +
          "detect（识别引擎，args=[src_dir]）/" +
          "compile_en（编译英文版，args=[paper_dir, main_tex]）/" +
          "compile_zh（编译中文版，args=[paper_dir, main_tex]）/" +
          "check_citations（引用一致性，args=[src_dir, zh_dir]）/" +
          "check_untranslated（残留英文扫描，args=[zh_pdf]）/" +
          "package（按标题打包，args=[paper_dir]）。",
        parameters: z.object({
          step: z.enum([
            "fetch", "detect", "compile_en", "compile_zh",
            "check_citations", "check_untranslated", "package",
          ]),
          args: z.array(z.string()).default([]),
        }),
        async execute({ step, args }) {
          const A = (xs) => [...args, ...(xs ?? [])];
          try {
            switch (step) {
              case "fetch":
                return { ok: true, output: await sh(ctx, config, "fetch_arxiv.sh", A([])) };
              case "detect":
                return { ok: true, output: await sh(ctx, config, "detect_engine.py", A([])) };
              case "compile_en": {
                const [dir, main] = args;
                return { ok: true, output: await sh(ctx, config, "compile_latex.sh", [dir, main, config.engine]) };
              }
              case "compile_zh": {
                const [dir, main] = args;
                return { ok: true, output: await sh(ctx, config, "compile_latex.sh", [dir, main, config.zhEngine]) };
              }
              case "check_citations": {
                const [src, zh] = args;
                return { ok: true, output: await sh(ctx, config, "check_citations.py", [src, zh]) };
              }
              case "check_untranslated": {
                const [pdf] = args;
                const { stdout } = await run("pdftotext", [pdf, "-"], { timeout: config.timeoutMs });
                const probe = await run("python3", ["-"], { input: stdout, timeout: 30_000 })
                  .catch(() => null);
                // 直接调脚本（脚本从 stdin 读）
                const out = await new Promise((resolve, reject) => {
                  const p = execFile(
                    "python3",
                    [join(config.scriptsDir, "check_untranslated.py")],
                    { timeout: 30_000 },
                    (err, stdout2) => (err ? reject(err) : resolve(stdout2)),
                  );
                  p.stdin?.end(stdout);
                });
                return { ok: true, output: out };
              }
              case "package": {
                const [dir] = args;
                const out = await sh(ctx, config, "package_output.py", [dir, "--out", config.outDir]);
                notifyDone(ctx, config, `论文打包完成：${dir} → ${config.outDir}`);
                return { ok: true, output: out };
              }
              default:
                return { ok: false, error: `未知 step: ${step}` };
            }
          } catch (e) {
            logger.warn?.(`[paper-translate] ${step} 失败: ${e.message}`);
            return { ok: false, error: e.message, stderr: e.stderr?.slice?.(0, 4000) ?? "" };
          }
        },
      }),
    ),
  );

  ctx.effect(() =>
    ctx.tools.register(
      defineTool({
        name: "paper_translate_status",
        description: "检查本机 TeX/中文字体/脚本环境是否就绪。",
        parameters: z.object({}),
        async execute() {
          const which = async (b) => {
            try {
              const { stdout } = await run("bash", ["-c", `command -v ${b}`]);
              return stdout.trim();
            } catch {
              return "(缺失)";
            }
          };
          const engines = {};
          for (const b of ["pdflatex", "xelatex", "lualatex", "bibtex", "latexmk", "gs"]) {
            engines[b] = await which(b);
          }
          let fonts = "(未知)";
          try {
            const { stdout } = await run("bash", ["-c", "fc-list :lang=zh | head -3"]);
            fonts = stdout.trim() || "(缺失)";
          } catch { /* ignore */ }
          return {
            ok: true,
            scriptsDir: config.scriptsDir,
            scriptsDirExists: existsSync(config.scriptsDir),
            engines,
            zhFonts: fonts,
            workDir: config.workDir,
            outDir: config.outDir,
          };
        },
      }),
    ),
  );

  logger.info?.("[paper-translate] 已注入 paper_translate_run / paper_translate_status 工具");
}
