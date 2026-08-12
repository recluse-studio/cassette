# compiler_fixture.py — canonical small dense SafeTensors compiler material for S16/S19; depends on schema/tables.py, store.py.
"""Build one exact data-only source whose manifest is derived and independently verifiable."""

from __future__ import annotations

import copy
import hashlib
import struct

from schema.tables import DISPATCH_ROWS, Q40_MODES
from store import ArtifactIdentity, IdentityTuple, canonical_bytes, digest_bytes

GIB = 1024**3
CASE = {
    name: DISPATCH_ROWS[0][name]
    for name in (
        "case_id", "operator", "input_dtypes", "input_shapes", "output_dtype",
        "output_shape", "parameters",
    )
}


def _digest(value: object) -> str:
    return digest_bytes(canonical_bytes(value))


def manifest(label: str) -> dict:
    condition = "condition.identity"
    atom = "atom.identity"
    face = "face.identity"
    operation = "operation.matmul"
    law = "sampling.exact"
    metric = [["1" if row == column else "0" for column in range(4)] for row in range(4)]
    evidence = {
        "target": {
            "field": "REAL",
            "source_shape": [2, 2],
            "shape": [2, 2],
            "flattening_order": [0, 1, 2, 3],
        },
        "conditions": [
            {
                "condition_id": condition,
                "metric": metric,
                "provenance": {"fixture": label, "law": "identity-metric"},
            }
        ],
        "atoms": [
            {
                "atom_id": atom,
                "matrix": [[1, 0], [0, 1]],
                "service_face_id": face,
                "description": {
                    "class": "EXACT",
                    "description_bytes": 16,
                    "metadata_bytes": 256,
                    "reconstruction": [[1, 0], [0, 1]],
                    "estimator": {"kind": "NONE"},
                    "estimator_calibration": {
                        "distortion": "0",
                        "atom_norm_squared": "2",
                    },
                    "sampling_law_id": law,
                },
            }
        ],
        "description_contract": {
            "description_family": {"kind": "DECLARED_RECONSTRUCTION"},
            "distortion_metric": {"kind": "FROBENIUS_SQUARED"},
            "estimator_family": {"kind": "RESIDUAL_COLUMN_OR_EXACT"},
            "residual_family": {"relation": "ATOM_MINUS_RECONSTRUCTION"},
        },
        "observation_contract": {
            "kind": "PROTECTED_TEST_LAW",
            "experiment": {"name": "small-dense-identity"},
            "support": [condition],
            "selector": [{"condition_id": condition, "atom_id": atom}],
            "loss_family": {"kind": "condition-quadratic-loss"},
            "sample_count": 1,
            "confidence": 0.99,
            "off_support": "REJECT",
        },
        "execution_contract": {
            "sampling_laws": [
                {
                    "sampling_law_id": law,
                    "kind": "EXACT",
                    "law": {"family": "NO_RESIDUAL", "atom_ids": [atom]},
                    "work_unit": "COLUMNS",
                    "seed_policy": "NONE",
                }
            ],
            "operations": [
                {
                    "operation_id": operation,
                    "operator_case_id": CASE["case_id"],
                    "rank_accounting": {"kind": "ATOM_BOUND", "maximum_rank": 2},
                    "loss_propagation": {"coefficient": "1", "remainder_bound": "0"},
                    "sampling_law_id": law,
                }
            ],
            "risk_composition": {"kind": "DETERMINISTIC", "proof": {"rule": "exact"}},
        },
        "trace_contract": {
            "protected_trace_family": {"name": "one-exact-step"},
            "prefix_policy": "COHERENT_RESTRICTION",
            "fresh_traffic_unit": "SCALARS",
            "steps": [
                {
                    "step": 0,
                    "operation_id": operation,
                    "atom_id": atom,
                    "fresh_samples": 0,
                    "fresh_traffic": 0,
                }
            ],
        },
        "physical_conversion": {
            "conversion_rows": [
                {
                    "operation_id": operation,
                    "probe_unit": "COLUMNS",
                    "probes": 0,
                    "page_reads": 0,
                    "bytes": 0,
                    "memory_bytes_peak": 272,
                    "latency_ns_peak": 0,
                }
            ]
        },
        "minimal_nonface_proofs": [],
        "excluded_conditions": [],
    }
    return {
        "version": "s19-compiler-v1",
        "model": {
            "architecture": "SmallDenseTransformer",
            "config": {"fixture": label, "hidden_size": 2},
            "format_versions": [["safetensors", "1"]],
            "precision_scheme": "f32",
            "processor_digest": _digest({"processor": label}),
            "template_digest": _digest({"template": label}),
            "tokenizer_digest": _digest({"tokenizer": label}),
        },
        "target_tensor": "weight",
        "evidence": evidence,
        "profile": {
            "activation_bytes": 0,
            "cache_bytes": 0,
            "context_bytes": 0,
            "execution_bytes": 0,
            "other_observed_bytes": 0,
            "physical_bytes": 16 * GIB,
            "recommended_max_working_set_bytes": 16 * GIB,
            "runtime_buffer_bytes": 0,
            "training_window_bytes": 0,
        },
        "eta_rep": 0.0,
        "rank_budget": 2,
        "operation_bounds": [
            {"operation_id": operation, "epsilon_exec": 0.0, "delta_exec": 0.0}
        ],
        "operator_inventory": [copy.deepcopy(CASE)],
        "prior_mode_failures": [
            {
                "ordinal": index + 1,
                "mode": mode,
                "q38_record_digest": _digest({"fixture": label, "failed_mode": mode}),
            }
            for index, mode in enumerate(Q40_MODES[:-1])
        ],
    }


def artifact(
    source_kind: str,
    locator: str,
    immutable_revision: str,
    license_digest: str,
    artifact_path: str,
    *,
    label: str | None = None,
    mutate_manifest=None,
    tensor: tuple[str, tuple[int, ...], bytes] | None = None,
) -> tuple[bytes, IdentityTuple, dict]:
    document = manifest(source_kind if label is None else label)
    if mutate_manifest is not None:
        mutate_manifest(document)
    metadata = canonical_bytes(document).decode()
    dtype, shape, weights = tensor or (
        "F32", (2, 2), struct.pack("<4f", 1.0, 0.0, 0.0, 1.0)
    )
    header = {
        "__metadata__": {"cassette.compiler.v1": metadata},
        "weight": {"dtype": dtype, "shape": list(shape), "data_offsets": [0, len(weights)]},
    }
    encoded = canonical_bytes(header)
    encoded += b" " * (-len(encoded) % 8)
    payload = len(encoded).to_bytes(8, "little") + encoded + weights
    tensor_index = [
        {
            "artifact_path": artifact_path,
            "semantic_tensor_id": "weight",
            "dtype": dtype,
            "shape": list(shape),
            "offset": 0,
            "length": len(weights),
        }
    ]
    material = IdentityTuple(
        revision_kind="source",
        source_kind=source_kind,
        source_alias=locator,
        canonical_locator=locator,
        requested_revision=None,
        immutable_revision=immutable_revision,
        artifacts=(ArtifactIdentity(
            artifact_path,
            len(payload),
            "sha256:" + hashlib.sha256(payload).hexdigest(),
        ),),
        format_versions=tuple(tuple(item) for item in document["model"]["format_versions"]),
        tensor_index_digest=_digest(tensor_index),
        config_digest=_digest(document["model"]["config"]),
        architecture=document["model"]["architecture"],
        operator_set=tuple(sorted({row["operator"] for row in document["operator_inventory"]})),
        tokenizer_digest=document["model"]["tokenizer_digest"],
        processor_digest=document["model"]["processor_digest"],
        template_digest=document["model"]["template_digest"],
        precision_scheme=document["model"]["precision_scheme"],
        license_digest=license_digest,
        parent_ids=(),
        transform_manifest_digest=None,
    )
    return payload, material, document


def sharded_artifacts(
    source_kind: str,
    locator: str,
    immutable_revision: str,
    license_digest: str,
    artifact_paths: tuple[str, str],
    *,
    label: str,
) -> tuple[dict[str, bytes], IdentityTuple, dict]:
    """Build two independently hashed containers whose tensor-to-artifact map is identity-bound."""

    document = manifest(label)
    metadata = canonical_bytes(document).decode()
    tensors = (
        (artifact_paths[0], "bias", "F32", [2], struct.pack("<2f", 0.25, -0.25)),
        (artifact_paths[1], "weight", "F32", [2, 2], struct.pack("<4f", 1.0, 0.0, 0.0, 1.0)),
    )
    payloads = {}
    tensor_index = []
    artifacts = []
    for artifact_path, tensor_id, dtype, shape, values in tensors:
        header = {
            "__metadata__": {"cassette.compiler.v1": metadata},
            tensor_id: {"dtype": dtype, "shape": shape, "data_offsets": [0, len(values)]},
        }
        encoded = canonical_bytes(header)
        encoded += b" " * (-len(encoded) % 8)
        payload = len(encoded).to_bytes(8, "little") + encoded + values
        payloads[artifact_path] = payload
        artifacts.append(ArtifactIdentity(
            artifact_path,
            len(payload),
            "sha256:" + hashlib.sha256(payload).hexdigest(),
        ))
        tensor_index.append({
            "artifact_path": artifact_path,
            "semantic_tensor_id": tensor_id,
            "dtype": dtype,
            "shape": shape,
            "offset": 0,
            "length": len(values),
        })
    tensor_index.sort(key=lambda row: row["semantic_tensor_id"])
    material = IdentityTuple(
        revision_kind="source",
        source_kind=source_kind,
        source_alias=locator,
        canonical_locator=locator,
        requested_revision=None,
        immutable_revision=immutable_revision,
        artifacts=tuple(sorted(artifacts, key=lambda item: item.path)),
        format_versions=tuple(tuple(item) for item in document["model"]["format_versions"]),
        tensor_index_digest=_digest(tensor_index),
        config_digest=_digest(document["model"]["config"]),
        architecture=document["model"]["architecture"],
        operator_set=tuple(sorted({row["operator"] for row in document["operator_inventory"]})),
        tokenizer_digest=document["model"]["tokenizer_digest"],
        processor_digest=document["model"]["processor_digest"],
        template_digest=document["model"]["template_digest"],
        precision_scheme=document["model"]["precision_scheme"],
        license_digest=license_digest,
        parent_ids=(),
        transform_manifest_digest=None,
    )
    return payloads, material, document
