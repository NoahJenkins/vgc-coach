# Browser Exactness

## Exact Browser Path

Use the repo-local wrapper for fully specified damage, KO, and survival questions:

`python3 tools/browser_damage_calc.py --request-file <json>`

Current v1 backend:

- `agent-browser`
- Pikalytics as the first supported site

The browser path is a support tool, not the user-facing output. Final answers still need to stay decision-first.

## Exact Eligibility

Attempt exact browser execution only when all of these are true:

- the question is about damage, KO odds, or survival
- attacker species is known
- defender species is known
- move is known
- level, nature, item, ability, and spread assumptions are explicit enough to encode honestly
- the spread is legal for the active ruleset

If any of those fail, stay in benchmark-framing mode.

## Fallback Rules

If the browser path returns `fallback` or `blocked`:

- say exact external verification did not complete
- keep the assumptions list explicit
- continue with the smallest honest benchmark answer that still helps the decision
- do not restate stale or guessed numbers as exact

## Scope Boundary

v1 exact browser support covers:

- damage ranges
- KO odds
- survival thresholds

v1 exact browser support does not cover:

- speed tiers
- browser screenshots in normal responses
- unsupported field mechanics that the wrapper cannot encode safely
