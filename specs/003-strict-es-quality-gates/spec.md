# Strict es-ES Quality Gates Specification

Status: Draft
Target locale: `es-ES`

## Purpose

Strengthen NainWrite ES without weakening semantic preservation. The system shall keep Qwen3.8-27B as the writer, add an independent semantic auditor, add local deterministic proofreading and test known-invalid candidates rather than validating only model-produced rewrites.

## Observed baseline

- The final 30-case run accepted every case twice with exact output stability.
- `ESRW-006` received only `4/5` for naturalness and contained avoidable repetition.
- Writer and semantic auditor used the same model, so their errors could be correlated.
- No independent spelling or grammar checker was present.
- The existing benchmark contained valid rewrite targets but no executable bank of intentionally invalid candidates.

## Scope

### In scope

- Local LanguageTool proofreading through a loopback-only HTTP endpoint.
- An independent installed model for a second semantic audit.
- Strict `5/5` naturalness and professional-tone thresholds for automatic acceptance.
- An adversarial candidate bank covering semantic mutations.
- Spanish labels in the generated human-review sheet.
- Reproducible comparison with the existing baseline.

### Out of scope

- Cloud proofreading or inference.
- Automatic application of LanguageTool suggestions.
- Model fine-tuning.
- Spanish-to-English translation.
- Docker changes or reuse of the occupied local port `8081`.
- A claim of mathematically perfect semantic equivalence.

## Requirements

### Local proofreading

- `REQ-033`: The proofreader shall accept only an HTTP endpoint on `127.0.0.1`, `localhost` or `::1`.
- `REQ-034`: The default LanguageTool endpoint shall use port `8082` because port `8081` is occupied by an unrelated local service on the target workstation.
- `REQ-035`: The client shall reject non-JSON responses and responses that do not identify LanguageTool.
- `REQ-036`: The request shall declare Spanish explicitly and shall never use the public LanguageTool API.
- `REQ-037`: Proofreading findings shall be returned as structured issues with rule identifier, issue type, message, offset, length and replacements.
- `REQ-038`: Spelling, grammar and typographical findings shall require review unless the finding overlaps an exact protected or automatically detected technical literal.
- `REQ-039`: LanguageTool shall be advisory for subjective style findings; the model quality gates remain authoritative for naturalness and professional tone.
- `REQ-040`: If the required local proofreader is unavailable or invalid, the service shall fail closed.

### Independent audit

- `REQ-041`: Automatic acceptance shall require both the writer-model audit and an audit from a separately configured installed model.
- `REQ-042`: Each auditor shall independently meet the semantic confidence, naturalness and professional-tone thresholds.
- `REQ-043`: The default strict style threshold shall be `5/5`.
- `REQ-044`: Reports shall identify every writer and auditor model and digest.

### Adversarial evaluation

- `REQ-045`: A versioned mutation bank shall contain candidates with changed negation, modality, actor, condition, quantity, date, causality or ambiguity.
- `REQ-046`: Every P0 invalid candidate shall be rejected by at least one deterministic or semantic gate.
- `REQ-047`: Valid controls shall remain accepted to detect an always-rejecting auditor.
- `REQ-048`: The mutation runner shall produce a machine-readable report and continue after a rejected candidate.

### Review usability

- `REQ-049`: Human-review sheets shall label source, Qwen output and proposed reference unambiguously in Spanish.
- `REQ-050`: A generated report shall remain preliminary until Aitor approves the references and outputs.

### Evidence integrity

- `REQ-051`: If an audit omits a required field or returns a value of the wrong type, the runtime shall reject the response through a controlled validation error.
- `REQ-052`: An empty candidate or an empty mutation bank shall never pass evaluation.
- `REQ-053`: An invalid mutation shall count as detected only when a deterministic invariant check or a valid semantic audit identifies drift; a spelling or style rejection alone shall not satisfy the mutation gate.
- `REQ-054`: When a benchmark completes a case, the runner shall atomically save a local partial report so an interrupted execution does not lose completed evidence.
- `REQ-055`: The mutation runner shall evaluate source and candidate without required-meaning or forbidden-change hints by default, and shall identify an explicitly assisted run in the report.
- `REQ-056`: The strict rewrite benchmark shall require acceptance of every result in every run; a rejected lower-priority case shall not be hidden by a successful P0 summary.
- `REQ-057`: When local proofreading reports blocking language findings, the writer may make exactly one constrained linguistic repair from the original source; the runtime shall rerun invariant checks, proofreading and both audits before acceptance.
- `REQ-058`: The linguistic repair shall not blindly apply suggested replacements, shall not run when proofreading is unavailable, and shall preserve both the initial proofreading evidence and the repair generation.
- `REQ-059`: Before requesting inference, the client shall reject a prompt larger than 12000 UTF-8 bytes, preserving a conservative budget within the configured 16384-token context for the measured local model templates and output allowance. Arbitrarily long document rewriting is not supported in this slice.
- `REQ-060`: If Ollama reports that generation ended because of a length limit, the client shall reject the result even if its JSON is syntactically valid.
- `REQ-061`: Local HTTP clients shall ignore environment/system proxies and reject HTTP redirects rather than forwarding source text outside the configured loopback service.
- `REQ-062`: If a proofreading finding omits its issue type or rule identifier, the client shall reject the response rather than treating it as advisory.
- `REQ-063`: The strict service shall reject configurations that disable required proofreading or the independent auditor; the candidate evaluator shall require at least two distinct auditors.

## Exit criteria

- Unit tests cover proofreader endpoint security, response validation, finding classification and dual-audit orchestration.
- LanguageTool runs locally without modifying existing Docker services.
- The existing 30-case benchmark completes twice with all changes disclosed.
- The adversarial mutation suite rejects every P0 invalid candidate and accepts its valid controls.
- Documentation records measured false positives, failures and performance impact.
- No generated report, model weight or local tool installation is committed.

## Safety boundary

LanguageTool and model audits are fallible. A clean automatic result means that configured checks found no issue; it does not authorize publishing or signing high-impact text without human review.
