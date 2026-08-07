# Battle State V1

`battle-state-v1` is VGC Coach's runtime-neutral interchange format for
observed Pokemon Champions battle evidence. It is intended for battle review,
practice journaling, and future format-specific adapters. It is not a battle
simulator and does not claim to parse proprietary or undocumented replay
formats.

## Canonical artifacts

- Schema: `data/schemas/battle-state-v1.schema.json`
- Current M-B example: `data/fixtures/battle-state-v1.example.json`
- Local normalizer: `tools/ingest_battle_state.py`

The schema identifier is
`https://vgccoach.com/schemas/battle-state-v1.schema.json`, and every document
must declare `"schema_version": "battle-state-v1"`.

URL provenance fields accept absolute lowercase `http://` or `https://` URLs
with a valid hostname (or bracketed IPv6 address) and optional port from 0 to
65535. Userinfo, control characters, backslashes, malformed authorities, and
non-HTTP schemes are rejected. Date-time fields use RFC 3339 syntax, including
an explicit `Z` or numeric offset.

## Normalize a record

```bash
python3 tools/ingest_battle_state.py battle.json --pretty
python3 tools/ingest_battle_state.py - --output normalized.json
```

The command accepts one JSON document from an explicit file or standard input,
validates the V1 contract, and emits deterministic JSON. Input is limited to
1,048,576 bytes. It performs no network access, opens no path named inside the
document, never edits the input, and writes only the explicit `--output` path
when one is supplied. Output replacement occurs only after validation succeeds.

## Evidence boundary

- Omit facts that were not observed. Use `null` only where the schema permits it.
- Do not infer opponent items, abilities, moves, spreads, decisions, HP rolls,
  or hidden RNG.
- `preview_roster`, `selected`, `active`, and `bench` may contain only what the
  source actually established. Empty or omitted optional collections do not
  imply a hidden value.
- When `active` or `bench` is present, it describes the earliest board state in
  the event record; subsequent state changes belong in ordered turn events. A
  Pokemon identity (species plus form) cannot occupy both arrays at once.
- Turn events are evidence, not a full engine state. Their `(turn, sequence)`
  pairs must be unique and strictly increasing.
- If both series fields are known, `game_number` cannot exceed `best_of`.
- A target with `side: "field"` represents the shared field only, so it cannot
  include species, form, or position. Player-side targets may include those
  observed slot details.
- Revealed `value` and `evidence` strings must contain non-whitespace text.
- `outcome.result` is from the `self` perspective. `win` requires winner
  `self`, `loss` requires `opponent`, and `draw` requires `null`; `incomplete`
  and `unknown` may omit winner or set it to `null`.
- A source adapter may emit this contract only when it can map its documented
  input fields honestly. Unsupported raw formats remain unsupported.
