"""Offline saved image connections, precedence, and standalone request routing."""
import base64
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import openai
from openai import OpenAI

if int(openai.__version__.split('.')[0]) >= 3:
    import httpx2 as httpx
else:
    import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/gpt-image/scripts'))
import generate


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cwd = self.root / 'project'
        self.home = self.root / 'home'
        self.cwd.mkdir()
        self.home.mkdir()
        self.config = self.home / '.config/gpt-image/config.toml'
        self.enterContext(patch.dict(os.environ, {}, clear=True))
        self.enterContext(patch.object(generate.Path, 'cwd', return_value=self.cwd))
        self.enterContext(patch.object(generate.Path, 'home', return_value=self.home))

    def write_config(self, content, path=None):
        target = path if path is not None else self.config
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
        return target

    def parse(self, *flags):
        with patch.object(sys, 'argv', ['generate.py', '-p', 'Offline test', *flags]):
            return generate.parse_args()

    def test_saved_connection_beats_host_connection_across_projects(self):
        self.write_config('api_key = "fake-image-key"\nbase_url = "https://images.example/custom/v1"\n'
                          'model = "gateway-image-alias"\ntimeout = 45\n')
        os.environ.update(OPENAI_API_KEY='fake-host-key', OPENAI_BASE_URL='https://text.example/v1')
        other = self.root / 'another-project'
        other.mkdir()
        for cwd in (self.cwd, other):
            with self.subTest(cwd=cwd), patch.object(generate.Path, 'cwd', return_value=cwd):
                args = self.parse()
                self.assertEqual(args.api_key, 'fake-image-key')
                self.assertEqual(args.base_url, 'https://images.example/custom/v1')
                self.assertEqual(args.model, 'gateway-image-alias')
                self.assertEqual(args.timeout, 45)
        self.assertEqual(os.environ['OPENAI_API_KEY'], 'fake-host-key')

    def test_image_env_and_cli_precedence(self):
        self.write_config('api_key = "fake-config-key"\nbase_url = "https://config.example/v1"\n'
                          'model = "config-alias"\ntimeout = 20\n')
        os.environ.update(GPT_IMAGE_API_KEY='fake-image-env-key', GPT_IMAGE_BASE_URL='https://env.example/v1',
                          GPT_IMAGE_MODEL='env-alias', GPT_IMAGE_TIMEOUT='30')
        args = self.parse()
        self.assertEqual((args.api_key, args.base_url, args.model, args.timeout),
                         ('fake-image-env-key', 'https://env.example/v1', 'env-alias', 30))
        args = self.parse('--base-url', 'https://cli.example/v1', '--model', 'cli-alias', '--timeout', '40')
        self.assertEqual((args.api_key, args.base_url, args.model, args.timeout),
                         ('fake-image-env-key', 'https://cli.example/v1', 'cli-alias', 40))

    def test_explicit_config_and_environment_config_paths(self):
        self.write_config('model = "default-alias"\n')
        selected = self.write_config('model = "selected-alias"\n', self.root / 'selected.toml')
        os.environ['GPT_IMAGE_CONFIG'] = str(selected)
        self.assertEqual(self.parse().model, 'selected-alias')
        self.assertEqual(self.parse('--config', str(self.config)).model, 'default-alias')

    def test_legacy_base_url_precedence(self):
        (self.cwd / '.env').write_text('OPENAI_BASE_URL=https://project.example/v1\n', encoding='utf-8')
        (self.home / '.env').write_text('OPENAI_BASE_URL=https://home.example/v1\n', encoding='utf-8')
        os.environ['OPENAI_BASE_URL'] = 'https://process.example/v1'
        self.assertEqual(self.parse().base_url, 'https://process.example/v1')
        os.environ.pop('OPENAI_BASE_URL')
        self.assertEqual(self.parse().base_url, 'https://project.example/v1')
        os.environ.pop('OPENAI_BASE_URL')
        (self.cwd / '.env').unlink()
        self.assertEqual(self.parse().base_url, 'https://home.example/v1')

    def test_missing_optional_config_keeps_defaults(self):
        args = self.parse()
        self.assertIsNone(args.api_key)
        self.assertEqual(args.base_url, generate.DEFAULT_BASE_URL)
        self.assertEqual(args.model, generate.DEFAULT_MODEL)
        self.assertEqual(args.timeout, generate.DEFAULT_TIMEOUT)

    def test_invalid_config_stops_without_exposing_values(self):
        cases = ('api_key = "fake-secret-not-to-print', 'api_key = 123', 'base_url = ""',
                 'model = ""', 'timeout = true', 'timeout = "oops"', 'timeout = nan',
                 'timeout = 0', 'timeout = []', 'timeout = ' + str(2 ** 2048),
                 'unknown = "fake-secret-not-to-print"')
        for content in cases:
            with self.subTest(content=content):
                self.write_config(content)
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr), patch.object(generate, 'OpenAI') as constructor, \
                     patch.object(sys, 'argv', ['generate.py', '-p', 'Offline test']):
                    with self.assertRaises(SystemExit) as raised:
                        generate.main()
                self.assertEqual(raised.exception.code, 2)
                constructor.assert_not_called()
                self.assertNotIn('fake-secret-not-to-print', stderr.getvalue())

    def test_invalid_saved_timeout_is_not_hidden_by_cli(self):
        self.write_config('timeout = "oops"\n')
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            self.parse('--timeout', '20')
        self.assertEqual(raised.exception.code, 2)

    def test_windows_utf8_bom_config(self):
        self.write_config('\ufeffmodel = "saved-alias"\n')
        self.assertEqual(self.parse().model, 'saved-alias')

    def test_help_does_not_load_bad_config(self):
        self.write_config('api_key = "fake-secret-not-to-print')
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), self.assertRaises(SystemExit) as raised:
            self.parse('--help')
        self.assertEqual(raised.exception.code, 0)
        self.assertIn('--base-url', stdout.getvalue())
        self.assertNotIn('fake-secret-not-to-print', stdout.getvalue())

    def test_missing_explicit_config_does_not_fall_back(self):
        for flags in (['--config', str(self.root / 'missing.toml')], []):
            with self.subTest(flags=flags):
                if not flags:
                    os.environ['GPT_IMAGE_CONFIG'] = str(self.root / 'missing.toml')
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                    self.parse(*flags)
                self.assertEqual(raised.exception.code, 2)

    def test_invalid_url_and_timeout_stop_before_request(self):
        cases = [('--base-url', value) for value in ('', 'gateway.example/v1', 'ftp://example/v1',
                  'https://user:fake-secret@example/v1', 'https://example/v1?token=fake-secret',
                  'https://example/v1#fragment', 'https://example:bad/v1', 'https://example:0/v1',
                  'https://bad host/v1')]
        cases += [('--timeout', value) for value in ('0', '-1', 'nan', 'inf')]
        for flags in cases:
            with self.subTest(flags=flags), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    self.parse(*flags)
                self.assertEqual(raised.exception.code, 2)

    def test_empty_image_key_blocks_paid_fallback(self):
        self.write_config('api_key = "fake-config-key"\n')
        os.environ.update(GPT_IMAGE_API_KEY='', OPENAI_API_KEY='fake-host-key')
        with patch.object(sys, 'argv', ['generate.py', '-p', 'Offline test']), \
             patch.object(generate, 'OpenAI') as constructor, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(generate.main(), 2)
        constructor.assert_not_called()

    def test_copied_script_uses_saved_connection_for_generate_and_edit(self):
        source = Path(generate.__file__)
        copied = self.root / 'installed-skill/scripts/generate.py'
        copied.parent.mkdir(parents=True)
        shutil.copyfile(source, copied)
        spec = importlib.util.spec_from_file_location('copied_generate', copied)
        standalone = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(standalone)
        self.write_config('api_key = "fake-saved-key"\nbase_url = "https://gateway.example/custom/v1"\n'
                          'model = "saved-alias"\ntimeout = 15\n')
        requests = []
        payload = b'offline-image-bytes'
        reference = self.root / 'reference.png'
        reference.write_bytes(payload)

        def respond(request):
            requests.append(request)
            return httpx.Response(200, json={'created': 0, 'data': [
                {'b64_json': base64.b64encode(payload).decode()}]}, request=request)

        def construct(**options):
            self.assertEqual(options, dict(api_key='fake-saved-key', base_url='https://gateway.example/custom/v1',
                                           timeout=15, max_retries=0))
            client = OpenAI(**options, http_client=httpx.Client(transport=httpx.MockTransport(respond)))
            self.addCleanup(client.close)
            return client

        for flags, endpoint in (([], 'generations'), (['-i', str(reference)], 'edits')):
            output = self.root / (endpoint + '.png')
            with patch.object(standalone, 'OpenAI', side_effect=construct), \
                 patch.object(sys, 'argv', [str(copied), '-p', 'Offline test', '-f', str(output), *flags]), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(standalone.main(), 0)
            self.assertEqual(output.read_bytes(), payload)
            request = requests[-1]
            self.assertEqual(str(request.url), 'https://gateway.example/custom/v1/images/' + endpoint)
            self.assertEqual(request.headers['Authorization'], 'Bearer fake-saved-key')
            self.assertEqual(request.extensions['timeout']['read'], 15)
            if endpoint == 'generations':
                self.assertEqual(json.loads(request.content)['model'], 'saved-alias')
            else:
                self.assertIn(b'saved-alias', request.content)
                self.assertIn(b'reference.png', request.content)
        self.assertEqual(len(requests), 2)


if __name__ == '__main__':
    unittest.main()
