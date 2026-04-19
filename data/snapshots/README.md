# Meta Snapshots

This folder stores versioned metagame snapshots used by the coaching skills.

Each snapshot should include:

- format metadata
- rules version
- source provenance
- freshness window
- usage leaders
- common cores
- sample teams

Snapshots are the shared truth layer for coaching outputs. Skills should prefer these artifacts over ad hoc claims.

## Current Usage

- Keep dated snapshots here for reproducible examples and fallback context.
- For `vgc-meta-research`, snapshots support live work but do not replace live verification for "current" questions.
- When the active format is moving quickly, keep `fresh_until` short and note that the snapshot is early-meta if applicable.
