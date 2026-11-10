# test_l04_campaign.py — L04 evidence integrity, ownership, graph reachability and measurement boundaries; depends on tools/campaign.py, store.py, errors.py, broker.py, pager.py, trainer.py, tests/test_l02_native.py, tests/test_s22_trainer.py, tests/fixture_server.py.
"""Exercise campaign controls on real scratch storage with independent expected outcomes."""
import asyncio
from contextlib import closing, ExitStack
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

import pytest
from errors import CassetteError
from store import (
    CapacityCoordinator,
    CapacityTransition,
    await_extent_io,
    campaign_head,
    compare_campaign_head,
    complete_capacity_claim,
    digest_bytes,
    execute_claimed_write,
    grant_profile_extents,
    reclaim_profile_extents,
    seal_profile_extents,
    storage_counter_snapshot,
)
from broker import CanonicalBroker
import tools.campaign as campaign


def test_q80_q44_evidence_ownership_graph_and_replay(tmp_path):
    """Q80/Q44/Q60: exact namespaces, atomic lease succession and transitive evidence invalidation."""
    root = tmp_path / 'evidence'; root.mkdir()
    (root / 'raw').write_bytes(b'actual output')
    seal = campaign.seal_namespace(root, {'attempt': 1})
    assert campaign.verify_namespace(root, seal) == seal['digest']
    for fault in ('extra', 'missing', 'symlink', 'hardlink', 'fifo'):
        if fault == 'missing': (root / 'raw').rename(root / 'renamed')
        elif fault == 'symlink': (root / 'extra').symlink_to(root / 'raw')
        elif fault == 'hardlink': os.link(root / 'raw', root / 'extra')
        elif fault == 'fifo': os.mkfifo(root / 'extra')
        else: (root / 'extra').write_bytes(b'foreign')
        with pytest.raises(CassetteError): campaign.verify_namespace(root, seal)
        if fault == 'missing': (root / 'renamed').rename(root / 'raw')
        else: (root / 'extra').unlink()
    failed = campaign.seal_namespace(root, {}, missing=['stderr'])
    with pytest.raises(CassetteError): campaign.verify_namespace(root, failed)
    control = tmp_path / 'control'; control.mkdir(); owner = CapacityCoordinator(control)
    manifest = {'candidate':{'parent':'a'*40,'tree':'b'*40}, 'assertions':{'Q80':'INTEGRATION'}}
    history = campaign.ReviewHistory(owner, 'L04', 1, campaign.identity(manifest), manifest=manifest)
    first = history.acquire('one', None, now=100, expires=110, worktree=tmp_path)
    with pytest.raises(CassetteError): history.acquire('two', first['digest'], now=101, expires=111, worktree=tmp_path)
    with pytest.raises(CassetteError): history.acquire('two', None, now=111, expires=120, worktree=tmp_path)
    successor = history.acquire('two', first['digest'], now=111, expires=120, worktree=tmp_path)
    with pytest.raises(CassetteError): history.append('one', successor['digest'], {}, now=112)
    with pytest.raises(CassetteError):
        history.append('two', successor['digest'], {'binding': history.binding, 'status': 'REMEDIATED'}, now=112)
    with pytest.raises(CassetteError):
        history.append('two', successor['digest'], {'binding':history.binding,'status':'PASS_READY'}, now=112)
    mutation = tmp_path/'mutation.log'; mutation.write_text('detected changed namespace')
    envelope = {'review_id':'review-1','binding':history.binding,'status':'PASS_READY','previous':None,
                'candidate':manifest['candidate'], 'assertions':[{'assertion':'Q80','status':'PASS','level':'INTEGRATION',
                    'predicate':'exact namespace','source_trace':'tools/campaign.py:verify_namespace',
                    'challenge':'substitute artifact','expected':'rejected','observed':'rejected',
                    'evidence':['replay'],'discriminator':'mutation'}],
                'evidence':{'replay':{'path':str(root/'raw'),'digest':campaign.file_digest(root/'raw'),
                                     'command':['verify_namespace'],'exit_code':0},
                            'mutation':{'path':str(mutation),'digest':campaign.file_digest(mutation),
                                        'command':['verify_substitution'],'exit_code':1}},
                'findings':[],'remediation':None,'invalidation':{'class':'replay_only','ids':[],'operation_lineages':[],'qualification_lineages':[]}}
    for fault in ('missing_claim','wrong_candidate','wrong_digest','no_discriminator','false_value'):
        bad = copy.deepcopy(envelope)
        if fault == 'missing_claim': bad['assertions'] = []
        if fault == 'wrong_candidate': bad['candidate']['tree'] = 'c'*40
        if fault == 'wrong_digest': bad['evidence']['replay']['digest'] = campaign.identity('other')
        if fault == 'no_discriminator': bad['evidence']['mutation']['exit_code'] = 0
        if fault == 'false_value': bad['assertions'][0]['observed'] = 'accepted'
        with pytest.raises(CassetteError): history.append('two',successor['digest'],bad,now=112)
    terminal = history.append('two', successor['digest'], envelope, now=112)
    with pytest.raises(CassetteError): history.release('two',terminal['digest'],now=113)
    with pytest.raises(CassetteError): history.release('two',terminal['digest'],now=1)
    with pytest.raises(CassetteError): history.append('two', terminal['digest'], {'binding': history.binding, 'status': 'REMEDIATED'}, now=113)
    assert campaign_head(control, history.key)['previous'] == successor['digest']
    def node(key, depends, level, owners=()):
        return {'id':key, 'depends':depends, 'evidence_level':level, 'matrix_assertion_owners':list(owners),
                'owner_stage':'L04', 'permission':'READ_ONLY'}
    nodes = [node('a', [], 'LIVE', ['Q80']), node('b', ['a'], 'INTEGRATION'), node('c', ['b'], 'LIVE')]
    graph = campaign.validate_graph(nodes, required_owners={'Q80':['a']})
    assert graph['order'] == ['a', 'b', 'c']
    assert campaign.descendants(graph, ['a']) == ['a', 'b', 'c']
    replay = campaign.clean_replay(graph, ['a','c'])
    assert replay[1]['depends'] == ['Q80-a']
    assert replay[0]['operation_id'] != campaign.clean_replay(graph, ['a'])[0]['operation_id']
    with pytest.raises(CassetteError): campaign.invalidate(graph, ['a'], ['a', 'c'])
    assert campaign.invalidate(graph, ['a'], ['a','b','c'])['invalidated'] == ['a','b','c']
    head = campaign.publish_graph(owner,graph)
    successor_graph = campaign.validate_graph([*nodes,node('d',['c'],'PLATFORM')],required_owners={'Q80':['a']},parent=graph,materializer='a')
    campaign.publish_graph(owner,successor_graph,head['digest'])
    with pytest.raises(CassetteError): campaign.invalidate_latest(owner,graph['revision_digest'],['a'],['a','b','c'])
    assert campaign.invalidate_latest(owner,graph['revision_digest'],['a'],['a','b','c','d'])['invalidated'] == ['a','b','c','d']
    for alteration in ('cycle', 'missing', 'owner', 'duplicate', 'inherited', 'permission', 'unapproved_write', 'unresolved_card'):
        changed = copy.deepcopy(nodes)
        if alteration == 'unresolved_card':
            changed[0].update(permission='CAMPAIGN_DIRECTORY_WRITE',approved_card_digest=campaign.identity('absent-card'))
        if alteration == 'permission': changed[0]['permission'] = 'UNDECLARED_PERMISSION'
        if alteration == 'unapproved_write': changed[0]['permission'] = 'CAMPAIGN_DIRECTORY_WRITE'
        if alteration == 'cycle': changed[0]['depends'] = ['c']
        if alteration == 'missing': changed[2]['depends'] = ['absent']
        if alteration == 'owner': changed[0]['matrix_assertion_owners'] = []
        if alteration == 'duplicate': changed.append(changed[0])
        if alteration == 'inherited': changed[1]['evidence_level'] = 'PLATFORM'
        with pytest.raises(CassetteError):
            campaign.validate_graph(changed, required_owners={'Q80':['a']}, parent=graph, materializer='a')
    assert campaign.coverage(['atom1', 'atom2'], ['atom1'])['status'] == 'NOT_RUN'
    assert campaign.coverage(['atom1', 'atom2'], ['atom2','atom1'])['status'] == 'PASS'


def test_q41_q43_q47_q48_q74_q79_inventory_and_measurements(tmp_path):
    """Q41/Q43/Q47/Q48/Q74/Q79: resumable inventory, aligned collectors and unchanged thermal bounds."""
    (tmp_path/'protected').mkdir(); (tmp_path/'protected'/'private-name').write_bytes(b'12345')
    (tmp_path/'.volatile').mkdir(); (tmp_path/'.volatile'/'cache').write_bytes(b'ignore')
    result = campaign.inventory_step(tmp_path, excluded=['.volatile'], limit=1)
    assert result['status'] == 'NOT_RUN'
    result = campaign.inventory_step(tmp_path, excluded=['.volatile'], checkpoint=result['checkpoint'], limit=1)
    assert result['inventory'] == {'protected': {'type':'directory', 'logical_bytes':5}}
    assert 'private-name' not in json.dumps(result['inventory'])
    (tmp_path/'protected'/'private-name').write_bytes(b'123456')
    other = campaign.inventory_step(tmp_path, excluded=['.volatile'])
    with pytest.raises(CassetteError): campaign.compare_inventory(result['inventory'], other['inventory'])
    binding = {'operation':'one'}
    required = {kind:list(campaign.COLLECTORS[kind]) for kind in ['memory','power','network','writes']}
    samples = [{'binding':binding,'collector':kind,'start':start,'end':start+1,
                'values':dict.fromkeys(fields,1),'before':dict.fromkeys(fields,1)}
               for kind,fields in required.items() for start in [0,1]]
    assert campaign.interval_evidence(binding,0,2,samples,required)['status'] == 'PASS'
    with pytest.raises(CassetteError): campaign.interval_evidence(binding,0,2,samples[:-1],required)
    changed = copy.deepcopy(samples); changed[1]['binding'] = {'operation':'other'}
    with pytest.raises(CassetteError): campaign.interval_evidence(binding,0,2,changed,required)
    for value in (-1, True, float('nan'), float('inf'), None, '1', .5):
        changed = copy.deepcopy(samples)
        changed[-1]['values']['device_write_bytes'] = value
        with pytest.raises(CassetteError): campaign.interval_evidence(binding,0,2,changed,required)
    changed = copy.deepcopy(samples); changed[-1]['values']['binding'] = {'operation':'foreign'}
    with pytest.raises(CassetteError): campaign.interval_evidence(binding,0,2,changed,required)
    changed = copy.deepcopy(samples); changed[-1]['before']['device_write_bytes'] = 2
    with pytest.raises(CassetteError): campaign.interval_evidence(binding,0,2,changed,required)
    binding = dict.fromkeys(['drive','host','path','operation','plan'], 'exact')
    patterns = [{'read_bytes':100,'write_bytes':100},{'read_bytes':200,'write_bytes':0}]
    observations = [{'binding':binding,'pattern':p,'duration_seconds':t,'errors':0,'readback_ok':True,
                     'flush_ok':True,'host_write_bytes':p['write_bytes'],'device_write_bytes':p['write_bytes'],
                     'read_seconds':t/3,'write_seconds':t/3,'flush_seconds':t/3}
                    for p,t in zip(patterns,[1,2])]
    profile = campaign.storage_profile(binding,patterns,observations,expected_binding=binding)
    assert profile['latency_seconds']['0.5'] == 1
    assert profile['throughput_bytes_per_second']['0.05'] == 100
    for field, value in [('duration_seconds',True),('duration_seconds',float('nan')),('duration_seconds',5e-324),
                         ('device_write_bytes',-1),('device_write_bytes',.5),('host_write_bytes',True),
                         ('read_seconds',None),('write_seconds',None),('flush_seconds',None),
                         ('errors',False),('readback_ok',1),('flush_ok',1)]:
        changed = copy.deepcopy(observations); changed[0][field] = value
        with pytest.raises(CassetteError): campaign.storage_profile(binding,patterns,changed,expected_binding=binding)
    observations[0]['device_write_bytes'] = None
    with pytest.raises(CassetteError): campaign.storage_profile(binding,patterns,observations,expected_binding=binding)
    windows = [{'start':i*300,'end':(i+1)*300,'integrity_errors':0,'critical_thermal_seconds':0,
                'q68_pass':True,'q74_pass':True,'host_write_bytes':100,'tokens':1000,'rd_p05':100,
                'duty':.4,'binding':'thermal-fixture','bs_bytes_per_second':100,'bm_proxy_bytes_per_second':1000,
                'power_watts':20,'device_write_bytes':100} for i in range(24)]
    assert campaign.thermal_windows(windows, slc_bytes=1000,training=True,warmup_end=0,knee_duty=.5,duty_experiments=[{'duty':.6,'sustained':False},{'duty':.4,'sustained':True}],binding='thermal-fixture',recovery_end=0)['duration_seconds'] == 7200
    thermal_args = dict(slc_bytes=1000,training=True,warmup_end=0,knee_duty=.5,
                        duty_experiments=[{'duty':.6,'sustained':False},{'duty':.4,'sustained':True}],
                        binding='thermal-fixture',recovery_end=0)
    for field in ('start','end','critical_thermal_seconds','host_write_bytes','device_write_bytes','tokens',
                  'integrity_errors','power_watts','rd_p05','duty'):
        for value in (-1,True,float('nan'),float('inf'),None):
            trace = copy.deepcopy(windows); trace[0][field] = value
            with pytest.raises(CassetteError): campaign.thermal_windows(trace,**thermal_args)
    for field in ('q68_pass','q74_pass'):
        trace = copy.deepcopy(windows); trace[0][field] = 1
        with pytest.raises(CassetteError): campaign.thermal_windows(trace,**thermal_args)
    for field,value in [('slc_bytes',True),('slc_bytes',.5),('training',1),('warmup_end',float('nan')),
                        ('recovery_end',True),('knee_duty',True)]:
        with pytest.raises(CassetteError): campaign.thermal_windows(windows,**{**thermal_args,field:value})
    for change in ('duration','cache','gap','decay','endurance'):
        trace = copy.deepcopy(windows)
        if change == 'duration': trace.pop()
        if change == 'cache':
            for window in trace: window['host_write_bytes'] = 1
        if change == 'gap': trace[2]['start'] += 1
        if change == 'decay': trace[-1]['rd_p05'] = 89
        if change == 'endurance': trace[-1]['q74_pass'] = False
        with pytest.raises(CassetteError): campaign.thermal_windows(trace,slc_bytes=1000,training=True,warmup_end=0,knee_duty=.5,duty_experiments=[{'duty':.6,'sustained':False},{'duty':.4,'sustained':True}],binding='thermal-fixture',recovery_end=0)


@pytest.mark.parametrize("kind", ["run", "train", "prepare"])
def test_q5_q25_real_kill_and_boundary_recovery(tmp_path, kind):
    """Q5/Q25: kill acquisition, generation or training at its first durable boundary and recover without repeating work."""
    from test_l02_native import _case, PROFILE
    from store import load_root, recover_generation
    from pager import NativeTransformer
    with _case(tmp_path, 'hold', hidden=8, layers=1) as (cartridge, owner, root, config, weights, payloads, source, _), ExitStack() as contexts:
        log = cartridge / 'operations'
        request = {'protocol_version':'1','operation':'run','idempotency_key':'l04-native-hold',
                   'target':load_root(cartridge,root)['identity'],
                   'arguments':{'messages':[{'role':'user','content':'hello world'}], 'tools':[],
                                'seed':17,'temperature':0.0,'max_tokens':2}}
        boundary, method, source_arguments = 'runtime-commit', 'generate_native', {}
        if kind == 'train':
            from trainer import prepare_native_training, native_training_state
            from test_s22_trainer import _profile
            runtime = NativeTransformer(cartridge, root, PROFILE, 'training-setup', 'blake3:'+'0'*64)
            adapters = {'lm_head.weight': {'a': [[.01]*8], 'b': [[.01]]*config['vocab_size'], 'scale':1.0}}
            batch = campaign.canonical_bytes({'sequence':{'tokens':[1,3,4,2],'mask':[0,0,1,1]}})
            checkpoint, manifest = prepare_native_training(cartridge, root, 'ADAPTER_SFT', adapters, (batch,batch),
                epochs=1,learning_rate=.1,precision='FP32',seed=17,window_limit_bytes=4096,reference_root=None,beta=.1,
                capacity_controller=owner,resource_profile=_profile(),memory_peak_bytes=runtime.declared_peak_bytes*8)
            request = {**request,'operation':'train','idempotency_key':'l04-training-hold',
                       'arguments':{'checkpoint_root':checkpoint,'manifest_digest':manifest}}
            boundary, method = 'training-checkpoint', 'train_native'
        if kind == 'prepare':
            from fixture_server import source_fixture_server
            artifacts = tuple((name,payload,'"native-v1"') for name,payload in payloads.items() if name.endswith('.safetensors'))
            semantics = tuple((name,payload,'"native-v1"') for name,payload in payloads.items() if name.endswith('.json'))
            server = contexts.enter_context(source_fixture_server(artifact_overrides={'huggingface':artifacts},
                semantic_overrides={'huggingface':semantics},identity_overrides={'huggingface':source['identity']}))
            request = {**request,'operation':'prepare','idempotency_key':'l04-source-hold',
                'arguments':{'source':{'kind':'huggingface','locator':source['locator'],'revision':'main',
                    'credential_ref':'keychain:l04','license_acceptance_ref':'license:l04','expected_identity':source['identity']}}}
            boundary, method = 'source-checkpoint', 'run_acquisition'
            source_arguments = {'url':server.base_url,'artifacts':source['artifacts']}
        with closing(CanonicalBroker(log)) as broker:
            operation = broker.issue(request); op = operation['operation_id']
            broker.request_hold(op, boundary)
        script = """import asyncio,json,sys
from contextlib import closing, ExitStack
from broker import CanonicalBroker
from store import CapacityCoordinator
async def main():
 owner=CapacityCoordinator(sys.argv[2])
 with closing(CanonicalBroker(sys.argv[1])) as broker:
  if sys.argv[5]=='run_acquisition':
   import os
   from broker import AcquisitionContext
   from sources import SourceAdapter,transfer_state_bytes
   from store import grant_transfer_extent
   inputs=json.loads(sys.argv[6]); transfers={}; fds=[]
   try:
    for index,artifact in enumerate(inputs['artifacts']):
     extents=tuple(grant_transfer_extent(sys.argv[2],'l04-source',f'{kind}-{index}',size,capacity_controller=owner)
       for kind,size in [('bytes',artifact['size']),('state',transfer_state_bytes(artifact['size']))])
     transfers[artifact['path']]=extents; fds.extend(item.fd for item in extents)
    adapter=SourceAdapter('huggingface',inputs['url'],lambda _: 's09-fixture-secret-never-serialize')
    result=await broker.run_acquisition(json.loads(sys.argv[3]),AcquisitionContext(adapter,owner,transfers,sys.argv[2]))
   finally:
    for fd in fds: os.close(fd)
  else:
   result=await getattr(broker,sys.argv[5])(json.loads(sys.argv[3]),sys.argv[2],json.loads(sys.argv[4]),owner)
  print(json.dumps(result))
asyncio.run(main())
"""
        command = [sys.executable,'-c',script,str(log),str(cartridge),json.dumps(request),json.dumps(PROFILE),method,json.dumps(source_arguments)]
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic()+30
            acknowledged = False
            while time.monotonic()<deadline:
                for path in log.glob('*.json'):
                    record = json.loads(path.read_text()).get('record', {})
                    if record.get('operation_id') == op and any(e['payload'].get('hold') == 'ACKNOWLEDGED' for e in record.get('events',[])):
                        acknowledged = True
                        break
                if acknowledged or process.poll() is not None: break
                time.sleep(.02)
            assert acknowledged, process.communicate(timeout=1) if process.poll() is not None else 'native hold not reached'
            first = recover_generation(cartridge)
            time.sleep(.05)
            assert recover_generation(cartridge) == first
            assert process.poll() is None
            process.kill(); process.wait(timeout=5)
            if kind == 'run':
                runtime = NativeTransformer(cartridge,first.root_digest,PROFILE,op,campaign.identity(request))
                assert len(runtime.state['generated_tokens']) == 1
            elif kind == 'train':
                held = record['checkpoint']
                state = native_training_state(cartridge,held['checkpoint_root'],held['manifest_digest'])
                assert len(state['losses']) == 1 and not state['complete']
            with closing(CanonicalBroker(log)) as broker:
                assert broker.status(op)['state'] == 'RUNNING'
                with pytest.raises(CassetteError): broker.release_hold(op,'wrong-boundary')
                broker.release_hold(op, boundary)
                if kind == 'prepare':
                    broker.close()
                    first_path = next(row['path'] for row in server.requests if row['range'])
                    before_reads = sum(row['path'] == first_path and bool(row['range']) for row in server.requests)
                    resumed = subprocess.run(command,capture_output=True,text=True,timeout=60)
                    assert resumed.returncode == 0, resumed.stderr
                    result = json.loads(resumed.stdout)
                    assert sum(row['path'] == first_path and bool(row['range']) for row in server.requests) == before_reads
                else:
                    result = asyncio.run(getattr(broker,method)(request,cartridge,PROFILE,owner))
                assert result['state'] == 'SUCCEEDED', result
                if kind == 'run':
                    assert len(result['result']['tokens']) == 2
                    tokens = [event['payload']['token_index'] for event in broker.events(op) if 'token_index' in event['payload']]
                    assert tokens == [0,1]
                elif kind == 'train':
                    state = native_training_state(cartridge,result['result']['root_digest'],result['result']['manifest_digest'])
                    assert len(state['losses']) == 2 and state['complete']
                if kind != 'prepare':
                    assert asyncio.run(getattr(broker,method)(request,cartridge,PROFILE,owner)) == result
        finally:
            if process.poll() is None: process.kill(); process.wait(timeout=5)
            process.stdout.close(); process.stderr.close()


def test_q33_q42_q44_q53_capture_and_profile_resume(tmp_path):
    """Q5/Q6/Q25/Q33/Q42/Q44/Q53/Q80: resume exact measurements and retain durable boundaries."""
    owner = CapacityCoordinator(tmp_path)
    with closing(CanonicalBroker(tmp_path / 'profile-holds')) as broker:
        operation = broker.issue({'protocol_version': '1', 'operation': 'run',
            'idempotency_key': 'ordered-profile-holds', 'target': 'blake3:' + '0' * 64,
            'arguments': {}})['operation_id']
        async def hold_and_release(boundary):
            broker.request_hold(operation, boundary)
            with pytest.raises(CassetteError):
                broker.request_hold(operation, 'competing-boundary')
            waiter = asyncio.create_task(broker.hold_boundary(operation, boundary))
            try:
                await asyncio.sleep(0)
                assert broker.events(operation)[-1]['payload'] == {'hold': 'ACKNOWLEDGED', 'boundary': boundary}
                with pytest.raises(CassetteError):
                    broker.release_hold(operation, 'wrong-boundary')
                broker.release_hold(operation, boundary)
                await waiter
            finally:
                if not waiter.done():
                    waiter.cancel()
                    await asyncio.gather(waiter, return_exceptions=True)
        asyncio.run(hold_and_release('CARTRIDGE-DURABILITY'))
        asyncio.run(hold_and_release('profile-checkpoint'))
        assert [event['payload']['hold'] for event in broker.events(operation)
                if 'hold' in event['payload']] == ['REQUESTED', 'ACKNOWLEDGED', 'RELEASED'] * 2
    # Q44/Q53: cancellation cannot release an extent while its owned I/O still runs.
    started, release = threading.Event(), threading.Event()
    finished = []
    descriptor = os.open(tmp_path / 'cancelled-io-proof', os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    def delayed_write():
        started.set()
        assert release.wait(3)
        os.pwrite(descriptor, b'joined', 0)
        finished.append(True)
    async def cancel_during_io():
        task = asyncio.create_task(await_extent_io(delayed_write))
        try:
            assert await asyncio.to_thread(started.wait, 2)
            task.cancel()
            await asyncio.sleep(.02)
            assert not task.done()
        finally:
            release.set()
            with pytest.raises(asyncio.CancelledError):
                await task
    try:
        asyncio.run(cancel_during_io())
        assert finished == [True] and os.pread(descriptor, 6, 0) == b'joined'
    finally:
        os.close(descriptor)
    template = {'command':[sys.executable,'-c','import json,os; b=json.loads(os.environ["CASSETTE_EXECUTION_BINDING"]); print(json.dumps({"binding_digest":b["digest"],"result":b["inputs"]["operand"]*2}))'], 'cwd':str(tmp_path),
                'permission':'CAMPAIGN_DIRECTORY_WRITE','host':'fixture','disk':'scratch','path':str(tmp_path),
                'stop_conditions':['timeout'],'next_byte_claim':10000}
    binding = campaign.bind_action(template,campaign.identity(template),{'operand':21},'graph')
    assert binding['operation_id'] != campaign.bind_action(template,campaign.identity(template),{},'graph')['operation_id']
    for field,value in [('inputs',{'operand':22}),('graph_digest','other'),('started_ns','1'),('operation_id',str(campaign.uuid.uuid4()))]:
        changed = copy.deepcopy(binding); changed[field] = value
        with pytest.raises(CassetteError): campaign.capture_attempt(owner,'L04',changed)
    captured = campaign.capture_attempt(owner,'L04',binding)
    attempt = captured['value']['attempts'][0]
    assert attempt['status'] == 'CAPTURED'
    root = tmp_path/'captures'/binding['operation_id']
    assert json.loads((root/'stdout.log').read_text())['result'] == 42
    assert campaign.verify_capture(root,attempt,lambda bound: 2*bound['inputs']['operand'])['status'] == 'PASS'
    with pytest.raises(CassetteError): campaign.verify_capture(root,attempt,lambda bound: 2*bound['inputs']['operand']+1)
    ignored = copy.deepcopy(template); ignored['command'] = [sys.executable,'-c','print(42)']
    unused = campaign.bind_action(ignored,campaign.identity(ignored),{'operand':22},'other-graph')
    second_capture = campaign.capture_attempt(owner,'L04',unused,expected=captured['digest'])
    ignored_attempt = second_capture['value']['attempts'][-1]
    assert ignored_attempt['status'] == 'CAPTURED'
    with pytest.raises(CassetteError):
        campaign.verify_capture(tmp_path/'captures'/unused['operation_id'],ignored_attempt,lambda bound: 2*bound['inputs']['operand'])
    campaign.verify_namespace(root,attempt['seal'])
    patterns = [{'write_bytes':256,'read_bytes':128,'payload_digest':digest_bytes(bytes(256))},
                {'write_bytes':512,'read_bytes':256,'payload_digest':digest_bytes(bytes(512))}]
    binding = dict.fromkeys(['drive','host','path','operation','plan'],'fixture')
    writes = iter([1000,5096,5096,9192])
    host_writes = iter([0,256,256,768])
    def collector(value): return {'binding':value,'device_write_bytes':next(writes),'host_write_bytes':next(host_writes)}
    first = campaign.measure_profile(owner,binding,patterns,collector)
    second = campaign.measure_profile(owner,binding,patterns,collector,expected=first['digest'])
    assert len(second['value']['observations']) == 2
    profile = campaign.storage_profile(binding,patterns,second['value']['observations'],expected_binding=binding)
    assert profile['device_write_bytes'] == 8192
    assert profile['host_write_bytes'] == 768
    # Q42: recorded hardware observations classify a complete cache-crossing window.
    # Flags alone never satisfy the predicate; no large/live transfer is implied by this fixture.
    source_binding = {**binding, 'plan': {'host_memory_bytes': 128, 'cache_crossing_required': True,
                                        'uncached_read_request_available': True}}
    source_observations = [{**row, 'binding': source_binding, 'data_allocated_bytes': pattern['write_bytes'],
                            'observed_data_write_bytes': pattern['write_bytes']}
        for pattern, row in zip(patterns, second['value']['observations'], strict=True)]
    resumed = [{'binding': source_binding, 'pattern': pattern, 'host_write_bytes': 0,
        'observed_data_read_bytes': pattern['read_bytes'], 'process_data_read_bytes': 256,
        'device_read_bytes': 256, 'data_reads_with_process_io': 1, 'data_reads_without_process_io': 0,
        'errors': 0, 'readback_ok': True, 'uncached_request': True} for pattern in patterns]
    # These rows are recorded-hardware classifier fixtures, not live source captures.
    empty_rate = {'samples': 0, 'minimum': None, 'maximum': None, 'empirical_percentiles': {}}
    def classifier_statistics(row, phase):
        seconds = row.get('duration_seconds', .001)
        call = {'samples': 1, 'minimum': seconds, 'maximum': seconds,
                'empirical_percentiles': {'0.5': seconds, '0.95': seconds, '0.99': seconds, '1.0': seconds}}
        return {'phases': {name: {'calls': {'data.read': call} if name == phase else {},
            'durable_chunk_bytes_per_second': empty_rate, 'verified_range_bytes_per_second': empty_rate}
            for name in ('FRESH_WRITE_READBACK', 'RESUME_VERIFY', 'RETAINED_REVALIDATION')},
            'windows': [{'active_seconds': seconds, 'downtime_before_seconds': 0}]}
    source_observations = [{**row, 'trace_statistics': classifier_statistics(row, 'FRESH_WRITE_READBACK')}
                           for row in source_observations]
    resumed = [{**row, 'trace_statistics': classifier_statistics(row, 'RETAINED_REVALIDATION')} for row in resumed]
    crossed = campaign.storage_profile(source_binding, patterns, source_observations,
                                      expected_binding=source_binding, revalidations=resumed)
    assert crossed['cache']['classification'] == 'MIXED_CACHE_SOURCE_WINDOW_WITH_PHYSICAL_IO'
    assert crossed['cache']['per_read_attribution'] == 'NOT_ESTABLISHED'
    # Q42/Q51: arbitrarily many state writes cannot conceal missing source data writes.
    with pytest.raises(CassetteError):
        campaign.storage_profile(source_binding, patterns,
            [{**row, 'host_write_bytes': 1 << 40, 'observed_data_write_bytes': pattern['write_bytes'] - 1}
             for pattern, row in zip(patterns, source_observations, strict=True)],
            expected_binding=source_binding, revalidations=resumed)
    overlapping = [{'depth': 2, 'registry_id': 'near-driver', 'registry_class': 'IOBlockStorageDriver',
                    'read_bytes': 100, 'write_bytes': 200, 'read_operations': 1},
                   {'depth': 7, 'registry_id': 'ancestor-driver', 'registry_class': 'IOBlockStorageDriver',
                    'read_bytes': 100, 'write_bytes': 200, 'read_operations': 1}]
    selected_counter = storage_counter_snapshot(overlapping)
    assert selected_counter['authority']['registry_id'] == 'near-driver'
    assert selected_counter['device_read_bytes'] == 100
    assert selected_counter['device_write_bytes'] == 200
    assert selected_counter['counter_candidates'] == overlapping
    with pytest.raises(CassetteError):
        campaign.storage_profile(source_binding, patterns, source_observations, expected_binding=source_binding,
            revalidations=[{**row, 'device_read_bytes': selected_counter['device_read_bytes']} for row in resumed])
    # The rejected old sum would falsely cross this same recorded minimum.
    falsely_summed = campaign.storage_profile(source_binding, patterns, source_observations,
        expected_binding=source_binding, revalidations=[{**row, 'device_read_bytes': 200} for row in resumed])
    assert falsely_summed['status'] == 'PASS'
    ambiguous = storage_counter_snapshot([overlapping[0], {**overlapping[1], 'depth': 2}])
    assert ambiguous['authority'] is None and ambiguous['device_read_bytes'] is None
    assert storage_counter_snapshot([])['device_write_bytes'] is None
    for field, bad in [('process_data_read_bytes', 0), ('device_read_bytes', 0),
                       ('data_reads_with_process_io', 0), ('observed_data_read_bytes', 0),
                       ('host_write_bytes', 1), ('uncached_request', False)]:
        changed = [{**row, field: bad} for row in resumed]
        with pytest.raises(CassetteError):
            campaign.storage_profile(source_binding, patterns, source_observations,
                                     expected_binding=source_binding, revalidations=changed)
    with pytest.raises(CassetteError):
        campaign.storage_profile(source_binding, patterns,
            [{**row, 'data_allocated_bytes': 0} for row in source_observations],
            expected_binding=source_binding, revalidations=resumed)
    with pytest.raises(CassetteError):
        campaign.storage_profile(source_binding, patterns, source_observations,
                                 expected_binding=source_binding, revalidations=[])
    assert not list(tmp_path.rglob('profile.bin'))
    assert all(observation['scratch_retention'] == 'TEMPORARY_UNLINKED'
               for observation in second['value']['observations'])
    assert campaign.measure_profile(owner,binding,patterns,collector,expected=second['digest']) == second
    for offset in (100_000_008, (1 << 63)-1-16*1024*1024):
        claims_before = len(owner.claims())
        with pytest.raises(CassetteError) as unsupported:
            campaign.campaign_profile_io(owner, str(campaign.uuid.uuid4()), {
                'write_bytes':1, 'read_bytes':1, 'payload_digest':digest_bytes(bytes(1)), 'offset_bytes':offset})
        assert unsupported.value.code == 'INVALID_REQUEST'
        assert len(owner.claims()) == claims_before

    # Q42/Q53/Q60: a named synthetic working set survives descriptor close and process restart.
    profile_key = 'q42-profile-extents'
    profile_binding = {'drive': 'fixture', 'host': 'fixture-host', 'operation': 'q42', 'plan': 'synthetic'}
    profile_lengths = {'data': 32, 'state': 24}
    data_bytes = b'profile-data-' + bytes(range(19))
    state_bytes = b'profile-state-' + bytes(range(10))
    prepared, extents = grant_profile_extents(owner, profile_key, profile_binding, profile_lengths)
    assert prepared['value']['status'] == 'RETAINED'
    operation = prepared['value']['operation_id']
    transfer_dir = tmp_path / 'transfers' / operation
    data_path = transfer_dir / 'data.extent'
    state_path = transfer_dir / 'state.extent'
    user_path = transfer_dir / 'user.txt'
    user_path.write_text('preserve this unrelated file')
    try:
        assert os.pwrite(extents['data'].fd, data_bytes, 0) == len(data_bytes)
        assert os.pwrite(extents['state'].fd, state_bytes, 0) == len(state_bytes)
        os.fsync(extents['data'].fd)
        os.fsync(extents['state'].fd)
        original_inodes = {role: os.fstat(extent.fd).st_ino for role, extent in extents.items()}
    finally:
        for extent in extents.values():
            os.close(extent.fd)

    restart_script = (
        'import json, os, sys; '
        'from store import CapacityCoordinator, grant_profile_extents; '
        'owner = CapacityCoordinator(sys.argv[1]); '
        'head, extents = grant_profile_extents(owner, sys.argv[2], json.loads(sys.argv[3]), json.loads(sys.argv[4])); '
        'assert os.pread(extents["data"].fd, len(bytes.fromhex(sys.argv[5])), 0) == bytes.fromhex(sys.argv[5]); '
        'print(json.dumps({"status": head["value"]["status"], "inodes": {role: os.fstat(extent.fd).st_ino for role, extent in extents.items()}})); '
        '[os.close(extent.fd) for extent in extents.values()]'
    )
    restarted = subprocess.run(
        [sys.executable, '-c', restart_script, str(tmp_path), profile_key,
         json.dumps(profile_binding), json.dumps(profile_lengths), data_bytes.hex()],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, check=True,
    )
    restart_result = json.loads(restarted.stdout)
    assert restart_result['status'] == 'RETAINED'
    assert restart_result['inodes'] == {role: prepared['value']['identities'][role]['inode']
                                        for role in profile_lengths}
    assert restart_result['inodes'] == original_inodes

    with pytest.raises(CassetteError):
        grant_profile_extents(owner, profile_key, {**profile_binding, 'plan': 'changed'}, profile_lengths)
    with pytest.raises(CassetteError):
        grant_profile_extents(owner, profile_key, profile_binding, {**profile_lengths, 'state': 25})

    missing_path = transfer_dir / 'state.missing'
    state_path.rename(missing_path)
    try:
        with pytest.raises(CassetteError):
            grant_profile_extents(owner, profile_key, profile_binding, profile_lengths)
    finally:
        missing_path.rename(state_path)

    replacement_path = transfer_dir / 'data.replaced'
    data_path.rename(replacement_path)
    data_path.write_bytes(data_bytes)
    try:
        with pytest.raises(CassetteError):
            grant_profile_extents(owner, profile_key, profile_binding, profile_lengths)
    finally:
        data_path.unlink()
        replacement_path.rename(data_path)

    evidence_key = 'q42-profile-evidence'
    invented_evidence_digest = digest_bytes(b'q42-invented-evidence')
    with pytest.raises(CassetteError):
        reclaim_profile_extents(owner, profile_key, invented_evidence_digest)

    retained, locked_extents = grant_profile_extents(owner, profile_key, profile_binding, profile_lengths)
    with pytest.raises(CassetteError):
        seal_profile_extents(owner, profile_key, retained['digest'], evidence_key, invented_evidence_digest)
    wrong_evidence_key = 'q42-profile-evidence-wrong'
    wrong_evidence = compare_campaign_head(owner, wrong_evidence_key, None, {
        'retained_manifests': [{'key': 'q42-other-profile', 'retained_digest': retained['digest']}],
    })
    with pytest.raises(CassetteError):
        seal_profile_extents(owner, profile_key, retained['digest'], wrong_evidence_key, wrong_evidence['digest'])
    evidence = compare_campaign_head(owner, evidence_key, None, {
        'retained_manifests': [{'key': profile_key, 'retained_digest': retained['digest']}],
    })
    sealed = seal_profile_extents(owner, profile_key, retained['digest'], evidence_key, evidence['digest'])
    assert sealed['value']['status'] == 'SEALED'
    try:
        with pytest.raises(CassetteError):
            reclaim_profile_extents(owner, profile_key, sealed['digest'])
    finally:
        for extent in locked_extents.values():
            os.close(extent.fd)

    active = owner(CapacityTransition('q42-profile-active', 'hold', write_bytes=(0,)))
    try:
        with pytest.raises(CassetteError):
            reclaim_profile_extents(owner, profile_key, sealed['digest'])
    finally:
        execute_claimed_write(active, lambda: None)
        complete_capacity_claim(active)

    reclaimed = reclaim_profile_extents(owner, profile_key, sealed['digest'])
    assert reclaimed['value']['status'] == 'RECLAIMED'
    assert not data_path.exists() and not state_path.exists()
    assert user_path.read_text() == 'preserve this unrelated file'
    assert reclaim_profile_extents(owner, profile_key, sealed['digest']) == reclaimed

    # Q6/Q60: malformed immutable values fail through Cassette's typed error boundary.
    malformed_values = {
        'scalar': 'not-a-manifest',
        'list': [],
        'status': {'status': 'UNKNOWN', 'binding': profile_binding, 'lengths': profile_lengths,
                   'operation_id': 'profile-22222222-2222-2222-2222-222222222222',
                   'retention': 'TEMPORARY'},
    }
    for suffix, value in malformed_values.items():
        malformed_key = f'q42-profile-malformed-{suffix}'
        compare_campaign_head(owner, malformed_key, None, value)
        with pytest.raises(CassetteError):
            grant_profile_extents(owner, malformed_key, profile_binding, profile_lengths)

    # Q42/Q53/Q60: an interrupted PREPARED namespace is preserved; a fresh namespace is used.
    prepared_key = 'q42-profile-prepared-recovery'
    old_operation = 'profile-11111111-1111-1111-1111-111111111111'
    old_directory = tmp_path / 'transfers' / old_operation
    old_directory.mkdir(parents=True)
    old_data = old_directory / 'data.extent'
    old_data_bytes = b'unknown-old-inode'.ljust(profile_lengths['data'], b'!')
    old_data.write_bytes(old_data_bytes)
    compare_campaign_head(owner, prepared_key, None, {
        'status': 'PREPARED', 'binding': profile_binding, 'lengths': profile_lengths,
        'operation_id': old_operation, 'retention': 'TEMPORARY',
    })
    recovered, recovered_extents = grant_profile_extents(owner, prepared_key, profile_binding, profile_lengths)
    try:
        assert recovered['value']['status'] == 'RETAINED'
        assert recovered['value']['operation_id'] != old_operation
        assert old_data.read_bytes() == old_data_bytes
        assert (tmp_path / 'transfers' / recovered['value']['operation_id'] / 'data.extent').is_file()
    finally:
        for extent in recovered_extents.values():
            os.close(extent.fd)
    assert campaign.expand_coordinates('X-<row>-<record>',{'row':['a','b'],'record':['START','VERIFY']}) == [
        'X-a-START','X-b-START','X-a-VERIFY','X-b-VERIFY']
    with pytest.raises(CassetteError): campaign.expand_coordinates('X-<row>',{'row':['a','a']})


def test_q29_q33_q80_scoped_accounting_and_remediation_diff(tmp_path):
    """Q29/Q33/Q80: research is separate, admitted code remains counted, and repairs obey the diff bound."""
    from tools.ledger import discover, remediation_diff, top_level_imports
    repo = tmp_path/'repo'; repo.mkdir()
    def git(*args):
        result = subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,check=True)
        return result.stdout.strip()
    git('init','-q'); git('config','user.name','L04 Fixture'); git('config','user.email','fixture@localhost')
    authority = '''<!-- CASSETTE_REMOVAL_MAP_BEGIN -->
```json
{"module.py":["Q80"]}
```
<!-- CASSETTE_REMOVAL_MAP_END -->
<!-- CASSETTE_RESEARCH_ROOTS_BEGIN -->
```json
["pure_math_lab"]
```
<!-- CASSETTE_RESEARCH_ROOTS_END -->
'''
    (repo/'AGENTS.md').write_text(authority)
    (repo/'module.py').write_text('# module.py — Q80 fixture; depends on (none).\nvalue = 1\n')
    git('add','.'); git('commit','-qm','fixture parent'); parent = git('rev-parse','HEAD')
    (repo/'module.py').write_text('# changed comment\nvalue = 2\n')
    git('add','.'); git('commit','-qm','fixture child'); child = git('rev-parse','HEAD')
    report = remediation_diff(repo,parent,child)
    assert report['added'] == report['deleted'] == 1 and report['within_limit']
    control = tmp_path/'review-control'; control.mkdir()
    manifest = {'candidate':{'parent':parent,'tree':git('rev-parse',parent+'^{tree}')},'assertions':{'Q80':'INTEGRATION'}}
    history = campaign.ReviewHistory(CapacityCoordinator(control),'L04','repair',campaign.identity(manifest),manifest=manifest)
    head = history.acquire('reviewer',None,now=100,expires=200,worktree=repo)
    raw = tmp_path/'review-proof.log'; raw.write_text('fixture deciding output')
    evidence = {role:{'path':str(raw),'digest':campaign.file_digest(raw),'command':['fixture',role],
                      'exit_code':0 if role in {'child_green','suite','ledger'} else 1}
                for role in ('parent_red','child_green','mutation','suite','ledger')}
    row = {'assertion':'Q80','status':'FAIL','level':'INTEGRATION','predicate':'value is two',
           'source_trace':'module.py','challenge':'read value','expected':2,'observed':1,
           'evidence':['parent_red'],'discriminator':'mutation'}
    envelope = {'review_id':'red','binding':history.binding,'status':'INCOMPLETE','previous':None,
                'candidate':manifest['candidate'],'assertions':[row],'evidence':evidence,
                'findings':[{'id':'finding-1','assertion':'Q80','cause':'wrong value'}],'remediation':None,
                'invalidation':{'class':'assertion_local_rerun','ids':['L04'],'operation_lineages':[],'qualification_lineages':[]}}
    head = history.append('reviewer',head['digest'],envelope,now=150)
    with pytest.raises(CassetteError): history.release('reviewer',head['digest'],now=120)
    green = {**envelope,'review_id':'green','status':'REMEDIATED','previous':campaign.identity(envelope),
             'assertions':[{**row,'status':'PASS','observed':2,'evidence':['child_green']}],'findings':[],
             'remediation':{'parent':parent,'child':child,'assertion':'Q80','finding':'finding-1','diff':report,
                            'proofs':{role:role for role in evidence}}}
    for fault in ('no_op','unrelated_parent','unlinked_finding','unresolved_assertion','zero_diff','missing_proof'):
        bad = copy.deepcopy(green)
        if fault == 'no_op': bad['remediation']['child'] = parent
        if fault == 'unrelated_parent': bad['remediation']['parent'] = child
        if fault == 'unlinked_finding': bad['remediation']['finding'] = 'unknown'
        if fault == 'unresolved_assertion': bad['remediation']['assertion'] = 'unknown'
        if fault == 'zero_diff': bad['remediation']['diff']['executable_line_changes'] = 0
        if fault == 'missing_proof': del bad['remediation']['proofs']['parent_red']
        with pytest.raises(CassetteError): history.append('reviewer',head['digest'],bad,now=151)
    with pytest.raises(CassetteError): history.append('reviewer',head['digest'],green,now=120)
    terminal = history.append('reviewer',head['digest'],green,now=151)
    assert terminal['value']['terminal']
    with pytest.raises(CassetteError): history.acquire('another',terminal['digest'],now=201,expires=210,worktree=repo)
    with pytest.raises(CassetteError): history.release('reviewer',terminal['digest'],now=152)
    (repo/'pure_math_lab').mkdir(); (repo/'pure_math_lab'/'standalone.py').write_text('independent = 1\n')
    assert discover(repo) == [Path('module.py')]
    (repo/'module.py').write_text('import pure_math_lab\n')
    assert top_level_imports(repo,Path('module.py')) == {'pure_math_lab'}
    (repo/'README.md').write_text('outside normal remediation')
    git('add','module.py','README.md'); git('commit','-qm','disallowed change')
    with pytest.raises(ValueError): remediation_diff(repo,parent,git('rev-parse','HEAD'))
    queue, matrix = campaign.load_contracts(Path(__file__).resolve().parent.parent)
    assert [stage['id'] for stage in queue['fixed_steps']] == ['L01','L02','L03','L04','L05','L06','L07','L08','L09','L10']
    assertions = campaign.matrix_assertions(matrix)
    assert 'matrix#failure_rows.assertions[0]' in assertions
    async def work():
        await asyncio.sleep(.025)
        return {'done':True}
    collected = asyncio.run(campaign.collect_interval({'operation':'fixture'},work,
        {'process':campaign.process_observation}, {'process':list(campaign.COLLECTORS['process'])},period_seconds=.01))
    assert collected['result'] == {'done':True}
    assert collected['evidence']['status'] == 'PASS'
    assert len(collected['evidence']['collectors']['process']) >= 2


def test_q33_q80_materialization_derives_owners_and_edges(tmp_path):
    """Q33/Q80: frozen dimensions produce literal records; missing dependency and owner edges reject."""
    (tmp_path/'research').mkdir(); (tmp_path/'schema/campaign').mkdir(parents=True)
    family = {'family':'dense', 'id_format':'F4-<batch-id>-<record>', 'owner_stage':'L07',
              'records_per_coordinate':['START','VERIFY'], 'dependencies':{'START':['L04'],'VERIFY':['matching-START']}}
    contract = {'materialized_record_contract':{'family_evidence_levels':{'dense':'LIVE'}},
                'dependency_graph_revision_contract':{},'expanded_session_families':[family]}
    queue = {**contract, 'fixed_steps':[{'id':'L04','depends':[]}],
             'operation_records':[{'id':'F4-GATE','depends':['F4-a-b-VERIFY']}]}
    (tmp_path/'IMPLEMENTATION.md').write_text('```yaml\n'+campaign.yaml.safe_dump({'phase_live_queue':queue},sort_keys=False)+'```\n')
    matrix = {'fixture_gate_rows':[{'id':'f4_gate','pass_condition':'exact independent comparison'}]}
    (tmp_path/'research/ACCEPTANCE_MATRIX.yaml').write_text(campaign.yaml.safe_dump(matrix))
    generated = {**contract,'matrix_axes':{},'assertion_owner_patterns':{'fixture_gate_rows[id=f4_gate]':['F4-GATE']}}
    (tmp_path/'schema/campaign/contract.json').write_text(json.dumps(generated))
    authority = 'matrix#fixture_gate_rows[id=f4_gate].pass_condition[0]'
    def node(key,depends,owners=(),level='LIVE'):
        return {'id':key,'depends':depends,'evidence_level':level,'matrix_assertion_owners':list(owners),
                'owner_stage':'L07' if level == 'LIVE' else 'L04','permission':'READ_ONLY'}
    registry = {'matrix_digest':campaign.file_digest(tmp_path/'research/ACCEPTANCE_MATRIX.yaml'),
                'materializer':'L04','required_owners':{authority:['F4-GATE']},
                'fixed_records':[node('L04',[],level='INTEGRATION'),node('F4-GATE',['F4-a-b-VERIFY'],[authority])],
                'families':{'dense':{'dimensions':{'batch-id':['a-b'],'record':['START','VERIFY']},
                                    'records':[node('F4-a-b-START',['L04']),node('F4-a-b-VERIFY',['F4-a-b-START'])]}}}
    graph = campaign.materialize(tmp_path,registry)
    assert graph['order'] == ['L04','F4-a-b-START','F4-a-b-VERIFY','F4-GATE']
    early = {**registry, 'fixed_records': registry['fixed_records'][:1], 'families': {},
             'required_owners': {}, 'deferred_assertion_owners': {authority: ['F4-GATE']}}
    provisional = campaign.materialize(tmp_path, early)
    assert provisional['deferred_assertion_owners'] == {authority: ['F4-GATE']}
    with pytest.raises(CassetteError): campaign.clean_replay(provisional, ['L04'])
    for invalid in ({}, {authority: ['L04']}, {authority: ['F4-GATE'], 'unknown': ['future']}):
        with pytest.raises(CassetteError):
            campaign.materialize(tmp_path, {**early, 'deferred_assertion_owners': invalid})
    with pytest.raises(CassetteError):
        campaign.materialize(tmp_path, {**early, 'materializer': 'Q80-MATERIALIZE'})
    with pytest.raises(CassetteError):
        campaign.validate_graph(early['fixed_records'], required_owners={}, parent=provisional,
                                deferred_owners={})
    completed = campaign.materialize(tmp_path, registry, parent=provisional)
    assert not completed.get('deferred_assertion_owners')
    assert completed['parent_graph_digest'] == provisional['revision_digest']
    assert len(campaign.clean_replay(completed, completed['order'])) == 4
    control = tmp_path/'control'; control.mkdir()
    owner = CapacityCoordinator(control)
    head = campaign.publish_graph(owner, provisional)
    published = campaign.publish_graph(owner, completed, head['digest'])
    assert published['value']['graph'] == completed
    assert published['value']['ancestors'] == [provisional['revision_digest']]
    changed = copy.deepcopy(registry); changed['families']['dense']['records'][1]['depends'] = ['L04']
    with pytest.raises(CassetteError): campaign.materialize(tmp_path,changed)
    changed = copy.deepcopy(registry); changed['required_owners'][authority] = ['L04']
    with pytest.raises(CassetteError): campaign.materialize(tmp_path,changed)

    aggregate_root = tmp_path/'aggregates'
    (aggregate_root/'research').mkdir(parents=True)
    (aggregate_root/'schema/campaign').mkdir(parents=True)
    aggregate_queue = copy.deepcopy(queue)
    aggregate_family = aggregate_queue['expanded_session_families'][0]
    aggregate_family.update(aggregate_record='DENSE-ALL-PASS',
        aggregate_dependencies=['every-F4-<batch-id>-VERIFY'], aggregate_owner_stage='L08')
    aggregate_generated = {**generated, 'expanded_session_families':[aggregate_family]}
    (aggregate_root/'IMPLEMENTATION.md').write_text('```yaml\n'+campaign.yaml.safe_dump(
        {'phase_live_queue':aggregate_queue},sort_keys=False)+'```\n')
    (aggregate_root/'research/ACCEPTANCE_MATRIX.yaml').write_text(campaign.yaml.safe_dump(matrix))
    (aggregate_root/'schema/campaign/contract.json').write_text(json.dumps(aggregate_generated))
    aggregate_registry = copy.deepcopy(registry)
    aggregate_registry['fixed_records'].append({**node('DENSE-ALL-PASS',['F4-a-b-VERIFY']),
                                                'owner_stage':'L08'})
    aggregate_graph = campaign.materialize(aggregate_root,aggregate_registry)
    assert aggregate_graph['nodes']['DENSE-ALL-PASS']['depends'] == ['F4-a-b-VERIFY']
    assert aggregate_graph['order'].index('F4-a-b-VERIFY') < aggregate_graph['order'].index('DENSE-ALL-PASS')
    for fault in ('omitted','missing_edge','foreign_edge','wrong_owner','wrong_level','undeclared'):
        bad = copy.deepcopy(aggregate_registry)
        if fault == 'omitted': bad['fixed_records'].pop()
        elif fault == 'missing_edge': bad['fixed_records'][-1]['depends'] = []
        elif fault == 'foreign_edge': bad['fixed_records'][-1]['depends'] = ['L04']
        elif fault == 'wrong_owner': bad['fixed_records'][-1]['owner_stage'] = 'L07'
        elif fault == 'wrong_level': bad['fixed_records'][-1]['evidence_level'] = 'UNIT'
        else: bad['fixed_records'][-1]['id'] = 'UNDECLARED-ALL-PASS'
        with pytest.raises(CassetteError): campaign.materialize(aggregate_root,bad)

    aggregate_family.update(id_format='INPUT-<batch-id>-FREEZE', records_per_coordinate=['FREEZE'],
        dependencies={'FREEZE':['L04']}, aggregate_dependencies=['every INPUT-<batch-id>-FREEZE'])
    aggregate_registry['families']['dense'] = {'dimensions':{'batch-id':['a','b']},
        'records':[node('INPUT-'+key+'-FREEZE',['L04']) for key in ('a','b')]}
    aggregate_registry['fixed_records'][1]['depends'] = ['INPUT-a-FREEZE','INPUT-b-FREEZE']
    aggregate_queue['operation_records'][0]['depends'] = ['INPUT-a-FREEZE','INPUT-b-FREEZE']
    aggregate_registry['fixed_records'][-1]['depends'] = ['INPUT-a-FREEZE','INPUT-b-FREEZE']
    (aggregate_root/'IMPLEMENTATION.md').write_text('```yaml\n'+campaign.yaml.safe_dump(
        {'phase_live_queue':aggregate_queue},sort_keys=False)+'```\n')
    (aggregate_root/'schema/campaign/contract.json').write_text(json.dumps(aggregate_generated))
    literal_graph = campaign.materialize(aggregate_root,aggregate_registry)
    assert literal_graph['nodes']['INPUT-a-FREEZE']['depends'] == ['L04']
    assert literal_graph['nodes']['DENSE-ALL-PASS']['depends'] == ['INPUT-a-FREEZE','INPUT-b-FREEZE']
    bad = copy.deepcopy(aggregate_registry)
    bad['families']['dense']['records'][0]['depends'] = []
    with pytest.raises(CassetteError): campaign.materialize(aggregate_root,bad)

    historical_text = '''```yaml
steps:
  - id: S27
    depends: []
    status: DONE fixture: exact accounting
  - id: S28
    depends: [S27]
    status: "DONE fixture closeout"
```
'''
    queue['fixed_steps'][0]['depends'] = ['S28']
    (tmp_path/'IMPLEMENTATION.md').write_text(historical_text + '```yaml\n' +
        campaign.yaml.safe_dump({'phase_live_queue': queue}, sort_keys=False) + '```\n')
    historical = campaign.historical_steps(tmp_path)
    anchored = copy.deepcopy(registry)
    anchored['fixed_records'][0]['depends'] = ['S28']
    anchored['fixed_records'].extend({**node(key, row['depends'], level='INTEGRATION'),
        'historical_authority_digest': campaign.identity(row)} for key, row in historical.items())
    assert campaign.materialize(tmp_path, anchored)['order'][:3] == ['S27', 'S28', 'L04']
    for field, value in [('historical_authority_digest', 'foreign'), ('permission', 'CAMPAIGN_DIRECTORY_WRITE'),
                         ('evidence_level', 'LIVE'), ('depends', ['unknown'])]:
        bad = copy.deepcopy(anchored); bad['fixed_records'][-1][field] = value
        with pytest.raises(CassetteError): campaign.materialize(tmp_path, bad)

    # Q80 composes existing recovery and verification rules before one monotone publication.
    edge_root = tmp_path/'proof-edges'
    (edge_root/'research').mkdir(parents=True)
    (edge_root/'schema/campaign').mkdir(parents=True)
    actual_contract = json.loads((Path(__file__).resolve().parents[1]/'schema/campaign/contract.json').read_text())
    proof_families = [copy.deepcopy(row) for row in actual_contract['expanded_session_families']
                      if row['family'] in {'physical_qualification','checkpoint_proof','verification_work'}]
    proof_contract = {'materialized_record_contract': {'family_evidence_levels': {
        row['family']: actual_contract['materialized_record_contract']['family_evidence_levels'][row['family']]
        for row in proof_families}}, 'dependency_graph_revision_contract': {},
        'expanded_session_families': proof_families}
    terminals = ['QUALIFY-'+key+'-VERIFY' for key in ('ACQ-F4-c1','ACQ-F4-c10')]
    proof_queue = {**proof_contract, 'fixed_steps': [{'id':'L04','depends':[]}],
                   'operation_records':[{'id':'F4-GATE','depends':terminals}],
                   'long_operation_contract': {'checkpoint_proof':'Every product START requires its exact RECOVERABILITY coordinate'},
                   'verification_contract': {'fixed_targets':['F4-GATE']}}
    (edge_root/'IMPLEMENTATION.md').write_text('```yaml\n'+campaign.yaml.safe_dump(
        {'phase_live_queue':proof_queue},sort_keys=False)+'```\n')
    (edge_root/'research/ACCEPTANCE_MATRIX.yaml').write_text(campaign.yaml.safe_dump(
        {'fixture_gate_rows':[{'id':'f4_gate','pass_condition':'exact independent comparison'}],
         'physical_storage_qualification':{'required_assertions':['exact_drive_operation_plan_profile_recorded']}}))
    (edge_root/'schema/campaign/contract.json').write_text(json.dumps({**proof_contract,
        'matrix_axes':{},'assertion_owner_patterns':{'fixture_gate_rows[id=f4_gate]':['F4-GATE'],
            'physical_storage_qualification':actual_contract['assertion_owner_patterns']['physical_storage_qualification']}}))
    physical_authority = 'matrix#physical_storage_qualification.required_assertions[0]'
    checkpoint_records = [node('CHECKPOINT-QUALIFY-'+key+'-START-RECOVERABILITY',
                               ['QUALIFY-'+key+'-START']) for key in ('ACQ-F4-c1','ACQ-F4-c10')]
    verification_records = []
    for target in [*terminals,'F4-GATE']:
        predecessors = (terminals if target == 'F4-GATE' else [target.removesuffix('-VERIFY')+'-START',
            'CHECKPOINT-'+target.removesuffix('-VERIFY')+'-START-RECOVERABILITY'])
        verification_records.extend([node('VERIFY-WORK-'+target+'-START',list(predecessors)),
            node('VERIFY-WORK-'+target+'-RESULT',['VERIFY-WORK-'+target+'-START'])])
    physical_records = []
    for key, terminal in zip(('ACQ-F4-c1','ACQ-F4-c10'),terminals,strict=True):
        physical_records.extend([node('QUALIFY-'+key+'-START',['L04']),
            node(terminal,['QUALIFY-'+key+'-START','CHECKPOINT-QUALIFY-'+key+'-START-RECOVERABILITY',
                           'VERIFY-WORK-'+terminal+'-RESULT'],[physical_authority])])
    proof_registry = {'matrix_digest':campaign.file_digest(edge_root/'research/ACCEPTANCE_MATRIX.yaml'),
        'materializer':'L04','required_owners':{authority:['F4-GATE'],physical_authority:terminals},
        'fixed_records':[node('L04',[],level='INTEGRATION'),
            node('F4-GATE',[*terminals,'VERIFY-WORK-F4-GATE-RESULT'],[authority])],
        'families':{
            'physical_qualification':{'dimensions':{'consumer-flat-id':['ACQ-F4-c1','ACQ-F4-c10'],'record':['START','VERIFY']},
                'dependency_bindings':{'literal_consumer_prerequisites_that_do_not_depend_on_this_profile':['L04']},
                'records':physical_records},
            'checkpoint_proof':{'dimensions':{'operation-start-flat-id':['QUALIFY-ACQ-F4-c1-START','QUALIFY-ACQ-F4-c10-START']},
                'records':checkpoint_records},
            'verification_work':{'dimensions':{'target-flat-id':[*terminals,'F4-GATE'],'record':['START','RESULT']},
                'records':verification_records}}}
    proof_early = {**proof_registry,'fixed_records':proof_registry['fixed_records'][:1],'families':{},
                   'required_owners':{},'deferred_assertion_owners':{authority:['F4-GATE'],
                       physical_authority:actual_contract['assertion_owner_patterns']['physical_storage_qualification']}}
    proof_parent = campaign.materialize(edge_root,proof_early)
    proof_graph = campaign.materialize(edge_root,proof_registry,parent=proof_parent)
    assert proof_graph['nodes']['L04'] == proof_parent['nodes']['L04']
    for key, terminal in zip(('ACQ-F4-c1','ACQ-F4-c10'),terminals,strict=True):
        start = 'QUALIFY-'+key+'-START'
        checkpoint = 'CHECKPOINT-'+start+'-RECOVERABILITY'
        assert proof_graph['nodes'][checkpoint]['depends'] == [start]
        assert set(proof_graph['nodes'][terminal]['depends']) == {
            start,checkpoint,'VERIFY-WORK-'+terminal+'-RESULT'}
        assert set(proof_graph['nodes']['VERIFY-WORK-'+terminal+'-START']['depends']) == {start,checkpoint}
        assert terminal not in proof_graph['nodes']['VERIFY-WORK-'+terminal+'-START']['depends']
        assert not any(name.startswith('CHECKPOINT-VERIFY-WORK-') for name in proof_graph['nodes'])
    assert set(proof_graph['nodes']['F4-GATE']['depends']) == {*terminals,'VERIFY-WORK-F4-GATE-RESULT'}
    assert proof_graph['nodes']['VERIFY-WORK-F4-GATE-START']['depends'] == terminals
    assert proof_graph['required_owners'][physical_authority] == terminals
    for key in ('ACQ-F4-c1','ACQ-F4-c10'):
        chain = ['QUALIFY-'+key+'-START','CHECKPOINT-QUALIFY-'+key+'-START-RECOVERABILITY',
                 'VERIFY-WORK-QUALIFY-'+key+'-VERIFY-START','VERIFY-WORK-QUALIFY-'+key+'-VERIFY-RESULT',
                 'QUALIFY-'+key+'-VERIFY']
        assert [proof_graph['order'].index(name) for name in chain] == sorted(proof_graph['order'].index(name) for name in chain)
    first, second = terminals
    start_a, start_b = [target.removesuffix('-VERIFY')+'-START' for target in terminals]
    cp_a, cp_b = ['CHECKPOINT-'+start+'-RECOVERABILITY' for start in (start_a,start_b)]
    vs_a, vs_b = ['VERIFY-WORK-'+target+'-START' for target in terminals]
    vr_a = 'VERIFY-WORK-'+first+'-RESULT'
    mismatch = 'literal graph edges differ from composed contract prerequisites'
    observations = []
    faults = ['omitted_checkpoint','missing_checkpoint_edge','crosswired_checkpoint','union_checkpoint',
              'foreign_checkpoint_edge','omitted_verification','target_cycle','verifier_missing_checkpoint',
              'verifier_missing_start','missing_original_edge','recursive_checkpoint','verify_checkpoint',
              'verify_verifier','stale_checkpoint_binding','stale_verifier_binding','crosswired_result']
    for fault in faults:
        bad = copy.deepcopy(proof_registry)
        indexed = {row['id']:row for family in bad['families'].values() for row in family['records']}
        expected_key, expected_detail = first, mismatch
        if fault == 'omitted_checkpoint':
            bad['families']['checkpoint_proof']['dimensions']['operation-start-flat-id'].remove(start_a)
            bad['families']['checkpoint_proof']['records'].remove(indexed[cp_a])
            indexed[first]['depends'].remove(cp_a); indexed[vs_a]['depends'].remove(cp_a)
            expected_key, expected_detail = start_a, 'long-operation START lacks its checkpoint proof coordinate'
        elif fault == 'missing_checkpoint_edge': indexed[first]['depends'].remove(cp_a)
        elif fault in {'crosswired_checkpoint','union_checkpoint'}:
            indexed[cp_a]['depends'] = [start_b] if fault == 'crosswired_checkpoint' else [start_a,start_b]
            expected_key = cp_a
        elif fault == 'foreign_checkpoint_edge': indexed[first]['depends'][1] = cp_b
        elif fault == 'omitted_verification':
            bad['families']['verification_work']['dimensions']['target-flat-id'].remove(second)
            bad['families']['verification_work']['records'] = [row for row in bad['families']['verification_work']['records']
                if row['id'] not in {'VERIFY-WORK-'+second+'-START','VERIFY-WORK-'+second+'-RESULT'}]
            indexed[second]['depends'].remove('VERIFY-WORK-'+second+'-RESULT')
            expected_key, expected_detail = second, 'terminal target lacks its independent verification coordinate'
        elif fault in {'target_cycle','verifier_missing_checkpoint','verifier_missing_start'}:
            if fault == 'target_cycle': indexed[vs_a]['depends'].append(first)
            else: indexed[vs_a]['depends'].remove(cp_a if fault == 'verifier_missing_checkpoint' else start_a)
            expected_key = vs_a
        elif fault == 'missing_original_edge': indexed[first]['depends'].remove(start_a)
        elif fault == 'recursive_checkpoint':
            key = 'CHECKPOINT-'+vs_a+'-RECOVERABILITY'
            bad['families']['checkpoint_proof']['dimensions']['operation-start-flat-id'].append(vs_a)
            bad['families']['checkpoint_proof']['records'].append(node(key,[vs_a]))
            expected_key, expected_detail = key, 'checkpoint coordinate is not a product operation START'
        elif fault in {'verify_checkpoint','verify_verifier'}:
            target = cp_a if fault == 'verify_checkpoint' else vr_a
            bad['families']['verification_work']['dimensions']['target-flat-id'].append(target)
            bad['families']['verification_work']['records'].extend([
                node('VERIFY-WORK-'+target+'-START',[start_a]),
                node('VERIFY-WORK-'+target+'-RESULT',['VERIFY-WORK-'+target+'-START'])])
            expected_key = 'VERIFY-WORK-'+target+'-START'
            expected_detail = 'verification coordinate is absent or recursively verifies proof work'
        elif fault == 'stale_checkpoint_binding':
            bad['families']['checkpoint_proof']['dependency_bindings'] = {'exact-operation-START':[start_a]}
            expected_key, expected_detail = cp_a, 'checkpoint predecessor must come only from its coordinate'
        elif fault == 'stale_verifier_binding':
            bad['families']['verification_work']['dependency_bindings'] = {'every-original-target-predecessor':[start_a]}
            expected_key, expected_detail = vs_a, 'verification predecessors must come only from their target'
        else:
            indexed[vr_a]['depends'] = [vs_b]
            expected_key = vr_a
        with pytest.raises(CassetteError) as rejected:
            campaign.materialize(edge_root,bad,parent=proof_parent)
        assert (rejected.value.object_id,rejected.value.detail) == (expected_key,expected_detail), fault
        observations.append({'fault':fault,'error':rejected.value.payload()})
    legacy_nodes = [*proof_parent['nodes'].values(),
        node(start_a,['L04']),node(first,[start_a],[physical_authority]),
        node(start_b,['L04']),node(second,[start_b],[physical_authority])]
    legacy = campaign.validate_graph(legacy_nodes,required_owners={physical_authority:terminals},parent=proof_parent,
        materializer='L04',deferred_owners={authority:['F4-GATE']})
    with pytest.raises(CassetteError) as sealed:
        campaign.materialize(edge_root,proof_registry,parent=legacy)
    assert (sealed.value.object_id,sealed.value.detail) == (first,'successor rewrites or removes an inherited record or edge')
    assert {key:value for key,value in legacy['nodes'][first].items() if key != 'depends'} == {
        key:value for key,value in proof_graph['nodes'][first].items() if key != 'depends'}
    observations.append({'fault':'sealed_target_edges','error':sealed.value.payload()})

    # Q80: a failed attempt does not create a second required tuple or erase its history.
    succession_root = tmp_path/'same-profile-attempts'
    (succession_root/'research').mkdir(parents=True)
    (succession_root/'schema/campaign').mkdir(parents=True)
    succession_contract = copy.deepcopy(proof_contract)
    succession_contract['materialized_record_contract']['family_evidence_levels']['source_profile_group'] = 'LIVE'
    succession_contract['expanded_session_families'].append({'family':'source_profile_group',
        'records':['SOURCE-PROFILES-ALL-PASS'],'owner_stage':'L07',
        'dependencies':['every-QUALIFY-<consumer-flat-id>-VERIFY']})
    succession_queue = {**succession_contract,'fixed_steps':[{'id':'L04','depends':[]}],
        'operation_records':[],'long_operation_contract':proof_queue['long_operation_contract'],
        'verification_contract':{'fixed_targets':[]}}
    (succession_root/'IMPLEMENTATION.md').write_text('```yaml\n'+campaign.yaml.safe_dump(
        {'phase_live_queue':succession_queue},sort_keys=False)+'```\n')
    (succession_root/'research/ACCEPTANCE_MATRIX.yaml').write_text(campaign.yaml.safe_dump(
        {'physical_storage_qualification':{'required_assertions':['exact_drive_operation_plan_profile_recorded']}}))
    (succession_root/'schema/campaign/contract.json').write_text(json.dumps({**succession_contract,
        'matrix_axes':{},'assertion_owner_patterns':{
            'physical_storage_qualification':actual_contract['assertion_owner_patterns']['physical_storage_qualification']}}))
    attempt_registry = copy.deepcopy(proof_registry)
    attempt_registry.update(matrix_digest=campaign.file_digest(succession_root/'research/ACCEPTANCE_MATRIX.yaml'),
        fixed_records=attempt_registry['fixed_records'][:1],required_owners={physical_authority:terminals},approved_cards={})
    attempt_registry['families']['verification_work']['dimensions']['target-flat-id'].remove('F4-GATE')
    attempt_registry['families']['verification_work']['records'] = [row for row in
        attempt_registry['families']['verification_work']['records'] if not row['id'].startswith('VERIFY-WORK-F4-GATE-')]
    def approve_start(reg, key, plan):
        start = next(row for row in reg['families']['physical_qualification']['records'] if row['id']==key)
        request = {'consumer_flat_id':key.removeprefix('QUALIFY-').removesuffix('-START'),
            'physical_disk_id':['fixture'],'apfs_volume_uuid':'fixture','host_id':campaign.identity('host'),
            'assembled_path_digest':campaign.identity('path'),'operation':'acquire-qualification-only',
            'plan_digest':campaign.identity(plan),'expected_read_write_shape':[{'artifact':'fixture','read_bytes':256,'write_bytes':256}]}
        card = {'record_id':key,'permission':'CAMPAIGN_DIRECTORY_WRITE','command':['fixture',key],
            'host':'fixture','disk':'scratch','path':str(succession_root),'stop_conditions':['first-boundary'],
            'bound':{'profile_request':request}}
        digest = campaign.identity(card);reg['approved_cards'][digest] = card
        start.update(permission=card['permission'],approved_card_digest=digest)
    for start, plan in ((start_a,'c1'),(start_b,'c10')): approve_start(attempt_registry,start,plan)
    prior_registry_bytes = campaign.canonical_bytes(attempt_registry)
    attempt_parent = campaign.materialize(succession_root,attempt_registry)
    assert campaign.canonical_bytes(attempt_registry) == prior_registry_bytes
    local = {start_a,first,cp_a,vs_a,vr_a}
    def append_attempt(reg, consumer, prior):
        for family, inputs in reg['families'].items():
            inputs['records'].extend(json.loads(json.dumps(row).replace('ACQ-F4-c1',consumer))
                for row in list(inputs['records']) if row['id'] in local)
        terminal = 'QUALIFY-'+consumer+'-VERIFY'
        reg['families']['physical_qualification']['dimensions']['consumer-flat-id'].append(consumer)
        reg['families']['checkpoint_proof']['dimensions']['operation-start-flat-id'].append('QUALIFY-'+consumer+'-START')
        reg['families']['verification_work']['dimensions']['target-flat-id'].append(terminal)
        next(row for row in reg['families']['physical_qualification']['records']
             if row['id']==terminal)['prior_qualification'] = prior
        approve_start(reg,'QUALIFY-'+consumer+'-START','c1')
        return terminal
    successor_registry = copy.deepcopy(attempt_registry)
    current = append_attempt(successor_registry,'ACQ-F4-c2',first)
    successor_registry['required_owners'][physical_authority] = sorted([second,current])
    successor_registry['families']['source_profile_group'] = {
        'records':[node('SOURCE-PROFILES-ALL-PASS',sorted([second,current]))]}
    successor_registry_bytes = campaign.canonical_bytes(successor_registry)
    successor = campaign.materialize(succession_root,successor_registry,parent=attempt_parent)
    assert campaign.canonical_bytes(successor_registry) == successor_registry_bytes
    assert successor['required_owners'] == {physical_authority:sorted([second,current])}
    assert all(successor['nodes'][key]==value for key,value in attempt_parent['nodes'].items())
    assert successor['nodes']['SOURCE-PROFILES-ALL-PASS']['depends'] == sorted([second,current])
    assert successor['parent_graph_digest'] == attempt_parent['revision_digest']
    attempt_control = succession_root/'control';attempt_control.mkdir()
    attempt_owner = CapacityCoordinator(attempt_control)
    old_head = campaign.publish_graph(attempt_owner,attempt_parent)
    next_head = campaign.publish_graph(attempt_owner,successor,old_head['digest'])
    assert next_head['value']['ancestors'] == [attempt_parent['revision_digest']]
    readonly_start = copy.deepcopy(list(successor['nodes'].values()))
    next(row for row in readonly_start if row['id']==current.removesuffix('-VERIFY')+'-START')['permission'] = 'READ_ONLY'
    with pytest.raises(CassetteError,match='approved action card'):
        campaign.validate_graph(readonly_start,required_owners=successor['required_owners'],parent=attempt_parent,
            materializer=successor['materializer_record_id'],registry_digest=successor['expansion_registry_digest'])
    readonly_prior = copy.deepcopy(list(attempt_parent['nodes'].values()))
    prior_start = next(row for row in readonly_prior if row['id']==start_a)
    prior_start['permission'] = prior_start['approved_card']['permission'] = 'READ_ONLY'
    prior_start['approved_card_digest'] = campaign.identity(prior_start['approved_card'])
    readonly_parent = campaign.validate_graph(readonly_prior,required_owners=attempt_parent['required_owners'])
    readonly_child = [copy.deepcopy(row) for row in successor['nodes'].values()
                      if row['id'] not in attempt_parent['nodes']]
    next_start = next(row for row in readonly_child if row['id']==current.removesuffix('-VERIFY')+'-START')
    next_start['permission'] = next_start['approved_card']['permission'] = 'READ_ONLY'
    next_start['approved_card_digest'] = campaign.identity(next_start['approved_card'])
    campaign.validate_graph([*readonly_prior,*readonly_child],required_owners=successor['required_owners'],
                            parent=readonly_parent)
    for fault in ('missing_digest','foreign_record','missing_command'):
        bad_child = copy.deepcopy(readonly_child)
        bad_start = next(row for row in bad_child if row['id']==next_start['id'])
        if fault=='missing_digest': del bad_start['approved_card_digest']
        else:
            if fault=='foreign_record': bad_start['approved_card']['record_id'] = start_a
            else: del bad_start['approved_card']['command']
            bad_start['approved_card_digest'] = campaign.identity(bad_start['approved_card'])
        with pytest.raises(CassetteError,match='approved action card'):
            campaign.validate_graph([*readonly_prior,*bad_child],required_owners=successor['required_owners'],
                                    parent=readonly_parent)
    for missing in local - {first}:
        prior_records = [{**copy.deepcopy(row),'depends':[key for key in row['depends'] if key!=missing]}
                         for row in attempt_parent['nodes'].values() if row['id']!=missing]
        incomplete_parent = campaign.validate_graph(prior_records,required_owners=attempt_parent['required_owners'])
        child_records = [copy.deepcopy(row) for row in successor['nodes'].values()
                         if row['id'] not in attempt_parent['nodes']]
        with pytest.raises(CassetteError):
            campaign.validate_graph([*prior_records,*child_records],required_owners=successor['required_owners'],
                                    parent=incomplete_parent)
    for missing in ('CHECKPOINT-'+current.removesuffix('-VERIFY')+'-START-RECOVERABILITY',
                    'VERIFY-WORK-'+current+'-START','VERIFY-WORK-'+current+'-RESULT'):
        incomplete = [{**copy.deepcopy(row),'depends':[key for key in row['depends'] if key!=missing]}
                      for row in successor['nodes'].values() if row['id']!=missing]
        with pytest.raises(CassetteError,match='proof targets'):
            campaign.validate_graph(incomplete,required_owners=successor['required_owners'],parent=attempt_parent)
    for fault in ('missing_link','unknown_prior','self_prior','malformed_prior','branch','wrong_plan','wrong_drive',
                  'wrong_shape','wrong_host','wrong_disk','wrong_path','wrong_permission','consumer_mismatch',
                  'malformed_consumer','malformed_request','owner_loss'):
        bad = copy.deepcopy(successor_registry)
        target = next(row for row in bad['families']['physical_qualification']['records'] if row['id']==current)
        start = next(row for row in bad['families']['physical_qualification']['records']
                     if row['id']==current.removesuffix('-VERIFY')+'-START')
        card = bad['approved_cards'][start['approved_card_digest']]
        if fault == 'missing_link': del target['prior_qualification']
        elif fault == 'unknown_prior': target['prior_qualification'] = 'QUALIFY-absent-VERIFY'
        elif fault == 'self_prior': target['prior_qualification'] = current
        elif fault == 'malformed_prior': target['prior_qualification'] = 1
        elif fault == 'branch':
            extra = append_attempt(bad,'ACQ-F4-c3',first)
            bad['required_owners'][physical_authority].append(extra)
        elif fault == 'owner_loss': target['matrix_assertion_owners'] = []
        else:
            request = card['bound']['profile_request']
            if fault == 'wrong_plan': request['plan_digest'] = campaign.identity('foreign')
            elif fault == 'wrong_drive': request['apfs_volume_uuid'] = 'foreign'
            elif fault == 'wrong_shape': request['expected_read_write_shape'][0]['write_bytes'] += 1
            elif fault == 'consumer_mismatch': request['consumer_flat_id'] = 'foreign'
            elif fault == 'malformed_consumer': request['consumer_flat_id'] = 1
            elif fault == 'malformed_request': card['bound']['profile_request'] = []
            elif fault == 'wrong_permission': card['permission'] = start['permission'] = 'PHYSICAL_FAULT'
            else: card[fault.removeprefix('wrong_')] = 'foreign'
            digest = campaign.identity(card);bad['approved_cards'][digest] = card;start['approved_card_digest'] = digest
        with pytest.raises(CassetteError): campaign.materialize(succession_root,bad,parent=attempt_parent)
    consumed_registry = copy.deepcopy(attempt_registry)
    consumed_registry['families']['source_profile_group'] = {
        'records':[node('SOURCE-PROFILES-ALL-PASS',terminals)]}
    consumed = campaign.materialize(succession_root,consumed_registry)
    with pytest.raises(CassetteError,match='consum'):
        campaign.materialize(succession_root,successor_registry,parent=consumed)
    for name,value in [('registry.json',proof_registry),('parent.json',proof_parent),('graph.json',proof_graph),
                       ('observations.json',observations)]:
        (edge_root/name).write_text(json.dumps(value,sort_keys=True))

    # The actual failure authority expands all 80 coordinates and 432 records before publication.
    source_root = Path(__file__).resolve().parent.parent
    actual = json.loads((source_root/'schema/campaign/contract.json').read_text())
    failure = actual['failure_contract']
    family = next(row for row in actual['expanded_session_families'] if row['family'] == 'live_failure')
    _, full_matrix = campaign.load_contracts(source_root)
    matrix = {'failure_rows':full_matrix['failure_rows']}
    contract = {'materialized_record_contract':{'family_evidence_levels':{'live_failure':'LIVE'}},
                'dependency_graph_revision_contract':{},'expanded_session_families':[family]}
    fixed = [node('FAILURE-MATERIALIZE',[])]
    for operation, subject in failure['phase_live_operation_bindings'].items():
        source_id = subject['source_artifact_record']
        if not any(row['id'] == source_id for row in fixed):
            fixed.append({**node(source_id,[]),'artifact_digest':campaign.identity(source_id),
                          'operation_plan_digest':campaign.identity('plan-'+source_id)})
        source = next(row for row in fixed if row['id'] == source_id)
        fixed.append({**node(subject['starting_profile_record'],['FAILURE-MATERIALIZE']),'status':'TODO',
                      'source_artifact_digest':source['artifact_digest'],'operation_plan_digest':source['operation_plan_digest']})
    records, bindings, cards = [], {}, {}
    assertions = campaign.matrix_assertions(matrix)
    for injection in failure['phase_live_injections']:
        for operation, subject in failure['phase_live_operation_bindings'].items():
            source = next(row for row in fixed if row['id'] == subject['source_artifact_record'])
            bound = {'source_artifact_record_id':source['id'],'source_artifact_digest':source['artifact_digest'],
                     'operation_plan_digest':source['operation_plan_digest'],
                     'physical_qualification_record_id':subject['starting_profile_record'],
                     'logical_operation_id':str(campaign.uuid.uuid4()),'state':'PENDING'}
            bindings[injection+':'+operation] = bound
            requalify = injection in failure['requalification_after_recovery']['required_for']
            prefix = 'FAILURE-'+injection+'-'+operation+'-'
            suffixes = ['ARM','INJECT','RECOVER','VERIFY']+(['REQUALIFY_START','REQUALIFY_VERIFY'] if requalify else [])
            for suffix in suffixes:
                edges = {'ARM':['FAILURE-MATERIALIZE',source['id'],subject['starting_profile_record']],
                         'INJECT':[prefix+'ARM'],'RECOVER':[prefix+'INJECT'],
                         'VERIFY':[prefix+'RECOVER']+([prefix+'REQUALIFY_VERIFY'] if requalify else []),
                         'REQUALIFY_START':[prefix+'RECOVER'],'REQUALIFY_VERIFY':[prefix+'REQUALIFY_START']}[suffix]
                permission = 'PHYSICAL_FAULT' if suffix == 'INJECT' and injection in failure['approval_contract']['physical_fault_card_required_for'] else 'CAMPAIGN_DIRECTORY_WRITE'
                key = prefix+suffix
                card = {'record_id':key,'permission':permission,'logical_operation_id':bound['logical_operation_id'],
                        'source_artifact_digest':bound['source_artifact_digest'],'physical_qualification_record_id':subject['starting_profile_record'],
                        'command':['fixture',key],'stop_conditions':['first-boundary'],'disk':'scratch','path':str(tmp_path),'bound':'one atom'}
                digest = campaign.identity(card); cards[digest] = card
                records.append({**node(key,edges,assertions if suffix == 'VERIFY' else []),
                                **{k:v for k,v in bound.items() if k != 'state'}, 'owner_stage':'L09',
                                'requalification_required':requalify,'permission':permission,'approved_card_digest':digest})
    queue = {**contract,'fixed_steps':[{'id':row['id'],'depends':row['depends']} for row in fixed],'operation_records':[]}
    (tmp_path/'IMPLEMENTATION.md').write_text('```yaml\n'+campaign.yaml.safe_dump({'phase_live_queue':queue},sort_keys=False)+'```\n')
    (tmp_path/'research/ACCEPTANCE_MATRIX.yaml').write_text(campaign.yaml.safe_dump(matrix))
    generated = {**contract,'failure_contract':failure,'matrix_axes':{},'assertion_owner_patterns':{'failure_rows':['FAILURE-.+-VERIFY']}}
    (tmp_path/'schema/campaign/contract.json').write_text(json.dumps(generated))
    registry = {'matrix_digest':campaign.file_digest(tmp_path/'research/ACCEPTANCE_MATRIX.yaml'),
                'materializer':'FAILURE-MATERIALIZE','fixed_records':fixed,
                'required_owners':{assertion:sorted(row['id'] for row in records if row['id'].endswith('-VERIFY')) for assertion in assertions},
                'operation_bindings':bindings,'approved_cards':cards,
                'families':{'live_failure':{'dimensions':{'injection':failure['phase_live_injections'],
                    'operation':failure['expand_over_operations'],'record':family['base_records_per_coordinate']+family['requalification_records']},'records':records}}}
    graph = campaign.materialize(tmp_path,registry)
    assert len(records) == 432 and len(bindings) == 80 and len(graph['nodes']) == len(fixed)+432
    for fault in ('source','qualification','terminal','reused','card','permission','omitted_operation'):
        bad = copy.deepcopy(registry)
        selected = next(iter(bad['operation_bindings'].values()))
        if fault == 'source': selected['source_artifact_digest'] = campaign.identity('foreign')
        if fault == 'qualification': selected['physical_qualification_record_id'] = 'foreign'
        if fault == 'terminal': selected['state'] = 'SUCCEEDED'
        if fault == 'reused': list(bad['operation_bindings'].values())[1]['logical_operation_id'] = selected['logical_operation_id']
        if fault == 'card': bad['approved_cards'].clear()
        if fault == 'permission': bad['families']['live_failure']['records'][0]['permission'] = 'UNDECLARED_PERMISSION'
        if fault == 'omitted_operation': bad['families']['live_failure']['dimensions']['operation'] = ['acquisition']
        with pytest.raises(CassetteError): campaign.materialize(tmp_path,bad)
