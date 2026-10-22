"""Tests only the OpenAI API adapter; does not call the network."""
import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import patch


def _load_adapter():
    fake_openai = types.ModuleType("openai")

    class FakeSDK:
        def __init__(self, **kwargs):
            self.options = kwargs
            self.received = None
            self.responses = types.SimpleNamespace(create=self.create)

        def create(self, **kwargs):
            self.received = kwargs
            return types.SimpleNamespace(output_text="  Vysvetlenie k pasáži.  ")

    fake_openai.OpenAI = FakeSDK
    spec = importlib.util.spec_from_file_location(
        "project_openai_backend", Path(__file__).resolve().parents[1] / "openai_backend.py"
    )
    with patch.dict(sys.modules, {"openai": fake_openai}):
        module = importlib.util.module_from_spec(spec)
        # dataclass checks the module namespace while importing.
        with patch.dict(sys.modules, {"project_openai_backend": module}):
            spec.loader.exec_module(module)
    return module


def test_openai_responses_api_is_called_with_corpus_only():
    module = _load_adapter()
    client = module.make_client("fake-secret", 120000)
    assert client.options["timeout"] == 120
    result = module.generate_content(
        client, model="gpt-6.1-sol", contents="Zdroje: [odsek 1]",
        system="Použi len odsek a vlastnú argumentáciu označ.",
        max_output_tokens=2800, reasoning_effort="low",
    )
    assert result.text == "Vysvetlenie k pasáži."
    request = client.received
    assert request["model"] == "gpt-6.1-sol"
    assert request["input"] == "Zdroje: [odsek 1]"
    assert request["instructions"].startswith("Použi len odsek")
    assert request["store"] is False
    assert request["reasoning"] == {"effort": "low"}
    assert "tools" not in request


def test_low_effort_fallback_for_unavailable_none():
    module = _load_adapter()
    client = module.make_client("fake-secret")
    module.generate_content(client, model="gpt-6.1-sol", contents="X", system="Y", reasoning_effort="none")
    assert client.received["reasoning"]["effort"] == "low"
