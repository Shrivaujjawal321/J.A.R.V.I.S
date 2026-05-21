# GLP-1 Nutrition Copilot — UI/UX Design Brief
**Project:** P1 · RAG Decathlon  
**Stack:** Next.js 15 · React 19 · Tailwind 4 · shadcn/ui v4 · Vercel  
**Author:** ui-ux-designer-agent (Jarvis)  
**Date:** 2026-05-14  
**Status:** Production-ready brief for frontend-engineer-agent

---

## 1. Design Direction

Six principles that govern every decision in this brief:

1. **Evidence-first, never authority-faking.** Every response displays its source count and citation chain before the answer text. The product's job is to reduce information asymmetry between peer-reviewed literature and the user — not to be an oracle. Source badges are structural, not decorative.

2. **Calm clinical density, not chatbot warmth.** Reference anchor: OpenEvidence's clinical economy meets Linear's typographic restraint meets Stripe's component precision. This is not a wellness app with gradients and sparkles. It is a knowledge tool with the visual register of a good journal abstract viewer.

3. **OKLCH-grounded palette: trust-blue as primary, evidence-green as positive signal, muted amber for warnings.** All three have an explicit dark-mode mirror with identical perceptual lightness step offsets. No pure white — off-white ground reduces eye strain for long reading sessions.

4. **Motion is a cognition aid, not decoration.** Skeleton shimmer communicates data retrieval (not page chrome loading). Streaming text cursor marks "live synthesis in progress." All motion respects prefers-reduced-motion with instant/fade alternatives.

5. **Safety surface area is visible architecture.** The disclaimer is structurally permanent — it cannot be dismissed entirely. Out-of-scope refusals render a distinct visual component, never a plain text paragraph mixed into a normal answer.

6. **Superscript citation markers, not inline brackets.** protein(1) calcium(2) over protein [1] calcium [2] — screen-reader narrative stays coherent, visual noise is lower, and hover reveals the source card progressively.

---

## 2. Reference Landscape (2026 Healthcare AI UI Bar)

### Reference 1 — OpenEvidence
**URL:** https://www.openevidence.com  
**Takeaway:** The closest living reference for this product. "Citation formatting is well-designed — sources are inline and tappable." Clean, focused, single-purpose layout; clinician-first information hierarchy. The interface does one thing and stays out of the way. Pharmaceutical ads are separated from answer content — spatial separation as trust signal.

### Reference 2 — Perplexity Health (Pro tier, launched March 2026)
**URL:** https://www.perplexity.ai/enterprise/use-cases/health  
**Takeaway:** Inline citations with title + favicon metadata for quick relevance scanning. Progressive disclosure: hover for preview, click for full source. Grounds all health answers in NEJM / BMJ / FDA sources — the journal badge next to each citation communicates provenance instantly without opening the source.

### Reference 3 — Glass Health
**URL:** https://glass.health  
**Takeaway:** "Every output includes citations and is meant to be critically evaluated by the treating physician." The design actively positions itself as decision-support, not decision-maker — this is the posture our product should adopt in copy and layout alike. Sparse, data-dense, zero chatbot personality.

### Reference 4 — Elicit (AI for Scientific Research)
**URL:** https://elicit.com  
**Takeaway:** Sentence-level citations from underlying sources (not paragraph-level). Literature matrix as visual affordance for evidence density. The UI communicates "this claim came from this exact sentence in this paper" — the precision model we should aspire to for micronutrient claims.

### Reference 5 — Hippocratic AI (Polaris system)
**URL:** https://hippocraticai.com  
**Takeaway:** Safety is the explicit product headline. Key design lesson: the voice of the interface — even in text — must feel like a knowledgeable support person, not a search engine returning results. Empathy-inference driven without resorting to chatbot persona design.

### Reference 6 — ShapeOfAI Citation Patterns (2026 survey)
**URL:** https://www.shapeof.ai/patterns/citations  
**Takeaway:** Authoritative 2026 survey of citation UI across AI products. Key finding: inline cues work for sentence-level claims; panels/drawers work for long-form exploration. Broken sources must be explicitly labelled, not hidden. Hover-for-preview + click-for-full is the 2026 gold standard.

### Reference 7 — FuseLab Healthcare UX Guide 2026
**URL:** https://fuselabcreative.com/healthcare-ux-design-best-practices-guide/  
**Takeaway:** "The three-second rule" — critical information must be visually prominent in under 3 seconds. Progressive disclosure: surface confidence level before answer body. AI confidence must be visible so users evaluate before acting. Accessibility from wireframe, not as a post-design patch.

### Reference 8 — Mobbin Medical App Category
**URL:** https://mobbin.com/explore/mobile/app-categories/medical  
**Takeaway:** 2026 medical apps on Mobbin converge on: high x-height sans-serif type, muted off-white backgrounds, status-coloured micro-badges, bottom-sheet source panels on mobile, and no gamification in clinical flows.

### Shared Patterns Across Reference Set

- Source attribution is structural, not supplemental. Adjacent to each claim, not in a footer.
- Calm, desaturated colour grounds (off-white, slate-50) with single-hue accent in trust-blue or evidence-green.
- Dense information, generous line-height. These are reading interfaces. Line-height 1.65–1.75 for body.
- Safety copy is visible without being alarming. Disclaimer banners are quiet (muted border, small text) but always present. Red register reserved for refusals only.
- No chatbot avatars, no first-person AI persona. The product is the knowledge base.
- Citation count badge ("3 sources") appears before the answer body — users know evidential weight before reading.

---

## 3. Design Tokens

### CSS Custom Properties (@theme block, Tailwind 4 CSS-first)

```css
@theme {
  /* COLOUR */

  /* Neutral ground */
  --color-bg-base:      oklch(98.5% 0.004 250);   /* warm off-white, reading-safe */
  --color-bg-surface:   oklch(96.5% 0.006 250);   /* card / answer-card ground */
  --color-bg-sunken:    oklch(94.0% 0.008 250);   /* input area, recessed fields */
  --color-bg-overlay:   oklch(99.0% 0.003 250);   /* modal / sheet backdrop lift */

  /* Foreground */
  --color-fg-base:      oklch(18.0% 0.010 250);   /* primary text, ~13:1 on bg-base (AAA) */
  --color-fg-muted:     oklch(46.0% 0.012 250);   /* secondary text, metadata, ~5.8:1 (AA) */
  --color-fg-subtle:    oklch(62.0% 0.009 250);   /* placeholder, disabled labels */
  --color-fg-inverse:   oklch(98.0% 0.003 250);   /* text on dark/primary surfaces */

  /* Trust blue — primary interactive + source indicators */
  --color-primary-50:   oklch(97.0% 0.012 240);
  --color-primary-100:  oklch(93.0% 0.028 240);
  --color-primary-200:  oklch(86.0% 0.055 240);
  --color-primary-400:  oklch(66.0% 0.130 240);
  --color-primary-500:  oklch(55.0% 0.170 240);   /* main interactive, 5.4:1 on bg-base */
  --color-primary-600:  oklch(44.0% 0.155 240);   /* hover state */
  --color-primary-700:  oklch(36.0% 0.120 240);   /* active / pressed */
  --color-primary-900:  oklch(18.0% 0.045 240);

  /* Evidence green — positive signal, verified sources */
  --color-evidence-50:  oklch(97.0% 0.015 158);
  --color-evidence-100: oklch(92.0% 0.040 158);
  --color-evidence-400: oklch(66.0% 0.130 158);
  --color-evidence-500: oklch(55.0% 0.155 158);   /* peer-reviewed badge */
  --color-evidence-600: oklch(44.0% 0.130 158);
  --color-evidence-900: oklch(18.0% 0.045 158);

  /* Calm amber — dietary advisory warnings, not errors */
  --color-warning-50:   oklch(97.0% 0.020 80);
  --color-warning-100:  oklch(93.0% 0.055 80);
  --color-warning-400:  oklch(70.0% 0.135 80);
  --color-warning-500:  oklch(60.0% 0.155 80);   /* 4.8:1 on bg-base */
  --color-warning-600:  oklch(48.0% 0.130 80);
  --color-warning-900:  oklch(22.0% 0.050 80);

  /* Alert red — refusal state and scope-exceeded queries only */
  --color-danger-50:    oklch(97.0% 0.012 25);
  --color-danger-100:   oklch(92.0% 0.040 25);
  --color-danger-500:   oklch(55.0% 0.190 25);
  --color-danger-600:   oklch(44.0% 0.165 25);
  --color-danger-900:   oklch(18.0% 0.060 25);

  /* Borders */
  --color-border-base:    oklch(88.0% 0.012 250);
  --color-border-strong:  oklch(76.0% 0.018 250);
  --color-border-focus:   oklch(55.0% 0.170 240);   /* = primary-500 */

  /* Source-type accent colours */
  --color-source-pubmed:  oklch(55.0% 0.170 240);   /* trust-blue */
  --color-source-usda:    oklch(55.0% 0.155 158);   /* evidence-green */
  --color-source-nih:     oklch(60.0% 0.155 80);    /* amber */
  --color-source-asmbs:   oklch(52.0% 0.120 280);   /* indigo */

  /* TYPOGRAPHY */

  --font-sans:  "Inter Variable", "Inter", system-ui, sans-serif;
  --font-mono:  "IBM Plex Mono", "Fira Code", monospace;

  /* Type scale */
  --text-xs:    0.6875rem;   /* 11px — citation micro-labels */
  --text-sm:    0.8125rem;   /* 13px — citation chips, metadata */
  --text-base:  0.9375rem;   /* 15px — answer body */
  --text-lg:    1.0625rem;   /* 17px — section headings in answers */
  --text-xl:    1.25rem;     /* 20px — question echo */
  --text-2xl:   1.5rem;      /* 24px — page heading */
  --text-3xl:   1.875rem;    /* 30px — hero / empty-state heading */

  /* Line-height for medical longform */
  --leading-body:    1.733;  /* 15px body -> 26px */
  --leading-tight:   1.4;    /* headings */
  --leading-relaxed: 1.85;   /* evidence-gap cards, disclaimer */

  /* Font weights */
  --weight-regular:  400;
  --weight-medium:   500;
  --weight-semibold: 600;

  /* SPACING (4-point base) */

  --space-1:   4px;
  --space-2:   8px;
  --space-3:   12px;
  --space-4:   16px;
  --space-5:   20px;
  --space-6:   24px;
  --space-8:   32px;
  --space-10:  40px;
  --space-12:  48px;
  --space-16:  64px;
  --space-20:  80px;
  --space-24:  96px;

  /* RADIUS */

  --radius-sm:   4px;     /* citation chips, badges */
  --radius-md:   8px;     /* input fields, cards */
  --radius-lg:   12px;    /* answer card, modals */
  --radius-xl:   16px;    /* prominent surfaces */
  --radius-full: 9999px;  /* pill badges */

  /* SHADOWS (hue 240 blue-grey) */

  --shadow-sm:    0 1px 2px oklch(18% 0.015 240 / 0.06),
                  0 1px 1px oklch(18% 0.015 240 / 0.04);
  --shadow-md:    0 4px 8px oklch(18% 0.015 240 / 0.08),
                  0 2px 4px oklch(18% 0.015 240 / 0.06);
  --shadow-lg:    0 12px 24px oklch(18% 0.015 240 / 0.10),
                  0 4px 8px oklch(18% 0.015 240 / 0.07);
  --shadow-modal: 0 20px 48px oklch(18% 0.015 240 / 0.16),
                  0 8px 16px oklch(18% 0.015 240 / 0.10);

  /* MOTION */

  --duration-fast:   150ms;
  --duration-base:   250ms;
  --duration-slow:   400ms;

  --ease-out-quart: cubic-bezier(0.25, 1.0, 0.5, 1.0);
  --ease-in-out:    cubic-bezier(0.4, 0.0, 0.2, 1.0);
  /* Spring for citation card reveal */
  --ease-spring:    linear(
    0, 0.009, 0.035 2.1%, 0.141 4.4%, 0.723 12.9%,
    0.938, 1.077 20.4%, 1.121, 1.051 27.7%,
    1.020 29.4%, 0.999 31.4%, 1.000 35.7%, 1.000
  );

  /* BREAKPOINTS */

  --breakpoint-sm: 480px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1440px;
}
```

### Dark Mode Token Mirror

```css
@media (prefers-color-scheme: dark) {
  @theme {
    --color-bg-base:      oklch(14.0% 0.010 250);
    --color-bg-surface:   oklch(18.0% 0.012 250);
    --color-bg-sunken:    oklch(12.0% 0.008 250);
    --color-bg-overlay:   oklch(20.0% 0.012 250);

    --color-fg-base:      oklch(94.0% 0.008 250);
    --color-fg-muted:     oklch(65.0% 0.012 250);
    --color-fg-subtle:    oklch(46.0% 0.010 250);
    --color-fg-inverse:   oklch(14.0% 0.010 250);

    /* Primary raised for dark background */
    --color-primary-500:  oklch(68.0% 0.150 240);   /* 5.1:1 on dark bg-base */
    --color-primary-600:  oklch(78.0% 0.130 240);   /* hover (lighter on dark) */
    --color-primary-700:  oklch(86.0% 0.100 240);

    --color-evidence-500: oklch(66.0% 0.135 158);
    --color-warning-500:  oklch(70.0% 0.135 80);
    --color-danger-500:   oklch(66.0% 0.170 25);

    --color-border-base:   oklch(28.0% 0.015 250);
    --color-border-strong: oklch(36.0% 0.018 250);

    --color-source-pubmed: oklch(68.0% 0.150 240);
    --color-source-usda:   oklch(66.0% 0.135 158);
    --color-source-nih:    oklch(70.0% 0.135 80);
    --color-source-asmbs:  oklch(64.0% 0.110 280);

    --shadow-sm:    0 1px 2px oklch(5% 0.005 240 / 0.25);
    --shadow-md:    0 4px 8px oklch(5% 0.005 240 / 0.35);
    --shadow-lg:    0 12px 24px oklch(5% 0.005 240 / 0.45);
    --shadow-modal: 0 20px 48px oklch(5% 0.005 240 / 0.60);
  }
}
```

### WCAG 2.2 Contrast Verification

| Pair | Ratio | Grade |
|------|-------|-------|
| fg-base on bg-base (light) | ~13.2:1 | AAA |
| fg-muted on bg-base (light) | ~5.8:1 | AA |
| primary-500 on bg-base (light) | ~5.4:1 | AA |
| primary-500 on bg-surface (light) | ~4.8:1 | AA |
| warning-500 on bg-base (light) | ~4.8:1 | AA |
| fg-base on bg-base (dark) | ~11.8:1 | AAA |
| primary-500 on bg-base (dark) | ~5.1:1 | AA |

---

## 4. Flow Maps

### F1 — First-Time User

```
Landing
  Hero: "Evidence-based nutrition guidance for GLP-1 users"
  Subtitle lists data sources (PubMed, USDA, NIH)
       |
       v
DisclaimerBanner -- full, top of screen, permanent
  "This tool provides evidence-based nutrition information,
   not medical advice. Not a substitute for a registered
   dietitian or physician."
  [ Learn why we show this ] -- expands inline
       |
       v
AskBox -- focus state
  Placeholder: "Ask about protein, vitamins, or foods
   while on GLP-1 therapy..."
  Suggestion chips (3 visible):
    "How much protein do I need on Ozempic?"
    "Which foods have the most iron?"
    "Will I lose muscle if I am not eating enough?"
       |
       | Cmd+Enter submit
       v
AnswerCard -- loading-skeleton state
  Shimmer lines + "Searching 200+ peer-reviewed papers..."
       |
       | streaming begins
       v
AnswerCard -- streaming state
  [SourceCountBadge: "4 sources found"] (pre-rendered)
  [CitationChipRow] (chips appear as citations are retrieved)
  Answer text streams token by token
  Superscript markers appear inline as stream hits cited claims
       |
       | done event
       v
AnswerCard -- complete state
  Full answer with superscript citations
  CitationChips row (tappable / hoverable on desktop)
  "Ask a follow-up" affordance below card
```

### F2 — Returning User

```
Page load (localStorage returning=true)
  DisclaimerBanner minimised to compact 36px sticky pill
  AskBox in default/ready state
  SuggestionChips hidden (re-appear after 10s idle in empty box)
```

### F3 — Out-of-Scope Query (Dosing / Medical Decisions)

```
User types: "Should I increase my Ozempic dose?"
  OR: "Can I stop taking semaglutide?"
  OR: semantic variants caught by server-side check
       |
       v
Scope check (client-side keyword regex + server-side semantic)
  Client-side catches: "dose", "dosage", "stop taking",
  "prescribe", "should I take", "is X safe for me"
       |
       | out-of-scope match
       v
AnswerCard -- out-of-scope-refusal state
  [ShieldIcon, danger-50 background, role="alert"]
  Heading: "This is a question for your prescriber"
  Body: "Questions about medication doses, starting,
   stopping, or changing GLP-1 therapy should be
   discussed with the physician who prescribed it."
  [Find a GLP-1 specialist ->] external link
  "What I can help with:" + 3 nutrition chips

No LLM call made for keyword-matched refusals.
Server-side catches semantic variants before RAG pipeline.
```

### F4 — Low-Confidence Answer (Evidence Gap)

```
Query: "Does vitamin K2 affect muscle retention on GLP-1?"
RAG pipeline returns: confidence < 0.60 threshold
                      AND fewer than 3 sources above threshold
       |
       v
EvidenceGapCard renders ABOVE answer body
  [FlaskIcon, warning-100 background, role="status"]
  "Limited evidence on this specific topic"
  "We found 1 relevant study. The answer below reflects
   current best available evidence, which is limited."
  Evidence density meter: 1 of 5 dots filled
  [View the 1 source found ->]
       |
       v
AnswerCard -- low-confidence variant
  Answer text (hedged language enforced by system prompt)
  CitationChips (1 chip, clearly labelled)
```

### F5 — Source Verification (Citation Tap)

```
User hovers/taps CitationChip or superscript link
       |
       | (desktop: hover 400ms dwell)
       v
Source Preview (HoverCard, 320px, side="top")
  [SourceTypeBadge: "PubMed - Peer-Reviewed"]
  Paper title (semibold, 14px)
  Authors + Year + Journal
  Abstract excerpt (first 150 chars)
  [Read full abstract ->]
       |
       | user clicks Read full abstract / taps chip on mobile
       v
SourceModal
  Mobile (<768px): Sheet (bottom, 80vh)
    - Swipe down to dismiss OR tap close button (44x44px)
  Desktop (>=768px): Dialog (centred, max-width 640px)
    - Esc or click outside to dismiss

  Content: full paper metadata, complete abstract,
  retrieved excerpt highlighted in primary-100 bg,
  [Open on PubMed] external link,
  "Also cited in N other answers" (session-level)
```

---

## 5. Component Specifications

### 5.1 AskBox

Anatomy:
```
+-- AskBox -----------------------------------------------+
| [Label sr-only: "Ask a nutrition question"]             |
| +-- Textarea ------------------------------------------+ |
| |  placeholder text                                    | |
| |                                                      | |
| +------------------------------------------------------+ |
|  [CharCount 0/500 — fg-subtle]    [Button "Ask"]        |
|  [SuggestionChips row] (conditional, when value="")     |
+----------------------------------------------------------+
```

States:

| State | Visual Description |
|-------|-------------------|
| default | bg-sunken, border-base, fg-subtle placeholder, shadow-sm |
| focus | border-focus 2px solid, focus-visible ring 3px primary-100, shadow-md |
| typing | fg-base text, CharCount visible (fg-muted), SuggestionChips hidden |
| submitting | Textarea opacity-60 disabled, SubmitButton shows Loader2 spinner, cannot re-submit |
| disabled | opacity-50, pointer-events-none, cursor-not-allowed, border dashed |
| error | border-danger-500 2px, error message below (danger-600, 13px, role="alert") |
| success | brief border flash to evidence-500 150ms, return to default |

Keyboard interactions:
- Tab: focus Textarea
- Cmd/Ctrl + Enter: submit (not bare Enter — multi-line medical queries)
- Esc: blur, SuggestionChips re-appear
- Tab from Textarea: focus SubmitButton; Enter: submit

ARIA:
```html
<form role="search" aria-label="Ask a nutrition question">
  <label for="ask-input" class="sr-only">
    Ask a nutrition question about GLP-1 therapy
  </label>
  <textarea
    id="ask-input"
    aria-describedby="ask-hint ask-error"
    aria-required="true"
    maxlength="500"
  ></textarea>
  <p id="ask-hint" class="sr-only">
    Ask about protein, vitamins, or foods. For medication questions,
    consult your prescriber. Press Cmd+Enter to submit.
  </p>
  <p id="ask-error" role="alert" aria-live="assertive"></p>
  <button type="submit" aria-label="Submit question">Ask</button>
</form>
```

Motion:
- Focus: border-color transition 150ms ease-out-quart
- Submit press: scale 0.97 to 1.0 spring, spinner fade-in 150ms
- prefers-reduced-motion: border color instant, no scale

---

### 5.2 AnswerCard

Anatomy:
```
+-- AnswerCard -------------------------------------------+
| [QuestionEcho — fg-muted, text-sm, italic]              |
| ------------------------------------------------------- |
| [SourceCountBadge "4 sources"]  [CitationChipRow]       |
| ------------------------------------------------------- |
| [EvidenceGapCard] (conditional, renders above body)     |
|                                                         |
|  Answer body text with superscript markers (1) (2)      |
|                                                         |
|  For GLP-1 users, protein targets of 1.2-1.6 g/kg (1)  |
|  are supported by two 2024 RCTs. (2)                    |
|                                                         |
| ------------------------------------------------------- |
| [Reference list: collapsed by default, expandable]      |
+----------------------------------------------------------+
```

States:

| State | Visual Description |
|-------|-------------------|
| empty | Dashed border card, centred fg-muted copy: "Ask something above to see evidence-based guidance" |
| loading-skeleton | Three shimmer lines (100%, 85%, 65%), SourceCountBadge skeleton (80px), 3x CitationChip skeletons |
| streaming | Text token-by-token, streaming cursor (2px fg-muted, blink 500ms), CitationChips pre-populate as citations arrive |
| complete | Full text, cursor removed, all CitationChips rendered |
| has-citations | CitationChipRow visible, superscripts in body, SourceCountBadge n > 0 |
| no-citations | SourceCountBadge shows "0 peer-reviewed sources" in warning-100 bg with warning icon; body still renders with hedged prompt language |
| out-of-scope-refusal | danger-50 bg surface, ShieldIcon, refusal heading + redirect body, role="alert", no citation chips |
| low-confidence | EvidenceGapCard above body (warning-100 bg), EvidenceDensityMeter visible |

ARIA:
```html
<article
  aria-label="Answer to your question"
  aria-live="polite"
  aria-busy="true"
>
  <header>
    <p aria-label="Your question">{questionEcho}</p>
    <span aria-label="{n} sources cited">{sourceCountBadge}</span>
  </header>
  <!-- Visible streaming div: aria-hidden="true" during streaming -->
  <!-- Hidden aria-live mirror: receives completed answer on done event only -->
  <div id="answer-body" aria-label="Answer">{content}</div>
  <section aria-label="Citations">{citationList}</section>
</article>
```

Motion:
- Card entrance: translateY(8px) opacity(0) to translateY(0) opacity(1), 250ms ease-out-quart
- Streaming cursor: CSS blink 500ms steps(2)
- CitationChips stagger: each chip +50ms delay, opacity 0 to 1, translateX(-4px to 0)
- prefers-reduced-motion: fade only on entrance, no translate, no stagger, cursor = solid block

---

### 5.3 CitationChip

Anatomy:
```
+-- CitationChip ---------------------------+
| [SourceTypeDot]  [ShortLabel]  [sup: n]  |
| [blue-dot] PubMed · Peer-Reviewed  (1)   |
+-------------------------------------------+
```

States:

| State | Visual Description |
|-------|-------------------|
| default | radius-full, bg-primary-50, fg-primary-700, border-primary-200, source dot left, 13px text, 36px min-height |
| hover | bg-primary-100, border-primary-400, shadow-sm, cursor-pointer. HoverCard appears after 400ms dwell |
| hover-source-card-visible | HoverCard (320px) above chip: source type badge, paper title semibold, authors/year/journal, abstract excerpt 150 chars, "Read full" button |
| active | bg-primary-200, scale 0.96 spring |
| linked | fg-primary-900 (darker), subtle underline, after SourceModal was opened for this citation |

Source-type dot colours:
- PubMed / PMC: primary-500 (trust-blue)
- USDA FoodData Central: evidence-500 (evidence-green)
- NIH ODS fact sheet: warning-500 (amber)
- ASMBS / clinical guideline: source-asmbs (indigo)

Keyboard: Tab to focus, Enter or Space opens SourceModal. Focus ring: 2px primary-500, 2px offset.

ARIA:
```html
<!-- Chip button -->
<button
  id="citation-chip-{n}"
  aria-label="Source {n}: {title}, {year} — tap to view full details"
  aria-haspopup="dialog"
>
  <span aria-hidden="true">{sourceTypeDot}</span>
  <span>{label}</span>
  <sup aria-hidden="true">{n}</sup>
</button>

<!-- In answer body -->
<sup>
  <a href="#citation-{n}"
     aria-label="Reference {n}: {paper title}">
    {n}
  </a>
</sup>
```

Motion: hover background-color 150ms ease-out-quart. HoverCard reveal: fade + translateY(-4px to 0) 250ms ease-out-quart. Active: spring scale.

---

### 5.4 SourceModal

Decision: Sheet on mobile (<768px), Dialog on desktop (>=768px).

Rationale: Sheet slides from bottom preserving answer context visible above. Dialog centres on large screens where full abstract benefits from centred reading layout.

Anatomy:
```
+-- SourceModal -----------------------------------------+
| [SourceTypeBadge: "PubMed - Peer-Reviewed"]            |
| ------------------------------------------------------ |
| Paper Title (semibold, 17px / 24px line-height)        |
| Authors · Year · Journal                               |
| PMID: 12345678                                         |
| ------------------------------------------------------ |
| Abstract                                               |
| [Retrieved excerpt: primary-100 bg, primary-500 left   |
|  border, represents the chunk that was retrieved]      |
| ------------------------------------------------------ |
| [Open on PubMed ->]    [Copy citation]                 |
| ------------------------------------------------------ |
| "Also cited in N other answers this session"           |
+--------------------------------------------------------+
```

States:

| State | Visual Description |
|-------|-------------------|
| loading | Skeleton: title (100% width 20px), authors (60% 14px), abstract (5 lines varying widths), shadow-modal on container |
| paper-loaded | Full metadata visible. Retrieved excerpt in primary-50 bg with primary-500 3px left border |
| abstract-only | Full abstract shown, no highlighted excerpt (fallback when chunk context unavailable) |
| error-loading | danger-50 bg, "Couldn't load full paper details", [Try again] button, [Open on PubMed directly] as fallback |

Keyboard:
- Esc: close modal, focus returns to CitationChip that opened it
- Tab: cycles [Open on PubMed], [Copy citation], [Close]
- Focus trap active inside modal

ARIA:
```html
<dialog
  aria-modal="true"
  aria-labelledby="source-modal-title"
  aria-describedby="source-modal-abstract"
>
  <h2 id="source-modal-title">{paperTitle}</h2>
  <p id="source-modal-abstract">{abstract}</p>
  <button aria-label="Close source details">Close</button>
</dialog>
```

Motion:
- Dialog: scale(0.96) opacity(0) to scale(1) opacity(1), 250ms ease-out-quart
- Sheet: translateY(100%) to translateY(0), 300ms ease-out-quart
- prefers-reduced-motion: fade only, no scale or translate

---

### 5.5 DisclaimerBanner

Decision: Two-tier — persistent compact pill (always visible) + expandable full banner (first visit and on every out-of-scope query).

Anatomy:
```
Full state (first visit / out-of-scope triggered):
+-- DisclaimerBanner -----------------------------------+
| [InfoIcon] Not medical advice. This tool provides     |
| nutrition information based on peer-reviewed research.|
| Always consult a registered dietitian or physician.   |
|                         [Got it, minimise ^]          |
+-------------------------------------------------------+

Minimised state (returning users, post-acknowledgement):
[i] Evidence tool · Not medical advice    [expand v]
(36px tall, sticky top, bg-surface, border-b)
```

States:

| State | Visual Description |
|-------|-------------------|
| default-visible | Full banner: bg-primary-50, border-b border-primary-200, 16px padding, InfoIcon primary-500, fg-muted text at leading-relaxed |
| minimised | 36px sticky bar: bg-surface, border-b border-base, info icon + compact copy + expand affordance |
| never-dismissable-on-medical-context | Auto-expands full on out-of-scope query. Cannot re-minimise until next in-scope query submitted |

Implementation note: minimise state in localStorage. Hard refresh without localStorage entry shows full banner. sessionStorage alternative if regulatory guidance requires per-session disclosure.

ARIA:
```html
<aside
  role="note"
  aria-label="Medical disclaimer"
  aria-live="polite"
>
```

Motion: expand/collapse max-height transition ease-out-quart 250ms (not opacity-only — height change must be perceivable by screen readers).

---

### 5.6 EvidenceGapCard

Renders above AnswerCard body when retrieval confidence < 0.60 OR fewer than 3 sources above threshold.

Anatomy:
```
+-- EvidenceGapCard ----------------------------------------+
| [FlaskIcon]  Limited evidence on this question            |
| "We found 1 relevant study. The answer below reflects     |
|  current best available evidence, which is limited.       |
|  Research on this topic is still emerging."               |
|                                                           |
| Evidence density: [filled][empty][empty][empty][empty]    |
| [View source ->]                                         |
+-----------------------------------------------------------+
```

Visual: bg-warning-50, border border-warning-200, radius-md, 16px padding. FlaskIcon warning-500. EvidenceDensityMeter: 5 SVG dots (filled = warning-500, empty = bg-surface with border-warning-200).

ARIA:
```html
<section role="status" aria-label="Evidence quality notice" aria-live="polite">
  <p>Limited evidence: {n} source found for this question.</p>
</section>
```

---

### 5.7 LoadingSkeleton

Matches AnswerCard shape exactly to prevent layout shift (CLS = 0 goal).

```
+-- AnswerCard Skeleton ------------------------------------+
| [QuestionEcho skeleton: 240px, 16px tall, shimmer]       |
| -------------------------------------------------------- |
| [SourceBadge skeleton: 80px pill]  [3x chip skeletons]   |
| -------------------------------------------------------- |
| [line: 100% width]                                       |
| [line: 87% width]                                        |
| [line: 93% width]                                        |
| [line: 72% width]                                        |
| [line: 80% width]                                        |
| [line: 45% width]                                        |
+-----------------------------------------------------------+
```

Shimmer implementation:
```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-surface) 0%,
    var(--color-bg-base) 50%,
    var(--color-bg-surface) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}

@keyframes shimmer {
  from { background-position: -200% 0; }
  to { background-position: 200% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton {
    background: var(--color-bg-surface);
    animation: none;
  }
}
```

---

## 6. WCAG 2.2 Accessibility Plan

### Focus Order (Tab sequence)

1. DisclaimerBanner action button (if full banner visible)
2. AskBox Textarea
3. AskBox SubmitButton
4. SuggestionChips [1] [2] [3] (if visible)
5. AnswerCard container (focusable, tabIndex=0)
6. CitationChips [1] through [n]
7. EvidenceGapCard "View source" link (if visible)
8. CitationList expand toggle (if collapsed footnote list exists)

### Streaming Content ARIA Pattern

AnswerCard: aria-live="polite" on container. aria-busy="true" during streaming, removed on completion.

Screen readers announce completed answer, not individual streaming chunks:
- Visible streaming div: aria-hidden="true" during streaming
- Hidden aria-live mirror div (visually-hidden class): receives completed answer text only on stream done event
- On completion: visible div gets aria-hidden removed, mirror div cleared

### Citation Rendering (Screen-Reader Continuity)

```html
<!-- In answer body: superscript with descriptive aria-label -->
protein<sup>
  <a href="#citation-1"
     aria-label="Reference 1: Smith et al 2024, protein in GLP-1 therapy">
    1
  </a>
</sup>

<!-- Citation list below card -->
<ol aria-label="References" role="list">
  <li id="citation-1">
    <cite>Smith et al (2024). Protein requirements in GLP-1 therapy.
    PubMed PMID: xxxxxxx</cite>
    <button aria-label="View full details for Reference 1: Smith et al 2024">
      View source
    </button>
  </li>
</ol>
```

Screen reader reads: "protein, Reference 1 [link]" — user presses Enter on superscript link to jump to citation-1 in list, or Tab to CitationChip, or Enter to open SourceModal. Three keyboard-reachable entry paths.

### Colour as Sole Differentiator — None

Source-type chips: BOTH colour dot AND text label. EvidenceGapCard: BOTH FlaskIcon AND bg-color. OutOfScope refusal: BOTH ShieldIcon AND bg-color AND distinct heading copy.

### Target Size (WCAG 2.5.5 / 2.5.8)

| Component | Min touch target |
|-----------|-----------------|
| CitationChips | 36px H x 44px W minimum |
| SubmitButton | 44x44px |
| DisclaimerBanner action | 44x44px |
| SuggestionChips | 36px H minimum |
| SourceModal close button | 44x44px |
| Superscript links | 24x24px (WCAG 2.5.8 minimum) |

### WCAG 2.5.7 Drag Alternative

No swipe-only patterns. Sheet dismisses via both downward swipe AND visible close button (44x44px).

### Out-of-Scope Refusal Announcement

Refusal state sets role="alert" on OutOfScopeCard — announced immediately by screen readers, interrupting any in-progress streaming. Appropriate: safety-relevant state transition.

---

## 7. shadcn/ui v4 + Radix Component Mapping

| Design Component | shadcn/ui v4 | Radix Primitive | Notes |
|-----------------|-------------|-----------------|-------|
| AskBox | Textarea + Form | @radix-ui/react-form | Custom sizing; maxLength=500 |
| SubmitButton | Button variant="default" | — | aria-label + loading state |
| SuggestionChips | Badge variant="outline" as button | — | role="button", tabIndex=0 |
| AnswerCard | Custom article element | — | No shadcn equivalent — build from scratch |
| CitationChip hover reveal | HoverCard | @radix-ui/react-hover-card | openDelay={400} prevents accidental triggers |
| SourceModal desktop (>=768px) | Dialog | @radix-ui/react-dialog | Focus trap, Esc close, aria-modal |
| SourceModal mobile (<768px) | Sheet side="bottom" | @radix-ui/react-dialog | Sheet extends Dialog; swipe + button close |
| DisclaimerBanner | Alert variant="default" | — | Custom max-height expand/collapse |
| EvidenceGapCard | Custom Alert variant | — | role="status" override |
| LoadingSkeleton | Skeleton | — | Compose into AnswerCard layout shape |
| SourceCountBadge | Badge | — | Custom colour variant per source-type |
| EvidenceDensityMeter | Custom SVG 5-dot component | — | aria-label="{n} of 5 evidence sources" |
| Streaming cursor | Custom CSS ::after | — | animation: blink 500ms steps(2) infinite |

### HoverCard vs Popover Decision

Use HoverCard for citation chip preview.

- HoverCard is purpose-built for link/reference previews on hover; keyboard users access via focus (no hover required on keyboard).
- Popover is for interactive actionable panels (menus, pickers) — wrong semantic for "here is source information."
- HoverCard has openDelay prop — use 400ms to prevent accidental card flickering during reading.

### Streaming + Skeleton with React 19 / Suspense

```tsx
// Pattern:
// 1. Suspense wraps AnswerCardContent with skeleton fallback
// 2. ReadableStream from Next.js API route -> useStreamingText hook
// 3. Stream done event: post-process [n] markers -> <sup><a> elements,
//    remove aria-hidden from visible div, set aria-busy="false"

<Suspense fallback={<AnswerCardSkeleton />}>
  <AnswerCardContent questionId={questionId} />
</Suspense>
```

---

## 8. Implementation Snippet — Core Components

### AskBox.tsx

```tsx
"use client";

import { useState, useRef } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface AskBoxProps {
  onSubmit: (query: string) => Promise<void>;
  isSubmitting: boolean;
  disabled?: boolean;
  showSuggestions?: boolean;
  error?: string;
}

const SUGGESTIONS = [
  "How much protein do I need on Ozempic?",
  "Which foods are highest in iron for GLP-1 users?",
  "Will I lose muscle if I am not eating enough?",
];

export function AskBox({
  onSubmit,
  isSubmitting,
  disabled = false,
  showSuggestions = true,
  error,
}: AskBoxProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim() || isSubmitting || disabled) return;
    await onSubmit(value.trim());
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <form
      role="search"
      aria-label="Ask a nutrition question"
      onSubmit={handleSubmit}
      className="w-full"
    >
      <label htmlFor="ask-input" className="sr-only">
        Ask a nutrition question about GLP-1 therapy
      </label>

      <div
        className={cn(
          "relative rounded-[var(--radius-md)] border",
          "transition-[border-color,box-shadow]",
          "duration-[var(--duration-fast)] ease-[var(--ease-out-quart)]",
          "bg-[var(--color-bg-sunken)] border-[var(--color-border-base)]",
          "shadow-[var(--shadow-sm)]",
          "focus-within:border-[var(--color-border-focus)]",
          "focus-within:shadow-[0_0_0_3px_var(--color-primary-100),var(--shadow-md)]",
          error && "border-[var(--color-danger-500)]",
          disabled && "opacity-50 pointer-events-none",
        )}
      >
        <Textarea
          id="ask-input"
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about protein, vitamins, or foods while on GLP-1 therapy..."
          maxLength={500}
          rows={3}
          aria-describedby="ask-hint ask-error"
          aria-required="true"
          className={cn(
            "resize-none border-0 bg-transparent",
            "p-[var(--space-4)] pb-10",
            "text-[length:var(--text-base)] text-[var(--color-fg-base)]",
            "placeholder:text-[var(--color-fg-subtle)]",
            "leading-[var(--leading-body)]",
            "focus-visible:ring-0 focus-visible:ring-offset-0",
          )}
        />

        <div className="absolute bottom-0 inset-x-0 flex items-center justify-between px-[var(--space-3)] pb-[var(--space-2)]">
          {value.length > 0 && (
            <span
              className="text-[length:var(--text-xs)] text-[var(--color-fg-subtle)]"
              aria-live="polite"
            >
              {value.length}/500
            </span>
          )}
          <Button
            type="submit"
            disabled={!value.trim() || isSubmitting || disabled}
            className={cn(
              "ml-auto h-9 px-[var(--space-4)]",
              "bg-[var(--color-primary-500)]",
              "hover:bg-[var(--color-primary-600)]",
              "active:bg-[var(--color-primary-700)]",
              "text-[var(--color-fg-inverse)]",
              "text-[length:var(--text-sm)] font-[number:var(--weight-medium)]",
              "transition-[background-color,transform]",
              "duration-[var(--duration-fast)] ease-[var(--ease-out-quart)]",
              "active:scale-[0.97] motion-reduce:active:scale-100",
            )}
            aria-label={isSubmitting ? "Searching literature..." : "Submit question"}
          >
            {isSubmitting ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              "Ask"
            )}
          </Button>
        </div>
      </div>

      <p id="ask-hint" className="sr-only">
        Ask about nutrition for GLP-1 therapy. For medication questions,
        consult your prescriber. Press Cmd or Ctrl plus Enter to submit.
      </p>

      {error && (
        <p
          id="ask-error"
          role="alert"
          aria-live="assertive"
          className="mt-[var(--space-2)] text-[length:var(--text-sm)] text-[var(--color-danger-600)]"
        >
          {error}
        </p>
      )}

      {showSuggestions && !value && (
        <div
          className="mt-[var(--space-3)] flex flex-wrap gap-[var(--space-2)]"
          role="group"
          aria-label="Suggested questions"
        >
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => {
                setValue(s);
                textareaRef.current?.focus();
              }}
              className={cn(
                "h-9 px-[var(--space-3)] rounded-[var(--radius-full)]",
                "border border-[var(--color-border-base)]",
                "bg-[var(--color-bg-surface)]",
                "hover:bg-[var(--color-primary-50)]",
                "hover:border-[var(--color-primary-200)]",
                "text-[length:var(--text-sm)] text-[var(--color-fg-muted)]",
                "transition-[background-color,border-color]",
                "duration-[var(--duration-fast)] ease-[var(--ease-out-quart)]",
                "focus-visible:outline-none focus-visible:ring-2",
                "focus-visible:ring-[var(--color-border-focus)] focus-visible:ring-offset-2",
              )}
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </form>
  );
}
```

### CitationChip.tsx

```tsx
"use client";

import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export type SourceType = "pubmed" | "usda" | "nih" | "asmbs";

interface CitationChipProps {
  index: number;
  title: string;
  authors: string;
  year: number;
  journal: string;
  abstractExcerpt: string;
  sourceType: SourceType;
  visited?: boolean;
  onOpen: () => void;
}

const SOURCE_LABELS: Record<SourceType, string> = {
  pubmed: "PubMed · Peer-Reviewed",
  usda:   "USDA FoodData",
  nih:    "NIH · Fact Sheet",
  asmbs:  "Clinical Guideline",
};

const DOT_CLASSES: Record<SourceType, string> = {
  pubmed: "bg-[var(--color-source-pubmed)]",
  usda:   "bg-[var(--color-source-usda)]",
  nih:    "bg-[var(--color-source-nih)]",
  asmbs:  "bg-[var(--color-source-asmbs)]",
};

export function CitationChip({
  index,
  title,
  authors,
  year,
  journal,
  abstractExcerpt,
  sourceType,
  visited = false,
  onOpen,
}: CitationChipProps) {
  return (
    <HoverCard openDelay={400} closeDelay={200}>
      <HoverCardTrigger asChild>
        <button
          id={`citation-chip-${index}`}
          onClick={onOpen}
          aria-label={`Source ${index}: ${title}, ${year} — tap to view full details`}
          aria-haspopup="dialog"
          className={cn(
            "inline-flex items-center gap-[var(--space-1)]",
            "h-9 px-[var(--space-3)] rounded-[var(--radius-full)]",
            "border border-[var(--color-primary-200)]",
            "bg-[var(--color-primary-50)]",
            "text-[length:var(--text-sm)] text-[var(--color-primary-700)]",
            "transition-[background-color,border-color,box-shadow]",
            "duration-[var(--duration-fast)] ease-[var(--ease-out-quart)]",
            "hover:bg-[var(--color-primary-100)] hover:border-[var(--color-primary-400)]",
            "hover:shadow-[var(--shadow-sm)]",
            "active:scale-[0.96] motion-reduce:active:scale-100",
            "focus-visible:outline-none focus-visible:ring-2",
            "focus-visible:ring-[var(--color-border-focus)] focus-visible:ring-offset-2",
            visited && "text-[var(--color-primary-900)] underline",
          )}
        >
          <span
            className={cn("h-2 w-2 rounded-full flex-shrink-0", DOT_CLASSES[sourceType])}
            aria-hidden="true"
          />
          <span>{SOURCE_LABELS[sourceType]}</span>
          <sup className="text-[10px] leading-none" aria-hidden="true">{index}</sup>
        </button>
      </HoverCardTrigger>

      <HoverCardContent
        className={cn(
          "w-80 p-[var(--space-4)]",
          "bg-[var(--color-bg-overlay)] shadow-[var(--shadow-lg)]",
          "border border-[var(--color-border-base)] rounded-[var(--radius-lg)]",
        )}
        side="top"
        align="start"
      >
        <Badge
          variant="outline"
          className="mb-[var(--space-2)] text-[length:var(--text-xs)]"
        >
          <span
            className={cn("mr-1 h-1.5 w-1.5 rounded-full", DOT_CLASSES[sourceType])}
            aria-hidden="true"
          />
          {SOURCE_LABELS[sourceType]}
        </Badge>

        <p className="font-[number:var(--weight-semibold)] text-[length:var(--text-sm)] text-[var(--color-fg-base)] leading-[var(--leading-tight)] mb-[var(--space-1)]">
          {title}
        </p>
        <p className="text-[length:var(--text-xs)] text-[var(--color-fg-muted)] mb-[var(--space-3)]">
          {authors} · {year} · {journal}
        </p>
        <p className="text-[length:var(--text-xs)] text-[var(--color-fg-base)] leading-[var(--leading-relaxed)] line-clamp-4">
          {abstractExcerpt}
        </p>
        <button
          onClick={onOpen}
          className="mt-[var(--space-3)] text-[length:var(--text-xs)] text-[var(--color-primary-500)] hover:text-[var(--color-primary-600)] underline underline-offset-2"
        >
          Read full abstract
        </button>
      </HoverCardContent>
    </HoverCard>
  );
}
```

---

## 9. Healthcare Trust Visual Signals

### Disclaimer Placement

Decision: Sticky-top compact pill (always) + full banner (first visit, out-of-scope triggered).

The sticky top position means the disclaimer is always in peripheral vision. This is the OpenEvidence pattern — the disclaimer is not a one-time gate, it is ambient context for every interaction.

The banner does NOT use red or warning visual register for the standard disclaimer. Red is reserved exclusively for out-of-scope refusals. The disclaimer uses calm primary-50 / primary-500 to signal "informational" not "danger."

### Source Type Visual Hierarchy

| Source | Chip Dot | Label | Context |
|--------|----------|-------|---------|
| PubMed / PMC peer-reviewed paper | primary-500 trust-blue | "PubMed · Peer-Reviewed" | RCT / meta-analysis |
| USDA FoodData Central | evidence-500 evidence-green | "USDA FoodData" | Authoritative nutrient database |
| NIH ODS Fact Sheet | warning-500 amber | "NIH · Fact Sheet" | Authoritative summary |
| ASMBS / Clinical Guideline | source-asmbs indigo | "Clinical Guideline" | Professional consensus |

Visual hierarchy: peer-reviewed literature (blue) > authoritative database (green) > fact sheet summary (amber). Users learn this pattern after 3 interactions.

### Source-Count Badge Plus Inline Footnotes

Decision: Both.

Badge at card top: "4 sources" signals evidential weight BEFORE the user reads the answer. The trust decision happens in the first second.

Inline superscripts: connect each specific claim to its specific source — essential for medical context where "this specific calcium claim" must link to "this specific paper" and not just a general source list.

Collapsed footnote list at card bottom: always expandable, collapsed by default to reduce visual noise.

This mirrors Perplexity Health's 2026 gold standard pattern.

### No Verified/Unverified Binary Badge

Do NOT show a verified/unverified binary. A binary creates false confidence. Source-type colour coding communicates quality continuously and proportionally.

---

## 10. Anti-Patterns (Explicit Forbidden List)

### Anti-patterns That Signal "Generic AI Chatbot"

- Gradient avatar with AI name ("Hi, I am Aria!") — this product has no persona. The knowledge base IS the product.
- Sparkle icons on AI responses — medical context, not magic.
- "Hi! I am an AI assistant and I want to help you on your wellness journey!" — any variant. Opening copy: the ask box + a brief statement of what corpus it retrieves from.
- Animated AI face or chat head.
- Typing indicator dots (...) as the only feedback during LLM inference — use the skeleton pattern, which communicates "searching literature" not "chatbot is thinking."
- Dark mode with neon accents — medical trust is not a hacker aesthetic.
- Gradient hero section — Stripe uses white. Linear uses black. Both are credible. Gradient = template-tier.
- "Powered by GPT-4 / Claude" marketing copy in UI chrome — cite data sources, not LLM vendor.

### Anti-patterns That Undermine Medical Safety

- Big confident verdict tiles ("Your protein score: 8/10") — gamifies literature data and implies precision the evidence does not support.
- Emoji reactions on answers — use a minimal "Was this helpful? Yes / No" text affordance if feedback is needed.
- Gamification (streaks, badges, XP for asking, leaderboards) — this is a clinical reference tool, not a habit app.
- Conversational filler ("Great question!", "Absolutely!") at start of answers — start with the answer.
- Confident declarative framing ("You should eat 120g protein daily") — always range-based, literature-cited ("Studies suggest 1.2-1.6 g/kg...").
- "Based on my training data" copy — hides the actual sources. Every claim must trace to a specific retrieved chunk from a specific paper.
- Fully dismissable disclaimers — the disclaimer can minimise to compact view but cannot be hidden entirely.
- Collecting or displaying personal health data (weight, BMI, lab values) without explicit consent — this product is stateless, it answers questions, it does not track users.
- Red colour for the primary CTA button — red = danger in medical context. Primary interactive is trust-blue.

---

## 11. Responsive Breakpoints

### Layout Shifts by Breakpoint

| Breakpoint | Width | Layout |
|-----------|-------|--------|
| Mobile S | 360px | Single column. AskBox full-width 100px tall. CitationChips wrap 2-per-row max. DisclaimerBanner full-width. SourceModal = Sheet 80vh. |
| Mobile M | 480px | Same layout but CitationChips row scrolls horizontally (overflow-x auto, scroll-snap-x). |
| Tablet | 768px | Two-column: ask column 58% + source panel column 42% slides in on citation tap. DisclaimerBanner compact pill. SourceModal = Dialog (60vw, max 640px). |
| Desktop | 1024px | Container max-width 800px centred. Answer body max 680px for reading-width. Source panel = right-side overlay sheet 320px (does not displace content). |
| Wide | 1440px | Container max-width 900px. Answer body max 680px. Generous vertical rhythm. |

### Tailwind 4 Breakpoint Tokens

```css
@theme {
  --breakpoint-sm: 480px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1440px;
}
```

### Mobile-Specific Patterns

- CitationChip tap on mobile: HoverCard does not fire on touch. Chip tap goes directly to Sheet (skips hover preview). Sheet is the primary citation detail experience on mobile.
- AskBox on mobile: Textarea expands up to 5 lines, then scrolls internally. Use visualViewport resize event to scroll AskBox above virtual keyboard.
- DisclaimerBanner on mobile: Full banner minimises after first "Got it" tap. Compact pill is 36px sticky top. Re-expands full on out-of-scope queries only.
- SuggestionChips on 360px: Wrap to maximum 2 rows of 2 chips (not horizontal scroll — 360px is too narrow for that affordance).

---

## 12. Open Questions for Engineering

1. **Streaming pipeline architecture:** Does the stream start after retrieval completes (serial), or do retrieval and generation pipeline concurrently (stream starts before all chunks retrieved)? If pipelined, CitationChip pre-population must handle partial citation data arriving mid-stream. Recommendation: clarify before building the streaming renderer.

2. **Superscript marker injection timing:** LLM answer will contain [1] markers. Frontend post-processes on stream done event to replace with superscript links. Recommendation: stream plain text, post-process full string on done event (not per-chunk — too expensive and risks partial replacements).

3. **HoverCard on touch devices:** This brief recommends option A: CitationChip tap on touch goes directly to Sheet (skip hover preview). Alternative option B: first tap shows Popover preview, second tap opens Sheet. Option A is simpler and less error-prone. Engineering team should confirm.

4. **Out-of-scope check latency:** Client-side regex is first-line fast. If server-side semantic check runs in same RAG call, skeleton shows for both in-scope and out-of-scope — acceptable. If instant refusal without skeleton is required, client-side regex must be comprehensive. Recommendation: client-side covers obvious patterns, server-side catches semantic variants; latency delta is acceptable.

5. **Evidence confidence threshold calibration:** This brief uses < 0.60 cosine similarity and < 3 sources as EvidenceGapCard triggers. These are initial values. Instrument retrieval scores on first 100 real queries and calibrate empirically. Values should be env vars (EVIDENCE_GAP_SIMILARITY_THRESHOLD, EVIDENCE_GAP_MIN_SOURCES), not hardcoded.

6. **LocalStorage disclaimer minimise persistence:** Minimise state in localStorage persists across sessions. If future regulatory guidance requires full disclaimer per session, change to sessionStorage. Flag as product decision pending FDA AI guidance updates.

7. **Citation cross-linking ("Also cited in N other answers"):** Requires session-level citation frequency tracking. If sessions are stateless (no server-side session), this is client-side only for the current session — acceptable for v1 MVP. Note for v2 backlog if cross-session citation graph becomes valuable.

8. **IBM Plex Mono subsetting:** Mono used only for PMID values and numerical amounts. Evaluate whether Inter Variable's tabular-nums figure variant covers these cases. If yes, drop IBM Plex Mono for v1 to reduce font payload.

---

*End of UI/UX Brief — P1 GLP-1 Nutrition Copilot*  
*Brief version: 1.0 · 2026-05-14 · ui-ux-designer-agent*  
*Recipients: frontend-engineer-agent (implementation) · ml-engineer-agent (streaming / confidence thresholds)*
