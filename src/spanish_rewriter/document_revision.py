"""Pure conservative mapping of wording-only revisions to original manifest IDs."""

from collections import Counter
from difflib import SequenceMatcher
import re

from .document import literal_issues, protected_literals

_GUIDANCE = "Edit is structural or ambiguous; use smaller wording edits or start a new source job"
_THEMATIC_BREAK = re.compile(r"(?:(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,})")
_SETEXT_UNDERLINE = re.compile(r"[=-]+")
_EMPTY_BLOCK_MARKER = re.compile(r"(?:#{1,6}|[-+])")


def map_revision(manifest, baseline_replacements, edited_text):
    baseline = manifest.assemble(baseline_replacements)
    if not isinstance(edited_text, str) or not edited_text.strip():
        raise ValueError("Empty revision. " + _GUIDANCE)
    if edited_text == baseline:
        return dict(baseline_replacements)
    regions = []
    offset = 0
    for piece in manifest.pieces:
        value = "" if piece.removed else baseline_replacements[piece.id] if piece.editable else piece.text
        if piece.editable:
            regions.append((offset, offset + len(value), piece.id))
        offset += len(value)
    counts = Counter(baseline_replacements.values())
    roles = {piece.id: piece.role for piece in manifest.editable}
    starts = {key: start for start, _end, key in regions}
    protected = [match.span() for literal in set(protected_literals(baseline))
                 for match in re.finditer(re.escape(literal), baseline)]
    edits = {piece.id: [] for piece in manifest.editable}
    for operation, left, right, start, end in SequenceMatcher(None, baseline, edited_text, autojunk=False).get_opcodes():
        if operation == "equal":
            continue
        if any((left < end and start < right) or (left == right and start < left < end)
               for start, end in protected):
            raise ValueError("Edit touches a protected literal. " + _GUIDANCE)
        if any(marker in baseline[left:right] or marker in edited_text[start:end]
               for marker in ('*', '_', '`', '[', ']', '|', '\n', '\r')):
            raise ValueError("Edit touches protected inline structure. " + _GUIDANCE)
        owners = [(a, b, key) for a, b, key in regions
                  if (a <= left and right <= b and left != right)
                  or (left == right and (a < left < b or left == a == 0 or left == b == len(baseline)))]
        if len(owners) != 1:
            raise ValueError(_GUIDANCE)
        a, b, key = owners[0]
        if counts[baseline_replacements[key]] != 1:
            raise ValueError("Repeated prose makes edit ownership ambiguous. " + _GUIDANCE)
        edits[key].append((left - a, right - a, edited_text[start:end]))
    replacements = dict(baseline_replacements)
    for key, operations in edits.items():
        value = replacements[key]
        for left, right, replacement in reversed(operations):
            value = value[:left] + replacement + value[right:]
        if operations:
            if not value.strip() or value != value.strip():
                raise ValueError(_GUIDANCE)
            if literal_issues(replacements[key], value):
                raise ValueError("Edit changes protected literals or inline structure. " + _GUIDANCE)
            if (
                roles[key] == "prose" and (
                    _THEMATIC_BREAK.fullmatch(value)
                    or (_SETEXT_UNDERLINE.fullmatch(value)
                        and _has_preceding_content_line(baseline, starts[key]))
                )
            ) or _is_empty_block_marker(roles[key], value):
                raise ValueError("Edit creates a Markdown structural line. " + _GUIDANCE)
            if re.search(r"<[/!A-Za-z]|\[[^\]]*\]\[|^\s*(?:#{1,6}\s|[-+*>]\s|\d+[.)]\s|```|~~~)", value):
                raise ValueError("Unsupported inline or block structure. " + _GUIDANCE)
            replacements[key] = value
    if manifest.assemble(replacements) != edited_text:
        raise ValueError(_GUIDANCE)
    return replacements


def _has_preceding_content_line(text, start):
    if not _is_full_prose_line(text, start):
        return False
    line_start = text.rfind("\n", 0, start) + 1
    prior_lines = text[:line_start].splitlines()
    return bool(prior_lines and prior_lines[-1].strip())


def _is_full_prose_line(text, start):
    line_start = text.rfind("\n", 0, start) + 1
    return not text[line_start:start].strip()


def _is_empty_block_marker(role, value):
    return _EMPTY_BLOCK_MARKER.fullmatch(value) and (
        role == "prose" or (role == "heading" and value.startswith("#"))
    )
