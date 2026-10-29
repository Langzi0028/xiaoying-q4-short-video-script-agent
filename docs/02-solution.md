# 02 Solution

## Agent 闭环

```text
check_rules -> search_materials -> build_draft -> estimate_duration
-> compress_draft -> estimate_duration -> finish
```

检索无结果时的候选路径由在线模型或 fallback 在受限动作集合中选择：

```text
search_materials -> rewrite_search -> search_materials -> request_more_info
```

模型也可以直接选择 `request_more_info`，不必先改写检索；这避免对素材库不支持的主题进行无意义循环。

每个工具执行后会将安全参数和结果摘要写入 Trace，`decide()` 只接收确定性代码提供的合法动作集合，再根据上一个工具结果选出下一动作。未配置模型时，确定性 fallback 会在“38 秒 > 30 秒”后选择 `compress_draft`；配置了兼容模型时，在线模型可以从同一个受限集合选择动作。在线请求异常时，CLI 只在 stderr 输出异常类型和 fallback 提示，随后降级。规则风险直接阻断；工具异常直接失败；执行计数达到 `max_steps` 后返回 `EXECUTION_LIMIT_REACHED`。

## 组件职责

- `fixtures/scenarios.py`：合成 P01 素材与演示输入；P01 只支持“支持字幕”这一可用事实。
- `tools/`：素材搜索、品牌规则和时长估算；工具彼此独立且可注入故障。
- `graph/workflow.py`：受约束决策循环、时长压缩和 Trace 形成。
- `storage/repositories.py`：保存最终运行 JSON，支持 `show` 查询。
- `cli.py`：CLI 边界，stdout 只输出 JSON，stderr 输出 fallback 提示。

## 安全边界

模型或 fallback 不能访问文件系统、SQLite 或发布工具；在线模型调用只接收允许动作和脱敏计数/时长摘要，不能接收凭据、私有 URL、完整请求或数据库内容。生成脚本只使用检索出的合成素材 ID；压缩只减少镜头时长，不新增事实或来源。数据库只保存请求结果和 Trace，不保存凭据、请求正文或私有 URL。

## 版本与选择

本题采用原生 Python 状态循环，而不是为本题规模额外引入图框架；循环仍完整实现“动作选择 -> 工具执行 -> 结果观察 -> 下一动作”的可审计边界。`langchain-openai` 仅用于可选的 OpenAI-compatible 在线动作选择，读取 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL` 和 `LLM_API_MODE`；当前 `chat_completions` 模式通过 `ChatOpenAI` 接入。外部模型不是运行所必需。采用根包结构 `main.py + short_video_script_agent/`，符合本仓库题目约定，未使用 `src/` 或可编辑安装。
