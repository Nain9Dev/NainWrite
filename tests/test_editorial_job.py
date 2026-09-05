import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.editorial_job import run_job, start_job
from spanish_rewriter.document_store import read_state, save_state
from test_document_transform import FakeClient, FakeProofreader
from spanish_rewriter.document_transform import DocumentTransformer


def service(client=None):
    return DocumentTransformer(client or FakeClient(), model='writer', audit_model='auditor',
                               proofreaders={locale: FakeProofreader('es' if locale == 'es-ES' else locale)
                                             for locale in ('es-ES', 'en-GB', 'en-US')})


class EditorialJobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'source.md'
        self.source.write_text('A report.\n', encoding='utf-8')
        self.service = service()
        self.job = start_job(self.source, self.service)

    def gate(self):
        return run_job(self.job, self.service)

    def test_first_completion_requires_exact_spanish_approval(self):
        result = self.gate()
        self.assertEqual('awaiting_spanish_approval', result['phase'])
        self.assertFalse(result['generation_complete'])
        self.assertFalse(result['human_approved'])
        self.assertFalse(any(call[1]['target_locale'].startswith('en-') for call in self.service.client.calls))
        self.assertTrue((self.job / result['editable_file']).is_file())
        self.assertTrue((self.job / result['review_file']).is_file())
        with self.assertRaises(ValueError):
            run_job(self.job, self.service, approve_spanish='0' * 64)

    def test_explicit_synthetic_approval_generates_both_from_same_spanish(self):
        gate = self.gate()
        result = run_job(self.job, self.service, approve_spanish=gate['revision_sha256'])
        self.assertTrue(result['generation_complete'])
        self.assertTrue(result['human_approved'])
        self.assertEqual({'es-ES', 'en-GB', 'en-US'}, set(result['files']))
        rewrites = [data for _, data, _ in self.service.client.calls
                    if data['task'] == 'rewrite' and data['target_locale'].startswith('en-')]
        self.assertEqual(['en-GB', 'en-US'], [d['target_locale'] for d in rewrites])
        self.assertEqual(rewrites[0]['source_items'], rewrites[1]['source_items'])
        self.assertEqual('Un informe.', rewrites[0]['source_items'][0]['text'])
        originals = [data for _, data, _ in self.service.client.calls
                     if data['task'] == 'audit' and data['target_locale'].startswith('en-')
                     and data['source_items'][0]['text'] == 'A report.']
        self.assertEqual(4, len(originals))

    def test_edit_invalidates_authority_and_retains_history(self):
        gate = self.gate()
        complete = run_job(self.job, self.service, approve_spanish=gate['revision_sha256'])
        old = {name: (self.job / name).read_bytes() for name in complete['files'].values()}
        (self.job / gate['editable_file']).write_text('Un informe claro.\n', encoding='utf-8')
        previous = len(self.service.client.calls)
        result = self.gate()
        self.assertFalse(result['human_approved'])
        self.assertFalse(result['generation_complete'])
        self.assertTrue(result['outdated_revisions'])
        self.assertNotEqual(gate['revision_sha256'], result['revision_sha256'])
        self.assertTrue(all(call[1]['task'] == 'audit' and call[1]['target_locale'] == 'es-ES'
                            for call in self.service.client.calls[previous:]))
        for name, raw in old.items():
            self.assertEqual(raw, (self.job / name).read_bytes())

    def test_resume_does_not_repeat_completed_english_generation(self):
        gate = self.gate()
        original = self.service.review
        interrupted = False
        def interrupt(items, replacements, locale, context):
            nonlocal interrupted
            if locale == 'en-GB' and not interrupted:
                interrupted = True
                raise RuntimeError('synthetic interruption')
            return original(items, replacements, locale, context)
        self.service.review = interrupt
        with self.assertRaises(RuntimeError):
            run_job(self.job, self.service, approve_spanish=gate['revision_sha256'])
        result = self.gate()
        self.assertTrue(result['generation_complete'])
        self.assertEqual(1, sum(data['task'] == 'rewrite' and data['target_locale'] == 'en-GB'
                                for _, data, _ in self.service.client.calls))

    def test_review_required_needs_acknowledgement_and_remains_required(self):
        self.service.client.audit_failure = True
        gate = self.gate()
        self.assertEqual('review_required', gate['automatic_status'])
        with self.assertRaises(ValueError):
            run_job(self.job, self.service, approve_spanish=gate['revision_sha256'])
        self.service.client.audit_failure = False
        result = run_job(self.job, self.service, approve_spanish=gate['revision_sha256'],
                         acknowledge_review=True)
        self.assertTrue(result['generation_complete'])
        self.assertEqual('review_required', result['automatic_status'])

    def test_resealed_checkpoint_tampering_is_rejected_before_calls(self):
        gate = self.gate()
        baseline = read_state(self.job)
        cases = []
        changed = copy.deepcopy(baseline)
        changed['configuration_sha256'] = '0' * 64
        cases.append(changed)
        changed = copy.deepcopy(baseline)
        changed['revisions'][gate['revision_sha256']]['approval'] = {'revision_sha256': '0' * 64}
        cases.append(changed)
        changed = copy.deepcopy(baseline)
        changed['revisions'][gate['revision_sha256']]['reviews'][0]['output_hashes'] = {}
        cases.append(changed)
        calls = len(self.service.client.calls)
        for changed in cases:
            with self.subTest(changed=changed.keys()):
                save_state(self.job, changed)
                with self.assertRaises(ValueError):
                    self.gate()
                self.assertEqual(calls, len(self.service.client.calls))
        save_state(self.job, baseline)

    def test_concurrent_edit_during_review_cannot_approve_stale_text(self):
        gate = self.gate()
        editable = self.job / gate['editable_file']
        editable.write_text('Un informe claro.\n', encoding='utf-8')
        original = self.service.review
        def edit(items, replacements, locale, context):
            result = original(items, replacements, locale, context)
            editable.write_text('Un informe diferente.\n', encoding='utf-8')
            return result
        self.service.review = edit
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.gate()
        self.assertFalse(any(data['target_locale'].startswith('en-')
                             for _, data, _ in self.service.client.calls))

    def test_unreviewed_revision_cannot_be_approved_even_with_exact_hash(self):
        from spanish_rewriter.document import sha
        gate = self.gate()
        edited = 'Un informe claro.\n'
        (self.job / gate['editable_file']).write_bytes(edited.encode('utf-8'))
        calls = len(self.service.client.calls)
        with self.assertRaisesRegex(ValueError, 'review'):
            run_job(self.job, self.service, approve_spanish=sha(edited))
        self.assertEqual(calls, len(self.service.client.calls))

    def test_reverting_to_historical_revision_does_not_restore_authority(self):
        gate = self.gate()
        run_job(self.job, self.service, approve_spanish=gate['revision_sha256'])
        editable = self.job / gate['editable_file']
        editable.write_text('Un informe claro.\n', encoding='utf-8')
        self.gate()
        editable.write_text('Un informe.\n', encoding='utf-8')
        result = self.gate()
        self.assertFalse(result['human_approved'])
        self.assertFalse(result['generation_complete'])
        self.assertEqual({'es-ES'}, set(result['files']))

    def test_saved_completion_boolean_is_not_authority(self):
        self.gate()
        state = read_state(self.job)
        state.update(generation_complete=True, human_approved=True)
        save_state(self.job, state)
        result = self.gate()
        self.assertFalse(result['human_approved'])
        self.assertFalse(result['generation_complete'])

    def test_original_crosscheck_failure_is_separate_from_generation(self):
        gate = self.gate()
        original = self.service.review
        def crosscheck(items, replacements, locale, context):
            self.service.client.audit_failure = locale == 'en-US'
            try:
                return original(items, replacements, locale, context)
            finally:
                self.service.client.audit_failure = False
        self.service.review = crosscheck
        result = run_job(self.job, self.service, approve_spanish=gate['revision_sha256'])
        self.assertEqual('review_required', result['automatic_status'])
        stage = read_state(self.job)['revisions'][gate['revision_sha256']]['english']['en-US']
        self.assertEqual('accepted', stage['results'][0]['status'])
        self.assertEqual('review_required', stage['crosschecks'][0]['status'])

    def test_edit_during_english_generation_blocks_publication(self):
        gate = self.gate()
        original = self.service.transform
        def edit(items, locale, context):
            result = original(items, locale, context)
            if locale == 'en-GB':
                (self.job / gate['editable_file']).write_text('Un informe cambiado.\n', encoding='utf-8')
            return result
        self.service.transform = edit
        with self.assertRaisesRegex(ValueError, 'changed'):
            run_job(self.job, self.service, approve_spanish=gate['revision_sha256'])
        self.assertFalse(list(self.job.glob('*.en-GB.md')))
        state = read_state(self.job)
        self.assertIsNone(state['active_approval'])
        self.assertFalse(state['generation_complete'])

    def test_empty_and_overlong_edits_fail_before_new_audit_calls(self):
        gate = self.gate()
        count = len(self.service.client.calls)
        for edited in ('', 'Un informe ' + 'largo ' * 1200 + '.\n'):
            (self.job / gate['editable_file']).write_text(edited, encoding='utf-8')
            with self.assertRaises(ValueError):
                self.gate()
            self.assertEqual(count, len(self.service.client.calls))

    def test_structural_line_edit_fails_before_new_audit_calls(self):
        gate = self.gate()
        count = len(self.service.client.calls)
        (self.job / gate['editable_file']).write_text('---\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.gate()
        self.assertEqual(count, len(self.service.client.calls))

    def test_legacy_checkpoint_requires_new_job_without_model_calls(self):
        state = read_state(self.job)
        state['config']['job_version'] = 'bilingual-job-v2'
        save_state(self.job, state)
        with self.assertRaisesRegex(ValueError, 'Legacy checkpoint'):
            self.gate()
        self.assertEqual([], self.service.client.calls)

    def test_source_change_during_spanish_generation_blocks_baseline_publication(self):
        original = self.service.transform
        def edit(items, locale, context):
            result = original(items, locale, context)
            self.source.write_text('Changed original.\n', encoding='utf-8')
            return result
        self.service.transform = edit
        with self.assertRaisesRegex(ValueError, 'Original document changed'):
            self.gate()
        self.assertFalse((self.job / 'spanish.baseline.md').exists())

    def test_multibatch_spanish_generation_resumes_only_missing_work(self):
        self.source.write_text('\n'.join(f'A sentence with value {number}.' for number in range(25)),
                               encoding='utf-8')
        job = start_job(self.source, self.service)
        original = self.service.transform
        calls = 0
        def interrupt(items, locale, context):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError('synthetic second-batch interruption')
            return original(items, locale, context)
        self.service.transform = interrupt
        with self.assertRaises(RuntimeError):
            run_job(job, self.service)
        self.assertEqual(1, len(read_state(job)['spanish_results']))
        self.service.transform = original
        result = run_job(job, self.service)
        self.assertEqual('awaiting_spanish_approval', result['phase'])
        rewrites = [data for _, data, _ in self.service.client.calls if data['task'] == 'rewrite']
        self.assertEqual(3, len(rewrites))

    def test_missing_or_altered_immutable_snapshot_is_not_recreated(self):
        gate = self.gate()
        snapshot = self.job / gate['files']['es-ES']
        snapshot.write_text('Tampered Spanish.\n', encoding='utf-8')
        calls = len(self.service.client.calls)
        with self.assertRaisesRegex(ValueError, 'artifact differs'):
            self.gate()
        self.assertEqual(calls, len(self.service.client.calls))
        self.assertEqual('Tampered Spanish.\n', snapshot.read_text(encoding='utf-8'))

    def test_invalid_edit_also_revokes_existing_approval(self):
        gate = self.gate()
        run_job(self.job, self.service, approve_spanish=gate['revision_sha256'])
        editable = self.job / gate['editable_file']
        original = editable.read_bytes()
        editable.write_bytes(b'')
        with self.assertRaises(ValueError):
            self.gate()
        editable.write_bytes(original)
        self.assertFalse(self.gate()['human_approved'])

    def test_altered_review_report_blocks_approval_before_generation(self):
        gate = self.gate()
        (self.job / gate['review_file']).write_text('Tampered report.', encoding='utf-8')
        calls = len(self.service.client.calls)
        with self.assertRaises(ValueError):
            run_job(self.job, self.service, approve_spanish=gate['revision_sha256'])
        self.assertEqual(calls, len(self.service.client.calls))


if __name__ == '__main__':
    unittest.main()
