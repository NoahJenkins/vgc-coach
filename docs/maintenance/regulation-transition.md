# Regulation Transition Runbook

Use this runbook when the official Pokemon Champions regulation set changes, or when `python3 tools/check_format_freshness.py` warns that the current window ends within 30 days.

## Automation

`.github/workflows/regulation-watch.yml` runs every third day and on manual dispatch.

- The `watch` job runs `python3 tools/regulation_watch.py check`. It reads the official Pokemon HOME news feed (`https://news.pokemon-home.com/en/json/list.json`), keeps the Pokemon Champions `Regulations` entries, and compares them with `data/official-regulation-feed.json`. It makes no model calls. A new or changed entry opens a `regulation-watch` issue. It also opens an issue 3 days before the official source refresh in section 5 is due.
- The `draft` job runs only for a change that has no draft branch yet. It fetches the official page and its eligible Pokemon list, runs `tools/draft_regulation_update.py` with Copilot (`COPILOT_GITHUB_TOKEN`; model from the `REGULATION_DRAFT_MODEL` variable, default `claude-sonnet-5.5`), records the feed baseline, regenerates derived files, and opens a draft pull request.
- The drafter cannot fetch URLs and can write only the format artifacts in step 2. Review every fact in the draft against the official page, then click **Ready for review** to start the required checks.
- The watcher reads only `news.pokemon-home.com` and `web-view.app.pokemonchampions.jp`. `pokemon.com` serves a bot challenge to scripts, so it is not used.

When you handle a change by hand, also run `python3 tools/regulation_watch.py check --report <path>` and `python3 tools/regulation_watch.py update-baseline --report <path>` so the watcher stops reporting it.

The freshness check fails closed after the current window ends. Every pull request then fails `plugin-package-check`, including Dependabot updates. Finish the transition before the end timestamp.

## 1. Confirm The Successor Live

- Find the official announcement for the next regulation set on the Pokemon HOME news page (`https://news.pokemon-home.com/en/list`, Pokemon Champions tab), `pokemon.com`, or the Play! Pokemon news surface.
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
| `data/official-regulation-feed.json` | Run `python3 tools/regulation_watch.py update-baseline` with a fresh report. |
| `data/fixtures/*-request-v1.example.json`, `data/fixtures/battle-state-v1.example.json` | Move the current `format` or `format_provenance` block to the new regulation. |
| `skills/*/SKILL.md` | Update every link to the old legality note. |
| `.opencode/skills/*/SKILL.md` | Update every link to the old legality note. The freshness check rejects wrappers that route to a historical note. |
| `docs/evals/*-live-checklist.md` | Update the regulation name, window, and snapshot and legality paths. |
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
