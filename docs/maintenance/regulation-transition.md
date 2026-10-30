# Regulation Transition Runbook

Use this runbook when the official Pokemon Champions regulation set changes, or when `python3 tools/check_format_freshness.py` warns that the current window ends within 30 days.

The freshness check fails closed after the current window ends. Every pull request then fails `plugin-package-check`, including Dependabot updates. Finish the transition before the end timestamp.

## 1. Confirm The Successor Live

- Find the official announcement for the next regulation set on `pokemon.com` or the Play! Pokemon news surface.
- Record the exact start and end timestamps in UTC, the publication date, and the canonical URL.
- Record only what the page states: added Pokemon, Mega Evolutions, mechanics, item rules, and timers. List anything it does not state as unverified.
- If no official announcement exists yet, stop. Do not create a successor designation from community sources or from an expected schedule.

## 2. Update The Format Artifacts

Replace `<old>` and `<new>` with regulation ids such as `m-c` and `m-d`.

| Artifact | Change |
|---|---|
| `data/snapshots/champions-reg-<new>-<date>.json` | Add the new snapshot with `temporal_status: current`, the official window, and one official source with an exact `fetched_at`. |
| `data/snapshots/champions-reg-<old>-<date>.json` | Set `temporal_status` to `historical`. Keep the file. |
| `docs/skills/shared/references/champions-reg-<new>-legality.md` | Add the new legality note with `temporal_status: current` front matter. |
| `docs/skills/shared/references/champions-reg-<old>-legality.md` | Delete it, or keep it with `temporal_status: historical` if a fixture still needs it. |
| `docs/skills/shared/references/live-source-registry.yaml` | Replace the `official_regulation` entry: id, URL, `regulation_id`, and `active_window`. |
| `data/fixtures/*-request-v1.example.json`, `data/fixtures/battle-state-v1.example.json` | Move the current `format` or `format_provenance` block to the new regulation. |
| `skills/*/SKILL.md` | Update every link to the old legality note. |
| `.opencode/skills/*/SKILL.md` | Update every link to the old legality note. The freshness check rejects wrappers that route to a historical note. |
| `tests/test_format_freshness.py`, `tests/test_source_registry.py`, `tests/test_ingest_battle_state.py` | Update the checked-in regulation ids, windows, and URLs. |

Find the remaining references with:

```bash
git grep -n "reg-<old>\|regulation-<old>" -- ':!plugins' ':!data/snapshots'
```

## 3. Regenerate Derived Files

```bash
python3 tools/render_source_registry_docs.py build
python3 tools/build_plugins.py build
python3 tools/generate_site_trust_data.py build
python3 tools/validate.py
```

Do not hand-edit `plugins/`, `docs/skills/shared/references/live-source-map.md`, or `site/src/generated/trustData.ts`.

## 4. Ship The Transition

- Open a dedicated pull request. Do not push format changes onto a Dependabot branch.
- After merge, bump `VERSION`, run `python3 tools/build_plugins.py build` and `python3 tools/build_plugins.py update-release-notes`, merge that, and run the `Plugin Release` workflow from `main`. Installed plugins update only when the version changes.

## 5. Between Transitions

The official source entry allows 30 days between fetches. When the public trust panel shows the source as stale, recheck the official page, update `fetched_at` and `verified_on` in the current snapshot, and regenerate the trust data.
