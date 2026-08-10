# test_s18_adapters.py — S18 Q31/Q76 named-agent conformance fixture; depends on adapters/, errors.py.
"""Drive independent wire goldens, lossless provider fields, and hostile capability claims."""

import ast
from copy import deepcopy
from pathlib import Path

import pytest

import adapters
from adapters import NamedAdapter
from errors import CassetteError

MODEL_REF = "revision:model-a"
AGENT_REF = "openclaw/main"
ERROR = {
    "code": "CAPABILITY_MISMATCH",
    "object_id": "run-1",
    "failed_invariant": "Q31/Q76 exact semantics",
    "retryability": "terminal",
    "detail": "provider refused the exact request",
}


def _adapter(name: str) -> NamedAdapter:
    return NamedAdapter(
        name,
        model_aliases={MODEL_REF: AGENT_REF},
        server_contract=name == "hermes",
    )


def _profile(namespace: str) -> dict:
    return {
        "protocol_version": "1",
        "model_refs": [MODEL_REF],
        "modalities": ["text"],
        "context": {"maximum_tokens": 8192},
        "reasoning": {"supported": True},
        "tools": {"supported": True},
        "structured_output": {"supported": True},
        "streaming": True,
        "cancellation": True,
        "training": {"tiers": ["adapter"]},
        "source": {"kinds": ["huggingface"]},
        "performance_tiers": [{"id": "frontier-class"}],
        "extensions": {
            namespace: {"models": {MODEL_REF: {"provider_tag": "local-cartridge"}}}
        },
    }


def _request(name: str) -> dict:
    namespace = _adapter(name).definition["namespace"]
    common = {
        "idempotency_key": f"{name}-request-1",
        "model_ref": MODEL_REF,
        "input": [{"role": "user", "content": "Return one object."}],
        "context_ref": "conversation-1",
        "extensions": {
            namespace: {
                "body": {"provider_note": {"trace": name}},
                "headers": {"X-Provider-Trace": f"trace-{name}"},
            }
        },
    }
    if name == "ollama":
        del common["context_ref"]
        return {
            **common,
            "generation": {"options": {"temperature": 0.25}, "stream": True},
            "reasoning": True,
            "output_schema": {"type": "object", "properties": {"answer": {"type": "string"}}},
            "tools": [{"type": "function", "function": {"name": "lookup"}}],
        }
    if name in {"openclaw", "hermes"}:
        return {
            **common,
            "generation": {"max_output_tokens": 32, "stream": True},
            "tools": [{"type": "function", "name": "lookup"}],
        }
    if name == "custom":
        return {
            **common,
            "generation": {"seed": 17},
            "reasoning": {"effort": "high"},
            "output_schema": {"type": "object"},
            "tools": [{"name": "lookup"}],
        }
    return {
        **common,
        "generation": {"max_output_tokens": 32, "temperature": 0.25, "stream": True},
        "reasoning": {"effort": "high"},
        "output_schema": {
            "type": "json_schema",
            "name": "answer",
            "schema": {"type": "object", "properties": {"answer": {"type": "string"}}},
        },
        "tools": [{"type": "function", "name": "lookup"}],
    }


def _trace(namespace: str, *, reasoning: bool = True) -> list[dict]:
    events = [
        {"run_id": "run-1", "sequence": 0, "type": "started", "payload": {"model_ref": MODEL_REF}},
        {"run_id": "run-1", "sequence": 1, "type": "reasoning_delta", "payload": {"text": "check"}},
        {
            "run_id": "run-1",
            "sequence": 2,
            "type": "output_delta",
            "payload": {"text": "answer"},
            "extensions": {namespace: {"frame": {"provider_marker": "kept"}}},
        },
        {
            "run_id": "run-1", "sequence": 3, "type": "tool_call",
            "payload": {"id": "call-1", "name": "lookup", "arguments": {"query": "cassette"}},
        },
        {
            "run_id": "run-1", "sequence": 4, "type": "tool_result",
            "payload": {"id": "call-1", "output": {"found": True}},
        },
        {
            "run_id": "run-1", "sequence": 5, "type": "usage",
            "payload": {"input_tokens": 11, "output_tokens": 7},
        },
        {
            "run_id": "run-1", "sequence": 6, "type": "completed",
            "payload": {"finish_reason": "stop"},
        },
    ]
    if reasoning:
        return events
    del events[1]
    for sequence, event in enumerate(events):
        event["sequence"] = sequence
    return events


def _rejected(code: str, call) -> CassetteError:
    with pytest.raises(CassetteError) as caught:
        call()
    assert caught.value.code == code
    return caught.value


def test_q31_q76_named_adapters_round_trip_exact_traces_and_reject_fabrication():
    """Q31/Q76 acceptance: every named wire is lossless where exact and refuses every false claim."""

    expected = {
        "codex": {
            "version": "openai-responses@9c8e1216bdaee0b020d1253ab7cc03a32eb36efe",
            "commit": "9c8e1216bdaee0b020d1253ab7cc03a32eb36efe",
            "authority": "https://github.com/openai/openai-openapi",
            "discovery": ("GET", "/v1/models"),
            "surfaces": {"responses": ("POST", "/v1/responses", "sse")},
        },
        "ollama": {
            "version": "ollama-api@a836eb8c3cc21a30020aadc70a1cc06012a4ef01",
            "commit": "a836eb8c3cc21a30020aadc70a1cc06012a4ef01",
            "authority": "https://github.com/ollama/ollama",
            "discovery": ("GET", "/api/tags"),
            "surfaces": {
                "chat": ("POST", "/api/chat", "ndjson"),
                "generate": ("POST", "/api/generate", "ndjson"),
            },
        },
        "openclaw": {
            "version": "openclaw-gateway-v4@810c3510ee6102e7a263553f871a11233708e275",
            "commit": "810c3510ee6102e7a263553f871a11233708e275",
            "authority": "https://github.com/openclaw/openclaw",
            "discovery": ("GET", "/v1/models"),
            "surfaces": {
                "responses": ("POST", "/v1/responses", "sse"),
                "chat": ("POST", "/v1/chat/completions", "sse"),
                "gateway": ("WS", "gateway:v4", "json"),
            },
        },
        "hermes": {
            "version": "hermes-agent-api@a98aee47cecddab9ab9f58fc3a3b94b25f78d394",
            "commit": "a98aee47cecddab9ab9f58fc3a3b94b25f78d394",
            "authority": "https://github.com/NousResearch/hermes-agent",
            "discovery": ("GET", "/v1/models"),
            "surfaces": {
                "responses": ("POST", "/v1/responses", "sse"),
                "chat": ("POST", "/v1/chat/completions", "sse"),
                "agent": ("POST", "/v1/runs", "sse"),
            },
        },
        "custom": {
            "version": "cassette-q31-v1",
            "commit": None,
            "authority": "https://recluse.studio/cassette/schema/v1",
            "discovery": ("JSONL", "capabilities"),
            "surfaces": {"canonical": ("JSONL", "run", "jsonl")},
        },
    }
    assert set(expected) == {"codex", "ollama", "openclaw", "hermes", "custom"}
    for name, literal in expected.items():
        definition = _adapter(name).definition
        assert definition["adapter_version"] == literal["version"]
        assert definition["commit"] == literal["commit"]
        assert definition["authority"] == literal["authority"]
        assert (definition["discovery"]["method"], definition["discovery"]["path"]) == literal["discovery"]
        assert {
            surface: (record["method"], record["path"], record["stream"])
            for surface, record in definition["surfaces"].items()
        } == literal["surfaces"]
        assert all(
            status in {"EXACT", "BEST_EFFORT", "PROVIDER_MANAGED", "UNSUPPORTED"}
            for status in definition["field_status"].values()
        )
        assert all(
            status in {"EXACT", "BEST_EFFORT", "PROVIDER_MANAGED", "UNSUPPORTED"}
            for surface in definition["surfaces"].values()
            for status in (*surface["features"].values(), *surface["event_features"].values())
        )

    # Discovery is exact only with the Cassette capability sidecar. Native names alone prove none.
    for name in expected:
        adapter = _adapter(name)
        profile = _profile(adapter.definition["namespace"])
        wire = adapter.to_wire_capabilities([profile])
        assert adapter.from_wire_capabilities(wire) == [profile]
        if name == "custom":
            assert wire == {"encoding": "jsonl", "record": {"capabilities": [profile]}}
            continue
        assert wire["method"] == expected[name]["discovery"][0]
        assert wire["path"] == expected[name]["discovery"][1]
        assert wire["body"]["x_cassette"]["field_status"] == adapter.definition["field_status"]
        assert set(wire["body"]["x_cassette"]["surface_status"]) == set(
            adapter.definition["surfaces"]
        )
        if name == "ollama":
            assert wire["body"]["models"][0]["name"] == MODEL_REF
            assert wire["detail_requests"] == [
                {"method": "POST", "path": "/api/show", "body": {"model": MODEL_REF}}
            ]
            native_rows = wire["body"]["models"]
            id_field = "model"
        else:
            expected_id = AGENT_REF if name == "openclaw" else MODEL_REF
            assert wire["body"]["data"][0]["id"] == expected_id
            native_rows = wire["body"]["data"]
            id_field = "id"
        no_sidecar = deepcopy(wire)
        del no_sidecar["body"]["x_cassette"]
        _rejected("CAPABILITY_MISMATCH", lambda: adapter.from_wire_capabilities(no_sidecar))
        changed_model = deepcopy(wire)
        rows = changed_model["body"]["models"] if name == "ollama" else changed_model["body"]["data"]
        rows[0][id_field] = "foreign-model"
        if name == "ollama":
            rows[0]["name"] = "foreign-model"
        _rejected("CAPABILITY_MISMATCH", lambda: adapter.from_wire_capabilities(changed_model))
        assert native_rows[0]["provider_tag"] == "local-cartridge"
        if name == "ollama":
            bad_show = deepcopy(wire)
            bad_show["detail_requests"][0]["path"] = "/api/not-show"
            _rejected("CAPABILITY_MISMATCH", lambda: adapter.from_wire_capabilities(bad_show))
        stale_version = deepcopy(wire)
        stale_version["body"]["x_cassette"]["adapter_version"] = "stale"
        _rejected("CAPABILITY_MISMATCH", lambda: adapter.from_wire_capabilities(stale_version))
        stale_status = deepcopy(wire)
        stale_status["body"]["x_cassette"]["field_status"]["cancellation"] = "UNSUPPORTED"
        _rejected("CAPABILITY_MISMATCH", lambda: adapter.from_wire_capabilities(stale_status))
        stale_surface = deepcopy(wire)
        first_surface = next(iter(stale_surface["body"]["x_cassette"]["surface_status"]))
        stale_surface["body"]["x_cassette"]["surface_status"][first_surface]["request"][
            "text"
        ] = "UNSUPPORTED"
        _rejected("CAPABILITY_MISMATCH", lambda: adapter.from_wire_capabilities(stale_surface))

    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: NamedAdapter("openclaw").to_wire_capabilities([
            _profile("openclaw.gateway.v4")
        ]),
    )
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: NamedAdapter("hermes").to_wire_capabilities([_profile("hermes.agent.api")]),
    )
    codex_profile = _profile("openai.responses")
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("codex").to_wire_capabilities([codex_profile, codex_profile]),
    )
    codex_wire = _adapter("codex").to_wire_capabilities([codex_profile])
    duplicate_sidecar = deepcopy(codex_wire)
    duplicate_sidecar["body"]["x_cassette"]["capabilities"].append(
        deepcopy(duplicate_sidecar["body"]["x_cassette"]["capabilities"][0])
    )
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("codex").from_wire_capabilities(duplicate_sidecar),
    )
    forged_sidecar_extension = deepcopy(codex_wire)
    forged_sidecar_extension["body"]["x_cassette"]["capabilities"][0]["extensions"] = {
        "openai.responses": {"models": {MODEL_REF: {"forged": True}}}
    }
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("codex").from_wire_capabilities(forged_sidecar_extension),
    )
    custom_profile = _profile("cassette.q31")
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("custom").to_wire_capabilities([custom_profile, custom_profile]),
    )
    _rejected(
        "INVALID_REQUEST",
        lambda: _adapter("custom").from_wire_capabilities(
            {"encoding": "jsonl", "record": {"capabilities": []}}
        ),
    )
    absent_model_extension = _profile("openai.responses")
    absent_model_extension["extensions"]["openai.responses"]["models"]["absent"] = {"x": 1}
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("codex").to_wire_capabilities([absent_model_extension]),
    )

    # Default request surfaces carry each exact native field and preserve provider-only material.
    wires = {}
    for name in expected:
        adapter = _adapter(name)
        request = _request(name)
        wire = adapter.to_wire_request(request)
        wires[name] = wire
        assert adapter.from_wire_request(wire) == request
    assert wires["codex"]["body"] == {
        "provider_note": {"trace": "codex"},
        "model": MODEL_REF,
        "input": [{"role": "user", "content": "Return one object."}],
        "previous_response_id": "conversation-1",
        "max_output_tokens": 32,
        "temperature": 0.25,
        "stream": True,
        "reasoning": {"effort": "high"},
        "text": {"format": {
            "type": "json_schema", "name": "answer",
            "schema": {"type": "object", "properties": {"answer": {"type": "string"}}},
        }},
        "tools": [{"type": "function", "name": "lookup"}],
    }
    assert wires["ollama"]["body"]["messages"] == _request("ollama")["input"]
    assert wires["ollama"]["body"]["think"] is True
    assert wires["ollama"]["body"]["format"] == _request("ollama")["output_schema"]
    assert wires["openclaw"]["body"]["model"] == AGENT_REF
    assert wires["openclaw"]["headers"]["X-OpenClaw-Session-Key"] == "conversation-1"
    assert wires["hermes"]["body"]["model"] == MODEL_REF
    assert wires["custom"] == {"encoding": "jsonl", "record": _request("custom")}

    # Every additional route named by Q76 is executable, not decorative map data.
    ollama_generate = {
        "idempotency_key": "ollama-generate", "model_ref": MODEL_REF, "input": "hello",
        "generation": {"options": {"temperature": 0.0}, "stream": True},
        "reasoning": True, "output_schema": {"type": "object"},
    }
    ollama_generate_wire = _adapter("ollama").to_wire_request(ollama_generate, surface="generate")
    assert ollama_generate_wire["path"] == "/api/generate"
    assert ollama_generate_wire["body"]["prompt"] == "hello"
    assert _adapter("ollama").from_wire_request(
        ollama_generate_wire, surface="generate"
    ) == ollama_generate

    openclaw_chat = {
        "idempotency_key": "openclaw-chat", "model_ref": MODEL_REF,
        "input": [{"role": "user", "content": "hello"}], "context_ref": "session-2",
        "generation": {"max_output_tokens": 12, "temperature": 0.2, "stream": True},
        "tools": [{"type": "function", "function": {"name": "lookup"}}],
    }
    openclaw_chat_wire = _adapter("openclaw").to_wire_request(openclaw_chat, surface="chat")
    assert openclaw_chat_wire["path"] == "/v1/chat/completions"
    assert openclaw_chat_wire["body"]["max_completion_tokens"] == 12
    assert _adapter("openclaw").from_wire_request(
        openclaw_chat_wire, surface="chat"
    ) == openclaw_chat

    openclaw_gateway = {
        "idempotency_key": "openclaw-gateway", "model_ref": MODEL_REF, "input": "hello",
        "context_ref": "session-3", "generation": {},
    }
    openclaw_gateway_wire = _adapter("openclaw").to_wire_request(
        openclaw_gateway, surface="gateway"
    )
    assert openclaw_gateway_wire == {
        "method": "WS", "path": "gateway:v4", "headers": {},
        "body": {
            "type": "req", "method": "chat.send", "id": "openclaw-gateway",
            "params": {"agentId": AGENT_REF, "message": "hello", "sessionKey": "session-3"},
        },
    }
    assert _adapter("openclaw").from_wire_request(
        openclaw_gateway_wire, surface="gateway"
    ) == openclaw_gateway

    hermes_chat = {
        "idempotency_key": "hermes-chat", "model_ref": MODEL_REF,
        "input": [{"role": "user", "content": "hello"}], "generation": {"stream": True},
        "tools": [{"type": "function", "function": {"name": "lookup"}}],
    }
    hermes_chat_wire = _adapter("hermes").to_wire_request(hermes_chat, surface="chat")
    assert hermes_chat_wire["path"] == "/v1/chat/completions"
    assert _adapter("hermes").from_wire_request(hermes_chat_wire, surface="chat") == hermes_chat
    hermes_agent = {
        "idempotency_key": "hermes-run", "model_ref": MODEL_REF, "input": "hello",
        "context_ref": "hermes-session", "generation": {},
    }
    hermes_agent_wire = _adapter("hermes").to_wire_request(hermes_agent, surface="agent")
    assert hermes_agent_wire["path"] == "/v1/runs"
    assert hermes_agent_wire["body"] == {
        "model": MODEL_REF, "input": "hello", "session_id": "hermes-session",
    }
    assert _adapter("hermes").from_wire_request(hermes_agent_wire, surface="agent") == hermes_agent

    # Provider additions survive; credentials do not enter canonical logs or an outbound extension.
    incoming = deepcopy(wires["codex"])
    incoming["body"]["future_provider_field"] = {"value": 7}
    incoming["body"]["future_empty_field"] = {}
    incoming["headers"]["X-Future-Field"] = "kept"
    incoming["headers"]["Authorization"] = "Bearer never-canonical"
    decoded = _adapter("codex").from_wire_request(incoming)
    assert decoded["extensions"]["openai.responses"] == {
        "body": {
            "provider_note": {"trace": "codex"},
            "future_provider_field": {"value": 7},
            "future_empty_field": {},
        },
        "headers": {"X-Provider-Trace": "trace-codex", "X-Future-Field": "kept"},
    }
    assert "never-canonical" not in repr(decoded)
    assert _adapter("codex").from_wire_request(
        _adapter("codex").to_wire_request(decoded)
    ) == decoded
    duplicate_header = _request("codex")
    duplicate_header["extensions"]["openai.responses"]["headers"][
        "x-provider-trace"
    ] = "second"
    _rejected("INVALID_REQUEST", lambda: _adapter("codex").to_wire_request(duplicate_header))
    control_header = _request("codex")
    control_header["extensions"]["openai.responses"]["headers"]["X-Control"] = "one\0two"
    _rejected("INVALID_REQUEST", lambda: _adapter("codex").to_wire_request(control_header))

    # Complete event traces retain IDs, order, exact payloads, terminal states, and provider fields.
    full_traces = {}
    event_surfaces = {"codex": None, "ollama": None, "hermes": "agent", "custom": None}
    for name, surface in event_surfaces.items():
        adapter = _adapter(name)
        trace = _trace(adapter.definition["namespace"])
        wire = adapter.to_wire_events(trace, surface=surface)
        full_traces[name] = wire
        assert adapter.from_wire_events(wire, surface=surface) == trace
    assert [frame["type"] for frame in full_traces["codex"]["frames"]] == [
        "response.created", "response.reasoning_summary_text.delta",
        "response.output_text.delta", "response.output_item.done", "cassette.tool_result",
        "cassette.usage", "response.completed",
    ]
    assert [frame["x_cassette"]["type"] for frame in full_traces["ollama"]["frames"]] == [
        "started", "reasoning_delta", "output_delta", "tool_call", "tool_result", "usage",
        "completed",
    ]
    assert [frame["event"] for frame in full_traces["hermes"]["frames"]] == [
        "cassette.started", "reasoning.available", "message.delta", "tool.started",
        "tool.completed", "cassette.usage", "run.completed",
    ]
    assert full_traces["custom"] == {
        "encoding": "jsonl", "records": _trace("cassette.q31")
    }

    openclaw_trace = _trace("openclaw.gateway.v4", reasoning=False)
    for surface in ("responses", "chat", "gateway"):
        wire = _adapter("openclaw").to_wire_events(openclaw_trace, surface=surface)
        assert _adapter("openclaw").from_wire_events(wire, surface=surface) == openclaw_trace
        assert (
            wire["frames"][0].get("response", {}).get("model")
            or wire["frames"][0].get("model")
            or wire["frames"][0].get("payload", {}).get("agentId")
        ) == AGENT_REF
    gateway_wire = _adapter("openclaw").to_wire_events(openclaw_trace, surface="gateway")
    assert [frame["event"] for frame in gateway_wire["frames"]] == [
        "session.operation", "session.message", "session.tool", "session.tool",
        "cassette.usage", "session.operation",
    ]

    for name, surface in {
        "codex": None, "ollama": None, "openclaw": "gateway", "hermes": "agent",
        "custom": None,
    }.items():
        adapter = _adapter(name)
        namespace = adapter.definition["namespace"]
        cancelled = [
            {"run_id": "run-1", "sequence": 0, "type": "started", "payload": {"model_ref": MODEL_REF}},
            {"run_id": "run-1", "sequence": 1, "type": "cancelled", "payload": {"reason": "client"}},
        ]
        failed = [
            {"run_id": "run-1", "sequence": 0, "type": "started", "payload": {"model_ref": MODEL_REF}},
            {
                "run_id": "run-1", "sequence": 1, "type": "failed", "payload": {"error": ERROR},
                "extensions": {namespace: {"frame": {"provider_failure_id": "failure-1"}}},
            },
        ]
        for terminal_trace in (cancelled, failed):
            wire = adapter.to_wire_events(terminal_trace, surface=surface)
            assert adapter.from_wire_events(wire, surface=surface) == terminal_trace

    # Q6 status/training stay canonical extensions unless the pinned wire has an exact native cancel.
    cancel = {
        "protocol_version": "1", "operation": "cancel", "idempotency_key": "cancel-1",
        "target": "run-1", "arguments": {},
    }
    training = {
        "protocol_version": "1", "operation": "train", "idempotency_key": "train-1",
        "target": MODEL_REF, "arguments": {"tier": "adapter"},
    }
    status = {
        "operation_id": "run-1", "kind": "run", "state": "FAILED", "progress": 1.0,
        "error": ERROR,
    }
    cancel_paths = {
        "codex": "/v1/responses/run-1/cancel",
        "ollama": "/cassette/v1/operations/run-1/cancel",
        "openclaw": "/cassette/v1/operations/run-1/cancel",
        "hermes": "/v1/runs/run-1/stop",
    }
    for name in expected:
        adapter = _adapter(name)
        for action, record in (("cancel", cancel), ("training", training), ("status", status)):
            wire = adapter.to_wire_operation(action, record)
            assert adapter.from_wire_operation(action, wire) == record
        if name != "custom":
            cancel_wire = adapter.to_wire_operation("cancel", cancel)
            status_wire = adapter.to_wire_operation("status", status)
            training_wire = adapter.to_wire_operation("training", training)
            assert cancel_wire["path"] == cancel_paths[name]
            assert status_wire["path"] == "/cassette/v1/operations/run-1"
            assert training_wire["path"] == "/cassette/v1/operations"
            assert status_wire["body"] == status
            assert training_wire["body"] == training
            if name in {"codex", "hermes"}:
                assert cancel_wire["body"] == {}
                assert cancel_wire["headers"] == {"Idempotency-Key": "cancel-1"}
                lowercase_header = deepcopy(cancel_wire)
                lowercase_header["headers"] = {"idempotency-key": "cancel-1"}
                assert adapter.from_wire_operation("cancel", lowercase_header) == cancel
            else:
                assert cancel_wire["body"] == cancel
    bad_status_route = _adapter("codex").to_wire_operation("status", status)
    bad_status_route["path"] = "/cassette/v1/operations/another-run"
    _rejected(
        "INVALID_REQUEST", lambda: _adapter("codex").from_wire_operation("status", bad_status_route)
    )
    for action, record in (("cancel", cancel), ("training", training)):
        missing_target = deepcopy(record)
        del missing_target["target"]
        _rejected(
            "INVALID_REQUEST",
            lambda action=action, record=missing_target: _adapter("ollama").to_wire_operation(
                action, record
            ),
        )
        _rejected(
            "INVALID_REQUEST",
            lambda action=action, record=missing_target: _adapter("custom").from_wire_operation(
                action, {"encoding": "jsonl", "action": action, "record": record}
            ),
        )
    wrong_custom_cancel = deepcopy(cancel)
    wrong_custom_cancel["operation"] = "train"
    _rejected(
        "INVALID_REQUEST",
        lambda: _adapter("custom").from_wire_operation(
            "cancel", {"encoding": "jsonl", "action": "cancel", "record": wrong_custom_cancel}
        ),
    )

    # Hostile semantics are rejected, never hidden in an extension or re-labelled as exact.
    openclaw = _adapter("openclaw")
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: openclaw.to_wire_request({**_request("openclaw"), "reasoning": {"effort": "high"}}),
    )
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: openclaw.to_wire_request({**_request("openclaw"), "output_schema": {"type": "object"}}),
    )
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: openclaw.to_wire_request({**_request("openclaw"), "output_schema": {}}),
    )
    blocked_openclaw = deepcopy(wires["openclaw"])
    blocked_openclaw["body"]["reasoning"] = {"effort": "high"}
    _rejected("CAPABILITY_MISMATCH", lambda: openclaw.from_wire_request(blocked_openclaw))
    extension_bypass = _request("openclaw")
    extension_bypass["extensions"]["openclaw.gateway.v4"]["body"]["reasoning"] = {
        "effort": "high"
    }
    _rejected("CAPABILITY_MISMATCH", lambda: openclaw.to_wire_request(extension_bypass))
    blocked_stop = deepcopy(openclaw_chat_wire)
    blocked_stop["body"]["stop"] = ["END"]
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: openclaw.from_wire_request(blocked_stop, surface="chat"),
    )
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("ollama").to_wire_request(
            {**ollama_generate, "tools": [{"name": "not-on-generate"}]}, surface="generate"
        ),
    )
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("ollama").to_wire_request({**_request("ollama"), "context_ref": "lost"}),
    )
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("hermes").to_wire_request(
            {**_request("hermes"), "reasoning": {"effort": "high"}}
        ),
    )
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("codex").to_wire_request({**_request("codex"), "generation": {"seed": 7}}),
    )
    colliding = _request("codex")
    colliding["extensions"]["openai.responses"]["body"]["model"] = "forged"
    _rejected("CAPABILITY_MISMATCH", lambda: _adapter("codex").to_wire_request(colliding))
    foreign_extension = _request("codex")
    foreign_extension["extensions"]["foreign.provider"] = {"body": {"x": 1}}
    _rejected("CAPABILITY_MISMATCH", lambda: _adapter("codex").to_wire_request(foreign_extension))
    credential_extension = _request("codex")
    credential_extension["extensions"]["openai.responses"]["headers"]["Authorization"] = "Bearer x"
    _rejected("CAPABILITY_MISMATCH", lambda: _adapter("codex").to_wire_request(credential_extension))
    split_header = _request("codex")
    split_header["extensions"]["openai.responses"]["headers"]["X-Trace"] = "one\r\ntwo"
    _rejected("INVALID_REQUEST", lambda: _adapter("codex").to_wire_request(split_header))
    non_json = _request("codex")
    non_json["input"] = b"not-json"
    _rejected("INVALID_REQUEST", lambda: _adapter("codex").to_wire_request(non_json))
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("openclaw").to_wire_events(
            _trace("openclaw.gateway.v4"), surface="responses"
        ),
    )

    bad_sequence = _trace("openai.responses")
    bad_sequence[2]["sequence"] = 1
    _rejected("INVALID_REQUEST", lambda: _adapter("codex").to_wire_events(bad_sequence))
    foreign_run = _trace("openai.responses")
    foreign_run[2]["run_id"] = "run-2"
    _rejected("INVALID_REQUEST", lambda: _adapter("codex").to_wire_events(foreign_run))
    after_terminal = _trace("openai.responses")
    after_terminal.append(
        {"run_id": "run-1", "sequence": 7, "type": "usage", "payload": {"output_tokens": 8}}
    )
    _rejected("INVALID_REQUEST", lambda: _adapter("codex").to_wire_events(after_terminal))
    reordered = deepcopy(full_traces["codex"])
    reordered["frames"][1], reordered["frames"][2] = reordered["frames"][2], reordered["frames"][1]
    _rejected("INVALID_REQUEST", lambda: _adapter("codex").from_wire_events(reordered))
    unknown_event = {"encoding": "sse", "frames": [{"type": "response.unknown"}]}
    _rejected("INVALID_REQUEST", lambda: _adapter("codex").from_wire_events(unknown_event))
    duplicate_tool_argument = deepcopy(full_traces["codex"])
    duplicate_tool_argument["frames"][3]["item"]["arguments"] = '{"query":"a","query":"b"}'
    _rejected(
        "INVALID_REQUEST", lambda: _adapter("codex").from_wire_events(duplicate_tool_argument)
    )
    _rejected(
        "INVALID_REQUEST",
        lambda: _adapter("codex").to_wire_operation("cancel", training),
    )
    _rejected(
        "CAPABILITY_MISMATCH",
        lambda: _adapter("codex").to_wire_operation(
            "cancel", {**cancel, "arguments": {"provider_option": True}}
        ),
    )
    without_target = dict(cancel)
    del without_target["target"]
    _rejected("INVALID_REQUEST", lambda: _adapter("codex").to_wire_operation("cancel", without_target))
    _rejected(
        "INVALID_REQUEST",
        lambda: _adapter("codex").to_wire_operation("cancel", {**cancel, "target": "../run-1"}),
    )

    # The handwritten shim contains no named-client control branch; names select generated data only.
    tree = ast.parse(Path(adapters.__file__).read_text(encoding="utf-8"))
    named_literals = set(expected)
    branch_literals = {
        comparator.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Compare)
        for comparator in node.comparators
        if isinstance(comparator, ast.Constant) and comparator.value in named_literals
    }
    assert branch_literals == set()
