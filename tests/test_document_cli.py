import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import rewrite_document


class DocumentCLITests(unittest.TestCase):
    def test_unavailable_proofreader_stops_before_private_generation(self):
        service = Mock()
        proofreader = Mock()
        proofreader.check.side_effect = RuntimeError('proofreader unavailable')
        service.proofreaders = {'es-ES': proofreader, 'en-GB': proofreader}
        with patch.object(rewrite_document, 'DocumentTransformer', return_value=service), \
             patch.object(rewrite_document, 'start_job') as start, \
             patch.object(rewrite_document, 'run_job') as run, \
             contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            code = rewrite_document.main(['--input', 'private-draft.md'])
        self.assertEqual(1, code)
        start.assert_not_called()
        run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
