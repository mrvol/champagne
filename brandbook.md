# Champagne — Brandbook

## Project

Champagne is a marketplace for champagne and wine: producers (companies) list
goods (bottles), buyers browse, add to cart, and check out into orders.
Mobile-first, server-rendered Django app styled with Tailwind (CDN, no build
step).

## Personality

This is not a marketplace with wine in it — it's a destination where
producers present the result of years of dedication, and every page should
honour that. The benchmark is a premium wine label, a luxury winery
brochure, and an elegant tasting room, not an admin dashboard or a generic
online store. Concretely, that means:

- **Every producer page is theirs, not ours.** A producer should be proud
  to send this URL to a distributor. See [company_detail.html](templates/company_detail.html).
- **Photography carries the emotion, copy earns its place.** Prefer a real
  photo of the vineyard/cellar/bottle over a paragraph describing it. Where
  there's no photo yet, fall back to a deep green gradient (never a gray
  box) — see "Photography" below.
- **Data pages stay honest data pages.** Internal/account views (orders,
  payments, stock, users, transactions) get the same color and type system
  as everything else, but not fabricated storytelling — a "Payment #4"
  record doesn't get a hero image. Elegance here means generous spacing and
  quiet typography, not invented narrative.
- Warm, understated, a little luxurious. Cream and bottle-green over stark
  black-and-white; gold used as a rare accent, not a background.

## Typography

Headings and display text use **Cormorant Garamond** (a serif with the
engraved, tapering quality of an actual wine-label letterform), loaded via
Google Fonts in `templates/base.html` and mapped onto Tailwind's `font-serif`
token — so `class="font-serif"` is all any template needs. Body copy stays
on the system sans stack (Tailwind's default): dense pages (stock tables,
order lists) need plain legibility, not a serif fighting for attention.

- **`font-serif`** — section headings, page titles, producer/wine names.
- **`font-serif italic`** — the wordmark ("Champagne" in the header — as
  plain text, never `{% trans %}`, it's a brand name not a phrase) and
  emotional/editorial moments: "Our Story", page titles on destination
  pages like Producers/Goods/Cart. Reserve italic for the one or two most
  emotional words on a page — if everything is italic, nothing reads as a
  flourish.
- Plain sans, `font-medium`/`font-semibold` — data labels, buttons, nav,
  and anything on a utility/account page.

## Motion

One shared keyframe, `.fade-up` (defined once in `base.html`, not
per-template), lifts hero content in on page load — logo, heading, tagline,
CTA staggered a beat apart via inline `animation-delay`. Beyond that:

- Cards lift and shadow on hover (`hover:-translate-y-0.5 hover:shadow-lg`),
  never on page load — motion should reward an interaction, not perform
  for its own sake.
- Photography zooms subtly on hover inside an `overflow-hidden` frame
  (`hover:scale-105` on the `<img>`, not the card) — a controlled reveal,
  not a jarring jump.
- That's the whole vocabulary. Don't add scroll-triggered reveals,
  parallax, or a third animation style without a reason — "subtle" is the
  brief, and subtlety runs out fast once every element is moving.

## Photography

Real photography of vineyards, cellars, bottles, and the people behind them
is the single highest-leverage way this platform reads as premium rather
than templated — more than any color or font choice. Rules of thumb:

- Every hero (home, producer) is a real photo with a dark gradient overlay
  (`bg-gradient-to-t from-black/70…`) for text legibility — never a stock
  gray placeholder box on a marketing page.
- No photo yet? Fall back to a `from-green-900 to-stone-900` gradient, not
  gray — it still reads as "this brand has a color," just not a photo yet.
- Company/product galleries (`CompanyPhoto`, `GoodPhoto`) are real uploads
  via `Company.upload()` / `Good.upload()` — don't wire a gallery section
  to a template until there are real images to put in it.

## Color palette

## Color palette

Palette values are calibrated against real luxury-brand references (Rolex's
forest green and gold, true oxblood leather) rather than stock Tailwind
hues — stock `green-900`/`amber-600` read as generic "corporate" tones once
placed next to a premium product photo. All overrides live in a
`tailwind.config` block in `templates/base.html` (the app has no build step,
so this is the only way to retune a CDN Tailwind palette); the Tailwind
*token names* below are unchanged, only their hex values differ from
Tailwind's defaults.

| Role | Tailwind token | Hex | Used for |
|---|---|---|---|
| Background | `stone-50` | `#f7f3ea` | Page background — warm ivory, not near-white |
| Surface | `white` | `#ffffff` | Cards, header, bottom nav |
| Border | `stone-200` | `#e8ddc7` | Card/divider borders |
| Border (inputs) | `stone-300` | `#d7c7a5` | Form field borders |
| Text (primary) | `stone-900` | `#1a1510` | Body text — near-black warm charcoal |
| Text (secondary) | `stone-500` / `stone-600` | `#82786a` / `#645b4c` | Labels, muted text, nav links |
| Primary accent | `green-900` | `#0f3d2e` | Primary buttons, brand logo — depth of a Rolex-green, not a bright green |
| Link accent | `green-800` | `#17493a` | Text links — same family as primary, one step lighter |
| Gold accent (rule) | custom `.gold-foil-rule` | gradient `#6b5219 → #c9a227 → #f0dfa8 → #c9a227 → #6b5219` | Header rule only — a light/dark sweep reads as foil-stamped metal; a flat color reads as paint |
| Gold accent (price) | custom `gold` | `#9c7a20` | Product prices — the *only* place gold appears as flat text |
| Success/warning | `amber-50` / `amber-700` | `#fffbeb` / `#b45309` | Warning messages — stock Tailwind amber, deliberately *not* the brand gold |
| Error | `red-50` / `red-700` | `#fef2f2` / `#b91c1c` | Error messages |

Oxblood (`#4a0404`, true oxblood-leather depth) is reserved for a future
"limited vintage" / "reserve" badge — there's no `Good` field for that status
yet, so it isn't wired into any template. Add it as a custom color alongside
`gold` in `base.html` when that field exists; don't add the token or a badge
ahead of the data it would represent.

## Usage rules

- **Gold is sparing.** It marks the header rule and product prices only —
  never a background fill, never body text. Overusing it reads as gaudy
  rather than premium.
- **Gold accent is its own token, not `amber-700`.** Prices used to share
  `amber-700` with warning messages; that coupling meant recoloring gold
  would also recolor warnings. `gold` and `amber-*` are now independent —
  warnings stay stock-Tailwind semantic regardless of what the brand gold
  does.
- **Flat color alone doesn't read as metal.** The header rule uses a
  gradient (`.gold-foil-rule` in `base.html`) that sweeps light→dark→light,
  the same cue foil-stamped labels use. Reserve this technique for rules/
  dividers, not body text — gradient text at small sizes reads as muddy, not
  shiny.
- **Green is the workhorse accent.** Every primary action (Add to cart, Place
  order, Sign in, Create account) and every text link uses green, not the
  gold.
- **Stone, not gray.** Warm neutrals (`stone-*`) throughout, not cool
  `neutral`/`gray`/`slate` — keeps the palette feeling like paper/cream
  instead of a generic admin UI.
- Error and warning message colors stay semantic (red/amber) regardless of
  brand palette — don't reskin those for "on-brand" gold.

## Layout & components

Reusable patterns, so new pages compose from the same vocabulary instead of
reinventing it:

- **Navigation** (`base.html`) — the one component every page shares, so it
  sets the tone before anything else loads. Primary links use `.nav-link`:
  small uppercase text (`text-xs tracking-[0.18em]`), quiet `stone-600` by
  default, and — on hover *or* for the current section — the same foil-gold
  gradient as the header rule draws in as a 1px underline
  (`transform: scaleX(0→1)` on a `::after`, not a color swap alone). That
  reuse is deliberate: the foil sweep is becoming this brand's signature
  motif, not a one-off on the header rule. `Sign up` is the one filled/pill
  CTA in the nav (`border-green-900 rounded-full`, fills solid on hover) —
  it's the only action in the header that should read as a button; every
  other link stays plain text. The current section is computed once, in the
  template, via `{% with url_name=request.resolver_match.url_name %}` — no
  view changes needed. On mobile the equivalent is `.tab-link`: a small
  hand-drawn line icon (24×24, `stroke-width: 1.5`, no icon library) over a
  tracked micro-label, same active-state logic, in the fixed bottom bar.
  Don't reach for a hamburger/drawer pattern here — the bottom bar is a
  deliberate, thumb-reachable mobile-commerce pattern, not a placeholder for
  something more "proper."
- **Hero** (`home.html`, `company_detail.html`) — full-width photo (edge to
  edge of the content column via `-mx-4`, not the true viewport), a
  `bg-gradient-to-t from-black/70…` overlay, `.fade-up` content stacked at
  the bottom-left or center. No hero without a real photo behind it.
- **Product/producer card** (`good_md.html`, `company_md.html`) — the one
  card shape used everywhere a wine or producer appears (home, lists,
  producer pages): `rounded-xl border border-stone-200`, photo on top,
  name + one line of meta below, hover lift + image zoom. When you need a
  card grid, `{% include %}` one of these two partials rather than writing
  a third card shape.
- **Pill/tag** (`bg-stone-100 rounded-full px-3 py-1` for filled, `border
  border-stone-300` for outline) — grape varieties, certifications. Filled
  vs. outline is the only distinction; don't add more tag styles.
- **Label/value grid** — the pattern for both storytelling stats
  (region/founded/production on `company_detail.html`) and plain record
  data (`order_detail.html`, `user_detail.html`, etc.): a
  `text-xs uppercase tracking-wide text-stone-500` label over a
  `font-medium` value, in a `grid grid-cols-2` (or 4, for shorter values).
  This replaced the old boxed `<dl class="divide-y">` look everywhere —
  that pattern read as an admin record, not a page about a wine.
- **Card list** — for plain record lists (orders, payments, addresses,
  users, stock, transactions, warehouses): each row is its own
  `rounded-xl border border-stone-200` card with `hover:shadow-md`,
  stacked with `space-y-3`, not one bordered box with internal
  `divide-y` rows.

## Content this system depends on

A few templates render nothing until a field is populated — by design,
don't fill empty sections with placeholder copy:

- `Company.story`, `.tagline`, `.region`, `.certifications`,
  `.annual_production`, `.contact_email/phone`, `.hero_photo`, and the
  `CompanyPhoto` gallery drive everything on `company_detail.html` past the
  name. A producer with none of these still gets a working page; it just
  won't look like a showroom yet.
- `Good.description` and `.bullets` (JSON list of short marketing lines)
  drive the tasting-note section on `good_detail.html`. Both existed on
  the model before this pass but were never rendered anywhere — worth
  populating for real bottles, since it's currently the only place a
  wine's own story (not the producer's) gets told.
