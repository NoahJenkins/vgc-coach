# VGC Coach

VGC Coach is an open-source AI coaching assistant for Pokemon VGC (Video Game Championships).

It gives you a set of coaching tools — called *skills* — that run inside AI assistants like Codex, Claude Code, or OpenCode. Ask them in plain English to help with team building, meta research, lead planning, replay review, and other prep work.

This is not a standalone app or ladder client. You clone this repo, open it in a supported AI tool, and use natural-language prompts to get coaching help. Developers and contributors can find architecture notes in [How The Repo Works](#how-the-repo-works).

## Open Source Status

- License: [Apache-2.0](./LICENSE)
- Contributions: [CONTRIBUTING.md](./CONTRIBUTING.md)
- Security reporting: [SECURITY.md](./SECURITY.md)

## Use This Repo

The simplest way to use these skills is to clone this repository and open it in a supported AI tool. There is nothing to install or configure beyond cloning — just open it and start asking questions.

```bash
git clone https://github.com/NoahJenkins/vgc-coach.git
cd vgc-coach
```

After cloning, open the repo in a supported AI tool:

- **Codex** — skills load automatically from `.agents/skills/`
- **Claude Code** — skills load automatically from `.claude/skills/`
- **OpenCode** — supported via `opencode.json` and `.opencode/skills/`

Then ask the AI tool in plain English:

- "Build me a Pokemon Champions team around Mega Blastoise."
- "Audit this team for bad matchups and weak slots."
- "Plan my leads into common rain and Trick Room teams."
- "Review this replay and tell me what mistakes actually mattered."
- "Give me a current meta snapshot before I build."

Setup notes and AI-tool-specific details:

- [Codex runtime](./docs/runtime/codex.md)
- [Claude Code runtime](./docs/runtime/claude-code.md)
- [OpenCode runtime](./docs/runtime/opencode.md)

## Web Site Deployment

The project website lives in `site/` and is deployed on Vercel from that directory.

- Production host: Vercel
- Vercel Root Directory: `site`
- Vercel config: [`site/vercel.json`](./site/vercel.json)

When importing to Vercel, set the Root Directory to `site` so the build runs against the Vite app.

## Prerequisites

This repo does not have a root app package to install. The main requirements are:

- `git` to clone the repository
- a supported AI tool such as Codex, Claude Code, or OpenCode
- `python3` if you want to use the optional exact-calc helper at `tools/browser_damage_calc.py`

### Install Core Dependencies

#### macOS (Homebrew)

```bash
brew install git python node
```

#### Windows (PowerShell with `winget`)

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id OpenJS.NodeJS.LTS -e
```

#### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip nodejs npm
```

For other Linux distributions, install the equivalent packages from your distro's package manager.

## Optional Setup

### Exact Calc Helper

`vgc-calcs-assistant` can use `python3 tools/browser_damage_calc.py` for exact damage, KO, and survival checks. This requires a local `agent-browser` install (not included in this repo).

## How The Repo Works

> **For contributors and developers** — this section covers internal architecture. VGC players can skip to [Skill Catalog](#skill-catalog).

- `skills/` is the source of truth for all coaching logic. This is what you edit.
- `.agents/skills/`, `.claude/skills/`, and `.opencode/skills/` are thin wrappers that point AI tools to the shared packages in `skills/`.
- `docs/skills/` contains examples and references that support the shared skills.
- `data/fixtures/evals/` and `data/rubrics/` are how skill quality is judged — test cases and scoring rubrics that changes must pass.
- `docs/runtime/` documents AI-tool-specific behavior without duplicating the underlying skill logic.

To adapt these skills for your own setup, use `skills/` as the source of truth and keep any AI-tool-specific wrappers minimal.

## Core Coaching Tools

The current focus is five core coaching skills:

1. `vgc-meta-research`
2. `vgc-team-builder`
3. `vgc-team-audit`
4. `vgc-lead-planner`
5. `vgc-battle-review`

Support skills reinforce that core layer:

- `vgc-format-verifier`
- `vgc-source-verifier`
- `vgc-calcs-assistant`
- `vgc-opponent-scout`
- `vgc-practice-journal`

## Skill Catalog

### Core Focus Skills

- `vgc-meta-research`: live Pokemon Champions meta snapshots, trend reads, and anti-meta openings grounded in current sources
- `vgc-team-builder`: one practical, coherent team around a target mon, strategy, or anti-meta goal
- `vgc-team-audit`: findings-first team reviews that preserve identity unless the identity itself is the problem
- `vgc-lead-planner`: default leads, matchup branches, preserve targets, and turn-one priorities
- `vgc-battle-review`: replay or turn-log review that separates real mistakes from variance and hindsight

### Support Skills

- `vgc-format-verifier`: verify legality, regulation, and current-format truth before coaching
- `vgc-source-verifier`: audit whether a meta, matchup, or rules claim is actually sourced cleanly
- `vgc-calcs-assistant`: damage, survival, speed, and benchmark framing; exact damage/KO/survival calculations are supported today; speed comparisons are stated as assumptions unless verified manually
- `vgc-opponent-scout`: turn public info into likely shells, techs, and prep notes
- `vgc-practice-journal`: compress testing notes into next-session changes and follow-up questions

## What's Included Today

The repo already includes:

- Shared coaching skill packages under `skills/`
- Codex support under `.agents/skills/`
- Claude Code support under `.claude/skills/`
- OpenCode support under `opencode.json`, `.opencode/skills/`, and `.opencode/commands/`
- AI-tool-specific usage notes under `docs/runtime/`
- Skill examples and references under `docs/skills/`
- Eval test cases under `data/fixtures/evals/`
- Scoring rubrics under `data/rubrics/`
- Meta snapshot history under `data/snapshots/`
- Helper tools under `tools/`
- Exact damage/KO/survival calc support for `vgc-calcs-assistant` via `python3 tools/browser_damage_calc.py`

## Planned Work

These are still in progress, not yet available:

- Local eval runner tooling
- Replay ingestion utilities
- Battle-state data schema
- Broader exact calc support beyond damage, KO, and survival

## Principles

- Verify current meta, rules, and legality before presenting them as current.
- Prefer official rules sources; use community sources only for trends and archetype interpretation.
- Keep shared coaching logic AI-tool-neutral where possible.
- Avoid duplicating skill logic into AI-tool-specific copies.
- Judge skill changes against test cases and rubrics, not just cleaner wording.

## Where To Start

**For VGC players:**
- [Skill Catalog](#skill-catalog): overview of what VGC Coach can help with today
- [Use This Repo](#use-this-repo): how to clone and start asking questions

**For developers and contributors:**
- [Codex runtime](./docs/runtime/codex.md), [Claude Code runtime](./docs/runtime/claude-code.md), [OpenCode runtime](./docs/runtime/opencode.md): AI-tool-specific usage notes
- [AGENTS.md](./AGENTS.md): repo rules and project constraints
- [CONTRIBUTING.md](./CONTRIBUTING.md): contribution scope and validation expectations
- [SECURITY.md](./SECURITY.md): responsible disclosure guidance
- [data/snapshots/README.md](./data/snapshots/README.md): meta snapshot artifact format

## Repo Layout

Abridged view of the main public-facing structure:

```text
vgc-coach/
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── .agents/
│   └── skills/
├── .claude/
│   ├── CLAUDE.md
│   └── skills/
├── .opencode/
│   ├── commands/
│   └── skills/
├── opencode.json
├── data/
│   ├── fixtures/
│   │   └── evals/
│   ├── rubrics/
│   └── snapshots/
├── docs/
│   ├── evals/
│   ├── runtime/
│   └── skills/
├── tools/
└── skills/
```
