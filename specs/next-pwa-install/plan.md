# Implementation Plan - Installable Web Client

## Files

| File | Change |
| --- | --- |
| `tests/test_pwa_install.py` | New contract test for PWA-001 to PWA-004, written before the files. It reads PNG headers with `struct`, so no image library is needed. |
| `src/spanish_rewriter/web/manifest.webmanifest` | New manifest. |
| `src/spanish_rewriter/web/icons/` | New: `icon-192.png`, `icon-512.png`, `icon-maskable-512.png`, `apple-touch-icon.png`. |
| `src/spanish_rewriter/web/index.html` | Link the manifest and the touch icon, add the four mobile web app meta tags. |
| `docs/01-requirements.md`, `docs/05-tasks.md`, `docs/07-traceability.md` | One row each. |

## Decisions

- Paths are relative (`./`), like the rest of the page, so the manifest works whatever the host path is.
- `background_color` and `theme_color` are `#edf1f6`, the `--paper` colour the page paints first and its
  `theme-color` meta.
- Status bar style is `default` because the page is light.
- The loopback server is not changed: see the notes in `spec.md`.
- No service worker (owner decision of 2026-11-13). Adding one later needs its own ADR.

## Icons

The mark is a blue tile with three white strokes, so the maskable and Apple icons use the tile colour as
background and the favicon at 85% of the width: its tile blends into the background and the three strokes
stay inside the safe zone (radius 40%).

```
node make-install-icons.mjs --source src/spanish_rewriter/web/favicon.svg --out src/spanish_rewriter/web/icons --bg "#0047AB" --maskable-scale 0.85 --apple-scale 1
```

(`make-install-icons.mjs` is a local helper that uses `sharp`; it is not part of the repository.)

## Test strategy

- `tests/test_pwa_install.py` runs under the command CI uses (`python -m unittest discover -s tests -v`).
- Manual: Chrome `Page.getInstallabilityErrors` on the `web/` folder; after the deploy, an Android phone and an iPhone.
