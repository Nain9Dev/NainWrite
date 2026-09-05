import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.calibration import run_experiment, summarize
from spanish_rewriter.ollama_client import OllamaError
from test_editorial_job import service


class CalibrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bank = self.root / 'bank.json'
        self.case = dict(id='CASE-001', locale='es-ES', source='A report.', candidate='Un informe.',
                         expected_equivalent=True, reason='HIDDEN_EXPECTED_REASON')
        self.bank.write_text(json.dumps(dict(review_status='draft', cases=[self.case])), encoding='utf-8')

    def test_labels_withheld_and_completed_resume_reuses_verified_results(self):
        worker = service()
        job, result = run_experiment(self.bank, worker, output_dir=self.root / 'out')
        self.assertTrue(result['complete'])
        self.assertEqual(1, result['summary']['valid_automatically_accepted'])
        self.assertNotIn('HIDDEN_EXPECTED_REASON', str(worker.client.calls))
        count = len(worker.client.calls)
        _, resumed = run_experiment(self.bank, worker, resume=job)
        self.assertEqual(result, resumed)
        self.assertEqual(count, len(worker.client.calls))
        (job / 'CASE-001.json').write_text('{}', encoding='utf-8')
        with self.assertRaises(ValueError):
            run_experiment(self.bank, worker, resume=job)

    def test_changed_bank_and_nonboolean_labels_stop_before_inference(self):
        worker = service()
        job, _ = run_experiment(self.bank, worker, output_dir=self.root / 'out')
        self.case['candidate'] = 'Otro informe.'
        self.bank.write_text(json.dumps(dict(review_status='draft', cases=[self.case])), encoding='utf-8')
        count = len(worker.client.calls)
        with self.assertRaises(ValueError):
            run_experiment(self.bank, worker, resume=job)
        self.case['expected_equivalent'] = 'false'
        self.bank.write_text(json.dumps(dict(review_status='draft', cases=[self.case])), encoding='utf-8')
        with self.assertRaises(ValueError):
            run_experiment(self.bank, worker, output_dir=self.root / 'out')
        self.assertEqual(count, len(worker.client.calls))

    def test_execution_errors_are_retained_and_never_count_as_detection(self):
        worker = service()
        worker.review = lambda *args: (_ for _ in ()).throw(OllamaError('length limit'))
        job, result = run_experiment(self.bank, worker, output_dir=self.root / 'out')
        self.assertEqual(1, result['summary']['execution_errors'])
        self.assertEqual(0, result['summary']['valid_automatically_accepted'])
        self.assertFalse(result['quality_gate_passed'])
        _, resumed = run_experiment(self.bank, worker, resume=job)
        self.assertEqual(result, resumed)

    def test_style_only_rejection_is_not_semantic_detection(self):
        record = dict(case=dict(self.case, expected_equivalent=False),
                      evidence=dict(status='review_required', issues=['editorial:empty_emphasis'],
                                    audits=[dict(audit=dict(equivalent=True))]),
                      deterministic_drift=[])
        summary = summarize([record])
        self.assertEqual(0, summary['invalid_semantically_detected'])
        self.assertEqual(0, summary['invalid_automatically_accepted'])
        self.assertEqual(1, summary['invalid_cases'])

    def test_interrupted_run_preserves_completed_cases_and_rejects_configuration_change(self):
        second = dict(self.case, id='CASE-002', source='Another report.', candidate='Otro informe.')
        self.bank.write_text(json.dumps(dict(review_status='draft', cases=[self.case, second])), encoding='utf-8')
        worker = service()
        original_review = worker.review
        def interrupt(items, *args):
            if items[0]['id'] == 'CASE-002':
                raise RuntimeError('synthetic interruption')
            return original_review(items, *args)
        worker.review = interrupt
        with self.assertRaises(RuntimeError):
            run_experiment(self.bank, worker, output_dir=self.root / 'out')
        job = next((self.root / 'out').iterdir())
        count = len(worker.client.calls)
        worker.config['editorial_version'] = 'changed'
        with self.assertRaises(ValueError):
            run_experiment(self.bank, worker, resume=job)
        self.assertEqual(count, len(worker.client.calls))
        worker = service()
        _, result = run_experiment(self.bank, worker, resume=job)
        self.assertEqual(2, len(result['results']))
        self.assertEqual(2, len(worker.client.calls))
        self.assertTrue(all(data['source_items'][0]['id'] == 'CASE-002' for _, data, _ in worker.client.calls))

    def test_semantically_valid_style_control_cannot_hide_false_semantic_rejection(self):
        self.case.update(source='El equipo revisará el alcance.', candidate='Cabe destacar que el equipo revisará el alcance.',
                         expected_style_acceptable=False)
        self.bank.write_text(json.dumps(dict(review_status='draft', cases=[self.case])), encoding='utf-8')
        worker = service()
        worker.client.audit_failure = True
        _, result = run_experiment(self.bank, worker, output_dir=self.root / 'out')
        self.assertEqual(1, result['summary']['valid_semantically_rejected'])
        self.assertFalse(result['quality_gate_passed'])

    def test_invalid_audit_is_an_operational_failure_even_when_other_audit_detects_drift(self):
        self.case['expected_equivalent'] = False
        self.bank.write_text(json.dumps(dict(review_status='draft', cases=[self.case])), encoding='utf-8')
        worker = service()
        worker.client.audit_failure = True
        generate = worker.client.generate_json
        def invalid_one(**kwargs):
            result = generate(**kwargs)
            if kwargs['model'] == 'auditor':
                result.content['confidence'] = 100
            return result
        worker.client.generate_json = invalid_one
        _, result = run_experiment(self.bank, worker, output_dir=self.root / 'out')
        self.assertEqual(1, result['summary']['invalid_semantically_detected'])
        self.assertFalse(result['quality_gate_passed'])
        self.assertEqual(1, result['summary']['invalid_audit_cases'])

    def test_resume_recovers_published_case_before_checkpoint_without_regeneration(self):
        import spanish_rewriter.calibration as module
        worker = service()
        save = module.save_state
        def interrupt(job, state):
            if state['results']:
                raise RuntimeError('interruption after publication')
            save(job, state)
        with patch.object(module, 'save_state', side_effect=interrupt), self.assertRaises(RuntimeError):
            run_experiment(self.bank, worker, output_dir=self.root / 'out')
        job = next((self.root / 'out').iterdir())
        count = len(worker.client.calls)
        _, result = run_experiment(self.bank, worker, resume=job)
        self.assertTrue(result['complete'])
        self.assertEqual(count, len(worker.client.calls))
