export type Skill = {
  name: string;
  displayName: string;
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
  { label: "Coaching Tools", href: "#skills" },
  { label: "AI Tools", href: "#runtimes" },
  { label: "Getting Started", href: "#getting-started" },
  { label: "How It Works", href: "#how-it-works" },
];

export const quickFacts = [
  { value: "5", label: "core coaching tools" },
  { value: "3", label: "supported AI tools" },
  { value: "0", label: "invented facts — sources only" },
];

export const heroBullets = [
  "Meta research grounded in current format sources",
  "Practical team-building and matchup planning",
  "Replay review that separates real mistakes from bad luck",
];

export const coreSkills: Skill[] = [
  {
    name: "vgc-meta-research",
    displayName: "Meta Research",
    summary:
      "Current Pokemon Champions meta snapshots, trend reads, and anti-meta openings grounded in live sources — not month-old guesses.",
    emphasis: "Current-format accuracy before advice.",
  },
  {
    name: "vgc-team-builder",
    displayName: "Team Builder",
    summary:
      "One practical, coherent team built around a target Pokemon, strategy, or anti-meta goal — not a pile of weak alternatives.",
    emphasis: "One real draft, not five halfhearted ones.",
  },
  {
    name: "vgc-team-audit",
    displayName: "Team Audit",
    summary:
      "Findings-first team reviews that fix real problems without stripping a team of its identity unless the identity itself is the problem.",
    emphasis: "Clear problems, direct fixes, honest tradeoffs.",
  },
  {
    name: "vgc-lead-planner",
    displayName: "Lead Planner",
    summary:
      "Default leads, preserve targets, matchup branches, and turn-one priorities for the shells you actually run into.",
    emphasis: "Turn planning that holds up in a real set.",
  },
  {
    name: "vgc-battle-review",
    displayName: "Battle Review",
    summary:
      "Replay and turn-log review that separates the decisions that actually changed the game from variance and hindsight bias.",
    emphasis: "Focus on the moves that mattered.",
  },
];

export const supportSkills: Skill[] = [
  {
    name: "vgc-format-verifier",
    displayName: "Format Verifier",
    summary: "Checks legality, regulation, and current-format rules before any coaching advice is given.",
    emphasis: "Official rules before community interpretation.",
  },
  {
    name: "vgc-source-verifier",
    displayName: "Source Verifier",
    summary: "Audits whether a rules, usage, or matchup claim is actually sourced — and flags clearly when it is not.",
    emphasis: "Source and inference are never mixed without a label.",
  },
  {
    name: "vgc-calcs-assistant",
    displayName: "Calcs Assistant",
    summary:
      "Damage, survival, speed, and benchmark checks. Damage and KO checks are exact. Speed comparisons are framed as benchmarks unless an exact source confirms them.",
    emphasis: "Honest about what is exact and what is estimated.",
  },
  {
    name: "vgc-opponent-scout",
    displayName: "Opponent Scout",
    summary: "Turns public information about an opponent into likely team shells, possible techs, and practical prep notes.",
    emphasis: "Useful scouting without pretending to know the unknowable.",
  },
  {
    name: "vgc-practice-journal",
    displayName: "Practice Journal",
    summary:
      "Compresses testing session notes into actionable changes, patterns worth repeating, and follow-up questions for next session.",
    emphasis: "Actionable practice loops, not emotional recaps.",
  },
];

export const runtimes: Runtime[] = [
  {
    name: "Codex",
    summary: "Primary AI tool for this repo.",
    notes:
      "Open the repo in Codex and the coaching tools are available immediately. No extra configuration needed.",
    href: `${blobUrl}/docs/runtime/codex.md`,
  },
  {
    name: "Claude Code",
    summary: "Full support via the same shared coaching logic.",
    notes:
      "Open the repo in Claude Code and it picks up the same coaching tools and rules as Codex, without duplicating any logic.",
    href: `${blobUrl}/docs/runtime/claude-code.md`,
  },
  {
    name: "OpenCode",
    summary: "Secondary support with its own setup notes.",
    notes:
      "OpenCode has its own configuration layer but still pulls from the same shared coaching logic. See the setup notes for details.",
    href: `${blobUrl}/docs/runtime/opencode.md`,
  },
];

export const principles = [
  "Verify current meta, rules, and legality before presenting them as fact.",
  "Prefer official rules sources over community interpretation.",
  "Keep the coaching logic consistent across every AI tool you use.",
  "Judge coaching changes against test cases and scoring rubrics — not just whether the wording improved.",
];

export const gettingStartedSteps = [
  {
    title: "Clone the workspace",
    body: "Pull the repo locally and open it in a supported AI tool.",
    code: "git clone https://github.com/NoahJenkins/vgc-coach.git\ncd vgc-coach",
    isCode: true,
  },
  {
    title: "Open it in your preferred AI tool",
    body: "Codex, Claude Code, and OpenCode each pick up the coaching tools automatically when you open the repo. No extra setup is needed.",
    code: null,
    isCode: false,
  },
  {
    title: "Start with a real coaching task",
    body: "The fastest way to understand what it can do is to ask a real question.",
    code: "\"Build me a Pokemon Champions team around Mega Blastoise.\"\n\"Plan my leads into common rain teams.\"",
    isCode: false,
  },
];

export const repoLayers = [
  {
    title: "One shared coaching engine",
    body: "The coaching logic lives in one place. Every AI tool you use gets the same instructions, so the quality is consistent regardless of which tool you prefer.",
  },
  {
    title: "Thin connectors per AI tool",
    body: "Codex, Claude Code, and OpenCode each have a small connector that plugs into the shared coaching logic. Nothing gets duplicated or diverges.",
  },
  {
    title: "Test cases and scoring rubrics",
    body: "Fixed test cases and scoring criteria mean you can tell if a coaching change actually improved the output — not just the wording.",
  },
  {
    title: "Per-tool setup notes",
    body: "Each AI tool has its own documentation covering setup quirks and known limitations, without forking the actual coaching behavior.",
  },
];

export const footerLinks = [
  { label: "GitHub Repo", href: repoUrl },
  { label: "README", href: `${blobUrl}/README.md` },
  { label: "Contributing", href: `${blobUrl}/CONTRIBUTING.md` },
  { label: "Security", href: `${blobUrl}/SECURITY.md` },
  { label: "License", href: `${blobUrl}/LICENSE` },
];
