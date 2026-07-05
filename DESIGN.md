---
name: Job Application Tracker
description: A warm, calm personal tool for tracking job applications
colors:
  parchment-white: "oklch(98% 0.004 75)"
  warm-linen: "oklch(95.5% 0.007 75)"
  ink-charcoal: "oklch(28% 0.012 75)"
  warm-graphite: "oklch(46% 0.012 75)"
  soft-taupe: "oklch(52% 0.010 75)"
  hairline-mist: "oklch(90% 0.006 75)"
  border-fog: "oklch(78% 0.010 75)"
  border-stone: "oklch(68% 0.012 75)"
  teal-signal: "oklch(58% 0.10 195)"
  teal-signal-hover: "oklch(52% 0.11 195)"
  teal-signal-active: "oklch(46% 0.11 195)"
  accent-contrast-ink: "oklch(99% 0.005 195)"
  status-applied: "oklch(42% 0.045 235)"
  status-interviewing: "oklch(46% 0.11 85)"
  status-offer: "oklch(42% 0.11 150)"
  status-rejected: "oklch(45% 0.12 25)"
  status-withdrawn: "oklch(46% 0.010 75)"
  umber-night: "oklch(23% 0.014 70)"
  umber-panel: "oklch(29% 0.020 62)"
  warm-ivory: "oklch(93% 0.010 70)"
  dusty-gold: "oklch(78% 0.014 70)"
  faded-bronze: "oklch(67% 0.012 70)"
  border-ember-low: "oklch(37% 0.018 66)"
  border-ember: "oklch(47% 0.020 66)"
  border-ember-high: "oklch(57% 0.022 66)"
  teal-signal-dark: "oklch(74% 0.09 195)"
  ember-coral: "oklch(76% 0.13 45)"
  accent-contrast-abyss: "oklch(14% 0.01 195)"
  status-applied-dark: "oklch(81% 0.09 235)"
  status-interviewing-dark: "oklch(83% 0.15 85)"
  status-offer-dark: "oklch(81% 0.17 150)"
  status-rejected-dark: "oklch(81% 0.15 25)"
  status-withdrawn-dark: "oklch(73% 0.010 70)"
typography:
  display:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1.266rem"
    fontWeight: 700
  title:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
  label:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.889rem"
    fontWeight: 600
rounded:
  control: "6px"
  panel: "10px"
spacing:
  "1": "4px"
  "2": "8px"
  "3": "12px"
  "4": "16px"
  "5": "24px"
  "6": "32px"
  "7": "48px"
components:
  button-primary:
    backgroundColor: "{colors.teal-signal}"
    textColor: "{colors.accent-contrast-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "8px 16px"
  button-primary-hover:
    backgroundColor: "{colors.teal-signal-hover}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink-charcoal}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "8px 16px"
  input-text:
    backgroundColor: "{colors.parchment-white}"
    textColor: "{colors.ink-charcoal}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  nav-link:
    textColor: "{colors.warm-graphite}"
    typography: "{typography.label}"
  nav-link-active:
    textColor: "{colors.teal-signal}"
    typography: "{typography.label}"
---

# Design System: Job Application Tracker

## 1. Overview

**Creative North Star: "The Warm Ledger"**

This is a well-worn accounting ledger, not a SaaS dashboard: a single person's private record of applications, kept in warm paper tones rather than clinical engineering-tool gray. The system explicitly rejects flat, monochromatic admin-panel dark mode (a single desaturated gray scale with one timid accent) and anything that reads as lifeless or generic, per this project's PRODUCT.md anti-references.

Both light and dark themes are tinted toward the same warm neutral hue family (never a pure gray, never pure black or white), so switching themes never feels like switching products, only like switching the ambient light in the room the ledger sits in. One teal accent (`teal-signal`) carries every primary action and the current navigation selection across both themes; a warm coral heading accent (`ember-coral`) and richer, more saturated status colors give dark mode extra life without turning the system into a rainbow.

**Key Characteristics:**
- Warm-tinted neutrals in every surface, text, and border color, never a flat desaturated gray.
- One consistent teal accent for actions and current selection, in both themes.
- Five named status colors (Applied, Interviewing, Offer, Rejected, Withdrawn) that carry meaning through color and text together, never color alone.
- Flat by default: no shadows, no elevation layering; depth comes from background tone shifts (panel vs. page) only.
- Dark mode is warmer and more saturated than a naive "invert the lightness" dark mode would produce.

## 2. Colors

A tinted-neutral base carries almost all surface area; one teal accent is reserved for action and selection; five semantic status colors and one warm heading accent complete the palette.

### Primary
- **Teal Signal** (`teal-signal`, oklch(58% 0.10 195) light / `teal-signal-dark`, oklch(74% 0.09 195) dark): The one accent color. Used for links, primary button fills, focus rings, and the active navigation link. Nowhere else. Its rarity is what makes it legible as "this is actionable" at a glance.
- **Teal Signal Hover / Active** (`teal-signal-hover` oklch(52% 0.11 195), `teal-signal-active` oklch(46% 0.11 195)): Pressed-state variants of the primary accent, light mode. Darker as pressure increases; dark mode lightens instead (`accent-hover` 80% L, `accent-active` 68% L) since darkening further on a dark surface would kill contrast.

### Secondary
- **Ember Coral** (`ember-coral`, oklch(76% 0.13 45), dark mode only): A warm coral-orange reserved for section headings (`h2`). In light mode, headings use the neutral `warm-graphite` secondary text color instead; this asymmetry is intentional; see the Warmth Asymmetry Rule below.

### Neutral (Light)
- **Parchment White** (`parchment-white`, oklch(98% 0.004 75)): Page background.
- **Warm Linen** (`warm-linen`, oklch(95.5% 0.007 75)): Panel background (header, table headers, hover rows, expanded row detail).
- **Ink Charcoal** (`ink-charcoal`, oklch(28% 0.012 75)): Primary text.
- **Warm Graphite** (`warm-graphite`, oklch(46% 0.012 75)): Secondary text, labels, inactive nav links, table header text.
- **Soft Taupe** (`soft-taupe`, oklch(52% 0.010 75)): Muted text (placeholders).
- **Hairline Mist / Border Fog / Border Stone** (oklch(90/78/68% 0.006-0.012 75)): Three border weights, subtle to strong.

### Neutral (Dark)
- **Umber Night** (`umber-night`, oklch(23% 0.014 70)): Page background.
- **Umber Panel** (`umber-panel`, oklch(29% 0.020 62)): Panel background, noticeably richer and warmer than the page behind it, not just lighter.
- **Warm Ivory / Dusty Gold / Faded Bronze**: Primary / secondary / muted text, mirroring the light triad at inverted lightness with slightly more chroma for warmth.
- **Border Ember Low / Ember / Ember High**: Three border weights, dark mode.

### Semantic Status
- **Applied** (`status-applied`, blue, hue 235), **Interviewing** (`status-interviewing`, amber, hue 85), **Offer** (`status-offer`, green, hue 150), **Rejected** (`status-rejected`, red, hue 25), **Withdrawn** (`status-withdrawn`, neutral hue 75): Each status gets a text/background/border triad at the same hue. Withdrawn is deliberately desaturated (near-neutral) since it represents an inactive, closed-out state; the other four are actively saturated so they read as "this needs attention or is moving."
- In dark mode, every status color's chroma increases by roughly 40-70% over its light-mode value at the equivalent role (see `*-dark` color entries) so status pills stay vivid against the darker page instead of going muddy. This is a deliberate enrichment, not an automatic dark-mode transform; do not derive dark status colors by mechanically inverting lightness alone.

### Named Rules
**The Text-Plus-Color Rule.** Status is never conveyed by color alone. The status control is a `<select>` showing the status name as text; color reinforces it, it does not replace it.

**The Warmth Asymmetry Rule.** Dark mode is allowed to be more colorful than light mode (the `ember-coral` heading accent and richer status chroma exist only in dark mode). This is intentional: a dark surface can carry more saturated color before it looks garish, and dark mode is where "too flat" was the original complaint this palette was built to fix. Do not force light mode to adopt the same heading accent; it would look overwrought on a near-white background.

## 3. Typography

**Body Font:** -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif (the OS-native UI font stack, no custom font loaded)

**Character:** Unstyled and native-feeling on purpose. This is a personal tool used by one person on their own machine; a custom webfont would add load time and a layer of "designed-ness" the Warm Ledger metaphor doesn't call for.

### Hierarchy
- **Display** (700, 1.266rem): The "Job Application Tracker" header title. Appears once, at the top of every page.
- **Title** (600, 1.125rem, colored via `{colors.warm-graphite}` in light / `{colors.ember-coral}` in dark): Section headings ("Log a new application", "Applications", "Export / Import").
- **Body** (400, 1rem): All form inputs, table cell content, paragraph text.
- **Label** (600, 0.889rem): Navigation links, table column headers, the status `<select>` text, button labels.

### Named Rules
**The One Weight-Step Rule.** Only two font weights exist in the whole system: 400 (body) and 600-700 (everything else that needs emphasis). Do not introduce a 500 or 800 weight; the two-weight system is what keeps a single native font stack feeling deliberate rather than accidental.

## 4. Elevation

Flat by default, no exceptions. There is not a single `box-shadow` in the stylesheet. Depth is conveyed entirely through background tone: page background vs. panel background (header, table header, hovered table row, expanded row detail all use the panel tone) vs. focus rings (a 3px `accent-focus-ring` glow, the only shadow-adjacent effect in the system, reserved for keyboard focus).

### Named Rules
**The Flat-By-Default Rule.** No card ever gets a drop shadow to indicate it is "raised." If something needs to stand apart from the page, give it the panel background color, not a shadow. This keeps the Warm Ledger metaphor intact: paper sitting on paper, not glass floating over paper.

## 5. Components

### Buttons
- **Shape:** 6px corner radius (`{rounded.control}`), consistent across primary and secondary buttons.
- **Primary:** Filled with `teal-signal` / `accent-contrast-ink` text, `8px 16px` padding. This is the only filled-background interactive element in the system; reserve it for the single most important action on a page ("Continue", "Save application").
- **Hover / Active:** Background steps to `teal-signal-hover` then `teal-signal-active` (darker in light mode, lighter in dark mode). Transition is 150ms ease-out on background/border/color, never on layout properties.
- **Secondary / Ghost:** Transparent background, `border-fog` / `border-ember` outline, text in the primary text color. Used for every non-primary action (Save on a row, Import, theme toggle).
- **Friendlier hover going forward:** the component philosophy for this system is tactile and friendly, not clinical. When adding new interactive elements, prefer a warm background-tint shift on hover (a wash of the relevant accent color, 4-8% opacity) over a purely cosmetic border-color change; this reads as more inviting without adding a shadow or breaking the Flat-By-Default Rule.

### Inputs / Fields
- **Style:** 1px `border-default` stroke, `bg-page` background (not panel), 6px radius, `8px 12px` padding, capped at 420px max-width so a field never stretches the full container width on a wide screen.
- **Focus:** Border shifts to the accent color plus a 3px soft accent-colored glow (`box-shadow: 0 0 0 3px var(--accent-focus-ring)`). This is the only shadow in the system and only appears on focus.
- **Number inputs:** Native spinner arrows are removed (`-webkit-appearance: none` / `-moz-appearance: textfield`) everywhere a number input appears; a plain integer field, no counter widget.
- **Date inputs:** Native date picker, no custom calendar widget; defaults to today's date so the browser's own "today" highlight does the work.

### Navigation
- **Style:** Plain text links, `label` typography, `warm-graphite` / `dusty-gold` by default.
- **Hover:** Shifts to the primary text color (no underline, no background change).
- **Active (current page):** Shifts to `teal-signal`, the accent color. This is the accent's second reserved use case (alongside primary actions), per the Text-Plus-Color-adjacent principle that accent color always means "this is the thing that matters right now."

### Status Pills (the `<select>` dropdown)
- **Shape:** Same 6px radius as buttons/inputs, custom SVG chevron replacing the native arrow (`appearance: none` plus a background-image chevron, since Safari ignores `background-color`/`border-color` on unstyled `<select>` elements).
- **Color:** Background, text, and border all shift together per the `data-status` attribute, using the semantic status triad for that status. This is the single most colorful element on the page by design, since status is the one piece of information a user scans the table for repeatedly.

### Table
- **Header:** Panel background, `label` typography, bottom border in `border-strong`.
- **Rows:** Hover shifts the row to the panel background (a full-row tint, not a stripe). Expandable rows (`.app-row` / `.app-detail`) use a native `hidden` attribute toggle; the expanded detail row also gets the panel background so it visually reads as "opened out of" its summary row above it.
- **Collapsed vs. expanded:** Only Company / Role / Date Applied / Status show by default; Job Posting link, Total Rounds, Current Round, and Feedback live in the collapsible detail row, keeping the default view scannable.

## 6. Do's and Don'ts

### Do:
- **Do** tint every neutral toward the warm hue family already established (light: hue ~75, dark: hue ~62-70). Never introduce a pure, untinted gray.
- **Do** keep the teal accent to its two reserved jobs: primary actions and current-selection indicators (active nav link). Nothing else may use it.
- **Do** let dark mode be more saturated than light mode when it serves legibility or life (the Warmth Asymmetry Rule) — richer status chroma and the `ember-coral` heading accent are deliberate, not accidental drift.
- **Do** convey status through text plus color together, never color alone.
- **Do** prefer a background-tint hover treatment for new interactive elements, in keeping with the tactile-and-friendly component philosophy.
- **Do** keep number inputs free of native spinner arrows, matching the existing pattern.

### Don't:
- **Don't** build a flat, monochromatic "SaaS admin panel gray" dark mode: a single desaturated gray scale plus one timid accent. This is this system's core anti-reference (per PRODUCT.md) and the entire reason the dark-mode palette was enriched.
- **Don't** use `border-left` or `border-right` greater than 1px as a colored accent stripe on any row, card, or callout. Use a full background tint, a full hairline border, or nothing.
- **Don't** add a drop shadow to indicate elevation. This system has none; use the panel background color instead (the Flat-By-Default Rule).
- **Don't** introduce a new accent hue for a "secondary action." Secondary actions are transparent/ghost buttons with the existing border tokens, not a second brand color.
- **Don't** derive a dark-mode color by mechanically inverting a light-mode color's lightness. Every dark-mode token in this system was tuned by hand for warmth and vividness, not generated by a formula.
- **Don't** load a custom webfont. The native OS font stack is intentional, not a placeholder.
