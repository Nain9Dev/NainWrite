"""Local bilingual block transformation with bounded repair and retained evidence."""

from dataclasses import asdict
import re

from .document import FIDELITY_VERSION, literal_issues, protected_literals, sha
from .document_editorial import EDITORIAL_VERSION, editorial_issues
from .document_ambiguity import CONTEXTUAL_VERSION, contextual_issues
from .document_prompts import DOCUMENT_PROMPT_VERSION, DOCUMENT_SCHEMA, TERMINOLOGY, build_prompt
from .language_tool import LanguageToolClient, partition_proofreading_issues
from .prompts import AUDIT_SCHEMA
from .service import DEFAULT_MODEL, DEFAULT_AUDIT_MODEL, AuditValidationError, parse_audit, audit_issues


class DocumentTransformer:
    def __init__(self, client, *, model=DEFAULT_MODEL, audit_model=DEFAULT_AUDIT_MODEL,
                 proofreaders=None):
        self.client = client
        self.model, self.audit_model = model, audit_model
        self.proofreaders = proofreaders if proofreaders is not None else {
            locale: LanguageToolClient(language=locale) for locale in ("es-ES", "en-GB", "en-US")}
        digests = {name: client.get_fresh_model_digest(name) for name in (model, audit_model)}
        if any(not re.fullmatch(r"[a-f0-9]{64}", value) for value in digests.values()):
            raise ValueError("Both installed local model digests must be known")
        if model == audit_model or len(set(digests.values())) != 2:
            raise ValueError("Writer and independent auditor must have distinct model digests")
        self.config = {"prompt_version": DOCUMENT_PROMPT_VERSION, "evidence_contract": "trilingual-review-v2",
                       "editorial_version": EDITORIAL_VERSION, "fidelity_version": FIDELITY_VERSION,
                       "contextual_version": CONTEXTUAL_VERSION,
                       "models": digests,
                       "writer": model, "auditor": audit_model, "max_repairs": 1,
                       "semantic_threshold": 0.95, "minimum_style_score": 5,
                       "terminology": TERMINOLOGY,
                       "ollama_url": client.base_url,
                       "proofreaders": {locale: {"endpoint": p.endpoint, "language": p.language,
                                                 "level": p.level}
                                        for locale, p in self.proofreaders.items()}}

    def _generate(self, model, prompt, schema):
        if self.client.get_fresh_model_digest(model) != self.config["models"][model]:
            raise ValueError("Model identity changed before generation")
        result = self.client.generate_json(model=model, prompt=prompt, schema=schema, num_predict=2048)
        if (result.model_digest != self.config["models"][model]
                or self.client.get_fresh_model_digest(model) != self.config["models"][model]):
            raise ValueError("Model identity changed during generation")
        return result

    @staticmethod
    def _candidate(content, items):
        values = content.get("items")
        if not isinstance(values, list) or type(content.get("uncertain")) is not bool:
            raise ValueError("Invalid document generation contract")
        if any(not isinstance(v, dict) or not isinstance(v.get("text"), str)
               or not v["text"].strip() for v in values):
            raise ValueError("Empty or invalid generated document item")
        if [v.get("id") for v in values] != [i["id"] for i in items]:
            raise ValueError("Missing, duplicated or reordered generated document IDs")
        if sum(len(v["text"].encode("utf-8")) for v in values) > 4800:
            raise ValueError("Candidate exceeds the bounded audit budget")
        return [{"id": v["id"], "text": v["text"].strip()} for v in values]

    def transform(self, items, locale, context):
        if locale not in ("es-ES", "en-GB", "en-US") or locale not in self.proofreaders:
            raise ValueError("A language-appropriate proofreader is required")
        if not items or len({i['id'] for i in items}) != len(items):
            raise ValueError("Source items must be nonempty and uniquely identified")
        attempts = []
        candidate, findings = [], []
        uncertainty = False
        for attempt in range(2):
            generated = self._generate(self.model, build_prompt(
                "rewrite" if attempt == 0 else "repair", locale, items, context, candidate, findings),
                DOCUMENT_SCHEMA)
            candidate = self._candidate(generated.content, items)
            uncertainty |= generated.content["uncertain"]
            issues = [f"{source['id']}:{issue}" for source, target in zip(items, candidate)
                      for issue in literal_issues(source["text"], target["text"])]
            issues.extend(f"{target['id']}:{issue}" for target in candidate
                          for issue in editorial_issues(target['text'], locale))
            issues.extend(f"{source['id']}:{issue}" for source, target in zip(items, candidate)
                          for issue in contextual_issues(source['text'], target['text'], locale))
            text = "\n\n".join(v["text"] for v in candidate)
            proofreading = self.proofreaders[locale].check(text)
            expected = {"es", "es-ES"} if locale == "es-ES" else {locale}
            if proofreading.language not in expected:
                raise ValueError("Proofreader locale does not match the transformation")
            blocking, advisory, ignored = partition_proofreading_issues(
                text, proofreading.issues, protected_literals(text))
            issues.extend(f"language_tool:{i.rule_id}:{i.message}" for i in blocking)
            audits = []
            for audit_model in (self.model, self.audit_model):
                audit_generation = self._generate(audit_model, build_prompt(
                    "audit", locale, items, context, candidate), AUDIT_SCHEMA)
                try:
                    audit = parse_audit(audit_generation.content)
                    issues.extend(audit_issues(audit, .95, 5, prefix=f"{audit_model}:"))
                    audits.append({"generation": asdict(audit_generation), "audit": asdict(audit)})
                except AuditValidationError as error:
                    issues.append(f"{audit_model}:invalid_audit:{error.code}")
                    audits.append({"generation": asdict(audit_generation), "audit": None,
                                   "validation_error": error.code})
            if uncertainty:
                issues.append("writer_reported_uncertainty")
            attempts.append({"generation": asdict(generated), "proofreading": asdict(proofreading),
                             "blocking": [asdict(i) for i in blocking],
                             "advisory": [asdict(i) for i in advisory],
                             "ignored_technical_spelling": [asdict(i) for i in ignored],
                             "audits": audits, "issues": issues})
            if not issues:
                break
            # A bounded repair message never includes unbounded service diagnostics.
            findings = issues if len(str(issues).encode("utf-8")) <= 900 else [
                "One or more literal, grammar, meaning or style checks failed. Recheck every item against source."]
        replacements = {v["id"]: v["text"] for v in candidate}
        return {"replacements": replacements, "status": "review_required" if issues else "accepted",
                "issues": list(issues), "locale": locale, "attempts": attempts,
                "input_hashes": {i["id"]: sha(i["text"]) for i in items},
                "output_hashes": {key: sha(value) for key, value in replacements.items()}}

    def review(self, items, replacements, locale, context):
        """Audit an exact external candidate without generating or repairing it."""
        from .document_review import review
        return review(self, items, replacements, locale, context)
