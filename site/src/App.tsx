import { useState } from "react";
import {
  coreSkills,
  footerLinks,
  gettingStartedSteps,
  heroBullets,
  navLinks,
  principles,
  quickFacts,
  repoLayers,
  runtimeInstalls,
  runtimes,
  supportSkills,
} from "./siteContent";

function App() {
  const currentYear = new Date().getFullYear();
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const externalLinkProps = {
    target: "_blank",
    rel: "noreferrer",
  } as const;
  const closeMobileNav = () => {
    setIsMobileNavOpen(false);
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
              <div className="eyebrow">Pokemon Champions coaching workspace</div>
              <h1>Smarter AI coaching for Pokemon VGC.</h1>
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

            <aside className="hero-aside">
              <div className="battle-board" aria-label="VGC Coach operating loop">
                <div className="board-topline">
                  <span>shared coaching workflow</span>
                  <strong>current format first</strong>
                </div>
                <ol className="board-steps">
                  <li>
                    <span>01</span>
                    <strong>Verify the format</strong>
                    <p>Legality, regulation, and rules are checked before coaching advice is given.</p>
                  </li>
                  <li>
                    <span>02</span>
                    <strong>Ground the source</strong>
                    <p>Official rules, current sources, and community trend signals stay clearly separated.</p>
                  </li>
                  <li>
                    <span>03</span>
                    <strong>Give practical prep</strong>
                    <p>Team builds, lead plans, audits, and replay reviews resolve into usable next steps.</p>
                  </li>
                </ol>
                <div className="board-footer">
                  <span>shared skills</span>
                  <span>runtime adapters</span>
                  <span>eval rubrics</span>
                </div>
              </div>
              <div className="fact-strip">
                {quickFacts.map((fact) => (
                  <div className="fact-item" key={fact.label}>
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
            <h2>Not a ladder client. Not a content site. A coaching layer for your AI tool.</h2>
          </div>
          <div className="split-copy protocol-panel">
            <p>
              VGC Coach gives your AI assistant structured,
              quality-controlled coaching tools for real Pokemon Champions
              prep: current meta research, team-building, matchup planning,
              replay feedback, and practice tracking.
            </p>
            <ul className="protocol-list">
              <li>Shared coaching logic across every supported AI tool.</li>
              <li>Fixed test cases and rubrics for judging skill quality.</li>
              <li>Current format claims verified before they are presented as fact.</li>
            </ul>
          </div>
        </section>

        <section className="section" id="skills">
          <div className="section-heading compact">
            <div className="eyebrow">Core coaching tools</div>
            <h2>The five coaching tasks that matter most.</h2>
          </div>
          <div className="skill-playbook">
            {coreSkills.map((skill) => (
              <article className="skill-row" key={skill.name}>
                <div className="skill-row-title">
                  <p className="skill-slug">{skill.name}</p>
                  <h3>{skill.displayName}</h3>
                </div>
                <p>{skill.summary}</p>
                <strong>{skill.emphasis}</strong>
              </article>
            ))}
          </div>
        </section>

        <section className="section runtimes-layout" id="runtimes">
          <div className="section-heading">
            <div className="eyebrow">Supported AI tools</div>
            <h2>One coaching engine, three AI tools to run it.</h2>
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
          <div className="install-station">
            <article className="install-lead">
              <span>01</span>
              <div>
                <h3>Install as a plugin</h3>
                <p>Pick your AI tool and run the install. Restart after and the coaching tools are ready.</p>
              </div>
            </article>
            <div className="install-grid">
              {runtimeInstalls.map((r) => (
                <div key={r.name} className="install-card">
                  <p className="install-label">{r.name}</p>
                  <pre>{r.code}</pre>
                </div>
              ))}
            </div>
            {gettingStartedSteps.map((step, index) => (
              <article className="install-lead prompt-lead" key={step.title}>
                <span>0{index + 2}</span>
                <div>
                  <h3>{step.title}</h3>
                  <p>{step.body}</p>
                  {step.code && step.isCode && <pre>{step.code}</pre>}
                  {step.code && !step.isCode && (
                    <p className="prompt-examples">{step.code}</p>
                  )}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="section support-layout">
          <div className="section-heading compact">
            <div className="eyebrow">Support tools</div>
            <h2>Tools that keep the core coaching honest and accurate.</h2>
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
                  Damage, KO, and survival checks are exact. Speed comparisons
                  are framed as benchmarks, not invented numbers, unless a
                  verified exact source confirms them.
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
