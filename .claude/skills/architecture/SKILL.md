---
name: architecture
description: Architectural guidance for a Next.js + React + Tailwind project — folder structure, App Router conventions, server/client component boundaries, data flow, and state management. Use when planning a new feature, deciding where code should live, or reviewing overall project structure.
---

# Architecture

Guidance for structuring a professional Next.js (App Router) + React + Tailwind codebase so it stays maintainable as it grows.

## Folder structure

- `app/` — routes only. Each route segment gets `page.tsx`, and `layout.tsx`/`loading.tsx`/`error.tsx`/`not-found.tsx` as needed.
- `components/` — shared, reusable UI components, organized by domain (`components/nav/`, `components/forms/`) not by type.
- `components/ui/` — low-level primitives (Button, Input, Card) that mirror a design system, framework-agnostic of business logic.
- `lib/` — non-React logic: API clients, utilities, validation schemas, constants.
- `hooks/` — shared custom hooks.
- `types/` — shared TypeScript types/interfaces not colocated with a single feature.
- Colocate feature-specific components, hooks, and tests next to the route that uses them; only promote to a shared folder once a second consumer appears.

## Server vs. client components

- Default to Server Components. Add `"use client"` only at the leaf where interactivity (state, effects, browser APIs, event handlers) is actually required.
- Push `"use client"` boundaries as far down the tree as possible — wrap only the interactive part, not the whole page, so the rest stays server-rendered and out of the client bundle.
- Never import server-only code (database clients, secrets, `fs`) into a file that could end up in a client bundle; use the `server-only` package to enforce this at build time.
- Pass data down as props from Server to Client Components rather than fetching the same data twice.

## Data flow

- Fetch data in Server Components (or Route Handlers/Server Actions) close to where it's used; avoid client-side waterfalls for initial page data.
- Use Server Actions for mutations from forms instead of hand-rolled API routes + `fetch` where possible; fall back to Route Handlers for public/external APIs or webhooks.
- Keep a single source of truth for each piece of state — don't duplicate server data into client state unless it needs local, optimistic mutation.

## State management

- Local component state (`useState`/`useReducer`) first. Reach for a global client store (Zustand, Jotai) only for state genuinely shared across distant parts of the tree (auth session, theme, cart).
- Use URL search params for state that should be shareable/bookmarkable (filters, pagination, tabs).
- Avoid prop-drilling more than 2-3 levels — introduce context or composition (children props) instead.

## Module boundaries

- Group by feature/domain, not by technical layer, once the app grows beyond a handful of routes (e.g. `features/billing/{components,hooks,actions}.ts` rather than scattering billing code across generic `components/`, `hooks/`).
- Keep cross-feature imports one-directional; shared primitives live in `lib`/`components/ui`, features don't import from each other.
- Barrel files (`index.ts` re-exports) are fine for public feature APIs but avoid deep barrel chains that hurt tree-shaking and build times.
