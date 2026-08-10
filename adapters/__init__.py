# __init__.py — generated-map protocol translation for Q31/Q76 named agents; depends on errors.py, schema/.
"""Translate canonical Cassette records without owning model or operation lifecycle."""

from __future__ import annotations

from copy import deepcopy
import json

from errors import CassetteError
from schema.tables import ADAPTER_EVENT_FORMATS, ADAPTER_PROTOCOLS
from schema.validator import validate

_MISSING = object()
_TERMINAL_EVENTS = frozenset({"completed", "cancelled", "failed"})
_SENSITIVE_HEADERS = frozenset({
    "authorization", "cookie", "proxy-authorization", "x-api-key", "x-auth-token",
})
_HEADER_TOKEN = frozenset("!#$%&'*+-.^_`|~")


def _fail(code: str, object_id: str, detail: str) -> CassetteError:
    return CassetteError(code, object_id, "Q31/Q76 exact adapter semantics", "terminal", detail)


def _validated(kind: str, value: object) -> dict:
    if not isinstance(value, dict):
        raise _fail("INVALID_REQUEST", kind, "canonical record must be an object")
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        if json.loads(encoded) != value:
            raise TypeError("record changes under JSON serialization")
    except (TypeError, ValueError) as exc:
        raise _fail("INVALID_REQUEST", kind, f"record is not exact JSON: {exc}") from exc
    defects = validate(kind, value)
    if defects:
        raise _fail("INVALID_REQUEST", kind, "; ".join(defects[:4]))
    return deepcopy(value)


def _path_text(path: list[object]) -> str:
    return ".".join(str(part) for part in path)


def _get(value: object, path: list[object]) -> object:
    current = value
    for part in path:
        if isinstance(part, int):
            if not isinstance(current, list) or part >= len(current):
                return _MISSING
            current = current[part]
        else:
            if not isinstance(current, dict) or part not in current:
                return _MISSING
            current = current[part]
    return current


def _put(value: object, path: list[object], item: object) -> None:
    current = value
    for index, part in enumerate(path):
        final = index == len(path) - 1
        following = None if final else path[index + 1]
        if isinstance(part, int):
            if not isinstance(current, list):
                raise _fail("INVALID_REQUEST", _path_text(path), "wire map expected an array")
            while len(current) <= part:
                current.append(None)
            if final:
                if current[part] is not None:
                    raise _fail(
                        "CAPABILITY_MISMATCH", _path_text(path),
                        "provider extension collides with an exact mapped field",
                    )
                current[part] = deepcopy(item)
            else:
                if current[part] is None:
                    current[part] = [] if isinstance(following, int) else {}
                current = current[part]
            continue
        if not isinstance(current, dict):
            raise _fail("INVALID_REQUEST", _path_text(path), "wire map expected an object")
        if final:
            if part in current:
                raise _fail(
                    "CAPABILITY_MISMATCH", _path_text(path),
                    "provider extension collides with an exact mapped field",
                )
            current[part] = deepcopy(item)
        else:
            if part not in current:
                current[part] = [] if isinstance(following, int) else {}
            current = current[part]


def _delete(value: object, path: list[object]) -> bool:
    part = path[0]
    if isinstance(part, int):
        if not isinstance(value, list) or part >= len(value):
            return False
        if len(path) == 1:
            value[part] = None
        elif _delete(value[part], path[1:]) and isinstance(value[part], (dict, list)):
            value[part] = None
        while value and value[-1] is None:
            value.pop()
        return not value
    if not isinstance(value, dict) or part not in value:
        return False
    if len(path) == 1:
        del value[part]
    elif _delete(value[part], path[1:]) and isinstance(value[part], (dict, list)):
        del value[part]
    return not value


def _pop(value: object, path: list[object]) -> object:
    found = _get(value, path)
    if found is _MISSING:
        return _MISSING
    result = deepcopy(found)
    _delete(value, path)
    return result


def _set_static(target: dict, values: dict[str, object]) -> None:
    for path, value in values.items():
        _put(target, path.split("."), value)


def _match(target: dict, values: dict[str, object]) -> bool:
    return all(_get(target, path.split(".")) == value for path, value in values.items())


def _remove_static(target: dict, values: dict[str, object]) -> None:
    for path, expected in values.items():
        parts = path.split(".")
        if _get(target, parts) != expected:
            raise _fail("INVALID_REQUEST", path, "provider frame disagrees with its pinned schema")
        _pop(target, parts)


def _codec(value: object, name: str, *, encode: bool, adapter: "NamedAdapter") -> object:
    if name == "identity":
        return deepcopy(value)
    if name == "model":
        return adapter._wire_model(value) if encode else adapter._canonical_model(value)
    if name == "json":
        if encode:
            return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        if not isinstance(value, str):
            raise _fail("INVALID_REQUEST", adapter.name, "provider tool arguments must be JSON text")
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise _fail("INVALID_REQUEST", adapter.name, "provider tool arguments are invalid JSON") from exc
    raise _fail("INVALID_REQUEST", adapter.name, f"unknown generated field codec {name!r}")


def _mapped(source: dict, target: dict, fields: list[dict], adapter: "NamedAdapter") -> None:
    for field in fields:
        value = _pop(source, field["canonical"])
        if value is _MISSING:
            continue
        _put(target, field["wire"], _codec(value, field["codec"], encode=True, adapter=adapter))


def _unmapped(source: dict, target: dict, fields: list[dict], adapter: "NamedAdapter") -> None:
    for field in fields:
        value = _pop(source, field["wire"])
        if value is _MISSING:
            continue
        _put(target, field["canonical"], _codec(value, field["codec"], encode=False, adapter=adapter))


def _merge_disjoint(target: dict, extra: dict, object_id: str) -> None:
    for key, value in extra.items():
        if key not in target:
            target[key] = deepcopy(value)
        elif isinstance(target[key], dict) and isinstance(value, dict):
            _merge_disjoint(target[key], value, f"{object_id}.{key}")
        else:
            raise _fail("CAPABILITY_MISMATCH", f"{object_id}.{key}", "record has duplicate authority")


def _headers(headers: object, object_id: str, *, forbid_sensitive: bool) -> dict:
    if not isinstance(headers, dict) or any(
        not isinstance(name, str) or not isinstance(value, str) for name, value in headers.items()
    ):
        raise _fail("INVALID_REQUEST", object_id, "wire headers must be a string map")
    for name, value in headers.items():
        if (
            not name or not name.isascii()
            or any(not character.isalnum() and character not in _HEADER_TOKEN for character in name)
            or "\r" in value or "\n" in value
        ):
            raise _fail("INVALID_REQUEST", object_id, f"header {name!r} is not HTTP-safe")
        if forbid_sensitive and name.lower() in _SENSITIVE_HEADERS:
            raise _fail(
                "CAPABILITY_MISMATCH", object_id,
                f"credential header {name!r} cannot enter the canonical extension namespace",
            )
    return deepcopy(headers)


def _route_id(value: object, object_id: str) -> str:
    if (
        not isinstance(value, str) or not value or not value.isascii()
        or any(not character.isalnum() and character not in "._:-" for character in value)
    ):
        raise _fail("INVALID_REQUEST", object_id, "operation identity is not safe for this route")
    return value


class NamedAdapter:
    """A stateless Q31 translator selected entirely by generated Q76 maps."""

    def __init__(
        self,
        name: str,
        *,
        model_aliases: dict[str, str] | None = None,
        server_contract: bool = False,
    ) -> None:
        if name not in ADAPTER_PROTOCOLS:
            raise _fail("INVALID_REQUEST", name, "unknown named adapter")
        aliases = model_aliases or {}
        if any(not isinstance(key, str) or not key or not isinstance(value, str) or not value
               for key, value in aliases.items()):
            raise _fail("INVALID_REQUEST", name, "model aliases must map nonempty strings")
        if len(set(aliases.values())) != len(aliases):
            raise _fail("INVALID_REQUEST", name, "model aliases must be reversible")
        self.name = name
        self._definition = ADAPTER_PROTOCOLS[name]
        self._aliases = dict(aliases)
        self._reverse_aliases = {value: key for key, value in aliases.items()}
        self._server_contract = server_contract

    @property
    def definition(self) -> dict:
        """Return the pinned generated map without exposing mutable shared data."""
        return deepcopy(self._definition)

    def _ready(self) -> None:
        if self._definition["requires_server_contract"] and not self._server_contract:
            raise _fail(
                "CAPABILITY_MISMATCH", self.name,
                "raw model weights do not establish the required agent server contract",
            )

    def _wire_model(self, model_ref: object) -> object:
        if self._definition["model_scope"] != "agent":
            return deepcopy(model_ref)
        if not isinstance(model_ref, str) or model_ref not in self._aliases:
            raise _fail(
                "CAPABILITY_MISMATCH", str(model_ref),
                "the canonical model revision has no explicit OpenClaw agent target",
            )
        return self._aliases[model_ref]

    def _canonical_model(self, wire_ref: object) -> object:
        if self._definition["model_scope"] != "agent":
            return deepcopy(wire_ref)
        if not isinstance(wire_ref, str) or wire_ref not in self._reverse_aliases:
            raise _fail(
                "CAPABILITY_MISMATCH", str(wire_ref),
                "the OpenClaw agent target has no canonical model revision",
            )
        return self._reverse_aliases[wire_ref]

    def _surface(self, surface: str | None) -> dict:
        self._ready()
        selected = surface or self._definition["default_surface"]
        if selected not in self._definition["surfaces"]:
            raise _fail("CAPABILITY_MISMATCH", f"{self.name}:{selected}", "surface is unsupported")
        return self._definition["surfaces"][selected]

    def _feature(self, surface: dict, name: str) -> None:
        status = surface["features"].get(name, "UNSUPPORTED")
        if status != "EXACT":
            raise _fail(
                "CAPABILITY_MISMATCH", f"{self.name}:{name}",
                f"the selected wire marks this semantic {status}; Cassette requires EXACT",
            )

    def _request_features(self, request: dict, surface: dict) -> None:
        self._feature(surface, "text")
        for field, feature in (
            ("reasoning", "reasoning"), ("tools", "tools"),
            ("output_schema", "structured_output"),
        ):
            if field in request:
                self._feature(surface, feature)
        if request.get("generation", {}).get("stream"):
            self._feature(surface, "streaming")

    def _extensions(self, canonical: dict, allowed: set[str]) -> dict:
        extensions = canonical.pop("extensions", {})
        if set(extensions) - {self._definition["namespace"]}:
            raise _fail(
                "CAPABILITY_MISMATCH", self.name,
                "the selected wire cannot carry another provider's extension namespace",
            )
        selected = deepcopy(extensions.get(self._definition["namespace"], {}))
        if not isinstance(selected, dict) or set(selected) - allowed:
            raise _fail(
                "CAPABILITY_MISMATCH", self.name,
                f"provider extension permits only {sorted(allowed)} on this record",
            )
        return selected

    def to_wire_request(self, request: dict, *, surface: str | None = None) -> dict:
        """Validate and encode one canonical RunRequest for a pinned client surface."""
        canonical = _validated("run_request", request)
        selected_name = surface or self._definition["default_surface"]
        selected = self._surface(selected_name)
        self._request_features(canonical, selected)
        if selected_name == "canonical":
            return {"encoding": "jsonl", "record": canonical}
        extension = self._extensions(canonical, {"body", "headers"})
        body = extension.get("body", {})
        if not isinstance(body, dict):
            raise _fail("INVALID_REQUEST", self.name, "provider body extension must be an object")
        headers = _headers(extension.get("headers", {}), self.name, forbid_sensitive=True)
        wire = {
            "method": selected["method"], "path": selected["path"],
            "headers": headers, "body": deepcopy(body),
        }
        for path, status in selected["blocked_wire"].items():
            if _get(wire, path.split(".")) is not _MISSING:
                raise _fail(
                    "CAPABILITY_MISMATCH", f"{self.name}:{path}",
                    f"the pinned protocol marks this semantic {status}",
                )
        _set_static(wire, selected["static"])
        _mapped(canonical, wire, selected["fields"], self)
        if canonical.get("generation") == {}:
            del canonical["generation"]
        if canonical:
            raise _fail(
                "CAPABILITY_MISMATCH", f"{self.name}:{selected_name}",
                f"canonical fields have no exact wire mapping: {sorted(canonical)}",
            )
        return wire

    def from_wire_request(self, wire: dict, *, surface: str | None = None) -> dict:
        """Decode one provider request and retain every safe provider-only field."""
        selected_name = surface or self._definition["default_surface"]
        selected = self._surface(selected_name)
        if selected_name == "canonical":
            if not isinstance(wire, dict) or set(wire) != {"encoding", "record"} or wire.get("encoding") != "jsonl":
                raise _fail("INVALID_REQUEST", self.name, "custom requests require one JSONL record")
            return _validated("run_request", wire["record"])
        if not isinstance(wire, dict) or set(wire) != {"method", "path", "headers", "body"}:
            raise _fail("INVALID_REQUEST", self.name, "wire request has an unknown envelope field")
        if wire["method"] != selected["method"] or wire["path"] != selected["path"]:
            raise _fail("INVALID_REQUEST", self.name, "wire request uses the wrong method or path")
        work = {"headers": deepcopy(wire["headers"]), "body": deepcopy(wire["body"])}
        if not isinstance(work["body"], dict):
            raise _fail("INVALID_REQUEST", self.name, "wire body must be an object")
        work["headers"] = _headers(work["headers"], self.name, forbid_sensitive=False)
        for mapping in selected["fields"]:
            path = mapping["wire"]
            if path[:1] != ["headers"] or _get(work, path) is not _MISSING:
                continue
            wanted = str(path[1]).lower()
            matches = [name for name in work["headers"] if name.lower() == wanted]
            if len(matches) > 1:
                raise _fail("INVALID_REQUEST", self.name, f"duplicate HTTP header {path[1]!r}")
            if matches:
                work["headers"][path[1]] = work["headers"].pop(matches[0])
        for path, status in selected["blocked_wire"].items():
            if _get(work, path.split(".")) is not _MISSING:
                raise _fail(
                    "CAPABILITY_MISMATCH", f"{self.name}:{path}",
                    f"the pinned protocol marks this semantic {status}",
                )
        _remove_static(work, selected["static"])
        canonical: dict = {}
        _unmapped(work, canonical, selected["fields"], self)
        for name in tuple(work.get("headers", {})):
            if name.lower() in _SENSITIVE_HEADERS or name.lower() in {"content-type", "accept"}:
                del work["headers"][name]
        residue = {name: value for name, value in work.items() if value != {}}
        if residue:
            canonical["extensions"] = {self._definition["namespace"]: residue}
        canonical.setdefault("generation", {})
        result = _validated("run_request", canonical)
        self._request_features(result, selected)
        return result

    def to_wire_capabilities(self, profiles: list[dict]) -> dict:
        """Encode exact discovery; native model rows are never treated as full capabilities."""
        self._ready()
        if not isinstance(profiles, list) or not profiles:
            raise _fail("INVALID_REQUEST", self.name, "discovery requires at least one capability")
        canonical = [_validated("capability_profile", profile) for profile in profiles]
        discovery = self._definition["discovery"]
        if discovery["format"] == "canonical":
            return {"encoding": "jsonl", "record": {"capabilities": canonical}}
        items = []
        sidecar = []
        seen_models: set[str] = set()
        for profile in canonical:
            extension = self._extensions(profile, {"models"})
            model_extensions = extension.get("models", {})
            if not isinstance(model_extensions, dict):
                raise _fail("INVALID_REQUEST", self.name, "discovery model extensions must be an object")
            if set(model_extensions) - set(profile["model_refs"]):
                raise _fail("CAPABILITY_MISMATCH", self.name, "model extension names an absent model")
            sidecar.append(profile)
            for model_ref in profile["model_refs"]:
                if model_ref in seen_models:
                    raise _fail("CAPABILITY_MISMATCH", model_ref, "model has two capability authorities")
                seen_models.add(model_ref)
                extra = model_extensions.get(model_ref, {})
                if not isinstance(extra, dict):
                    raise _fail("INVALID_REQUEST", model_ref, "model extension must be an object")
                if discovery["format"] == "ollama_tags":
                    item = {"name": self._wire_model(model_ref), "model": self._wire_model(model_ref)}
                else:
                    item = {"id": self._wire_model(model_ref), "object": "model"}
                for field, value in extra.items():
                    if field in item:
                        raise _fail("CAPABILITY_MISMATCH", model_ref, "model extension collides with discovery")
                    item[field] = deepcopy(value)
                if discovery["format"] != "ollama_tags":
                    item.setdefault("owned_by", "cassette")
                items.append(item)
        body = {"models": items} if discovery["format"] == "ollama_tags" else {
            "object": "list", "data": items,
        }
        body["x_cassette"] = {
            "capabilities": sidecar,
            "adapter_version": self._definition["adapter_version"],
            "field_status": deepcopy(self._definition["field_status"]),
            "surface_status": {
                name: {
                    "request": deepcopy(surface["features"]),
                    "events": deepcopy(surface["event_features"]),
                }
                for name, surface in self._definition["surfaces"].items()
            },
        }
        result = {"method": discovery["method"], "path": discovery["path"], "body": body}
        if discovery["format"] == "ollama_tags":
            result["detail_requests"] = [
                {
                    "method": discovery["detail_method"], "path": discovery["detail_path"],
                    "body": {"model": item["model"]},
                }
                for item in items
            ]
        return result

    def from_wire_capabilities(self, wire: dict) -> list[dict]:
        """Decode discovery only when the exact Cassette capability sidecar is present."""
        self._ready()
        discovery = self._definition["discovery"]
        if discovery["format"] == "canonical":
            if not isinstance(wire, dict) or wire.get("encoding") != "jsonl":
                raise _fail("INVALID_REQUEST", self.name, "custom discovery requires JSONL")
            record = wire.get("record")
            if not isinstance(record, dict) or set(record) != {"capabilities"}:
                raise _fail("INVALID_REQUEST", self.name, "custom discovery record is malformed")
            return [_validated("capability_profile", profile) for profile in record["capabilities"]]
        allowed = {"method", "path", "body"}
        if discovery["format"] == "ollama_tags":
            allowed.add("detail_requests")
        if not isinstance(wire, dict) or set(wire) != allowed:
            raise _fail("INVALID_REQUEST", self.name, "discovery envelope is malformed")
        if wire.get("method") != discovery["method"] or wire.get("path") != discovery["path"]:
            raise _fail("INVALID_REQUEST", self.name, "discovery uses the wrong method or path")
        body = wire.get("body")
        if not isinstance(body, dict) or not isinstance(body.get("x_cassette"), dict):
            raise _fail(
                "CAPABILITY_MISMATCH", self.name,
                "native model names cannot fabricate a canonical capability profile",
            )
        sidecar = body["x_cassette"]
        expected_body_fields = (
            {"models", "x_cassette"}
            if discovery["format"] == "ollama_tags"
            else {"object", "data", "x_cassette"}
        )
        if set(body) != expected_body_fields or (
            discovery["format"] != "ollama_tags" and body.get("object") != "list"
        ):
            raise _fail("CAPABILITY_MISMATCH", self.name, "discovery has unmapped top-level fields")
        if set(sidecar) != {"capabilities", "adapter_version", "field_status", "surface_status"}:
            raise _fail("INVALID_REQUEST", self.name, "capability sidecar has unknown fields")
        if sidecar.get("adapter_version") != self._definition["adapter_version"]:
            raise _fail("CAPABILITY_MISMATCH", self.name, "discovery adapter version is stale")
        expected_surface_status = {
            name: {"request": surface["features"], "events": surface["event_features"]}
            for name, surface in self._definition["surfaces"].items()
        }
        if (
            sidecar["field_status"] != self._definition["field_status"]
            or sidecar["surface_status"] != expected_surface_status
        ):
            raise _fail("CAPABILITY_MISMATCH", self.name, "discovery field status is stale")
        profiles = [_validated("capability_profile", profile) for profile in sidecar.get("capabilities", [])]
        items = body.get("models") if discovery["format"] == "ollama_tags" else body.get("data")
        if not isinstance(items, list):
            raise _fail("INVALID_REQUEST", self.name, "native discovery list is missing")
        native: dict[str, dict] = {}
        for item in items:
            if not isinstance(item, dict):
                raise _fail("INVALID_REQUEST", self.name, "native model row must be an object")
            if discovery["format"] == "ollama_tags":
                if item.get("name") != item.get("model"):
                    raise _fail("CAPABILITY_MISMATCH", self.name, "Ollama name and model disagree")
                wire_ref = item.get("model")
                base_fields = {"name", "model"}
            else:
                if item.get("object") != "model":
                    raise _fail("INVALID_REQUEST", self.name, "OpenAI model row has the wrong object")
                wire_ref = item.get("id")
                base_fields = {"id", "object"}
            canonical_ref = self._canonical_model(wire_ref)
            if canonical_ref in native:
                raise _fail("INVALID_REQUEST", canonical_ref, "native discovery model is duplicated")
            extra = {key: deepcopy(value) for key, value in item.items() if key not in base_fields}
            if extra.get("owned_by") == "cassette":
                del extra["owned_by"]
            native[canonical_ref] = extra
        expected = {model_ref for profile in profiles for model_ref in profile["model_refs"]}
        if set(native) != expected:
            raise _fail("CAPABILITY_MISMATCH", self.name, "native model list disagrees with capability sidecar")
        for profile in profiles:
            extras = {model_ref: native[model_ref] for model_ref in profile["model_refs"] if native[model_ref]}
            if extras:
                profile["extensions"] = {self._definition["namespace"]: {"models": extras}}
            _validated("capability_profile", profile)
        if discovery["format"] == "ollama_tags":
            expected_details = [
                {
                    "method": discovery["detail_method"], "path": discovery["detail_path"],
                    "body": {"model": item["model"]},
                }
                for item in items
            ]
            if wire["detail_requests"] != expected_details:
                raise _fail("CAPABILITY_MISMATCH", self.name, "Ollama /api/show requests disagree")
        return profiles

    def _event_feature(self, event: dict, surface: dict) -> None:
        event_surface = {**surface, "features": surface["event_features"]}
        if event["type"] == "reasoning_delta":
            self._feature(event_surface, "reasoning")
        if event["type"] in {"tool_call", "tool_result"}:
            self._feature(event_surface, "tools")
        self._feature(event_surface, "streaming")

    @staticmethod
    def _trace(events: list[dict], object_id: str) -> None:
        if not events:
            return
        run_id = events[0]["run_id"]
        previous = events[0]["sequence"] - 1
        terminal = False
        for event in events:
            if event["run_id"] != run_id or event["sequence"] != previous + 1 or terminal:
                raise _fail(
                    "INVALID_REQUEST", object_id,
                    "event IDs, contiguous sequence, or terminal transition are invalid",
                )
            previous = event["sequence"]
            terminal = event["type"] in _TERMINAL_EVENTS

    def to_wire_events(self, events: list[dict], *, surface: str | None = None) -> dict:
        """Encode an ordered canonical event trace through one generated event map."""
        selected_name = surface or self._definition["default_surface"]
        selected = self._surface(selected_name)
        canonical = [_validated("run_event", event) for event in events]
        self._trace(canonical, f"{self.name}:{selected_name}")
        if selected_name == "canonical":
            return {"encoding": "jsonl", "records": canonical}
        event_format = ADAPTER_EVENT_FORMATS[selected["event_format"]]
        frames = []
        for event in canonical:
            self._event_feature(event, selected)
            if event["type"] not in event_format["events"]:
                raise _fail(
                    "CAPABILITY_MISMATCH", f"{self.name}:{event['type']}",
                    "the selected event surface has no exact transition",
                )
            spec = event_format["events"][event["type"]]
            extension = self._extensions(event, {"frame"})
            frame = extension.get("frame", {})
            if not isinstance(frame, dict):
                raise _fail("INVALID_REQUEST", self.name, "provider frame extension must be an object")
            frame = deepcopy(frame)
            _set_static(frame, spec["selector"])
            _set_static(frame, spec["static"])
            event.pop("type")
            _mapped(event, frame, spec["fields"], self)
            if event.get("payload") == {}:
                del event["payload"]
            if set(event) - {"payload"}:
                raise _fail("INVALID_REQUEST", self.name, "generated event map omitted canonical identity")
            if "payload" in event:
                _put(frame, ["x_cassette", "payload"], event["payload"])
            frames.append(frame)
        return {"encoding": event_format["encoding"], "frames": frames}

    def from_wire_events(self, wire: dict, *, surface: str | None = None) -> list[dict]:
        """Decode ordered provider frames, preserving every provider-only field."""
        selected_name = surface or self._definition["default_surface"]
        selected = self._surface(selected_name)
        if selected_name == "canonical":
            if not isinstance(wire, dict) or set(wire) != {"encoding", "records"} or wire.get("encoding") != "jsonl":
                raise _fail("INVALID_REQUEST", self.name, "custom events require JSONL records")
            result = [_validated("run_event", event) for event in wire["records"]]
            self._trace(result, self.name)
            return result
        event_format = ADAPTER_EVENT_FORMATS[selected["event_format"]]
        if not isinstance(wire, dict) or set(wire) != {"encoding", "frames"}:
            raise _fail("INVALID_REQUEST", self.name, "wire event stream has an unknown field")
        if wire["encoding"] != event_format["encoding"] or not isinstance(wire["frames"], list):
            raise _fail("INVALID_REQUEST", self.name, "wire event encoding is wrong")
        result = []
        for supplied in wire["frames"]:
            if not isinstance(supplied, dict):
                raise _fail("INVALID_REQUEST", self.name, "wire event frame must be an object")
            matches = [
                (event_type, spec) for event_type, spec in event_format["events"].items()
                if _match(supplied, spec["selector"])
            ]
            if len(matches) != 1:
                raise _fail("INVALID_REQUEST", self.name, "wire event selector is absent or ambiguous")
            event_type, spec = matches[0]
            work = deepcopy(supplied)
            _remove_static(work, spec["selector"])
            _remove_static(work, spec["static"])
            canonical = {"type": event_type, "payload": {}}
            _unmapped(work, canonical, spec["fields"], self)
            residual_payload = _pop(work, ["x_cassette", "payload"])
            if residual_payload is not _MISSING:
                if not isinstance(residual_payload, dict):
                    raise _fail("INVALID_REQUEST", self.name, "Cassette event payload extension is malformed")
                _merge_disjoint(canonical["payload"], residual_payload, "payload")
            residue = work
            if residue:
                canonical["extensions"] = {self._definition["namespace"]: {"frame": residue}}
            event = _validated("run_event", canonical)
            self._event_feature(event, selected)
            result.append(event)
        self._trace(result, f"{self.name}:{selected_name}")
        return result

    def to_wire_operation(self, action: str, record: dict) -> dict:
        """Encode cancellation, status, or training through native control or the Q6 extension."""
        self._ready()
        if action not in self._definition["operations"]:
            raise _fail("CAPABILITY_MISMATCH", f"{self.name}:{action}", "operation is unsupported")
        kind = "operation" if action == "status" else "request"
        canonical = _validated(kind, record)
        if action == "training" and canonical["operation"] != "train":
            raise _fail("INVALID_REQUEST", action, "training transport requires operation=train")
        if action == "cancel" and canonical["operation"] != "cancel":
            raise _fail("INVALID_REQUEST", action, "cancellation transport requires operation=cancel")
        if action in {"training", "cancel"} and not canonical.get("target"):
            raise _fail("INVALID_REQUEST", action, "operation target is required")
        route = self._definition["operations"][action]
        object_id = canonical["operation_id"] if action == "status" else canonical.get("target", "")
        if "{" in route["path"]:
            object_id = _route_id(object_id, action)
        path = route["path"].format(run_id=object_id, operation_id=object_id)
        if route["method"] == "JSONL":
            return {"encoding": "jsonl", "action": action, "record": canonical}
        if route["transport"] == "native":
            if canonical["protocol_version"] != "1" or canonical["arguments"] != {}:
                raise _fail(
                    "CAPABILITY_MISMATCH", object_id,
                    "the native cancellation wire cannot carry protocol or argument extensions",
                )
            return {
                "method": route["method"], "path": path, "transport": "native",
                "headers": {"Idempotency-Key": canonical["idempotency_key"]}, "body": {},
            }
        return {
            "method": route["method"], "path": path, "transport": route["transport"],
            "body": canonical,
        }

    def from_wire_operation(self, action: str, wire: dict) -> dict:
        """Decode one control/status/training trace without creating lifecycle state."""
        self._ready()
        if action not in self._definition["operations"]:
            raise _fail("CAPABILITY_MISMATCH", f"{self.name}:{action}", "operation is unsupported")
        kind = "operation" if action == "status" else "request"
        route = self._definition["operations"][action]
        if route["method"] == "JSONL":
            if not isinstance(wire, dict) or set(wire) != {"encoding", "action", "record"}:
                raise _fail("INVALID_REQUEST", self.name, "custom operation record is malformed")
            if wire["encoding"] != "jsonl" or wire["action"] != action:
                raise _fail("INVALID_REQUEST", self.name, "custom operation action is wrong")
            canonical = _validated(kind, wire["record"])
            if action == "training" and canonical["operation"] != "train":
                raise _fail("INVALID_REQUEST", action, "training transport requires operation=train")
            if action == "cancel" and canonical["operation"] != "cancel":
                raise _fail("INVALID_REQUEST", action, "cancellation transport requires operation=cancel")
            if action in {"training", "cancel"} and not canonical.get("target"):
                raise _fail("INVALID_REQUEST", action, "operation target is required")
            return canonical
        if route["transport"] == "native":
            if not isinstance(wire, dict) or set(wire) != {
                "method", "path", "transport", "headers", "body",
            }:
                raise _fail("INVALID_REQUEST", self.name, "native operation envelope is malformed")
            if (
                wire["method"] != route["method"] or wire["transport"] != "native"
                or wire["body"] != {}
            ):
                raise _fail("INVALID_REQUEST", self.name, "native operation fields are malformed")
            headers = _headers(wire["headers"], self.name, forbid_sensitive=False)
            template = route["path"]
            marker = "{run_id}"
            if marker not in template:
                raise _fail("INVALID_REQUEST", self.name, "native operation route lacks its run ID")
            prefix, suffix = template.split(marker)
            if not wire["path"].startswith(prefix) or not wire["path"].endswith(suffix):
                raise _fail("INVALID_REQUEST", self.name, "native operation path is malformed")
            target = wire["path"][len(prefix):len(wire["path"]) - len(suffix) if suffix else None]
            target = _route_id(target, action)
            if set(headers) != {"Idempotency-Key"}:
                raise _fail("INVALID_REQUEST", self.name, "native operation identity is missing")
            canonical = {
                "protocol_version": "1", "operation": "cancel",
                "idempotency_key": headers["Idempotency-Key"],
                "target": target, "arguments": {},
            }
            return _validated("request", canonical)
        if not isinstance(wire, dict) or set(wire) != {"method", "path", "transport", "body"}:
            raise _fail("INVALID_REQUEST", self.name, "operation envelope is malformed")
        canonical = _validated(kind, wire["body"])
        object_id = canonical["operation_id"] if action == "status" else canonical.get("target", "")
        if "{" in route["path"]:
            object_id = _route_id(object_id, action)
        expected_path = route["path"].format(run_id=object_id, operation_id=object_id)
        if (
            wire["method"] != route["method"] or wire["path"] != expected_path
            or wire["transport"] != route["transport"]
        ):
            raise _fail("INVALID_REQUEST", self.name, "operation route disagrees with its Q6 record")
        if action == "training" and canonical["operation"] != "train":
            raise _fail("INVALID_REQUEST", action, "training transport requires operation=train")
        if action == "cancel" and canonical["operation"] != "cancel":
            raise _fail("INVALID_REQUEST", action, "cancellation transport requires operation=cancel")
        if action in {"training", "cancel"} and not canonical.get("target"):
            raise _fail("INVALID_REQUEST", action, "operation target is required")
        return canonical
