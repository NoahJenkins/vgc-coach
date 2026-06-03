# Battle-Ready Legality Ledger

Use this reference for `vgc-team-builder` battle-ready outputs.

## Purpose

A battle-ready build needs a stricter legality standard than a normal team shell.

Species legality alone is not enough when the build names:

- exact held items
- exact four-move sets
- export-ready status

## Minimum Ledger Coverage

For battle-ready builds, the legality ledger should cover:

- the requested species or form
- the five supporting species
- mega stones
- any non-mega held item named exactly in the final build
- any exact four-move set named in the final build
- active mechanics that materially shape the build

## Output Rules

If a named item or move is verified:

- it may appear as confirmed in `Battle-Ready Spreads`
- it may contribute to `export-ready` status

If a named item or move is not verified:

- label it inline as `unverified/provisional`
- keep the set usable with move-package or role wording
- downgrade `Export Status` away from `export-ready`

## Export Status Labels

Use one of these exact labels:

- `export-ready`
- `battle-ready but not export-ready`
- `provisional build blocked by legality or calc gaps`

## Practical Boundary

A build may still be battle-ready when:

- the six is coherent
- spreads are justified
- benchmark notes are clear
- some items or moves remain provisional

But it is not export-ready until the named item and move choices are verified by the ledger.
