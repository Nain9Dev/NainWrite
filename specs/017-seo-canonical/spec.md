# SEO Canonical URL

Goal: remove the Search Console reason "Duplicate: no canonical selected by the user"
for `write.naindev.com`. Google crawled `http://write.naindev.com/` and the HTTPS
page as two equal pages with no declared preference.

Scope: the static web client page under `src/spanish_rewriter/web/`. Redirecting
HTTP to HTTPS is a Cloudflare zone setting (Always Use HTTPS, enabled on
2026-11-09) and is outside this repository.

## Requirements (EARS)

- **SEO-001 Canonical:** The web client page shall declare exactly one
  `<link rel="canonical">` whose absolute HTTPS URL is the production origin
  `https://write.naindev.com/`.
- **SEO-002 Origin match:** The canonical origin shall equal the host in
  `src/spanish_rewriter/web/CNAME`, so a domain change cannot leave a stale value.
- **SEO-003 Local mode unchanged:** When the page is served by the loopback
  server, the added tag shall not introduce inline handlers, inline styles or any
  cross-origin resource.
