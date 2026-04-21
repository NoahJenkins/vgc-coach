import {
  coreSkills,
  footerLinks,
  gettingStartedSteps,
  heroBullets,
  navLinks,
  principles,
  quickFacts,
  repoLayers,
  runtimes,
  supportSkills,
} from "./siteContent";

function App() {
  return (
    <div className="page-shell">
      <div className="background-texture" aria-hidden="true" />
      <header className="site-header">
        <a className="brand" href="#top">
          <span className="brand-mark">VGC</span>
          <span className="brand-copy">
            <strong>Coach</strong>
            <span>Open-source skill workspace</span>
          </span>
        </a>
        <nav className="site-nav" aria-label="Primary">
          {navLinks.map((link) => (
            <a key={link.href} href={link.href}>
              {link.label}
            </a>
          ))}
        </nav>
        <a
          className="button button-ghost"
          href="https://github.com/NoahJenkins/vgc-coach"
        >
          View Repo
        </a>
      </header>

      <main id="top">
        <section className="hero section">
          <div className="hero-copy">
            <div className="eyebrow">Pokemon Champions coaching workspace</div>
            <h1>
              A cleaner way to turn coding agents into serious VGC prep tools.
            </h1>
            <p className="hero-intro">
              VGC Coach is an open-source skill-and-eval workspace for
              team-building, meta research, lead planning, replay review, and
              disciplined coaching iteration across Codex, Claude Code, and
              OpenCode.
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

          <aside className="hero-aside">
            <div className="info-card spotlight-card">
              <p className="card-label">Why it exists</p>
              <p className="spotlight-copy">
                Most agent-generated VGC advice fails because it sounds sharp
                while drifting on legality, format truth, or practical in-game
                tradeoffs. This repo hardens shared coaching behavior against
                those failure modes.
              </p>
            </div>
            <div className="fact-grid">
              {quickFacts.map((fact) => (
                <div className="fact-card" key={fact.label}>
                  <strong>{fact.value}</strong>
                  <span>{fact.label}</span>
                </div>
              ))}
            </div>
          </aside>
        </section>

        <section className="section split-section" id="what-it-does">
          <div className="section-heading">
            <div className="eyebrow">What it does</div>
            <h2>Not a ladder client. Not a content site. A reusable coaching layer.</h2>
          </div>
          <div className="split-copy">
            <p>
              VGC Coach is built for people who want coding agents to produce
              stronger Pokemon Champions prep: current-format research,
              practical team-building help, matchup plans, replay feedback, and
              repeatable evaluation.
            </p>
            <p>
              The canonical behavior lives in shared skill packages under
              <code>skills/</code>. Runtime wrappers stay thin. Fixtures and
              rubrics exist so changes can be judged against actual quality
              rather than tone alone.
            </p>
          </div>
        </section>

        <section className="section" id="skills">
          <div className="section-heading compact">
            <div className="eyebrow">Core MVP skills</div>
            <h2>The first five surfaces that matter most.</h2>
          </div>
          <div className="skill-grid">
            {coreSkills.map((skill) => (
              <article className="skill-card skill-card-core" key={skill.name}>
                <p className="card-kicker">Core focus</p>
                <h3>{skill.name}</h3>
                <p>{skill.summary}</p>
                <span>{skill.emphasis}</span>
              </article>
            ))}
          </div>
        </section>

        <section className="section runtimes-layout" id="runtimes">
          <div className="section-heading">
            <div className="eyebrow">Supported runtimes</div>
            <h2>One shared skill tree, three ways to use it.</h2>
          </div>
          <div className="runtime-grid">
            {runtimes.map((runtime) => (
              <article className="runtime-card" key={runtime.name}>
                <div className="runtime-topline">
                  <h3>{runtime.name}</h3>
                  <a href={runtime.href}>Runtime notes</a>
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
            <h2>Use the repo directly in the runtime you already prefer.</h2>
          </div>
          <div className="timeline">
            {gettingStartedSteps.map((step, index) => (
              <article className="timeline-card" key={step.title}>
                <div className="timeline-marker">0{index + 1}</div>
                <div className="timeline-copy">
                  <h3>{step.title}</h3>
                  <p>{step.body}</p>
                  <pre>{step.code}</pre>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="section support-layout">
          <div className="section-heading compact">
            <div className="eyebrow">Support skills</div>
            <h2>Helpers that make the core coaching surfaces more reliable.</h2>
          </div>
          <div className="support-grid">
            {supportSkills.map((skill) => (
              <article className="support-card" key={skill.name}>
                <h3>{skill.name}</h3>
                <p>{skill.summary}</p>
                <span>{skill.emphasis}</span>
              </article>
            ))}
          </div>
        </section>

        <section className="section systems-layout" id="how-it-works">
          <div className="section-heading">
            <div className="eyebrow">How it works</div>
            <h2>Shared packages, thin adapters, explicit validation.</h2>
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
                <p className="card-label">Current exact-calc boundary</p>
                <p>
                  <code>vgc-calcs-assistant</code> currently supports exact
                  damage, KO, and survival checks through the local browser
                  helper path. Speed guidance remains assumption-framed unless a
                  verified exact backend exists.
                </p>
              </div>
              <div className="info-card">
                <p className="card-label">Evaluation posture</p>
                <p>
                  A skill is not considered better just because it reads better.
                  This repo keeps fixed evals and rubrics so output quality can
                  be checked against concrete failure modes.
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
              <h2>Use the workspace, inspect the skill contracts, and improve the layer.</h2>
            </div>
            <div className="cta-actions">
              <a
                className="button button-primary"
                href="https://github.com/NoahJenkins/vgc-coach"
              >
                Open on GitHub
              </a>
              <a
                className="button button-secondary"
                href="https://github.com/NoahJenkins/vgc-coach/blob/main/CONTRIBUTING.md"
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
            shared skills, runtime adapters, and evaluation-backed quality.
          </p>
        </div>
        <div className="footer-links">
          {footerLinks.map((link) => (
            <a key={link.label} href={link.href}>
              {link.label}
            </a>
          ))}
        </div>
      </footer>
    </div>
  );
}

export default App;
