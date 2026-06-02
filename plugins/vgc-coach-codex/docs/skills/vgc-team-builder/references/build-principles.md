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
