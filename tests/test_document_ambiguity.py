"""Source-grounded ambiguity regressions independent of positive model audits."""

import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.document_review import validate_review
from spanish_rewriter.document_evidence import validate_transformation
from test_editorial_job import service


class ContextualReviewTests(unittest.TestCase):
    def review(self, source, target, locale='en-US'):
        worker = service()
        items = [{'id': 'p1', 'text': source, 'role': 'prose'}]
        return worker, items, worker.review(items, {'p1': target}, locale, {})

    def test_unqualified_source_requires_context_in_all_locales(self):
        for locale, target in [('es-ES', 'No incluye el alojamiento.'),
                               ('en-US', 'Hosting is not included.'),
                               ('en-GB', 'Accommodation is not included.')]:
            with self.subTest(locale=locale):
                _, _, result = self.review('No incluye el alojamiento.', target, locale)
                self.assertIn('p1:source_ambiguity:alojamiento', result['issues'])
                self.assertEqual('review_required', result['status'])

    def test_explicit_senses_accept_matching_translation(self):
        for source, target in [
            ('No incluye el alojamiento web.', 'Web hosting is not included.'),
            ('No incluye el alojamiento en un hotel.', 'Hotel accommodation is not included.'),
            ('No incluye alojamiento para los participantes.', 'Accommodation for participants is not included.'),
        ]:
            _, _, result = self.review(source, target)
            self.assertEqual('accepted', result['status'])

    def test_opposite_sense_is_detected(self):
        for source, target in [
            ('No incluye el alojamiento web.', 'Accommodation is not included.'),
            ('No incluye alojamiento en un hotel.', 'Hosting is not included.'),
        ]:
            _, _, result = self.review(source, target)
            self.assertIn('p1:contextual_sense_changed:alojamiento', result['issues'])

    def test_unrelated_keywords_and_candidate_explanations_do_not_resolve_source(self):
        for source in ['La web anuncia el encuentro. No incluye el alojamiento.',
                       'El ejemplo dice "alojamiento web". No incluye el alojamiento.',
                       'El alojamiento web o hotelero no está incluido.',
                       'Se ofrece alojamiento web y alojamiento en un hotel. No incluye el alojamiento.']:
            _, _, result = self.review(source, 'Web hosting is not included.')
            self.assertIn('p1:source_ambiguity:alojamiento', result['issues'])

    def test_protected_mentions_do_not_trigger_prose_ambiguity(self):
        for source in ['Conserva `alojamiento`.', 'La etiqueta es "alojamiento".']:
            _, _, result = self.review(source, source, 'es-ES')
            self.assertEqual('accepted', result['status'])

    def test_generation_and_replay_retain_context_question(self):
        worker = service()
        items = [{'id': 'p1', 'text': 'No incluye el alojamiento.', 'role': 'prose'}]
        result = worker.transform(items, 'es-ES', {})
        self.assertIn('p1:source_ambiguity:alojamiento', result['issues'])
        validate_transformation(result, items, 'es-ES', worker.config)
        altered = copy.deepcopy(result)
        altered['issues'] = []
        altered['status'] = 'accepted'
        with self.assertRaises(ValueError):
            validate_transformation(altered, items, 'es-ES', worker.config)

    def test_review_replay_rejects_removed_context_question(self):
        worker, items, result = self.review('No incluye el alojamiento.', 'Hosting is not included.')
        self.assertEqual('contextual-fidelity-v1', worker.config['contextual_version'])
        result['issues'] = []
        result['status'] = 'accepted'
        with self.assertRaises(ValueError):
            validate_review(result, items, 'en-US', worker.config, {})

    def test_job_report_exposes_a_question_before_translation(self):
        from spanish_rewriter.editorial_job import start_job, run_job
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'source.md'
            source.write_text('No incluye el alojamiento.\n', encoding='utf-8')
            worker = service()
            job = start_job(source, worker, output_dir=Path(folder) / 'jobs')
            result = run_job(job, worker)
            report = (job / result['review_file']).read_text(encoding='utf-8')
            self.assertIn('## Dudas de contexto', report)
            self.assertIn('servicio web', report)
            self.assertIn('source_ambiguity:alojamiento', report)
            self.assertEqual('awaiting_spanish_approval', result['phase'])
            self.assertFalse(result['human_approved'])
