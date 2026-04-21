# Codex Runtime

Codex is the primary runtime for this repo.

## Loading Model

- Prefer repo-root `AGENTS.md` as the shared operating contract.
- Keep canonical skill logic in `skills/` so Codex can share the same core content as future runtimes.
- Expose repo-local Codex skills through `.agents/skills/` as a thin discovery layer that points back to `skills/`.
- Package distributable Codex installs through `plugins/vgc-coach-codex/` and `.agents/plugins/marketplace.json`.
- Use web verification for current meta, rules, and recommendations.

## Expected Behavior

- Verify current format assumptions before giving meta or legality guidance.
- Distinguish sourced facts from inference.
- Use repo fixtures and rubrics when validating skill changes.

## Runtime-Specific Notes

- Codex can combine local repo artifacts with live web verification cleanly.
- `.agents/skills/` should not become a second editable skill tree; keep it as wrappers or symlinks only.
- Keep Codex-specific behavior in this file, not inside shared skill logic.
- `vgc-calcs-assistant` v1 exact support depends on local `agent-browser` plus `python3 tools/browser_damage_calc.py`.
- The current exact backend is Pikalytics for damage, KO, and survival only; speed checks still stay in assumption-framed guidance.

## Install

Build the generated package, then install it into your local Codex marketplace:

```bash
python3 tools/build_plugins.py build
python3 tools/install_codex_plugin.py
```

That command copies the generated package into `~/plugins/vgc-coach-codex` and writes `~/.agents/plugins/marketplace.json`.

## Update

Refresh your checkout, rebuild, then reinstall the local package:

```bash
git pull
python3 tools/build_plugins.py build
python3 tools/install_codex_plugin.py
```

Restart Codex after updating so the refreshed package is reloaded cleanly.

## Verify

Confirm the generated package and local marketplace entry both exist:

```bash
ls ~/.agents/plugins/marketplace.json ~/plugins/vgc-coach-codex/.codex-plugin/plugin.json
```

If those paths exist, Codex has the packaged plugin and the marketplace entry needed to surface it.
