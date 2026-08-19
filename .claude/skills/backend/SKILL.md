---
name: backend
description: Server-side best practices for a Next.js project — Route Handlers, Server Actions, middleware, validation, and error handling. Use when writing API routes, server actions, or any server-side request-handling logic.
---

# Backend

Best practices for server-side logic in a Next.js (App Router) project.

## Route Handlers vs. Server Actions

- Use Server Actions for form submissions and mutations triggered from within the app's own UI — they avoid hand-written `fetch` + API route boilerplate and integrate with `useFormState`/`useTransition`.
- Use Route Handlers (`app/api/**/route.ts`) for anything a third party or external client needs to call: public APIs, webhooks, integrations, or endpoints consumed by a non-Next.js client.
- Never expose a Server Action as the only way to perform a security-sensitive mutation without also re-checking auth/authorization inside the action itself — Server Actions are still public HTTP endpoints.

## Validation

- Validate all external input (body, query params, headers) at the boundary with a schema library (Zod) before touching it — never trust client-supplied data, including values the client "shouldn't" be able to change.
- Return structured, typed error responses (consistent shape: `{ error: { code, message } }`) so the frontend can handle failures predictably.
- Reject unknown/extra fields rather than silently ignoring them when the schema allows it, to avoid mass-assignment-style bugs.

## Error handling

- Never leak internal error details (stack traces, SQL errors, file paths) to the client in production responses; log them server-side and return a generic message.
- Use explicit HTTP status codes (400 validation, 401 unauthenticated, 403 unauthorized, 404 not found, 409 conflict, 429 rate-limited, 500 unexpected) rather than always returning 200 with an error flag in the body.
- Wrap route handlers in a consistent try/catch (or a shared error-handling wrapper) so an unexpected throw doesn't crash the function silently.

## Middleware

- Keep `middleware.ts` fast and side-effect-light (it runs on the Edge runtime, on every matching request) — auth-token presence checks and redirects, not full session/database lookups.
- Scope middleware with a `matcher` so it doesn't run on static assets or unrelated routes.
- Do authoritative authorization checks in the Route Handler/Server Action itself, not only in middleware — middleware is a first line of defense, not the only one.

## API design

- Keep endpoints resource-oriented and consistent (`/api/posts/:id`, not a grab-bag of RPC-style verbs).
- Version public APIs you don't control the only consumer of, so you can evolve them without breaking existing clients.
- Rate-limit and validate payload size on any publicly reachable endpoint, especially unauthenticated ones (webhooks, contact forms, signup).
- Make external calls (email, payment, third-party APIs) idempotent where possible, and add timeouts so a hanging dependency can't hang your request.
