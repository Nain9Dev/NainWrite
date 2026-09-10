"""Local queue and exact human gates tested with synthetic model contracts."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.workbench import Workbench
from test_editorial_job import service as synthetic_transformer


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.app = Workbench(self.root, transformer_factory=synthetic_transformer)

    def imported(self):
        key = self.app.upload('draft.txt', b'A report.\n')
        self.app.step()
        return key

    def spanish(self):
        key = self.imported()
        detail = self.app.detail(key)
        self.app.accept_extraction(key, detail['intake']['revision'], 'Reviewed.', True)
        self.app.step()
        return key

    def test_upload_cannot_skip_extraction_or_spanish_approval(self):
        key = self.imported()
        with self.assertRaises(ValueError):
            self.app.translate(key, '0' * 64, 'Reviewed.', True, True)
        detail = self.app.detail(key)
        self.assertEqual('extraction_review', detail['status'])
        self.assertNotIn('result', detail)

    def test_rewrite_pauses_then_explicit_translation_and_final_review(self):
        key = self.spanish()
        detail = self.app.detail(key)
        self.assertEqual('spanish_review', detail['status'])
        self.assertEqual({'es-ES'}, set(detail['exports']))
        revision = detail['result']['revision_sha256']
        with self.assertRaises(ValueError):
            self.app.translate(key, revision, 'There are doubts.', False, True)
        self.app.translate(key, revision, 'Reviewed synthetic text.', True, True)
        self.app.step()
        detail = self.app.detail(key)
        self.assertEqual({'es-ES', 'en-US', 'en-GB'}, set(detail['exports']))
        self.assertEqual({}, detail.get('final_approvals', {}))
        with self.assertRaises(ValueError):
            self.app.approve_final(key, 'en-US', '0' * 64, 'Reviewed.')
        self.app.approve_final(key, 'en-US', detail['exports']['en-US']['text_sha256'], 'Reviewed.')
        self.assertIn('en-US', self.app.detail(key)['final_approvals'])
        self.assertNotEqual('ready', self.app.detail(key)['status'])
        for locale in ('es-ES', 'en-GB'):
            self.app.approve_final(key, locale, detail['exports'][locale]['text_sha256'], 'Reviewed.')
        self.assertEqual('ready', self.app.detail(key)['status'])
        self.app.edit_spanish(key, 'An edited report.\n', detail['spanish_revision'])
        self.assertEqual('spanish_edited', self.app.detail(key)['status'])

    def test_queue_pause_and_restart_preserve_pending_work(self):
        key = self.app.upload('draft.txt', b'A report.\n')
        self.app.settings(paused=True)
        self.assertFalse(self.app.step())
        restored = Workbench(self.root, transformer_factory=synthetic_transformer)
        self.assertEqual('queued', restored.summary()['documents'][key]['status'])
        restored.settings(paused=False)
        self.assertTrue(restored.step())
        self.assertEqual('extraction_review', restored.detail(key)['status'])

    def test_edit_invalidates_translation_and_exports(self):
        key = self.spanish()
        detail = self.app.detail(key)
        old = detail['result']['revision_sha256']
        self.app.edit_spanish(key, 'A revised report.\n', old)
        with self.assertRaises(ValueError):
            self.app.translate(key, old, 'Reviewed.', True, True)
        self.assertEqual({}, self.app.detail(key)['exports'])

    def test_changed_extraction_blocks_downstream_execution(self):
        key = self.spanish()
        detail = self.app.detail(key)
        intake = self.root / detail['intake_path']
        (intake / 'extraction.md').write_text('Different original.\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.app.translate(key, detail['result']['revision_sha256'], 'Reviewed.', True, True)

    def test_night_schedule_and_manual_override(self):
        self.app.settings(mode='scheduled', night_start=22, night_end=7)
        self.assertEqual('intensive', self.app.effective_mode(hour=23))
        self.assertEqual('limited', self.app.effective_mode(hour=12))
        self.app.settings(mode='intensive')
        self.assertEqual('intensive', self.app.effective_mode(hour=12))

    def test_final_review_shows_text_and_repeated_approval_is_idempotent(self):
        key = self.spanish()
        detail = self.app.detail(key)
        artifact = detail['exports']['es-ES']
        self.assertEqual(detail['spanish'], artifact['text'])
        revision = artifact['text_sha256']
        self.app.approve_final(key, 'es-ES', revision, 'Synthetic review.')
        first = self.app.detail(key)['final_approvals']['es-ES']
        self.app.approve_final(key, 'es-ES', revision, 'Repeated request.')
        self.assertEqual(first, self.app.detail(key)['final_approvals']['es-ES'])

    def test_tampered_pdf_cannot_be_downloaded_or_approved(self):
        key = self.spanish()
        artifact = self.app.detail(key)['exports']['es-ES']
        (self.root / artifact['pdf']).write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.app.read_artifact(artifact['pdf'])
        with self.assertRaises(ValueError):
            self.app.approve_final(key, 'es-ES', artifact['text_sha256'], 'Reviewed.')


if __name__ == '__main__':
    unittest.main()
