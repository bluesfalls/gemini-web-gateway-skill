"""Build blank-key WorkBuddy additions from an explicitly supplied model catalog.

Stdlib only. No network, credential discovery, live configuration edit or merge.
"""
import argparse
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

MAX_INPUT = 1024 * 1024
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}\Z')


def clean_text(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError(label)
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError(label)
    return value.strip()


def endpoint(base):
    if not isinstance(base, str) or any(c.isspace() or ord(c) < 32 for c in base):
        raise ValueError('invalid_gateway_url')
    p = urlsplit(base)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username is not None or p.password is not None or p.query or p.fragment:
        raise ValueError('invalid_gateway_url')
    try:
        _ = p.port
    except ValueError:
        raise ValueError('invalid_gateway_port') from None
    path = p.path.rstrip('/')
    if path.endswith('/chat/completions'):
        pass
    elif path.endswith('/v1'):
        path += '/chat/completions'
    else:
        raise ValueError('expected_v1_base_or_chat_endpoint')
    return urlunsplit((p.scheme, p.netloc, path, '', ''))


def build(catalog, base_url, prefix='Gemini 网页 · 对话'):
    if not isinstance(catalog, dict) or not isinstance(catalog.get('data'), list):
        raise ValueError('invalid_model_catalog')
    if not 1 <= len(catalog['data']) <= 1000:
        raise ValueError('invalid_model_count')
    url, label = endpoint(base_url), clean_text(prefix, 'invalid_name_prefix')
    rows, seen = [], set()
    for item in catalog['data']:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not ID.fullmatch(item['id']):
            raise ValueError('invalid_model_id')
        model_id = item['id']
        if model_id in seen:
            raise ValueError('duplicate_model_id')
        seen.add(model_id)
        for field in ('available', 'is_available'):
            if field in item and type(item[field]) is not bool:
                raise ValueError('invalid_availability')
        if item.get('available') is False or item.get('is_available') is False:
            continue
        name = clean_text(item.get('display_name') or item.get('name') or model_id, 'invalid_display_name')
        combined = clean_text(label + ' · ' + name, 'display_name_too_long')
        rows.append({'id': model_id, 'name': combined, 'vendor': 'Custom', 'url': url,
                     'apiKey': '', 'supportsToolCall': False, 'supportsImages': False,
                     'supportsReasoning': False, 'useCustomProtocol': False})
    if not rows:
        raise ValueError('no_eligible_models')
    return rows


def write_new(path, models):
    data = (json.dumps(models, ensure_ascii=False, indent=2) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prefix', default='Gemini 网页 · 对话')
    args = parser.parse_args()
    try:
        with args.catalog.open('rb') as stream:
            data = stream.read(MAX_INPUT + 1)
        if len(data) > MAX_INPUT:
            raise ValueError('catalog_too_large')
        models = build(json.loads(data), args.base_url, args.prefix)
        write_new(args.output, models)
    except FileExistsError:
        parser.exit(2, 'error: output_already_exists\n')
    except (ValueError, OSError) as exc:
        # Never print values or path-bearing exception strings from untrusted input.
        code = str(exc) if type(exc) is ValueError and str(exc) in {
            'invalid_gateway_url', 'invalid_gateway_port', 'expected_v1_base_or_chat_endpoint',
            'invalid_model_catalog', 'invalid_model_count', 'invalid_model_id',
            'duplicate_model_id', 'invalid_availability', 'invalid_display_name',
            'invalid_name_prefix', 'display_name_too_long', 'no_eligible_models', 'catalog_too_large',
        } else 'invalid_input_or_filesystem'
        parser.exit(2, 'error: ' + code + '\n')
    print(json.dumps({'models': len(models), 'api_keys_empty': True, 'live_config_modified': False, 'network_requests': 0}))


if __name__ == '__main__':
    main()
