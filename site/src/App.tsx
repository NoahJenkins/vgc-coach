import { useEffect, useState, type KeyboardEvent } from "react";
import { trustData } from "./generated/trustData";
import {
  coachingExamples,
  coreSkills,
  evidenceSteps,
  footerLinks,
  gettingStartedSteps,
  heroBullets,
  navLinks,
  prepSignals,
  principles,
  quickFacts,
  repoLayers,
  runtimeInstalls,
  runtimes,
  supportSkills,
} from "./siteContent";

type Theme = "light" | "dark";
type CopyStatus = "copied" | "error";

const themeStorageKey = "vgc-coach-theme";

function getInitialTheme(): Theme {
  if (typeof window === "undefined") {
    return "light";
  }

  const storedTheme = window.localStorage.getItem(themeStorageKey);

  if (storedTheme === "dark" || storedTheme === "light") {
    return storedTheme;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function App() {
  const currentYear = new Date().getFullYear();
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [theme, setTheme] = useState<Theme>(getInitialTheme);
  const [activeExampleId, setActiveExampleId] = useState(
    coachingExamples[0].id,
  );
  const [copyStatus, setCopyStatus] = useState<{
    exampleId: string;
    status: CopyStatus;
  } | null>(null);
  const externalLinkProps = {
    target: "_blank",
    rel: "noreferrer",
  } as const;
  const closeMobileNav = () => {
    setIsMobileNavOpen(false);
  };
  const toggleTheme = () => {
    setTheme((currentTheme) => (currentTheme === "dark" ? "light" : "dark"));
  };

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem(themeStorageKey, theme);
  }, [theme]);

  const selectExample = (exampleId: (typeof coachingExamples)[number]["id"]) => {
    setActiveExampleId(exampleId);
    setCopyStatus(null);
  };

  const handleExampleKeyDown = (
    event: KeyboardEvent<HTMLButtonElement>,
    index: number,
  ) => {
    let nextIndex: number | null = null;

    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      nextIndex = (index + 1) % coachingExamples.length;
    } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      nextIndex = (index - 1 + coachingExamples.length) % coachingExamples.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = coachingExamples.length - 1;
    }

    if (nextIndex === null) {
      return;
    }

    event.preventDefault();
    const nextExample = coachingExamples[nextIndex];
    selectExample(nextExample.id);
    document.getElementById(`example-tab-${nextExample.id}`)?.focus();
  };

  const copyPrompt = async (
    example: (typeof coachingExamples)[number],
  ) => {
    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error("Clipboard API unavailable");
      }
      await navigator.clipboard.writeText(example.prompt);
      setCopyStatus({ exampleId: example.id, status: "copied" });
    } catch {
      setCopyStatus({ exampleId: example.id, status: "error" });
    }
  };

  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <div className="page-shell" id="top">
        <div className="background-texture" aria-hidden="true" />
        <header className="site-header">
          <a className="brand" href="#top">
            <span className="brand-mark" aria-hidden="true">
              VGC
            </span>
            <span className="brand-copy">
              <strong>Coach</strong>
              <span>Open-source skill workspace</span>
            </span>
          </a>
          <div
            className="site-nav-shell"
            data-open={isMobileNavOpen ? "true" : "false"}
          >
            <nav className="site-nav" aria-label="Primary" id="primary-navigation">
              {navLinks.map((link) => (
                <a key={link.href} href={link.href} onClick={closeMobileNav}>
                  {link.label}
                </a>
              ))}
              <a
                className="site-nav-link-external"
                href="https://github.com/NoahJenkins/vgc-coach"
                aria-label="View the VGC Coach repository on GitHub"
                onClick={closeMobileNav}
                {...externalLinkProps}
              >
                View Repo
              </a>
            </nav>
          </div>
          <div className="header-actions">
            <button
              className="theme-toggle"
              type="button"
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
              aria-pressed={theme === "dark"}
              data-theme-mode={theme}
              onClick={toggleTheme}
            >
              <span className="theme-toggle-track" aria-hidden="true">
                <span className="theme-toggle-icon" />
              </span>
              <span className="theme-toggle-label">
                {theme === "dark" ? "Dark" : "Light"}
              </span>
            </button>
            <a
              className="button button-ghost header-repo-link"
              href="https://github.com/NoahJenkins/vgc-coach"
              aria-label="View the VGC Coach repository on GitHub"
              {...externalLinkProps}
            >
              View Repo
            </a>
            <button
              className="button button-ghost header-menu-toggle"
              type="button"
              aria-controls="primary-navigation"
              aria-expanded={isMobileNavOpen}
              onClick={() => {
                setIsMobileNavOpen((current) => !current);
              }}
            >
              <span className="header-menu-toggle-icon" aria-hidden="true">
                <span />
                <span />
                <span />
              </span>
              <span>{isMobileNavOpen ? "Close" : "Menu"}</span>
            </button>
          </div>
        </header>

        <main id="main-content">
          <section className="hero section">
            <div className="hero-copy">
              <div className="eyebrow">Pokemon Champions prep room</div>
              <h1>
                A sharper coaching layer for current-format VGC prep.
              </h1>
              <p className="hero-intro">
                VGC Coach is an open-source coaching workspace that gives
                Codex, Claude Code, and OpenCode structured tools for
                team-building, meta research, lead planning, replay review, and
                consistent prep work, grounded in current format rules instead
                of guesses.
              </p>
              <div className="hero-actions">
                <a className="button button-primary" href="#getting-started">
                  Start Using It
                </a>
                <a className="button button-secondary" href="#skills">
                  Explore Skills
                </a>
              </div>
              <ul className="hero-bullets">
                {heroBullets.map((bullet) => (
                  <li key={bullet}>{bullet}</li>
                ))}
              </ul>
            </div>

            <aside className="hero-console" aria-label="VGC Coach prep console">
              <div className="console-topline">
                <span>Prep console</span>
                <strong>Source-aware</strong>
              </div>
              <div className="bracket-map">
                <div className="bracket-board-top">
                  <span>Top cut</span>
                  <strong>Matchup route</strong>
                </div>
                <svg
                  className="tournament-bracket"
                  viewBox="0 0 620 260"
                  role="img"
                  aria-label="Tournament bracket route from verified sources to team plan"
                >
                  <title>Top-cut matchup bracket showing rules, meta, leads, and review paths into one team plan</title>
                  <g className="bracket-entries">
                    {[
                      { y: 24, seed: "01", label: "Rules" },
                      { y: 54, seed: "02", label: "Meta" },
                      { y: 84, seed: "03", label: "Team" },
                      { y: 114, seed: "04", label: "Calcs" },
                      { y: 154, seed: "05", label: "Scout" },
                      { y: 184, seed: "06", label: "Leads" },
                      { y: 214, seed: "07", label: "Replay" },
                      { y: 244, seed: "08", label: "Journal" },
                    ].map((entry) => (
                      <g key={entry.seed}>
                        <circle cx="22" cy={entry.y} r="10" />
                        <text className="bracket-seed" x="22" y={entry.y + 4}>
                          {entry.seed}
                        </text>
                        <text className="bracket-entry-label" x="40" y={entry.y + 4}>
                          {entry.label}
                        </text>
                      </g>
                    ))}
                  </g>

                  <g className="bracket-line">
                    <path d="M106 24 H142 V54 H106" />
                    <path d="M106 84 H142 V114 H106" />
                    <path d="M142 39 H178 V99 H142" />
                    <path d="M106 154 H142 V184 H106" />
                    <path d="M106 214 H142 V244 H106" />
                    <path d="M142 169 H178 V229 H142" />
                    <path d="M178 69 H222 V199 H178" />
                    <path d="M222 134 H286" />
                  </g>

                  <path className="route-line route-primary" d="M178 69 H214 V92 H250 V116 H292 V134 H340" />
                  <path className="route-line route-alt" d="M178 229 H214 V202 H250 V178 H292 V154 H340" />
                  <path className="route-line route-risk" d="M142 99 H198 V134 H252 V154 H292" />
                  <path className="route-line route-risk" d="M142 169 H198 V154 H252 V134 H292" />

                  <g className="bracket-finish">
                    <circle cx="364" cy="134" r="17" />
                    <path d="M352 134 H376" />
                    <path d="M364 122 V146" />
                  </g>

                  <g className="bracket-labels">
                    <text x="424" y="54">Safe lead</text>
                    <text x="424" y="91">Pivot line</text>
                    <text x="424" y="128">Risk to verify</text>
                    <text x="424" y="200">Team plan</text>
                  </g>
                  <g className="bracket-key-lines">
                    <path className="route-primary" d="M384 48 H414" />
                    <path className="route-alt" d="M384 85 H414" />
                    <path className="route-risk" d="M384 122 H414" />
                    <path className="bracket-line-sample" d="M384 194 H414" />
                  </g>
                </svg>
              </div>
              <div className="console-grid">
                {prepSignals.map((signal) => (
                  <div className="signal-tile" key={signal.label}>
                    <span>{signal.label}</span>
                    <strong>{signal.value}</strong>
                  </div>
                ))}
              </div>
              <div className="evidence-panel">
                <div className="panel-label">Evidence queue</div>
                {evidenceSteps.map((step, index) => (
                  <div className="evidence-row" key={step.label}>
                    <span>{String(index + 1).padStart(2, "0")}</span>
                    <div>
                      <strong>{step.label}</strong>
                      <p>{step.detail}</p>
                    </div>
                  </div>
                ))}
              </div>
            </aside>
          </section>

        <section className="section split-section" id="what-it-does">
          <div className="section-heading">
            <div className="eyebrow">What it does</div>
            <h2>A control room for the coaching questions that decide sets.</h2>
          </div>
          <div className="split-copy">
            <p>
              VGC Coach gives your AI assistant structured, quality-controlled
              coaching tools for real Pokemon Champions prep: current meta
              research, team-building, matchup planning, replay feedback, and
              practice tracking.
            </p>
            <p>
              The coaching logic is shared across every supported AI tool, so
              it stays consistent. Fixed test cases and scoring rubrics exist so
              you can tell when a change actually made the coaching better, not
              just whether it sounds better.
            </p>
            <ul className="trust-list" aria-label="VGC Coach quality checks">
              {quickFacts.map((fact) => (
                <li key={fact}>{fact}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="section" id="skills">
          <div className="section-heading compact">
            <div className="eyebrow">Core coaching tools</div>
            <h2>Five lanes through the same prep wall.</h2>
          </div>
          <div className="skill-grid">
            {coreSkills.map((skill) => (
              <article className="skill-card skill-card-core" key={skill.name}>
                <p className="card-kicker">Core tool</p>
                <h3>{skill.displayName}</h3>
                <p className="skill-slug">{skill.name}</p>
                <p>{skill.summary}</p>
                <span>{skill.emphasis}</span>
              </article>
            ))}
          </div>
        </section>

        <section className="section examples-layout" id="examples">
          <div className="section-heading compact">
            <div className="eyebrow">Try a coaching tool</div>
            <h2>Bring a real prep question. Get a usable next move.</h2>
            <p className="section-intro">
              These abbreviated examples show the shape of the coaching, not a
              frozen meta answer. Current-format claims are verified live when
              you use the tool.
            </p>
          </div>
          <div className="example-desk">
            <div
              className="example-tabs"
              role="tablist"
              aria-label="Coaching example"
            >
              {coachingExamples.map((example, index) => (
                <button
                  className="example-tab"
                  id={`example-tab-${example.id}`}
                  key={example.id}
                  type="button"
                  role="tab"
                  aria-selected={activeExampleId === example.id}
                  aria-controls={`example-panel-${example.id}`}
                  tabIndex={activeExampleId === example.id ? 0 : -1}
                  onClick={() => selectExample(example.id)}
                  onKeyDown={(event) => handleExampleKeyDown(event, index)}
                >
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <strong>{example.tabLabel}</strong>
                  <small>{example.skill}</small>
                </button>
              ))}
            </div>
            <div className="example-panels">
              {coachingExamples.map((example) => {
                const status =
                  copyStatus?.exampleId === example.id
                    ? copyStatus.status
                    : null;
                return (
                  <article
                    className="example-panel"
                    id={`example-panel-${example.id}`}
                    key={example.id}
                    role="tabpanel"
                    aria-labelledby={`example-tab-${example.id}`}
                    hidden={activeExampleId !== example.id}
                    tabIndex={0}
                  >
                    <div className="example-brief">
                      <p className="card-kicker">Prep brief</p>
                      <h3>{example.displayName}</h3>
                      <p>{example.situation}</p>
                    </div>
                    <div className="prompt-block">
                      <div className="prompt-topline">
                        <span>Copyable prompt</span>
                        <button
                          type="button"
                          className="copy-button"
                          onClick={() => void copyPrompt(example)}
                        >
                          {status === "copied"
                            ? "Copied"
                            : status === "error"
                              ? "Try copy again"
                              : "Copy prompt"}
                        </button>
                      </div>
                      <p>{example.prompt}</p>
                      <p className="copy-status" aria-live="polite">
                        {status === "copied" && "Prompt copied to your clipboard."}
                        {status === "error" &&
                          "Copy was blocked. Select the prompt text and copy it manually."}
                      </p>
                    </div>
                    <div className="output-sheet">
                      <div className="output-heading">
                        <span>Representative output</span>
                        <small>Abbreviated</small>
                      </div>
                      <ol>
                        {example.output.map((item) => (
                          <li key={item.label}>
                            <strong>{item.label}</strong>
                            <span>{item.detail}</span>
                          </li>
                        ))}
                      </ol>
                    </div>
                    <p className="example-caveat">
                      Live use rechecks current regulation and source-sensitive
                      claims. This sample demonstrates structure, not current
                      field evidence.
                    </p>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section className="section trust-layout" id="trust">
          <div className="section-heading compact">
            <div className="eyebrow">Trust and freshness</div>
            <h2>See what is fixed in the repo, and what still needs a live check.</h2>
            <p className="section-intro">
              This board is generated from versioned snapshots, source roles,
              eval fixtures, and rubrics in the repository. It reports the
              validation structure without pretending a live model just ran.
            </p>
          </div>
          <div className="trust-board">
            <article className="regulation-ticket">
              <div className="ticket-topline">
                <span>Current repository snapshot</span>
                <strong>v{trustData.version}</strong>
              </div>
              <div className="ticket-status">
                <span className="status-dot" aria-hidden="true" />
                Snapshot marked current
              </div>
              <h3>{trustData.regulation.name}</h3>
              <dl>
                <div>
                  <dt>Starts</dt>
                  <dd>
                    <time dateTime={trustData.regulation.starts_at}>
                      {trustData.regulation.starts_label}
                    </time>
                  </dd>
                </div>
                <div>
                  <dt>Ends</dt>
                  <dd>
                    <time dateTime={trustData.regulation.ends_at}>
                      {trustData.regulation.ends_label}
                    </time>
                  </dd>
                </div>
                <div>
                  <dt>Source fetched</dt>
                  <dd>
                    <time dateTime={trustData.regulation.verified_at}>
                      {trustData.regulation.verified_label}
                    </time>
                  </dd>
                </div>
              </dl>
              <a
                className="source-link"
                href={trustData.regulation.source_url}
                {...externalLinkProps}
              >
                Open official regulation source
              </a>
              <p>{trustData.regulation.freshness_note}</p>
            </article>

            <div className="trust-ledger">
              <article className="ledger-row">
                <div>
                  <p className="ledger-label">Evaluation assets</p>
                  <h3>
                    {trustData.evaluation.fixture_count} fixed cases ·{" "}
                    {trustData.evaluation.rubric_count} scoring rubrics
                  </h3>
                </div>
                <p>{trustData.evaluation.scope_note}</p>
              </article>
              <article className="ledger-row">
                <div>
                  <p className="ledger-label">Minimum source stack</p>
                  <h3>{trustData.source_stack.required_sources.length} required roles configured</h3>
                </div>
                <ul className="source-stack-list">
                  {trustData.source_stack.required_sources.map((source) => (
                    <li key={source.id}>
                      <span>{source.role.replaceAll("_", " ")}</span>
                      <a href={source.url} {...externalLinkProps}>
                        {source.name}
                      </a>
                    </li>
                  ))}
                </ul>
                <p>{trustData.source_stack.scope_note}</p>
              </article>
              <article className="ledger-row ledger-calc-row">
                <div>
                  <p className="ledger-label">Exact-calculation boundary</p>
                  <h3>{trustData.calculation_boundary.exact.join(" · ")} exact</h3>
                </div>
                <p>
                  Speed stays assumption-framed unless a verified exact source
                  confirms it. {trustData.calculation_boundary.scope_note}
                </p>
              </article>
            </div>
          </div>
        </section>

        <section className="section runtimes-layout" id="runtimes">
          <div className="section-heading">
            <div className="eyebrow">Supported AI tools</div>
            <h2>One coaching engine, three ways to bring it into your workflow.</h2>
          </div>
          <div className="runtime-grid">
            {runtimes.map((runtime) => (
              <article className="runtime-card" key={runtime.name}>
                <div className="runtime-topline">
                  <h3>{runtime.name}</h3>
                  <a
                    href={runtime.href}
                    aria-label={`Open ${runtime.name} setup notes on GitHub`}
                    {...externalLinkProps}
                  >
                    Setup notes
                  </a>
                </div>
                <p className="runtime-summary">{runtime.summary}</p>
                <p>{runtime.notes}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section getting-started-layout" id="getting-started">
          <div className="section-heading compact">
            <div className="eyebrow">Getting started</div>
            <h2>Use it directly in the AI tool you already prefer.</h2>
          </div>
          <div className="timeline">
            <article className="timeline-card">
              <div className="timeline-marker">01</div>
              <div className="timeline-copy">
                <h3>Install as a plugin</h3>
                <p>Pick your AI tool and run the install. Restart after and the coaching tools are ready.</p>
                <div className="install-grid">
                  {runtimeInstalls.map((r) => (
                    <div key={r.name} className="install-card">
                      <p className="install-label">{r.name}</p>
                      <pre
                        aria-label={`${r.name} install command`}
                        tabIndex={0}
                      >
                        {r.code}
                      </pre>
                    </div>
                  ))}
                </div>
              </div>
            </article>
            {gettingStartedSteps.map((step, index) => (
              <article className="timeline-card" key={step.title}>
                <div className="timeline-marker">0{index + 2}</div>
                <div className="timeline-copy">
                  <h3>{step.title}</h3>
                  <p>{step.body}</p>
                  {step.code && step.isCode && <pre>{step.code}</pre>}
                  {step.code && !step.isCode && (
                    <p className="timeline-examples">{step.code}</p>
                  )}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="section support-layout">
          <div className="section-heading compact">
            <div className="eyebrow">Support tools</div>
            <h2>The verification layer behind the advice.</h2>
          </div>
          <div className="support-grid">
            {supportSkills.map((skill) => (
              <article className="support-card" key={skill.name}>
                <h3>{skill.displayName}</h3>
                <p className="skill-slug">{skill.name}</p>
                <p>{skill.summary}</p>
                <span>{skill.emphasis}</span>
              </article>
            ))}
          </div>
        </section>

        <section className="section systems-layout" id="how-it-works">
          <div className="section-heading">
            <div className="eyebrow">How it works</div>
            <h2>One coaching engine, consistent across every tool.</h2>
          </div>
          <div className="systems-grid">
            <div className="systems-column">
              {repoLayers.map((layer) => (
                <article className="system-card" key={layer.title}>
                  <h3>{layer.title}</h3>
                  <p>{layer.body}</p>
                </article>
              ))}
            </div>
            <aside className="systems-aside">
              <div className="info-card">
                <p className="card-label">Damage and survival checks</p>
                <p>
                  With complete inputs and the local browser helper available,
                  damage, KO, and survival can be verified exactly. Speed stays
                  assumption-framed unless a verified exact source confirms it.
                </p>
              </div>
              <div className="info-card">
                <p className="card-label">How quality is judged</p>
                <p>
                  Coaching that sounds better is not automatically better. Fixed
                  test cases and scoring rubrics exist so every change can be
                  checked against concrete failure modes, not just tone.
                </p>
              </div>
            </aside>
          </div>
        </section>

        <section className="section principles-layout">
          <div className="section-heading compact">
            <div className="eyebrow">Project principles</div>
            <h2>Guardrails that keep the coaching useful.</h2>
          </div>
          <div className="principles-grid">
            {principles.map((principle) => (
              <article className="principle-card" key={principle}>
                <p>{principle}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section cta-section">
          <div className="cta-card">
            <div>
              <div className="eyebrow">Open source</div>
              <h2>Clone the repo, use the coaching tools, and help make them better.</h2>
            </div>
            <div className="cta-actions">
              <a
                className="button button-primary"
                href="https://github.com/NoahJenkins/vgc-coach"
                aria-label="Open the VGC Coach GitHub repository"
                {...externalLinkProps}
              >
                Open on GitHub
              </a>
              <a
                className="button button-secondary"
                href="https://github.com/NoahJenkins/vgc-coach/blob/main/CONTRIBUTING.md"
                aria-label="Open the VGC Coach contribution guide on GitHub"
                {...externalLinkProps}
              >
                Contribution guide
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div>
          <p className="footer-title">VGC Coach</p>
          <p className="footer-copy">
            An open-source Pokemon Champions coaching workspace built around
            shared coaching tools, quality-checked against real VGC scenarios.
          </p>
          <p className="footer-legal">
            Pokemon and related names are trademarks and copyright of Nintendo,
            1996-{currentYear}.
          </p>
        </div>
        <nav className="footer-links" aria-label="Footer">
          {footerLinks.map((link) => (
            <a key={link.label} href={link.href} {...externalLinkProps}>
              {link.label}
            </a>
          ))}
        </nav>
      </footer>
      </div>
    </>
  );
}

export default App;
