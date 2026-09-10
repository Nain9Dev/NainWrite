"""Lossless source-span manifests for a conservative Markdown/TXT subset."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import asdict, dataclass


PARSER_VERSION = "document-spans-v2"
FIDELITY_VERSION = "document-fidelity-v2"
_QUOTED = re.compile(r'`+[^`]*`+|https?://\S+|«[^»]*»|“[^”]*”|"[^"\n]*"')
_CONDITIONAL = re.compile(r'\b(?:podría(?:s|mos|is|n)?|could)\b', re.IGNORECASE)
_POSSIBILITY = re.compile(r'\b(?:podría(?:s|mos|is|n)?|could|might|may|would\s+be\s+able\s+to)\b', re.IGNORECASE)
_ABILITY = re.compile(r'\b(?:can|puedo|puedes|puede|podemos|podéis|pueden)\b', re.IGNORECASE)
BATCH_BYTES = 1800
MAX_ITEMS = 12
_LITERALS = re.compile(
    r"`+[^`\r\n]+`+|https?://[^\s<>`\])]+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"
    r"|\]\([^\)\r\n]+\)|\b[\w]+(?:[_.][\w]+)+\b"
    r"|\b[A-Za-z]+-[\w.]*\d[\w.]*\b|\b(?:[a-z]+[A-Z][A-Za-z0-9]*|[A-Z]{2,}[A-Za-z0-9]*)\b"
    r"|(?<!\w)[+−-]?\d+(?:[.,]\d+)*(?:%|\b)|[€$£¥≤≥<>]", re.UNICODE,
)
_NOTES = re.compile(r"`?\[(?:VERIFY|DAVID)\b[^\]\r\n]*\]`?")
_PREFIX = re.compile(r"^(?:\ufeff)?(?:[ \t]*(?:> ?)*(?:#{1,6} +|(?:[-+*]|\d+[.)]) +(?:\[[ xX]\] +)?|(?<=>) ?))")
_LINK = re.compile(r"!?\[[^\]\r\n]*\]\([^\)\r\n]*\)")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def protected_literals(text: str) -> list[str]:
    return [m.group().rstrip(".,;") for m in _LITERALS.finditer(text)]


def literal_issues(source: str, candidate: str) -> list[str]:
    issues = []
    source_prose, candidate_prose = _QUOTED.sub(' ', source), _QUOTED.sub(' ', candidate)
    # This intentionally narrow review flag does not prove modal equivalence.
    if (_CONDITIONAL.search(source_prose) and _ABILITY.search(candidate_prose)
            and not _POSSIBILITY.search(candidate_prose)):
        issues.append('conditional_modality_changed')
    if Counter(protected_literals(source)) != Counter(protected_literals(candidate)):
        issues.append("protected_literals_changed")
    # Syntax is retained by the assembler; inline syntax is the model's responsibility.
    for marker in ("*", "_", "`", "[", "]", "|", "\n", "\r"):
        if source.count(marker) != candidate.count(marker):
            issues.append(f"inline_structure_changed:{marker!r}")
    return issues


@dataclass(frozen=True)
class Piece:
    id: str
    start: int
    end: int
    text: str
    original_text: str
    role: str
    editable: bool
    removed: bool = False

    @property
    def digest(self) -> str:
        return sha(self.text)


@dataclass
class Manifest:
    pieces: list[Piece]
    removals: list[dict]
    source_sha256: str

    @property
    def editable(self) -> list[Piece]:
        return [p for p in self.pieces if p.editable]

    def to_dict(self) -> dict:
        return {"parser_version": PARSER_VERSION, "source_sha256": self.source_sha256,
                "pieces": [dict(asdict(p), sha256=p.digest, original_sha256=sha(p.original_text))
                           for p in self.pieces],
                "removals": self.removals}

    def assemble(self, replacements: dict[str, str]) -> str:
        if set(replacements) != {p.id for p in self.editable}:
            raise ValueError("Replacement coverage differs from the manifest")
        if any(not isinstance(v, str) or not v.strip() for v in replacements.values()):
            raise ValueError("Empty or invalid replacement")
        return "".join("" if p.removed else replacements[p.id] if p.editable else p.text
                       for p in self.pieces)


def _split(text: str, start: int, end: int, limit: int) -> list[tuple[int, int]]:
    spans = []
    while len(text[start:end].encode("utf-8")) > limit:
        protected = [(start + m.start(), start + m.end())
                     for pattern in (_LITERALS, _LINK) for m in pattern.finditer(text[start:end])]
        safe = [start + m.end() for m in re.finditer(r"\s+", text[start:end])
                if not any(a < start + m.end() < b for a, b in protected)
                and len(text[start:start + m.end()].encode("utf-8")) <= limit]
        if not safe:
            raise ValueError("A protected construct exceeds the safe block budget")
        sentence = [n for n in safe if re.search(r"[.!?][\s]+$", text[start:n])]
        cut = sentence[-1] if sentence else safe[-1]
        spans.append((start, cut))
        start = cut
    if start < end:
        spans.append((start, end))
    return spans


def parse_document(text: str, *, markdown: bool = True, clean_notes: bool = False,
                   omit_lines=()) -> Manifest:
    pieces: list[Piece] = []
    removals: list[dict] = []
    lines = text.splitlines(keepends=True)
    if markdown and (re.search(r"\[[^\]\n]+\]\[[^\]\n]*\]", text)
                     or re.search(r"(?m)^\s{0,3}\[[^\]\n]+\]:", text)):
        raise ValueError("Reference-style Markdown links are unsupported; use inline links")
    omitted: set[int] = set()
    for first, last in omit_lines:
        if not 1 <= first <= last <= len(lines):
            raise ValueError("Invalid omitted line range")
        for index in range(first, last + 1):
            if re.match(r"^\s*#{1,6} +\d+[.)]", lines[index - 1]):
                raise ValueError("Cleanup cannot erase a numbered document field")
            omitted.add(index)

    def append(start, end, role, editable=False, removed=False, rendered=None, record=True):
        if start >= end:
            return
        original = text[start:end]
        piece = Piece(f"p{len(pieces):05d}", start, end,
                      original if rendered is None else rendered, original, role, editable, removed)
        pieces.append(piece)
        if removed and record:
            removals.append({"start": start, "end": end, "text": piece.text,
                             "line": text.count("\n", 0, start) + 1, "reason": role})

    def content(start, end, role):
        notes = list(_NOTES.finditer(text, start, end)) if clean_notes else []
        code = list(re.finditer(r"`+[^`\r\n]+`+", text[start:end]))
        links = list(_LINK.finditer(text, start, end))
        notes = [note for note in notes
                 if not any(start + span.start() < note.end() and note.start() < start + span.end()
                            and (start + span.start(), start + span.end()) != note.span() for span in code)
                 and not any(span.start() < note.end() and note.start() < span.end() for span in links)]
        groups = []
        for note in notes:
            if groups and not text[groups[-1][1]:note.start()].strip(" \t"):
                groups[-1] = (groups[-1][0], note.end())
            else:
                groups.append(note.span())
        deleted = set()
        ranges = []
        for note_start, note_end in groups:
            left, right = note_start, note_end
            if left > start and right < end and text[left - 1].isalnum() and text[right].isalnum():
                raise ValueError("Ambiguous word join around an editorial note")
            while left > start and text[left - 1] in " \t":
                left -= 1
            while right < end and text[right] in " \t":
                right += 1
            if right < end and text[right] in ".,;:!?)]}":
                pass
            elif right == end or text[right] in "\r\n":
                # Preserve existing trailing spaces, including deliberate hard breaks.
                right = note_end
            elif left < note_start:
                left = note_start
            else:
                left, right = note_start, note_end
            if ranges and left <= ranges[-1][1]:
                ranges[-1] = (ranges[-1][0], max(right, ranges[-1][1]))
            else:
                ranges.append((left, right))
        for left, right in ranges:
            deleted.update(range(left, right))
            removals.append({"start": left, "end": right, "text": text[left:right],
                             "line": text.count("\n", 0, left) + 1, "reason": "editorial_marker"})
        positions = [i for i in range(start, end) if i not in deleted]
        cleaned = "".join(text[i] for i in positions)
        if not cleaned:
            append(start, end, "editorial_marker", removed=True, record=False)
            return
        segments = []
        for left, right in _split(cleaned, 0, len(cleaned), BATCH_BYTES):
            raw = cleaned[left:right]
            leading = len(raw) - len(raw.lstrip())
            trailing = len(raw) - len(raw.rstrip())
            if not raw.strip():
                segments.append((left, right, "whitespace", False))
                continue
            segments.extend([(left, left + leading, "whitespace", False),
                             (left + leading, right - trailing, role, True),
                             (right - trailing, right, "whitespace", False)])
        segments = [segment for segment in segments if segment[0] < segment[1]]
        cursor = start
        for index, (left, right, segment_role, editable) in enumerate(segments):
            boundary = end if index == len(segments) - 1 else positions[right]
            append(cursor, boundary, segment_role, editable, rendered=cleaned[left:right])
            cursor = boundary

    offset = 0
    fence = None
    for line_no, line in enumerate(lines, 1):
        end = offset + len(line)
        if line_no in omitted:
            append(offset, end, "explicit_preparation_range", removed=True)
            offset = end
            continue
        stripped = line.strip()
        fence_match = re.match(r"^\s*(`{3,}|~{3,})", line) if markdown else None
        if fence_match:
            mark = fence_match[1]
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence) and not line[fence_match.end():].strip():
                fence = None
            append(offset, end, "code_fence")
        elif fence is not None:
            append(offset, end, "code")
        elif markdown and re.match(r"^\s*<(?:[A-Za-z!/])", line):
            raise ValueError("HTML blocks are unsupported; convert them explicitly first")
        elif not stripped or (markdown and (re.fullmatch(r"[-*_= ]{3,}", stripped)
                                           or re.fullmatch(r"[|:\- ]+", stripped))):
            append(offset, end, "separator")
        elif markdown and line.startswith(("    ", "\t")):
            append(offset, end, "indented_code")
        elif markdown and stripped.startswith("|") and stripped.endswith("|"):
            protected = [(m.start(), m.end()) for m in re.finditer(r"`+[^`]+`+|\\\|", line)]
            pipes = [i for i, ch in enumerate(line) if ch == "|" and not any(a <= i < b for a, b in protected)]
            cursor = offset
            for pipe in pipes:
                content(cursor, offset + pipe, "table_cell")
                append(offset + pipe, offset + pipe + 1, "table_delimiter")
                cursor = offset + pipe + 1
            content(cursor, end, "table_cell")
        else:
            if markdown and len(re.findall(r"(?<!\\)`+", line)) % 2:
                raise ValueError("Multiline or unmatched inline code is unsupported")
            prefix = _PREFIX.match(line) if markdown else None
            start = offset + (prefix.end() if prefix else 0)
            append(offset, start, "structural_prefix")
            role = "heading" if markdown and stripped.startswith("#") else "prose"
            content(start, end, role)
        offset = end
    if fence:
        raise ValueError("Unclosed code fence")
    return Manifest(pieces, removals, sha(text))


def make_batches(manifest: Manifest) -> list[list[Piece]]:
    batches: list[list[Piece]] = []
    current: list[Piece] = []
    size = 0
    for piece in manifest.editable:
        weight = len(piece.text.encode("utf-8"))
        if current and (size + weight > BATCH_BYTES or len(current) >= MAX_ITEMS):
            batches.append(current)
            current, size = [], 0
        current.append(piece)
        size += weight
    if current:
        batches.append(current)
    return batches
