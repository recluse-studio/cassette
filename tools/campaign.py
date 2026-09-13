# campaign.py — approved attempts, evidence graphs, review ownership and campaign measurements (Q33/Q44/Q48/Q79/Q80); depends on errors.py, store.py, tools.
"""Execute the campaign's evidence controls; physical claims require physical observations."""
from __future__ import annotations

import argparse
import asyncio
import copy
import itertools
import json
import math
import os
from pathlib import Path
import platform
import plistlib
import re
import resource
import stat
import subprocess
import sys
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import yaml

from errors import CassetteError
from store import CapacityCoordinator, artifact_hasher, campaign_head, campaign_profile_io, canonical_bytes, compare_campaign_head, compare_inventory, digest_bytes, inventory_step, write_campaign_artifact
from tools.ledger import remediation_diff


def reject(object_id, detail, code="PROVENANCE_VIOLATION"):
    raise CassetteError(code, str(object_id), "Q80: exact campaign evidence", "terminal", detail)


def identity(value):
    return digest_bytes(canonical_bytes(value))


def file_digest(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as handle:
        before = os.fstat(handle.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            reject(path, "evidence must be an unlinked regular file")
        hasher = artifact_hasher("blake3:", str(path))
        while chunk := handle.read(1024 * 1024):
            hasher.update(chunk)
        after = os.fstat(handle.fileno())
        if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            reject(path, "evidence changed during hashing")
        return "blake3:" + hasher.hexdigest()


def namespace(root):
    """Q60/Q80: enumerate every entry using lstat; never follow links or special files."""
    root = Path(root)
    result = {}
    pending = [root]
    while pending:
        path = pending.pop()
        metadata = path.lstat()
        relative = path.relative_to(root).as_posix()
        if stat.S_ISDIR(metadata.st_mode):
            result[relative] = {"type": "directory"}
            pending.extend(sorted(path.iterdir(), reverse=True))
        elif stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1:
            result[relative] = {"type": "file", "bytes": metadata.st_size, "digest": file_digest(path)}
        else:
            reject(relative, "namespace contains a link or special object")
    return result


def seal_namespace(root, binding, *, missing=()):
    entries = namespace(root)
    result = {"binding": binding, "entries": entries, "missing": sorted(missing),
              "status": "CAPTURE_FAILED" if missing else "CAPTURED"}
    return {**result, "digest": identity(result)}


def verify_namespace(root, seal):
    body = {key: value for key, value in seal.items() if key != "digest"}
    if identity(body) != seal["digest"] or namespace(root) != seal["entries"]:
        reject(root, "sealed namespace has missing, extra or changed entries")
    if seal["missing"] or seal["status"] != "CAPTURED":
        reject(root, "capture is incomplete; retained bytes are recovery evidence only")
    return seal["digest"]


PERMISSIONS = {'READ_ONLY', 'CAMPAIGN_DIRECTORY_WRITE', 'PHYSICAL_FAULT', 'DESTRUCTIVE'}


def number(value, field, *, integer=False, positive=False, maximum=None):
    """Reject missing, boolean, nonfinite and out-of-range measurements before arithmetic."""
    if (type(value) not in ({int} if integer else {int, float})
            or (type(value) is float and not math.isfinite(value)) or value < 0 or (positive and value == 0)
            or (maximum is not None and value > maximum)):
        reject(field, 'measurement has an invalid type, unit count or range')
    return value


def validate_binding(binding):
    fields = {'template', 'approval_digest', 'inputs', 'graph_digest', 'operation_id', 'started_ns', 'digest'}
    if set(binding) != fields or identity({k:v for k,v in binding.items() if k != 'digest'}) != binding['digest']:
        reject('action', 'complete execution binding differs from its sealed digest')
    if identity(binding['template']) != binding['approval_digest']:
        reject('action', 'execution template differs from its approval')
    try:
        if str(uuid.UUID(binding['operation_id'])) != binding['operation_id']:
            raise ValueError('noncanonical operation identity')
        if not isinstance(binding['started_ns'], str) or not re.fullmatch(r'[1-9][0-9]*', binding['started_ns']):
            raise ValueError('invalid execution timestamp')
    except (ValueError, TypeError, AttributeError):
        reject('action', 'operation identity or timestamp is invalid')
    if binding['template']['permission'] not in PERMISSIONS or not isinstance(binding['inputs'], dict) or not binding['graph_digest']:
        reject('action', 'permission, inputs or graph identity is invalid')


def bind_action(template, approved_digest, inputs, graph_digest, *, now_ns=None):
    """Approval covers exact template fields; each launch gets a fresh identity."""
    required = {"command", "cwd", "permission", "host", "disk", "path", "stop_conditions", "next_byte_claim"}
    if set(template) != required or identity(template) != approved_digest:
        reject("action", "approved template differs from the proposed action")
    if template["permission"] not in PERMISSIONS:
        reject("action", "permission class is unknown")
    number(template['next_byte_claim'], 'next atomic byte claim', integer=True)
    if not isinstance(template["command"], list) or not template["command"] or not all(isinstance(x, str) for x in template["command"]):
        reject("action", "command must be a literal argument list")
    binding = copy.deepcopy({"template": template, "approval_digest": approved_digest, "inputs": inputs,
            "graph_digest": graph_digest, "operation_id": str(uuid.uuid4()),
            "started_ns": str(time.time_ns() if now_ns is None else now_ns)})
    binding["digest"] = identity(binding)
    validate_binding(binding)
    return binding


def capture_attempt(owner, stage, binding, *, expected=None, timeout=1200):
    """Count launch before execution; preserve raw output and a seal even on command failure."""
    validate_binding(binding)
    number(timeout, 'capture timeout seconds', positive=True)
    key = 'attempts-' + stage
    current = campaign_head(owner.cartridge, key)
    previous = current['value']['attempts'] if current else []
    if current and current['value'].get('active'):
        reject(key, 'prior capture must be recovered before another launch')
    if len(previous) >= 5:
        reject(key, 'five execution attempts are exhausted')
    if any(attempt['binding']['operation_id'] == binding['operation_id'] for attempt in previous):
        reject(key, 'execution binding reuses an earlier operation identity')
    if identity(binding['template']) != binding['approval_digest']:
        reject(key, 'execution template differs from its approval')
    attempt = {'number':len(previous)+1, 'binding':binding, 'status':'RUNNING'}
    head = compare_campaign_head(owner, key, expected, {'attempts':[*previous, attempt], 'active':True})
    name = binding['operation_id']
    write_campaign_artifact(owner, name, 'binding.json', canonical_bytes(binding))
    try:
        command = binding['template']['command']
        environment = {**os.environ, 'CASSETTE_EXECUTION_BINDING':canonical_bytes(binding).decode()}
        result = subprocess.run(command, cwd=binding['template']['cwd'], env=environment,
                                capture_output=True, timeout=timeout)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as error:
        stdout, stderr, code = error.stdout or b'', error.stderr or b'', None
    except OSError as error:
        stdout, stderr, code = b'', str(error).encode(), None
    write_campaign_artifact(owner, name, 'stdout.log', stdout)
    path = write_campaign_artifact(owner, name, 'stderr.log', stderr)
    write_campaign_artifact(owner, name, 'result.json', canonical_bytes({'exit_code':code}))
    seal = seal_namespace(path.parent, binding, missing=['terminal-exit'] if code is None else [])
    attempt = {**attempt, 'status':'CAPTURED' if code == 0 else 'CAPTURE_FAILED' if code is None else 'FAIL', 'seal':seal}
    return compare_campaign_head(owner, key, head['digest'], {'attempts':[*previous, attempt], 'active':False})


def verify_capture(root, attempt, replay):
    """Compare captured results with a verifier's independent replay of the sealed inputs.

    The verifier is trusted executable code: it must compute the expected result from the
    bound inputs and graph, without reading the child output. Exit zero and echoed IDs alone
    establish no result. The receipt binds the result to the complete launch identity.
    """
    binding = attempt['binding']
    validate_binding(binding)
    verify_namespace(root, attempt['seal'])
    if attempt['status'] != 'CAPTURED' or attempt['seal']['binding'] != binding:
        reject('capture', 'attempt is incomplete or its seal binds another launch')
    expected = replay(copy.deepcopy(binding))
    if expected is None:
        reject('capture', 'independent replay supplied no deciding result')
    try:
        receipt = json.loads((Path(root)/'stdout.log').read_bytes())
    except (ValueError, UnicodeError):
        reject('capture', 'child output is not a result receipt')
    if (not isinstance(receipt, dict) or set(receipt) != {'binding_digest', 'result'}
            or receipt['binding_digest'] != binding['digest']
            or canonical_bytes(receipt['result']) != canonical_bytes(expected)):
        reject('capture', 'result differs from the bound independent replay')
    return {'status':'PASS', 'binding_digest':binding['digest'],
            'capture_digest':attempt['seal']['digest'], 'result_digest':identity(expected)}


def recover_capture(owner, stage, expected):
    """Seal whatever an interrupted capture left; missing output never becomes passing evidence."""
    key = 'attempts-' + stage
    current = campaign_head(owner.cartridge, key)
    if current is None or not current['value']['active']:
        reject(key, 'no interrupted capture is active')
    attempts = copy.deepcopy(current['value']['attempts'])
    attempt = attempts[-1]
    root = owner.cartridge / 'captures' / attempt['binding']['operation_id']
    if not root.exists():
        write_campaign_artifact(owner, attempt['binding']['operation_id'], 'recovery.json', canonical_bytes({'capture_failed':True}))
    missing = [name for name in ['binding.json','stdout.log','stderr.log','result.json'] if not (root/name).is_file()]
    attempt.update(status='CAPTURE_FAILED', seal=seal_namespace(root, attempt['binding'], missing=[*missing,'unconfirmed-terminal']))
    return compare_campaign_head(owner,key,expected,{'attempts':attempts,'active':False})


def measure_profile(owner, binding, patterns, collect, *, expected=None):
    """Resume after the last sealed atom; boundary collectors supply physical device observations."""
    key = 'profile-' + identity(binding).split(':')[1]
    current = campaign_head(owner.cartridge, key)
    state = current['value'] if current else {'binding':binding, 'patterns':patterns, 'observations':[]}
    if state['binding'] != binding or state['patterns'] != patterns:
        reject(key, 'resumed profile changes the bound path or plan patterns')
    index = len(state['observations'])
    if index == len(patterns): return current
    pattern = patterns[index]
    before = collect(binding)
    observed = campaign_profile_io(owner, str(uuid.uuid4()), pattern)
    after = collect(binding)
    if before['binding'] != binding or after['binding'] != binding:
        reject(key, 'physical collector binding changed during the profile atom')
    for boundary in (before, after):
        for field in ('device_write_bytes', 'host_write_bytes'):
            number(boundary.get(field), field, integer=True)
    delta = after['device_write_bytes'] - before['device_write_bytes']
    host_delta = after['host_write_bytes'] - before['host_write_bytes']
    if delta < 0 or host_delta < 0: reject(key, 'write counter regressed')
    observation = {**observed, 'binding':binding, 'pattern':pattern, 'device_write_bytes':delta, 'host_write_bytes':host_delta,
                   'boundary_before':before, 'boundary_after':after}
    return compare_campaign_head(owner,key,expected, {**state,'observations':[*state['observations'],observation]})


def path_identity(root, *, disk_record, host_record):
    """Bind measured disk/host records without treating media descriptions as admission gates."""
    path = Path(root).resolve(strict=True)
    required_disk = {"physical_disk", "volume_uuid", "filesystem", "mount_point"}
    if not required_disk <= disk_record.keys() or not host_record.get("host_id"):
        reject(path, "disk or host identity is incomplete")
    mount = Path(disk_record["mount_point"]).resolve(strict=True)
    if path.stat().st_dev != mount.stat().st_dev:
        reject(path, "operation path differs from the bound mounted volume")
    return {"path": str(path), "device": str(path.stat().st_dev),
            "disk": disk_record, "host": host_record}


def collect_path_identity(root):
    """Read the exact macOS volume, physical-store chain and hardware UUID without writing the drive."""
    def plist(*command):
        result = subprocess.run(command,capture_output=True,timeout=10)
        if result.returncode:
            reject(root, f'identity collector failed: {command[0]}', 'CAPABILITY_MISMATCH')
        return plistlib.loads(result.stdout)
    mounted = subprocess.run(['/bin/df','-P',str(Path(root).resolve(strict=True))],capture_output=True,text=True,timeout=10)
    if mounted.returncode or len(mounted.stdout.splitlines()) != 2:
        reject(root,'mounted device could not be identified','CAPABILITY_MISMATCH')
    device = mounted.stdout.splitlines()[1].split()[0]
    volume = plist('/usr/sbin/diskutil','info','-plist',device)
    stores = volume.get('APFSPhysicalStores')
    if volume.get('FilesystemType') != 'apfs' or not stores:
        reject(root,'volume is not an identified locally attached APFS path','CAPABILITY_MISMATCH')
    physical = []
    for store in stores:
        partition = plist('/usr/sbin/diskutil','info','-plist',store['APFSPhysicalStore'])
        whole = plist('/usr/sbin/diskutil','info','-plist',partition['ParentWholeDisk'])
        physical.append({'partition':partition,'whole_disk':whole})
    hardware = plist('/usr/sbin/ioreg','-a','-r','-d','1','-c','IOPlatformExpertDevice')
    uuid_value = next((row['IOPlatformUUID'] for row in hardware if 'IOPlatformUUID' in row),None)
    if uuid_value is None: reject(root,'hardware UUID is unavailable')
    disk = {'physical_disk':[row['whole_disk']['DeviceIdentifier'] for row in physical],
            'volume_uuid':volume['VolumeUUID'],'filesystem':'apfs','mount_point':volume['MountPoint'],
            'volume_record':volume,'physical_stores':physical}
    host = {'host_id':identity({'hardware_uuid':uuid_value}), 'os':platform.platform(),
            'machine':platform.machine(), 'python':platform.python_version()}
    return path_identity(root,disk_record=disk,host_record=host)


def validate_graph(records, *, required_owners, parent=None, materializer="L04", registry_digest="", deferred_owners=None):
    """Q33/Q80: validate literal predecessors, complete owners and monotone extensions."""
    nodes = {}
    for record in records:
        required = {"id", "depends", "evidence_level", "matrix_assertion_owners", "owner_stage", "permission"}
        if not required <= record.keys() or record["id"] in nodes or re.search(r'[<>*]', record["id"]):
            reject("graph", "record fields, literal ID or uniqueness failed")
        if record["permission"] not in PERMISSIONS:
            reject(record["id"], "permission class is undeclared")
        if record["permission"] != "READ_ONLY":
            card = record.get('approved_card')
            if (not isinstance(card, dict) or identity(card) != record.get('approved_card_digest')
                    or card.get('permission') != record['permission'] or card.get('record_id') != record['id']
                    or not all(card.get(field) for field in ('command','disk','path','bound','stop_conditions'))):
                reject(record['id'], 'write-bearing record lacks its exact approved action card')
        if record["evidence_level"] not in {"UNIT", "INTEGRATION", "PLATFORM", "LIVE"}:
            reject(record["id"], "evidence level is unresolved")
        if len(set(record["depends"])) != len(record["depends"]):
            reject(record["id"], "predecessors contain duplicate IDs")
        nodes[record["id"]] = copy.deepcopy(record)
    owners = {}
    for key, node in nodes.items():
        if set(node["depends"]) - nodes.keys():
            reject(key, "graph has missing literal predecessors")
        for assertion in node["matrix_assertion_owners"]:
            owners.setdefault(assertion, []).append(key)
    if set(owners) != set(required_owners):
        reject("graph", "assertion owner set has missing or unknown authorities")
    for assertion, expected in required_owners.items():
        if sorted(owners[assertion]) != sorted(expected):
            reject(assertion, "assertion owners differ from their complete declared producer set")
    if deferred_owners is None:
        deferred_owners = parent.get("deferred_assertion_owners", {}) if parent else {}
    if parent:
        if identity({key:value for key,value in parent.items() if key != 'revision_digest'}) != parent['revision_digest']:
            reject('graph', 'parent graph content differs from its sealed revision')
        for key, value in parent["nodes"].items():
            if nodes.get(key) != value:
                reject(key, "successor rewrites or removes an inherited record or edge")
        if materializer not in parent["nodes"]:
            reject(materializer, "successor materializer is absent from its parent graph")
        for assertion, patterns in parent.get("deferred_assertion_owners", {}).items():
            if assertion not in deferred_owners and any(
                    not any(re.fullmatch(pattern, owner) for owner in owners.get(assertion, []))
                    for pattern in patterns):
                reject(assertion, "successor drops an unresolved matrix obligation")
    remaining, order = set(nodes), []
    while remaining:
        ready = sorted(key for key in remaining if set(nodes[key]["depends"]) <= set(order))
        if not ready:
            reject("graph", "dependency cycle prevents execution")
        order.extend(ready)
        remaining.difference_update(ready)
    body = {"nodes": nodes, "order": order, "required_owners": required_owners,
            "parent_graph_digest": parent["revision_digest"] if parent else None,
            "expansion_registry_digest": registry_digest, "materializer_record_id": materializer}
    if deferred_owners:
        body["deferred_assertion_owners"] = copy.deepcopy(deferred_owners)
    return {**body, "revision_digest": identity(body)}


def publish_graph(owner, graph, expected=None):
    """Seal a monotone graph successor and its ancestry under the single store CAS head."""
    current = campaign_head(owner.cartridge,'graph')
    parent = current['value']['graph'] if current else None
    verified = validate_graph(list(graph['nodes'].values()),required_owners=graph['required_owners'],parent=parent,
                              materializer=graph['materializer_record_id'],registry_digest=graph['expansion_registry_digest'],
                              deferred_owners=graph.get('deferred_assertion_owners', {}))
    if verified != graph:
        reject('graph','proposed graph identity differs from its verified successor')
    ancestors = [*current['value']['ancestors'],parent['revision_digest']] if current else []
    return compare_campaign_head(owner,'graph',expected,{'graph':graph,'ancestors':ancestors})


def invalidate_latest(owner, attempt_graph_digest, changed, declared):
    current = campaign_head(owner.cartridge,'graph')
    if current is None or attempt_graph_digest not in [*current['value']['ancestors'],current['value']['graph']['revision_digest']]:
        reject('invalidation','attempt graph is not an ancestor of the active graph')
    return invalidate(current['value']['graph'],changed,declared)


def descendants(graph, changed):
    affected = set(changed)
    if not affected <= graph["nodes"].keys():
        reject("invalidation", "changed records are absent from the graph")
    for key in graph["order"]:
        if affected.intersection(graph["nodes"][key]["depends"]):
            affected.add(key)
    return sorted(affected)


def invalidate(graph, changed, declared):
    expected = descendants(graph, changed)
    if sorted(declared) != expected:
        reject("invalidation", "declared invalidation omits or adds descendants")
    return {"graph_digest": graph["revision_digest"], "invalidated": expected,
            "operation_lineages": sorted({graph["nodes"][key].get("operation_id", key) for key in expected}),
            "qualification_lineages": sorted({value for key in expected
                for value in graph["nodes"][key].get("qualification_lineages", [])})}


def clean_replay(graph, members):
    """Preserve reachability through intermediate evidence levels in a fresh replay lineage."""
    if graph.get("deferred_assertion_owners"):
        reject("replay", "Q80 replay requires every matrix assertion owner to be materialized")
    members = set(members)
    if not members <= graph["nodes"].keys():
        reject("replay", "replay membership contains an unknown record")
    ancestors = {}
    for key in graph["order"]:
        ancestors[key] = set(graph["nodes"][key]["depends"])
        for predecessor in graph["nodes"][key]["depends"]:
            ancestors[key].update(ancestors[predecessor])
    return [{"id": "Q80-" + key, "source": key, "operation_id": str(uuid.uuid4()),
             "depends": ["Q80-" + p for p in sorted(ancestors[key] & members)]}
            for key in graph["order"] if key in members]


def coverage(required, completed):
    if len(set(required)) != len(required) or len(set(completed)) != len(completed) or set(completed) - set(required):
        reject("coverage", "coverage contains duplicate or unknown coordinates")
    missing = sorted(set(required) - set(completed))
    return {"status": "NOT_RUN" if missing else "PASS", "missing": missing,
            "required_digest": identity(sorted(required)), "completed": sorted(completed)}


class ReviewHistory:
    """Q80: one atomic record serializes lease succession and append-only review envelopes."""
    def __init__(self, owner, stage, attempt, machine_digest, *, manifest=None):
        self.owner = owner
        self.manifest = copy.deepcopy(manifest)
        if manifest is not None and (set(manifest) != {'candidate','assertions'}
                or set(manifest['candidate']) != {'parent','tree'}
                or any(not re.fullmatch(r'[0-9a-f]{40}', value) for value in manifest['candidate'].values())
                or not manifest['assertions'] or any(level not in {'STATIC','FIXTURE','INTEGRATION','PLATFORM'} for level in manifest['assertions'].values())
                or identity(manifest) != machine_digest):
            reject("review", "frozen manifest differs from the machine digest")
        self.binding = {"stage": stage, "attempt": attempt, "machine_digest": machine_digest}
        self.key = "review-" + identity(self.binding).split(':')[1]

    def read(self):
        return campaign_head(self.owner.cartridge, self.key)

    def acquire(self, holder, expected, *, now, expires, worktree):
        current = self.read()
        state = current['value'] if current else {"binding": self.binding, "envelopes": [], "terminal": False}
        lease = state.get('lease')
        if state['terminal'] or (lease and lease['released'] is False and now < lease['expires']):
            reject(self.key, "review is terminal or another unexpired lease owns it", "IDEMPOTENCY_CONFLICT")
        number(now, 'review time', integer=True)
        number(expires, 'lease expiry', integer=True)
        if now < state.get('last_event', 0) or not now < expires <= now + 1200:
            reject(self.key, "lease must expire within the twenty-minute review bound")
        lease = {"holder": holder, "acquired": now, "expires": expires, "released": False,
                 "worktree": str(Path(worktree).resolve()), "predecessor": identity(lease) if lease else None}
        return compare_campaign_head(self.owner, self.key, expected, {**state, "lease": lease, "last_event":now})

    def append(self, holder, expected, envelope, *, now):
        current = self.read()
        if current is None:
            reject(self.key, "review lease has not been acquired")
        number(now, 'review time', integer=True)
        state, lease = current['value'], current['value']['lease']
        if state['terminal'] or lease['holder'] != holder or lease['released'] or now >= lease['expires']:
            reject(self.key, "review lease is unavailable, expired or terminal", "IDEMPOTENCY_CONFLICT")
        if len(state['envelopes']) >= 5 or envelope.get('status') not in {'PASS_READY', 'INCOMPLETE', 'QUEUE_ROUTE', 'REMEDIATED'}:
            reject(self.key, "review envelope status or five-envelope bound failed")
        if envelope.get('binding') != self.binding:
            reject(self.key, "review envelope changes its execution binding")
        if type(now) is not int or now < state['last_event']:
            reject(self.key, 'review time precedes lease acquisition')
        self.validate_envelope(envelope, state, lease)
        envelopes = [*state['envelopes'], envelope]
        if len(envelopes) == 5 and envelope['status'] == 'INCOMPLETE':
            reject(self.key, "fifth incomplete envelope must route to the queue")
        terminal = envelope['status'] in {'PASS_READY', 'QUEUE_ROUTE', 'REMEDIATED'}
        return compare_campaign_head(self.owner, self.key, expected,
            {**state, "envelopes": envelopes, "terminal": terminal, "last_event":now,
             "lease": {**lease, "released": terminal}})

    def release(self, holder, expected, *, now):
        current = self.read()
        if current is None or current['value']['lease']['holder'] != holder:
            reject(self.key, "release does not own the current lease")
        state = current['value']
        if (state['terminal'] or state['lease']['released'] or type(now) is not int
                or now < state['last_event'] or not state['envelopes']):
            reject(self.key, 'release is terminal, repeated, unsealed or predates the last event')
        return compare_campaign_head(self.owner, self.key, expected,
            {**state, 'last_event':now, "lease": {**state['lease'], "released": True, "released_at": now}})

    def validate_envelope(self, envelope, state, lease):
        """Resolve every declared claim and raw proof against the frozen candidate before closure."""
        fields = {'review_id','binding','status','previous','candidate','assertions','evidence','findings','remediation','invalidation'}
        manifest = self.manifest
        if (set(envelope) != fields or not manifest or not envelope['review_id']
                or envelope['previous'] != (identity(state['envelopes'][-1]) if state['envelopes'] else None)
                or envelope['candidate'] != manifest['candidate']):
            reject(self.key, 'envelope fields, predecessor or frozen candidate differ')
        if any(row['review_id'] == envelope['review_id'] for row in state['envelopes']):
            reject(self.key, 'review identity was already used')
        rows = envelope['assertions']
        if (len(rows) != len(manifest['assertions']) or
                {row.get('assertion') for row in rows} != set(manifest['assertions'])):
            reject(self.key, 'review does not resolve the complete frozen assertion set')
        evidence = envelope['evidence']
        if not isinstance(evidence, dict) or not evidence:
            reject(self.key, 'review has no raw command evidence')
        for key, proof in evidence.items():
            if (set(proof) != {'path','digest','command','exit_code'} or not proof['command']
                    or not isinstance(proof['command'], list) or not all(isinstance(arg, str) for arg in proof['command'])
                    or type(proof['exit_code']) is not int or file_digest(proof['path']) != proof['digest']):
                reject(key, 'raw review artifact, command or exit result differs')
        for row in rows:
            if (set(row) != {'assertion','status','level','predicate','source_trace','challenge','expected','observed','evidence','discriminator'}
                    or row['status'] not in {'PASS','FAIL','NOT_RUN','BLOCKED'}
                    or row['level'] != manifest['assertions'][row['assertion']]
                    or not all(row[key] for key in ('predicate','source_trace','challenge','evidence','discriminator'))
                    or not set(row['evidence']) <= evidence.keys()
                    or row['discriminator'] not in evidence):
                reject(self.key, 'assertion lacks its declared level, trace, replay or discriminator')
            if row['status'] == 'PASS' and (row['expected'] != row['observed']
                    or any(evidence[key]['exit_code'] != 0 for key in row['evidence'])
                    or evidence[row['discriminator']]['exit_code'] == 0):
                reject(self.key, 'passing assertion lacks matching replay and failing discriminator')
        invalidation = envelope['invalidation']
        if (not isinstance(invalidation, dict) or set(invalidation) != {'class','ids','operation_lineages','qualification_lineages'}
                or invalidation['class'] not in {'replay_only','assertion_local_rerun','machine_proof_rerun_required','physical_requalification_required','mechanism_revision_new_campaign_required'}
                or any(not isinstance(invalidation[key], list) for key in ('ids','operation_lineages','qualification_lineages'))
                or (invalidation['class'] != 'replay_only' and not invalidation['ids'])):
            reject(self.key, 'invalidation class or affected identities are incomplete')
        findings = envelope['findings']
        if not isinstance(findings, list) or any(set(f) != {'id','assertion','cause'} or not f['id'] or not f['cause']
                or f['assertion'] not in manifest['assertions'] for f in findings):
            reject(self.key, 'finding identity or assertion is undeclared')
        if envelope['status'] == 'PASS_READY' and (findings or any(row['status'] != 'PASS' for row in rows)):
            reject(self.key, 'PASS_READY requires every assertion to pass without unresolved findings')
        if envelope['status'] != 'REMEDIATED':
            if envelope['remediation'] is not None:
                reject(self.key, 'non-remediation envelope carries a repair')
            return
        repair = envelope['remediation']
        if not isinstance(repair, dict) or set(repair) != {'parent','child','assertion','finding','diff','proofs'}:
            reject(self.key, 'remediation schema is incomplete')
        prior = [f for old in state['envelopes'] for f in old['findings']]
        if (not any(row['assertion'] == repair['assertion'] and row['status'] == 'FAIL'
                    for old in state['envelopes'] for row in old['assertions'])
                or repair['parent'] != manifest['candidate']['parent'] or repair['child'] == repair['parent']
                or not any(f['id'] == repair['finding'] and f['assertion'] == repair['assertion'] for f in prior)):
            reject(self.key, 'repair does not descend from the reviewed candidate and its finding')
        def git(*args):
            result = subprocess.run(['git','-C',lease['worktree'],*args],capture_output=True,text=True)
            if result.returncode: reject(self.key, 'remediation Git lineage cannot be resolved')
            return result.stdout.strip()
        if (git('rev-parse', repair['parent']+'^{tree}') != manifest['candidate']['tree']
                or git('rev-parse', repair['child']+'^') != repair['parent']):
            reject(self.key, 'repair is not the direct child of the exact reviewed tree')
        report = remediation_diff(Path(lease['worktree']), repair['parent'], repair['child'])
        if report != repair['diff'] or not report['within_limit'] or report['executable_line_changes'] == 0:
            reject(self.key, 'repair is empty, excessive or differs from the executable diff')
        if not any(row['assertion'] == repair['assertion'] and row['status'] == 'PASS' for row in rows):
            reject(self.key, 'remediated assertion has not passed')
        roles = {'parent_red','child_green','mutation','suite','ledger'}
        if set(repair['proofs']) != roles or not set(repair['proofs'].values()) <= evidence.keys():
            reject(self.key, 'remediation lacks parent, child, mutation, suite or ledger proof')
        for role, key in repair['proofs'].items():
            if (evidence[key]['exit_code'] == 0) != (role in {'child_green','suite','ledger'}):
                reject(self.key, 'remediation proof has the wrong outcome')



# Units are part of field names; counters are cumulative at each observation boundary.
COLLECTORS = {
    'process': {'pid':'identity', 'max_rss_bytes':'integer', 'user_cpu_seconds':'counter',
                'system_cpu_seconds':'counter', 'block_output_operations':'integer_counter'},
    'memory': {'rss_bytes':'integer', 'swap_bytes':'integer'},
    'power': {'power_watts':'number', 'critical_thermal_seconds':'counter'},
    'network': {'socket_count':'integer', 'received_bytes':'integer_counter', 'sent_bytes':'integer_counter'},
    'writes': {'host_write_bytes':'integer_counter', 'device_write_bytes':'integer_counter'},
}


def observation(collector, values, fields):
    schema = COLLECTORS.get(collector)
    if (schema is None or set(fields) != set(schema) or
            set(values) - {'binding'} != set(schema)):
        reject(collector, 'observation fields differ from the collector contract')
    for field, kind in schema.items():
        number(values[field], field, integer=kind in {'integer','integer_counter','identity'}, positive=kind == 'identity')
    return schema


def interval_evidence(binding, start, end, samples, required):
    """Q47/Q48/Q79: each mandatory collector covers the exact operation without gaps."""
    number(start, 'interval start')
    number(end, 'interval end')
    if end <= start or not required:
        reject("telemetry", "operation interval or required collector set is invalid")
    if set(required) - COLLECTORS.keys() or any(sample.get('collector') not in required for sample in samples):
        reject('telemetry', 'collector is undeclared')
    output = {}
    for collector, fields in required.items():
        trace = sorted((sample for sample in samples if sample.get('collector') == collector), key=lambda x: x['start'])
        cursor = start
        if not trace:
            reject(collector, "mandatory operation samples are missing")
        previous = None
        for sample in trace:
            number(sample['start'], 'sample start')
            number(sample['end'], 'sample end')
            if sample.get('binding') != binding or sample['start'] != cursor or not cursor < sample['end'] <= end:
                reject(collector, "sample binding or continuous operation interval differs")
            schema = observation(collector, sample.get('values', {}), fields)
            before = sample.get('before', {})
            observation(collector, before, fields)
            if any(value.get('binding', binding) != binding for value in (before, sample['values'])):
                reject(collector, 'boundary collector names another operation binding')
            if previous is not None and before != previous:
                reject(collector, 'adjacent observations do not share the same boundary')
            for field, kind in schema.items():
                if ('counter' in kind and sample['values'][field] < before[field]
                        or kind == 'identity' and sample['values'][field] != before[field]):
                    reject(collector, 'counter regressed or process identity changed')
            previous = sample['values']
            cursor = sample['end']
        if cursor != end:
            reject(collector, "collector does not reach the operation end")
        output[collector] = trace
    return {"binding": binding, "start": start, "end": end, "collectors": output, "status": "PASS"}


async def collect_interval(binding, operation, collectors, required, *, period_seconds=.1):
    """Collect boundary observations throughout the actual awaited operation in this process."""
    number(period_seconds, 'observation period seconds', positive=True, maximum=300)
    if set(collectors) != set(required):
        reject('telemetry', 'collector membership or observation period differs from its contract')
    def collect():
        values = {name: callback(binding) for name, callback in collectors.items()}
        for name, fields in required.items():
            observation(name, values[name], fields)
        return values
    previous = collect()
    started = cursor = time.monotonic()
    task = asyncio.create_task(operation())
    samples = []
    try:
        while True:
            done, _ = await asyncio.wait([task], timeout=period_seconds)
            observed = collect()
            end = time.monotonic()
            samples.extend({'binding':binding,'collector':name,'start':cursor,'end':end,
                            'values':observed[name],'before':previous[name]} for name in collectors)
            previous, cursor = observed, end
            if done:
                result = await task
                return {'result':result, 'evidence':interval_evidence(binding,started,end,samples,required)}
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


def process_observation(binding):
    """Observe this process; ru_oublock is reported as block operations, never device bytes."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {'pid':os.getpid(), 'max_rss_bytes':usage.ru_maxrss,
            'user_cpu_seconds':usage.ru_utime, 'system_cpu_seconds':usage.ru_stime,
            'block_output_operations':usage.ru_oublock, 'binding':binding}


def storage_profile(binding, patterns, observations, *, expected_binding):
    """Q41-Q44: assess independent read/write/flush observations for exact plan patterns."""
    if binding != expected_binding or not {'drive', 'host', 'path', 'operation', 'plan'} <= binding.keys():
        reject('profile', 'drive, host, path, operation or plan identity differs')
    if not patterns or len(patterns) != len(observations):
        reject('profile', 'profile observation coverage is incomplete')
    for pattern, observed in zip(patterns, observations, strict=True):
        if observed.get('pattern') != pattern or observed.get('binding') != binding:
            reject('profile', 'observation differs from the exact plan pattern')
        for field in ('read_bytes', 'write_bytes'):
            number(pattern.get(field), field, integer=True)
        for field in ('host_write_bytes', 'device_write_bytes', 'errors'):
            number(observed.get(field), field, integer=True)
        number(observed.get('duration_seconds'), 'duration seconds', positive=True)
        for field in ('read_seconds', 'write_seconds', 'flush_seconds'):
            if field in observed:
                number(observed[field], field, maximum=observed['duration_seconds'])
        if (observed.get('errors') != 0 or observed.get('readback_ok') is not True
                or observed.get('flush_ok') is not True or observed.get('duration_seconds', 0) <= 0):
            reject('profile', 'readback, flush, error or timing evidence failed')
        if observed.get('host_write_bytes', -1) < pattern.get('write_bytes', 0):
            reject('profile', 'observed host writes omit planned writes')
        if observed.get('device_write_bytes') is None:
            reject('profile', 'physical write observation is unavailable')
    latencies = sorted(x['duration_seconds'] for x in observations)
    def percentile(values, q):
        return values[max(0, math.ceil(q * len(values)) - 1)]
    throughput = sorted((p.get('read_bytes', 0) + p.get('write_bytes', 0)) / o['duration_seconds']
                        for p, o in zip(patterns, observations, strict=True))
    for value in throughput:
        number(value, 'derived throughput bytes per second')
    return {"binding": binding, "status": "PASS", "patterns_digest": identity(patterns),
            "throughput_bytes_per_second": {str(q): percentile(throughput, q) for q in (.05, .5, .95)},
            "latency_seconds": {str(q): percentile(latencies, q) for q in (.5, .95, .99, 1.)},
            "host_write_bytes": sum(x['host_write_bytes'] for x in observations),
            "device_write_bytes": sum(x['device_write_bytes'] for x in observations)}


def thermal_windows(windows, *, slc_bytes, training, warmup_end, knee_duty, duty_experiments, binding, recovery_end):
    """Q48/Q74: require a continuous two-hour trace and cache-exhausting training writes."""
    number(slc_bytes, 'SLC bytes', integer=True, positive=True)
    number(warmup_end, 'warmup end')
    number(recovery_end, 'recovery end')
    number(knee_duty, 'duty knee', positive=True, maximum=1)
    if type(training) is not bool:
        reject('thermal', 'training flag must be boolean')
    for trial in duty_experiments:
        number(trial.get('duty'), 'trial duty', positive=True, maximum=1)
        if type(trial.get('sustained')) is not bool:
            reject('thermal', 'sustained trial flag must be boolean')
    if len(windows) < 24:
        reject('thermal', 'duration, cache-volume or duty-knee evidence is incomplete')
    start = number(windows[0].get('start'), 'thermal interval start')
    if start < recovery_end:
        reject('thermal', 'continuous proof interval began before recovery completed')
    cursor, written, tokens = start, 0, 0
    stable = []
    if not any(x['duty'] > knee_duty and x['sustained'] is False for x in duty_experiments) or not any(
            x['duty'] <= knee_duty and x['sustained'] is True for x in duty_experiments):
        reject('thermal', 'independent above/below-knee experiments are missing')
    for window in windows:
        if window.get('binding') != binding:
            reject('thermal', 'window belongs to a different operation interval')
        for field in ('rd_p05','bs_bytes_per_second','bm_proxy_bytes_per_second','power_watts','start','end'):
            number(window.get(field), field)
        for field in ('device_write_bytes','host_write_bytes','tokens','integrity_errors'):
            number(window.get(field), field, integer=True)
        number(window.get('critical_thermal_seconds'), 'critical thermal seconds', maximum=300)
        number(window.get('duty'), 'duty', positive=True, maximum=1)
        if any(type(window.get(field)) is not bool for field in ('q68_pass','q74_pass')):
            reject('thermal', 'admission flags must be boolean')
        if window['start'] != cursor or window['end'] - cursor != 300:
            reject('thermal', 'five-minute measurement windows are discontinuous')
        if window['integrity_errors'] or window['critical_thermal_seconds'] > 60:
            reject('thermal', 'integrity or critical thermal bound failed', 'THERMAL_LIMIT')
        if not window['q68_pass'] or not window['q74_pass']:
            reject('thermal', 'execution service or endurance admission failed', 'ENDURANCE_EXCEEDED')
        if window['host_write_bytes'] < 0 or window['tokens'] < 0 or window['rd_p05'] <= 0:
            reject('thermal', 'write, token or throughput observation is invalid')
        if window['start'] >= warmup_end:
            stable.append(window['rd_p05'])
        if window['duty'] > knee_duty:
            reject('thermal', 'passing continuous interval exceeds the measured duty knee')
        written += window['host_write_bytes']; tokens += window['tokens']; cursor = window['end']
    if cursor - start < 7200 or len(stable) < 4 or (training and written < 2 * slc_bytes) or (not training and tokens < 20000):
        reject('thermal', 'continuous duration, stable baseline, tokens or cache-write volume is insufficient')
    baseline = sum(stable[:4]) / 4
    if min(stable) < .9 * baseline:
        reject('thermal', 'throughput decay exceeds ten percent', 'THERMAL_LIMIT')
    return {"status": "PASS", "duration_seconds": cursor-start, "host_write_bytes": written,
            "tokens": tokens, "baseline_rd_p05": baseline, "binding":binding,
            "device_write_bytes":sum(window['device_write_bytes'] for window in windows)}


def load_contracts(root):
    root = Path(root)
    text = (root / 'IMPLEMENTATION.md').read_text()
    blocks = re.findall(r'```yaml\n(.*?)```', text, re.S)
    block = next((value for value in blocks if value.startswith('phase_live_queue:')), None)
    if block is None:
        reject(root, 'phase_live_queue YAML authority is missing')
    return yaml.safe_load(block)['phase_live_queue'], yaml.safe_load((root / 'research/ACCEPTANCE_MATRIX.yaml').read_text())


def matrix_assertions(matrix):
    """Retain the literal source path and text for every matrix-owned acceptance assertion."""
    result = {}
    assertion_keys = {'assertions', 'required_assertions', 'portability_assertions', 'required_for_every_training_row', 'pass_condition'}
    def walk(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = path + '.' + key if path else key
                if key in assertion_keys:
                    items = child if isinstance(child, list) else [child]
                    for index, item in enumerate(items):
                        result[f'matrix#{child_path}[{index}]'] = item
                else: walk(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                selector = f'id={child["id"]}' if isinstance(child, dict) and 'id' in child else str(index)
                walk(child, path + '[' + selector + ']')
    walk(matrix, '')
    return result


def failure_binding(record, coordinate, contract, registry, records, parent):
    """Resolve one failure coordinate to its exact source, plan, qualification and action card."""
    operation = coordinate['operation']
    authority = contract['phase_live_operation_bindings'].get(operation)
    if authority is None:
        reject(record['id'], 'failure operation has no matrix subject')
    source_id, qualification_id = authority['source_artifact_record'], authority['starting_profile_record']
    nodes = {row['id']:row for row in records}
    source, qualification = nodes.get(source_id), nodes.get(qualification_id)
    binding = registry.get('operation_bindings', {}).get(coordinate['injection']+':'+operation)
    fields = {'source_artifact_record_id','source_artifact_digest','operation_plan_digest',
              'physical_qualification_record_id','logical_operation_id','state'}
    if not source or not qualification or not binding or set(binding) != fields:
        reject(record['id'], 'failure source, qualification or unique operation binding is absent')
    if (binding['state'] != 'PENDING' or binding['source_artifact_record_id'] != source_id
            or binding['physical_qualification_record_id'] != qualification_id
            or binding['source_artifact_digest'] != source.get('artifact_digest')
            or binding['operation_plan_digest'] != source.get('operation_plan_digest')
            or qualification.get('source_artifact_digest') != binding['source_artifact_digest']
            or qualification.get('operation_plan_digest') != binding['operation_plan_digest']):
        reject(record['id'], 'failure subject or qualified plan differs, or operation is already terminal')
    for field in ('source_artifact_digest','operation_plan_digest'):
        if not re.fullmatch(r'blake3:[0-9a-f]{64}', binding[field]):
            reject(record['id'], 'source or plan digest is invalid')
    try:
        if str(uuid.UUID(binding['logical_operation_id'])) != binding['logical_operation_id']: raise ValueError()
    except (ValueError, TypeError, AttributeError):
        reject(record['id'], 'logical operation identity is invalid')
    operations = [row['logical_operation_id'] for row in registry['operation_bindings'].values()]
    if len(set(operations)) != len(operations) or (parent and record['id'] not in parent['nodes'] and any(
            node.get('logical_operation_id') == binding['logical_operation_id'] for node in parent['nodes'].values()
            if node['id'] != record['id'])):
        reject(record['id'], 'logical operation identity is reused across coordinates or prior graph')
    if any(record.get(field) != value for field,value in binding.items() if field != 'state'):
        reject(record['id'], 'record differs from its frozen operation binding')
    required = contract['requalification_after_recovery']['required_for']
    omitted = contract['requalification_after_recovery']['not_applicable_for']
    injection = coordinate['injection']
    if (injection in required) == (injection in omitted) or record.get('requalification_required') is not (injection in required):
        reject(record['id'], 'requalification differs from the matrix injection rule')
    card = registry.get('approved_cards', {}).get(record.get('approved_card_digest'))
    if (not card or identity(card) != record['approved_card_digest']
            or card.get('permission') != record['permission']
            or card.get('logical_operation_id') != binding['logical_operation_id']
            or card.get('source_artifact_digest') != binding['source_artifact_digest']
            or card.get('physical_qualification_record_id') != qualification_id
            or card.get('record_id') != record['id'] or not card.get('command') or not card.get('stop_conditions')):
        reject(record['id'], 'failure coordinate lacks its exact approved action card')
    approvals = contract['approval_contract']
    if (coordinate['record'] == 'INJECT' and injection in approvals['physical_fault_card_required_for']
            and record['permission'] != 'PHYSICAL_FAULT'):
        reject(record['id'], 'physical injection requires its physical-fault permission class')
    if not all(card.get(field) for field in ('disk','path','bound')):
        reject(record['id'], 'action card omits its exact disk, path or byte/state bound')
    if record['permission'] not in PERMISSIONS:
        reject(record['id'], 'failure permission is undeclared')
    return binding


def historical_steps(root):
    """Read completed machine prerequisites from the queue's historical prose records."""
    text = (Path(root)/'IMPLEMENTATION.md').read_text()
    blocks = re.findall(r'```yaml\n(.*?)```', text, re.S)
    records = {}
    for block in (value for value in blocks if value.startswith('steps:')):
        for match in re.finditer(r'^  - id: (S[0-9]+)\n(.*?)(?=^  - id: |\Z)', block, re.M | re.S):
            status = re.search(r'^    status: (.*)$', match[2], re.M)
            dependencies = re.search(r'^    depends: (.*)$', match[2], re.M)
            if status and re.match(r'''^["']?DONE(?:\s|$)''', status[1]) and dependencies:
                records[match[1]] = {'id': match[1], 'depends': yaml.safe_load(dependencies[1]),
                    'status': status[1], 'authority_digest': identity(match[0])}
    return records


def materialize(root, registry, *, parent=None):
    """Expand frozen family coordinates against generated contracts and preserve inherited records."""
    queue, matrix = load_contracts(root)
    generated = json.loads((Path(root)/'schema/campaign/contract.json').read_text())
    if any(generated[key] != queue[key] for key in queue.keys() & generated.keys()):
        reject('materialization', 'generated campaign contracts differ from the queue')
    if registry.get('matrix_digest') != file_digest(Path(root)/'research/ACCEPTANCE_MATRIX.yaml'):
        reject('materialization', 'frozen matrix digest differs')
    failure_contract = generated.get('failure_contract')
    if failure_contract is not None and any(failure_contract[key] != matrix['failure_rows'][key] for key in failure_contract):
        reject('materialization', 'generated failure operation contract differs from the matrix')
    families = {family['family']: family for family in generated['expanded_session_families']}
    if set(registry['families']) - families.keys():
        reject('materialization', 'registry contains an unknown family')
    records = copy.deepcopy(registry.get('fixed_records', []))
    fixed_authorities = {record['id']: record for record in [*queue['fixed_steps'], *queue['operation_records']]}
    aggregates = {}
    for name in registry['families']:
        family = families[name]
        if 'aggregate_record' in family:
            key = family['aggregate_record']
            if key in fixed_authorities or key in aggregates:
                reject(key, 'aggregate has more than one declaration')
            aggregates[key] = {'depends': family['aggregate_dependencies'],
                'owner_stage': family.get('aggregate_owner_stage', family['owner_stage']),
                'evidence_level': generated['materialized_record_contract']['family_evidence_levels'][name]}
    if set(aggregates) - {record['id'] for record in records}:
        reject('materialization', 'registered family omits its declared aggregate record')
    fixed_authorities.update(aggregates)
    historical = historical_steps(root)
    fixed_authorities.update(historical)
    for record in records:
        if record['id'] not in fixed_authorities:
            reject(record['id'], 'fixed record is absent from the execution queue')
        if record['id'] in aggregates and any(record[field] != aggregates[record['id']][field]
                                               for field in ('owner_stage', 'evidence_level')):
            reject(record['id'], 'aggregate owner or evidence level differs from its declared family')
        if record['id'] in historical and (record.get('historical_authority_digest') != identity(historical[record['id']])
                or record['permission'] != 'READ_ONLY' or record['evidence_level'] == 'LIVE'):
            reject(record['id'], 'historical prerequisite must bind its completed authority without live execution')
    for name, inputs in registry['families'].items():
        family = families[name]
        template = family.get('id_format')
        if template is None:
            allowed = set(family.get('records', []))
        else:
            allowed = set(expand_coordinates(template, inputs['dimensions']))
            if name == 'live_failure':
                if failure_contract is None:
                    reject(name, 'generated failure operation contract is absent')
                for axis, expected in [('injection',failure_contract['phase_live_injections']),
                                       ('operation',failure_contract['expand_over_operations']),
                                       ('record',family['base_records_per_coordinate']+family['requalification_records'])]:
                    if sorted(inputs['dimensions'].get(axis, [])) != sorted(expected):
                        reject(name, 'failure coordinate axis differs from its complete matrix population')
                omitted = failure_contract['requalification_after_recovery']['not_applicable_for']
                allowed = {key for key in allowed if not any(key.startswith('FAILURE-'+injection+'-')
                    and key.endswith(('-REQUALIFY_START','-REQUALIFY_VERIFY')) for injection in omitted)}
            for axis, source in generated['matrix_axes'].get(name, {}).items():
                source_rows = matrix[source]
                expected_values = list(source_rows) if isinstance(source_rows,dict) else [row['id'] for row in source_rows]
                if sorted(inputs['dimensions'].get(axis, [])) != sorted(expected_values):
                    reject(name, 'frozen coordinate axis omits or rewrites matrix membership')
            record_axis = inputs['dimensions'].get('record')
            required = next((value for key, value in family.items() if key.startswith('records_per_')), None)
            if record_axis is not None and required is not None and record_axis != required:
                reject(name, 'record dimension omits or rewrites required family records')
        if {record['id'] for record in inputs['records']} != allowed:
            reject(name, 'literal family records do not cover the full frozen coordinate expansion')
        expected_level = generated['materialized_record_contract']['family_evidence_levels'][name]
        for record in inputs['records']:
            if expected_level not in {'inherit_operation', 'inherit_target'} and record['evidence_level'] != expected_level:
                reject(record['id'], 'family evidence level differs from its authority')
            if family['owner_stage'].startswith('L') and record['owner_stage'] != family['owner_stage']:
                reject(record['id'], 'family stage owner differs from its authority')
        records.extend(inputs['records'])
    ids = {record['id'] for record in records}
    for record in registry.get('fixed_records', []):
        expected = fixed_authorities[record['id']].get('depends', [])
        if record['id'] in aggregates:
            expanded = []
            for dependency in expected:
                if dependency.startswith(('every-', 'every ')):
                    pattern = re.sub(r'<[^<>]+>', r'.+', re.escape(dependency[6:]))
                    matches = sorted(key for key in ids if re.fullmatch(pattern, key))
                    if not matches:
                        reject(record['id'], 'aggregate prerequisite expansion is empty')
                    expanded.extend(matches)
                else:
                    expanded.append(dependency)
            expected = sorted(set(expanded))
        if sorted(record['depends']) != sorted(expected):
            reject(record['id'], 'fixed record rewrites queue prerequisites')
    for name, inputs in registry['families'].items():
        family = families[name]
        template = family.get('id_format')
        fields = re.findall(r'<([^<>]+)>',template or '')
        bindings = {}
        if template:
            for coordinate in itertools.product(*(inputs['dimensions'][field] for field in fields)):
                values = dict(zip(fields,coordinate,strict=True))
                key = template
                for field,value in values.items(): key = key.replace('<'+field+'>',value)
                bindings[key] = values
        for record in inputs['records']:
            values = bindings.get(record['id'],{})
            suffix = values.get('record')
            if suffix is None:
                declared_records = next((value for key, value in family.items() if key.startswith('records_per_')), [])
                if len(declared_records) == 1:
                    suffix = declared_records[0]
            if name == 'live_failure':
                bound_operation = failure_binding(record, values, failure_contract, registry, records, parent)
            dependencies = family.get('dependencies',{})
            raw_dependencies = dependencies.get(suffix,[]) if isinstance(dependencies,dict) else dependencies
            if isinstance(raw_dependencies, dict):
                raw_dependencies = [*raw_dependencies['always'], *raw_dependencies.get('when_requalification_required', [])] if record.get('requalification_required') else raw_dependencies['always']
            expected = []
            for raw in raw_dependencies:
                if name == 'live_failure':
                    raw = {'literal-source-artifact-record-id':bound_operation['source_artifact_record_id'],
                           'literal-physical-qualification-record-id':bound_operation['physical_qualification_record_id']}.get(raw, raw)
                expanded = family.get('row_dependencies',{}).get(values.get('row'),[]) if raw == 'literal-row-dependencies' else [raw]
                if raw == 'literal-row-dependencies' and not expanded:
                    reject(record['id'], 'row prerequisite binding is missing')
                for dependency in expanded:
                    if dependency.startswith('matching-'):
                        target = dependency.removeprefix('matching-')
                        dependency = template.replace('<record>',target) if target in inputs.get('dimensions',{}).get('record',[]) else target
                    for field,value in values.items():
                        if field != 'record': dependency = dependency.replace('<'+field+'>',value)
                    if dependency.startswith('every-'):
                        pattern = re.escape(dependency.removeprefix('every-'))
                        pattern = re.sub(r'<[^<>]+>',r'.+',pattern)
                        matches = sorted(key for key in ids if re.fullmatch(pattern,key))
                        if not matches: reject(record['id'], 'aggregate prerequisite expansion is empty')
                        expected.extend(matches)
                    elif dependency in ids:
                        expected.append(dependency)
                    else:
                        bound = inputs.get('dependency_bindings',{}).get(dependency)
                        if not bound or not set(bound) <= ids:
                            reject(record['id'], f'prerequisite requires a frozen materializer binding: {dependency}')
                        expected.extend(bound)
            if sorted(record['depends']) != sorted(set(expected)):
                reject(record['id'], 'literal graph edges differ from declared family prerequisites')
    required, deferred = {}, {}
    for assertion in matrix_assertions(matrix):
        section = assertion.removeprefix('matrix#').split('.')[0]
        patterns = generated['assertion_owner_patterns'].get(section)
        if not patterns:
            reject(assertion, 'matrix assertion has no generated owner rule')
        owners, missing = [], []
        for pattern in patterns:
            matching = sorted(record['id'] for record in records if re.fullmatch(pattern,record['id']))
            if not matching:
                missing.append(pattern)
            owners.extend(matching)
        if missing:
            deferred[assertion] = missing
        if owners:
            required[assertion] = sorted(set(owners))
    if registry.get('deferred_assertion_owners', {}) != deferred:
        reject('materialization', 'every unresolved owner must retain its exact generated selector')
    if deferred and registry['materializer'] == 'Q80-MATERIALIZE':
        reject('materialization', 'Q80 requires complete matrix assertion ownership')
    if registry['required_owners'] != required:
        reject('materialization', 'registry owners differ from generated matrix ownership')
    records = copy.deepcopy(records)
    for record in records:
        if record['permission'] != 'READ_ONLY':
            card = registry.get('approved_cards', {}).get(record.get('approved_card_digest'))
            if card is None:
                reject(record['id'], 'approved card is absent from the frozen registry')
            record['approved_card'] = copy.deepcopy(card)
    return validate_graph(records, required_owners=required, parent=parent,
                          materializer=registry['materializer'], registry_digest=identity(registry),
                          deferred_owners=deferred)


def expand_coordinates(template, dimensions):
    """Q33: finite Cartesian expansion; unresolved or unused dimensions reject the input."""
    fields = set(re.findall(r'<([^<>]+)>', template))
    if fields != set(dimensions) or any(not values or len(set(values)) != len(values) for values in dimensions.values()):
        reject(template, 'coordinate dimensions are missing, duplicated or unused')
    keys = sorted(fields)
    result = []
    for values in itertools.product(*(dimensions[key] for key in keys)):
        record = template
        for key, value in zip(keys, values, strict=True):
            record = record.replace('<' + key + '>', str(value))
        if re.search(r'[<>*]', record) or record in result:
            reject(template, 'expansion is not literal and unique')
        result.append(record)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['seal', 'verify', 'inventory', 'identity', 'graph', 'contracts', 'materialize', 'capture', 'recover-capture'])
    parser.add_argument('path', type=Path)
    parser.add_argument('--record', type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text()) if args.record else {}
        if args.action == 'seal': result = seal_namespace(args.path, record)
        elif args.action == 'verify': result = {'digest': verify_namespace(args.path, record)}
        elif args.action == 'inventory': result = inventory_step(args.path, checkpoint=record or None)
        elif args.action == 'identity': result = collect_path_identity(args.path)
        elif args.action == 'graph': result = validate_graph(**json.loads(args.path.read_text()))
        elif args.action == 'materialize': result = materialize(args.path,record)
        elif args.action == 'capture': result = capture_attempt(CapacityCoordinator(args.path),**record)
        elif args.action == 'recover-capture': result = recover_capture(CapacityCoordinator(args.path),**record)
        else:
            queue, matrix = load_contracts(args.path)
            result = {'fixed_stages': [x['id'] for x in queue['fixed_steps']],
                      'families': [x['family'] for x in queue['expanded_session_families']],
                      'matrix_schema': matrix.get('schema_version')}
        print(json.dumps(result, sort_keys=True))
        return 0
    except CassetteError as error:
        print(json.dumps(error.payload(), sort_keys=True))
        return 1
    except (KeyError, ValueError, TypeError, OSError) as error:
        failure = CassetteError('INVALID_REQUEST',str(args.path),'Q6/Q80: campaign input','terminal',str(error))
        print(json.dumps(failure.payload(),sort_keys=True))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
