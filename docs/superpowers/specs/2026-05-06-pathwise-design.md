# Pathwise — Design Spec & Claude Design Prompts

**Date:** 2026-05-06
**Project:** ADA Module 7 final assignment — Personalized AI Career Coach
**Status:** Approved brand & UX direction; ready for Claude Design generation.

This document captures the locked design direction and contains two paste-ready prompts at the bottom: one for the **UI** and one for the **logo**.

---

## 1. Brand Foundation

| | |
|---|---|
| **Name** | Pathwise |
| **One-liner** | A personalized AI career coach that turns your goal into a resume, an interview prep set, and a 6-month growth plan. |
| **Audience** | Career switchers (Marketing → Tech is the default persona, but the app supports five personas) |
| **Vibe** | Friendly · bright · optimistic — Notion / Headspace / Duolingo-lite, never childish |
| **Voice** | Warm mentor. Encouraging, concrete, never bossy. *"Nice — here's a draft of your bullets. Tweak anything that doesn't sound like you."* |

## 2. Visual Language

### Color
- **Primary:** Sage green (`#6F8F73` ballpark — bright, alive, not dusty)
- **Background:** Soft cream (`#F7F3EC` ballpark — warm off-white, not stark)
- **Text:** Deep ink (`#1F2A24` — green-tinted near-black)
- **Accent / CTA:** Warm amber (`#E0A24B` ballpark — used sparingly for primary buttons and progress)
- **Subtle / muted:** Sage at 12–20% opacity for chips, dividers, hover states
- Always cream-on-sage and sage-on-cream — avoid pure white and pure black

### Typography
- **Headings:** Manrope, weights 600 / 700, tight letter-spacing
- **Body:** Inter, weights 400 / 500, comfortable line-height (1.55)
- **UI labels:** Inter 500, slightly tracked-out

### Logo
- **Primary lockup:** path-and-wordmark — a stylised winding path / arrow glyph that gestures upward, paired with the "Pathwise" wordmark in Manrope 700
- **App icon:** rounded-square monogram — the same path glyph forming a "P" inside a soft-cornered tile, sage-on-cream
- **Forbidden:** clip-art compass, generic mountain, lightbulbs, gradients

### Imagery & motion
- Editorial photography of real people in transition moments (allowed but not required)
- Soft custom illustrations with sage line-work and cream fills
- Micro-animations: the path-glyph subtly redraws itself for loading states; cards lift 2–4px on hover
- No stock corporate photography; no glassmorphism

## 3. App Structure — Hybrid Wizard + Recap

A guided wizard for the three coaching steps, ending on a single beautiful **Coaching Recap** page.

| # | Screen | Purpose | Key elements |
|---|---|---|---|
| 1 | **Welcome / Profile** | Capture audience, target role, skills, career goal, tone | Hero with path-glyph, friendly headline, single-page form, "Start coaching" CTA |
| 2 | **Step 1 — Resume bullets** | Generate 5 ATS-aware bullets | Big card showing bullets as editable list, copy-each / copy-all, "Continue" CTA |
| 3 | **Step 2 — Mock interview** | Paste a job description, generate 5 questions + answer hints | Two-column: pasted JD on left, generated Q&A cards on right, expandable hints |
| 4 | **Step 3 — Growth roadmap** | 6-month plan: courses, networking, projects, monthly milestones | Roadmap visualised as a horizontal path with month markers (M1–M6) |
| 5 | **Coaching Recap** | Single page that surfaces every artefact for download/share | Sticky table-of-contents on left, all sections stacked, "Download as PDF" / "Start a new session" |

**Persistent shell:**
- Top-left: Pathwise logo, click → home
- Top-right: profile summary chip (target role + persona) + "New Session" reset
- Left or top progress indicator: 4-dot path showing where the user is (Welcome → 1 → 2 → 3 → Recap)
- Bottom-right: subtle "Coach is thinking…" indicator with the redrawing path-glyph during LLM calls

## 4. Key UX Moments
- **First impression:** Welcome screen feels like opening a journal, not a form. Headline: *"Let's map your next move."*
- **After step 1:** Coach line in warm-mentor voice appears above the bullets. *"Here's a draft. Tweak anything that doesn't sound like you."*
- **Empty interview state:** Friendly nudge to paste a job description, with a one-click "Use a sample JD" affordance.
- **Roadmap reveal:** The horizontal path animates in, milestone-by-milestone (≤ 1.2s total — never feels slow).
- **Recap page:** Feels like a personal portfolio of the session — copy-friendly, screenshot-friendly, one click to download.

## 5. Out of Scope (for first design pass)
- Authentication / multi-user accounts
- Saved sessions / history beyond the current run
- Stripe / billing / paywalls
- Mobile-native app (responsive web is enough)
- Dark mode (the cream palette is the identity; dark mode is a future iteration)

---

## 6. Paste-ready Prompt — UI in Claude Design

> Copy everything inside the fence into Claude Design as a single prompt.

```
Design a polished, friendly web app called "Pathwise" — a personalized AI career
coach that turns a user's goal into (1) a tailored resume, (2) interview practice
questions, and (3) a 6-month growth plan. The audience is career switchers
(Marketing → Tech is the default persona).

BRAND
- Name: Pathwise
- Vibe: friendly, bright, optimistic — feels like Notion crossed with Headspace, never childish
- Voice (microcopy): warm mentor — encouraging, concrete, never bossy.
  Sample line: "Nice — here's a draft of your bullets. Tweak anything that doesn't sound like you."

VISUAL LANGUAGE
- Color: sage green primary (#6F8F73), soft cream background (#F7F3EC),
  deep green-ink text (#1F2A24), one warm-amber accent (#E0A24B) for primary CTAs only.
  Always cream-on-sage / sage-on-cream — avoid pure white and pure black.
- Typography: Manrope (headings, weights 600/700, tight tracking) + Inter (body, 400/500, line-height 1.55)
- Imagery: soft custom line illustrations with sage strokes and cream fills.
  No stock corporate photos, no glassmorphism, no gradients.
- Motion: cards lift 2–4px on hover; loading state shows a small "path" glyph that
  redraws itself; roadmap reveals milestone-by-milestone in under 1.2 seconds total.

LAYOUT — HYBRID WIZARD + RECAP
A guided wizard with five screens. Persistent shell: top-left Pathwise logo,
top-right profile-summary chip + "New Session" reset, and a 4-step progress
indicator showing path position (Welcome → 1 → 2 → 3 → Recap).

Screens to design:

1. WELCOME / PROFILE
   Hero with the path glyph and headline "Let's map your next move."
   Single-page form: target role, current skills (chips), career goal (one
   sentence), persona dropdown (5 options: Junior Data Scientists, Career
   Switchers Marketing → Tech, High School Graduates, Return-to-Work Parents,
   Freelancers going full-time), tone selector (professional / friendly /
   direct / encouraging). Big amber "Start coaching" CTA.

2. STEP 1 — RESUME BULLETS
   Coach intro line at the top in warm-mentor voice.
   A large card showing 5 ATS-style resume bullets as an editable list with
   copy-each and copy-all controls. Cream card on sage-tinted background.
   Bottom-right: sage "Continue" CTA.

3. STEP 2 — MOCK INTERVIEW
   Two-column layout: left column is a JD paste area (with a "Use a sample JD"
   helper), right column is a stack of 5 generated question cards. Each card
   has the question, an "Answer hint" expand affordance, and a "Mark as
   practiced" toggle. Empty-state on the right shows the friendly nudge.

4. STEP 3 — GROWTH ROADMAP
   The roadmap renders as a horizontal sage-line path with six month markers
   M1–M6. Above the path: three cards — "Courses & certifications",
   "Networking actions", "Portfolio projects" (3 items each). Below each
   month marker: the milestone for that month. Animated reveal.

5. COACHING RECAP
   A single beautiful page that surfaces every artefact from the session.
   Sticky left sidebar with a section table-of-contents. Sections stack
   vertically: Profile summary → Resume bullets → Interview prep →
   Growth roadmap. Top-right buttons: "Download as PDF", "Start a new session".
   Feels like a personal portfolio of the session, screenshot-friendly.

OUT OF SCOPE
No login, no billing, no dark mode, no mobile-native app. Design for
desktop / responsive web only.

Deliver each screen as a clean static frame plus one short hover/active
state per screen. Use real, plausible filler content (not lorem ipsum) —
the persona is "Sara, marketing manager moving into product management at
a SaaS scale-up."
```

---

## 7. Paste-ready Prompt — Logo in Claude Design

> Copy everything inside the fence into Claude Design as a separate prompt.

```
Design a logo system for "Pathwise" — a friendly, optimistic AI career
coach app for career switchers.

DELIVER TWO ASSETS

1. PRIMARY LOCKUP (horizontal)
   A custom path/arrow glyph paired with the wordmark "Pathwise".
   - Glyph: a stylised winding path that gently curves upward and to the right;
     the upper end of the path forms a subtle arrowhead. The shape suggests
     forward motion, growth, and guidance — never a literal compass, never a
     mountain, never a lightbulb.
   - Wordmark: "Pathwise" set in Manrope 700 with slightly tightened tracking,
     in deep green-ink (#1F2A24). Glyph sits to the left of the wordmark with
     comfortable optical spacing.
   - Glyph color: sage green (#6F8F73). On dark surfaces, the glyph flips to
     soft cream (#F7F3EC).

2. APP ICON / MONOGRAM
   A rounded-square tile (iOS-radius corners, ~22% radius) containing the
   same path glyph reinterpreted to read as a stylised letter "P".
   - Tile background: soft cream (#F7F3EC)
   - Glyph fill: sage green (#6F8F73)
   - The "P" loop is the curl of the path; the descender is the path's tail.
     The shape should still read as a path even if the viewer doesn't notice
     the letter.

CONSTRAINTS
- No gradients, no drop shadows, no glassmorphism, no 3D.
- Single-weight strokes preferred; if filled, keep shapes simple and bold.
- Must work at 16px favicon size and at large display size.
- Pair samples should sit on a soft-cream background unless flipped for a
  dark surface.

DELIVER
- Primary lockup on cream
- Primary lockup on sage (cream glyph + cream wordmark)
- App icon at 1024×1024
- Favicon at 32×32 and 16×16
- A small "logo grammar" sheet showing min-clear-space and the smallest
  acceptable size.
```

---

## 8. Self-review notes

- Placeholders / TODOs: none — all colors/fonts/screens are concrete.
- Internal consistency: prompts both reference the same hex colors, fonts, and glyph definition. ✓
- Scope: focused on visual + UX direction; backend chains live in `chains.py` already. ✓
- Ambiguity: persona for filler content is named ("Sara, marketing manager → PM") so Claude Design has a concrete subject. ✓
