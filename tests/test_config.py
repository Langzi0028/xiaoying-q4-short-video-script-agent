from short_video_script_agent.config import Settings


def test_environment_requires_llm_key_base_url_model_and_supported_mode(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_API_MODE", raising=False)

    assert Settings.from_environment(dotenv_path=tmp_path / "missing.env").llm_configured is False

    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_MODE", "chat_completions")
    settings = Settings.from_environment(dotenv_path=tmp_path / "missing.env")

    assert settings.llm_configured is True
    assert settings.api_mode == "chat_completions"


def test_environment_rejects_unsupported_llm_api_mode(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_MODE", "unsupported")

    assert Settings.from_environment(dotenv_path=tmp_path / "missing.env").llm_configured is False
