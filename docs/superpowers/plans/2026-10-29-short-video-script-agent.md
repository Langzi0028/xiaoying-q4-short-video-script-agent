# 短视频脚本 Agent Implementation Plan

> **Historical planning record:** This document records the pre-implementation plan and may list superseded files, framework choices, and unchecked task steps. It is not delivery evidence. Review `docs/02-solution.md`, `docs/03-evaluation.md`, the source code, tests, and `examples/` for the implemented system and verified results.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个可运行、可审计的短视频脚本 Agent，它基于合成素材和规则生成短脚本，并通过工具结果动态决定压缩、补充信息或结束。

**Architecture:** 使用 Python CLI、Pydantic 数据模型和 LangGraph 状态图。确定性代码提供合法动作和工具结果；可选 OpenAI-compatible 模型只从合法动作中做结构化选择，缺配置/失败时使用带明确标识的 fallback。SQLite 存储合成素材和运行摘要，Trace 被包含在最终 JSON 和 `examples/` 证据中。

**Tech Stack:** Python 3.11+, LangGraph, Pydantic v2, LangChain OpenAI, python-dotenv, Typer, SQLite, pytest。

---

## 预定文件结构

- `main.py`：唯一直接入口，只导入并调用 CLI `main()`。
- `short_video_script_agent/models.py`：请求、素材、分镜、工具结果和最终响应的 Pydantic 合同。
- `short_video_script_agent/config.py`：`.env` 与环境变量读取，环境优先级和无密钥 fallback 提示。
- `short_video_script_agent/fixtures/scenarios.py`：安全的合成素材、P01 以及演示输入。
- `short_video_script_agent/tools/`：检索、规则校验、时长估算和失败注入，彼此无模型依赖。
- `short_video_script_agent/llm/`：受限的动作选择与安全的 fallback / live LLM 客户端。
- `short_video_script_agent/graph/`：TypedDict 状态、节点、路由和 LangGraph 工作流。
- `short_video_script_agent/storage/`：SQLite 初始化和运行摘要存取。
- `short_video_script_agent/presentation.py`：机器可读 JSON 输出和安全 Trace 格式。
- `short_video_script_agent/cli.py`：`run`、`demo`、`show` 和 `main` 命令。
- `tests/`：按行为拆分的 regression tests；每项生产行为先有 failing test。
- `scripts/generate_examples.py`：真实运行三个以上固定演示场景，写入 `examples/`。
- `README.md`、`docs/01...05`、`.env.example`、`.gitignore`、`requirements.txt`：交付与安全材料。

### Task 1: 创建题目骨架与不可提交运行产物规则

**Files:**
- Create: `xiaoying-q4-short-video-script-agent/main.py`
- Create: `xiaoying-q4-short-video-script-agent/short_video_script_agent/__init__.py`
- Create: `xiaoying-q4-short-video-script-agent/tests/test_conventions.py`
- Create: `xiaoying-q4-short-video-script-agent/.gitignore`
- Create: `xiaoying-q4-short-video-script-agent/.env.example`
- Create: `xiaoying-q4-short-video-script-agent/requirements.txt`
- Create: `xiaoying-q4-short-video-script-agent/data/.gitkeep`

- [ ] **Step 1: 写入会失败的仓库约定测试。**

```python
def test_root_entrypoint_and_required_delivery_paths_exist(project_root):
    assert (project_root / "main.py").is_file()
    assert (project_root / "short_video_script_agent").is_dir()
    assert (project_root / "data" / ".gitkeep").is_file()
    assert (project_root / ".env.example").is_file()
```

- [ ] **Step 2: 从 Q4 题目根目录运行测试，确认它因缺少文件失败。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_conventions.py -v`  
Expected: FAIL，缺少入口或目录。

- [ ] **Step 3: 创建最小骨架。**

```python
# main.py
from short_video_script_agent.cli import main

if __name__ == "__main__":
    main()
```

`.gitignore` 必须忽略 `.env`、`.idea/`、`.venv/`、Python 缓存、pytest 缓存和 `data/*.db`，但不能忽略 `data/.gitkeep`。`.env.example` 只列出 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`。

- [ ] **Step 4: 重新运行约定测试，确认通过。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_conventions.py -v`  
Expected: PASS。

- [ ] **Step 5: 提交独立骨架。**

```powershell
git add -- xiaoying-q4-short-video-script-agent
git commit -m "chore: scaffold q4 script agent"
```

### Task 2: 定义输入/输出合同和合成素材夹具

**Files:**
- Create: `short_video_script_agent/models.py`
- Create: `short_video_script_agent/enums.py`
- Create: `short_video_script_agent/fixtures/__init__.py`
- Create: `short_video_script_agent/fixtures/scenarios.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: 写入输入验证与输出字段的失败测试。**

```python
def test_request_rejects_non_positive_target_seconds():
    with pytest.raises(ValidationError):
        ScriptRequest(topic="牙齿护理", audience="新手父母", target_seconds=0, style="轻快")

def test_response_exposes_required_script_fields():
    response = ScriptResponse(...)
    assert response.model_dump().keys() >= {
        "status", "title", "shots", "total_estimated_seconds",
        "material_source_ids", "risks", "trace", "decision_source",
    }
```

- [ ] **Step 2: 运行模型测试并确认正确失败。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_models.py -v`  
Expected: FAIL，无法导入模型。

- [ ] **Step 3: 最小实现模型与夹具。**

定义 `RunStatus`（`completed`、`needs_info`、`blocked`、`failed`、`incomplete`）、`DecisionSource`（`live_llm`、`fallback`）与 `ErrorCode`。`ScriptRequest` 要求非空主题/受众/风格和正数目标秒数。`Shot` 含 `index`、`visual_description`、`voiceover`、`subtitle`、`estimated_seconds`、`material_source_ids`。`ScriptResponse` 含全量交付字段。

在夹具内定义 P01（仅包含“支持字幕”的产品事实）以及足够命中的合成素材；另定义无匹配和规则风险数据，保证测试永远不访问网络。

- [ ] **Step 4: 运行模型测试确认通过。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_models.py -v`  
Expected: PASS。

- [ ] **Step 5: 提交合同。**

```powershell
git add -- xiaoying-q4-short-video-script-agent/short_video_script_agent xiaoying-q4-short-video-script-agent/tests/test_models.py
git commit -m "feat: add q4 script contracts"
```

### Task 3: 实现素材、规则和时长业务工具

**Files:**
- Create: `short_video_script_agent/tools/__init__.py`
- Create: `short_video_script_agent/tools/materials.py`
- Create: `short_video_script_agent/tools/rules.py`
- Create: `short_video_script_agent/tools/duration.py`
- Create: `short_video_script_agent/tools/failure_injection.py`
- Create: `tests/test_tools.py`

- [ ] **Step 1: 为 P01 命中、无检索结果、品牌风险和 38 秒估算写失败测试。**

```python
def test_p01_search_returns_only_supported_material_ids():
    result = search_materials("支持字幕", material_id="P01")
    assert result.material_source_ids
    assert all(source.startswith("P01-") for source in result.material_source_ids)

def test_duration_estimation_reports_38_second_first_draft():
    assert estimate_duration(build_initial_draft(...)).estimated_seconds == 38
```

- [ ] **Step 2: 运行测试，确认它们因工具不存在失败。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_tools.py -v`  
Expected: FAIL，导入或函数缺失。

- [ ] **Step 3: 最小实现工具。**

`search_materials` 仅从夹具返回命中项和安全摘要。`check_factual_rules` 验证脚本声明全部由 P01 产品事实支持。`check_brand_rules` 检查禁用断言或素材品牌风险。`estimate_duration` 求和分镜秒数。`compress_draft` 只减小/合并镜头文本和秒数，不能新增素材来源或事实。`FailureInjector` 允许测试使指定工具抛出受控异常。

- [ ] **Step 4: 运行工具测试确认通过。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_tools.py -v`  
Expected: PASS。

- [ ] **Step 5: 提交业务工具。**

```powershell
git add -- xiaoying-q4-short-video-script-agent/short_video_script_agent/tools xiaoying-q4-short-video-script-agent/tests/test_tools.py
git commit -m "feat: add q4 material and rule tools"
```

### Task 4: 实现受限模型决策和 fallback

**Files:**
- Create: `short_video_script_agent/config.py`
- Create: `short_video_script_agent/llm/__init__.py`
- Create: `short_video_script_agent/llm/client.py`
- Create: `short_video_script_agent/llm/decision_tools.py`
- Create: `tests/test_llm_config.py`
- Create: `tests/test_llm_decision.py`
- Create: `tests/test_llm_fallback.py`

- [ ] **Step 1: 编写失败测试，固定合法动作边界。**

```python
def test_missing_llm_configuration_selects_explicit_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert Settings.from_environment().llm_configured is False

def test_invalid_model_action_is_rejected_in_favor_of_safe_legal_action():
    decision = validate_decision("invent_source", ["build_draft", "request_more_info"])
    assert decision.action == "request_more_info"
    assert decision.source == "fallback"
```

- [ ] **Step 2: 运行 LLM 测试确认它们失败。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_llm_config.py tests/test_llm_decision.py tests/test_llm_fallback.py -v`  
Expected: FAIL，模块或选择逻辑不存在。

- [ ] **Step 3: 实现最小安全决策层。**

`Settings.from_environment()` 调用 `load_dotenv()`；若无完整配置，打印一行 stderr 提示并选择 fallback。在线调用只请求动作 JSON（`action`、`reason`），只传递安全状态摘要；异常时 stderr 只打印异常类型并 fallback。fallback 规则必须实现：有素材则建稿；超长则压缩；无结果则先改写一次检索再 `request_more_info`；规则失败则 `finish_blocked`。所有选择经过合法动作检查。

- [ ] **Step 4: 运行 LLM 测试确认通过。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_llm_config.py tests/test_llm_decision.py tests/test_llm_fallback.py -v`  
Expected: PASS。

- [ ] **Step 5: 提交决策边界。**

```powershell
git add -- xiaoying-q4-short-video-script-agent/short_video_script_agent/config.py xiaoying-q4-short-video-script-agent/short_video_script_agent/llm xiaoying-q4-short-video-script-agent/tests/test_llm_*.py
git commit -m "feat: add constrained script decisions"
```

### Task 5: 构建 LangGraph Agent 闭环与执行上限

**Files:**
- Create: `short_video_script_agent/graph/__init__.py`
- Create: `short_video_script_agent/graph/state.py`
- Create: `short_video_script_agent/graph/nodes.py`
- Create: `short_video_script_agent/graph/routing.py`
- Create: `short_video_script_agent/graph/workflow.py`
- Create: `tests/test_workflow.py`
- Create: `tests/test_trace.py`
- Create: `tests/test_execution_limit.py`
- Create: `tests/test_tool_failure.py`

- [ ] **Step 1: 用失败测试定义三个主要运行路径。**

```python
def test_p01_overlength_is_compressed_then_reestimated_to_target():
    result = workflow.invoke(p01_request(target_seconds=30))
    assert result["final_response"]["status"] == "completed"
    assert result["final_response"]["total_estimated_seconds"] <= 30
    assert [event["action"] for event in result["trace"]] == [
        "search_materials", "build_draft", "estimate_duration", "compress_draft", "estimate_duration", "finish"
    ]

def test_no_material_result_requests_more_information_without_sources():
    result = workflow.invoke(unmatched_request())
    assert result["final_response"]["status"] == "needs_info"
    assert result["final_response"]["material_source_ids"] == []
```

另加测试验证：规则阻断、工具错误返回 `failed`、`max_steps=1` 返回 `incomplete/EXECUTION_LIMIT_REACHED`；每条 Trace 事件包含节点、动作、参数、返回摘要、下一动作、理由且不含密钥。

- [ ] **Step 2: 运行图测试并确认失败。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_workflow.py tests/test_trace.py tests/test_execution_limit.py tests/test_tool_failure.py -v`  
Expected: FAIL，无法导入图工作流。

- [ ] **Step 3: 实现最小 LangGraph 工作流。**

节点固定为 `validate_input`、`search_materials`、`check_rules`、`derive_legal_actions`、`decide_next_action`、`build_draft`、`estimate_duration`、`compress_draft`、`finalize`。每次可执行节点包装在 `_with_execution_limit()` 中。`decide_next_action` 写入 `decision_source`；动作执行后的节点将工具参数摘要和结果摘要追加至 Trace，再回到决策节点或 `finalize`。执行上限只返回未完成状态，绝不伪造完成。

- [ ] **Step 4: 运行图测试确认通过。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_workflow.py tests/test_trace.py tests/test_execution_limit.py tests/test_tool_failure.py -v`  
Expected: PASS。

- [ ] **Step 5: 提交 Agent 闭环。**

```powershell
git add -- xiaoying-q4-short-video-script-agent/short_video_script_agent/graph xiaoying-q4-short-video-script-agent/tests/test_workflow.py xiaoying-q4-short-video-script-agent/tests/test_trace.py xiaoying-q4-short-video-script-agent/tests/test_execution_limit.py xiaoying-q4-short-video-script-agent/tests/test_tool_failure.py
git commit -m "feat: add q4 dynamic script workflow"
```

### Task 6: 添加 SQLite 运行存储、JSON 表示层和 CLI

**Files:**
- Create: `short_video_script_agent/storage/__init__.py`
- Create: `short_video_script_agent/storage/database.py`
- Create: `short_video_script_agent/storage/repositories.py`
- Create: `short_video_script_agent/presentation.py`
- Create: `short_video_script_agent/cli.py`
- Create: `tests/conftest.py`
- Create: `tests/test_cli.py`
- Create: `tests/test_persistence.py`
- Create: `tests/test_cli_smoke.py`

- [ ] **Step 1: 写失败测试，验证 CLI 的 stdout/stderr 分离和运行恢复。**

```python
def test_run_command_prints_single_machine_readable_json_to_stdout(tmp_path):
    result = runner.invoke(app, ["run", "--topic", "字幕功能", ...])
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert "LLM configuration" in result.stderr

def test_show_command_reads_persisted_result(tmp_path):
    run_id = run_via_cli(...)
    assert json.loads(show_via_cli(run_id))["run_id"] == run_id
```

- [ ] **Step 2: 运行测试并确认失败。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_cli.py tests/test_persistence.py tests/test_cli_smoke.py -v`  
Expected: FAIL，CLI/存储不存在。

- [ ] **Step 3: 实现最小 CLI 和存储。**

`run` 接收 `--topic`、`--audience`、`--target-seconds`、`--style`、可选 `--material-id`、`--max-steps`、`--database`。`demo` 运行固定场景（`p01-overlength`、`no-material`、`rule-risk`、`tool-failure`、`execution-limit`）。`show` 读取已存结果。stdout 仅使用 `json.dumps(..., ensure_ascii=False)` 输出一份结果；stderr 仅含安全提醒。数据库只保留请求和最终 JSON，不保存秘密或 LLM 请求体。

- [ ] **Step 4: 运行 CLI/存储测试确认通过。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_cli.py tests/test_persistence.py tests/test_cli_smoke.py -v`  
Expected: PASS。

- [ ] **Step 5: 执行代表性命令。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python main.py demo p01-overlength --database data/final-verification/q4.db`  
Expected: stdout 为有效 JSON，显示压缩后的完成脚本和 Trace；stderr 为 fallback 提示（若未配置 LLM）。

- [ ] **Step 6: 提交运行入口。**

```powershell
git add -- xiaoying-q4-short-video-script-agent/short_video_script_agent/storage xiaoying-q4-short-video-script-agent/short_video_script_agent/presentation.py xiaoying-q4-short-video-script-agent/short_video_script_agent/cli.py xiaoying-q4-short-video-script-agent/main.py xiaoying-q4-short-video-script-agent/tests
git commit -m "feat: add q4 cli and persistence"
```

### Task 7: 生成真实证据并编写交付文档

**Files:**
- Create: `scripts/generate_examples.py`
- Create: `examples/README.md`
- Create: `examples/01-p01-overlength.md`
- Create: `examples/02-no-material.md`
- Create: `examples/03-tool-failure.md`
- Create: `examples/04-execution-limit.md`
- Create: `README.md`
- Create: `docs/01-requirements.md`
- Create: `docs/02-solution.md`
- Create: `docs/03-evaluation.md`
- Create: `docs/04-ai-usage.md`
- Create: `docs/05-retrospective.md`
- Create: `tests/test_required_materials.py`
- Create: `tests/test_examples.py`

- [ ] **Step 1: 写失败测试，验证 required docs 和实际证据结构。**

```python
def test_required_assessment_documents_and_evidence_are_present(project_root):
    for path in REQUIRED_PATHS:
        assert (project_root / path).is_file()

def test_example_records_include_input_output_and_trace():
    text = (examples / "01-p01-overlength.md").read_text(encoding="utf-8")
    assert "## Input" in text and "## Actual Output" in text and "## Actual Trace" in text
```

- [ ] **Step 2: 运行测试并确认失败。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest tests/test_required_materials.py tests/test_examples.py -v`  
Expected: FAIL，交付材料未创建。

- [ ] **Step 3: 添加脚本和文档。**

`generate_examples.py` 必须调用真实 CLI/工作流并将实际 JSON 中的输入、输出与 Trace 写入证据，不能手写预期输出。四个证据最少覆盖：P01 38 秒压缩至合规、无素材后改写/补充信息、注入工具失败、执行上限。

README 给出安装、运行、测试、审阅入口、fallback 和无秘密策略。五份 docs 分别满足项目规则；`docs/03-evaluation.md` 逐条链接到证据和测试。`docs/05-retrospective.md` 仅记录实际耗时、已完成范围、限制和下一步，不虚构 live LLM 调用。

- [ ] **Step 4: 运行生成器和材料测试。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python scripts/generate_examples.py; python -m pytest tests/test_required_materials.py tests/test_examples.py -v`  
Expected: evidence 文件更新，测试 PASS。

- [ ] **Step 5: 提交证据与文档。**

```powershell
git add -- xiaoying-q4-short-video-script-agent/README.md xiaoying-q4-short-video-script-agent/docs xiaoying-q4-short-video-script-agent/examples xiaoying-q4-short-video-script-agent/scripts xiaoying-q4-short-video-script-agent/tests/test_required_materials.py xiaoying-q4-short-video-script-agent/tests/test_examples.py
git commit -m "docs: add q4 evidence and assessment materials"
```

### Task 8: 完整验证、Git 审计和最终交付提交

**Files:**
- Modify only if verification reveals a fault: files implicated by failing tests.

- [ ] **Step 1: 从 Q4 根目录运行完整测试。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python -m pytest -v`  
Expected: 全部 PASS。

- [ ] **Step 2: 重启执行上下文后运行代表性 CLI 命令。**

Run: `Set-Location xiaoying-q4-short-video-script-agent; python main.py run --topic "P01 字幕功能" --audience "短视频创作者" --target-seconds 30 --style "轻快" --material-id P01 --database data/final-verification/q4-smoke.db`  
Expected: 单一 JSON stdout；含 `completed`、有效素材 ID、`fallback` 或 `live_llm`、完整 Trace；若无配置则 stderr 只出现简短 fallback notice。

- [ ] **Step 3: 审计 Git 忽略和工作区。**

Run: `git status --short; git check-ignore -v xiaoying-q4-short-video-script-agent/.env xiaoying-q4-short-video-script-agent/data/final-verification/q4-smoke.db`  
Expected: 仅 Q4 源码、docs、tests、examples 为可提交文件；`.env` 与数据库被忽略；不触碰 Q1/Q2。

- [ ] **Step 4: 提交最终验证后的状态。**

```powershell
git add -- xiaoying-q4-short-video-script-agent
git commit -m "feat: complete q4 short video script agent"
git rev-parse HEAD
```

- [ ] **Step 5: 如存在远程仓库，推送已验证的准确提交。**

Run: `git remote -v; git push <remote> master`  
Expected: 只有用户配置且有推送权限时才执行；记录仓库 URL 和最终 SHA，若无远程则明确说明未能提供 GitHub URL。
