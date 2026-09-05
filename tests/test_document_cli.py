import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import rewrite_document


class DocumentCLITests(unittest.TestCase):
    def test_approval_only_with_resume(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
            rewrite_document.main(['--input', 'draft.md', '--approve-spanish', 'a' * 64])
        self.assertEqual(2, result.exception.code)

    def test_both_still_pauses_for_revision_specific_approval(self):
        service = Mock()
        service.proofreaders = {}
        result = dict(phase='awaiting_spanish_approval', generation_complete=False,
                      human_approved=False, revision_sha256='a' * 64,
                      automatic_status='accepted', files={'es-ES': 'spanish.md'},
                      editable_file='spanish.editable.md', review_file='spanish-review.md')
        output = io.StringIO()
        with patch.object(rewrite_document, 'DocumentTransformer', return_value=service), \
             patch.object(rewrite_document, 'start_job', return_value=Path('job')), \
             patch.object(rewrite_document, 'run_job', return_value=result) as run, \
             contextlib.redirect_stdout(output):
            code = rewrite_document.main(['--input', 'draft.md', '--both'])
        self.assertEqual(3, code)
        self.assertIn('a' * 64, output.getvalue())
        self.assertIn('spanish-review.md', output.getvalue())
        self.assertNotIn('desactualizadas', output.getvalue())
        self.assertIsNone(run.call_args.kwargs['approve_spanish'])

    def test_outdated_revisions_are_visible_to_the_user(self):
        service = Mock()
        service.proofreaders = {}
        result = dict(phase='awaiting_spanish_approval', generation_complete=False,
                      human_approved=False, revision_sha256='a' * 64,
                      automatic_status='accepted', files={'es-ES': 'spanish.md'},
                      editable_file='spanish.editable.md', review_file='spanish-review.md',
                      outdated_revisions=['b' * 64, 'c' * 64])
        output = io.StringIO()
        with patch.object(rewrite_document, 'DocumentTransformer', return_value=service), \
             patch.object(rewrite_document, 'start_job', return_value=Path('job')), \
             patch.object(rewrite_document, 'run_job', return_value=result), \
             contextlib.redirect_stdout(output):
            code = rewrite_document.main(['--input', 'draft.md'])
        self.assertEqual(3, code)
        self.assertIn('desactualizadas', output.getvalue())
        self.assertIn('b' * 64, output.getvalue())
        self.assertIn('c' * 64, output.getvalue())

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
