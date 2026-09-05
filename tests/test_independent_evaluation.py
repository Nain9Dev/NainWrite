import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.independent_evaluation import select_pawsx, compare_auditors, wilson, load_comparison, blind_review
from spanish_rewriter.calibration import run_experiment
from test_editorial_job import service


def rows():
    return [dict(id=i, sentence1=f'Source sentence {i}.',
                 sentence2=f'Candidate sentence {i}.', label=i % 2) for i in range(40)]


def record(key, expected, first, second):
    def saved(value):
        return dict(audit=None if value is None else dict(
            equivalent=value, confidence=.99, critical_changes=[],
            naturalness_score=5, professional_tone_score=5))
    return dict(case=dict(id=key, expected_equivalent=expected),
                evidence=dict(audits=[saved(first), saved(second)], status='review_required'))


class IndependentEvaluationTests(unittest.TestCase):
    def test_reproducible_balanced_sentence_disjoint_selection(self):
        evaluation, reserve, stats = select_pawsx(rows(), count=8)
        self.assertEqual((evaluation, reserve, stats), select_pawsx(list(reversed(rows())), count=8))
        for bank in (evaluation, reserve):
            self.assertEqual(8, len(bank['cases']))
            self.assertEqual(4, sum(c['expected_equivalent'] for c in bank['cases']))
            self.assertEqual('draft', bank['review_status'])
            self.assertFalse(bank['human_approved'])
            self.assertNotIn('expected_style_acceptable', bank['cases'][0])
        texts = lambda bank: {c[f].casefold() for c in bank['cases'] for f in ('source', 'candidate')}
        self.assertFalse(texts(evaluation) & texts(reserve))

    def test_placeholders_empty_and_oversized_excluded_without_rewriting(self):
        extra = [dict(id=100+i, sentence1=s, sentence2='Other.', label=0)
                 for i, s in enumerate(('NS', 'The NS placeholder.', '', 'é' * 901))]
        evaluation, reserve, stats = select_pawsx(rows() + extra, count=8)
        self.assertEqual(4, stats['excluded_invalid_text'])
        self.assertEqual(40, stats['eligible_rows'])

    def test_duplicate_ids_invalid_labels_and_insufficient_classes_fail(self):
        for data in (rows() + [rows()[0]], [dict(rows()[0], label=True)], rows()[:2]):
            with self.assertRaises(ValueError):
                select_pawsx(data, count=8)
        for count in (0, 3, 102, True):
            with self.assertRaises(ValueError):
                select_pawsx(rows(), count=count)

    def test_external_metadata_and_labels_never_reach_models(self):
        bank, _, _ = select_pawsx(rows(), count=2)
        bank['provenance']['sentinel'] = 'HIDDEN_EXTERNAL_PROVENANCE'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'bank.json'
            path.write_text(json.dumps(bank), encoding='utf-8')
            worker = service()
            run_experiment(path, worker, output_dir=root / 'out')
            calls = str(worker.client.calls)
            for label in ('HIDDEN_EXTERNAL_PROVENANCE', 'expected_equivalent', 'external_id', 'PAWS-X'):
                self.assertNotIn(label, calls)

    def test_comparison_keeps_errors_abstentions_and_disagreement_distinct(self):
        values = [record('X-001', False, True, False),
                  record('X-002', True, True, False),
                  record('X-003', False, False, False),
                  record('X-004', True, None, True)]
        result = compare_auditors(values, ('first', 'second'))
        self.assertEqual(1, result['auditors']['first']['false_equivalence'])
        self.assertEqual(0, result['auditors']['first']['false_drift'])
        self.assertEqual(1, result['auditors']['first']['abstentions'])
        self.assertEqual(1, result['auditors']['second']['false_drift'])
        self.assertEqual(2, result['pairwise']['disagreements'])
        self.assertEqual(3, result['pairwise']['comparable'])
        self.assertEqual(0, result['conservative_semantic_pair']['false_equivalence'])
        self.assertEqual(1, result['conservative_semantic_pair']['false_drift'])
        self.assertEqual(1, result['conservative_semantic_pair']['abstentions'])

    def test_style_or_critical_comments_are_not_semantic_false(self):
        value = record('X-001', True, True, True)
        value['evidence']['audits'][0]['audit']['critical_changes'] = ['A wording comment.']
        value['evidence']['audits'][1]['audit']['naturalness_score'] = 2
        result = compare_auditors([value], ('first', 'second'))
        self.assertEqual(0, result['conservative_semantic_pair']['false_drift'])
        self.assertEqual(0, result['auditors']['first']['strict_accepted'])
        self.assertEqual(0, result['auditors']['second']['strict_accepted'])

    def test_execution_error_not_counted_as_semantic_detection(self):
        value = dict(case=dict(id='X-001', expected_equivalent=False), evidence=None)
        result = compare_auditors([value], ('first', 'second'))
        self.assertEqual(1, result['execution_errors'])
        self.assertEqual(0, result['conservative_semantic_pair']['correct_drift'])
        self.assertEqual(1, result['conservative_semantic_pair']['abstentions'])

    def test_wilson_zero_errors_does_not_claim_zero_risk(self):
        interval = wilson(0, 20)
        self.assertAlmostEqual(0, interval[0])
        self.assertGreater(interval[1], .15)
        self.assertIsNone(wilson(0, 0))

    def test_offline_comparison_rejects_tampered_or_incomplete_evidence(self):
        bank, _, _ = select_pawsx(rows(), count=2)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'bank.json'
            path.write_text(json.dumps(bank), encoding='utf-8')
            job, state = run_experiment(path, service(), output_dir=root / 'out')
            result = load_comparison(job, path)
            self.assertEqual(2, result['cases'])
            (job / 'EXT-001.json').write_text('{}', encoding='utf-8')
            with self.assertRaises(ValueError):
                load_comparison(job, path)

    def test_blind_packet_omits_labels_models_and_scores_and_quotes_source(self):
        bank, _, _ = select_pawsx(rows(), count=2)
        bank['cases'][0]['source'] = 'First line.\n# Untrusted heading\n<script>example</script>'
        packet = blind_review(bank)
        for secret in ('expected_equivalent', 'external_id', 'qwen', 'gemma', 'PAWS-X'):
            self.assertNotIn(secret, packet)
        self.assertIn('> # Untrusted heading', packet)
        self.assertIn('&lt;script&gt;', packet)
        self.assertEqual(2, packet.count('Significado: [ ]'))

    def test_normalized_sentence_overlap_is_excluded(self):
        variants = ['CAFÉ compartido.', 'cafe\u0301 compartido.', 'café   compartido.']
        data = rows() + [dict(id=100+i, sentence1=text, sentence2=f'Alternative {i}.', label=i % 2)
                         for i, text in enumerate(variants)]
        evaluation, reserve, _ = select_pawsx(data, count=20)
        selected = evaluation['cases'] + reserve['cases']
        self.assertEqual(1, sum(c['external_id'] >= 100 for c in selected))
        self.assertEqual(len(selected), len({c['external_id'] for c in selected}))

    def test_comparison_records_and_applies_actual_strict_threshold(self):
        values = [record('X-001', True, True, True)]
        result = compare_auditors(values, ('first', 'second'), semantic_threshold=.995)
        self.assertEqual(.995, result['strict_criteria']['semantic_threshold'])
        self.assertEqual(0, result['auditors']['first']['strict_accepted'])
        self.assertEqual(1, result['auditors']['first']['correct_equivalence'])


if __name__ == '__main__':
    unittest.main()
