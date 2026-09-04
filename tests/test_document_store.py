import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter import document_store as store


def sharing_error():
    error = PermissionError('Synthetic Windows sharing conflict')
    error.winerror = 32
    return error


class DocumentStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.job = Path(self.tmp.name)
        store.save_state(self.job, {'sequence': 1})

    def test_transient_checkpoint_lock_retries_atomic_replace(self):
        replace = store.os.replace
        attempts = []

        def transient(source, target):
            attempts.append((source, target))
            if len(attempts) < 3:
                raise sharing_error()
            return replace(source, target)

        with patch.object(store.os, 'replace', side_effect=transient):
            store.save_state(self.job, {'sequence': 2})
        self.assertEqual(3, len(attempts))
        self.assertEqual({'sequence': 2}, store.read_state(self.job))
        self.assertEqual([], list(self.job.glob('.pending-*')))

    def test_persistent_lock_preserves_prior_state_and_is_not_silenced(self):
        with patch.object(store.os, 'replace', side_effect=sharing_error()) as replacement:
            with self.assertRaises(PermissionError):
                store.save_state(self.job, {'sequence': 2})
        self.assertEqual(6, replacement.call_count)
        self.assertEqual({'sequence': 1}, store.read_state(self.job))
        self.assertEqual([], list(self.job.glob('.pending-*')))

    def test_other_filesystem_errors_are_not_retried(self):
        with patch.object(store.os, 'replace', side_effect=OSError('Unrelated failure')) as replacement:
            with self.assertRaises(OSError):
                store.save_state(self.job, {'sequence': 2})
        self.assertEqual(1, replacement.call_count)
        self.assertEqual({'sequence': 1}, store.read_state(self.job))


if __name__ == '__main__':
    unittest.main()
