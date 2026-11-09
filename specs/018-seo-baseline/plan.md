# Implementation Plan - SEO Baseline

## Files

| File | Change |
| --- | --- |
| `tests/test_web_client.py` | New tests for SEO-004 to SEO-007, written before the markup. |
| `src/spanish_rewriter/web/index.html` | Add author link, Open Graph, Twitter card and JSON-LD to `<head>`. |
| `src/spanish_rewriter/web/robots.txt` | New: allow all, advertise the sitemap. |
| `src/spanish_rewriter/web/sitemap.xml` | New: canonical root only. |
| `src/spanish_rewriter/web/llms.txt` | New: Markdown summary and key links. |
| `docs/07-traceability.md` | Map SEO-004 to SEO-008 to the tests. |

## Notes

- `.github/workflows/deploy.yml` uploads the whole `web/` folder, so the new files are published without workflow changes.
- The loopback server only serves `.js`, `.css` and `.svg`; the new root files exist for the hosted demo.
- `og:image` reuses the shared NainDev cover because the repository ships no raster social image.
