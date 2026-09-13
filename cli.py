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
    connect = commands.add_parser('connect', help='Connect publicly or save a masked read token in macOS Keychain.')
    connect.add_argument('--source', choices=['huggingface', 'ollama'], required=True)
    connect.add_argument('--endpoint')
    mode = connect.add_mutually_exclusive_group(required=True)
    mode.add_argument('--public', action='store_true')
    mode.add_argument('--token', action='store_true')
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
    go.add_argument('--model-selection', required=True)
    go.add_argument('--drive-selection', required=True)
    remount = commands.add_parser('watch-remount', help='Wait for physical reconnection and verify the held drive.')
    remount.add_argument('operation_id')
    for command in (models, connect, select, drives, drive, go, remount):
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
                'source': args.source, 'endpoint': endpoint, 'mode': 'token' if args.token else 'public',
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
        elif args.command == 'go':
            request.update(operation='acquire', target=args.drive_selection, arguments={'acquisition': {
                'model_selection_id': args.model_selection, 'drive_selection_id': args.drive_selection}})
            print('Checking the selected source and creating the durable Cassette folder.', file=sys.stderr, flush=True)
            result = asyncio.run(broker.start_download(request))
            if result['state'] == 'PAUSED':
                print('Go paused at the physical drive qualification boundary. Model bytes have not been downloaded.', file=sys.stderr)
        elif args.command == 'watch-remount':
            request.update(operation='drive.remount', target=args.operation_id, arguments={'context_ref': args.operation_id})
            print('Waiting for the selected drive to disconnect and reconnect.', file=sys.stderr, flush=True)
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
