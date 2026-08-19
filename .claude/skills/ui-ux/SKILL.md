---
name: ui-ux
description: Visual design and UX best practices for a Tailwind-based Next.js website — design tokens, spacing/typography scales, responsive layout, dark mode, and interaction polish. Use when styling components, building layouts, or making visual design decisions.
---

# UI/UX

Best practices for visual design and interaction quality using Tailwind CSS.

## Design tokens & consistency

- Define a small, fixed scale for spacing, font size, and radius in `tailwind.config` (theme extension) and use it everywhere — avoid arbitrary one-off values (`mt-[13px]`) except for genuine edge cases.
- Pick a limited color palette (primary, secondary, neutral grays, semantic success/warning/error) and reference it via Tailwind theme colors, not raw hex values scattered through components.
- Keep a consistent type scale (e.g. `text-sm`/`base`/`lg`/`xl`/`2xl`/`3xl`) and don't introduce new sizes ad hoc; consistent scale is what makes a UI feel designed rather than assembled.

## Layout & responsiveness

- Design mobile-first: base classes target the smallest viewport, then layer `sm:`/`md:`/`lg:` breakpoints up.
- Use `flex`/`grid` utilities over manual positioning; reach for CSS grid for two-dimensional layouts (page shells, card grids) and flexbox for one-dimensional alignment (nav bars, button groups).
- Constrain content width with a max-width container (`max-w-7xl mx-auto px-4`) rather than letting text/content stretch full-bleed on wide screens.
- Test every layout at real breakpoints (375px, 768px, 1024px, 1440px) — don't just shrink a desktop browser window.

## Dark mode

- Use Tailwind's `dark:` variant with `class` strategy so it's user/system-togglable rather than relying only on `prefers-color-scheme`.
- Define dark variants for every custom color token up front, not bolted on later — background, text, border, and shadow all need a dark counterpart.
- Check contrast in both themes, not just light — a border or shadow that reads fine on white can disappear entirely on dark backgrounds.

## Interaction & polish

- Every interactive element needs a visible `hover:`, `focus-visible:`, and `active:` state — don't rely on cursor changes alone.
- Use `transition` utilities for state changes (color, opacity, transform) with short durations (150-200ms) — motion should feel responsive, not sluggish.
- Show loading states (skeletons, spinners, disabled buttons) for anything that takes more than ~200ms, so the UI never feels unresponsive or frozen.
- Keep touch targets at least 44x44px on mobile for anything tappable.

## Accessibility & contrast

- Meet WCAG AA contrast ratios (4.5:1 for body text, 3:1 for large text) for every text/background color pairing, including on hover/focus states.
- Don't communicate meaning by color alone (error states need an icon or text label too, not just red).
- Respect `prefers-reduced-motion` for any non-essential animation.
