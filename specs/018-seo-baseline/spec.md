# SEO Baseline

Goal: make the public demo at `write.naindev.com` understandable to search engines and
AI engines, building on the canonical URL from spec 017.

Scope: the static web client under `src/spanish_rewriter/web/`, which is also the
GitHub Pages artifact. Visual design and visible copy are unchanged.

## Requirements (EARS)

- **SEO-004 Description:** The web client page shall declare exactly one meta
  description between 70 and 160 characters.
- **SEO-005 Social metadata:** The page shall declare Open Graph tags (`og:type`
  `website`, `og:site_name`, `og:title`, `og:description`, `og:url` equal to the
  canonical URL, an absolute HTTPS `og:image`) and a `summary_large_image` Twitter
  card with the same image.
- **SEO-006 Structured data:** The page shall embed one `SoftwareApplication`
  JSON-LD block that names the author with the `@id`
  `https://www.naindev.com/#person`, and a `rel="author"` link to the main site.
- **SEO-007 Root files:** The Pages artifact shall contain `robots.txt` that allows
  all crawlers and advertises the sitemap, a `sitemap.xml` whose only `<loc>` is
  the canonical URL, and an `llms.txt` that starts with an H1.
- **SEO-008 Local mode unchanged:** The added markup shall keep passing the
  loopback Content Security Policy checks (no inline handlers, styles or scripts
  that execute).

## Notes

- The JSON-LD block has type `application/ld+json`, a data block that the browser
  never executes, so `script-src 'self'` is unaffected.
