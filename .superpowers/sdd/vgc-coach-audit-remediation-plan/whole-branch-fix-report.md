# Whole-branch review fix report

## Outcome

Both review findings are closed locally in implementation commit `075c883` (`fix: enforce format and source freshness`). No external state was changed.

## Important finding: battle-state freshness coverage

- `tools/check_format_freshness.py` now detects regulation identifiers and active windows in both supported shapes: `format` and `format_provenance`.
- Canonical `battle-state-v1` example fixtures are explicitly treated by the checker as current-facing when no top-level designation exists. An explicit designation still takes precedence.
- Existing fail-closed behavior remains: a non-battle fixture with regulation-bearing `format_provenance` but no temporal designation raises an error.
- Regression tests prove the checked-in M-B battle-state example is yielded as current through `2026-09-09T01:59:00Z` and an equivalent expired battle-state fixture fails one second after its exact end boundary.
- Plugin generation produced no content changes because the canonical fixture itself did not change; `tools/build_plugins.py check` confirms all packaged copies remain byte-aligned.

## Minor finding: calculated trust freshness

- `tools/generate_site_trust_data.py` derives freshness from the exact source fetch timestamp plus the current official registry source's positive integer `freshness.max_age_days`.
- The boundary is inclusive: the snapshot is `fresh` through the exact threshold and `stale` immediately afterward.
- Generator render/write/check helpers accept an injectable timezone-aware clock. A regression proves a previously fresh generated artifact is rejected by `check` immediately after the freshness boundary.
- Generated trust data exposes `fresh_until`, the source maximum age, and distinct fresh/stale labels and notes.
- `site/src/App.tsx` independently evaluates `fresh_until` against the visitor's current time at page load, so a deployed static page can show a stale state without waiting for regeneration. Both states retain the requirement to recheck live before present-tense coaching.

## Verification

- `.venv/bin/python -m unittest tests.test_format_freshness tests.test_generate_site_trust_data`: 20 passed.
- `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`: 189 passed.
- `.venv/bin/python tools/validate.py --scope core`: passed all tests, registry rendering, current-format freshness, battle-state ingestion, and plugin drift.
- `.venv/bin/python tools/generate_site_trust_data.py check`: passed.
- `.venv/bin/python tools/build_plugins.py check`: passed.
- Cached repository-pinned pnpm `10.33.0` ran the exact site `build` script: TypeScript checks and Vite production build passed.
- Production bundle: JavaScript 224.98 kB raw / 70.18 kB Vite gzip (69,230 bytes gzip-9), below the 73.82 kB ceiling; CSS 35.45 kB raw / 7.83 kB Vite gzip (7,789 bytes gzip-9).
- `git diff --check`: passed before the implementation commit.

The global pnpm 11 binary attempted to auto-switch to the package's pinned version and stalled under restricted network access. The cached pnpm 10.33.0 binary was therefore invoked directly; it executed the repository's unchanged `pnpm run build` script successfully.
