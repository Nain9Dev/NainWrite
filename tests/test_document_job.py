import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.document_job import start_job, run_job, _validate_results, _global_checks
from spanish_rewriter.document import parse_document, make_batches
from spanish_rewriter.document_store import read_state, save_state
from test_document_transform import transformer, FakeClient


class DocumentJobTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / 'draft with spaces.md'
        self.source.write_text('# A report.\n\nA report.\n', encoding='utf-8')

    def test_bilingual_output_and_idempotent_resume_preserve_original(self):
        original = self.source.read_bytes()
        service = transformer()
        job = start_job(self.source, service)
        result = run_job(job, service)
        self.assertTrue(result['generation_complete'])
        self.assertFalse(result['human_approved'])
        self.assertEqual(original, self.source.read_bytes())
        self.assertIn('Un informe.', (job / result['files']['es-ES']).read_text(encoding='utf-8'))
        self.assertIn('A report.', (job / result['files']['en-GB']).read_text(encoding='utf-8'))
        count = len(service.client.calls)
        self.assertEqual(result, run_job(job, service))
        self.assertEqual(count, len(service.client.calls))
        en_call = next(c[1] for c in service.client.calls if c[1]['target_locale'] == 'en-GB')
        self.assertTrue(all(i['text'] == 'Un informe.' for i in en_call['source_items']))

    def test_interruption_checkpoints_and_does_not_publish_partial(self):
        service = transformer()
        job = start_job(self.source, service)
        original_transform = service.transform

        def interrupt(items, locale, context):
            if locale == 'en-GB':
                raise RuntimeError('synthetic interruption')
            return original_transform(items, locale, context)

        service.transform = interrupt
        with self.assertRaises(RuntimeError):
            run_job(job, service)
        state = read_state(job)
        self.assertEqual(1, len(state['results']['es-ES']))
        self.assertFalse(state['generation_complete'])
        self.assertEqual([], list(job.glob('*.en-GB.*')))
        count = len(service.client.calls)
        service.transform = original_transform
        self.assertTrue(run_job(job, service)['generation_complete'])
        self.assertEqual(3, len(service.client.calls) - count)

    def test_source_configuration_and_tampered_state_rejected(self):
        service = transformer()
        job = start_job(self.source, service)
        service.config = dict(service.config, prompt_version='changed')
        with self.assertRaises(ValueError):
            run_job(job, service)
        service = transformer()
        self.source.write_text('Changed source', encoding='utf-8')
        with self.assertRaises(ValueError):
            run_job(job, service)
        checkpoint = job / 'checkpoint.json'
        checkpoint.write_text(checkpoint.read_text(encoding='utf-8').replace('Changed source', 'tampered').replace('source_sha256', 'tampered'), encoding='utf-8')
        with self.assertRaises(ValueError):
            read_state(job)

    def test_upstream_review_flags_propagate(self):
        client = FakeClient()
        client.audit_failure = True
        service = transformer(client)
        job = start_job(self.source, service)
        original_transform = service.transform

        def change_auditor(items, locale, context):
            client.audit_failure = locale == 'es-ES'
            return original_transform(items, locale, context)

        service.transform = change_auditor
        result = run_job(job, service)
        self.assertEqual('review_required', result['automatic_status'])
        self.assertIn('review-required', result['files']['en-GB'])
        english = read_state(job)['results']['en-GB'][0]
        self.assertIn('upstream_spanish_review_required', english['issues'])

    def test_unsupported_format_and_invalid_utf8(self):
        for name, content in [('draft.pdf', b'%PDF'), ('draft.txt', b'\xff')]:
            path = self.source.with_name(name)
            path.write_bytes(content)
            with self.assertRaises(ValueError):
                start_job(path, transformer())

    def test_unique_jobs_and_output_collision(self):
        service = transformer()
        first = start_job(self.source, service)
        second = start_job(self.source, service)
        self.assertNotEqual(first, second)
        result = run_job(first, service)
        output = first / result['files']['es-ES']
        output.write_text('User edits must stay', encoding='utf-8')
        with self.assertRaises(ValueError):
            run_job(first, service)
        self.assertEqual('User edits must stay', output.read_text(encoding='utf-8'))

    def test_resume_rejects_forged_coverage_even_with_new_checksum(self):
        service = transformer()
        job = start_job(self.source, service)
        run_job(job, service)
        state = read_state(job)
        state['results']['es-ES'].append(state['results']['es-ES'][0])
        save_state(job, state)
        with self.assertRaises(ValueError):
            run_job(job, service)

    def test_resume_revalidates_evidence_not_just_text_hashes(self):
        service = transformer()
        job = start_job(self.source, service)
        run_job(job, service)
        original = read_state(job)
        mutations = [
            lambda r: r['attempts'][0]['audits'][1]['generation'].update(model_digest='f' * 64),
            lambda r: r['attempts'][0]['audits'][1]['audit'].update(equivalent=False),
            lambda r: r.update(attempts=[{}]),
            lambda r: r.update(locale='en-GB'),
            lambda r: r['attempts'][0]['proofreading'].update(language='en-US'),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                state = json.loads(json.dumps(original))
                mutate(state['results']['es-ES'][0])
                save_state(job, state)
                with self.assertRaises(ValueError):
                    _validate_results(state, make_batches(parse_document(self.source.read_text(encoding='utf-8'))))

    def test_identical_source_headings_report_translation_variants(self):
        manifest = parse_document('### Draft text\nOne claim.\n### Draft text\nAnother claim.\n')
        headings = [p.id for p in manifest.editable if p.role == 'heading']
        values = {p.id: p.text for p in manifest.editable}
        for locale, variants in [('es-ES', ['Texto provisional', 'Texto preliminar']),
                                 ('en-GB', ['Draft text', 'Provisional text'])]:
            values.update(zip(headings, variants))
            findings = _global_checks(manifest, values, locale)['terminology_findings']
            self.assertTrue(any('inconsistent_heading' in item for item in findings))
            self.assertTrue(all(any(block in item for item in findings) for block in headings))
        values.update(dict.fromkeys(headings, 'Draft text'))
        self.assertEqual([], _global_checks(manifest, values, 'en-GB')['terminology_findings'])


if __name__ == '__main__':
    unittest.main()
