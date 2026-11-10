# test_live_stage_acceptance.py — sole L05 orchestration, raw replay and exact-input verdict (Q5/Q9/Q31/Q41/Q44/Q51/Q52/Q53/Q80); depends on broker.py, errors.py, sources.py, store.py, tools/campaign.py, tests/test_l05_acquire.py, tests/test_l05_credentials.py, tests/test_l05_drive.py, tests/test_l05_entry.py, tests/test_l05_ollama.py, tests/test_l05_package.py, tests/test_s10_transfer.py.
"""Keep the original L05 checks inside one stage verdict; live evidence remains compulsory."""

import asyncio
import ast
import copy
from dataclasses import replace
from fractions import Fraction
import fcntl
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import inspect
import json
import os
from pathlib import Path
import subprocess
import threading
import time

import pytest
import broker as broker_module

from broker import CanonicalBroker, _source_from, _source_record, _transfer_extent_id, _verify_partials
from sources import (Artifact, OperationGeometry, SourceAdapter, _load_state, _pread_exact, _retained_source_range,
                     transfer_header, transfer_state_bytes)
from store import (CapacityCoordinator, DriveSelection, DriveVolume, WriterContext,
                   artifact_hasher, campaign_head, canonical_bytes, digest_bytes, grant_transfer_extent,
                   verify_campaign_artifact)
from tools.campaign import (bind_action, identity, load_contracts, qualification_successions,
                            materialize, publish_graph)
from errors import CassetteError
import test_l05_acquire as acquisition_checks
import test_l05_credentials as credential_checks
import test_l05_drive as drive_checks
import test_l05_entry as entry_checks
import test_l05_ollama as source_checks
import test_l05_package as package_checks
import test_s10_transfer as transfer_checks


class _LiveL05:
    """Q5/Q31/Q44/Q51/Q80: the sole stage test owns every live CLI child and recovery."""

    def __init__(self, config, evidence):
        self.config, self.evidence, self.child = config, evidence, None
        self.cartridge = Path(config['cartridge'])
        self.sequence = max((int(path.name.partition('-')[0]) for path in evidence.iterdir()
                             if path.is_dir() and path.name.partition('-')[0].isdigit()), default=0)
        self.profiles = {}
        self.graph_digest = config['graph_digest']
        self.registry = json.loads(Path(config['registry']).read_bytes())
        self.head = campaign_head(Path(config['control']), 'graph')
        assert self.head['digest'] == config['graph_head']

    def publish(self):
        parent = self.head['value']['graph']
        graph = materialize(Path(__file__).resolve().parents[1], self.registry, parent=parent)
        assert all(graph['nodes'][key] == value for key, value in parent['nodes'].items())
        self.head = publish_graph(CapacityCoordinator(self.config['control']), graph, self.head['digest'])
        self.graph_digest = graph['revision_digest']
        self.save('graph-' + graph['revision_digest'].partition(':')[2] + '.json',
                  {'registry': self.registry, 'publication': self.head})

    def register_profile(self, plan):
        current_f4 = 'QUALIFY-' + self.config['f4_consumer'] + '-VERIFY'
        if plan['operation_id'] == self.config['f4_operation_id'] and current_f4 in self.head['value']['graph']['nodes']:
            assert plan['profile']['key'] == self.config['f4_profile_key']
            return
        alias = self.config['instance_aliases'].get(plan['instance'], plan['instance'])
        consumer = ('HEADER-' if plan['kind'] == 'header' else 'ACQ-') + alias
        if plan['instance'].startswith('ollama-generated'):
            consumer = 'OLLAMA-GEOMETRY' if 'geometry' in plan else 'OLLAMA'
        if plan['operation_id'] == self.config['f4_operation_id']:
            consumer = self.config['f4_consumer']
        start, verify = 'QUALIFY-' + consumer + '-START', 'QUALIFY-' + consumer + '-VERIFY'
        if start in self.head['value']['graph']['nodes']:
            return
        original = self.config['qualification_template_consumer']
        old_start, old_verify = 'QUALIFY-' + original + '-START', 'QUALIFY-' + original + '-VERIFY'
        local = {old_start, old_verify, 'CHECKPOINT-' + old_start + '-RECOVERABILITY',
                 'VERIFY-WORK-' + old_verify + '-START', 'VERIFY-WORK-' + old_verify + '-RESULT'}
        for family, axis, coordinate in (('physical_qualification', 'consumer-flat-id', consumer),
                ('checkpoint_proof', 'operation-start-flat-id', start),
                ('verification_work', 'target-flat-id', verify)):
            population = self.registry['families'][family]
            additions = [json.loads(json.dumps(row).replace(original, consumer))
                         for row in population['records'] if row['id'] in local]
            for row in additions:
                row.pop('prior_qualification', None)
            population['records'].extend(additions)
            population['dimensions'][axis].append(coordinate)
        arguments = self.profile_arguments(plan)
        request = {'consumer_flat_id': consumer, 'physical_disk_id': self.config['template']['disk']['physical_disk'],
            'apfs_volume_uuid': self.config['template']['disk']['apfs_volume_uuid'],
            'host_id': self.config['template']['host']['host_id'],
            'assembled_path_digest': identity(plan['profile']['binding']['path']), 'operation': 'acquire-qualification-only',
            'plan_digest': identity(plan['profile']['binding']['plan']), 'expected_read_write_shape': plan['profile']['patterns']}
        for family, record in (('physical_qualification', start),
                               ('checkpoint_proof', 'CHECKPOINT-' + start + '-RECOVERABILITY')):
            node = next(row for row in self.registry['families'][family]['records'] if row['id'] == record)
            template = {**self.config['template'], 'command': [self.config['python'], '-I', '-B', '-m', 'cli',
                '--state', self.config['state'], *arguments], 'cwd': str(self.evidence)}
            card = {**template, 'record_id': record, 'authorization_lineage': 'Drew: Complete L05 now; existing selected-root scope',
                'bound': {'profile_request': request, 'inputs_digest': identity(plan),
                          'runtime_receipt_sha256': self.config['runtime_receipt_sha256'],
                          'sole_test_sha256': self.config['test_sha256'],
                          'recovery_executor': 'sole L05 test owns the CLI Popen and proves the exact held boundary'}}
            node.update(permission=template['permission'], approved_card_digest=identity(card))
            self.registry['approved_cards'][identity(card)] = card
        node = next(row for row in self.registry['families']['physical_qualification']['records'] if row['id'] == verify)
        if plan['operation_id'] == self.config['f4_operation_id']:
            node['prior_qualification'] = old_verify
        for assertion in node['matrix_assertion_owners']:
            owners = self.registry['required_owners'][assertion]
            if plan['operation_id'] == self.config['f4_operation_id']:
                owners = [value for value in owners if value != old_verify]
            self.registry['required_owners'][assertion] = sorted({*owners, verify})
        self.publish()

    def profile_verify_id(self, plan):
        if plan['operation_id'] == self.config['f4_operation_id']:
            return 'QUALIFY-' + self.config['f4_consumer'] + '-VERIFY'
        alias = self.config['instance_aliases'].get(plan['instance'], plan['instance'])
        consumer = ('HEADER-' if plan['kind'] == 'header' else 'ACQ-') + alias
        if plan['instance'].startswith('ollama-generated'):
            consumer = 'OLLAMA-GEOMETRY' if 'geometry' in plan else 'OLLAMA'
        return 'QUALIFY-' + consumer + '-VERIFY'

    def register_precursor(self, acquisition, header):
        """Materialize the three original literal Qwen records under its approved fixed ordering."""
        prefix = 'ACQ-qwen3_30b_a3b'
        start, verify = prefix + '-START', prefix + '-VERIFY'
        checkpoint = 'CHECKPOINT-' + start + '-RECOVERABILITY'
        work_start, work_result = 'VERIFY-WORK-' + verify + '-START', 'VERIFY-WORK-' + verify + '-RESULT'
        header_id = 'HEADER-qwen3_30b_a3b-RUN'
        if header_id in self.head['value']['graph']['nodes']:
            added = False
            for record in (header_id, start, checkpoint):
                original = self.head['value']['graph']['nodes'][record]
                prior = original['approved_card']
                command = [self.config['python'], *prior['command'][1:]]
                if command == prior['command']:
                    continue
                identifier = 'EXECUTION-' + identity({'operation_record': record, 'command': command,
                    'runtime_receipt_sha256': self.config['runtime_receipt_sha256'],
                    'sole_test_sha256': self.config['test_sha256']}).partition(':')[2]
                if identifier in self.head['value']['graph']['nodes']:
                    continue
                card = {**prior, 'command': command, 'record_id': identifier, 'bound': {
                    **prior['bound'], 'prior_approved_card_digest': original['approved_card_digest'],
                    'runtime_receipt_sha256': self.config['runtime_receipt_sha256'],
                    'sole_test_sha256': self.config['test_sha256']}}
                self.registry['approved_cards'][identity(card)] = card
                binding = {key: original[key] for key in
                    ('depends', 'evidence_level', 'owner_stage', 'permission')}
                binding.update(id=identifier, operation_record=record, matrix_assertion_owners=[],
                    approved_card_digest=identity(card))
                self.registry.setdefault('execution_bindings', []).append(binding)
                added = True
            if added:
                self.publish()
            return
        common = {'evidence_level': 'LIVE', 'owner_stage': 'L05', 'permission': 'READ_ONLY', 'matrix_assertion_owners': []}
        header_arguments = ['headers', '--source-selection', header['source_selection'], '--drive-selection',
            self.config['drive_selection_id'], '--key', header['request']['idempotency_key'],
            *[item for path, count in sorted(header['header_json_bytes'].items())
              for item in ('--header-json-bytes', f'{path}={count}')]]
        acquisition_arguments = ['go', '--source-selection', acquisition['source_selection'], '--drive-selection',
            self.config['drive_selection_id'], '--key', acquisition['request']['idempotency_key']]
        for record, dependencies, arguments, plan in (
                (header_id, ['BASELINE-INPUTS-FROZEN', 'QUALIFY-HEADER-qwen3_30b_a3b-VERIFY'], header_arguments, header),
                (start, [header_id, 'QUALIFY-ACQ-qwen3_30b_a3b-VERIFY'], acquisition_arguments, acquisition),
                (checkpoint, [start], acquisition_arguments, acquisition)):
            node = {**common, 'id': record, 'depends': dependencies, 'permission': 'CAMPAIGN_DIRECTORY_WRITE'}
            template = {**self.config['template'], 'command': [self.config['python'], '-I', '-B', '-m', 'cli',
                '--state', self.config['state'], *arguments], 'cwd': str(self.evidence)}
            card = {**template, 'record_id': record, 'authorization_lineage': 'Drew approved the pinned Qwen precursor only',
                    'bound': {'inputs_digest': identity(plan), 'source_revision':
                        'ad44e777bcd18fa416d9da3bd8f70d33ebb85d39', 'sole_test_sha256': self.config['test_sha256']}}
            self.registry['approved_cards'][identity(card)] = card
            node['approved_card_digest'] = identity(card)
            if record == checkpoint:
                population = self.registry['families']['checkpoint_proof']
                population['records'].append(node)
                population['dimensions']['operation-start-flat-id'].append(start)
            else:
                self.registry['fixed_records'].append(node)
        assertions = [key for key in self.config['matrix_assertions']
                      if key.startswith('matrix#source_rows[id=source_huggingface_all_immutable_models].')]
        self.registry['fixed_records'].append({**common, 'id': verify,
            'depends': [start, checkpoint, work_result], 'matrix_assertion_owners': assertions})
        population = self.registry['families']['verification_work']
        population['dimensions']['target-flat-id'].append(verify)
        population['records'].extend([{**common, 'id': work_start, 'depends': [start, checkpoint]},
                                      {**common, 'id': work_result, 'depends': [work_start]}])
        for assertion in assertions:
            self.registry['required_owners'][assertion] = [verify]
            self.registry['deferred_assertion_owners'].pop(assertion, None)
        self.publish()

    def source_entry(self):
        """Q41/Q42/Q80: close the original group only after all exact source profiles pass."""
        queue, _ = load_contracts(Path(__file__).resolve().parents[1])
        records = {row['id']: row for row in queue['operation_records']}
        required = records['SOURCE-PROFILES-ALL-PASS']['depends']
        assert set(self.profiles) == set(required)
        for plan in self.config['plans']:
            record = self.record(plan['operation_id'])
            if plan['instance'] != 'qwen3_30b_a3b':
                assert record['phase'] == 'EMPTY'
                assert not any('source_headers' in event['payload'] for event in record['events'])
        owner = CanonicalBroker(Path(self.config['state']) / 'operations')
        try:
            destination = owner._load(self.config['drive_selection_id'])['result']
            selection = DriveSelection(DriveVolume(**destination['selection']['volume']),
                                       WriterContext(**destination['selection']['writer']))
            observed = asyncio.run(owner._protected_inventory(selection, destination['folder']))
        finally:
            owner.close()
        for name in ('SOURCE-PROFILES-ALL-PASS', 'SOURCE-ENTRY-PASS'):
            self.registry['fixed_records'].append({'id': name, 'depends': records[name]['depends'],
                'evidence_level': 'LIVE', 'matrix_assertion_owners': [], 'owner_stage': 'L05', 'permission': 'READ_ONLY'})
        self.publish()
        self.save('source-entry.json', {'status': 'PASS', 'profiles': self.profiles,
            'inventory_digest': digest_bytes(canonical_bytes(observed)), 'graph_digest': self.graph_digest,
            'protected_inventory': observed, 'selected_inventory_digest': destination['inventory_digest'],
            'shared_drive_changed': observed != destination['protected_inventory'],
            'precursor_exception': 'Only the exact pinned Qwen3-30B-A3B required source read headers/payload earlier'})

    def register_consumers(self, ollama):
        """Freeze all remaining original consumers after their complete source group exists."""
        common = {'evidence_level': 'LIVE', 'owner_stage': 'L05', 'permission': 'READ_ONLY', 'matrix_assertion_owners': []}
        headers = [plan for plan in self.config['plans'] if plan['kind'] == 'header'
                   and plan['instance'] != 'qwen3_30b_a3b']
        model_names = {plan['instance'] for plan in headers}
        acquisitions = [plan for plan in self.config['plans'] if plan['kind'] == 'acquisition'
                        and plan['instance'] != 'qwen3_30b_a3b']
        alias = lambda plan: self.config['instance_aliases'].get(plan['instance'], plan['instance'])
        self.registry['families']['source_header'] = {'dimensions': {'instance': [alias(plan) for plan in headers]}, 'records': []}
        self.registry['families']['acquisition'] = {'dimensions': {'instance': [alias(plan) for plan in acquisitions
            if plan['instance'] in model_names], 'record': ['START', 'VERIFY']}, 'records': [],
            'dependency_bindings': {'QUALIFY-ACQ-F4-VERIFY': ['QUALIFY-' + self.config['f4_consumer'] + '-VERIFY']}}
        self.registry['families']['ollama_source'] = {'dimensions': {'record': ['START', 'VERIFY']}, 'records': []}
        def card(node, arguments, plan):
            template = {**self.config['template'], 'command': [self.config['python'], '-I', '-B', '-m', 'cli',
                '--state', self.config['state'], *arguments], 'cwd': str(self.evidence)}
            value = {**template, 'record_id': node['id'], 'authorization_lineage': 'Drew: Complete L05 now; original frozen inputs',
                     'bound': {'inputs_digest': identity(plan), 'sole_test_sha256': self.config['test_sha256']}}
            self.registry['approved_cards'][identity(value)] = value
            node.update(permission=template['permission'], approved_card_digest=identity(value))
        for plan in headers:
            name = alias(plan)
            node = {**common, 'id': 'HEADER-' + name + '-RUN', 'depends': ['SOURCE-ENTRY-PASS',
                'BASELINE-INPUTS-FROZEN', self.profile_verify_id(plan)]}
            arguments = ['headers', '--source-selection', plan['source_selection'], '--drive-selection',
                self.config['drive_selection_id'], '--key', plan['request']['idempotency_key'],
                *[item for path, count in sorted(plan['header_json_bytes'].items())
                  for item in ('--header-json-bytes', f'{path}={count}')]]
            card(node, arguments, plan)
            self.registry['families']['source_header']['records'].append(node)
        self.registry['fixed_records'].append({**common, 'id': 'HEADERS-ALL-PASS', 'depends': sorted([
            'HEADER-qwen3_30b_a3b-RUN', *['HEADER-' + alias(plan) + '-RUN' for plan in headers]])})
        for plan in [*acquisitions, ollama]:
            name = 'OLLAMA' if plan is ollama else 'ACQ-' + alias(plan)
            start, verify = name + '-START', name + '-VERIFY'
            checkpoint = 'CHECKPOINT-' + start + '-RECOVERABILITY'
            work_start, work_result = 'VERIFY-WORK-' + verify + '-START', 'VERIFY-WORK-' + verify + '-RESULT'
            dependencies = (['ACQ-qwen3_30b_a3b-VERIFY', self.profile_verify_id(plan)] if plan is ollama else
                ['SOURCE-ENTRY-PASS', self.profile_verify_id(plan)] +
                (['HEADER-' + alias(plan) + '-RUN'] if plan['instance'] in model_names else []))
            start_node = {**common, 'id': start, 'depends': dependencies}
            checkpoint_node = {**common, 'id': checkpoint, 'depends': [start]}
            arguments = ['go', '--source-selection', plan['source_selection'], '--drive-selection',
                         self.config['drive_selection_id'], '--key', plan['request']['idempotency_key']]
            card(start_node, arguments, plan)
            card(checkpoint_node, arguments, plan)
            assertions = [key for key in self.config['matrix_assertions'] if key.startswith(
                'matrix#source_rows[id=' + ('source_ollama_content_addressed_reimport' if plan is ollama else
                'source_huggingface_all_immutable_models') + '].')] if (plan is ollama or
                plan['instance'] in {'kimi_k3', 'qwen3_235b_a22b'}) else []
            verify_node = {**common, 'id': verify, 'depends': [start, checkpoint, work_result],
                           'matrix_assertion_owners': assertions}
            population = (self.registry['families']['ollama_source']['records'] if plan is ollama else
                self.registry['families']['acquisition']['records'] if plan['instance'] in model_names else
                self.registry['fixed_records'])
            population.extend([start_node, verify_node])
            self.registry['families']['checkpoint_proof']['dimensions']['operation-start-flat-id'].append(start)
            self.registry['families']['checkpoint_proof']['records'].append(checkpoint_node)
            self.registry['families']['verification_work']['dimensions']['target-flat-id'].append(verify)
            self.registry['families']['verification_work']['records'].extend([
                {**common, 'id': work_start, 'depends': [start, checkpoint]},
                {**common, 'id': work_result, 'depends': [work_start]}])
            for assertion in assertions:
                self.registry['required_owners'][assertion] = sorted({*self.registry['required_owners'].get(assertion, []), verify})
                self.registry['deferred_assertion_owners'].pop(assertion, None)
        self.publish()

    def record(self, operation):
        raw = (Path(self.config['state']) / 'operations' / (operation + '.json')).read_bytes()
        envelope = json.loads(raw)
        assert canonical_bytes(envelope) == raw
        assert digest_bytes(canonical_bytes(envelope['record'])) == envelope['digest']
        assert envelope['record']['operation_id'] == operation
        return envelope['record']

    def save(self, name, value):
        path, raw = self.evidence / name, canonical_bytes(value)
        if path.exists():
            assert path.read_bytes() == raw, 'Q80 resumed evidence differs: ' + name
            return
        with path.open('xb') as stream:
            stream.write(raw)

    def space(self):
        disk = os.statvfs('/System/Volumes/Data')
        assert disk.f_bavail * 10 >= disk.f_blocks, 'Q53 system-volume free space below10percent'

    def launch(self, label, arguments):
        assert self.child is None
        self.space()
        self.sequence += 1
        directory = self.evidence / f'{self.sequence:03d}-{label}'
        directory.mkdir()
        self.directory = directory
        command = [self.config['python'], '-I', '-B', '-m', 'cli', '--state', self.config['state'], *arguments]
        template = {**self.config['template'], 'command': command, 'cwd': str(self.evidence)}
        if arguments[0] in {'connect', 'models', 'select-model', 'select-dataset', 'select-drive'}:
            template['permission'] = 'READ_ONLY'
        cards = [node['approved_card'] for node in self.head['value']['graph']['nodes'].values()
                 if node.get('approved_card', {}).get('command') == command]
        if arguments[0] in {'go', 'qualify', 'headers'}:
            assert any(all(card.get(key) == value for key, value in template.items()) for card in cards), \
                'Q80 product I/O lacks its exact current graph card'
        binding = bind_action(template, identity(template), {'stage_inputs_digest': self.config['digest'],
                              'graph_cards': [identity(card) for card in cards]},
                              self.graph_digest)
        (directory / 'binding.json').write_bytes(canonical_bytes(binding))
        with (directory / 'stdout').open('xb') as stdout, (directory / 'stderr').open('xb') as stderr:
            self.child = subprocess.Popen(command, cwd=self.evidence, stdout=stdout, stderr=stderr,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', CASSETTE_EXECUTION_BINDING=canonical_bytes(binding).decode()))
        launch = {'command': command, 'parent_pid': os.getpid(), 'cli_pid': self.child.pid,
                  'binding_digest': binding['digest'], 'status': 'RUNNING'}
        (directory / 'launch.json').write_bytes(canonical_bytes(launch))
        print('L05 live: ' + label, flush=True)
        return directory

    def wait(self, directory, predicate=None):
        try:
            while self.child.poll() is None:
                self.space()
                if predicate is not None and predicate():
                    return
                time.sleep(.25)
            assert predicate is None, (directory, 'CLI ended before its declared durable boundary')
        except BaseException:
            self.stop(directory)
            raise

    def stop(self, directory):
        child = self.child
        assert child is not None
        if child.poll() is None:
            child.kill()
        code = child.wait(timeout=30)
        self.child = None
        (directory / 'exit.json').write_bytes(canonical_bytes({'exit_code': code,
            'own_direct_child': True, 'raw_sha256': {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                                                   for name in ('stdout', 'stderr')}}))
        return code

    def run(self, label, arguments, expected_code):
        directory = self.launch(label, arguments)
        self.wait(directory)
        code = self.stop(directory)
        assert code == expected_code, (directory, code, (directory / 'stderr').read_text()[-4000:])
        result = json.loads((directory / 'stdout').read_bytes())
        if 'operation_id' in result:
            record = self.record(result['operation_id'])
            assert all(key in record and record[key] == value for key, value in result.items()), \
                'Q80 CLI projection differs from its canonical operation'
            return record
        return result

    def arm(self, request, boundary):
        owner = CanonicalBroker(Path(self.config['state']) / 'operations')
        try:
            record = owner.issue(request)
            assert record['state'] not in {'FAILED', 'CANCELLED', 'SUCCEEDED'}
            if record['state'] == 'PAUSED':
                owner.resume(record['operation_id'])
            owner.request_hold(record['operation_id'], boundary)
        finally:
            owner.close()

    def release(self, operation, boundary):
        assert self.child is None
        owner = CanonicalBroker(Path(self.config['state']) / 'operations')
        try:
            owner.release_hold(operation, boundary)
        finally:
            owner.close()

    def profile_checkpoint(self, plan):
        head = campaign_head(self.cartridge, plan['profile']['key'])
        assert head['value']['binding'] == plan['profile']['binding']
        extents = campaign_head(self.cartridge, plan['profile']['key'] + '-0-extents')
        assert extents['value']['status'] == 'RETAINED'
        if 'geometry' in plan:
            artifact = OperationGeometry(plan['geometry']).artifacts[0]
        else:
            source = _source_from(self.record(plan['source_selection'])['result']['source_lock'], plan['source_selection'])
            artifact = sorted((*source.artifacts, *source.metadata_assets), key=lambda item: item.path)[0]
            if plan['header_json_bytes'] is not None:
                artifact = source.artifacts[0]
        assert extents['value']['binding'] == {'profile_digest': head['digest'], 'artifact': artifact.record()}
        key = 'source-' + extents['digest'].partition(':')[2] + '-capture'
        capture = campaign_head(self.cartridge, key)
        assert capture['value']['status'] == 'CHECKPOINTED'
        assert capture['value']['operation_id'] == plan['operation_id']
        assert capture['value']['extent_operation'] == extents['value']['operation_id']
        assert capture['value']['path'] == plan['profile']['binding']['path']
        for trace in capture['value']['checkpoint']['traces']:
            verify_campaign_artifact(self.cartridge, trace['attempt'], trace['name'], trace['digest'],
                                     trace['bytes'], maximum_bytes=2097152)
        return {'key': key, 'capture': capture, 'extents': extents, 'plan': head}

    def verify_profile(self, plan):
        assert self.child is None
        proof = json.loads((self.evidence / (plan['instance'] + '-' + plan['kind'] + '-checkpoint-proof.json')).read_bytes())
        assert proof['status'] == 'PASS_LIVE_CHECKPOINT_ONLY' and proof['operation_id'] == plan['operation_id']
        assert proof['before'] == proof['after'] and proof['owned_exits'] == [-9, -9]
        assert proof['before']['plan']['value']['binding'] == plan['profile']['binding']
        for trace in proof['before']['capture']['value']['checkpoint']['traces']:
            verify_campaign_artifact(self.cartridge, trace['attempt'], trace['name'], trace['digest'],
                                     trace['bytes'], maximum_bytes=2097152)
        owner = CanonicalBroker(Path(self.config['state']) / 'operations')
        try:
            destination = owner._load(self.config['drive_selection_id'])['result']
            selection = DriveSelection(DriveVolume(**destination['selection']['volume']),
                                       WriterContext(**destination['selection']['writer']))
            source = (OperationGeometry(plan['geometry']) if 'geometry' in plan else
                      _source_from(owner._load(plan['source_selection'])['result']['source_lock'], plan['source_selection']))
            result = asyncio.run(owner._qualify_download(plan['operation_id'], CapacityCoordinator(self.cartridge),
                selection, source, header_lengths=plan['header_json_bytes'], require_existing=True))
            assert result['status'] == 'PASS'
            assert any(event['payload'].get('source_qualification') == result
                       for event in owner._load(plan['operation_id'])['events'])
            self.save(plan['instance'] + '-' + plan['kind'] + '-profile-replay.json', result)
            self.profiles[self.profile_verify_id(plan)] = {'operation_id': plan['operation_id'],
                'binding_digest': identity(plan['profile']['binding']), 'result': result}
        finally:
            owner.close()

    def profile(self, plan):
        self.register_profile(plan)
        operation = plan['operation_id']
        complete = campaign_head(self.cartridge, plan['profile']['key'] + '-complete')
        if complete is not None:
            assert complete['value']['measurements']['status'] == 'PASS'
            self.verify_profile(plan)
            return
        arguments = self.profile_arguments(plan)
        label = plan['instance'] + '-' + plan['kind']
        self.arm(plan['request'], 'profile-checkpoint')
        first = self.launch(label + '-start', arguments)
        self.wait(first, lambda: [event['payload'] for event in self.record(operation)['events']
            if 'hold' in event['payload']][-1] == {'hold': 'ACKNOWLEDGED', 'boundary': 'profile-checkpoint'})
        before = self.profile_checkpoint(plan)
        self.save(label + '-before.json', before)
        assert self.stop(first) == -9
        count = len(self.record(operation)['events'])
        held = self.launch(label + '-held-resume', arguments)
        self.wait(held, lambda: any('source_profile_resume' in event['payload']
                                  for event in self.record(operation)['events'][count:]))
        after = self.profile_checkpoint(plan)
        assert after == before, 'Q60 held restart changed its exact profile boundary'
        assert self.stop(held) == -9
        self.release(operation, 'profile-checkpoint')
        self.save(label + '-checkpoint-proof.json', {'status': 'PASS_LIVE_CHECKPOINT_ONLY',
            'before': before, 'after': after, 'operation_id': operation, 'owned_exits': [-9, -9]})
        result = self.run(label + '-continued', arguments, 2)
        assert result['state'] == 'PAUSED' and result['error'] is None
        assert campaign_head(self.cartridge, plan['profile']['key'] + '-complete')['value']['measurements']['status'] == 'PASS'
        self.verify_profile(plan)

    def profile_arguments(self, plan):
        selected = ['--operation-plan', plan['geometry_path']] if 'geometry' in plan else ['--source-selection', plan['source_selection']]
        arguments = ['qualify', *selected,
            '--drive-selection', self.config['drive_selection_id'], '--key', plan['request']['idempotency_key']]
        if plan['header_json_bytes'] is not None:
            arguments += ['--headers', *[item for path, count in sorted(plan['header_json_bytes'].items())
                                        for item in ('--header-json-bytes', f'{path}={count}')]]
        return arguments

    def headers(self, plan):
        declarations = [item for path, count in sorted(plan['header_json_bytes'].items())
                        for item in ('--header-json-bytes', f'{path}={count}')]
        result = self.run(plan['instance'] + '-headers', ['headers', '--source-selection', plan['source_selection'],
            '--drive-selection', self.config['drive_selection_id'], '--key', plan['request']['idempotency_key'],
            *declarations], 2)
        assert result['state'] == 'PAUSED' and result['error'] is None
        assert any('source_headers' in event['payload'] for event in self.record(result['operation_id'])['events'])

    def source_checkpoint(self, plan):
        source = _source_from(self.record(plan['source_selection'])['result']['source_lock'], plan['source_selection'])
        artifact = sorted((*source.artifacts, *source.metadata_assets), key=lambda item: item.path)[0]
        extents = {}
        try:
            for role, size in (('data', artifact.size), ('state', transfer_state_bytes(artifact.size))):
                extents[role] = grant_transfer_extent(self.cartridge, plan['operation_id'],
                    _transfer_extent_id(plan['operation_id'], artifact.path, role), size,
                    capacity_controller=CapacityCoordinator(self.cartridge), require_existing=True)
            header, chunks = _load_state(extents['state'], artifact.path, None, plan['operation_id'], read_only=True)
            offset = header['contiguous_source_hash_offset']
            assert offset > 0
            payload = _pread_exact(extents['data'], 0, offset, artifact.path)
            assert [digest_bytes(payload[index:index + 4194304]) for index in range(0, offset, 4194304)] == list(chunks)
            return {'artifact': artifact.path, 'source_lock': _source_record(source), 'header': header,
                    'chunks': list(chunks), 'bytes_digest': digest_bytes(payload), 'offset': offset,
                    'extent_identity': {role: [os.fstat(extent.fd).st_dev, os.fstat(extent.fd).st_ino,
                                             extent.offset, extent.length] for role, extent in extents.items()}}
        finally:
            for extent in extents.values():
                os.close(extent.fd)

    def acquire(self, plan):
        operation = plan['operation_id']
        if self.record(operation)['state'] == 'SUCCEEDED':
            assert self.record(operation)['phase'] == 'SOURCE_VERIFIED'
            return operation
        arguments = ['go', '--source-selection', plan['source_selection'],
            '--drive-selection', self.config['drive_selection_id'], '--key', plan['request']['idempotency_key']]
        label = plan['instance'] + '-payload'
        self.arm(plan['request'], 'source-checkpoint')
        first = self.launch(label + '-start', arguments)
        self.wait(first, lambda: [event['payload'] for event in self.record(operation)['events']
            if 'hold' in event['payload']][-1] == {'hold': 'ACKNOWLEDGED', 'boundary': 'source-checkpoint'})
        before = self.source_checkpoint(plan)
        assert self.stop(first) == -9
        held = self.launch(label + '-held-resume', arguments)
        marker = (f"{before['artifact']}: received {before['offset']} bytes; "
                  f"readback verified {before['offset']} bytes; checkpoint saved.")
        self.wait(held, lambda: marker in (held / 'stderr').read_text())
        after = self.source_checkpoint(plan)
        assert before == after, 'Q51/Q60 held restart changed verified source bytes or checkpoints'
        assert self.stop(held) == -9
        self.release(operation, 'source-checkpoint')
        self.save(label + '-checkpoint-proof.json', {'status': 'PASS_LIVE_CHECKPOINT_ONLY',
            'before': before, 'after': after, 'operation_id': operation, 'owned_exits': [-9, -9], 'fresh_marker': marker})
        result = self.run(label + '-continued', arguments, 0)
        assert result['phase'] == 'SOURCE_VERIFIED' and result['state'] == 'SUCCEEDED' and result['error'] is None
        return operation


def _bind_profile(live, instance, selected, key, *, geometry=None, header_lengths=None):
    """Q33/Q42: reuse the installed qualifier's read-only prefix for an exact current plan."""
    destination = live.record(live.config['drive_selection_id'])['result']
    selection = DriveSelection(DriveVolume(**destination['selection']['volume']),
                               WriterContext(**destination['selection']['writer']))
    arguments = {'acquisition': {'drive_selection_id': live.config['drive_selection_id']}}
    if geometry is None:
        arguments['acquisition']['model_selection_id'] = selected['operation_id']
        arguments['source'] = selected['result']['descriptor']
        revision = _source_from(selected['result']['source_lock'], selected['operation_id'])
    else:
        arguments['acquisition']['operation_geometry'] = geometry
        revision = OperationGeometry(geometry)
    request = {'protocol_version': '1', 'idempotency_key': key, 'operation': 'acquire',
               'target': live.config['drive_selection_id'], 'arguments': arguments}
    operation = CanonicalBroker.operation_id(request)
    module = ast.parse(Path(broker_module.__file__).read_bytes())
    cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == 'CanonicalBroker')
    method = copy.deepcopy(next(node for node in cls.body if isinstance(node, ast.AsyncFunctionDef)
                                and node.name == '_qualify_download'))
    cut = next(index for index, node in enumerate(method.body) if isinstance(node, ast.Assign)
               and any(isinstance(target, ast.Name) and target.id == 'key' for target in node.targets))
    method.name, method.decorator_list = '_metadata_binding', []
    method.body = method.body[:cut + 1] + ast.parse('return {"binding": binding, "patterns": patterns, "key": key}').body
    namespace = dict(broker_module.__dict__)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 'installed-qualifier:metadata-prefix', 'exec'), namespace)
    profile = asyncio.run(namespace['_metadata_binding'](None, operation, None, selection, revision,
                                                         header_lengths=header_lengths))
    plan = {'instance': instance, 'kind': 'header' if header_lengths is not None else 'acquisition',
            'request': request, 'operation_id': operation, 'profile': profile,
            'header_json_bytes': header_lengths, 'source_selection': None if selected is None else selected['operation_id']}
    if geometry is not None:
        plan.update(geometry=geometry, geometry_path=str(live.evidence / (instance + '-geometry.json')))
        Path(plan['geometry_path']).write_bytes(canonical_bytes(geometry))
    live.save(instance + '-' + plan['kind'] + '-binding.json', plan)
    return plan


def _verify_acquired_bytes(record, source, cartridge):
    """Q51/Q60/Q80: recompute final source and chunk digests from existing store-granted bytes."""
    operation = record['operation_id']
    capacity = CapacityCoordinator(cartridge)
    partials = {item['path']: item for item in record['checkpoint']['partials']}
    external_paths = []
    for artifact in sorted((*source.artifacts, *source.metadata_assets), key=lambda item: item.path):
        extents = {}
        try:
            for role, size in (('data', artifact.size), ('state', transfer_state_bytes(artifact.size))):
                extents[role] = grant_transfer_extent(cartridge, operation,
                    _transfer_extent_id(operation, artifact.path, role), size,
                    capacity_controller=capacity, require_existing=True)
                native_path = fcntl.fcntl(extents[role].fd, 50, bytes(1024)).split(b'\0', 1)[0]  # macOS F_GETPATH
                actual_path = Path(os.fsdecode(native_path)).resolve(strict=True)
                assert actual_path.is_relative_to(cartridge.resolve(strict=True)), 'Q51 source extent escaped the selected cartridge'
                assert os.fstat(extents[role].fd).st_dev == cartridge.stat().st_dev
                external_paths.append(str(actual_path))
            proof = partials[artifact.path]['chunk_digests']
            manifest = proof['digest'] if isinstance(proof, dict) else digest_bytes(canonical_bytes(proof))
            _retained_source_range(source, artifact, extents, 0, 0, manifest)
            _, chunks = _load_state(extents['state'], artifact.path, None, 'l05-proof', read_only=True)
            hasher = artifact_hasher(artifact.digest, artifact.path, object_size=artifact.size)
            offset = 0
            for expected in chunks:
                payload = _pread_exact(extents['data'], offset, min(4194304, artifact.size - offset), artifact.path)
                assert digest_bytes(payload) == expected, 'Q51 acquired chunk changed: ' + artifact.path
                hasher.update(payload)
                offset += len(payload)
            assert offset == artifact.size
            assert artifact.digest == artifact.digest.partition(':')[0] + ':' + hasher.hexdigest(), \
                'Q51 final acquired source digest differs: ' + artifact.path
        finally:
            for extent in extents.values():
                os.close(extent.fd)
    return {'operation_id': operation, 'source_lock_digest': identity(record['checkpoint']['source_lock']),
            'verified_bytes': sum(item.size for item in (*source.artifacts, *source.metadata_assets)),
            'artifacts': [{'path': item.path, 'size': item.size, 'digest': item.digest}
                          for item in (*source.artifacts, *source.metadata_assets)],
            'verified_external_extent_paths': external_paths}


def _verify_model_headers(owner, records, source, drive):
    """Q42/Q50/Q80: replay each model's exact header profile and parse its retained header bytes."""
    source_digest = digest_bytes(canonical_bytes(_source_record(source)))
    cartridge = Path(drive['root'])
    matches = []
    for record in records:
        destinations = [event['payload']['drive_prepared'] for event in record['events']
                        if 'drive_prepared' in event['payload']]
        if len(destinations) != 1 or Path(destinations[0]['root']) != cartridge:
            continue
        for event in record['events']:
            summary = event['payload'].get('source_headers')
            if summary is None:
                continue
            head = campaign_head(cartridge, summary['metadata_record_key'])
            assert head is not None and head['digest'] == summary['metadata_record_digest']
            if head['value']['source_lock_digest'] == source_digest:
                matches.append((record, summary, head['value']))
    assert matches, 'Q50 required parsed headers are absent: ' + source.locator
    record, summary, value = matches[-1]
    assert summary['status'] == 'PARSED' and value['operation_id'] == record['operation_id']
    assert summary['artifacts'] == value['artifacts']
    assert {item['path'] for item in summary['artifacts']} == {item.path for item in source.artifacts}
    parsed = {}
    lengths = {}
    for item in summary['artifacts']:
        head = campaign_head(cartridge, item['header_record_key'])
        assert head is not None and head['digest'] == item['header_record_digest']
        assert head['value']['binding']['source_lock_digest'] == source_digest
        assert head['value']['binding']['operation_id'] == record['operation_id']
        parsed[item['path']] = head['value']['parsed']
        lengths[item['path']] = head['value']['binding']['header_json_bytes']
        assert parsed[item['path']]['header_digest'] == item['header_digest']
        assert parsed[item['path']]['header_bytes'] == item['header_bytes'] == lengths[item['path']] + 8
    capacity = CapacityCoordinator(cartridge)
    selection = DriveSelection(DriveVolume(**drive['selection']['volume']),
                               WriterContext(**drive['selection']['writer']))
    profile = asyncio.run(owner._qualify_download(record['operation_id'], capacity, selection,
        source, header_lengths=lengths, require_existing=True))
    assert profile['status'] == 'PASS'
    assert any(event['payload'].get('source_qualification') == profile for event in record['events'])
    assert value['physical_profile_digest'] == profile['profile_digest']
    adapter = SourceAdapter(source.source_kind, 'https://huggingface.co')
    for artifact in source.artifacts:
        extent = grant_transfer_extent(cartridge, record['operation_id'],
            _transfer_extent_id(record['operation_id'], artifact.path, 'header'), artifact.size,
            capacity_controller=capacity, require_existing=True)
        try:
            replay = asyncio.run(transfer_header(adapter, source, artifact, extent, capacity,
                expected_header_json_bytes=lengths[artifact.path],
                expected_header_digest=parsed[artifact.path]['header_digest']))
            assert replay == parsed[artifact.path], 'Q50 retained header parser result changed: ' + artifact.path
        finally:
            os.close(extent.fd)


def _ollama_recipe(live, original, header_operation):
    """Q9/Q50/Q51: derive the frozen native byte recipe from actual verified HF headers."""
    source = _source_from(original['checkpoint']['source_lock'], original['operation_id'])
    metadata = next(event['payload']['source_headers'] for event in live.record(header_operation)['events']
                    if 'source_headers' in event['payload'])
    tensors = {}
    for item in metadata['artifacts']:
        parsed = campaign_head(live.cartridge, item['header_record_key'])['value']['parsed']['inventory']
        for tensor in parsed['tensors']:
            name = tensor['semantic_tensor_id']
            assert name not in tensors
            tensors[name] = {**tensor, 'path': item['path'], 'offset': parsed['data_start'] + tensor['offset']}
    layout = json.loads(Path(live.config['ollama_layout']).read_bytes())
    predicted = json.loads(Path(live.config['ollama_config']).read_bytes())
    declared = json.loads(Path(live.config['ollama_plan']).read_bytes())
    artifacts, used = [], set()
    for blob in layout['blobs']:
        fields, segments = {}, []
        for output in sorted(blob['tensors'], key=lambda item: item['name']):
            fields[output['name']] = {'dtype': output['dtype'], 'shape': output['shape'],
                                      'data_offsets': output['output_data_offsets']}
            count = 0
            for name in output['source_names']:
                item = tensors[name]
                assert item['dtype'] == output['dtype'] and name not in used
                assert item['shape'] == (output['shape'] if len(output['source_names']) == 1 else output['shape'][1:])
                used.add(name)
                count += item['length']
                segments.append({'path': item['path'], 'offset': item['offset'], 'length': item['length']})
            assert count == output['bytes']
        header = json.dumps(fields, ensure_ascii=False, separators=(',', ':')).encode()
        assert len(header) == blob['header_json_bytes']
        header += b' ' * (-len(header) % 8)
        assert len(header) == blob['header_padded_bytes']
        prefix = len(header).to_bytes(8, 'little') + header
        artifacts.append({'path': blob['name'] + '.safetensors',
                          'segments': [{'literal_hex': prefix.hex()}, *segments]})
    assert used == set(tensors), 'Q50 generated Ollama recipe omits or duplicates a semantic tensor'
    assets = {item.path: item for item in source.metadata_assets}
    for path in sorted(name for name in assets if name.endswith('.json') and name != 'model.safetensors.index.json'):
        artifacts.append({'path': path, 'segments': [{'path': path, 'offset': 0, 'length': assets[path].size}]})
    license_row = next(item for item in declared['artifacts'] if item['role'] == 'LICENSE')
    artifacts.append({'path': license_row['path'], 'segments': [{'path': 'LICENSE', 'offset': 0,
                                                              'length': assets['LICENSE'].size}]})
    config = predicted['derived_config_v2']['encoded_utf8'].encode()
    assert len(config) == predicted['derived_config_v2']['utf8_bytes']
    artifacts.append({'path': 'ollama-config.json', 'segments': [{'literal_hex': config.hex()}]})
    artifacts.sort(key=lambda item: item['path'])
    expected = {item['path']: item['bytes'] for item in declared['artifacts']}
    actual = {item['path']: sum(len(segment['literal_hex']) // 2 if 'literal_hex' in segment else segment['length']
                               for segment in item['segments']) for item in artifacts}
    assert actual == expected
    recipe = {'source_record_digest': digest_bytes(canonical_bytes(source.record())), 'artifacts': artifacts}
    live.save('ollama-semantic-mapping.json', {'source_operation': original['operation_id'],
        'source_lock_digest': digest_bytes(canonical_bytes(original['checkpoint']['source_lock'])),
        'source_tensor_count': len(tensors), 'mapped_tensor_count': len(used),
        'recipe_digest': digest_bytes(canonical_bytes(recipe)), 'artifacts': actual})
    live.save('ollama-recipe.json', recipe)
    return recipe


def _ollama_reimport(live, precursor, header_operation):
    """Q9/Q42/Q51/Q52: serve actual store-owned generated bytes through the native registry wire."""
    original = live.record(precursor)
    recipe = _ollama_recipe(live, original, header_operation)
    composed = live.run('ollama-compose', ['qualify-composition', '--acquisition', precursor,
        '--recipe', str(live.evidence / 'ollama-recipe.json'), '--key', live.config['ollama_composition_key']], 0)
    assert composed['operation']['state'] == 'SUCCEEDED' and composed['source_qualification']['status'] == 'PASS'
    operation = composed['operation']['operation_id']
    ownership = campaign_head(live.cartridge, 'source-compose-' + operation.removeprefix('op-'))
    outputs = ownership['value']['outputs']
    declared = json.loads(Path(live.config['ollama_plan']).read_bytes())
    expected = {item['path']: item for item in declared['artifacts']}
    assert {item['path'] for item in outputs} == set(expected)
    for item in outputs:
        assert item['size'] == expected[item['path']]['bytes']
        if expected[item['path']]['known_digest'] is not None:
            assert item['digest'] == expected[item['path']]['known_digest']
    by_path = {item['path']: item for item in outputs}
    manifests = {}
    for item in outputs:
        key = 'source-compose-output-' + identity({'operation_id': operation, 'path': item['path']}).partition(':')[2]
        proof = campaign_head(live.cartridge, key)['value']
        assert proof['ownership_digest'] == ownership['digest'] and proof['output'] == item
        chunks = proof['partial']['chunk_digests']
        manifests[item['path']] = chunks['digest'] if isinstance(chunks, dict) else identity(chunks)
    tensor_order = [item['name'] + '.safetensors' for item in json.loads(Path(live.config['ollama_layout']).read_bytes())['blobs']]
    sidecars = sorted(item['path'] for item in outputs if expected[item['path']]['role'] == 'METADATA')
    license_path = next(item['path'] for item in outputs if expected[item['path']]['role'] == 'LICENSE')
    layers = [{'mediaType': 'application/vnd.ollama.image.' + ('tensor' if path in tensor_order else
               'license' if path == license_path else 'json'), 'digest': by_path[path]['digest'],
               'size': by_path[path]['size'], **({} if path == license_path else {'name': path.removesuffix('.safetensors')
                                                                            if path in tensor_order else path})}
              for path in [*tensor_order, *sidecars, license_path]]
    config = by_path['ollama-config.json']
    manifest = json.dumps({'schemaVersion': 2, 'mediaType': 'application/vnd.docker.distribution.manifest.v2+json',
        'config': {'mediaType': 'application/vnd.docker.container.image.v1+json', 'digest': config['digest'],
                   'size': config['size']}, 'layers': layers}, separators=(',', ':')).encode()
    manifest_digest = 'sha256:' + hashlib.sha256(manifest).hexdigest()
    live.save('ollama-manifest.json', json.loads(manifest))
    source = _source_from(original['checkpoint']['source_lock'], precursor)
    blobs = {item['digest']: Artifact(item['path'], item['size'], item['digest'], '', item['digest']) for item in outputs}
    served = replace(source, immutable_revision=digest_bytes(canonical_bytes(recipe)),
                     artifacts=tuple(blobs.values()), metadata_assets=())
    capacity = CapacityCoordinator(live.cartridge)
    def read(artifact, offset, count):
        extents = {}
        try:
            for role, size in (('data', artifact.size), ('state', transfer_state_bytes(artifact.size))):
                extents[role] = grant_transfer_extent(live.cartridge, operation,
                    _transfer_extent_id(operation, artifact.path, role), size,
                    capacity_controller=capacity, require_existing=True)
            return _retained_source_range(served, artifact, extents, offset, count, manifests[artifact.path])
        finally:
            for extent in extents.values():
                os.close(extent.fd)
    requests, model_reads_allowed = [], [False]
    model_digests = {by_path[path]['digest'] for path in tensor_order}
    class Registry(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            return

        def do_GET(self):
            requests.append({'path': self.path, 'range': self.headers.get('Range'), 'time_ns': time.monotonic_ns()})
            if self.path == '/api/tags':
                payload = canonical_bytes({'models': [{'name': live.config['ollama_locator'],
                    'digest': manifest_digest, 'size': sum(item['size'] for item in outputs)}]})
                self.send_response(200)
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if '/manifests/' in self.path:
                self.send_response(200)
                self.send_header('Content-Length', str(len(manifest)))
                self.send_header('Docker-Content-Digest', manifest_digest)
                self.end_headers()
                self.wfile.write(manifest)
                return
            artifact = blobs.get(self.path.rsplit('/', 1)[-1])
            if artifact is None:
                self.send_error(404)
                return
            if artifact.digest in model_digests and not model_reads_allowed[0]:
                self.send_error(403, 'Actual tensor reads require completed source entry')
                return
            requested = self.headers.get('Range')
            start, end = (0, artifact.size - 1) if requested is None else map(int, requested.removeprefix('bytes=').split('-'))
            assert 0 <= start <= end < artifact.size
            self.send_response(200 if requested is None else 206)
            self.send_header('Content-Length', str(end - start + 1))
            self.send_header('ETag', artifact.digest)
            if requested is not None:
                self.send_header('Content-Range', f'bytes {start}-{end}/{artifact.size}')
            self.end_headers()
            for offset in range(start, end + 1, 4194304):
                self.wfile.write(read(artifact, offset, min(4194304, end + 1 - offset)))
    server = ThreadingHTTPServer(('127.0.0.1', live.config['ollama_port']), Registry)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        endpoint = f'http://127.0.0.1:{server.server_port}'
        live.save('ollama-generated-source.json', {'manifest_digest': manifest_digest, 'endpoint': endpoint,
            'composition_operation': operation, 'outputs': outputs, 'provenance': 'Actual pinned HF bytes; no quantization; frozen native byte recipe'})
        geometry = _bind_profile(live, 'ollama-generated-geometry', None, live.config['ollama_geometry_key'], geometry={
            'source_lock': None, 'source_kind': 'ollama', 'revision_algorithm': 'sha256',
            'source_storage': 'CARTRIDGE_RETAINED',
            'provenance': {'recipe_digest': digest_bytes(canonical_bytes(recipe)), 'composition_operation': operation},
            'artifacts': [{'path': item['path'], 'size': item['size'], 'digest_algorithm': 'sha256',
                           'validator_template': 'sha256:{digest}'} for item in outputs]})
        live.profile(geometry)
        connection = live.run('ollama-generated-connect', ['connect', '--source', 'ollama', '--endpoint', endpoint,
            '--public', '--key', live.config['ollama_connection_key']], 0)
        preparation = {'composition_request': {'protocol_version': '1', 'operation': 'source.compose',
            'idempotency_key': live.config['ollama_composition_key'], 'target': precursor,
            'arguments': {'composition': {'acquisition_operation_id': precursor, 'recipe': recipe}}},
            'geometry_request': geometry['request']}
        live.save('ollama-preparation.json', preparation)
        selected = live.run('ollama-generated-select', ['select-model', '--connection', connection['operation_id'],
            '--model', live.config['ollama_locator'], '--revision', manifest_digest,
            '--preparation', str(live.evidence / 'ollama-preparation.json'), '--key', live.config['ollama_selection_key']], 0)
        assert selected['result']['source_lock']['immutable_revision'] == manifest_digest
        plan = _bind_profile(live, 'ollama-generated', selected, live.config['ollama_acquisition_key'])
        live.profile(plan)
        for pending in live.config['plans']:
            if pending['instance'] != 'qwen3_30b_a3b' and not (
                    pending['instance'] == 'f4_qwen3_4b' and pending['kind'] == 'acquisition'):
                live.profile(pending)
        live.source_entry()
        live.register_consumers(plan)
        model_reads_allowed[0] = True
        return live.acquire(plan)
    finally:
        if live.child is not None:
            live.stop(live.directory)
        server.shutdown()
        server.server_close()
        thread.join(timeout=30)
        live.save('ollama-provider-requests.json', {'requests': requests, 'server_closed': not thread.is_alive()})


def _execute_l05(config, repo):
    """Execute the finite original input population; the calling test alone decides completion."""
    body = {key: value for key, value in config.items() if key != 'digest'}
    assert identity(body) == config['digest']
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == config['test_sha256']
    assert Path(broker_module.__file__).resolve() == repo / 'broker.py'
    for name, expected in config['runtime_files'].items():
        assert hashlib.sha256((repo / name).read_bytes()).hexdigest() == expected
        assert hashlib.sha256((Path(config['installed_site']) / name).read_bytes()).hexdigest() == expected
    for path, expected in config['input_files'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected
    frozen = json.loads(Path(config['frozen_bindings']).read_bytes())['bindings']
    original_inputs = {row['instance']: row for row in frozen}
    assert len(original_inputs) == 20 and len(config['plans']) == 30
    assert {row['instance'] for row in config['plans']} == set(original_inputs)
    for plan in config['plans']:
        original = original_inputs[plan['instance']]
        assert plan['source_selection'] == original['operation_id']
        assert plan['source_lock_digest'] == original['source_lock_digest']
        source_file = Path(config['state']) / 'operations' / (original['operation_id'] + '.json')
        assert hashlib.sha256(source_file.read_bytes()).hexdigest() == original['operation_file_sha256']
    evidence = Path(config['evidence'])
    evidence.mkdir(exist_ok=bool(config.get('continued_evidence')))
    live = _LiveL05(config, evidence)
    verified = {}
    try:
        if config.get('completed_selection_evidence'):
            prior = Path(config['completed_selection_evidence'])
            saved_exit = json.loads((prior / 'exit.json').read_bytes())
            assert saved_exit['exit_code'] == 0
            for name in ('stdout', 'stderr'):
                assert hashlib.sha256((prior / name).read_bytes()).hexdigest() == saved_exit['raw_sha256'][name]
            shown = json.loads((prior / 'stdout').read_bytes())
            drive = live.record(config['drive_selection_id'])
            assert all(key in drive and drive[key] == value for key, value in shown.items())
            live.save('completed-selection-reused.json', {'source': str(prior), 'actual_exit': saved_exit,
                'canonical_operation_id': drive['operation_id'], 'scope': 'Retained completed read-only selection; no repeated scan'})
        else:
            drive = live.run('fresh-drive-selection', ['select-drive', '--volume', config['volume_uuid'],
                '--folder', config['folder'], '--cartridge-uuid', config['cartridge_uuid'],
                '--key', config['drive_selection_key']], 0)
        assert drive['operation_id'] == config['drive_selection_id']
        assert drive['state'] == 'SUCCEEDED' and drive['result']['folder'] == config['folder']
        assert drive['result']['cartridge_uuid'] == config['cartridge_uuid']
        live.save('selected-inventory.json', drive)
        for plan in config['plans']:
            selected = live.record(plan['source_selection'])
            assert identity(selected['result']['source_lock']) == plan['source_lock_digest']
            recomputed = _bind_profile(live, plan['instance'], selected, plan['request']['idempotency_key'],
                                       header_lengths=plan['header_json_bytes'])
            for field in ('request', 'operation_id', 'profile', 'header_json_bytes'):
                assert recomputed[field] == plan[field], (plan['instance'], field)
            if plan['instance'] == 'qwen3_30b_a3b' or (
                    plan['instance'] == 'f4_qwen3_4b' and plan['kind'] == 'acquisition'):
                live.profile(plan)
        precursor = next(plan for plan in config['plans']
                         if plan['instance'] == 'qwen3_30b_a3b' and plan['kind'] == 'acquisition')
        header = next(plan for plan in config['plans']
                      if plan['instance'] == 'qwen3_30b_a3b' and plan['kind'] == 'header')
        live.register_precursor(precursor, header)
        live.headers(header)
        operation = live.acquire(precursor)
        record = live.record(operation)
        source = _source_from(record['checkpoint']['source_lock'], operation)
        verified[operation] = _verify_acquired_bytes(record, source, live.cartridge)
        live.save('pinned-precursor-byte-verification.json', verified[operation])
        ollama = _ollama_reimport(live, operation, header['operation_id'])
        for plan in config['plans']:
            if plan['kind'] == 'header' and plan['instance'] != 'qwen3_30b_a3b':
                live.headers(plan)
        for plan in config['plans']:
            if plan['kind'] == 'acquisition' and plan['instance'] != 'qwen3_30b_a3b':
                live.acquire(plan)
        live.save('execution-result.json', {'graph_digest': live.graph_digest, 'graph_head': live.head['digest'],
            'ollama_operation': ollama, 'precursor_byte_verification': verified, 'all_commands_finished': True})
        return verified, evidence, live.graph_digest
    finally:
        if live.child is not None:
            live.stop(live.directory)


def test_l05_complete(tmp_path):
    """Q80/Q5/Q9/Q31/Q41/Q44/Q51/Q52/Q53: prove the complete original L05 outcome.

    Existing fixture routines remain the only fixtures for their invariants. This test calls
    them as internal checks, then requires actual supported-launch acquisition, qualification,
    credentials and frozen-input evidence. Fixture success cannot close a live source row.
    """
    repo = Path(__file__).resolve().parents[1]
    queue, matrix = load_contracts(repo)
    stage = next(row for row in queue['fixed_steps'] if row['id'] == 'L05')
    assert stage['acceptance_test'].endswith('::test_l05_complete')
    assert queue['stage_acceptance_contract']['tests_per_stage'] == 1
    assert queue['stage_acceptance_contract']['secondary_agent_review_required'] is False
    config_path = os.environ.get('CASSETTE_L05_EXECUTION_CONFIG')
    assert config_path, 'Q80 L05 requires its bound finite execution and deciding-receipt inputs'
    config = json.loads(Path(config_path).read_bytes())
    assert identity(json.loads(json.dumps(queue, default=str))) == config['queue_digest']
    # Q80: another repair attempt preserves the complete immutable capture history.
    capture_parent = json.loads(Path(config['capture_parent']).read_bytes())
    capture = campaign_head(config['control'], 'attempts-L05-complete')
    assert capture['value']['active'] is True
    assert capture['value']['attempts'][:-1] == capture_parent['value']['attempts']
    assert capture['value']['attempts'][-1]['number'] == len(capture_parent['value']['attempts']) + 1
    assert capture['value']['attempts'][-1]['binding']['inputs']['configuration_digest'] == config['digest']
    from tools.campaign import matrix_assertions
    assert matrix_assertions(matrix) == config['matrix_assertions'], 'An original matrix assertion changed'
    parent = json.loads(Path(config['retirement_parent']).read_bytes())
    old = 'QUALIFY-ACQ-F4-required-20261016-03-VERIFY'
    assert old in qualification_successions(parent['nodes'], parent)
    hostile = copy.deepcopy(parent['nodes'])
    hostile['UNAPPROVED-EXTERNAL-CONSUMER'] = {'id': 'UNAPPROVED-EXTERNAL-CONSUMER', 'depends': [old]}
    with pytest.raises(CassetteError, match='external consumer'):
        qualification_successions(hostile, parent)
    current = 'ACQ-F4-required-20261026-04'
    renamed = json.loads(json.dumps(parent['nodes']).replace(current, 'UNAPPROVED-OTHER-INSTANCE'))
    assert old not in qualification_successions(renamed, {'nodes': renamed}), \
        'The instance approval became a general retirement rule'
    families = {row['family']: row for row in queue['expanded_session_families']}
    assert families['physical_qualification']['approved_instance_retirement']['prior'] == old
    assert families['source_header']['dependencies']['RUN'][0] == 'SOURCE-ENTRY-PASS'
    assert families['acquisition']['dependencies']['START'][0] == 'SOURCE-ENTRY-PASS'
    assert families['source_header']['approved_fixed_instance']['instance'] == 'qwen3_30b_a3b'
    assert families['acquisition']['approved_fixed_instance']['instance'] == 'qwen3_30b_a3b'

    # Q13/Q15/Q16: consume the original freeze, including every native candidate and dataset.
    freeze = Path(stage['machine_continuation']['evidence'])
    descriptors = {}
    validation = json.loads((freeze / 'descriptor-validation.json').read_bytes())
    for name in ('datasets', 'native-candidates', 'workloads', 'training', 'scorers',
                 'teacher-and-hosted', 'scale-fit'):
        manifest = json.loads((freeze / (name + '.json')).read_bytes())
        claimed = manifest.pop('digest')
        assert digest_bytes(canonical_bytes(manifest)) == claimed == validation['digests'][name], \
            'Q16 frozen input descriptor changed: ' + name
        descriptors[name] = manifest
    datasets = descriptors['datasets']['datasets']
    workload = descriptors['workloads']
    model_set = next(row['model_set'] for row in matrix['source_rows']
                     if row['id'] == 'source_huggingface_all_immutable_models')
    assert {row['model'] for row in workload['coordinates']} == {'F4', *model_set}
    scorer_digest = validation['digests']['scorers']
    for model in {'F4', *model_set}:
        rows = [row for row in workload['coordinates'] if row['model'] == model]
        assert len({row['primary_stratum'] for row in rows}) == len(rows)
        weights = [Fraction(row['weight_numerator'], row['weight_denominator']) for row in rows]
        declared = workload['weights']['vision' if any(row['primary_stratum'] == 'multimodal' for row in rows) else 'text_only']
        assert weights == [Fraction(value) for value in declared.split(',')] and sum(weights) == 1
        for row in rows:
            trials = row['paired_trials']
            assert trials['count_per_subbatch'] >= row['paired_trials_minimum']
            assert all(len(trials[name]) == len(set(trials[name])) == trials['count_per_subbatch']
                       for name in ('sampler_seeds', 'execution_seeds'))
            assert row['scorer']['identities'] == scorer_digest
            assert row['protocol_invariants'] and row['runtime_resource_limit'] and row['timeout_seconds'] > 0
            assert set(row['acquisition_dependencies']) == {
                datasets[item['dataset']]['verified_acquisition_dependency'] for item in row['input_descriptor']}
            for item in row['input_descriptor']:
                dataset = datasets[item['dataset']]
                assert item['dataset_descriptor_digest'] == identity(dataset)
                assert set(item['files']) <= {asset['rfilename'] for asset in dataset['artifacts']}
                assert item['selection']['first_row'] >= 0 and item['selection']['row_count'] > 0
                assert item['scorer'] in descriptors['scorers']['scorers']
    training = descriptors['training']['coordinates']
    assert {(row['training_row'], row['operation']) for row in training} == {
        (row['id'], operation) for row in matrix['training_rows'] for operation in row['operations']}
    for row in training:
        dataset = datasets[row['dataset']]
        assert row['dataset_descriptor_digest'] == identity(dataset)
        assert row['acquisition_dependency'] == dataset['verified_acquisition_dependency']
        assert row['budget'] and row['held_out_budget'] and row['held_out_selection'] and row['tokenizer']

    checks = (
        package_checks.test_q31_supported_launch_uses_only_the_installed_local_wheel,
        source_checks.test_q9_q52_ollama_catalogue_and_registry_resolution_are_separate_real_wires,
        source_checks.test_q9_huggingface_credential_validation_rejects_a_missing_or_bad_whoami_record,
        source_checks.test_q9_huggingface_resolution_refuses_non_lfs_model_content_before_any_payload_read,
        credential_checks.test_q9_q52_cli_existing_ollama_login_signs_account_and_pull_grants_across_processes,
        credential_checks.test_q9_acquisition_entry_keychain_reference_is_bound_opaque_and_revocable,
        credential_checks.test_q9_q52_cli_token_connection_uses_keychain_across_processes_and_revocation,
        drive_checks.test_q41_q44_q49_q53_l05_discovers_nested_root_and_revalidates_apfs_volume,
        entry_checks.test_q9_q52_cli_catalogue_uses_broker_and_bounded_provider_pages,
        entry_checks.test_q49_cli_drive_selection_preserves_inventory_and_scoped_intent,
        entry_checks.test_q5_q9_cli_selection_pins_source_without_downloading_weights,
        acquisition_checks.test_q5_q51_q53_acquire_stops_at_verified_source_and_reuses_transfer_progress,
        transfer_checks.test_q51_q53_chunk_claims_use_the_store_owned_coordinator,
        transfer_checks.test_q51_random_interruption_corruption_validator_resume_without_final_reread,
    )
    for index, check in enumerate(checks):
        directory = tmp_path / str(index)
        directory.mkdir()
        print(f'L05 internal check: {check.__name__}', flush=True)
        with pytest.MonkeyPatch.context() as patch:
            arguments = {'tmp_path': directory, 'monkeypatch': patch}
            check(**{name: arguments[name] for name in inspect.signature(check).parameters})
        print(f'L05 internal check complete: {check.__name__}', flush=True)

    preverified, evidence, graph_digest = _execute_l05(config, repo)
    state = config['state']
    assert state, 'Q80 L05 requires the actual canonical campaign state, not fixture results'
    owner = CanonicalBroker(Path(state) / 'operations')
    try:
        records = [owner._load(path.stem) for path in sorted(owner.operation_log.glob('op-*.json'))]
        complete = [row for row in records if row['kind'] == 'acquire'
                    and row['state'] == 'SUCCEEDED' and row['phase'] == 'SOURCE_VERIFIED']
        hf = next(row for row in matrix['source_rows']
                  if row['id'] == 'source_huggingface_all_immutable_models')
        expected = [(matrix['immutable_models'][key]['locator'], matrix['immutable_models'][key]['revision'])
                    for key in hf['model_set']]
        f4 = next(row for row in matrix['fixture_gate_rows'] if row['id'] == 'f4_gate')
        expected.append((f4['model'], f4['source_revision']))
        expected.extend((candidate['repository'], candidate['revision'])
                        for candidate in descriptors['native-candidates']['candidates'])
        expected.extend((dataset['repository'], dataset['revision'])
                        for dataset in descriptors['datasets']['datasets'].values())
        frozen_artifacts = {(item['repository'], item['revision']): item['source_artifacts']
                            for item in descriptors['native-candidates']['candidates']}
        dataset_artifacts = {(item['repository'], item['revision']): item['artifacts']
                             for item in descriptors['datasets']['datasets'].values()}
        frozen_artifacts.update(dataset_artifacts)
        preparation = json.loads((repo / 'docs/l05/2026-10-15-source-qualification-preparation.json').read_bytes())
        for item in preparation['source_instances'].values():
            if item['kind'] == 'model':
                frozen_artifacts[(item['repository'], item['revision'].removeprefix('git-sha1:'))] = item['frozen_artifacts']
        assert set(expected) == set(frozen_artifacts)
        missing = []
        for locator, revision_id in expected:
            matches = [row for row in complete
                       if row['checkpoint']['source_lock']['source_kind'] == 'huggingface'
                       and row['checkpoint']['source_lock']['locator'] == locator
                       and row['checkpoint']['source_lock']['immutable_revision'] == 'git-sha1:' + revision_id]
            if not matches:
                missing.append(locator + '@' + revision_id)
                continue
            row = matches[-1]
            source = _source_from(row['checkpoint']['source_lock'], row['operation_id'])
            frozen = frozen_artifacts[(locator, revision_id)]
            actual = {item.path: item for item in (*source.artifacts, *source.metadata_assets)}
            wanted = {item.get('rfilename', item.get('path')) for item in frozen}
            if (locator, revision_id) in dataset_artifacts:
                assert {item.path for item in source.artifacts} == wanted
                assert json.loads(source.artifact_selector) == {'dataset_paths': sorted(wanted)}
            else:
                assert set(actual) == wanted and source.artifact_selector is None
            for item in frozen:
                artifact = actual[item.get('rfilename', item.get('path'))]
                assert artifact.size == item['size']
                if 'digest' in item:
                    assert artifact.digest == item['digest']
                elif item.get('lfs'):
                    assert artifact.digest == 'sha256:' + item['lfs']['sha256']
                else:
                    assert artifact.validator == '"' + item['blobId'] + '"'
            _verify_partials(row['checkpoint']['partials'], source, row['operation_id'],
                             (*source.artifacts, *source.metadata_assets))
            prepared = [event['payload']['drive_prepared'] for event in row['events']
                        if 'drive_prepared' in event['payload']]
            assert len(prepared) == 1, 'Q44 acquisition must come through the supported Go path'
            proof = prepared[0]
            assert digest_bytes(canonical_bytes(proof['protected_inventory'])) == proof['binding']['inventory_digest']
            assert asyncio.run(owner._revalidate_durability(Path(proof['root']), proof['binding']))
            selection = DriveSelection(DriveVolume(**proof['selection']['volume']),
                                       WriterContext(**proof['selection']['writer']))
            profile = asyncio.run(owner._qualify_download(row['operation_id'],
                CapacityCoordinator(proof['root']), selection, source, require_existing=True))
            assert profile['status'] == 'PASS'
            assert any(event['payload'].get('source_qualification') == profile for event in row['events']), \
                'Q41/Q42 raw profile replay differs from the acquisition receipt'
            assert row['result']['verified_bytes'] == sum(item.size for item in (*source.artifacts, *source.metadata_assets))
            assert row['result']['verified_artifacts'] == [
                {'path': item.path, 'size': item.size, 'digest': item.digest}
                for item in sorted((*source.artifacts, *source.metadata_assets), key=lambda item: item.path)]
            if row['operation_id'] not in preverified:
                preverified[row['operation_id']] = _verify_acquired_bytes(row, source, Path(proof['root']))
            if all(item.path.endswith('.safetensors') for item in source.artifacts):
                _verify_model_headers(owner, records, source, proof)
        assert not missing, 'Q80 L05 required acquisitions are unproved: ' + ', '.join(missing)

        selections = [row for row in records if row['kind'] == 'source.select' and row['state'] == 'SUCCEEDED']
        executed = json.loads((evidence / 'execution-result.json').read_bytes())
        reimports = [row for row in complete if row['operation_id'] == executed['ollama_operation']
                     and row['checkpoint']['source_lock']['source_kind'] == 'ollama'
                     and any(selected['result']['source_lock'] == row['checkpoint']['source_lock']
                             and selected['result'].get('preparation') for selected in selections)]
        assert reimports, \
            'Q80 L05 requires the pinned Ollama content-addressed reimport through the product path'
        for reimport in reimports:
            selected = next(selected for selected in selections
                            if selected['result']['source_lock'] == reimport['checkpoint']['source_lock']
                            and selected['result'].get('preparation'))
            prepared = selected['result']['preparation']
            composition = owner._load(prepared['composition_operation_id'])
            original = owner._load(composition['target'])
            pinned = matrix['immutable_models']['qwen3_30b_a3b']
            assert composition['kind'] == 'source.compose' and composition['state'] == 'SUCCEEDED'
            assert original['state'] == 'SUCCEEDED' and original['phase'] == 'SOURCE_VERIFIED'
            assert original['checkpoint']['source_lock']['locator'] == pinned['locator']
            assert original['checkpoint']['source_lock']['immutable_revision'] == 'git-sha1:' + pinned['revision']
            assert prepared['source_lock_digest'] == digest_bytes(canonical_bytes(reimport['checkpoint']['source_lock']))
            assert prepared['geometry_profile']['status'] == prepared['composition_profile']['status'] == 'PASS'
            source = _source_from(reimport['checkpoint']['source_lock'], reimport['operation_id'])
            _verify_partials(reimport['checkpoint']['partials'], source, reimport['operation_id'],
                             (*source.artifacts, *source.metadata_assets))
            drive = [event['payload']['drive_prepared'] for event in reimport['events']
                     if 'drive_prepared' in event['payload']]
            assert len(drive) == 1
            _verify_acquired_bytes(reimport, source, Path(drive[0]['root']))
        connection = owner._load(config['ollama_authenticated_connection'])
        assert connection['kind'] == 'source.connect' and connection['state'] == 'SUCCEEDED'
        assert (connection['result']['source'] == 'ollama' and connection['result'].get('credential_ref')
                and connection['result'].get('authentication', {}).get('authenticated') is True), \
            'Q9 L05 requires a provider-validated authenticated connection as well as public access'
        # Final input closure is read from the existing campaign, not inferred from source selection.
        dataset_proofs = {(row['checkpoint']['source_lock']['locator'],
                           row['checkpoint']['source_lock']['immutable_revision'].removeprefix('git-sha1:'))
                          for row in complete if row['checkpoint']['source_lock']['source_kind'] == 'huggingface'
                          and row['checkpoint']['source_lock'].get('artifact_selector', {}).get('dataset_paths')}
        assert set(dataset_artifacts) <= dataset_proofs, 'Q15/Q16 every original frozen dataset needs verified bytes'
        assert len(preverified) == len(set(expected)), 'Every frozen input needs its own full raw byte verification'
        assert json.loads((evidence / 'source-entry.json').read_bytes())['status'] == 'PASS'
        assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == config['test_sha256']
        for name, expected_hash in config['runtime_files'].items():
            assert hashlib.sha256((repo / name).read_bytes()).hexdigest() == expected_hash
            assert hashlib.sha256((Path(config['installed_site']) / name).read_bytes()).hexdigest() == expected_hash
        (evidence / 'assertions-result.json').write_bytes(canonical_bytes({'stage': 'L05',
            'stage_input_digest': config['digest'], 'sole_test_sha256': config['test_sha256'],
            'runtime_receipt_sha256': config['runtime_receipt_sha256'], 'runtime_files': config['runtime_files'],
            'frozen_input_verifications': preverified, 'ollama_operations': [row['operation_id'] for row in reimports],
            'graph_digest': graph_digest, 'original_assertions_digest': identity(config['matrix_assertions']),
            'assertions_completed': True, 'stage_verdict': 'Requires the actual single pytest exit and outer exact-input receipt'}))
    finally:
        owner.close()
