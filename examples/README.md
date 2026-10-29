# Examples

所有证据由 `python scripts/generate_examples.py` 使用实际工作流生成。每个文件同时保存输入、最终输出和实际 Trace；它们不含 API Key、私有 URL 或数据库文件。

若本地设置了 `LLM_*` 配置，可运行 `python scripts/record_live_llm_evidence.py` 生成 `05-live-llm-decision.json`。该脚本只保存业务输入、输出和安全 Trace，不保存模型密钥、网关地址或提示词。
