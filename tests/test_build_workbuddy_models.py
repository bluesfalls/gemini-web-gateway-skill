import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/deploy-gemini-web-gateway/scripts/build_workbuddy_models.py'
spec = importlib.util.spec_from_file_location('workbuddy_template', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
BASE = 'https://gateway.example.invalid/v1'


class TemplateTests(unittest.TestCase):
    def catalog(self):
        return {'data': [{'id': 'demo-fast', 'name': 'Example Fast'}, {'id': 'demo-pro', 'display_name': 'Example Pro'}]}

    def test_preserves_real_ids_without_runtime_prefix(self):
        rows = m.build(self.catalog(), BASE)
        self.assertEqual([v['id'] for v in rows], ['demo-fast', 'demo-pro'])
        self.assertTrue(all(v['url'] == BASE + '/chat/completions' for v in rows))

    def test_blank_keys_and_conservative_capabilities(self):
        for row in m.build(self.catalog(), BASE):
            self.assertEqual(row['apiKey'], '')
            self.assertEqual(row['vendor'], 'Custom')
            for field in ['supportsToolCall', 'supportsImages', 'supportsReasoning', 'useCustomProtocol']:
                self.assertIs(row[field], False)

    def test_extra_fields_never_transfer_credentials(self):
        catalog = self.catalog()
        catalog['apiKey'] = 'SYNTHETIC-not-a-real-secret'
        catalog['data'][0]['apiKey'] = 'SYNTHETIC-not-a-real-secret'
        self.assertNotIn('SYNTHETIC', json.dumps(m.build(catalog, BASE)))

    def test_unavailable_models_excluded(self):
        data = self.catalog()
        data['data'][0]['is_available'] = False
        self.assertEqual([x['id'] for x in m.build(data, BASE)], ['demo-pro'])

    def test_no_eligible_models_rejected(self):
        with self.assertRaisesRegex(ValueError, 'no_eligible_models'):
            m.build({'data': [{'id': 'demo', 'available': False}]}, BASE)

    def test_invalid_rows_rejected(self):
        for catalog in [{}, {'data': []}, {'data': ['wrong']}, {'data': [{'id': ''}]}, {'data': [{'id': 'a\nb'}]}, {'data': [{'id': 'demo', 'available': 'true'}]}]:
            with self.subTest(catalog=catalog), self.assertRaises(ValueError):
                m.build(catalog, BASE)

    def test_duplicate_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate_model_id'):
            m.build({'data': [{'id': 'demo'}, {'id': 'demo'}]}, BASE)

    def test_endpoint_normalization(self):
        self.assertEqual(m.endpoint(BASE + '/'), BASE + '/chat/completions')
        self.assertEqual(m.endpoint(BASE + '/chat/completions/'), BASE + '/chat/completions')
        self.assertEqual(m.endpoint('http://gateway.example.invalid/api/v1'), 'http://gateway.example.invalid/api/v1/chat/completions')

    def test_secret_bearing_or_invalid_urls_rejected(self):
        for url in ['https://name:password@gateway.example.invalid/v1', BASE + '?api_key=demo', BASE + '#demo', 'file:///v1', BASE + '\n', 'https://gateway.example.invalid:bad/v1', 'https://gateway.example.invalid/other']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                m.endpoint(url)

    def test_control_or_oversize_names_rejected(self):
        for name in ['x\ny', 'x' * 257]:
            with self.assertRaises(ValueError):
                m.build({'data': [{'id': 'demo', 'name': name}]}, BASE)

    def test_output_new_private_file_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'additions.json'
            rows = m.build(self.catalog(), BASE)
            m.write_new(path, rows)
            self.assertEqual(json.loads(path.read_text()), rows)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                m.write_new(path, [])
            self.assertEqual(path.read_bytes(), before)

    def test_cli_summary_and_error_do_not_dump_input(self):
        with tempfile.TemporaryDirectory() as td:
            catalog, output = Path(td) / 'catalog.json', Path(td) / 'new.json'
            catalog.write_text(json.dumps(self.catalog()))
            cmd = [sys.executable, str(SCRIPT), '--catalog', str(catalog), '--base-url', BASE, '--output', str(output)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)['models'], 2)
            self.assertFalse(json.loads(result.stdout)['live_config_modified'])
            repeat = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            self.assertEqual(repeat.returncode, 2)
            self.assertEqual(repeat.stderr, 'error: output_already_exists\n')
            catalog.write_text('SYNTHETIC-private-looking-invalid-input')
            invalid = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            self.assertEqual(invalid.returncode, 2)
            self.assertNotIn('SYNTHETIC', invalid.stdout + invalid.stderr)


if __name__ == '__main__':
    unittest.main()
