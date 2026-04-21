---
name: opencode-vgc-team-builder
description: Use when building one practical Pokemon Champions team around a target idea in OpenCode.
compatibility: opencode
---

OpenCode wrapper for the shared `vgc-team-builder` contract.

Read and follow these shared repo files directly:
- `skills/vgc-team-builder/SKILL.md`
- `docs/skills/vgc-team-builder/references/build-principles.md`
- `docs/skills/vgc-team-builder/references/output-rubric.md`
- `docs/skills/shared/references/champions-reg-m-a-legality.md`

Treat the legality note as a hard constraint for current Reg M-A builds:
- `Mega Gengar` is legal
- only one Mega Stone user belongs on the team
- do not give `Terastallization` recommendations
- if a non-`Gengarite` item is not currently verified as legal, do not name a speculative item; mark the item direction as unverified instead
- prefer current Reg M-A staples and currently evidenced species over older-format carryovers when uncertainty is high

When the shared contract says to use another repo skill, load the matching `opencode-vgc-*` wrapper instead of a shared `vgc-*` skill name.

Use repo files directly. Do not read from `.claude/skills/...` or `.agents/skills/...`.
