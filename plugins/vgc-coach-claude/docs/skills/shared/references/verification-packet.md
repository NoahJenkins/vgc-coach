# Verification Packet

Use a verification packet whenever a coaching answer depends on current Pokemon Champions format, legality, meta, matchup, or set claims.

The packet does not need to be printed as a full table unless the user asks for it. Skill outputs should summarize the packet clearly enough that a reviewer can audit why the answer is labeled as current-field, early-read, or provisional.

## Required Fields

- `checked_at`: absolute date, and time when available
- `active_regulation`: regulation name and battle mode
- `active_mechanics`: mechanics directly confirmed by official material
- `source_stack_status`: `complete`, `partial`, or `failed`
- `sources`: source id, source URL, fetched date/time, claim type, and freshness note
- `format_confidence`: `officially verified`, `partially verified`, or `unverified`
- `meta_confidence`: `community-supported`, `partially verified`, `inference`, or `unverified`
- `legality_ledger`: species, item, move, and mechanics claims that materially affect the answer
- `gaps`: missing sources, conflicts, or unsupported assumptions that constrain the answer

## Confidence Labels

- `officially verified`: directly supported by current official Pokemon Champions or Play! Pokemon material
- `community-supported`: supported by dated community usage, tournament, set, or editorial sources after format truth is locked
- `partially verified`: some required support exists, but a source role, exact legality point, or freshness field is missing
- `unverified`: not checked or not supported by the material available in the run
- `inference`: competitive interpretation built from verified or community-supported facts, not directly stated by a source

## Source Stack Rules

Use [Shared Live Source Map](./live-source-map.md) as the source-role contract.

For a `current-field recommendation`, the packet must include:

- at least one official regulation source
- at least one tournament-focused community source
- at least one broader usage or community source
- fetched dates for every source used in the minimum stack
- no material conflict that changes the recommendation

If the minimum stack is incomplete, conflicted, or too stale for the claim, label current-field coaching as `inference-heavy early read`.

## Legality Ledger

The legality ledger should cover only claims that materially affect the answer. It must include:

- requested species or forms when the build, audit, or plan depends on them
- all supporting species in a recommended team
- exact held items when they are recommended as legal
- exact moves when a locked move set or turn plan depends on move access
- active mechanics when mechanics change positioning, such as Mega Evolution or Terastallization

Use `officially verified` only for legality claims backed by official current-format material. If a move or item is plausible but not verified in-repo or live, label it `unverified` or use provisional set direction instead of presenting it as confirmed.

## Skill Usage

- `vgc-meta-research`: produce packet-compatible source summaries in `Sources`.
- `vgc-team-builder`: summarize the packet in `Evidence and Confidence` before recommending the team.
- `vgc-team-audit`: consume the packet when findings depend on current field assumptions or exact legality.
- `vgc-lead-planner`: consume the packet when lead plans depend on current matchup assumptions, item legality, move access, speed, or survival claims.

Snapshots under `data/snapshots/` can support examples and fallback context, but live verification remains required for present-tense current-format claims.
