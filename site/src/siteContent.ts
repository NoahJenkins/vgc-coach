export type Skill = {
  name: string;
  summary: string;
  emphasis: string;
};

export type Runtime = {
  name: string;
  summary: string;
  notes: string;
  href: string;
};

const repoUrl = "https://github.com/NoahJenkins/vgc-coach";
const blobUrl = `${repoUrl}/blob/main`;

export const navLinks = [
  { label: "What It Does", href: "#what-it-does" },
  { label: "Skills", href: "#skills" },
  { label: "Runtimes", href: "#runtimes" },
  { label: "Getting Started", href: "#getting-started" },
  { label: "How It Works", href: "#how-it-works" },
];

export const quickFacts = [
  { value: "5", label: "MVP coaching skills" },
  { value: "3", label: "supported runtimes" },
  { value: "1", label: "shared skill source of truth" },
];

export const heroBullets = [
  "Live meta research grounded in current sources",
  "Practical team-building and matchup planning",
  "Replay review and eval-driven skill hardening",
];

export const coreSkills: Skill[] = [
  {
    name: "vgc-meta-research",
    summary:
      "Live Pokemon Champions meta snapshots, trend reads, and anti-meta openings grounded in current sources.",
    emphasis: "Current-format accuracy before advice.",
  },
  {
    name: "vgc-team-builder",
    summary:
      "One practical, coherent team around a target mon, strategy, or anti-meta goal.",
    emphasis: "One real draft, not a pile of weak alternates.",
  },
  {
    name: "vgc-team-audit",
    summary:
      "Findings-first team reviews that preserve identity unless the identity itself is the problem.",
    emphasis: "Clear problems, direct fixes, honest tradeoffs.",
  },
  {
    name: "vgc-lead-planner",
    summary:
      "Default leads, preserve targets, matchup branches, and turn-one priorities for common shells.",
    emphasis: "Turn planning that is usable in an actual set.",
  },
  {
    name: "vgc-battle-review",
    summary:
      "Replay or turn-log review that separates real mistakes from variance and hindsight bias.",
    emphasis: "Focus on decisions that actually changed the game.",
  },
];

export const supportSkills: Skill[] = [
  {
    name: "vgc-format-verifier",
    summary: "Verify legality, regulation, and current-format truth before coaching.",
    emphasis: "Official rules before community interpretation.",
  },
  {
    name: "vgc-source-verifier",
    summary: "Audit whether a rules, usage, or matchup claim is actually sourced cleanly.",
    emphasis: "Clear distinction between source and inference.",
  },
  {
    name: "vgc-calcs-assistant",
    summary:
      "Damage, survival, speed, and benchmark framing. Exact support is currently limited to damage, KO, and survival.",
    emphasis: "Speed guidance stays assumption-framed unless exact support exists.",
  },
  {
    name: "vgc-opponent-scout",
    summary: "Turn public information into likely shells, techs, and prep notes.",
    emphasis: "Useful scouting without pretending to know what is unknowable.",
  },
  {
    name: "vgc-practice-journal",
    summary:
      "Compress testing notes into next-session changes, repeated patterns, and follow-up questions.",
    emphasis: "Actionable practice loops over emotional recap.",
  },
];

export const runtimes: Runtime[] = [
  {
    name: "Codex",
    summary: "Primary runtime for this repo.",
    notes:
      "Repo-local wrappers under .agents/skills stay thin and point back to shared skill packages under skills/.",
    href: `${blobUrl}/docs/runtime/codex.md`,
  },
  {
    name: "Claude Code",
    summary: "Thin adapter over the same shared skill packages.",
    notes:
      "Claude support reuses AGENTS.md, shared skills, eval fixtures, and a docs shim rather than forking logic.",
    href: `${blobUrl}/docs/runtime/claude-code.md`,
  },
  {
    name: "OpenCode",
    summary: "Additive runtime support with its own wrapper namespace.",
    notes:
      "OpenCode adapters remain thin and keep runtime-specific behavior in docs/runtime and .opencode wrappers.",
    href: `${blobUrl}/docs/runtime/opencode.md`,
  },
];

export const principles = [
  "Verify current meta, rules, and legality before presenting them as current.",
  "Prefer official rules sources over community sources.",
  "Keep shared coaching logic runtime-neutral wherever possible.",
  "Judge skill changes against fixtures and rubrics, not just nicer wording.",
];

export const gettingStartedSteps = [
  {
    title: "Clone the workspace",
    body: "Pull the repo locally and open it in a supported coding agent.",
    code: "git clone https://github.com/NoahJenkins/vgc-coach.git\ncd vgc-coach",
  },
  {
    title: "Use a supported runtime",
    body: "Codex, Claude Code, and OpenCode each have thin repo-local discovery layers over the same shared skills.",
    code: "Open the repo in your preferred runtime and invoke a matching skill or ask naturally.",
  },
  {
    title: "Start with a real coaching task",
    body: "The fastest way to understand the project is to use one of the core skills on a practical question.",
    code: "\"Build me a Pokemon Champions team around Mega Blastoise.\"\n\"Plan my leads into common rain teams.\"",
  },
];

export const repoLayers = [
  {
    title: "Shared skill packages",
    body: "skills/ is the only canonical editable source for shared coaching behavior.",
  },
  {
    title: "Runtime discovery shims",
    body: ".agents/skills, .claude/skills, and .opencode/skills stay thin and point back to the shared packages.",
  },
  {
    title: "Validation surface",
    body: "data/fixtures/evals and data/rubrics are used to judge whether a skill actually got better.",
  },
  {
    title: "Runtime docs",
    body: "docs/runtime explains runtime-specific behavior without duplicating the coaching logic.",
  },
];

export const footerLinks = [
  { label: "GitHub Repo", href: repoUrl },
  { label: "README", href: `${blobUrl}/README.md` },
  { label: "Contributing", href: `${blobUrl}/CONTRIBUTING.md` },
  { label: "Security", href: `${blobUrl}/SECURITY.md` },
  { label: "License", href: `${blobUrl}/LICENSE` },
];
