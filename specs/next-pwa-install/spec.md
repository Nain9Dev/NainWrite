# Installable Web Client

Goal: a visitor on a phone can install `write.naindev.com` from the browser and open it like an app, with its
own icon and name on the home screen and a window with no browser bar. Targets: Android Chrome and iOS Safari.

Scope: the static web client under `src/spanish_rewriter/web/`, which is also the GitHub Pages artifact.
Visual design and visible copy are unchanged. This is the NainWrite part of the ecosystem-wide change specified in
`specs/next-pwa-install/spec.md` of the `nain9dev.github.io` repository, which holds the verified browser
criteria (Chrome install criteria, iOS standalone behaviour, maskable safe zone). They are not repeated here.

## Requirements (EARS)

- **PWA-001 Manifest:** The Pages artifact shall publish `manifest.webmanifest`, valid JSON, with `name` and
  `short_name` equal to `NainWrite`, `display` `standalone`, `lang` `es`, `dir` `ltr`, `id`, `start_url` and
  `scope` as `./` (the page uses relative asset paths), `theme_color` and `background_color` as literal
  `#rrggbb` values, and no `prefer_related_applications`.
- **PWA-002 Description and theme:** The manifest `description` shall equal the page meta description, and its
  `theme_color` shall equal the page `theme-color` meta.
- **PWA-003 Icons:** The manifest shall declare PNG icons in `icons/`: 192 px and 512 px with purpose `any`, and
  512 px with purpose `maskable`, one purpose per entry. Every declared file shall exist at its declared size.
  `icons/apple-touch-icon.png` shall exist at 180 px. All are derived from `favicon.svg`.
- **PWA-004 Head tags:** `index.html` shall link the manifest and `icons/apple-touch-icon.png`, and shall carry
  `mobile-web-app-capable` and `apple-mobile-web-app-capable` set to `yes`, `apple-mobile-web-app-title` equal to
  the manifest `short_name`, and `apple-mobile-web-app-status-bar-style` set to `default` (the page is light).

## Notes

- Installable only: no service worker, no cache, no offline page and no install button (owner decision of
  2026-11-13). An installed window without network shows the browser's own offline screen.
- `.github/workflows/deploy.yml` uploads the whole `web/` folder, so the manifest and icons are published without
  a workflow change. The Pages host serves `.webmanifest` and `.png` files as files; there is no SPA fallback.
- The page has no Content-Security-Policy meta tag; the hosted site is not restricted. In local mode the loopback
  server sends `default-src 'self'`, which already allows a same-origin manifest and icons.
- The loopback server serves only root-level `.js`, `.css` and `.svg` files (UI-010), so locally the manifest and
  icons answer the JSON 404. Nothing breaks and the local application is not meant to be installed, so the
  server is unchanged.

## Session state

- Done: tests, manifest, icons, head tags, docs.
- Verified: `python -m unittest discover -s tests` shows only the 11 failures that exist on an untouched `main`
  (optional PDF packages); Chrome reports no installability error on the `web/` folder.
- Next: after the merge and deploy, check that the live manifest answers 200, then install on an Android phone and
  an iPhone.
- Blocked: the live install check needs the owner's phones.
