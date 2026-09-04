import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from spanish_rewriter.document import parse_document, make_batches, literal_issues


class DocumentTests(unittest.TestCase):
    def test_markdown_roundtrip_and_order(self):
        source = '# Title\r\n\r\n## 1. Contact\r\n\r\n| Field | Value |\r\n|---|---|\r\n| Code | `x|y` |\r\n\r\n- **Text**: [link](https://example.org/a).\r\n```py\r\nprint(1)\r\n```\r\n'
        manifest = parse_document(source)
        replacements = {p.id: p.text for p in manifest.editable}
        self.assertEqual(source, manifest.assemble(replacements))
        self.assertEqual(manifest, parse_document(source))
        self.assertTrue(any(p.role == 'table_cell' for p in manifest.editable))
        self.assertFalse(any('print(1)' in p.text for p in manifest.editable))
        self.assertEqual(len(manifest.pieces), len({p.id for p in manifest.pieces}))
        for left, right in zip(manifest.pieces, manifest.pieces[1:]):
            self.assertEqual(left.end, right.start)

    def test_missing_extra_and_empty_replacements_fail(self):
        manifest = parse_document('Hello world.\n')
        for values in ({}, {'unknown': 'Text'}, {manifest.editable[0].id: ''}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                manifest.assemble(values)

    def test_notes_have_explicit_source_ranges_and_disclosure_survives(self):
        source = '# Title\nPreparation only.\n## 11. AI disclosure\nAn assistant was used. `[VERIFY: date]`\n| Budget | `[DAVID: amount]` |\n'
        manifest = parse_document(source, clean_notes=True, omit_lines=[(2, 2)])
        result = manifest.assemble({p.id: p.text for p in manifest.editable})
        self.assertIn('## 11. AI disclosure', result)
        self.assertIn('An assistant was used.', result)
        self.assertNotIn('VERIFY', result)
        self.assertNotIn('DAVID', result)
        self.assertNotIn('Preparation', result)
        self.assertEqual(3, len(manifest.removals))
        for removal in manifest.removals:
            self.assertEqual(source[removal['start']:removal['end']], removal['text'])

    def test_cleanup_does_not_erase_numbered_field(self):
        with self.assertRaises(ValueError):
            parse_document('## 11. Disclosure\nA fact.\n', omit_lines=[(1, 2)])

    def test_long_prose_splits_without_cutting_protected_constructs(self):
        source = ('A complete sentence with `value 1.0` and a link https://example.org/test. ' * 60) + '\n'
        manifest = parse_document(source)
        self.assertGreater(len(make_batches(manifest)), 1)
        self.assertEqual(source, manifest.assemble({p.id: p.text for p in manifest.editable}))
        for batch in make_batches(manifest):
            self.assertLessEqual(sum(len(p.text.encode('utf-8')) for p in batch), 1800)
            for p in batch:
                self.assertEqual(0, p.text.count('`') % 2)

    def test_oversized_literal_and_unsafe_markdown_fail(self):
        for source in ('`' + 'x' * 4000 + '`', '```py\nnot closed', '<script>run()</script>'):
            with self.subTest(source=source[:20]), self.assertRaises(ValueError):
                parse_document(source)

    def test_invariants_preserve_counts_numbers_code_links_and_format(self):
        original = '**Use** `rt-01`, 1.0 and https://example.org/a.'
        self.assertEqual([], literal_issues(original, '**Usar** `rt-01`, 1.0 y https://example.org/a.'))
        for candidate in ('**Usar** `rt-02`, 1.0 y https://example.org/a.',
                          '**Usar** `rt-01`, 2.0 y https://example.org/a.',
                          '**Usar** `rt-01`, 1.0 y https://example.org/a. 99',
                          'Usar `rt-01`, 1.0 y https://example.org/a.'):
            with self.subTest(candidate=candidate):
                self.assertTrue(literal_issues(original, candidate))

    def test_txt_does_not_interpret_markdown(self):
        manifest = parse_document('# Literal heading\n| not | a table |\n', markdown=False)
        self.assertTrue(all(p.role == 'prose' for p in manifest.editable))

    def test_relative_links_emphasis_signs_and_currency_are_protected(self):
        for left, right in [('*Required* field.', 'Required field.'),
                            ('[Document](./draft)', '[Document](./final)'),
                            ('-10', '10'), ('100 €', '100 $')]:
            self.assertTrue(literal_issues(left, right))

    def test_ordinary_hyphenated_prose_can_be_translated(self):
        self.assertEqual([], literal_issues('A schema-defined real-time report.', 'Un informe de tiempo real definido por un esquema.'))

    def test_nested_prefix_setext_and_invalid_fences(self):
        manifest = parse_document('> - Required field.\nHeading\n====\n')
        self.assertFalse(any(p.text.startswith('- ') or '====' in p.text for p in manifest.editable))
        for source in ('```text\n```python\nStill code.\n', 'Use `first\nsecond` now.',
                       'See [' + 'word ' * 400 + '](./document).\n'):
            with self.subTest(source=source[:30]), self.assertRaises(ValueError):
                parse_document(source)

    def test_cleanup_protects_all_numbered_heading_variants(self):
        for heading in ('### 1. Disclosure', '## 1) Disclosure', '  ## 1. Disclosure'):
            with self.subTest(heading=heading), self.assertRaises(ValueError):
                parse_document(heading + '\nA fact.\n', omit_lines=[(1, 2)])

    def test_reference_links_are_rejected_until_supported(self):
        for source in ('Read [the guide][guide].\n\n[guide]: ./manual.md\n',
                       'Read [guide][].\n\n[guide]: ./manual.md\n'):
            with self.assertRaises(ValueError):
                parse_document(source)

    def test_notes_are_cleaned_before_sentence_segmentation(self):
        source = 'La propuesta [VERIFY: confirmar] depende de la aprobación.\r\nSe evaluará [DAVID: comprobar].\r\n'
        manifest = parse_document(source, clean_notes=True)
        expected = 'La propuesta depende de la aprobación.\r\nSe evaluará.\r\n'
        self.assertEqual(expected, manifest.assemble({p.id: p.text for p in manifest.editable}))
        self.assertEqual(['La propuesta depende de la aprobación.', 'Se evaluará.'],
                         [p.text for p in manifest.editable])
        self.assertEqual(source, ''.join(p.original_text for p in manifest.pieces))

    def test_cleanup_preserves_tables_code_and_hard_breaks(self):
        source = '| Item | La entrega [VERIFY: fecha] depende del permiso. |\r\n\r\nTexto [DAVID: confirmar], continuación.  \r\n```txt\r\n[VERIFY: literal code]\r\n```\r\n'
        manifest = parse_document(source, clean_notes=True)
        result = manifest.assemble({p.id: p.text for p in manifest.editable})
        self.assertIn('| Item | La entrega depende del permiso. |\r\n', result)
        self.assertIn('Texto, continuación.  \r\n', result)
        self.assertIn('[VERIFY: literal code]', result)
        self.assertEqual(source, ''.join(p.original_text for p in manifest.pieces))

    def test_multiple_notes_and_ambiguous_word_join(self):
        manifest = parse_document('Una [VERIFY: uno] [DAVID: dos] propuesta.', clean_notes=True)
        self.assertEqual('Una propuesta.', manifest.assemble({p.id: p.text for p in manifest.editable}))
        with self.assertRaises(ValueError):
            parse_document('pre[VERIFY: duda]sentación', clean_notes=True)

    def test_cleanup_note_groups_cannot_create_hard_breaks(self):
        for source, expected in [
            ('Text [VERIFY: one] \nNext line.\n', 'Text \nNext line.\n'),
            ('Text [VERIFY: one]  \nNext line.\n', 'Text  \nNext line.\n'),
            ('A [VERIFY: one] [DAVID: two].', 'A.'),
            ('Word [VERIFY: one]\r\n', 'Word\r\n'),
        ]:
            with self.subTest(source=source):
                manifest = parse_document(source, clean_notes=True)
                self.assertEqual(expected, manifest.assemble({p.id: p.text for p in manifest.editable}))
                self.assertEqual(source, ''.join(p.original_text for p in manifest.pieces))

    def test_cleanup_retains_notes_inside_non_editorial_inline_code_and_links(self):
        for source in ['Use `value [VERIFY: literal] suffix`.',
                       '| Value | `value [VERIFY: literal] suffix` |\n',
                       'Read [guide](./path-[VERIFY: literal]).']:
            with self.subTest(source=source):
                manifest = parse_document(source, clean_notes=True)
                self.assertEqual(source, manifest.assemble({p.id: p.text for p in manifest.editable}))
                self.assertEqual([], manifest.removals)


if __name__ == '__main__':
    unittest.main()
