# 短视频脚本 Agent 设计

## 目标

构建一个可从题目根目录运行的 Python CLI Agent。它根据主题、受众、时长、风格、品牌规则和合成素材库，生成可编辑的短视频脚本；输出标题、分镜、旁白/字幕、预计总时长、素材来源 ID、风险和任务状态。

系统必须展示可观察的 Agent 闭环：模型选择合法动作，工具执行并返回摘要，模型根据结果选择下一动作或结束。模型配置缺失或请求失败时，系统使用明确标注的确定性 fallback，只用于边界验证，不宣称为真实模型能力。

## 范围

- 建立独立题目目录 `xiaoying-q4-short-video-script-agent/`，使用 `main.py + short_video_script_agent/` 根包结构。
- 提供受约束 LangGraph 工作流、SQLite 运行记录、Pydantic 输入/输出模型和 OpenAI-compatible 可选模型客户端。
- 实现安全本地工具：素材检索、事实与品牌规则检查、脚本时长估算，以及草稿生成和压缩。
- 提供可审计 Trace、执行步数上限、失败和缺失信息处理。
- 提供测试、三个或更多真实运行证据、README 和评估文档。

## 非目标

- 不接入真实媒体资产、商业素材库、发布平台或生产内容管理系统。
- 不生成视频文件、图片或语音，也不实现 GUI、HTTP API、用户权限或多租户功能。
- 不保证在线模型可用；无本地配置时必须安全降级。

## 外部接口

`python main.py run --topic <text> --audience <text> --target-seconds <int> --style <text> [--material-id <id>] [--max-steps <int>]`

最终结果是 stdout 上的一行 JSON。stderr 仅输出简短的配置、fallback 或异常类型提示。JSON 包含：

- `status`：`completed`、`needs_info`、`blocked`、`failed` 或 `incomplete`。
- `title`、`shots`、`total_estimated_seconds`、`material_source_ids`、`risks`。
- `decision_source`：`live_llm` 或 `fallback`。
- `trace`：逐步记录节点、动作、脱敏参数、返回摘要、下一动作和简短决策理由。

该接口是新题目的独立合同，不更改已有 Q1/Q2 的 API、数据、状态或存储协议。

## 工作流

```text
validate_input
-> find_materials
-> check_rules
-> decide_next_action
-> build_draft
-> estimate_duration
-> decide_next_action
-> compress_draft / request_more_info / finish
```

决策节点只接收确定性代码计算出的 `legal_actions`。每次模型或 fallback 的输出均经结构化校验；不在允许集合中的动作被拒绝并安全终止。工具返回结果会写入状态和 Trace 后，再进入下一次决策。

关键动态路径：

1. `P01`、30 秒：检索成功、首稿估算 38 秒；决策改为 `compress_draft`，复估达到目标后完成。
2. 无检索结果：决策在安全的改写检索与请求补充信息之间选择；若仍无结果，返回 `needs_info`，不编造素材来源。
3. 规则风险或工具错误：返回 `blocked` 或 `failed`，不伪造完成结果。
4. 达到 `max_steps`：返回 `incomplete` 和明确错误码，不再继续循环。

## 数据与安全边界

- SQLite 仅存储合成素材、运行摘要和 checkpoint；运行数据库被 Git 忽略。
- 模型不能访问 SQLite、文件系统或网络工具，只能选择应用提供的合法动作。
- 合成素材包含明确的事实、品牌和可用性规则；最终结果不能将不存在的素材 ID 写入脚本。
- `.env` 为可选本地配置，shell 或 IDE 环境变量优先；文档和证据中不保存任何凭据、私有 URL 或请求正文。

## 测试与证据

遵循 test-first：为输入验证、首稿超时压缩、检索无结果、规则阻断、工具失败、执行上限、Trace 完整性、CLI stdout/stderr 分离和 fallback/LIVE 标识分别创建回归测试。每个新行为先运行并确认测试以预期方式失败，再实施最小代码使其通过。

`examples/` 至少保存三组来自实际 CLI 运行的输入、最终 JSON 和 Trace；`docs/03-evaluation.md` 将每项验收标准链接到对应测试和证据。

## 验收标准

- 可按 README 命令安装、执行和运行完整测试套件。
- 交付结果字段完整，分镜时长可加总且可追溯至有效素材来源 ID。
- Trace 包含节点、工具/动作、参数摘要、结果摘要、下一动作和简短理由，不泄露思维链或秘密。
- 至少两个不同工具结果导致不同后续动作，并存在执行上限的未完成状态。
- 缺配置、LLM 失败、空/错误输入、素材不足和工具错误均安全终止或降级。

