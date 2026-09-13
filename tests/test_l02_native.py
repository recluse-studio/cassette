# test_l02_native.py — L02 ordinary-source graph, semantics, and durable decode proof; depends on broker.py, compiler.py, errors.py, pager.py, sources.py, store.py, tests/fixture_server.py.
"""Judge native source execution with an independent scalar model and a real scratch store."""

import asyncio
from contextlib import closing, contextmanager
import copy
import hashlib
import json
import math
import os
import struct

import pytest
from tokenizers import Tokenizer, models, pre_tokenizers

from broker import AcquisitionContext, CanonicalBroker
from compiler import _native_template, inspect_source_identity, plan_revision, render_native_input, verify_native_bundle
from errors import CassetteError
from fixture_server import source_fixture_server
from pager import NativeTransformer
from sources import SourceAdapter, transfer_state_bytes
from store import (CapacityCoordinator, canonical_bytes, commit_runtime_state, digest_bytes,
                   grant_transfer_extent, load_root, model_identity, recover_generation)

PROFILE = {"physical_bytes": 16 * 2**30, "recommended_max_working_set_bytes": 12 * 2**30,
           "execution_bytes": 0, "other_observed_bytes": 0}
WORDS = ['[UNK]', 'user', 'assistant', 'hello', 'world', '<image>', 'tool', 'weather',
         'system', 'answer', 'yes', 'no', 'red', 'blue', 'green', 'today', 'tomorrow', 'end']
TEMPLATE = "{% for message in messages %}{{ message['role'] }} {{ message['content'] }} {% endfor %}{% for tool in tools %}tool {{ tool['name'] }} {% endfor %}{% if add_generation_prompt %}assistant{% endif %}"


def _sha(payload):
    return 'sha256:' + hashlib.sha256(payload).hexdigest()


def _model(*, hidden=8, layers=2, experts=0, image=False, vocabulary_size=len(WORDS)):
    words = WORDS[:vocabulary_size]
    config = dict(architectures=['SourceDecoder'], hidden_size=hidden, vocab_size=len(words),
                  num_hidden_layers=layers, num_attention_heads=2, num_key_value_heads=1,
                  intermediate_size=12, max_position_embeddings=24, hidden_act='silu',
                  rms_norm_eps=1e-5, rope_theta=10000.0, tie_word_embeddings=False)
    weights = {}

    def add(name, shape):
        seed = int.from_bytes(hashlib.sha256(name.encode()).digest()[:4], 'little')
        values = [1.0 + .02 * math.sin(seed + i) if len(shape) == 1
                  else .2 * math.sin(seed + i * .73) for i in range(math.prod(shape))]
        values = list(struct.unpack('<' + 'f' * len(values), struct.pack('<' + 'f' * len(values), *values)))
        weights[name] = (shape, values)

    add('model.embed_tokens.weight', [len(words), hidden])
    add('model.norm.weight', [hidden]); add('lm_head.weight', [len(words), hidden])
    for layer in range(layers):
        prefix = f'model.layers.{layer}.'
        for name in ('input_layernorm', 'post_attention_layernorm'):
            add(prefix + name + '.weight', [hidden])
        for name, width in (('q', hidden), ('k', hidden // 2), ('v', hidden // 2), ('o', hidden)):
            add(prefix + f'self_attn.{name}_proj.weight', [width, hidden])
        if experts:
            config.update(num_local_experts=experts, num_experts_per_tok=2)
            add(prefix + 'block_sparse_moe.gate.weight', [experts, hidden])
            for expert in range(experts):
                for name, shape in (('w1', [12, hidden]), ('w3', [12, hidden]), ('w2', [hidden, 12])):
                    add(prefix + f'block_sparse_moe.experts.{expert}.{name}.weight', shape)
        else:
            for name, shape in (('gate', [12, hidden]), ('up', [12, hidden]), ('down', [hidden, 12])):
                add(prefix + f'mlp.{name}_proj.weight', shape)
    assets = {}
    if image:
        config.update(vision_config={'patch_size': 2, 'num_channels': 3}, image_token_index=5)
        add('vision.patch_embedding.weight', [hidden, 3, 2, 2])
        assets['preprocessor_config.json'] = dict(do_rescale=True, rescale_factor=1/255,
                                                 do_normalize=True, image_mean=[.5]*3, image_std=[.25]*3)
    tokenizer = Tokenizer(models.WordLevel(dict(zip(words, range(len(words)))), unk_token='[UNK]'))
    tokenizer.pre_tokenizer = pre_tokenizers.WhitespaceSplit()
    assets.update({'config.json': config, 'tokenizer.json': json.loads(tokenizer.to_str()),
                   'tokenizer_config.json': {'chat_template': TEMPLATE}})
    payloads = {}; assignment = {}
    for shard in range(2):
        name = f'model-{shard + 1:05d}-of-00002.safetensors'
        header = {}; payload = bytearray()
        for index, (tensor, (shape, values)) in enumerate(sorted(weights.items())):
            if index % 2 != shard:
                continue
            start = len(payload); payload.extend(struct.pack('<' + 'f' * len(values), *values))
            header[tensor] = {'dtype': 'F32', 'shape': shape, 'data_offsets': [start, len(payload)]}
            assignment[tensor] = name
        encoded = canonical_bytes(header)
        payloads[name] = len(encoded).to_bytes(8, 'little') + encoded + payload
    assets['model.safetensors.index.json'] = {'weight_map': assignment,
        'metadata': {'total_size': sum(len(values)*4 for _, values in weights.values())}}
    payloads.update({name: canonical_bytes(value) for name, value in assets.items()})
    return config, weights, dict(sorted(payloads.items()))


@contextmanager
def _case(tmp_path, label, **geometry):
    config, weights, payloads = _model(**geometry)
    cartridge = tmp_path / label; cartridge.mkdir()
    owner = CapacityCoordinator(cartridge)
    source = {'source_kind': 'huggingface', 'source_alias': 'fixture/huggingface-model@main',
              'locator': 'fixture/huggingface-model', 'requested_revision': 'main',
              'immutable_revision': 'git-sha1:' + '1'*40, 'identity': 'blake3:' + '0'*64,
              'license_digest': _sha(b'hf-license'),
              'artifacts': [{'path': name, 'size': len(payload), 'digest': _sha(payload)}
                            for name, payload in payloads.items()]}
    fds = []; inspection = {}; transfers = {}
    try:
        for index, (name, payload) in enumerate(payloads.items()):
            extent = grant_transfer_extent(cartridge, 'source-identity', f'asset-{index}', len(payload), capacity_controller=owner)
            fds.append(extent.fd); os.pwrite(extent.fd, payload, 0)
            inspection[name] = dict(fd=extent.fd, offset=0, length=len(payload), operation_id='source-identity')
            pair = tuple(grant_transfer_extent(cartridge, 'acquire', f'{kind}-{index}', size, capacity_controller=owner)
                         for kind, size in (('bytes', len(payload)), ('state', transfer_state_bytes(len(payload)))))
            fds.extend(item.fd for item in pair); transfers[name] = pair
        material = inspect_source_identity(source, inspection, cartridge)
        source['identity'] = model_identity(material)
        artifacts = tuple((name, payload, '"native-v1"') for name, payload in payloads.items() if name.endswith('.safetensors'))
        semantics = tuple((name, payload, '"native-v1"') for name, payload in payloads.items() if name.endswith('.json'))
        with source_fixture_server(artifact_overrides={'huggingface': artifacts},
                                  semantic_overrides={'huggingface': semantics},
                                  identity_overrides={'huggingface': source['identity']}) as server:
            adapter = SourceAdapter('huggingface', server.base_url, lambda _: 's09-fixture-secret-never-serialize')
            descriptor = dict(kind='huggingface', locator=source['locator'], revision='main',
                              credential_ref='keychain:l02', license_acceptance_ref='license:l02',
                              expected_identity=source['identity'])
            request = _request('prepare', label, source['identity'], {'source': descriptor})
            with closing(CanonicalBroker(cartridge / 'operations')) as broker:
                context = AcquisitionContext(adapter, owner, transfers, cartridge)
                result = asyncio.run(broker.run_acquisition(request, context))
                assert result['state'] == 'SUCCEEDED', result
                root = broker.callable_revision(result['operation_id'], cartridge).root_digest
                if label == 'dense':
                    wrong_descriptor = {**descriptor, 'expected_identity': 'blake3:' + 'f'*64}
                    wrong = _request('prepare', label + '-wrong-identity', source['identity'], {'source': wrong_descriptor})
                    rejected = asyncio.run(broker.run_acquisition(wrong, context))
                    assert rejected['state'] == 'FAILED'
                    assert rejected['error']['code'] == 'IDENTITY_MISMATCH'
                    phases = [event['payload']['phase'] for event in broker.events(rejected['operation_id'])
                              if 'phase' in event['payload']]
                    assert phases[-1] == 'SOURCE_VERIFIED'
                    assert recover_generation(cartridge).root_digest == root
            requested_paths = {row['path'].split('/')[-1] for row in server.requests if row['range']}
            assert requested_paths == set(payloads)
        yield cartridge, owner, root, config, weights, payloads, source, inspection
    finally:
        for descriptor in fds:
            os.close(descriptor)


@contextmanager
def _changed_asset(source, extents, name, mutate):
    """Change only scratch acquisition bytes and their source lock, then restore the fixture."""
    source = copy.deepcopy(source); extents = {key: dict(value) for key, value in extents.items()}
    fd = extents[name]['fd']; original = os.pread(fd, extents[name]['length'], 0)
    document = json.loads(original); mutate(document); payload = canonical_bytes(document)
    os.ftruncate(fd, len(payload)); os.pwrite(fd, payload, 0)
    extents[name]['length'] = len(payload)
    for item in source['artifacts']:
        if item['path'] == name:
            item.update(size=len(payload), digest=_sha(payload))
    try:
        yield source, extents
    finally:
        os.ftruncate(fd, len(original)); os.pwrite(fd, original, 0)


def _request(operation, key, target, arguments):
    return dict(protocol_version='1', operation=operation, idempotency_key=key, target=target, arguments=arguments)


def _oracle(config, weights, tokens, pixels=None):
    """Recompute the entire prefix using scalar sums; no product graph or MLX oracle."""
    def linear(row, name):
        shape, values = weights[name]
        return [sum(a*b for a, b in zip(row, values[i*shape[1]:(i+1)*shape[1]])) for i in range(shape[0])]
    def norm(row, name):
        scale = (sum(x*x for x in row)/len(row) + config['rms_norm_eps'])**-.5
        return [x*scale*w for x, w in zip(row, weights[name][1])]
    def softmax(row):
        values = [math.exp(x-max(row)) for x in row]
        return [x/sum(values) for x in values]
    def silu(x):
        return x/(1+math.exp(-x))
    h = config['hidden_size']; dim = h//2
    embedding = weights['model.embed_tokens.weight'][1]
    rows = [embedding[token*h:(token+1)*h] for token in tokens]
    if pixels is not None:
        patches = []
        values = weights['vision.patch_embedding.weight'][1]
        for y in range(0, len(pixels[0]), 2):
            for x in range(0, len(pixels[0][0]), 2):
                patches.append([sum(((pixels[0][y+dy][x+dx][channel]/255-.5)/.25) * values[out*12+channel*4+dy*2+dx]
                                    for channel in range(3) for dy in range(2) for dx in range(2)) for out in range(h)])
        index = tokens.index(5); rows[index:index+1] = patches
    routes = []
    for layer in range(config['num_hidden_layers']):
        prefix = f'model.layers.{layer}.'
        normalized = [norm(row, prefix+'input_layernorm.weight') for row in rows]
        qs = [linear(row, prefix+'self_attn.q_proj.weight') for row in normalized]
        ks = [linear(row, prefix+'self_attn.k_proj.weight') for row in normalized]
        vs = [linear(row, prefix+'self_attn.v_proj.weight') for row in normalized]
        def rotate(row, position):
            out = list(row)
            for start in range(0, len(row), dim):
                for i in range(dim//2):
                    angle = position/config['rope_theta']**(2*i/dim)
                    a, b = row[start+i], row[start+i+dim//2]
                    out[start+i] = a*math.cos(angle)-b*math.sin(angle)
                    out[start+i+dim//2] = b*math.cos(angle)+a*math.sin(angle)
            return out
        qs = [rotate(row, i) for i, row in enumerate(qs)]
        ks = [rotate(row, i) for i, row in enumerate(ks)]
        residuals = []
        for t, query in enumerate(qs):
            attended = []
            for head in range(2):
                scores = softmax([sum(a*b for a,b in zip(query[head*dim:(head+1)*dim], ks[j]))/math.sqrt(dim) for j in range(t+1)])
                attended.extend(sum(scores[j]*vs[j][i] for j in range(t+1)) for i in range(dim))
            residuals.append([a+b for a,b in zip(rows[t], linear(attended, prefix+'self_attn.o_proj.weight'))])
        rows = []
        for row in residuals:
            value = norm(row, prefix+'post_attention_layernorm.weight')
            if config.get('num_local_experts'):
                probabilities = softmax(linear(value, prefix+'block_sparse_moe.gate.weight'))
                chosen = sorted(range(len(probabilities)), key=lambda i: -probabilities[i])[:2]
                routes.extend(chosen)
                all_outputs = []
                for expert in range(config['num_local_experts']):
                    name = prefix+f'block_sparse_moe.experts.{expert}.'
                    gated = [silu(a)*b for a,b in zip(linear(value, name+'w1.weight'), linear(value, name+'w3.weight'))]
                    all_outputs.append(linear(gated, name+'w2.weight'))
                delta = [sum(probabilities[e]*all_outputs[e][i] for e in chosen)/sum(probabilities[e] for e in chosen) for i in range(h)]
            else:
                gated = [silu(a)*b for a,b in zip(linear(value, prefix+'mlp.gate_proj.weight'), linear(value, prefix+'mlp.up_proj.weight'))]
                delta = linear(gated, prefix+'mlp.down_proj.weight')
            rows.append([a+b for a,b in zip(row, delta)])
    return linear(norm(rows[-1], 'model.norm.weight'), 'lm_head.weight'), routes


def test_q1_q9_q10_q20_q30_q33_q47_q55_q58_q63_q66_l02_native_source_and_state(tmp_path):
    """Q1/Q9/Q10/Q20/Q30/Q33/Q47/Q55/Q58/Q63/Q66: exact source semantics, graph, memory refusal and restart."""
    contained = _native_template("{{ messages|tojson }}")
    assert json.loads(contained.render(messages=[{'role': 'user', 'content': 'hello'}])) == [{'role': 'user', 'content': 'hello'}]
    for template in (
        "{% for a in messages[0]['content'] %}{% for b in messages[0]['content'] %}{% endfor %}{% endfor %}",
        "{{ messages[0]['content']|replace('x', 'xxxxxxxx') }}",
        "{% set x = 'x' %}" + "{% set x = [x, x] %}"*14 + "{{ x|tojson }}",
    ):
        with pytest.raises(CassetteError) as contained_error:
            list(_native_template(template).generate(messages=[{'content': 'x'*128}], tools=[]))
        assert contained_error.value.code == 'CONTAINMENT_REJECTED'
    for label, geometry in [('dense', {}), ('wider', {'hidden': 12, 'layers': 3}),
                            ('sparse', {'experts': 4}), ('image', {'image': True})]:
        with _case(tmp_path, label, **geometry) as (cartridge, owner, root, config, weights, payloads, source, extents):
            print('L02 source acquired:', label, flush=True)
            if label == 'dense':
                for asset, mutate, expected in (
                    ('model.safetensors.index.json', lambda doc: doc['weight_map'].pop(next(iter(doc['weight_map']))), 'METADATA_INSUFFICIENT'),
                    ('config.json', lambda doc: doc.update(hidden_act='unregistered'), 'UNSUPPORTED_OPERATOR'),
                    ('tokenizer_config.json', lambda doc: doc.update(chat_template='{{ range(100) }}'), 'CONTAINMENT_REJECTED'),
                ):
                    with _changed_asset(source, extents, asset, mutate) as (altered_source, altered_extents):
                        with pytest.raises(CassetteError) as refused:
                            plan_revision(altered_source, altered_extents, cartridge)
                        assert refused.value.code == expected
                for asset, mutate in (
                    ('tokenizer_config.json', lambda doc: doc.update(chat_template=doc['chat_template']+' end')),
                    ('tokenizer.json', lambda doc: doc['model']['vocab'].update(hello=4, world=3)),
                ):
                    with _changed_asset(source, extents, asset, mutate) as (altered_source, altered_extents):
                        assert model_identity(inspect_source_identity(altered_source, altered_extents, cartridge)) != source['identity']
                history = [{'role': 'system', 'content': 'answer'}, {'role': 'assistant', 'content': 'weather'},
                           {'role': 'tool', 'content': 'today'}, {'role': 'user', 'content': 'hello'}]
                rendered_history = render_native_input(cartridge, root, history, [{'name': 'weather'}])
                expected_history = 'system answer assistant weather tool today user hello tool weather assistant'
                assert rendered_history['rendered'] == expected_history
                assert rendered_history['token_ids'] == [WORDS.index(word) for word in expected_history.split()]
            graph = verify_native_bundle(cartridge, root)
            assert set(graph['contributions']) == set(weights)
            assert graph['layers'] == config['num_hidden_layers'] and graph['hidden_size'] != 4
            messages = [{'role': 'user', 'content': 'hello <image>' if label == 'image' else 'hello world'}]
            tools = [{'name': 'weather'}]
            rendered = render_native_input(cartridge, root, messages, tools)
            expected_text = 'user ' + messages[0]['content'] + ' tool weather assistant'
            assert rendered['rendered'] == expected_text
            tokens = [WORDS.index(word) for word in expected_text.split()]
            assert rendered['token_ids'] == tokens
            pixels = [[[[float((y*70+x*20+c*40)%256) for c in range(3)] for x in range(4)] for y in range(2)]] if label == 'image' else None
            session = 'op-' + hashlib.sha256(label.encode()).hexdigest()
            request_digest = digest_bytes(label.encode())
            state_root = root; prefix = list(tokens); observed_routes = set()
            steps = 3 if label == 'dense' else 1
            for step in range(steps):
                runtime = NativeTransformer(cartridge, state_root, PROFILE, session, request_digest)
                assert len(runtime.state['generated_tokens']) == step
                if step:
                    assert runtime.state['position'] == len(prefix)-1 + (1 if pixels is not None else 0)
                    assert runtime.kv and sum(value.nbytes for pair in runtime.kv.values() for value in pair) > 0
                candidate = runtime.step(tokens, seed=17, pixels=pixels)
                expected_logits, routes = _oracle(config, weights, prefix, pixels)
                assert candidate['logits'] == pytest.approx(expected_logits, abs=2e-5, rel=2e-5)
                assert candidate['token'] == max(range(len(expected_logits)), key=expected_logits.__getitem__)
                observed_routes.update(e for row in candidate['routes'] for chosen in row['experts'] for e in chosen)
                assert candidate['executed_nodes'] == [row['id'] for row in graph['nodes']]
                pin = commit_runtime_state(cartridge, state_root, session, candidate['payload'], capacity_controller=owner)
                state_root = pin.root_digest; prefix.append(candidate['token'])
            if label == 'sparse':
                assert len(observed_routes) >= 3, observed_routes
            if pixels is not None:
                changed = copy.deepcopy(pixels); changed[0][0][0][0] += 100
                altered = NativeTransformer(cartridge, root, PROFILE, 'image-control', request_digest).step(tokens, seed=17, pixels=changed)
                assert altered['logits'] != pytest.approx(_oracle(config, weights, tokens, pixels)[0], abs=1e-5)
            with pytest.raises(CassetteError) as mismatch:
                NativeTransformer(cartridge, state_root, PROFILE, session, digest_bytes(b'other-request'))
            assert mismatch.value.code == 'ROOT_INVALID'
            with pytest.raises(CassetteError) as memory:
                NativeTransformer(cartridge, root, {**PROFILE, 'other_observed_bytes': 12*2**30}, session, request_digest)
            assert memory.value.code == 'MEMORY_BUDGET_EXCEEDED'
            # A second product entry starts from the currently published model, then commits its own context.
            arguments = dict(messages=messages, tools=tools, seed=17, temperature=0.0, max_tokens=steps)
            if pixels is not None:
                arguments['pixels'] = pixels
            request = _request('run', label+'-broker', load_root(cartridge, root)['identity'], arguments)
            if label == 'dense':
                async def interrupt(broker):
                    task = asyncio.create_task(broker.generate_native(request, cartridge, PROFILE, owner))
                    operation_id = broker.operation_id(request)
                    for _ in range(30000):
                        await asyncio.sleep(.002)
                        if task.done():
                            pytest.fail('generation completed before the pause observer saw a committed token')
                        if any('token_index' in event['payload'] for event in broker.events(operation_id)):
                            broker.pause(operation_id)
                            return await task
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
                    pytest.fail('no committed-token event reached the pause observer')
                with closing(CanonicalBroker(cartridge / 'operations')) as broker:
                    paused = asyncio.run(interrupt(broker))
                    assert paused['state'] == 'PAUSED', paused
                committed = recover_generation(cartridge)
                restored = NativeTransformer(cartridge, committed.root_digest, PROFILE,
                    paused['operation_id'], digest_bytes(canonical_bytes(request)))
                assert 0 < len(restored.state['generated_tokens']) < 3
                assert restored.state['position'] >= len(tokens)
                with closing(CanonicalBroker(cartridge / 'operations')) as broker:
                    broker.resume(paused['operation_id'])
            with closing(CanonicalBroker(cartridge / 'operations')) as broker:
                result = asyncio.run(broker.generate_native(request, cartridge, PROFILE, owner))
                assert result['state'] == 'SUCCEEDED', result
                assert result['result']['tokens'] == prefix[len(tokens):]
            with closing(CanonicalBroker(cartridge / 'operations')) as broker:
                assert asyncio.run(broker.generate_native(request, cartridge, PROFILE, owner)) == result
            if label == 'dense':
                requests = [_request('run', 'concurrent-'+key, request['target'], {**arguments, 'max_tokens': 1}) for key in ('a', 'b')]
                async def concurrent(broker):
                    return await asyncio.gather(*(broker.generate_native(item, cartridge, PROFILE, owner) for item in requests))
                with closing(CanonicalBroker(cartridge / 'operations')) as broker:
                    results = asyncio.run(concurrent(broker))
                    assert all(item['state'] == 'SUCCEEDED' for item in results), results
                    current_maps = load_root(cartridge, recover_generation(cartridge).root_digest)['tensor_maps']
                    assert {'state.'+broker.operation_id(item) for item in requests} <= {item['semantic_tensor_id'] for item in current_maps}
            if label == 'image':
                with _changed_asset(source, extents, 'preprocessor_config.json', lambda doc: doc.update(do_resize=True)) as (altered_source, altered_extents):
                    with pytest.raises(CassetteError) as processor_error:
                        plan_revision(altered_source, altered_extents, cartridge)
                    assert processor_error.value.code == 'UNSUPPORTED_OPERATOR'
            print('L02 verified:', label, 'layers', graph['layers'], 'tokens', result['result']['tokens'], 'routes', sorted(observed_routes), flush=True)
            # Altering a verified semantic byte must fail before a preparation plan can be issued.
            descriptor = extents['tokenizer_config.json']['fd']
            original = os.pread(descriptor, 1, 0); os.pwrite(descriptor, b'!', 0)
            try:
                with pytest.raises(CassetteError) as changed:
                    plan_revision(source, extents, cartridge)
                assert changed.value.code == 'SOURCE_REVISION_CHANGED'
            finally:
                os.pwrite(descriptor, original, 0)
