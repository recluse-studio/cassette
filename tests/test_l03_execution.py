# test_l03_execution.py — L03 full-graph objectives, optimizer windows and broker publication; depends on adapters/__init__.py, broker.py, compiler.py, errors.py, pager.py, store.py, sources.py, trainer.py, tests/fixture_server.py, tests/test_l02_native.py, tests/test_s22_trainer.py, tests/test_s13_pager.py, tools/capture_fixture.py.
"""Compare native training against scalar graph probabilities and finite differences."""
import asyncio
from contextlib import closing
import copy
import math
from fractions import Fraction

import pytest

from broker import CanonicalBroker
from compiler import verify_native_bundle
from errors import CassetteError
from pager import NativeTransformer
from store import canonical_bytes, load_root, read_training_page, digest_bytes
from trainer import prepare_native_training, native_training_state, native_training_inputs, native_training_context, advance_native_training
from test_l02_native import _case, _oracle, PROFILE
from test_s22_trainer import _profile


def _adapt(weights, adapters):
    result = copy.deepcopy(weights)
    for name, factors in adapters.items():
        shape, original = result[name]
        a, b = factors['a'], factors['b']
        result[name] = (shape, [original[r*shape[1]+c] + factors['scale'] * sum(b[r][k]*a[k][c] for k in range(len(a)))
                              for r in range(shape[0]) for c in range(shape[1])])
    return result


def _probability(config, weights, sequence):
    value = 0
    for position, selected in enumerate(sequence['mask'][1:], 1):
        if selected:
            logits, _ = _oracle(config, weights, sequence['tokens'][:position])
            maximum = max(logits)
            value += logits[sequence['tokens'][position]] - maximum - math.log(sum(math.exp(x-maximum) for x in logits))
    return value


def _loss(config, weights, adapters, operation, batch, beta=.1, reference_weights=None):
    changed = _adapt(weights, adapters)
    if operation != 'OFFLINE_ADAPTER_DPO':
        return -_probability(config, changed, batch['sequence']) / sum(batch['sequence']['mask'])
    policy = _probability(config, changed, batch['chosen']) - _probability(config, changed, batch['rejected'])
    frozen = weights if reference_weights is None else reference_weights
    reference = _probability(config, frozen, batch['chosen']) - _probability(config, frozen, batch['rejected'])
    return math.log1p(math.exp(-beta*(policy-reference)))


def test_q21_q24_q25_q72_q73_native_objectives_windows_and_publication(tmp_path):
    """Q21/Q24/Q25/Q72/Q73: scalar sequence losses, frozen-window gradients, updates and callable children."""
    sequence = {'tokens': [1,3,4,2,0], 'mask': [0,0,1,1,0]}
    rejected = {'tokens': [1,3,11,2], 'mask': [0,0,1,1]}
    outcomes = []
    for operation in ('ADAPTER_SFT', 'ADAPTER_CONTINUED_PRETRAINING', 'OFFLINE_ADAPTER_DPO'):
        with _case(tmp_path, operation, hidden=8, layers=1) as (cartridge, owner, root, config, weights, *_):
            runtime = NativeTransformer(cartridge, root, PROFILE, 'objective', 'blake3:'+'0'*64)
            names = ['lm_head.weight', 'model.layers.0.self_attn.q_proj.weight']
            adapters = {name: {'a': [[.01*(i+1) for i in range(weights[name][0][1])]],
                              'b': [[.01*math.sin(i+1)] for i in range(weights[name][0][0])], 'scale': 1.0}
                        for name in names}
            batch = {'chosen': sequence, 'rejected': rejected} if operation == 'OFFLINE_ADAPTER_DPO' else {'sequence': sequence}
            reference = runtime if operation == 'OFFLINE_ADAPTER_DPO' else None
            expected_loss = _loss(config, weights, adapters, operation, batch)
            if reference:
                reverse = {'chosen': batch['rejected'], 'rejected': batch['chosen']}
                reversed_loss = runtime.objective(operation, reverse, adapters, differentiate=names[0], reference=reference)['loss']
                assert abs(reversed_loss - _loss(config, weights, adapters, operation, reverse)) < 2e-6
                assert reversed_loss != runtime.objective(operation, batch, adapters, differentiate=names[0], reference=reference)['loss']
            expected = copy.deepcopy(adapters)
            errors = []
            for name in names:
                result = runtime.objective(operation, batch, adapters, differentiate=name, reference=reference)
                assert abs(result['loss']-expected_loss) < 2e-6
                for factor in ('a', 'b'):
                    for row, values in enumerate(adapters[name][factor]):
                        for column in range(len(values)):
                            left, right = copy.deepcopy(adapters), copy.deepcopy(adapters)
                            left[name][factor][row][column] -= .001
                            right[name][factor][row][column] += .001
                            gradient = (_loss(config, weights, right, operation, batch)-_loss(config, weights, left, operation, batch))/.002
                            errors.append(abs(gradient-result['gradients'][factor][row][column]))
                            expected[name][factor][row][column] -= .1*gradient
            assert max(errors) < 1e-5
            checkpoint, manifest = prepare_native_training(cartridge, root, operation, adapters, (canonical_bytes(batch),),
                epochs=1, learning_rate=.1, precision='FP32', seed=17, window_limit_bytes=4096,
                reference_root=root if reference else None, beta=.1, capacity_controller=owner,
                resource_profile=_profile(), memory_peak_bytes=runtime.declared_peak_bytes*8)
            if operation == 'ADAPTER_SFT':
                state, frozen_batch, frozen_adapters = native_training_inputs(cartridge, checkpoint, manifest)
                receipt = runtime.objective(operation, frozen_batch, frozen_adapters,
                    differentiate=state['adapters'][0]['tensor_id'], training_context=native_training_context(state, manifest))
                forged = copy.deepcopy(receipt); forged['input_digest'] = 'blake3:'+'f'*64
                forged['receipt_digest'] = digest_bytes(canonical_bytes({k:v for k,v in forged.items() if k != 'receipt_digest'}))
                with pytest.raises(CassetteError) as wrong:
                    advance_native_training(cartridge, checkpoint, manifest, forged, capacity_controller=owner)
                assert wrong.value.code == 'GRADIENT_INVALID'
                checkpoint, manifest = advance_native_training(cartridge, checkpoint, manifest, receipt, capacity_controller=owner)
                assert native_training_state(cartridge, checkpoint, manifest)['window'] == 1
            request = {'protocol_version': '1', 'operation': 'train' , 'target': load_root(cartridge, root)['identity'],
                       'idempotency_key': 'train-'+operation, 'arguments': {'checkpoint_root': checkpoint, 'manifest_digest': manifest}}
            with closing(CanonicalBroker(cartridge/'operations')) as broker:
                operation_result = asyncio.run(broker.train_native(request, cartridge, PROFILE, owner))
                assert operation_result['state'] == 'SUCCEEDED', operation_result
                record = broker._load(operation_result['operation_id'])
                output = record['result']
            state = native_training_state(cartridge, output['root_digest'], output['manifest_digest'])
            verify_native_bundle(cartridge, output['root_digest'])
            for row in state['adapters']:
                import json
                factors = json.loads(read_training_page(cartridge, output['root_digest'], row['page_digest']))
                for factor in ('a', 'b'):
                    assert max(abs(a-b) for xs, ys in zip(factors[factor], expected[row['tensor_id']][factor]) for a,b in zip(xs,ys)) < 2e-6
            child = NativeTransformer(cartridge, output['root_digest'], PROFILE, 'child', 'blake3:'+'1'*64)
            import struct
            for name in names:
                merged = struct.unpack('<'+'f'*math.prod(weights[name][0]), child.effective_tensor(name))
                independent = _adapt(weights, expected)[name][1]
                assert max(abs(a-b) for a,b in zip(merged, independent)) < 2e-6
            child_logits = child.step([1,3,4], seed=17)['logits']
            oracle_logits, _ = _oracle(config, _adapt(weights, expected), [1,3,4])
            assert max(abs(a-b) for a,b in zip(child_logits, oracle_logits)) < 3e-6
            if operation == 'OFFLINE_ADAPTER_DPO':
                changed_reference = runtime.objective(operation, batch, adapters, differentiate=names[0], reference=child)['loss']
                expected_reference = _loss(config, weights, adapters, operation, batch, reference_weights=_adapt(weights, expected))
                assert abs(changed_reference-expected_reference) < 2e-6
                assert changed_reference != expected_loss
                asyncio.run(_clients(cartridge, owner, load_root(cartridge, output['root_digest'])['identity'], 'trained'))
            outcomes.append((operation, max(errors), state['losses']))
    print(outcomes)


def test_q23_q51_q52_dataset_transfer_and_bounded_records(tmp_path):
    """Q23/Q51/Q52: an interrupted real transfer preserves exact sequence and preference records."""
    import os
    from fixture_server import source_fixture_server
    from sources import SourceAdapter, training_records, transfer_artifact, transfer_state_bytes
    from store import CapacityCoordinator, grant_transfer_extent
    records = [{'sequence': {'tokens': [1,3,4,2,0], 'mask': [0,0,1,1,0]}},
               {'chosen': {'tokens': [1,3,4], 'mask': [0,0,1]}, 'rejected': {'tokens': [1,3,11], 'mask': [0,0,1]}}]
    payload = b''.join(canonical_bytes(row)+b'\n' for row in records)
    cartridge = tmp_path/'dataset'; cartridge.mkdir()
    owner = CapacityCoordinator(cartridge)
    extent = grant_transfer_extent(cartridge, 'dataset', 'bytes', len(payload), capacity_controller=owner)
    checkpoint = grant_transfer_extent(cartridge, 'dataset', 'checkpoint', transfer_state_bytes(len(payload)), capacity_controller=owner)
    try:
        with source_fixture_server(artifact_overrides={'huggingface': (('train.jsonl', payload, '"dataset-v1"'),)}) as server:
            adapter = SourceAdapter('huggingface', server.base_url, lambda _: 's09-fixture-secret-never-serialize')
            revision = asyncio.run(adapter.resolve({'kind': 'huggingface', 'locator': 'fixture/huggingface-model',
                'revision': 'main', 'credential_ref': 'keychain:dataset', 'license_acceptance_ref': 'license:dataset',
                'expected_identity': 'blake3:'+'a'*64}))
            artifact = revision.artifacts[0]
            async def interrupted():
                server.range_delay = .05
                task = asyncio.create_task(transfer_artifact(adapter, revision, artifact, extent, checkpoint, owner))
                await asyncio.sleep(.005)
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
                server.range_delay = 0
                return await transfer_artifact(adapter, revision, artifact, extent, checkpoint, owner)
            state = asyncio.run(interrupted())
            assert list(training_records(artifact, extent, state, record_limit_bytes=256)) == [canonical_bytes(row) for row in records]
            os.pwrite(extent.fd, b'!', 0)
            with pytest.raises(CassetteError) as corrupted:
                next(training_records(artifact, extent, state, record_limit_bytes=256))
            assert corrupted.value.code == 'IDENTITY_MISMATCH'
    finally:
        os.close(extent.fd); os.close(checkpoint.fd)


async def _clients(cartridge, owner, identity, label):
    from adapters import NamedAdapter
    import json
    messages = [{'role': 'user', 'content': 'hello'}, {'role': 'assistant', 'content': 'world'}, {'role': 'user', 'content': 'today'}]
    tools = [{'name': 'weather'}]
    with closing(CanonicalBroker(cartridge/'operations')) as broker:
        capability = broker.native_capability(cartridge)
        assert capability['reasoning'] is False and capability['structured_output']['supported'] is False
        assert capability['performance_tiers'] == []
        assert capability['tools'] == {'prompt_definitions': True, 'generated_calls': False}
        for name in ('codex', 'custom', 'hermes', 'ollama', 'openclaw'):
            adapter = NamedAdapter(name, server_contract=True, model_aliases={identity: 'openclaw:fixture'})
            if name == 'custom' and label == 'native':
                await _client_controls(adapter, broker, cartridge, owner, identity)
            request = {'idempotency_key': label+'-'+name, 'model_ref': identity, 'input': messages, 'tools': tools, 'generation': {}}
            wire = adapter.to_wire_request(request)
            assert adapter.from_wire_request(wire) == request
            server = await adapter.listen(broker, cartridge, PROFILE, owner)
            writer = None
            try:
                reader, writer = await asyncio.open_connection('127.0.0.1', server.sockets[0].getsockname()[1])
                if wire.get('encoding') == 'jsonl':
                    writer.write(canonical_bytes(wire['record'])+b'\n')
                    await writer.drain()
                    frames = [json.loads(line) for line in (await reader.read()).splitlines()]
                    response = {'encoding': 'jsonl', 'records': frames}
                else:
                    payload = canonical_bytes(wire['body'])
                    headers = ''.join(f'{key}: {value}\r\n' for key, value in wire['headers'].items())
                    writer.write(f"{wire['method']} {wire['path']} HTTP/1.1\r\n{headers}Content-Length: {len(payload)}\r\n\r\n".encode()+payload)
                    await writer.drain()
                    first = await reader.readline()
                    assert b'200' in first, (first, await reader.read())
                    while True:
                        header = await asyncio.wait_for(reader.readline(), 10)
                        assert header, 'listener closed before response headers completed'
                        if header == b'\r\n':
                            break
                    raw = b''
                    while True:
                        size = int((await reader.readline()).strip(), 16)
                        if not size:
                            break
                        raw += await reader.readexactly(size)
                        assert await reader.readexactly(2) == b'\r\n'
                    sse = raw.startswith(b'data: ')
                    frames = [json.loads(line[6:] if sse else line) for line in raw.splitlines() if line]
                    response = {'encoding': 'sse' if sse else 'ndjson', 'frames': frames}
                events = adapter.from_wire_events(response)
                assert events[-1]['type'] == 'completed', events
                assert any(event['type'] == 'output_delta' and event['payload'].get('text') for event in events), events
                assert events[-1]['payload']['execution_mode'] == ('COMPILED_CERTIFIED' if label.startswith('compiled') else 'NATIVE')
            finally:
                if writer is not None:
                    writer.close()
                    await writer.wait_closed()
                server.close()
                await server.wait_closed()


def test_q19_q20_q25_q31_q40_q58_q64_q76_compiled_source_and_clients(tmp_path, monkeypatch):
    """Q19/Q20/Q25/Q31/Q40/Q58/Q64/Q76: resumed compiled windows and actual native/compiled client journeys."""
    monkeypatch.setattr("secrets.token_hex", lambda count: "ff" * count)
    from compiler import prepare_native_compiled, render_native_input, _native_head_windows
    from tools.capture_fixture import capture_native
    from test_s13_pager import _fixture
    from store import commit_generation, recover_generation
    with _case(tmp_path, 'compiled', hidden=4, layers=1, vocabulary_size=8) as (cartridge, owner, root, config, weights, *_):
        messages = [{'role': 'user', 'content': 'hello'}, {'role': 'assistant', 'content': 'world'}, {'role': 'user', 'content': 'today'}]
        rendered = render_native_input(cartridge, root, messages, [{'name': 'weather'}])
        tokens = rendered['token_ids']
        workload = {'version': 'native-workload-v1', 'baseline': {'root_digest': root, 'equivalence': 'EXACT_FIXTURE'},
            'cases': [{'condition_id': 'hello', 'stratum': 'common', 'tokens': tokens, 'pixels': None,
                       'ablations': [['lm_head.weight']], 'gradient': {'operation': 'ADAPTER_SFT', 'batch': {'sequence': {'tokens': [1,3,4,2], 'mask': [0,0,1,1]}}, 'adapters': {'lm_head.weight': {'a': [[.01]*4], 'b': [[.01]]*8, 'scale': 1.0}}, 'window': 'lm_head.weight'}}],
            'seeds': [17], 'trials': 1, 'scorer': 'TOKEN_LOGIT_VECTOR', 'confidence': 1, 'support': ['hello'], 'off_support': 'REJECT'}
        observations = capture_native(cartridge, root, PROFILE, workload)
        assert observations == capture_native(cartridge, root, PROFILE, workload)
        assert observations['traces'][0]['ablations'][0]['changed']
        _false_cover_and_composition()
        plan, _, _, profile = _fixture(); profile['context_bytes'] = 0
        rank_one = next(_native_head_windows(cartridge, root, observations, 12, profile, plan['prior_mode_failures'], rank_budget=1))
        assert _window_oracle(rank_one, cartridge, root) == 1
        assert Fraction(rank_one['certificate']['resources']['eta_rep']) > 0
        from pager import admit_schedule
        for field, value in (('support', ['absent']), ('confidence', .5)):
            altered = copy.deepcopy(rank_one['evidence'])
            altered['observation_contract'][field] = value
            with pytest.raises(CassetteError):
                admit_schedule(rank_one['plan'], rank_one['certificate'], altered, profile)
        partial = prepare_native_compiled(cartridge, root, observations, 12, profile, plan['prior_mode_failures'],
            capacity_controller=owner, operation_id='compile', max_windows=2)
        assert load_root(cartridge, partial)['plans'][0]['compiled']['complete'] is False
        with pytest.raises(CassetteError):
            NativeTransformer(cartridge, partial, PROFILE, 'partial', 'blake3:'+'0'*64)
        candidate = prepare_native_compiled(cartridge, root, observations, 12, profile, plan['prior_mode_failures'],
            capacity_controller=owner, operation_id='compile', checkpoint_root=partial)
        runtime = NativeTransformer(cartridge, candidate, PROFILE, 'compiled-step', 'blake3:'+'0'*64)
        from fractions import Fraction as F
        for window in runtime.compiled_windows:
            _window_oracle(window, cartridge, candidate)
        resources = runtime.compiled['resources']
        assert resources['description_bytes_total'] == resources['description_bytes_peak'] == 16*len(runtime.compiled_windows)
        assert F(resources['delta_exec_total']) == sum(F(row['risk']) for row in runtime.compiled['windows'])
        assert F(resources['error_coefficient_squared']) == len(runtime.compiled_windows)*sum(F(row['error_coefficient_squared']) for row in runtime.compiled['windows'])
        result = asyncio.run(runtime.execute_step(tokens, seed=17))
        assert {after for _,_,after in runtime.compiled_exact_transitions} >= {'HASHED', 'RESIDENT', 'GPU_SUBMITTED', 'RECLAIMABLE'}
        assert runtime.compiled['resources']['exact_source_bytes_per_step'] > 0
        assert result['state']['correction_key'] == 'ffffffffffffffff'
        assert result['state']['correction_key'] != '0000000000000011'
        from store import commit_runtime_state
        asyncio.run(_clients(cartridge, owner, load_root(cartridge, root)['identity'], 'native'))
        current = recover_generation(cartridge)
        commit_generation(cartridge, 'before-context', candidate, expected_parent_root=current.root_digest, capacity_controller=owner, operation_id='before-context')
        pin = commit_runtime_state(cartridge, candidate, 'compiled-step', result['payload'], capacity_controller=owner)
        resumed = NativeTransformer(cartridge, pin.root_digest, PROFILE, 'compiled-step', 'blake3:'+'0'*64)
        assert resumed.state == result['state']
        runtime.state, runtime.kv = resumed.state, resumed.kv
        continued = asyncio.run(runtime.execute_step(tokens, seed=17))
        recovered = asyncio.run(resumed.execute_step(tokens, seed=17))
        assert continued['payload'] == recovered['payload'] and continued['logits'] == recovered['logits']

        expected, _ = _oracle(config, weights, tokens)
        assert max(abs(a-b) for a,b in zip(result['logits'], expected)) < .001
        assert sum(row['bytes'] for row in runtime.compiled_reads) <= len(tokens)*runtime.compiled['resources']['fresh_traffic_max']
        with pytest.raises(CassetteError):
            asyncio.run(runtime.execute_step([1,3,11], seed=17))
        current = recover_generation(cartridge)
        commit_generation(cartridge, 'publish-compiled', candidate, expected_parent_root=current.root_digest,
                          capacity_controller=owner, operation_id='publish-compiled')
        asyncio.run(_clients(cartridge, owner, load_root(cartridge, candidate)['identity'], 'compiled'))
        _compiled_training_recovery(cartridge, owner, candidate)
    _rare_observations(tmp_path)


def _window_oracle(window, cartridge, root):
    """Q19: compute 2x2 rank, projective loss and residual law independently."""
    from fractions import Fraction as F
    import struct
    evidence, certificate = window['evidence'], window['certificate']
    target = list(map(F, evidence['target']['source_values']))
    for address in window['addresses']:
        raw = read_training_page(cartridge, root, address['page_digest'])
        assert address['length'] == 4
        assert F(struct.unpack_from('<f', raw, address['offset'])[0]) == target[2*address['row']+address['column']]
    atom = [F(x) for row in evidence['atoms'][0]['matrix'] for x in row]
    reconstruction = [F(x) for row in evidence['atoms'][0]['description']['reconstruction'] for x in row]
    rank = 2 if atom[0]*atom[3] != atom[1]*atom[2] else int(any(atom))
    assert certificate['atoms'][0]['rank'] == rank
    for condition, witness in zip(evidence['conditions'], certificate['atoms'][0]['witness_losses']):
        metric = [[F(x) for x in row] for row in condition['metric']]
        def inner(x,y):
            return sum(x[r]*metric[r][c]*y[c] for r in range(4) for c in range(4))
        loss = inner(target,target)-inner(atom,target)**2/inner(atom,atom)
        assert loss == F(witness['loss'])
        assert loss <= F(certificate['resources']['eta_rep'])
    norms = [sum((atom[r*2+c]-reconstruction[r*2+c])**2 for r in range(2)) for c in range(2)]
    law = evidence['execution_contract']['sampling_laws'][0]['law']
    assert sum(norms) == F(certificate['atoms'][0]['description']['distortion_bound'])
    if sum(norms):
        assert {row['column']: F(row['probability']) for row in law['atom_distributions'][0]['columns']} == {c:n/sum(norms) for c,n in enumerate(norms) if n}
    return rank


def _compiled_training_recovery(cartridge, owner, parent):
    """Q25/Q70/Q75: regenerate from exact training and compare a clean compiler replay."""
    from compiler import prepare_native_compiled
    from store import commit_generation, recover_generation
    for precision in ('FP32', 'BF16'):
        current = recover_generation(cartridge)
        commit_generation(cartridge, 'reset-'+precision, parent, expected_parent_root=current.root_digest,
                          capacity_controller=owner, operation_id='reset-'+precision)
        runtime = NativeTransformer(cartridge, parent, PROFILE, 'training-'+precision, 'blake3:'+'0'*64, purpose='EXACT_SOURCE_TRAINING')
        adapters = {'lm_head.weight': {'a': [[.01]*4], 'b': [[.01]]*8, 'scale': 1.0}}
        batch = {'sequence': {'tokens': [1,3,4,2], 'mask': [0,0,1,1]}}
        checkpoint, manifest = prepare_native_training(cartridge, parent, 'ADAPTER_SFT', adapters, (canonical_bytes(batch),),
            epochs=1, learning_rate=.1, precision=precision, seed=17, window_limit_bytes=4096,
            reference_root=None, beta=.1, capacity_controller=owner, resource_profile=_profile(),
            memory_peak_bytes=runtime.declared_peak_bytes*8)
        with pytest.raises(CassetteError):
            NativeTransformer(cartridge, checkpoint, PROFILE, 'stale', 'blake3:'+'0'*64)
        request = {'protocol_version': '1', 'operation': 'train', 'target': load_root(cartridge, parent)['identity'],
                   'idempotency_key': 'recover-'+precision, 'arguments': {'checkpoint_root': checkpoint, 'manifest_digest': manifest}}
        with closing(CanonicalBroker(cartridge/'operations')) as broker:
            outcome = asyncio.run(broker.train_native(request, cartridge, PROFILE, owner))
            assert outcome['state'] == 'SUCCEEDED', outcome
            child = outcome['result']['root_digest']
            assert broker.callable_revision(outcome['operation_id'], cartridge).root_digest == child
        verify_native_bundle(cartridge, child)
        compiled = load_root(cartridge, child)['plans'][0]['compiled']
        assert compiled['observations']['corpus_digest'] != load_root(cartridge, parent)['plans'][0]['compiled']['observations']['corpus_digest']
        clean = prepare_native_compiled(cartridge, compiled['source_root'], compiled['observations'], compiled['horizon'],
            compiled['profile'], compiled['prior_failures'], capacity_controller=owner, operation_id='clean-'+precision,
            effective_target=compiled['effective_target'], rank_budget=compiled['rank_budget'], read_deadline_ns=compiled['read_deadline_ns'])
        assert clean == child
        from store import begin_generation, advance_generation, CapacityCoordinator
        commit_generation(cartridge, 'before-interruption-'+precision, parent, expected_parent_root=child,
                          capacity_controller=owner, operation_id='before-interruption-'+precision)
        transaction = 'interrupted-'+precision
        state = begin_generation(cartridge, transaction, child, expected_parent_root=parent, capacity_controller=owner, operation_id=transaction)
        for _ in range(4):
            state = advance_generation(cartridge, transaction, capacity_controller=owner, operation_id=transaction)
        assert recover_generation(cartridge).root_digest in {parent, child}
        restarted_owner = CapacityCoordinator(cartridge)
        pin = commit_generation(cartridge, transaction, child, expected_parent_root=parent, capacity_controller=restarted_owner, operation_id=transaction)
        assert pin.root_digest == child and recover_generation(cartridge).root_digest == child
        tokens = compiled['observations']['workload']['cases'][0]['tokens']
        actual = asyncio.run(NativeTransformer(cartridge, child, PROFILE, 'reloaded-'+precision, 'blake3:'+'1'*64).execute_step(tokens, seed=17))
        exact = NativeTransformer(cartridge, child, PROFILE, 'exact-'+precision, 'blake3:'+'1'*64, purpose='EXACT_SOURCE_OBSERVATION').step(tokens, seed=17)
        assert max(abs(a-b) for a,b in zip(actual['logits'], exact['logits'])) < .001
        if precision == 'FP32':
            asyncio.run(_clients(cartridge, owner, load_root(cartridge, child)['identity'], 'compiled-recovered'))
        print('compiled recovery', precision, child)


def _rare_observations(tmp_path):
    """Q18/Q40: every source expert is observed and its ablation has a measured effect."""
    from tools.capture_fixture import capture_native
    with _case(tmp_path, 'rare-observations', hidden=4, layers=1, experts=4) as (cartridge, owner, root, config, weights, *_):
        gradient = {'operation': 'ADAPTER_SFT', 'batch': {'sequence': {'tokens': [1,3,4,2], 'mask': [0,0,1,1]}},
                    'adapters': {'lm_head.weight': {'a': [[.01]*4], 'b': [[.01]]*18, 'scale': 1.0}}, 'window': 'lm_head.weight'}
        names = [f'model.layers.0.block_sparse_moe.experts.{index}.w2.weight' for index in range(4)]
        cases = [{'condition_id': 'token-'+str(token), 'stratum': 'common' if token == 3 else 'rare',
                  'tokens': [1,token,4], 'pixels': None, 'ablations': [[name] for name in names], 'gradient': gradient} for token in range(18)]
        workload = {'version': 'native-workload-v1', 'baseline': {'root_digest': root, 'equivalence': 'EXACT_FIXTURE'},
                    'cases': cases, 'seeds': [17], 'trials': 1, 'scorer': 'TOKEN_LOGIT_VECTOR', 'confidence': 1,
                    'support': [case['condition_id'] for case in cases], 'off_support': 'REJECT'}
        observations = capture_native(cartridge, root, PROFILE, workload)
        assert observations == capture_native(cartridge, root, PROFILE, workload)
        affected = set()
        for case, trace in zip(cases, observations['traces']):
            expected, routes = _oracle(config, weights, case['tokens'])
            assert trace['full']['logits'][-1] == pytest.approx(expected, abs=2e-5)
            assert trace['gradient']['gradients']
            for ablation in trace['ablations']:
                if ablation['changed']:
                    affected.update(ablation['contributions'])
        assert affected == set(names)
        altered = copy.deepcopy(workload); altered['confidence'] = .95
        with pytest.raises(CassetteError):
            capture_native(cartridge, root, PROFILE, altered)


async def _client_controls(adapter, broker, cartridge, owner, identity):
    """Q5/Q31/Q76/Q77: discover actual capabilities and cancel a live streamed operation."""
    import json
    server = await adapter.listen(broker, cartridge, PROFILE, owner)
    writers = []
    async def connect(record):
        reader, writer = await asyncio.open_connection('127.0.0.1', server.sockets[0].getsockname()[1])
        writers.append(writer); writer.write(canonical_bytes(record)+b'\n'); await writer.drain()
        return reader
    try:
        discovery = await connect({'operation': 'capabilities'})
        advertised = json.loads(await asyncio.wait_for(discovery.readline(), 10))['capabilities'][0]
        assert advertised == broker.native_capability(cartridge)
        reader = await connect({'idempotency_key': 'cancel-live-stream', 'model_ref': identity, 'input': 'hello',
                                'generation': {'max_output_tokens': 8}})
        first = json.loads(await asyncio.wait_for(reader.readline(), 10))
        assert first['type'] == 'started'
        run_id = first['run_id']
        assert broker.status(run_id)['state'] not in {'SUCCEEDED', 'FAILED', 'CANCELLED'}
        control = await connect({'protocol_version': '1', 'operation': 'cancel', 'target': run_id,
                                 'idempotency_key': 'cancel-control', 'arguments': {}})
        response = json.loads(await asyncio.wait_for(control.readline(), 10))
        assert 'error' not in response or response.get('state') == 'CANCELLED', response
        rest = await asyncio.wait_for(reader.read(), 10)
        events = [json.loads(line) for line in rest.splitlines()]
        assert events[-1]['type'] == 'cancelled', events
    finally:
        for writer in writers:
            writer.close(); await writer.wait_closed()
        server.close(); await server.wait_closed()


def _false_cover_and_composition():
    """Q19: pairwise faces cannot license a triple; this implementation admits triangle composition only."""
    from compiler import _certificate
    from test_s13_pager import _fixture
    plan, certificate, evidence, profile = _fixture()
    bounds = [{name: row[name] for name in ('operation_id', 'epsilon_exec', 'delta_exec')}
              for row in certificate['execution_contract']['operations']]
    actual = _certificate(evidence, .01, 1, bounds)
    assert len(actual['compatibility']['service_faces']) == 3
    assert len(actual['compatibility']['minimal_nonfaces']) == 1
    invalid = copy.deepcopy(evidence)
    invalid['observation_contract']['selector'][2]['atom_id'] = 'atom.ab'
    with pytest.raises(CassetteError) as false_cover:
        _certificate(invalid, .01, 1, bounds)
    assert false_cover.value.code == 'CAPABILITY_MISMATCH'
    invalid = copy.deepcopy(evidence); invalid['minimal_nonface_proofs'] = []
    with pytest.raises(CassetteError):
        _certificate(invalid, .01, 1, bounds)
    hypotheses = {'centering': True, 'orthogonality': True, 'fixed_linearization': True, 'remainder_bound': '0'}
    for omitted in (None, *hypotheses):
        invalid = copy.deepcopy(evidence)
        invalid['execution_contract']['operations'][0]['loss_propagation']['quadrature'] = {
            key:value for key,value in hypotheses.items() if key != omitted}
        with pytest.raises(CassetteError):
            _certificate(invalid, .01, 1, bounds)
