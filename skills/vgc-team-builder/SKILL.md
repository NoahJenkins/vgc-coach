---
name: vgc-team-builder
description: Build VGC teams around target mons, archetypes, or anti-meta goals.
---

# VGC Team Builder

## Purpose

Use this skill to build a coherent team draft around:

- specific mons
- a style or archetype
- a known meta weakness to target

## Inputs

- target mons
- target strategy
- playstyle
- anti-meta goals
- avoid list

## Output Contract

Always return:

1. team identity
2. six-mon draft
3. role map
4. why each slot exists
5. likely weaknesses
6. next refinement targets

## Rules

- do not force the requested mon if it clearly makes the team worse without saying so
- explain why the requested mon belongs on the team
- avoid generic six-mon piles with no structure

