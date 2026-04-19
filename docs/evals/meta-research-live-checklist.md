# Meta Research Live Checklist

Use this checklist when pressure-testing `vgc-meta-research` without `plugin-eval`.

## Goal

Confirm that the skill can answer real current-meta prompts with:

- correct format assumptions
- live source discipline
- useful competitive framing
- honest uncertainty handling

## Prompts To Run

### Prompt 1

`Use $vgc-meta-research to summarize the current Pokemon Champions Reg M-A metagame and identify two anti-meta openings.`

Pass if:

- the answer confirms Reg M-A and Mega-only assumptions first
- the answer names real current threats and cores
- the anti-meta ideas target specific popular teams or strategies

### Prompt 2

`Use $vgc-meta-research to tell me whether Hisuian Zoroark is a real current meta pick or mostly a niche angle in Champions.`

Pass if:

- the answer does not invent strong support if the data is thin
- the answer gives a competitive-direct conclusion
- the answer explains the role the mon can realistically play

### Prompt 3

`Use $vgc-meta-research to explain whether Terastallization is active in the current Champions regulation and how that changes team-building assumptions.`

Pass if:

- the answer uses official rules sources first
- the answer states the active mechanic picture correctly
- the answer does not drift into stale Scarlet/Violet assumptions

## Review Standard

Fail the run if any output:

- treats inactive mechanics as active
- presents memory as live fact
- gives unsourced confidence on current popularity
- confuses official legality with community usage data

## Supporting Artifacts

- `data/snapshots/champions-reg-m-a-2026-04-18.json`
- `skills/vgc-meta-research/references/source-policy.md`
- `skills/vgc-meta-research/references/current-source-map.md`
- `data/rubrics/meta-research-rubric.md`
