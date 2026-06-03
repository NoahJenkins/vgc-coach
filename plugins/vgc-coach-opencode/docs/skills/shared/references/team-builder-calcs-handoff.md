# Team Builder Calcs Handoff

Use this reference when `vgc-team-builder` enters `battle-ready` mode and needs `vgc-calcs-assistant` to help lock final spreads.

## Purpose

`vgc-team-builder` stays the public entrypoint for battle-ready teams.

`vgc-calcs-assistant` is a support step for:

- narrow benchmark questions
- spread tradeoffs
- nature tradeoffs
- preserve or KO thresholds that materially change the final build

Do not hand off the whole team for freeform optimization.

## When To Invoke

Invoke `vgc-calcs-assistant` only when all of these are true:

- the user explicitly requested battle-ready output
- the six-mon shell is already chosen
- the benchmark could materially change EVs, nature, item direction, or preserve decisions
- the question can be framed as one or two narrow benchmark decisions

Do not invoke it for every slot automatically. Utility mons may keep heuristic spreads.

## Locked Assumptions Before Handoff

Before the handoff, `vgc-team-builder` should lock:

- species
- level 50
- mega route if applicable
- provisional item
- provisional nature
- candidate move package
- relevant field assumptions such as weather, screens, boosts, or chip

If too many of those are still missing, keep the spread heuristic and do not pretend the calc pass is more precise than it is.

## Handoff Payload Shape

The builder should hand off a benchmark request that states:

- the spread decision being tested
- the benchmark type: speed, survival, damage, or KO
- attacker and defender species when relevant
- move when relevant
- item, ability, nature, and EV assumptions
- any field assumptions
- what final build choice depends on the answer

Good handoff examples:

- `Does this Rotom-Wash spread need more bulk to survive Mega Charizard Y sun pressure after chip?`
- `Does this Sneasler benchmark still matter if the team already has Tailwind support?`
- `Does this Mega Steelix spread need extra Attack to secure the Garchomp damage threshold, or is bulk better?`

Bad handoff examples:

- `Optimize this whole team`
- `Find the best spreads for every slot`
- `Tell me everything this team needs`

## Exactness Boundary

`vgc-calcs-assistant` may use exact browser evidence only for:

- damage
- KO
- survival

Speed remains assumption-framed in v1.

If exact browser eligibility fails or exact verification returns `fallback` or `blocked`:

- say exact external verification did not complete
- keep the assumptions explicit
- answer with the smallest honest benchmark framing that still helps the build

## Return Contract

For team-builder handoffs, `vgc-calcs-assistant` should return:

- the benchmark goal
- the locked assumptions
- whether exact verification ran
- the spread consequence
- what changed in EVs, nature, or preserve logic

`vgc-team-builder` then synthesizes the final `Battle-Ready Spreads` output for the user.
