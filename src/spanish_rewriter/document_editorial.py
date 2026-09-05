"""Narrow, reproducible corporate style findings; never authorship detection."""

import re

EDITORIAL_VERSION = 'corporate-style-v3'
_PROTECTED = re.compile(r'`+[^`]*`+|\[[^\]]*\]\([^)]*\)|«[^»]*»|“[^”]*”|"[^"]*"'
                        r"|‘[^’]*’|(?<!\w)'[^'\n]+'(?!\w)")
_DATA_CALQUE = re.compile(
    r'\b(?:conjunto\s+(?:de\s+)?(?:referencia|datos)|base\s+de\s+datos|dataset)'
    r'\s+(?:(?:ya|aún|todavía)\s+)?(?:está|están|estaba|estaban)\s+'
    r'(?:parcialmente\s+)?poblad[oa]s?\b', re.IGNORECASE)
_EMPTY_EMPHASIS = re.compile(
    r'\b(?:es\s+importante\s+destacar\s+que|cabe\s+destacar\s+que|'
    r'es\s+menester\s+(?:señalar|destacar)\s+que)\b', re.IGNORECASE)
_REDUNDANT_CONFORMANCE = re.compile(
    r'\bpruebas\s+de\s+conformidad\s+(?:comprueban|verifican|evalúan)\s+la\s+conformidad\b',
    re.IGNORECASE)


def editorial_issues(text, locale):
    """Return review flags, without changing text or semantic audit decisions."""
    if locale != 'es-ES':
        return []
    prose = _PROTECTED.sub(' ', text)
    return [f'editorial:{name}' for name, pattern in (
        ('populated_data_calque', _DATA_CALQUE), ('empty_emphasis', _EMPTY_EMPHASIS),
        ('redundant_conformance_definition', _REDUNDANT_CONFORMANCE))
        if pattern.search(prose)]
