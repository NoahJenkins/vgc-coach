# Meta Snapshots

This folder stores versioned metagame snapshots used by the coaching skills.

Each snapshot should include:

- format metadata
- rules version
- source provenance
- `temporal_status` as `current` or `historical`
- the official regulation `active_window`

Metagame snapshots should additionally include a short freshness window, usage leaders, common cores, and sample teams. Official format-only snapshots may omit usage data when it has not been independently verified.

Snapshots are dated support and reproducibility artifacts, not a replacement for live verification on present-tense questions.

## Current Usage

- Keep dated snapshots here for reproducible examples and fallback context.
- For `vgc-meta-research`, snapshots support live work but do not replace live verification for "current" questions.
- When the active format is moving quickly, keep `fresh_until` short and note that the snapshot is early-meta if applicable.
- Mark expired regulation snapshots `historical`; `python3 tools/check_format_freshness.py` fails when a `current` designation is past its official end.
