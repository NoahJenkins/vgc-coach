# Codex Skill Metadata

The canonical Codex UI metadata for VGC Coach now lives inside each skill package at:

- `skills/<skill-name>/agents/openai.yaml`

These files are the source of truth for app-visible skill labels, short descriptions, and default prompts.

The old per-skill YAML files were removed from this folder to avoid keeping two editable copies of the same runtime metadata.
