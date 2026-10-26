import test from 'node:test';
import assert from 'node:assert/strict';
import { splitByLiterals } from '../../src/spanish_rewriter/web/diff.js';
import { EXAMPLES, PHASES, frameFor } from '../../src/spanish_rewriter/web/showcase.js';

const joined = (parts) => parts.map((part) => part.text).join('');

test('UI-001: the showcase replays detect, rewrite and verify, in that order', () => {
  assert.deepEqual(PHASES, ['detect', 'rewrite', 'verify']);
});

test('UI-001: at least three bundled examples, each with a real change to show', () => {
  assert.ok(EXAMPLES.length >= 3);
  for (const example of EXAMPLES) assert.notEqual(example.original, example.revised);
});

test('UI-006: splitting by figures loses no text and marks the figures', () => {
  const text = 'Importe 14.500,00 € con 5% en 60 días.';
  const parts = splitByLiterals(text);

  assert.equal(joined(parts), text);
  assert.deepEqual(parts.filter((part) => part.kind === 'literal').map((part) => part.text), ['14.500,00', '5', '60']);
});

test('UI-001: the detect frame shows the original with its figures marked', () => {
  const example = EXAMPLES[0];
  const frame = frameFor(example, 'detect');

  assert.equal(joined(frame.parts), example.original);
  assert.ok(frame.parts.some((part) => part.kind === 'literal'));
});

test('UI-001: the rewrite frame shows deletions and insertions that rebuild both texts', () => {
  for (const example of EXAMPLES) {
    const frame = frameFor(example, 'rewrite');

    assert.equal(frame.parts.filter((part) => part.kind !== 'ins').map((part) => part.text).join(''), example.original);
    assert.equal(frame.parts.filter((part) => part.kind !== 'del').map((part) => part.text).join(''), example.revised);
    assert.ok(frame.parts.some((part) => part.kind === 'ins'));
  }
});

test('UI-001: the verify frame lists every figure and each one survives the rewrite', () => {
  for (const example of EXAMPLES) {
    const frame = frameFor(example, 'verify');

    assert.equal(joined(frame.parts), example.revised);
    assert.ok(frame.checks.length > 0, example.original);
    assert.ok(frame.checks.every((check) => check.present), example.original);
  }
});
