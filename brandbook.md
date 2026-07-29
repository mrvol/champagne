# Voilà Champagne — Brandbook

## Project

Voilà Champagne (voilachampagne.com) is a marketplace for champagne and wine: producers (companies) list
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
- **`font-serif italic`** — the wordmark ("Voilà Champagne" in the header — as
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

- Every hero — the producer storytelling hero and the homepage's conversion
  hero alike — is a real full-bleed photo with a dark gradient overlay
  (`bg-gradient-to-t from-black/75…`) for text legibility, never a stock
  gray placeholder box. See "Conversion hero" below for how the homepage
  layers its shopping content (bottle shot, CTA, search) on top of that
  same photo treatment.
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
  something more "proper." The header's nav/tab-bar crossover is `xl`
  (1280px), not `md` — the full desktop nav (logo + links + sign in/up +
  language select) needs that much room once an authenticated user's extra
  Cart/Orders links and a longer language name (`Français`, `Русский`) are
  both in play; anything narrower measurably overflows. Don't move this back
  down to `md`/`lg` without re-checking all three locales at that width.
- **Storytelling hero** (`company_detail.html`) — full-width photo (edge to
  edge of the content column via `-mx-4`, not the true viewport), a
  `bg-gradient-to-t from-black/70…` overlay, `.fade-up` content stacked at
  the bottom-left or center. No hero without a real photo behind it. Use
  this where the page's job is to make someone feel something before they
  do anything (a producer's story).
- **Conversion hero** (`home.html`) — uses the same full-bleed photo +
  dark gradient overlay as the storytelling hero (this was deliberately
  photo-*less* for a while — a pale panel with no background image — to
  keep the shopping CTA from competing with a photo for attention; brought
  back by request because the atmospheric photo treatment itself was worth
  keeping). Content is centered and stacked, `.fade-up` staggered: the
  bottle shot first (small, `object-contain`, capped `h-24`→`h-40` across
  breakpoints, drop-shadowed so it floats above the photo — still sized as
  a supporting accent, not full-bleed, so it doesn't out-compete the CTA),
  then the eyebrow/headline/subhead in white, then the CTA + search.
  The image and overlay are `absolute inset-0` on the *section*, while the
  text/CTA content sits in normal flow with a `min-h-[420px] md:min-h-[480px]`
  floor — not inside a fixed `aspect-[...]` box. This matters: an
  aspect-ratio box clips anything taller than the ratio allows, and once
  this hero grew to include a bottle image, headline, subhead, CTA *and*
  search stacked vertically, a fixed-aspect box silently clipped the CTA
  and search out of view entirely at the `sm`/`md` breakpoints — real bug,
  not hypothetical. Keep the CTA + search column `flex-col` at every
  breakpoint (no `sm:`/`md:`/`lg:flex-row`) for the same reason it was
  fixed before: a button and search field side by side run out of room and
  clip long labels (French/Russian) before any breakpoint's column is wide
  enough to hold both; full-width stacked always fits.
- **Product of the Day** (`home.html`, right after the conversion hero,
  before the filter chips — `mp.views.home` picks it) — a single spotlighted
  good in an oversized card (`rounded-2xl`, photo full-bleed on one side,
  details on the other, same responsive split as the hero: stacked on
  mobile, side-by-side from `md:`). It exists to sell one bottle hard
  without ever reading as a banner ad, so every "urgency" cue on it has to
  be true, not decorative:
  - **The pick itself rotates for real.** `mp.views.home` selects it via
    `date.today().toordinal() % len(eligible)` over in-stock, verified-seller
    goods — a deterministic daily rotation, not a random reroll per
    request. That's what makes the eyebrow copy ("Today's Selection" /
    "Featured today only — a new selection rotates in tomorrow.") honest
    instead of a fake-urgency trope: it really is a different bottle
    tomorrow, on a schedule, with no JS countdown timer required or wanted.
  - **Scarcity is only shown when it's real.** The "Only N bottles
    remaining" line renders solely when `pick.available <= 20` — never
    invented for a well-stocked bottle. Uses `amber-700` (semantic
    warning, see "Usage rules"), not red, not gold: a quiet fact, not an
    alarm.
  - **Discounts are real `Discount` rows, not fabricated.** If the picked
    good has a currently-active `Discount` (`starts_at`/`ends_at` window),
    the view computes a real `pick_price` and the template shows a
    strikethrough original beside the gold discounted price. No active
    discount → just the plain gold price, same as everywhere else in the
    app. Don't add a badge/banner implying a deal exists when
    `pick_discount` is `None`.
  - **Trust reuses existing proof, it doesn't invent new copy.** The
    verified-producer checkmark and "Est. {year}" line are the exact
    partial from `company_md.html`, not new marketing language — the
    credibility signal is "we already vouch for this producer everywhere,"
    not a one-off claim written just for this slot.
  - If there are no in-stock verified goods at all, the section doesn't
    render (`{% if pick %}`) — same "don't fabricate content" rule as the
    rest of the homepage.
- **Product/producer card** (`good_md.html`, `company_md.html`) — the one
  card shape used everywhere a wine or producer appears (home, lists,
  producer pages): `rounded-xl border border-stone-200`, photo on top,
  name + one line of meta below, hover lift + image zoom. When you need a
  card grid, `{% include %}` one of these two partials rather than writing
  a third card shape.
- **Pill/tag** (`bg-stone-100 rounded-full px-3 py-1` for filled, `border
  border-stone-300` for outline) — grape varieties, certifications. Filled
  vs. outline is the only distinction; don't add more tag styles.
- **Filter chip** (`home.html`'s category row) — a different job from
  Pill/tag above: these are clickable navigation into `good_list`, not
  descriptive metadata, so they get their own filled state:
  `bg-green-900 text-white rounded-full px-4 py-1.5` for the active/"All"
  entry, `border border-stone-300 text-stone-700 rounded-full px-4 py-1.5`
  for the rest — green because it's a primary action (see "Green is the
  workhorse accent" below), not because Pill/tag's filled style extends
  here.
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
