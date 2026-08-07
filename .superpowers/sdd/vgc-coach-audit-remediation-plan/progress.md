# SDD ledger — plan: /private/tmp/vgc-coach-audit-remediation-plan.md

Workspace: /private/tmp/vgc-coach-audit-remediation
Base: origin/main at 9483f9d
Status: setup complete; Task 1 pending
Baseline: plugin drift check passes; 40 Python tests pass and 8 source-registry tests reproduce the approved missing-PyYAML failure.

Task 1: complete
- Reviewed through two fix rounds; final spec and quality approved.
- PR 41 merged: https://github.com/NoahJenkins/vgc-coach/pull/41
- Merge commit: 3289fc6bc9a0df4f8fdc5c317a8cbb2b09e4f809
- All GitHub checks passed; integration branch auto-deleted remotely.

Task 2: minor (deferred): collapse the two overlapping two-package checks in team-builder case-10 during Task 4 fixture cleanup.
Task 2: complete
- Spec passed; quality passed with the recorded non-blocking fixture cleanup.
- PR 42 merged: https://github.com/NoahJenkins/vgc-coach/pull/42
- Merge commit: f779e438fed13ec75462b64ae65329ec21703a6c
- All GitHub checks passed; integration branch auto-deleted remotely.

Task 3A: complete
- Commits: d15bd13, 14a134c
- One fix round closed external-file `git diff` and end-to-end web-fetch gaps.
- Final spec and quality approved; 94 focused tests pass.
- Live SDK web research intentionally fails closed and reports inconclusive until Task 3C proves a mediated connector.

Task 3B: complete
- Commits: 56e4634, ca3e208
- One fix round closed stdin deadline, descendant cleanup, destination-subtree, and Unicode-control gaps.
- Final spec and quality approved; 29 focused tests, plugin build/check, and generated parity pass.
- Exact browser execution fails closed on unsupported non-POSIX hosts.

Task 3C: complete
- Commits: 86b0c17, 6f5c608
- One fix round replaced a signature-only SDK test with a real `CopilotClient.create_session` smoke against a controlled no-I/O JSON-RPC boundary.
- Final spec and security/code quality approved; 125 Python tests, registry/plugin checks, dependency integrity, workflow assertions, and production site build pass.
- The scheduled trigger remains disabled; guarded mutation is restricted to protected `main` and provider secrets exist only on the harness step.

Task 3: complete
- Authorization, filesystem/process bounds, dependency installation, repository-native validation, and workflow privilege boundaries are all reviewed and approved.

Task 4: complete
- Commits: eb2bc8a, 1e51b22
- One fix round closed three ambiguous M-A examples and made format freshness fail closed for unlabeled regulation-bearing registry entries, references, nested snapshots, and nested example fixtures.
- Final spec and security/code quality approved; 134 tests, registry rendering, freshness validation, generated-plugin parity, direct locked site build, and diff checks pass.
- Current truth is Regulation M-B from 2026-06-17 02:00 UTC through the official August 5 extension ending 2026-09-09 01:59 UTC.

Task 5A: complete
- Commits: e656dcb, 83c84db, 4b3b832, bc421d5, 27bee4b
- Four review rounds closed URL/RFC3339 schema parity, hostile JSON error handling, atomic output, cross-field state integrity, Python/ECMAScript regex semantics, and exact high-precision time ordering.
- Final spec and security/code quality approved with no findings after 36 focused tests, 170 core tests, exhaustive RFC3339/order matrices, all-four-CLI adversarial/atomic checks, package parity, plugin drift, compilation, and diff checks.
- The shipped boundary is a documented `battle-state-v1` JSON interchange plus local bounded normalizer; proprietary raw replay formats remain explicitly unsupported.

Task 5B: complete
- Commits: 4a04421, c490bec, cf8d844, 59e4553
- Final review closed clean-site-CI dependency setup, canonical trust-data validation, exact verification timestamps, and CSP `base-uri 'none'`.
- Final acceptance approved the player examples, generated trust dashboard, self-hosted fonts, responsive light/dark behavior, and production security-header configuration.

Task 6 local release preparation: complete, pending hosted publication
- Commit: 64118983e8712e05224294b6f86d4e6fde1cdce2
- Prepared `v0.2.0` release inputs and regenerated runtime packages, marketplaces, root/site package metadata, release notes, and site trust data.
- Added a generator contract that aligns `site/package.json` with `VERSION` and a freshness check that rejects OpenCode wrappers routed to historical regulation references.
- Corrected all ten OpenCode wrapper legality links from historical M-A to current M-B; remaining M-A artifacts are explicitly historical fixtures/references or negative tests.
- Fresh Python 3.12 environment installed pinned dependencies; 184 tests and the complete one-command validator passed with repository-pinned pnpm 10.33.0. JS measured 224,526 bytes raw / 69,082 bytes gzip-9 (Vite: 70.04 kB gzip).
- Scheduled autoresearch remains disabled. Hosted PR/settings/release/deployment/cleanup work has not been performed by this local-only task.

Whole-branch review fixes: complete
- Commit: 075c883
- Format freshness now recognizes both `format.regulation_id` and `format_provenance.regulation_id`; canonical `battle-state-v1` examples default to the current-facing designation and fail after their exact embedded end boundary.
- The public trust payload derives `fresh` or `stale` from the official registry source's `max_age_days` and exact fetched timestamp. The site re-evaluates that boundary at page load while retaining the live-recheck caveat.
- Regression evidence: 20 focused tests and 189 full Python tests pass; core validation, generated source/plugin/trust parity, the pinned pnpm 10.33.0 production build, bundle budget, and `git diff --check` pass.
- JavaScript is 224.98 kB raw / 70.18 kB Vite gzip (69,230 bytes gzip-9), below the 73.82 kB ceiling; CSS is 35.45 kB raw / 7.83 kB Vite gzip (7,789 bytes gzip-9).
- The global pnpm 11 auto-version wrapper stalled under restricted network access; the already-cached repository-pinned pnpm 10.33.0 executable ran the exact `pnpm run build` script successfully.
