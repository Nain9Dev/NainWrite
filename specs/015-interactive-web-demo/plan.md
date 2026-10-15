# Implementation Plan - Interactive Web Demo

## Architecture & Presentation
1. **In-Browser Deterministic Engine (`src/spanish_rewriter/web/mock-workbench.js`)**:
   - Provide an autonomous implementation of the `/api/state`, `/api/document`, `/api/action`, and `/api/file` endpoints.
   - Seed realistic initial documents:
     - Document 1: Commercial proposal in `spanish_review` with side-by-side diff, semantic invariant checks (numbers, dates, negations), and review findings.
     - Document 2: Technical cloud contract in `final_review` ready for trilingual comparison and approvals.
     - Document 3: Technical note in `extraction_review` for step-1 intake verification.
   - Implement local client-side transformation for user-uploaded text or files.
2. **Web Client Adaptation (`src/spanish_rewriter/web/app.js` & `index.html`)**:
   - Detect static demo environment (`window.location.hostname.endsWith('naindev.com')`, `github.io`, or offline fallback).
   - If static demo mode, route requests to `mockWorkbench`.
   - Add demo mode status indicator, sample document loader, and reset button.
   - Convert root asset paths to relative paths for subpath and root domain resilience.
3. **Refined Premium Aesthetics (`src/spanish_rewriter/web/app.css`)**:
   - Elevate typography, spacing, contrast, dark/light theme, and card hierarchy.
   - Enhance diff rendering with clear color markers (green additions, red removals).
   - Keep 100% backward compatibility with all DOM IDs and classes required by tests and runtime.
4. **CI/CD & Deployment (`.github/workflows/deploy.yml` & `CNAME`)**:
   - Add `CNAME` with `write.naindev.com` in `src/spanish_rewriter/web/CNAME`.
   - Add GitHub Actions deployment workflow for GitHub Pages.
   - Update `README.md` and repository homepage metadata to `https://write.naindev.com/`.
