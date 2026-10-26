# Task Handoff - Client Visual Redesign

## Tasks

- [x] `[A]` T-001 Failing test `tests/test_web_client.py`: DOM id contract, no inline
  handlers or styles, `.js`/`.css`/`.svg` static serving, traversal refusal.
  Failed on the inline `onclick` of the old page, then passed.
- [x] `[A]` T-002 Generic same-origin static rule in `workbench_http.py`.
- [x] `[A]` T-003 `diff.js`: tokeniser, weighted word LCS, change count, literal extraction
  (`tests/web/diff.test.mjs`, 12 tests).
- [x] `[A]` T-004 `showcase.js` and hero markup, with a pause button and a static final frame under
  reduced motion (`tests/web/showcase.test.mjs`, 6 tests).
- [x] `[A]` T-005 Workbench markup, stepper, tabs, export grid, toast, drag and drop. The three
  seeded documents were driven through their stages in the browser. Showing only the panel of the
  current stage was added so the page does not grow into one long scroll.
- [x] `[A]` T-006 `app.css` on NainDev tokens, responsive at 375 px, reduced motion.
- [x] `[A]` T-007 Docs: requirement index, traceability.
- [ ] `[M]` T-008 Aitor reviews the live page after deployment and decides whether
  the landing copy is the one to show to clients.

## Completed and verified

- `python -m unittest tests.test_web_client`: 5 tests pass.
- `node --test "tests/web/*.test.mjs"`: 18 tests pass.
- Browser at 1280 px (landing, comparison with four word-level changes and six literals marked
  present, stepper per stage) and 375 px (no horizontal overflow). The real loopback server served
  the page under its Content Security Policy, with the landing hidden.
- Full Python suite: the only failures are the 11 that also occur on an untouched checkout.

## Not verified

- axe and Lighthouse (not installed for this project), the production host (write.naindev.com),
  an uploaded `.txt` driven to `ready`, and the PDF flows (the optional packages are missing here).

## Deviations from the plan

- `mock-workbench.js` is unchanged: the comparison is computed in the browser from the two texts, so
  the demo engine needed neither a computed diff nor an `automatic_status`.

## Limits

- The literal check is a browser-side visual aid over two strings. It does not
  evaluate meaning and does not replace the server review or human approval.
- The showcase replays bundled sentences; it is not a live model run.

## Next

Owner review and merge; deploy; T-008.
