import json
from unittest.mock import MagicMock, patch

import agents.analyzer as analyzer_mod
import agents.coder as coder_mod


def _fake_response(text: str):
    resp = MagicMock()
    resp.content = [MagicMock(text=text)]
    resp.usage = MagicMock(input_tokens=10, output_tokens=10)
    return resp


def test_analyze_incident_parses_the_models_json_response():
    fake_json = json.dumps(
        {
            "structural_change_summary": "flat list became payload.items",
            "field_mapping": [{"target_field": "external_id", "how_to_get_it": "item.id"}],
            "pagination_detected": False,
            "confidence": 0.95,
        }
    )
    with patch.object(analyzer_mod.client.messages, "create", return_value=_fake_response(fake_json)):
        result = analyzer_mod.analyze_incident({"a": 1}, "def extract(raw): pass", "KeyError")

    assert result["structural_change_summary"] == "flat list became payload.items"
    assert result["field_mapping"][0]["target_field"] == "external_id"


def test_analyze_incident_strips_markdown_fences_even_though_told_not_to_use_them():
    payload = {
        "structural_change_summary": "x",
        "field_mapping": [],
        "pagination_detected": False,
        "confidence": 1.0,
    }
    fenced = "```json\n" + json.dumps(payload) + "\n```"
    with patch.object(analyzer_mod.client.messages, "create", return_value=_fake_response(fenced)):
        result = analyzer_mod.analyze_incident({}, "", "")

    assert result["structural_change_summary"] == "x"


def test_untrusted_data_is_labeled_and_truncated_in_the_prompt():
    """Guards the prompt-injection defense at the prompt-construction
    level: the raw sample must be wrapped in <UNTRUSTED_DATA> tags and
    capped in length, regardless of what it contains."""
    captured = {}

    def fake_create(**kwargs):
        captured["messages"] = kwargs["messages"]
        return _fake_response(
            json.dumps(
                {
                    "structural_change_summary": "x",
                    "field_mapping": [],
                    "pagination_detected": False,
                    "confidence": 1.0,
                }
            )
        )

    huge_payload = {"name": "A" * 10000}
    with patch.object(analyzer_mod.client.messages, "create", side_effect=fake_create):
        analyzer_mod.analyze_incident(huge_payload, "", "")

    user_message = captured["messages"][0]["content"]
    assert "<UNTRUSTED_DATA>" in user_message
    assert "</UNTRUSTED_DATA>" in user_message
    # the raw sample is capped at 3000 chars before being embedded
    assert len(user_message) < 3500


def test_generate_extractor_code_strips_markdown_fences():
    fenced = "```python\ndef extract(raw):\n    return raw\n```"
    with patch.object(coder_mod.client.messages, "create", return_value=_fake_response(fenced)):
        code = coder_mod.generate_extractor_code([], "no change")

    assert code == "def extract(raw):\n    return raw"
    assert "```" not in code


def test_generate_extractor_code_includes_previous_attempt_feedback_when_given():
    captured = {}

    def fake_create(**kwargs):
        captured["user_message"] = kwargs["messages"][0]["content"]
        return _fake_response("def extract(raw):\n    return raw\n")

    with patch.object(coder_mod.client.messages, "create", side_effect=fake_create):
        coder_mod.generate_extractor_code(
            [], "no change", previous_attempt_feedback="last attempt: KeyError on 'items'"
        )

    assert "PREVIOUS_ATTEMPT_FEEDBACK" in captured["user_message"]
    assert "KeyError on 'items'" in captured["user_message"]
