---
name: testing
description: Testing best practices for a Next.js + React project — unit tests, component tests, end-to-end tests, and what to prioritize covering. Use when writing tests, setting up a test suite, or deciding what test coverage a feature needs.
---

# Testing

Best practices for testing a Next.js + React application.

## Test pyramid for this stack

- **Unit tests** (Vitest/Jest) for pure functions: utilities, validation schemas, business logic — fast, no DOM, the bulk of your tests.
- **Component tests** (React Testing Library) for components with real behavior: forms, conditional rendering, interaction handling.
- **End-to-end tests** (Playwright) for critical user flows only (signup, checkout, core CRUD paths) — they're slow and expensive to maintain, so keep them few and high-value.
- Skip testing trivial presentational components with no logic (a component that just renders props) — the cost outweighs the benefit.

## Component testing principles

- Test behavior from the user's perspective: query by role/label/text (`getByRole`, `getByLabelText`), not by implementation detail (CSS class, internal state, test IDs as a first resort).
- Assert on what the user would see/experience (rendered text, disabled state, navigation) rather than on internal function calls.
- Use `userEvent` over `fireEvent` for interaction simulation — it more accurately models real browser event sequences (focus, then keydown, then input, etc).
- Mock network calls at the boundary (MSW) rather than mocking the fetch client deeply, so tests exercise real request/response handling.

## Server-side testing

- Unit test Server Actions and Route Handlers by calling the exported function directly with constructed input, asserting on the returned value/thrown error — no need to spin up a full HTTP server for most cases.
- Test validation schemas (Zod) directly with valid/invalid fixtures — this catches most input-handling bugs cheaply.
- For database-backed logic, test against a real (test/local) database instance or a well-scoped in-memory equivalent rather than mocking the ORM — ORM mocks drift from real query behavior easily.

## End-to-end tests

- Cover the golden path plus the highest-value edge cases (invalid form submission, auth-required redirect) for flows where a regression would be costly (payments, auth, onboarding).
- Keep E2E tests independent and able to run in parallel — each test sets up its own data/state rather than depending on execution order.
- Run E2E against a production-like build, not the dev server, to catch build-only issues (env var handling, bundling).

## CI integration

- Run unit + component tests on every PR; they should complete in well under a few minutes.
- Run E2E on PRs touching critical paths (or on a schedule/pre-deploy) if they're too slow for every push.
- Track coverage as a signal, not a target — a high percentage on trivial code is worse than lower coverage concentrated on business-critical logic.
