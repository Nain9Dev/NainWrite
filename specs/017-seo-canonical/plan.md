# Implementation Plan - SEO Canonical URL

## Files

| File | Change |
| --- | --- |
| `tests/test_web_client.py` | New test: one canonical link, absolute HTTPS, host equal to `web/CNAME`. |
| `src/spanish_rewriter/web/index.html` | Add `<link rel="canonical" href="https://write.naindev.com/">` in `<head>`. |
| `docs/07-traceability.md` | Map SEO-001 to SEO-003 to the test. |

## Notes

- A `<link>` element is not an inline handler or style, so the loopback CSP is unaffected.
- The HTTP to HTTPS redirect lives in Cloudflare, not in this repository.
