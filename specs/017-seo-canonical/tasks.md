# Task Handoff - SEO Canonical URL

## Tasks

- [x] `[A]` T-001 Failing test in `tests/test_web_client.py` for SEO-001 and SEO-002.
- [x] `[A]` T-002 Add the canonical link to `src/spanish_rewriter/web/index.html`.
- [x] `[A]` T-003 Traceability rows in `docs/07-traceability.md`.
- [x] `[H]` T-004 Always Use HTTPS enabled in the Cloudflare zone `naindev.com` (2026-11-09);
  `http://write.naindev.com/` now answers 301 to HTTPS.
- [ ] `[H]` T-005 After deploy, press "Validate fix" on the Search Console reason
  "Duplicate: no canonical selected by the user".

## Handoff

Done and verified: spec, plan, failing then passing test, Cloudflare redirect. Next: merge and deploy.
Blocked: T-005 needs deployment first.
