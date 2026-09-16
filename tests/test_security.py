import contextlib
import importlib.util
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('plug', ROOT / 'plug-notas.py')
plug = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plug)


class SecurityTests(unittest.TestCase):
    def config(self):
        env = dict(PLUGNOTAS_API_KEY='synthetic-secret', CNPJ_SERVICO='0',
                   CNPJ_PRODUTO='0', INSCRICAO_MUNICIPAL='0', INSCRICAO_ESTADUAL='0',
                   SERVICE_SHARE='0.7', ISS_RATE='0', PIS_RATE='0', COFINS_RATE='0',
                   PIS_CST='00', SERVICE_DESCRIPTION='synthetic', PRODUCT_DESCRIPTION='synthetic')
        with patch.dict(os.environ, env, clear=True):
            return plug.load_config()

    def test_missing_config(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(ValueError):
            plug.load_config()

    def test_dry_run_does_not_send_or_log_pii(self):
        output = io.StringIO()
        with patch.object(plug.requests, 'post') as post, contextlib.redirect_stdout(output):
            plug.processar_clientes(ROOT / 'clientes_teste.csv', self.config())
        post.assert_not_called()
        self.assertNotIn('Cliente Sintético', output.getvalue())
        self.assertNotIn('synthetic-secret', output.getvalue())

    def test_send_split_and_no_redirects(self):
        with patch.object(plug.requests, 'post', return_value=Mock(status_code=200)) as post:
            plug.processar_clientes(ROOT / 'clientes_teste.csv', self.config(), send=True)
        self.assertEqual(post.call_count, 2)
        self.assertEqual(post.call_args_list[0].kwargs['json'][0]['itens'][0]['valorUnitarioComercial'], 30)
        self.assertEqual(post.call_args_list[1].kwargs['json'][0]['servico']['valor'], 70)
        self.assertFalse(post.call_args.kwargs['allow_redirects'])

    def test_timeout_is_sanitized(self):
        with patch.object(plug.requests, 'post', side_effect=plug.requests.exceptions.Timeout('secret')):
            with self.assertRaisesRegex(RuntimeError, '^Falha de comunicação') as error:
                plug.enviar_para_plugNotas([], 'https://example.invalid', 'synthetic')
        self.assertNotIn('secret', str(error.exception))

    def test_partial_failure_stops_batch(self):
        with patch.object(plug.requests, 'post', return_value=Mock(status_code=500)) as post:
            with self.assertRaises(RuntimeError):
                plug.processar_clientes(ROOT / 'clientes_teste.csv', self.config(), send=True)
        self.assertEqual(post.call_count, 1)
