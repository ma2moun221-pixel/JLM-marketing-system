---
name: security
description: Security best practices for a Next.js website — authentication, authorization, input sanitization, secrets management, and HTTP security headers. Use when implementing auth, handling user input, managing secrets/env vars, or reviewing code for vulnerabilities.
---

# Security

Best practices for keeping a Next.js application secure.

## Authentication & sessions

- Use a proven library (Auth.js/NextAuth, Clerk, Lucia) rather than hand-rolling session/token logic.
- Store session tokens in `httpOnly`, `Secure`, `SameSite=Lax` (or `Strict`) cookies — never in `localStorage`, which is readable by any script (XSS turns into full account takeover).
- Hash passwords with a slow, salted algorithm (bcrypt/argon2) if you ever store them yourself; never store plaintext or reversibly-encrypted passwords.
- Expire and rotate sessions/refresh tokens; invalidate server-side sessions on logout, not just client-side state.

## Authorization

- Re-check authorization on every Server Action and Route Handler — never assume that because a link/button is hidden in the UI, the underlying action is protected.
- Default to deny: check the user is allowed to act on *this specific resource* (ownership/role check), not just that they're logged in.
- Keep authorization logic centralized (a shared `can(user, action, resource)` helper) rather than reimplemented inline at each call site, where it's easy to forget a check.

## Input handling

- Treat all user input as untrusted: validate shape/type/length server-side with a schema (Zod), even if the client already validated it.
- Use parameterized queries / your ORM's query builder — never string-concatenate user input into raw SQL.
- React escapes text content by default; avoid `dangerouslySetInnerHTML` entirely, or sanitize with a library like DOMPurify if rendering user-supplied HTML is unavoidable.
- Validate and constrain file uploads (type, size, and re-encode/scan images) before storing or serving them.

## Secrets management

- Keep secrets in environment variables, never committed to the repo; add `.env*` (except `.env.example`) to `.gitignore`.
- Only prefix env vars with `NEXT_PUBLIC_` if the value is genuinely safe to ship to the browser — anything with that prefix is bundled into client JS and publicly visible.
- Use different secrets per environment (dev/staging/prod); rotate any secret that may have leaked (committed by mistake, pasted in a shared channel, etc.).

## HTTP & headers

- Set security headers (CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Strict-Transport-Security`) via `next.config.js` headers or middleware.
- Scope a Content-Security-Policy that blocks inline scripts by default and explicitly allowlists required third-party origins.
- Rate-limit public, unauthenticated endpoints (login, signup, contact forms, webhooks) to blunt brute-force and abuse.
- Keep dependencies patched — run `npm audit`/Dependabot regularly, since most real-world Next.js vulnerabilities arrive via outdated packages, not novel app-level bugs.
