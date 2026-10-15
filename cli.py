# cli.py — product command triggers for canonical broker operations (Q9/Q31/Q52); depends on broker.py, errors.py.
"""Expose implemented Cassette operations without a second lifecycle or writer."""

import argparse
import asyncio
import getpass
import json
from pathlib import Path
import sys
import uuid

from broker import CanonicalBroker
from errors import CassetteError


async def _download(broker, request, *, qualification_only=False):
    operation_id = broker.operation_id(request)
    task = asyncio.create_task(broker.start_download(request, qualification_only=qualification_only))
    seen = 0
    while True:
        await asyncio.sleep(.1)
        result = await task if task.done() else None
        events = broker.events(operation_id)
        for event in events[seen:]:
            payload = event['payload']
            if 'source_qualification' in payload:
                print('Drive check: ' + payload['source_qualification']['status'], file=sys.stderr, flush=True)
            if 'received_bytes' in payload:
                print(f"{payload['artifact']}: received {payload['received_bytes']} bytes; "
                      f"readback verified {payload['verified_bytes']} bytes; checkpoint saved.", file=sys.stderr, flush=True)
        seen = len(events)
        if result is not None:
            if result['state'] == 'SUCCEEDED':
                print(f"Download verified: {result['result']['verified_bytes']} bytes; all file digests match.",
                      file=sys.stderr, flush=True)
            return result


def main(argv=None):
    parser = argparse.ArgumentParser(prog='cassette')
    parser.add_argument('--state', type=Path,
                        default=Path.home() / 'Library/Application Support/Cassette')
    commands = parser.add_subparsers(dest='command', required=True)
    models = commands.add_parser('models', help='Search a model source; no model bytes are downloaded.')
    models.add_argument('--source', choices=['huggingface', 'ollama'], default='huggingface')
    models.add_argument('--endpoint', default='https://huggingface.co')
    models.add_argument('--query', default='')
    models.add_argument('--limit', type=int, default=20)
    models.add_argument('--cursor')
    models.add_argument('--connection')
    connect = commands.add_parser('connect', help='Use public access, a masked read token, or an existing Ollama login.')
    connect.add_argument('--source', choices=['huggingface', 'ollama'], required=True)
    connect.add_argument('--endpoint')
    mode = connect.add_mutually_exclusive_group(required=True)
    mode.add_argument('--public', action='store_true')
    mode.add_argument('--token', action='store_true')
    mode.add_argument('--existing-login', action='store_true', help='Reuse the current Ollama account without a new login.')
    select = commands.add_parser('select-model', help='Freeze a model revision and recheck source access.')
    select.add_argument('--connection', required=True)
    select.add_argument('--model', required=True)
    select.add_argument('--revision')
    select.add_argument('--license-acceptance-ref')
    drives = commands.add_parser('drives', help='List mounted APFS drives and observed access.')
    drive = commands.add_parser('select-drive', help='Select a drive and record the content Cassette must preserve.')
    drive.add_argument('--volume', required=True, help='APFS volume UUID from drives.')
    drive.add_argument('--folder', default='Cassette')
    drive.add_argument('--cartridge-uuid')
    go = commands.add_parser('go', help='Start the selected download; first establish durable drive access.')
    qualify = commands.add_parser('qualify', help='Measure the selected download path without starting or continuing payload transfer.')
    for command in (go, qualify):
        command.add_argument('--model-selection', required=True)
        command.add_argument('--drive-selection', required=True)
    remount = commands.add_parser('watch-remount', help='Wait for physical reconnection and verify the held drive.')
    remount.add_argument('operation_id')
    remount.add_argument('--reconnected', action='store_true',
                         help='Report a completed physical reconnect and verify the saved drive data now.')
    for command in (models, connect, select, drives, drive, go, qualify, remount):
        command.add_argument('--key', default=None, help='Reuse this key to reconcile the same operation.')
    status = commands.add_parser('status', help='Read a recorded operation.')
    status.add_argument('operation_id')
    args = parser.parse_args(argv)
    broker = None
    try:
        broker = CanonicalBroker(args.state / 'operations')
        request = {'protocol_version': '1', 'idempotency_key': getattr(args, 'key', None) or str(uuid.uuid4())}
        if args.command == 'models':
            discovery = {key: getattr(args, key) for key in ('source', 'endpoint', 'query', 'limit', 'cursor')}
            if args.connection:
                connection = broker.status(args.connection).get('result', {})
                discovery.update(source=connection.get('source'), endpoint=connection.get('endpoint'),
                                 connection_id=args.connection)
            request.update(operation='source.discover', target=discovery['source'], arguments={'discovery': discovery})
            result = asyncio.run(broker.discover_models(request))
        elif args.command == 'connect':
            endpoint = args.endpoint or {'huggingface': 'https://huggingface.co', 'ollama': 'https://registry.ollama.ai'}[args.source]
            request.update(operation='source.connect', target=args.source, arguments={'connection': {
                'source': args.source, 'endpoint': endpoint,
                'mode': 'existing' if args.existing_login else 'token' if args.token else 'public',
                'credential_ref': None}})
            token = None
            if args.token:
                if not sys.stdin.isatty():
                    parser.error('masked token input requires an interactive terminal')
                token = getpass.getpass('Read token (stored in macOS Keychain): ')
            result = asyncio.run(broker.connect_source(request, token=token))
        elif args.command == 'select-model':
            request.update(operation='source.select', target=args.model, arguments={'selection': {
                'connection_id': args.connection, 'locator': args.model, 'revision': args.revision,
                'license_acceptance_ref': args.license_acceptance_ref}})
            result = asyncio.run(broker.select_model(request))
        elif args.command == 'drives':
            request.update(operation='drive.discover', target='mounted-apfs', arguments={})
            result = asyncio.run(broker.discover_drives(request))
        elif args.command == 'select-drive':
            request.update(operation='drive.select', target=args.volume, arguments={'drive': {
                'volume_uuid': args.volume, 'folder': args.folder, 'cartridge_uuid': args.cartridge_uuid}})
            print('Recording the existing files on the selected drive before Cassette writes.', file=sys.stderr, flush=True)
            result = asyncio.run(broker.select_drive(request))
        elif args.command in {'go', 'qualify'}:
            request.update(operation='acquire', target=args.drive_selection, arguments={'acquisition': {
                'model_selection_id': args.model_selection, 'drive_selection_id': args.drive_selection}})
            print('Checking the selected source and creating the durable Cassette folder.', file=sys.stderr, flush=True)
            result = asyncio.run(_download(broker, request, qualification_only=args.command == 'qualify'))
            if result['state'] == 'PAUSED':
                pause_error = broker.events(result['operation_id'])[-1]['payload'].get('error')
                if pause_error:
                    print(f"{args.command.capitalize()} paused: {pause_error['code']}: {pause_error['detail']}. Retry {args.command} with the same key.", file=sys.stderr)
                elif args.command == 'qualify' and any(
                        event['payload'].get('source_qualification', {}).get('status') == 'PASS'
                        for event in broker.events(result['operation_id'])):
                    print('Drive check passed. Download remains paused.', file=sys.stderr)
                else:
                    print('Go paused at the physical drive qualification boundary. Model bytes have not been downloaded.', file=sys.stderr)
        elif args.command == 'watch-remount':
            request.update(operation='drive.remount', target=args.operation_id, arguments={'context_ref': args.operation_id})
            if args.reconnected:
                request['arguments']['reconnect_confirmed'] = True
            print('Verifying the reconnected drive.' if args.reconnected else
                  'Waiting for the selected drive to disconnect and reconnect.', file=sys.stderr, flush=True)
            result = asyncio.run(broker.watch_drive_remount(request))
        else:
            result = broker.status(args.operation_id)
        print(json.dumps(result, sort_keys=True))
        return {'SUCCEEDED': 0, 'PAUSED': 2}.get(result['state'], 1)
    except CassetteError as error:
        print(json.dumps({'error': error.payload()}, sort_keys=True))
        return 1
    finally:
        if broker is not None:
            broker.close()


if __name__ == '__main__':
    raise SystemExit(main())
