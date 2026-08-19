---
name: frontend
description: React component and UI-development best practices for a Next.js + Tailwind project — component composition, hooks, forms, accessibility, and rendering performance. Use when writing or reviewing React components, hooks, or client-side interaction logic.
---

# Frontend

Best practices for writing React components in a Next.js + Tailwind codebase.

## Component design

- Keep components small and focused on one responsibility; extract a subcomponent once a component mixes layout, data-fetching, and interaction logic.
- Prefer composition (`children`, render props, slots) over configuration props that branch internally with booleans (`variant`, not `isPrimary`/`isSecondary`/`isLarge` flags stacked together).
- Type all props explicitly with TypeScript interfaces; avoid `any` and avoid over-widening with `React.FC` (prefer typed function signatures so children typing stays explicit).
- Name components after what they render, not their implementation detail (`UserAvatar`, not `Img1`).

## Hooks

- Follow the Rules of Hooks: only call hooks at the top level, never conditionally.
- Extract repeated stateful logic into custom hooks (`useDebouncedValue`, `useMediaQuery`) rather than copy-pasting `useEffect` blocks.
- Keep `useEffect` dependency arrays honest — don't suppress the lint rule; if a value shouldn't trigger a re-run, restructure (refs, derived state) instead of silencing it.
- Prefer deriving values during render over storing them in state and syncing with an effect.

## Forms

- Use a schema-based form library (React Hook Form + Zod) for anything beyond a single input — it centralizes validation, error state, and submission handling.
- Validate on both client (fast feedback) and server (source of truth) using the same Zod schema shared between them.
- Always show inline, field-level error messages, and keep the submit button in a `disabled`/loading state while a submission is in flight to prevent double-submits.

## Accessibility

- Use semantic HTML elements (`button`, `nav`, `label`, `header`) before reaching for `div` + ARIA.
- Every interactive element must be reachable and operable by keyboard (`Tab`, `Enter`, `Space`, `Esc` for dismiss).
- Images need meaningful `alt` text (or `alt=""` if purely decorative); icon-only buttons need `aria-label`.
- Manage focus explicitly for modals/drawers (trap focus while open, return focus to the trigger on close).

## Rendering performance

- Don't reach for `useMemo`/`useCallback`/`React.memo` by default — profile first; premature memoization adds complexity without measured benefit.
- Memoize when passing callbacks/objects to a memoized child, or when a computation is genuinely expensive and re-runs on unrelated re-renders.
- Virtualize long lists (hundreds+ of rows) instead of rendering every item.
- Give list items stable, unique `key`s (never array index if the list can reorder or filter).
