import { useState } from "react";
import { Analytics } from "@vercel/analytics/react";
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
              <h1>
                Smarter AI coaching for Pokemon VGC.
              </h1>
              <p className="hero-intro">
                VGC Coach is an open-source coaching workspace that gives
                Codex, Claude Code, and OpenCode structured tools for
                team-building, meta research, lead planning, replay review, and
                consistent prep work — grounded in current format rules, not
                guesses.
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
                  Most AI-generated VGC advice sounds sharp while quietly getting
                  the legality, format rules, or in-game tradeoffs wrong. This
                  workspace hardens the coaching behavior against those failure
                  modes so the advice you get is actually trustworthy.
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
            <h2>Not a ladder client. Not a content site. A coaching layer for your AI tool.</h2>
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
              you can tell when a change actually made the coaching better —
              not just whether it sounds better.
            </p>
          </div>
        </section>

        <section className="section" id="skills">
          <div className="section-heading compact">
            <div className="eyebrow">Core coaching tools</div>
            <h2>The five coaching tasks that matter most.</h2>
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
                      <pre>{r.code}</pre>
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
                  are framed as benchmarks — not invented numbers — unless a
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
      <Analytics />
    </>
  );
}

export default App;
