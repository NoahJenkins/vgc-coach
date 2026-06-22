---
name: vgc-team-builder
description: Use when building one practical Pokemon Champions team around a target idea.
---

# VGC Team Builder

Build one practical recommended team around a real user goal. Commit to one primary draft and stay honest when the ask is weak.

## Inputs
- target mons
- target strategy or archetype
- playstyle preference
- anti-meta goals
- avoid list
- optional event or ladder context
- optional output intent such as `battle-ready`, `ladder-ready`, `tournament-ready`, `with spreads`, `with EVs`, or `export-ready`

If format is omitted, assume the current Pokemon Champions regulation, verify it when current-context claims matter, and say so.

## Modes

### Default Mode

Use this when the user wants a normal build or team shell.

Return these sections in order:

1. `Build Goal` - objective, format basis, and `current-field recommendation` or `inference-heavy early read`
2. `Evidence and Confidence` - concise verification-packet summary with checked date, source stack status, source URLs or source names, fetched dates, format confidence, meta confidence, and material gaps
3. `Supporting Species Legality` - whether the five non-requested/supporting species were officially verified, partially verified, or remain unverified for the active regulation
4. `Recommended Team` - one six-mon draft only
5. `Role Map` - win path, speed or tempo control, board control, closer logic
6. `Set Direction` - lightweight role, item, move, and mechanics-aware direction for each slot
7. `Why Each Slot Exists` - job, team fit, and what each slot solves
8. `Matchup Notes` - pressure points this shell is built to handle
9. `Weaknesses and Next Refinements` - unresolved issues and optional future tuning only

### Battle-Ready Mode

Use this only when the user explicitly asks for a `battle-ready`, `ladder-ready`, `tournament-ready`, `with spreads`, `with EVs`, or `export-ready` build.

Return these sections in order:

1. `Build Goal`
2. `Evidence and Confidence`
3. `Supporting Species Legality`
4. `Targeted Meta Cores and Teams`
5. `Recommended Team`
6. `Role Map`
7. `Set Direction`
8. `Benchmark Plan`
9. `Battle-Ready Spreads`
10. `Playbook`
11. `Why Each Slot Exists`
12. `Matchup Notes`
13. `Weaknesses and Next Refinements`
14. `Export Status`

## Workflow
1. Lock the active format and major meta pressures first.
2. Align with `vgc-format-verifier` if legality or rules gate the build.
3. Identify the real build goal behind the request before choosing slots.
4. Build around one clear team identity.
5. Keep the requested idea only when it still supports that identity.
6. If the ask is weak, say so plainly and pivot to the nearest viable version that preserves the goal.
7. In `battle-ready` mode, ingest live common cores and recent top teams after the format and meta stack is grounded.
8. In `battle-ready` mode, choose a capped hybrid benchmark set before invoking `vgc-calcs-assistant`.
9. In `battle-ready` mode, derive a matchup-shaped playbook from the chosen six and the targeted core set instead of inventing independent lines.
10. Give lightweight set direction in default mode and battle-ready spreads only in `battle-ready` mode.
11. If a current-field positioning claim is thin, apply `vgc-source-verifier` discipline instead of overselling it.
12. End with real weaknesses instead of pretending the build is solved.

## Required behavior
- Read [build-principles](../../docs/skills/vgc-team-builder/references/build-principles.md) and [output-rubric](../../docs/skills/vgc-team-builder/references/output-rubric.md) before finalizing.
- Read [Champions Reg M-A legality](../../docs/skills/shared/references/champions-reg-m-a-legality.md), [Shared Live Source Map](../../docs/skills/shared/references/live-source-map.md), and [Verification Packet](../../docs/skills/shared/references/verification-packet.md) before finalizing current-format Champions builds.
- In `battle-ready` mode, also read [team-builder calcs handoff](../../docs/skills/shared/references/team-builder-calcs-handoff.md) and [battle-ready legality ledger](../../docs/skills/shared/references/battle-ready-legality-ledger.md) before finalizing.
- Use live verification by default when current meta context materially affects the build.
- Complete or summarize a verification packet before recommending slots when the build depends on current format, legality, meta, matchup, item, move, or mechanics claims.
- Use `current-field recommendation` only if the shared recommended minimum live stack succeeds.
- If that stack is incomplete, label the build `inference-heavy early read`.
- Include `Evidence and Confidence` immediately after `Build Goal`; it must include source stack status, fetched dates when live sources were used, format confidence, meta confidence, and any material gaps.
- Do not call the overall packet `complete` if material species, item, move, or mechanics legality remains unverified; say the minimum meta stack is complete but the overall verification packet is `partial`.
- Do not let a complete meta-source stack override unverified exact legality. If exact legality gaps materially affect the build, keep item and move direction provisional and consider the recommendation `inference-heavy early read`.
- Include `Supporting Species Legality` before the team list and explicitly say whether the five supporting species were officially verified, partially verified, or remain unverified for the active regulation.
- Keep optional swaps only in `Weaknesses and Next Refinements`.
- Explain how all six slots support the same plan.
- If the active regulation does not have `Terastallization` active, do not give Tera recommendations.
- If a species, item, or move is not currently verified for the active regulation, do not present it as confirmed legal.
- If a specific held item is not currently verified as legal in the verification packet legality ledger, either use a verified legal item or label the item direction as unverified/provisional.
- In `Recommended Team` and `Set Direction`, every exact held item name must either be verified in the legality ledger or carry an inline `unverified/provisional` label.
- If move legality is not verified in-repo, do not give an exact four-move locked set as if it were confirmed; use softer phrasing such as likely move emphasis, candidate utility slots, or provisional move direction.
- Do not satisfy requests for import-ready locked four-move sets when move legality is unverified; say the exact export is blocked by unverified move legality and provide move pools or role directions instead.
- In `battle-ready` mode, use live `2-mon`, `3-mon`, and `4-mon` cores plus recent top teams as first-class build inputs after the format stack is locked.
- In `battle-ready` mode, `Targeted Meta Cores and Teams` should usually contain 3 to 5 entries total and only list the shells that materially shaped slot choice, benchmarks, or matchup notes.
- In `battle-ready` mode, use cores and top teams in three places: slot selection, benchmark selection, and matchup framing.
- In `battle-ready` mode, benchmark target priority is:
  1. user-named anti-meta targets
  2. cores or top teams that directly pressure the requested strategy
  3. most common current-field cores or top teams
  4. individual threats not already covered by those shells
- In `battle-ready` mode, cap the benchmark set at 6 team-wide:
  - up to 2 speed benchmarks
  - up to 2 survival benchmarks
  - up to 2 KO or damage benchmarks
- In `battle-ready` mode, utility mons may keep heuristic spreads when no benchmark materially changes the build.
- In `battle-ready` mode, hand off only narrow benchmark questions to `vgc-calcs-assistant`; do not ask it to optimize the whole team.
- In `battle-ready` mode, `Battle-Ready Spreads` must include role, ability, nature, EV spread, item confidence, move confidence, and one short benchmark note per slot.
- In `battle-ready` mode, `Playbook` must include:
  - 3 packages by default
  - 4 packages only when the team honestly supports a fourth materially distinct plan
  - only 2 packages when the builder explicitly says the team does not honestly support a third package
  - at least 2 distinct lead pairs across the returned packages
  - for each package: `Use Into`, `Lead Pair`, `Preferred Backline`, `Opening Goal`, `Turn-One Pattern`, `Why This Package Works`, and `Watch-Outs`
  - a short `Playbook Notes` footer for cross-package heuristics when needed
- In `battle-ready` mode, each `Use Into` label must name a concrete opposing team shape derived from `Targeted Meta Cores and Teams`, not a vague label such as `aggressive teams`.
- In `battle-ready` mode, `Preferred Backline` should usually name exactly 2 mons; allow one locked closer plus one flex slot only when that is the honest team structure.
- In `battle-ready` mode, `Turn-One Pattern` must stay limited to turn-one or turn-one-plus-turn-two intent; do not fake full deterministic scripts.
- In `battle-ready` mode, the playbook must be downstream of the actual team identity, role map, and benchmark logic; do not use it as a separate creativity pass.
- In `battle-ready` mode, `Matchup Notes` should stay macro-level and avoid repeating the concrete bring packages already covered by `Playbook`.
- In `battle-ready` mode, exact four-move sets are allowed only when move legality is verified for the named moves.
- In `battle-ready` mode, `Export Status` must be one of:
  - `export-ready`
  - `battle-ready but not export-ready`
  - `provisional build blocked by legality or calc gaps`
- In `battle-ready` mode, if named items or moves are not verified, the build may still provide spreads and move packages, but `Export Status` must downgrade away from `export-ready`.
- Do not give multiple half-committed drafts, hide a bad requested mon, or turn the refinement section into a second team.
