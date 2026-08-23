# resource_frontier.py — deterministic Q37 mathematical-resource and simulated storage-class curves; depends on store.py.
"""Emit prediction-only resource curves without touching hardware, models, or live services."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from store import canonical_bytes, digest_bytes


_RESOURCE_FIELDS = {
    "name", "atom_count", "max_atom_rank", "description_bytes_peak",
    "description_bytes_total", "metadata_bytes_peak", "metadata_bytes_total",
    "fresh_samples_max", "fresh_samples_total", "fresh_traffic_max",
    "fresh_traffic_total", "fresh_traffic_unit", "fresh_bytes_total",
    "fresh_page_reads_total", "epsilon_exec", "delta_exec_total", "horizon",
}
_SCALE_FIELDS = {"name", "model_bytes", "page_bytes", "context_bytes"}
_PROFILE_FIELDS = {
    "name", "evidence_kind", "sustained_read_bytes_per_second",
    "p99_read_latency_ns", "recommended_max_working_set_bytes",
    "index_record_bytes",
}


def _u64(value: object, label: str, *, positive: bool = False) -> int:
    if type(value) is not int or value < int(positive) or value > 2**64 - 1:
        raise ValueError(f"{label} must be one bounded unsigned integer")
    return value


def _record(value: object, fields: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label} requires exactly {sorted(fields)}")
    return value


def resource_frontier(
    resources: object, scales: object, profiles: object
) -> dict:
    """Cross exact resource vectors with simulated profiles under Q37's declared lower bounds."""

    if not isinstance(resources, list) or not 0 < len(resources) <= 256:
        raise ValueError("resources must be one bounded nonempty list")
    if not isinstance(scales, list) or not 0 < len(scales) <= 256:
        raise ValueError("scales must be one bounded nonempty list")
    if not isinstance(profiles, list) or not 0 < len(profiles) <= 256:
        raise ValueError("profiles must be one bounded nonempty list")
    resource_rows = [_record(row, _RESOURCE_FIELDS, "resource vector") for row in resources]
    scale_rows = [_record(row, _SCALE_FIELDS, "scale point") for row in scales]
    profile_rows = [_record(row, _PROFILE_FIELDS, "storage profile") for row in profiles]
    points = []
    for resource in resource_rows:
        for field in _RESOURCE_FIELDS - {
            "name", "fresh_traffic_unit", "epsilon_exec", "delta_exec_total",
        }:
            _u64(resource[field], f"resource {field}")
        if not isinstance(resource["name"], str) or not resource["name"]:
            raise ValueError("resource name must be nonempty text")
        if resource["fresh_traffic_unit"] not in {"BYTES", "COLUMNS", "SCALARS"}:
            raise ValueError("fresh traffic unit is unsupported")
        for field in ("epsilon_exec", "delta_exec_total"):
            if type(resource[field]) not in {int, float} or not 0 <= resource[field] <= 1:
                raise ValueError(f"resource {field} must lie in [0,1]")
        for scale in scale_rows:
            if not isinstance(scale["name"], str) or not scale["name"]:
                raise ValueError("scale name must be nonempty text")
            for field in _SCALE_FIELDS - {"name"}:
                _u64(scale[field], f"scale {field}", positive=True)
            pages = (scale["model_bytes"] + scale["page_bytes"] - 1) // scale["page_bytes"]
            for profile in profile_rows:
                if (
                    not isinstance(profile["name"], str)
                    or not profile["name"]
                    or profile["evidence_kind"] != "SIMULATED_RECORDED_CLASS"
                ):
                    raise ValueError("profile requires one name and a simulated recorded storage class")
                bandwidth = _u64(
                    profile["sustained_read_bytes_per_second"],
                    "sustained read bandwidth",
                    positive=True,
                )
                latency = _u64(profile["p99_read_latency_ns"], "p99 read latency")
                memory = _u64(
                    profile["recommended_max_working_set_bytes"],
                    "recommended working set",
                    positive=True,
                )
                index_bytes = pages * _u64(
                    profile["index_record_bytes"], "index record bytes", positive=True
                )
                metadata_total = resource["metadata_bytes_total"] + index_bytes
                metadata_peak = resource["metadata_bytes_peak"] + index_bytes
                loaded = (
                    resource["description_bytes_total"]
                    + metadata_total
                    + resource["fresh_bytes_total"]
                )
                service_ns = (
                    loaded * 1_000_000_000 + bandwidth - 1
                ) // bandwidth + resource["fresh_page_reads_total"] * latency
                peak = (
                    resource["description_bytes_peak"]
                    + metadata_peak
                    + scale["context_bytes"]
                )
                points.append({
                    "resource_vector": resource["name"],
                    "scale": scale["name"],
                    "storage_profile": profile["name"],
                    "atom_count": resource["atom_count"],
                    "max_atom_rank": resource["max_atom_rank"],
                    "description_bytes_peak": resource["description_bytes_peak"],
                    "description_bytes_total": resource["description_bytes_total"],
                    "metadata_bytes_peak": metadata_peak,
                    "metadata_bytes_total": metadata_total,
                    "fresh_samples_max": resource["fresh_samples_max"],
                    "fresh_samples_total": resource["fresh_samples_total"],
                    "fresh_traffic_max": resource["fresh_traffic_max"],
                    "fresh_traffic_total": resource["fresh_traffic_total"],
                    "fresh_traffic_unit": resource["fresh_traffic_unit"],
                    "epsilon_exec": resource["epsilon_exec"],
                    "delta_exec_total": resource["delta_exec_total"],
                    "horizon": resource["horizon"],
                    "page_bytes": scale["page_bytes"],
                    "page_count": pages,
                    "model_bytes": scale["model_bytes"],
                    "context_bytes": scale["context_bytes"],
                    "predicted_loaded_bytes": loaded,
                    "predicted_working_set_bytes": peak,
                    "predicted_physical_service_ns": service_ns,
                    "within_simulated_working_set": peak <= memory,
                })
    body = {
        "version": "q37-machine-frontier-v1",
        "claim": "PREDICTION_ONLY_NO_F4_F5_OR_PHYSICAL_QUALIFICATION",
        "resources": resource_rows,
        "scales": scale_rows,
        "profiles": profile_rows,
        "points": points,
    }
    return {**body, "frontier_digest": digest_bytes(canonical_bytes(body))}


def machine_fixture_frontier() -> dict:
    """Return the committed S25 exact/fresh lower-stage curve input and prediction set."""

    resources = [
        {
            "name": "f2-exact",
            "atom_count": 1,
            "max_atom_rank": 2,
            "description_bytes_peak": 16,
            "description_bytes_total": 16,
            "metadata_bytes_peak": 256,
            "metadata_bytes_total": 256,
            "fresh_samples_max": 0,
            "fresh_samples_total": 0,
            "fresh_traffic_max": 0,
            "fresh_traffic_total": 0,
            "fresh_traffic_unit": "SCALARS",
            "fresh_bytes_total": 0,
            "fresh_page_reads_total": 0,
            "epsilon_exec": 0,
            "delta_exec_total": 0,
            "horizon": 2,
        },
        {
            "name": "f3-fresh",
            "atom_count": 3,
            "max_atom_rank": 1,
            "description_bytes_peak": 1024,
            "description_bytes_total": 3072,
            "metadata_bytes_peak": 256,
            "metadata_bytes_total": 768,
            "fresh_samples_max": 16,
            "fresh_samples_total": 48,
            "fresh_traffic_max": 48,
            "fresh_traffic_total": 144,
            "fresh_traffic_unit": "SCALARS",
            "fresh_bytes_total": 12288,
            "fresh_page_reads_total": 3,
            "epsilon_exec": 0.5,
            "delta_exec_total": 0.75,
            "horizon": 3,
        },
    ]
    scales = [
        {"name": "fixture", "model_bytes": 4 * 1024**2, "page_bytes": 4 * 1024**2, "context_bytes": 4096},
        {"name": "simulated-35g", "model_bytes": 35 * 1024**3, "page_bytes": 4 * 1024**2, "context_bytes": 2 * 1024**3},
        {"name": "simulated-120g", "model_bytes": 120 * 1024**3, "page_bytes": 4 * 1024**2, "context_bytes": 8 * 1024**3},
    ]
    profiles = [
        {
            "name": "simulated-usbc-flash",
            "evidence_kind": "SIMULATED_RECORDED_CLASS",
            "sustained_read_bytes_per_second": 130_000_000,
            "p99_read_latency_ns": 12_000_000,
            "recommended_max_working_set_bytes": 8 * 1024**3,
            "index_record_bytes": 76,
        },
        {
            "name": "simulated-usbc-ssd",
            "evidence_kind": "SIMULATED_RECORDED_CLASS",
            "sustained_read_bytes_per_second": 1_050_000_000,
            "p99_read_latency_ns": 2_000_000,
            "recommended_max_working_set_bytes": 24 * 1024**3,
            "index_record_bytes": 76,
        },
        {
            "name": "simulated-thunderbolt-ssd",
            "evidence_kind": "SIMULATED_RECORDED_CLASS",
            "sustained_read_bytes_per_second": 2_800_000_000,
            "p99_read_latency_ns": 500_000,
            "recommended_max_working_set_bytes": 64 * 1024**3,
            "index_record_bytes": 76,
        },
    ]
    return resource_frontier(resources, scales, profiles)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = canonical_bytes(machine_fixture_frontier()) + b"\n"
    if args.output is None:
        print(payload.decode(), end="")
    else:
        args.output.write_bytes(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
