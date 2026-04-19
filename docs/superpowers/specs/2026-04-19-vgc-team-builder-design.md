# VGC Team Builder Design

## Goal

Strengthen `vgc-team-builder` from a thin skill package into a recommendation-first builder spec that produces one practical Pokemon Champions team draft around a user goal without faking viability, hiding weaknesses, or branching into multiple half-committed versions.

## Scope

This design covers:

- the skill behavior contract
- weak-request handling
- output structure
- lightweight set-direction expectations
- evaluation implications for the fixed team-builder cases

This design does not cover:

- a repo-local eval runner
- battle-state schema work
- replay-ingestion tooling
- runtime-specific forks of the same core skill

## Core Product Decision

`vgc-team-builder` should produce **one primary recommended draft only**.

The skill is not a brainstorm tool and not a menu of alternate teams. If the user asks for a build, the skill should commit to the best honest version of that ask in the current format.

Optional swaps or future tuning ideas may appear only inside `Weaknesses and Next Refinements`. They should not turn the response into multiple parallel builds.

## User Jobs

The skill should solve these requests well:

- build around a target mon
- build around a target strategy or shell
- build an anti-meta team with a specific punishment goal
- salvage a favorite or awkward mon honestly if it is still workable
- tell the user when the requested idea is not strong enough and pivot to the nearest viable version

## Design Principles

### 1. Recommendation First

Give one recommended team, not a loose pool of reasonable options.

### 2. Team Identity Over Slot Quality

The six slots must belong to one shared game plan. Avoid six individually defensible mons with no coherent plan.

### 3. Honesty Over Wish Fulfillment

Do not silently force a weak request into the final six. If the ask damages team quality too much, say so directly.

### 4. Practicality Over Exhaustiveness

The output should be usable by a competitive player for immediate testing. It does not need to solve every matchup on paper.

### 5. Current-Field Discipline

When current meta assumptions materially affect the build, use live verification and clearly distinguish sourced claims from inference.

## Requested Mon And Concept Handling

The skill should use this rule:

`Keep the requested mon or concept only when it still supports one coherent recommended team. If it breaks team quality too hard, say so explicitly and pivot to the nearest viable version.`

This creates three valid behaviors:

1. `Requested idea is clearly viable`
Keep it central and build the best honest shell.

2. `Requested idea is weak but salvageable`
Keep it, explain the tradeoffs, and show the best workable version.

3. `Requested idea is not realistically viable in the requested role`
Do not fake viability. State that limitation and pivot to the nearest viable version that preserves as much of the user goal as possible.

Invalid behavior:

- forcing the request into the team with no real job
- quietly dropping the request without explanation
- hiding behind three alternative builds instead of making a choice

## Output Contract

`vgc-team-builder` should always return these sections in this order:

1. `Build Goal`
2. `Recommended Team`
3. `Role Map`
4. `Set Direction`
5. `Why Each Slot Exists`
6. `Matchup Notes`
7. `Weaknesses and Next Refinements`

## Section Requirements

### `Build Goal`

State:

- the real objective of the team
- the user ask being honored
- the relevant format assumption if the user did not specify one
- whether the team is a current-field recommendation or a more inference-heavy early read

### `Recommended Team`

List the six mons that make up the one primary draft.

This section should not contain alternate branches.

### `Role Map`

Explain the team structure at a high level, including:

- primary win path
- speed or tempo control
- board-control tools
- damage profile or pressure pattern
- likely preserve logic or closer identity when that is already clear from the build

### `Set Direction`

Give lightweight set direction for each slot.

This should stay lightweight and practical, not a full export set sheet. The minimum useful level is:

- role framing
- likely item direction
- move or utility emphasis
- tera-style or equivalent positioning direction when materially relevant

The purpose is to show how each slot is supposed to function, not to lock the user into an exact solved spread.

### `Why Each Slot Exists`

Explain each slot in the context of the full team plan.

Each explanation should answer:

- what job this slot performs
- why it belongs on this specific team
- what problem it helps solve in the current field or in the requested game plan

### `Matchup Notes`

Cover the team’s intended posture into the most relevant pressure points for the build.

This should be matchup-intent guidance, not exhaustive pairing coverage. The notes should stay tied to the actual shell rather than generic type-chart commentary.

### `Weaknesses and Next Refinements`

State the real unresolved weaknesses.

This is the only place where optional future tuning ideas belong. These may include:

- one or two likely swap directions
- matchups that still look shaky
- places where live meta data would most likely change the build

This section should not become a second team recommendation.

## Build Standard

A strong final draft should have:

- one clear team identity
- explicit speed or tempo logic
- clear board-control or positioning logic
- concrete jobs for all six slots
- enough set direction for a player to start testing immediately
- matchup notes tied to the real shell
- honest unresolved weaknesses

## Freshness And Sourcing Rules

When the answer depends on current format positioning, the skill should:

- verify the current regulation or rules state
- verify whether claimed meta pressures or common shells are actually current
- label inference when a positioning claim is not directly sourced

The skill should not:

- present stale meta claims as current
- invent legality or usage status
- claim a mon is well-positioned right now without checking when that claim matters to the build

## Evaluation Implications

This design sharpens the existing rubric and eval behavior.

The fixed team-builder cases should now reward:

- one coherent recommendation instead of branchy output
- explicit requested-mon honesty
- lightweight but useful set direction
- matchup notes tied to the proposed shell
- honest weakness disclosure

The fixed team-builder cases should now penalize:

- alternate-build sprawl
- fake viability for weak requests
- slot explanations that do not connect back to the team identity
- roster-only output with no usable set direction

## Acceptance Signals

The implementation should be considered aligned with this design when:

- the skill clearly commits to one primary draft
- the output contract matches this document exactly
- weak requested ideas are handled with explicit honesty rather than silent forcing
- each slot gets lightweight practical set direction
- refinements stay in the final section instead of taking over the response

## Open Constraint

This design intentionally leaves exact set-level detail flexible. The skill should stay at the “lightweight direction” level unless the user explicitly asks for a deeper export-style build.
