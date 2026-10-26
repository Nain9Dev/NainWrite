/**
 * Pure helpers for the visual comparison of the extracted original and the Spanish rewrite
 * (specs/016-client-visual-redesign, UI-005 and UI-006).
 *
 * Everything here runs in the browser over two strings and touches no DOM. It is a visual aid:
 * it never replaces the server review or the human approval.
 */

/** Longest side, in tokens, that gets the word-level comparison; above it the comparison is by line. */
const WORD_CAP = 3000;

const TOKEN = /\s+|\d+(?:[.,]\d+)*|[\p{L}_]+|[^\s]/gu;

/** Splits text into words, numbers with their Spanish separators, punctuation and whitespace runs. */
export function tokenize(text) {
  return text.match(TOKEN) ?? [];
}

/**
 * Word-level comparison. Returns runs of `equal`, `del` and `ins`; concatenating the non-`ins`
 * runs gives the original and the non-`del` runs give the new text.
 */
export function diffWords(original, revised) {
  const a = tokenize(original);
  const b = tokenize(revised);
  return compare(a, b, () => compareLines(original, revised));
}

function compareLines(original, revised) {
  const lines = (text) => text.match(/[^\n]*\n|[^\n]+/g) ?? [];
  const a = lines(original);
  const b = lines(revised);
  return compare(a, b, () => merge([...(original ? [{ type: 'del', text: original }] : []), ...(revised ? [{ type: 'ins', text: revised }] : [])]));
}

function compare(a, b, fallback) {
  let start = 0;
  while (start < a.length && start < b.length && a[start] === b[start]) start += 1;
  let endA = a.length;
  let endB = b.length;
  while (endA > start && endB > start && a[endA - 1] === b[endB - 1]) {
    endA -= 1;
    endB -= 1;
  }

  const middleA = a.slice(start, endA);
  const middleB = b.slice(start, endB);
  if (middleA.length > WORD_CAP || middleB.length > WORD_CAP) return fallback();

  const runs = [
    ...(start ? [{ type: 'equal', text: a.slice(0, start).join('') }] : []),
    ...lcs(middleA, middleB),
    ...(endA < a.length ? [{ type: 'equal', text: a.slice(endA).join('') }] : []),
  ];
  return merge(runs);
}

/** Longest common subsequence weighted by token length, so a whole word beats a lone space. */
function lcs(a, b) {
  const rows = a.length + 1;
  const cols = b.length + 1;
  const table = new Int32Array(rows * cols);

  for (let i = 1; i < rows; i += 1) {
    for (let j = 1; j < cols; j += 1) {
      const up = table[(i - 1) * cols + j];
      const left = table[i * cols + j - 1];
      const diagonal = a[i - 1] === b[j - 1] ? table[(i - 1) * cols + j - 1] + a[i - 1].length : 0;
      table[i * cols + j] = Math.max(up, left, diagonal);
    }
  }

  const reversed = [];
  let i = a.length;
  let j = b.length;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && a[i - 1] === b[j - 1] && table[i * cols + j] === table[(i - 1) * cols + j - 1] + a[i - 1].length) {
      reversed.push({ type: 'equal', text: a[i - 1] });
      i -= 1;
      j -= 1;
    } else if (j > 0 && (i === 0 || table[i * cols + j - 1] >= table[(i - 1) * cols + j])) {
      reversed.push({ type: 'ins', text: b[j - 1] });
      j -= 1;
    } else {
      reversed.push({ type: 'del', text: a[i - 1] });
      i -= 1;
    }
  }
  return reversed.reverse();
}

/** Joins neighbouring runs of one type, and puts a deletion before the insertion that replaces it. */
function merge(runs) {
  const out = [];
  let pendingDel = '';
  let pendingIns = '';

  const flush = () => {
    if (pendingDel) out.push({ type: 'del', text: pendingDel });
    if (pendingIns) out.push({ type: 'ins', text: pendingIns });
    pendingDel = '';
    pendingIns = '';
  };

  for (const run of runs) {
    if (run.type === 'del') pendingDel += run.text;
    else if (run.type === 'ins') pendingIns += run.text;
    else {
      flush();
      const last = out[out.length - 1];
      if (last && last.type === 'equal') last.text += run.text;
      else out.push({ ...run });
    }
  }
  flush();
  return out;
}

/** Number of separate edits: a deletion and the insertion beside it count as one. */
export function countChanges(runs) {
  let count = 0;
  let inChange = false;
  for (const run of runs) {
    if (run.type === 'equal') inChange = false;
    else if (!inChange) {
      count += 1;
      inChange = true;
    }
  }
  return count;
}

const MONTHS = 'enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre';
const DATE = new RegExp(`\\b\\d{1,2} de (?:${MONTHS}) de \\d{4}\\b|\\b\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}\\b`, 'gi');
// Not part of a time (9:00) and not glued to a longer number.
const NUMBER = /(?<![\d:.,])(?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?![\d:])/g;

/**
 * Figures the Spanish text has to keep: dates, currency, percentages and other numbers.
 * Single digits without a currency or percent sign are list numbering, not figures.
 */
export function extractLiterals(text) {
  const seen = new Set();
  return locateLiterals(text)
    .filter((item) => (seen.has(item.literal) ? false : seen.add(item.literal)))
    .map(({ literal, kind }) => ({ literal, kind }));
}

/** Every occurrence of a figure with its position, in reading order: used to highlight them in place. */
export function locateLiterals(text) {
  const dates = [...text.matchAll(DATE)].map((match) => ({ literal: match[0], kind: 'date', start: match.index, end: match.index + match[0].length }));
  const numbers = [];

  for (const match of text.matchAll(NUMBER)) {
    const start = match.index;
    const end = start + match[0].length;
    if (dates.some((date) => start >= date.start && end <= date.end)) continue;

    const after = text.slice(end, end + 6).match(/^\s*(%|€|EUR\b|USD\b|\$|£)/);
    const before = /[€$£]\s*$/.test(text.slice(Math.max(0, start - 3), start));
    const kind = after ? (after[1] === '%' ? 'percent' : 'currency') : before ? 'currency' : 'number';

    if (kind === 'number' && match[0].length < 2) continue;
    numbers.push({ literal: match[0], kind, start, end });
  }

  return [...dates, ...numbers].sort((x, y) => x.start - y.start);
}

/** Splits text into plain and figure parts, so the figures can be wrapped without touching the text. */
export function splitByLiterals(text) {
  const parts = [];
  let cursor = 0;
  for (const { start, end, kind } of locateLiterals(text)) {
    if (start > cursor) parts.push({ text: text.slice(cursor, start), kind: 'plain' });
    parts.push({ text: text.slice(start, end), kind: 'literal', literalKind: kind });
    cursor = end;
  }
  if (cursor < text.length) parts.push({ text: text.slice(cursor), kind: 'plain' });
  return parts;
}

const escape = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

/** Whether each literal of the original occurs verbatim in the Spanish text, as a whole figure. */
export function literalPresence(original, spanish) {
  return extractLiterals(original).map(({ literal, kind }) => {
    const pattern = kind === 'date' ? new RegExp(escape(literal)) : new RegExp(`(?<![\\d.,])${escape(literal)}(?!\\d|[.,]\\d)`);
    return { literal, kind, present: pattern.test(spanish) };
  });
}
