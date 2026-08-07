# Build Principles

## Start With The Real Build Goal

Clarify which of these is primary:

- make a target mon viable
- maximize raw ladder/tournament strength
- target specific meta teams
- support a preferred playstyle

Do not optimize for all of them equally if they conflict.

## Core Team Questions

Before finalizing the draft, answer:

- What is the primary win path?
- What gives the team speed control or tempo control?
- How does the team position around Fake Out, weather, Trick Room, or setup?
- What does the endgame usually look like?
- Which current meta shells is this team trying to punish?

## Recommendation Discipline

- Build one primary team, not a menu of branches.
- If you mention optional swaps, keep them for the final refinement section only.
- Use `current-field recommendation` only when the shared recommended minimum live stack in [Shared Live Source Map](../../shared/references/live-source-map.md) succeeds.
- If that stack is incomplete, call the build an `inference-heavy early read`.
- Summarize the shared [Verification Packet](../../shared/references/verification-packet.md) before recommending slots when current format, legality, meta, matchup, item, move, or mechanics claims materially affect the build.

## Evidence and Confidence

The `Evidence and Confidence` section should be short but auditable. Include:

- checked date
- source stack status
- source names or URLs and fetched dates
- format confidence
- meta confidence
- material legality or source gaps

Do not call the overall verification packet `complete` when the minimum meta-source stack succeeds but material species, item, move, or mechanics legality remains unverified. In that case, say the minimum meta stack is complete but the overall packet is `partial`, then keep exact set and item language provisional.

Do not use this section as a citation dump. Its job is to show why the recommendation is current-field, early-read, or provisional before the team list appears.

## Supporting Species Legality

Before listing the team, state whether the five non-requested/supporting species were:

- officially verified for the active regulation
- partially verified
- or still unverified

This note should appear before the team list so the user sees the confidence boundary before the recommendation.

## Battle-Ready Mode

`battle-ready` mode is opt-in only. Use it when the user explicitly asks for:

- `battle-ready`
- `ladder-ready`
- `tournament-ready`
- `with spreads`
- `with EVs`
- `export-ready`

Do not force battle-ready output onto normal shell-building requests.

In battle-ready mode:

- keep one primary six
- add `Targeted Meta Cores and Teams`
- build a capped benchmark plan
- hand narrow spread questions to `vgc-calcs-assistant`
- return `Battle-Ready Spreads`
- return `Playbook`
- end with explicit `Export Status`

## Requested Mon Handling

- If the requested mon is good in the requested role, commit to it.
- If the requested mon is weak but salvageable, say so and build the best honest shell.
- If the requested ask is not realistically viable, explain that directly and pivot to the nearest viable version that preserves the user goal as much as possible.

## Set Direction Standard

Each final build should provide lightweight set direction for every slot:

- likely role framing
- likely item direction
- move or utility emphasis
- mechanics-aware positioning direction when relevant

If the current regulation does not have `Terastallization` active, do not include Tera recommendations.

If an item is not currently verified as legal, do not treat it as confirmed legal.

If an exact item appears in `Recommended Team` or `Set Direction`, the item must either be verified in the legality ledger or carry an inline `unverified/provisional` label.

If move legality is not currently verified in-repo, do not give an exact locked four-move set as if it were confirmed. Use provisional move direction instead. If the user asks for an import-ready export, say the exact export is blocked by unverified move legality and provide move pools or role directions instead.

Do not turn this into a full export unless the user asks for one.

In battle-ready mode, `Battle-Ready Spreads` should add:

- likely ability
- nature
- EV spread
- exact item only when legality is verified, else inline `unverified/provisional`
- exact four moves only when move legality is verified
- otherwise a primary move package and explicit export block note
- one short benchmark note explaining why that spread exists

If named items or moves are not verified, the build may still be battle-ready, but it is not export-ready.

## Targeted Meta Cores And Teams

In battle-ready mode, use live current-field shells as first-class inputs:

- `2-mon`, `3-mon`, and `4-mon` common cores
- recent top teams from current tournaments
- individual high-usage threats when shell coverage is still incomplete

The visible `Targeted Meta Cores and Teams` section should:

- usually contain 3 to 5 entries total
- list only the shells that materially shaped slot choice, benchmark selection, or matchup notes
- stay short and actionable instead of turning into a mini meta report

Use those live shells in three places:

- slot selection
- benchmark selection
- matchup framing

Priority order:

1. user-named anti-meta targets
2. cores or top teams that directly pressure the requested strategy
3. most common current-field cores or top teams
4. individual threats not already covered by those shells

Heavy scouting remains out of scope here. Use `vgc-meta-research` or `vgc-opponent-scout` when the user needs a broader field report.

## Benchmark Plan

In battle-ready mode, build a fixed, capped hybrid benchmark set:

- up to 2 speed benchmarks
- up to 2 survival benchmarks
- up to 2 KO or damage benchmarks

Rules:

- require at least one benchmark tied to the team's main win path
- do not require a benchmark for every slot
- utility or support slots may keep heuristic spreads when no benchmark changes a real decision
- hand off only narrow benchmark questions to `vgc-calcs-assistant`
- do not ask `vgc-calcs-assistant` to optimize the whole team

## Playbook

In battle-ready mode, add a practical piloting layer after `Battle-Ready Spreads`.

The `Playbook` section should:

- usually contain 3 packages
- allow a 4th package only when it is materially distinct
- allow only 2 packages when the builder explicitly says the team does not honestly support a third
- use at least 2 distinct lead pairs across the returned packages
- derive each package from the chosen six plus the `Targeted Meta Cores and Teams` set
- stay focused on common bring patterns, not full matchup scripting

Each package should include:

- `Use Into`
- `Lead Pair`
- `Preferred Backline`
- `Opening Goal`
- `Turn-One Pattern`
- `Why This Package Works`
- `Watch-Outs`

Guidelines:

- `Use Into` should name concrete opposing shapes such as a named core, common weather shell, or bulky setup shell
- `Preferred Backline` should usually be 2 mons; only use a flex slot when the team genuinely has one
- `Turn-One Pattern` should describe turn-one or turn-one-plus-turn-two intent only
- `Why This Package Works` should tie back to the team's identity, not generic VGC advice
- `Watch-Outs` should name the main way the line gets punished

End the section with short `Playbook Notes` only when a cross-package default or warning helps the user choose between lines.

## Anti-Meta Framing

Anti-meta does not mean "unusual."

A strong anti-meta team should:

- punish common autopilot leads
- exploit over-centralized speed control or weather usage
- keep a clear game plan into popular balance shells

## Avoid These Failure Modes

- six individually strong mons with no shared plan
- support overload with no closer
- pure offense with no way to stabilize board position
- solving every matchup on paper and ending up with no identity
