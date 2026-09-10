"""Known conditional-ability miss and conservative exclusion controls."""

from pathlib import Path
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
        self.assertEqual('document-fidelity-v2', transformer().config['fidelity_version'])


if __name__ == '__main__':
    unittest.main()
