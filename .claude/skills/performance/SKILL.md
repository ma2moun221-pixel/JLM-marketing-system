---
name: performance
description: Performance best practices for a Next.js + React + Tailwind website — Core Web Vitals, image/font optimization, code splitting, streaming, and bundle size. Use when optimizing page load speed, investigating slow pages, or reviewing code for performance impact.
---

# Performance

Best practices for keeping a Next.js site fast, measured against Core Web Vitals (LCP, INP, CLS).

## Core Web Vitals targets

- **LCP** (Largest Contentful Paint, target <2.5s): usually the hero image or main heading — prioritize loading it (see image optimization below), avoid render-blocking resources above the fold.
- **INP** (Interaction to Next Paint, target <200ms): keep the main thread free — avoid long synchronous tasks on interaction, especially in client components handling clicks/input.
- **CLS** (Cumulative Layout Shift, target <0.1): always reserve space for images/embeds/ads (explicit `width`/`height` or aspect-ratio), avoid injecting content above existing content after load, and preload custom fonts to avoid layout jump on swap.

## Images & fonts

- Always use `next/image` instead of a raw `<img>` — it handles responsive sizing, lazy loading, and modern formats (WebP/AVIF) automatically.
- Mark the LCP image (usually the hero) with `priority` so it isn't lazy-loaded; leave every other offscreen image lazy (the default).
- Use `next/font` for custom fonts — it self-hosts and inlines font-loading to avoid extra round trips and layout shift, rather than linking to an external font CDN.

## Code splitting & bundle size

- Rely on the App Router's automatic per-route code splitting; additionally use `next/dynamic` for heavy, non-critical components (rich text editors, charts, modals) so they don't inflate the initial bundle.
- Keep client bundles lean: audit `"use client"` boundaries (see `architecture` skill) since every client component and its imports ship to the browser.
- Check bundle composition periodically (`@next/bundle-analyzer`) and watch for accidentally importing a large library entirely (e.g. all of `lodash`) when only one function is needed.
- Avoid shipping duplicate large dependencies (e.g. two date libraries) — standardize on one.

## Data fetching & rendering

- Use `Suspense` boundaries with streaming to show a fast initial shell while slower data-dependent parts of the page load in — avoid one big blocking `await` at the top of a page that delays everything behind the slowest fetch.
- Fetch data in parallel (`Promise.all`) when multiple independent requests are needed for a page, instead of sequential `await`s that compound latency.
- Cache and revalidate appropriately (see `deployment` skill) rather than refetching unchanged data on every request.

## Measurement

- Profile with Lighthouse/PageSpeed Insights and real-user monitoring (field data), not just local dev — dev-mode performance doesn't reflect production.
- Treat performance budgets as part of the definition of done for pages that matter (landing pages, checkout) — regressions should be caught before merge, not after a complaint.
