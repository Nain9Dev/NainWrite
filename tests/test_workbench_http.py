"""Loopback request protection must precede private state or mutations."""

import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.workbench import Workbench
from spanish_rewriter.workbench_http import create_server


class WorkbenchHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.server = create_server(Workbench(self.temp.name), port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.open = urllib.request.build_opener(urllib.request.ProxyHandler({})).open

    def test_private_reads_require_token(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.open(self.base + '/api/state')
        self.assertEqual(403, error.exception.code)
        request = urllib.request.Request(self.base + '/api/state', headers={'X-NainWrite-Token':self.server.token})
        with self.open(request) as response:
            self.assertEqual({}, json.load(response)['documents'])

    def test_cross_origin_mutations_and_host_rebinding_are_rejected(self):
        for headers in ({'Origin':'https://example.org'}, {'Host':'attacker.example'}):
            headers.update({'X-NainWrite-Token':self.server.token, 'Content-Type':'application/json'})
            request = urllib.request.Request(self.base + '/api/action', data=b'{"action":"settings","paused":true}', headers=headers)
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.open(request)
            self.assertEqual(403, error.exception.code)

    def test_file_traversal_is_rejected(self):
        request = urllib.request.Request(self.base + '/api/file?path=../secret.txt', headers={'X-NainWrite-Token':self.server.token})
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.open(request)
        self.assertEqual(400, error.exception.code)


if __name__ == '__main__':
    unittest.main()
