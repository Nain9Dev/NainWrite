# Client Visual Redesign

Goal: make `write.naindev.com` sell the product on sight. A visitor must understand
in seconds what NainWrite delivers, see it working without reading, and reach the
review workbench with the fewest possible words on screen.

Scope: the static web client under `src/spanish_rewriter/web/` and the static
file rule of the loopback HTTP adapter. The editorial API, the in-browser demo
engine contracts and the Python workbench are unchanged.

## Requirements (EARS)

- **UI-001 Landing:** When the client runs in demo mode (static host or no loopback
  server), it shall show above the workbench a hero with one headline, one
  secondary line, two calls to action and an animated showcase that replays the
  pipeline (literal detection, calque replacement, verification) on bundled
  example sentences without any network request.
- **UI-002 Value strip:** When the landing is shown, the client shall summarise the
  offer in four cards of at most twelve words each: meaning preserved, natural
  Spanish from Spain, en-US and en-GB from the approved Spanish, human approval.
- **UI-003 Local mode:** When the client runs against the loopback server, it shall
  hide the landing and the showcase, render only the workbench, and use only
  same-origin resources: no inline event handlers and no inline `style`
  attributes, so the server Content Security Policy is satisfied.
- **UI-004 Stage stepper:** When a document is selected, the client shall render a
  four-step indicator (extraction, Spanish, translation, approval) derived from
  the document status and show the panel of the current stage.
- **UI-005 Visual comparison:** When a document has a Spanish result, the client
  shall render a side-by-side word-level comparison of the extracted original and
  the current Spanish, computed in the browser, with removals and insertions
  highlighted and a count of changed segments. The server unified diff and the
  review text shall remain readable under an evidence tab.
- **UI-006 Literal check:** When the comparison is rendered, the client shall list
  the numeric, currency, percentage and date literals detected in the original
  and mark whether each one appears verbatim in the Spanish version. This is a
  visual aid; it never replaces the server review or human approval.
- **UI-007 Brand system:** The client shall apply the NainDev visual system (paper
  background, blue inks, Urbanist and IBM Plex Mono with system fallbacks, 4 px
  radius, stroke icons with round caps, solid-offset shadows) through tokens
  declared in `app.css`, so the local server renders correctly offline.
- **UI-008 DOM contract:** The client shall keep every element identifier used by
  the editorial actions of specifications 011 and 015 (`mode`, `night-start`,
  `night-end`, `save-settings`, `pause`, `upload-form`, `uploads`, `assets`,
  `documents`, `notice`, `empty`, `document`, `stage`, `title`, `progress`,
  `error`, `refresh`, `resume`, `original`, `extraction-section`, `pages`,
  `extraction`, `extraction-actions`, `save-extraction`, `extraction-note`,
  `complete`, `approve-extraction`, `spanish-section`, `spanish`, `save-spanish`,
  `review-spanish`, `diff`, `review`, `translation-actions`, `spanish-note`,
  `resolved`, `acknowledge`, `translate`, `exports-section`, `exports`).
- **UI-009 Accessibility:** The client shall remain usable at 375 px width, keep a
  visible keyboard focus, honour `prefers-reduced-motion`, and keep text contrast
  at or above WCAG 2.2 AA.
- **UI-010 Static files:** When the loopback server receives a GET for a path that
  resolves inside the web directory with a `.js`, `.css` or `.svg` suffix, it shall
  serve the file with the matching content type. Any other path, including
  traversal outside the directory, shall keep returning the JSON 404.

## Non-goals

- No change to the editorial gates, action payloads or demo engine persistence.
- No new dependency, build step, bundler, analytics or paid service.
- No claim of semantic equivalence: every verdict shown comes from the server or
  the demo engine, and the literal check is labelled as a visual aid.

## Handoff

See `tasks.md` for verified state, limits and the next step.
