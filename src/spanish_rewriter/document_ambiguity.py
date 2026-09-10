"""Narrow source-context questions; not an exhaustive word-sense classifier."""

import re

CONTEXTUAL_VERSION = 'contextual-fidelity-v1'
_PROTECTED = re.compile(r'`+[^`]*`+|https?://\S+|«[^»]*»|“[^”]*”|"[^"\n]*"')
_TERM = re.compile(r'\balojamientos?\b', re.IGNORECASE)
_WEB = re.compile(r'\s+(?:web|de\s+(?:sitios?\s+web|servidores?))\b', re.IGNORECASE)
_PEOPLE = re.compile(r'\s+(?:hoteler[oa]s?|en\s+(?:(?:un|el|los)\s+)?hotel(?:es)?'
                     r'|para\s+(?:(?:los|las)\s+)?(?:participantes|personas|huéspedes|viajeros))\b', re.IGNORECASE)


def contextual_issues(source, candidate, locale):
    """Require clarification when direct source qualification is insufficient.

    Indirect context may be meaningful to a reviewer but cannot silently waive
    this conservative rule. Candidate-added context never establishes source facts.
    """
    prose = _PROTECTED.sub(' ', source)
    senses = []
    for match in _TERM.finditer(prose):
        tail = prose[match.end():]
        web, people = _WEB.match(tail), _PEOPLE.match(tail)
        senses.append('web' if web else 'people' if people else None)
        qualifier = web or people
        if qualifier:
            conjunction = re.match(r'\s+(?:y|o)\s+', tail[qualifier.end():], re.IGNORECASE)
            if conjunction:
                alternative = ' ' + tail[qualifier.end() + conjunction.end():]
                if _WEB.match(alternative):
                    senses.append('web')
                if _PEOPLE.match(alternative):
                    senses.append('people')
    if not senses:
        return []
    if None in senses or len(set(senses)) != 1:
        return ['source_ambiguity:alojamiento']
    target = _PROTECTED.sub(' ', candidate)
    if locale in ('en-US', 'en-GB'):
        opposite = r'\b(?:accommodations?|lodging)\b' if senses[0] == 'web' else r'\bhosting\b'
        if re.search(opposite, target, re.IGNORECASE):
            return ['contextual_sense_changed:alojamiento']
    elif locale == 'es-ES':
        pattern = _PEOPLE if senses[0] == 'web' else _WEB
        if any(pattern.match(target[m.end():]) for m in _TERM.finditer(target)):
            return ['contextual_sense_changed:alojamiento']
    return []
