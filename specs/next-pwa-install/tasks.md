# Task Handoff - Installable Web Client

## Tasks

- [x] `[A]` T-001 Failing tests in `tests/test_pwa_install.py` for PWA-001 to PWA-004.
  - Done when: the test fails because `manifest.webmanifest` does not exist. Result: 5 errors before the change.
- [x] `[A]` T-002 Generate the four icons from `favicon.svg` (command in `plan.md`).
  - Done when: each declared file exists at its declared size.
- [x] `[A]` T-003 Add `manifest.webmanifest` and the head tags in `index.html`.
  - Done when: `tests/test_pwa_install.py` passes and the other web client tests still pass.
- [x] `[A]` T-004 Ask Chrome for installability errors on the `web/` folder.
  - Done when: `installabilityErrors` is empty. Result: empty list.
- [x] `[A]` T-005 Add the rows to `docs/01-requirements.md`, `docs/05-tasks.md` and `docs/07-traceability.md`.
- [ ] `[M]` T-006 After the deploy, check that `https://write.naindev.com/manifest.webmanifest` answers 200 and
  install the site on Android (Chrome) and on iOS (Safari).
  - Needs from owner: merge, then confirm icon, label `NainWrite` and the window with no browser bar.

## Handoff

Done and verified: spec, plan, failing then passing tests (5 tests in `tests/test_pwa_install.py`), Chrome check.
Next: merge and deploy. Blocked: T-006 needs the deployment and the owner's phones.
