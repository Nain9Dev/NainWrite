import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.document_review import validate_review
from test_editorial_job import service


class DocumentReviewTests(unittest.TestCase):
    items = [{'id': 'p1', 'text': 'A report.', 'role': 'prose'}]

    def test_review_only_has_genuine_audits_and_no_rewrite(self):
        worker = service()
        result = worker.review(self.items, {'p1': 'Un informe.'}, 'es-ES', {})
        self.assertEqual('review-only-v1', result['evidence_type'])
        self.assertNotIn('attempts', result)
        self.assertNotIn('generation', result)
        self.assertEqual(['writer', 'auditor'], [model for model, _, _ in worker.client.calls])
        self.assertTrue(all(data['task'] == 'audit' for _, data, _ in worker.client.calls))
        validate_review(result, self.items, 'es-ES', worker.config, {})

    def test_american_proofreading_and_wrong_locale_rejection(self):
        from spanish_rewriter.language_tool import LanguageToolClient
        self.assertEqual('en-US', LanguageToolClient(language='en-US').language)
        worker = service()
        result = worker.transform(self.items, 'en-US', {})
        self.assertEqual('en-US', result['attempts'][0]['proofreading']['language'])
        worker.proofreaders['en-US'].language = 'en-GB'
        with self.assertRaises(ValueError):
            worker.review(self.items, {'p1': 'A report.'}, 'en-US', {})
        with self.assertRaises(ValueError):
            worker.transform(self.items, 'en-US', {})

    def test_invalid_confidence_is_review_required(self):
        worker = service()
        worker.client.invalid_audit = True
        result = worker.review(self.items, {'p1': 'Un informe.'}, 'es-ES', {})
        self.assertEqual('review_required', result['status'])
        self.assertIn('confidence_out_of_range', str(result['issues']))
        validate_review(result, self.items, 'es-ES', worker.config, {})

    def test_candidate_hash_audit_response_and_prompt_tampering_rejected(self):
        worker = service()
        original = worker.review(self.items, {'p1': 'Un informe.'}, 'es-ES', {})
        changed = copy.deepcopy(original)
        changed['output_hashes']['p1'] = '0' * 64
        with self.assertRaises(ValueError):
            validate_review(changed, self.items, 'es-ES', worker.config, {})
        changed = copy.deepcopy(original)
        changed['audits'][0]['generation']['content']['confidence'] = 100
        with self.assertRaises(ValueError):
            validate_review(changed, self.items, 'es-ES', worker.config, {})
        changed = copy.deepcopy(original)
        changed['audits'][0]['prompt_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            validate_review(changed, self.items, 'es-ES', worker.config, {})
