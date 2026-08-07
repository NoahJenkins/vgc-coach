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
- Turn events are evidence, not a full engine state. Their `(turn, sequence)`
  pairs must be unique and strictly increasing.
- A source adapter may emit this contract only when it can map its documented
  input fields honestly. Unsupported raw formats remain unsupported.
