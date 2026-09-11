"""Known conditional-ability miss and conservative exclusion controls."""

from pathlib import Path
import copy
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.document import literal_issues
from test_document_transform import transformer


class ConditionalModalityTests(unittest.TestCase):
    def test_known_strengthening_is_flagged_despite_positive_model_audits(self):
        source = 'Podríamos entregar el informe si recibimos la aprobación.'
        candidate = 'We can deliver the report if we receive approval.'
        self.assertIn('conditional_modality_changed', literal_issues(source, candidate))
        result = transformer().review([{'id': 'p1', 'text': source}], {'p1': candidate}, 'en-GB', {})
        self.assertEqual('review_required', result['status'])
        self.assertIn('p1:conditional_modality_changed', result['issues'])

    def test_conditional_alternatives_and_protected_mentions(self):
        for source, candidate in (
            ('Podríamos entregar el informe.', 'We could deliver the report.'),
            ('Podrían entregar el informe.', 'They might deliver the report.'),
            ('Podría ser posible.', 'It may be possible.'),
            ('We could deliver.', 'Podríamos entregar.'),
            ('Podemos entregar.', 'We can deliver.'),
            ('The literal `could` can stay.', 'El literal `could` puede quedarse.'),
            ('La etiqueta "podría" puede mantenerse.', 'The label "podría" can remain.'),
        ):
            with self.subTest(source=source):
                self.assertNotIn('conditional_modality_changed', literal_issues(source, candidate))

    def test_rules_are_part_of_configuration_identity(self):
        self.assertEqual('document-fidelity-v3', transformer().config['fidelity_version'])

    def test_another_sentence_cannot_hide_strengthened_commitment(self):
        source = 'Podríamos entregar el informe. También podríamos revisar el contrato.'
        candidate = 'We can deliver the report. We could also review the contract.'
        self.assertIn('conditional_modality_changed', literal_issues(source, candidate))
        result = transformer().review([{'id': 'p1', 'text': source}], {'p1': candidate}, 'en-GB', {})
        self.assertEqual('review_required', result['status'])

    def test_swapped_modal_scope_is_not_just_a_word_count(self):
        source = 'Podríamos entregar el informe. Podemos revisar el contrato.'
        candidate = 'We can deliver the report. We could review the contract.'
        self.assertIn('conditional_modality_changed', literal_issues(source, candidate))

    def test_merged_sentences_do_not_hide_lost_conditional(self):
        source = 'Podríamos entregar el informe. Podríamos revisar el contrato.'
        candidate = 'We can deliver the report and could review the contract.'
        self.assertIn('conditional_modality_changed', literal_issues(source, candidate))

    def test_month_may_is_not_a_possibility_verb(self):
        for target in ('We can deliver in May.', 'We can deliver by May.',
                       'We can deliver on May 15.'):
            self.assertIn('conditional_modality_changed', literal_issues(
                'Podríamos entregar en mayo.', target))

    def test_valid_multiple_sentences_dates_and_modal_may(self):
        for source, target in (
            ('Podríamos entregar. Podemos revisar.', 'We could deliver. We can review.'),
            ('Podríamos entregar. Podríamos revisar.', 'We could deliver and might review.'),
            ('Podríamos entregar en mayo.', 'We may deliver in May.'),
            ('Podríamos entregar en mayo.', 'We could deliver in May.'),
            ('Podemos entregar en mayo.', 'We can deliver in May.'),
            ('Podríamos entregar. La etiqueta es "can".', 'We could deliver. The label is "can".'),
        ):
            with self.subTest(target=target):
                self.assertNotIn('conditional_modality_changed', literal_issues(source, target))

    def test_generation_and_saved_evidence_keep_scope_finding(self):
        from spanish_rewriter.document_evidence import validate_transformation
        worker = transformer()
        original_generate = worker.client.generate_json

        def generate(**kwargs):
            response = original_generate(**kwargs)
            if 'items' in response.content:
                response.content['items'][0]['text'] = (
                    'We can deliver the report. We could review the contract.')
            return response

        worker.client.generate_json = generate
        items = [{'id': 'p1', 'text': 'Podríamos entregar el informe. Podemos revisar el contrato.'}]
        result = worker.transform(items, 'en-GB', {})
        self.assertEqual('review_required', result['status'])
        self.assertTrue(all('p1:conditional_modality_changed' in attempt['issues']
                            for attempt in result['attempts']))
        validate_transformation(result, items, 'en-GB', worker.config)
        changed = copy.deepcopy(result)
        changed['attempts'][-1]['issues'] = []
        changed['issues'] = []
        changed['status'] = 'accepted'
        with self.assertRaises(ValueError):
            validate_transformation(changed, items, 'en-GB', worker.config)


if __name__ == '__main__':
    unittest.main()
