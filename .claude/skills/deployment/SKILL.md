---
name: deployment
description: Deployment and release best practices for a Next.js website — environment configuration, CI/CD, preview deployments, caching/ISR, and rollback strategy. Use when setting up deployment, configuring environments, or preparing a release.
---

# Deployment

Best practices for deploying and releasing a Next.js application.

## Environments

- Maintain at least three environments: local/dev, preview/staging, production — never test unreleased changes directly against production data.
- Keep environment variables scoped per environment (separate API keys, database URLs, feature flags for dev/staging/prod) — never point staging at the production database.
- Use platform preview deployments (e.g. one per pull request) so changes can be reviewed and QA'd in a real deployed environment before merging.

## CI/CD pipeline

- Gate merges on CI: type-check, lint, unit/component tests, and build must all pass before merge — a broken build should never reach `main`.
- Run the production build (`next build`) in CI, not just the dev server — build-time errors (type errors, invalid static generation, missing env vars) only surface there.
- Automate deployment from `main` (or a release branch) rather than deploying manually from a local machine, so every deploy is reproducible and traceable to a commit.

## Caching & rendering strategy

- Choose the right rendering mode per route deliberately: static generation for content that rarely changes, ISR (`revalidate`) for content that changes periodically, dynamic rendering only where truly required (personalized/real-time data).
- Set explicit `revalidate` times or on-demand revalidation (`revalidatePath`/`revalidateTag`) rather than leaving pages fully dynamic by default — unnecessary dynamic rendering costs latency and server load.
- Set appropriate `Cache-Control` headers on Route Handlers that serve cacheable data; let the CDN do the work instead of hitting the origin every request.

## Release safety

- Ship behind feature flags for risky or partial features so a bad change can be turned off without a redeploy.
- Roll out database migrations as backward-compatible steps (see `database` skill) so a deploy and a migration don't have to land in the exact same instant.
- Keep deploys small and frequent rather than large and infrequent — smaller diffs are easier to bisect when something breaks.
- Know the rollback path before you need it: confirm the platform can redeploy the previous build/commit quickly, and that migrations applied in the bad deploy don't block rolling back.

## Monitoring

- Wire up error tracking (Sentry or equivalent) in production so failures surface immediately instead of being discovered via user reports.
- Track Core Web Vitals and server response times in production, not just locally — real-world network/device conditions differ significantly from dev.
- Set up alerts for elevated error rates or failed background jobs (webhooks, cron, queues) right after a deploy.
