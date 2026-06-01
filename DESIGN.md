---
name: VGC Coach
description: Tactical Pokemon Champions coaching workspace for source-aware AI prep.
colors:
  bg: "oklch(97% 0.016 72)"
  bg-strong: "oklch(94% 0.032 60)"
  surface: "color-mix(in oklch, white 78%, oklch(92% 0.04 48))"
  surface-strong: "oklch(92% 0.05 52)"
  ink: "oklch(26% 0.025 38)"
  ink-soft: "oklch(38% 0.02 42)"
  line: "oklch(79% 0.04 55 / 0.7)"
  accent: "oklch(58% 0.135 38)"
  accent-soft: "oklch(79% 0.08 45)"
  accent-2: "oklch(60% 0.09 115)"
  dark-bg: "oklch(16% 0.008 38)"
  dark-surface: "color-mix(in oklch, oklch(23% 0.012 38) 90%, oklch(30% 0.02 48))"
  dark-ink: "oklch(94% 0.012 70)"
  dark-ink-soft: "oklch(78% 0.018 68)"
  dark-line: "oklch(44% 0.02 48 / 0.64)"
  dark-accent: "oklch(69% 0.13 32)"
  dark-accent-2: "oklch(76% 0.1 78)"
typography:
  display:
    fontFamily: "Sora, Manrope, sans-serif"
    fontSize: "clamp(3.25rem, 7vw, 7rem)"
    fontWeight: 800
    lineHeight: 0.92
    letterSpacing: "-0.065em"
  headline:
    fontFamily: "Sora, Manrope, sans-serif"
    fontSize: "clamp(2rem, 4.2vw, 4.4rem)"
    fontWeight: 800
    lineHeight: 0.92
    letterSpacing: "-0.065em"
  title:
    fontFamily: "Manrope, sans-serif"
    fontSize: "1.1rem"
    fontWeight: 800
    lineHeight: 1.25
  body:
    fontFamily: "Manrope, sans-serif"
    fontSize: "clamp(1rem, 1.25vw, 1.1rem)"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "Manrope, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 800
    lineHeight: 1
  mono:
    fontFamily: "SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace"
    fontSize: "0.78rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  pill: "999px"
  sm: "0.5rem"
  md: "1rem"
  lg: "1.6rem"
spacing:
  xs: "0.45rem"
  sm: "0.8rem"
  md: "1rem"
  lg: "1.6rem"
  xl: "clamp(2.6rem, 7vw, 6rem)"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.bg}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0.85rem 1.25rem"
    height: "3.2rem"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0.85rem 1.25rem"
    height: "3.2rem"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "1.25rem"
  navigation-link:
    backgroundColor: "transparent"
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.pill}"
    padding: "0.45rem 0.8rem"
    height: "2.75rem"
---

# Design System: VGC Coach

## 1. Overview

**Creative North Star: "The Match Prep Desk"**

VGC Coach should feel like a disciplined prep surface for competitive Pokemon Champions players: warm enough to be approachable, precise enough to trust before a set, and structured enough to show that advice is being checked against rules, sources, and evals. The current system is a brand surface, not an app dashboard. It sells confidence through useful specificity, not hype.

The visual language is tactical light mode with dark mode as a first-class companion. Large Sora headings create the competitive snap, Manrope carries the explanatory copy, and rounded cards group coaching tasks without turning the page into a generic SaaS grid. The grid texture, soft shadows, code blocks, and mono slugs signal tools and runtime adapters while preserving a player-first reading order.

This system rejects generic AI-product marketing, stale-meta certainty, and contributor-first architecture dumps. The homepage must keep player tasks visible: building teams, checking the current meta, planning leads, reviewing games, and understanding whether AI-generated advice is trustworthy.

**Key Characteristics:**

- Warm tactical neutrals with coral and olive accents.
- Large, compressed display type balanced by practical explanatory copy.
- Compact tool cards that make coaching tasks easy to scan.
- Source accuracy, legality, uncertainty, and eval quality made visible.
- Light and dark themes treated as equal product surfaces.

## 2. Colors

The palette is a warm tactical board: paper-like neutrals, grounded ink, coral action, and olive verification markers.

### Primary

- **Rules Coral** (`accent`): Primary actions, brand mark fills, active dots, and key emphasis. It should feel decisive and competitive, not decorative.
- **Soft Coral Wash** (`accent-soft`): Hover fills, selection backgrounds, and warm supporting surfaces.

### Secondary

- **Verification Olive** (`accent-2`): Secondary indicators, quality markers, and supporting proof points. Use it when a detail reinforces accuracy or confidence.

### Neutral

- **Prep Paper** (`bg`): The default light canvas. It should stay warm and lightly tinted, never pure white.
- **Tactical Surface** (`surface`): Cards, panels, and grouped content blocks.
- **Grounded Ink** (`ink`): Main readable text.
- **Rules Ink Soft** (`ink-soft`): Secondary prose, helper copy, and quieter navigation.
- **Format Line** (`line`): Borders, dividers, and low-pressure separation.
- **Night Prep Canvas** (`dark-bg`): The dark-mode background for late prep contexts.
- **Night Tactical Surface** (`dark-surface`): Dark-mode panels and cards.
- **Night Ink** (`dark-ink`): Main dark-mode text.
- **Night Ink Soft** (`dark-ink-soft`): Secondary dark-mode text.

### Named Rules

**The No Pure Neutral Rule.** Never use pure black or pure white. Every neutral is slightly warmed or cooled through OKLCH.

**The Accuracy Accent Rule.** Use olive for verification and support, not as a second competing CTA color.

**The Theme Parity Rule.** Any new section must preserve both light and dark color assignments. Do not patch only the default theme.

## 3. Typography

**Display Font:** Sora with Manrope fallback.  
**Body Font:** Manrope with sans-serif fallback.  
**Label/Mono Font:** SF Mono stack for slugs, code, and install commands.

**Character:** Sora brings blunt competitive hierarchy, while Manrope keeps the prose readable and practical. Mono is reserved for real tool names, commands, and skill slugs.

### Hierarchy

- **Display** (800, `clamp(3.25rem, 7vw, 7rem)`, 0.92): Hero headline only. Use this scale when the page needs immediate player-facing positioning.
- **Headline** (800, `clamp(2rem, 4.2vw, 4.4rem)`, 0.92): Section headings and CTA headings. Keep max-width tight enough to create strong line breaks.
- **Title** (800, `1.1rem`, 1.25): Card headings, runtime names, and timeline step titles.
- **Body** (400, `clamp(1rem, 1.25vw, 1.1rem)`, 1.7): Explanatory copy. Cap long prose around 58ch to 65ch.
- **Label** (800, `0.95rem`, normal or short uppercase): Eyebrows, card labels, install labels, and compact metadata.
- **Mono** (400, `0.78rem`, 1.5): Skill slugs, code blocks, and command snippets only.

### Named Rules

**The Practical Voice Rule.** Keep copy plain and repo-aligned. Use phrases like "open-source coaching workspace", "shared coaching logic", "current format rules", "fixed test cases and rubrics", and "support tools".

**The Mono Has A Job Rule.** Mono is for identifiers and commands. Do not use monospace as a lazy shorthand for technical style.

## 4. Elevation

Depth is a hybrid of tonal layering and soft ambient shadows. Cards and sticky navigation use rounded surfaces with low-contrast borders, while primary CTAs get a warmer glow. Shadows should feel like paper and tools on a desk, not glossy glass panels.

### Shadow Vocabulary

- **Ambient Panel** (`box-shadow: 0 28px 70px oklch(40% 0.03 35 / 0.13)`): Main card, runtime card, timeline card, and CTA depth in light mode.
- **Soft Header** (`box-shadow: 0 4px 16px oklch(40% 0.03 35 / 0.07)`): Sticky header and smaller supporting list items.
- **Primary Glow** (`box-shadow: 0 18px 45px oklch(58% 0.11 32 / 0.28)`): Primary CTA only.
- **Night Ambient Panel** (`box-shadow: 0 28px 70px oklch(5% 0.018 38 / 0.45)`): Dark-mode card depth.

### Named Rules

**The No Glass Rule.** Do not use blur-heavy glassmorphism as decoration. Use solid tonal surfaces and honest borders.

**The CTA Glow Rule.** Glow belongs to primary action and state feedback. Do not put CTA-level shadow on every card.

## 5. Components

### Buttons

- **Shape:** Fully rounded pill buttons (`999px`) with at least `3.2rem` height.
- **Primary:** Coral gradient over the primary accent with warm light text. Use for the main action per section only.
- **Hover / Focus:** Translate up by `1px`, increase shadow, and use a `2px` focus outline in the focus-ring color.
- **Secondary / Ghost:** Soft surface fill, line border, and warm hover tint. Use for supporting links and low-pressure navigation.

### Chips

- **Style:** The site does not currently use filter chips. If added, derive them from navigation links: pill radius, soft surface fill, `line` border, and label typography.
- **State:** Selected chips may use Soft Coral Wash. Do not create a new saturated chip palette.

### Cards / Containers

- **Corner Style:** Large tactical cards use `1.6rem`; nested list items and examples step down to `1rem` or `calc(var(--radius) - 0.55rem)`.
- **Background:** Use `surface`, spotlight gradients, or principle/CTA tonal fills depending on information priority.
- **Shadow Strategy:** Default cards use Ambient Panel. Small list items use Soft Header. Repeated cards should not all fight for depth.
- **Border:** Always pair card surfaces with `1px solid line` for readable separation in both themes.
- **Internal Padding:** Use `1.25rem` for standard cards and clamp up to `2.2rem` for CTA blocks.

### Inputs / Fields

- **Style:** No input system exists yet. Future fields should follow the button and card vocabulary: pill or 1rem radius, tonal surface, `line` border, Manrope body text.
- **Focus:** Use the existing `2px` focus ring and `3px` offset.
- **Error / Disabled:** Error and disabled states are not currently defined. Add explicit semantic tokens before shipping form-heavy surfaces.

### Navigation

- **Desktop:** Sticky header with brand mark, centered pill links, theme toggle, and repo CTA. Links use soft text by default and warm background on hover or focus.
- **Mobile:** Menu collapses into a bordered rounded panel with one-column pill links, stronger backgrounds, and the repo link moved into the menu.
- **Theme Toggle:** Pill control with a small circular indicator. Dark mode shifts the indicator and changes its accent to olive.

### Signature Component

**Install Timeline.** Timeline rows pair a circular numeric marker with copy and command blocks. This component is the bridge between player-facing explanation and tool setup. Keep command text readable, wrap safely on mobile, and keep the marker compact.

## 6. Do's and Don'ts

### Do:

- **Do** prioritize VGC player tasks over contributor architecture on public pages.
- **Do** make source accuracy, legality, and uncertainty visible without turning the page into documentation.
- **Do** preserve the established product voice: open-source coaching workspace, shared coaching logic, current format rules, fixed test cases and rubrics, support tools.
- **Do** support light and dark themes as first-class modes with accessible contrast.
- **Do** use bold visual hierarchy for scanning while keeping install paths and coaching tools easy to compare.
- **Do** use OKLCH tokens and tinted neutrals instead of raw hex neutrals.
- **Do** keep reduced-motion behavior intact for every animation or transition.

### Don't:

- **Don't** drift into generic AI-product hype or vague productivity language.
- **Don't** present stale meta claims, fake legality, usage, or matchup certainty as current truth.
- **Don't** fork shared coaching logic or make runtime-specific visual stories look like separate products.
- **Don't** use gradient text, decorative glassmorphism, side-stripe borders, or hero-metric templates.
- **Don't** use identical icon-heading-text card grids as the main design idea.
- **Don't** over-stylize copy at the expense of practical, repo-aligned language.
- **Don't** create dark-mode-only effects or light-mode-only surfaces.
