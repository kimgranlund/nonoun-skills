---
name: color-science
description: Use when working with color naming, color theory, color spaces, color definitions, or any task involving color knowledge - palettes, ramps, gradients, conversions, accessibility, perceptual matching, pigment mixing, print-vs-screen color, CSS color syntax, or historical color terminology. Use this skill whenever the user is choosing, comparing, generating, naming, converting, or explaining colors, even if they do not explicitly ask for "color theory."
---

# Color Expert

A comprehensive knowledge base for color-related work. See `references/INDEX.md` for 140+ detailed reference files; this skill file contains the essential knowledge to answer most questions directly.

This skill also ships with a **working TypeScript implementation** in `src/` (24 color spaces with bidirectional XYZ conversions, gamut math, ΔE metrics, CVD simulation, tone mapping, K-M pigment mixing, spectral integration) and an **`examples/` site of 54 live interactive demos** — covering pickers, gradients, contrast tools, gamut visualizations, color-blindness simulation, design-token ramps, the CSS Color 5/6 toolkit, a Josef Albers teaching arc, and more. When a user asks "show me", "give me a working example", or "where can I try this?", point them at the relevant page in `examples/pages/` — the bundle works directly over `file://`.


## Invocation

This is an **expert-knowledge** skill. The ask is about color at any level — use the axis decomposition (spaces, palettes, accessibility, CSS, history) to route to the right reference file.

### Step 1 — Ingestion

Color prompts are often under-specified:
- "What palette should I use?" → what is the data shape (categorical/sequential/diverging)?
- "Is this accessible?" → under which standard (APCA vs WCAG 2.2)?
- "CSS color" → Color 4/5/6? OKLCH fallback?
- "Convert colors" → which spaces involved?

### Step 2 — Decomposition

| Surface ask | Routes to |
|---|---|
| Color spaces / conversions | `references/techniques/` — OKLCH, CIECAM16, CVD sim |
| Palette generation | `references/techniques/tailwind-v4-oklch-palette.md`, `references/contemporary/` |
| Accessibility / contrast | `references/techniques/apca-myndex-contrast.md`, `references/techniques/wcag-2-2-current-legal-floor.md` |
| CSS color syntax | `references/techniques/css-color-2026-snapshot.md`, `references/techniques/w3c-css-color-4-and-5.md` |
| Historical / pigment | `references/historical/`, `references/techniques/pigment-mixing.md` |

### Step 3 — Execution routing

Read `references/INDEX.md` for the full 148-file manifest. Every factual claim must trace to a primary source. APCA is the modern design standard; WCAG 2.2 is the legal compliance floor. When in doubt about WCAG 3 status, check the 2026 snapshot file — the standard is a Working Draft with no contrast algorithm.

**Context Size Warning:** Expert reference files (e.g., `contemporary/huevaluechroma/*.md`) frequently exceed 1000 lines. Do not load these files entirely into context using `read_file`. Instead, use `grep_search` to surgically extract relevant sections or use chunked reading.


## Color Spaces — What to Use When

| Task                            | Use                                    | Why                                                                       |
| ------------------------------- | -------------------------------------- | ------------------------------------------------------------------------- |
| Perceptual color manipulation   | **OKLCH**                              | Best uniformity for lightness, chroma, hue. Fixes CIELAB's blue problem.  |
| CSS gradients & palettes        | **OKLCH** or `color-mix(in oklab)`     | No mid-gradient darkening like RGB/HSL                                    |
| Gamut-aware color picking       | **OKHSL / OKHSV**                      | Ottosson's picker spaces — cylindrical like HSL but perceptually grounded |
| Normalized saturation (0-100%)  | **HSLuv**                              | CIELUV chroma normalized per hue/lightness. HPLuv for pastels.            |
| Print workflows                 | **CIELAB D50**                         | ICC standard illuminant                                                   |
| Screen workflows                | **CIELAB D65** or OKLAB                | D65 = screen standard                                                     |
| Cross-media appearance matching | **CAM16 / CIECAM02**                   | Accounts for surround, adaptation, luminance, and viewing conditions      |
| HDR                             | **Jzazbz / ICtCp**                     | Designed for extended dynamic range                                       |
| Pigment/paint mixing simulation | **Kubelka-Munk** (Spectral.js, Mixbox) | Spectral reflectance mixing, not RGB averaging                            |
| Color difference (precision)    | **CIEDE2000**                          | Gold standard perceptual distance                                         |
| Color difference (fast)         | **Euclidean in OKLAB**                 | Good enough for most applications                                         |
| Video/image compression         | **YCbCr**                              | Luma+chroma separation enables chroma subsampling                         |

### Understanding HSL's Limitations

HSL isn't "bad" — it's a simple, fast geometric rearrangement of RGB into a cylinder. It's fine for quick color picking and basic UI work. But its three channels don't correspond to human perception:

- **Lightness (L):** fully saturated yellow (`hsl(60,100%,50%)`) and fully saturated blue (`hsl(240,100%,50%)`) have the same L=50% but vastly different perceived brightness. L is a mathematical average, not a perceptual measurement.
- **Hue (H):** non-uniform spacing. A 20° shift near red produces a dramatic change; the same 20° near green is barely visible. The green region is compressed, reds are stretched.
- **Saturation (S):** doesn't correlate with perceived saturation. A color can have S=100% and still look muted (e.g., dark saturated blue).

**When HSL is fine:** simple color pickers, quick CSS tweaks, situations where perceptual accuracy doesn't matter.

**When to use something better:**

- Generating palettes or scales → **OKLCH** (uniform lightness across hues)
- Creating gradients → **OKLAB** or `color-mix(in oklab)` (no mid-gradient darkening)
- Gamut-aware picking with HSL-like UX → **OKHSL** (Ottosson's perceptual HSL)
- Normalized saturation 0–100% → **HSLuv** (CIELUV-based, no out-of-bounds)

### Named Hue (HSL/HSV) Ranges

Use these degree ranges when generating or constraining colors by hue name. Source: [random-display-p3-color](https://github.com/mrmrs/random-display-p3-color) by mrmrs / mrmrs.cc.

| Name       | Degrees       |
| ---------- | ------------- |
| **red**    | 345–360, 0–15 |
| **orange** | 15–45         |
| **yellow** | 45–70         |
| **green**  | 70–165        |
| **cyan**   | 165–195       |
| **blue**   | 195–260       |
| **purple** | 260–310       |
| **pink**   | 310–345       |
| **warm**   | 0–70          |
| **cool**   | 165–310       |

### Key Distinctions

- **Chroma** = colorfulness relative to a same-lightness neutral reference
- **Saturation** = perceived colorfulness relative to the color's own brightness
- **Lightness** = perceived reflectance relative to a similarly lit white
- **Brightness** = perceived intensity of light coming from a stimulus
- Same chroma ≠ same saturation. These are different dimensions.

## Gamut Math — Peak Lightness and Peak Chroma in OKLCH

A common misconception: there's a closed-form formula for $L_\text{peak}(C)$ in OKLCH. There isn't — not unless you also fix hue, or define peak as "max across all hues." The reason: the gamut boundary is the unit RGB cube, which becomes non-convex after `OKLab → LMS³ → XYZ → linear-RGB`. For fixed `(C, h)`, each linear-RGB channel is a **cubic polynomial in $L$**, and the envelope is solved channel-by-channel against `[0, 1]`.

Practical algorithm — binary search over $L \in [0, 1]$, converges in ~32 iterations:

```js
function peakL(C, h, toLinearRGB) {
  let lo = 0, hi = 1;
  for (let i = 0; i < 32; i++) {
    const mid = (lo + hi) / 2;
    const [r, g, b] = toLinearRGB(mid, C, h);
    const inGamut = r >= 0 && r <= 1 && g >= 0 && g <= 1 && b >= 0 && b <= 1;
    if (inGamut) lo = mid; else hi = mid;
  }
  return lo;
}
```

For design tokens, **`peakC(L, h)` is more useful than `peakL(C, h)`** — token systems fix lightness per ramp step and want maximum chroma at each hue.

For the full derivation (Ottosson $M_1$ and $M_2$ matrices, XYZ→sRGB / P3 / Rec.2020 matrices, the symmetric `peakC(L, h)` problem, Ottosson's analytic cusp algorithm, and production implementations), see [`references/techniques/oklch-gamut-peak-math.md`](references/techniques/oklch-gamut-peak-math.md).

## Implementation Guidance — Code and CSS

When using colors in a program or CSS, add a semantic layer between raw color values and UI roles.

The examples below are pseudocode, not literal CSS requirements. They express the decision structure an agent should preserve even if the target stack uses different syntax.

Across CSS, JS/TS, Swift, design-token JSON, templates, or pseudocode, default to the same structure:

- **Reference tokens/palette values** for concrete colors
- **Semantic tokens/roles** that map meaning onto those colors
- **Component usage** that consumes semantic tokens rather than raw literals

Raw color literals should usually appear only in palette/reference definitions, conversions, diagnostics, or deliberately one-off examples.

- **Use reference tokens for concrete colors**: `ref.red = #f00`
- **Use semantic tokens for meaning/role**: `semantic.warning = ref.red`
- **Prefer semantic tokens in components** so themes can swap meaning without rewriting component code.
- **This default applies in any language**; translate to the target system's equivalent alias/reference mechanism (CSS custom properties, Swift enums, design-token JSON, etc.).
- **Encode color decisions when possible** instead of freezing one manual choice into a literal.

Pseudocode examples:

- `ref.red := closest('red', generatedPalette)`
- `semantic.warning := ref.red`
- `semantic.onSurface := mostReadableOn(surface)`

Good pattern: palette/reference tokens define available colors; semantic tokens map those colors to roles like surface, text, accent, success, warning, and danger.

If a system can derive a decision from constraints, encode that derivation. Examples: nearest named hue in a generated palette, foreground chosen by APCA/WCAG target, hover state computed from the base token in OKLCH instead of hand-picking a second unrelated hex.

For larger systems, prefer a **token graph** over a flat token dump: references, semantic roles, derived functions, and scope inheritance. This makes theme changes, accessibility guarantees, and multi-platform export auditable and easier to maintain.

## Accessibility — Key Numbers

Of ~281 trillion hex color pairs (research-survey by @mrmrs\_, computed via a Rust brute-force run):

| Threshold                 | % passing | Odds            |
| ------------------------- | --------- | --------------- |
| WCAG 3:1 (large text)     | 26.49%    | ~1 in 4         |
| WCAG 4.5:1 (AA body text) | 11.98%    | ~1 in 8         |
| WCAG 7:1 (AAA)            | 3.64%     | ~1 in 27        |
| APCA 60                   | 7.33%     | ~1 in 14        |
| APCA 75 (fluent reading)  | 1.57%     | ~1 in 64        |
| APCA 90 (preferred body)  | **0.08%** | **~1 in 1,250** |

APCA is far more restrictive than WCAG at comparable readability. At APCA 90, only 239 billion of 281 trillion pairs work. JPEG compression exploits the same biology: chroma subsampling (4× less color data) is invisible because human vision resolves brightness at higher resolution than color.

## Color Harmony — What Actually Works

### Hue-first harmony is a weak standalone heuristic

Complementary, triadic, tetradic intervals are weak predictors of mood, legibility, or accessibility on their own. Every hue plane has a different shape in perceptual space, so geometric hue intervals do not guarantee perceptual balance.

### Character-first harmony works (Ellen Divers' research-survey)

Organize by character (pale/muted/deep/vivid/dark), not hue. Finding: **hue is usually a weaker predictor of emotional response than chroma and lightness** — a muted palette often reads as calm across many hues. Relaxed vs intense is driven more by chroma + lightness than hue alone.

### Legibility = lightness variation

Grayscale is a quick sanity check for lightness separation, not an accessibility proof. You still need to verify contrast with WCAG/APCA and consider text size, weight, polarity, and CVD. Same character + varied lightness is often more readable. Same lightness regardless of hue is usually illegible.

### The 60-30-10 rule

60% dominant color, 30% secondary, 10% accent. One color dominates to prevent "three equally-sized gorillas fighting."

## Pigment Mixing — Not What You Think

- **Pigment mixing is not well described by the simple subtractive model alone** — "integrated mixing" (Küppers/Briggs) is a better practical description. It behaves like a compromise between subtractive and additive averaging.
- **CMY mixing paths curve outward** (retain chroma = vivid secondaries) — "extroverted octopus"
- **RGB mixing paths curve inward** (lose chroma = dull browns) — "introverted octopus"
- **Mixing is non-linear**: proportion of paint ≠ proportional hue change. You "turn a corner" at certain ratios.
- **Blue→yellow is a LONG road**, red→yellow is SHORT. Traditional wheel massively misrepresents distances.
- **Tinting strength varies**: blues are concentrated/strong, yellows are weak.
- **White doesn't just lighten** — it shifts hue AND kills chroma.
- **For spectral/K-M mixing in code**: use Spectral.js (open source) or Mixbox (commercial).

## Color Temperature

- **Temperature ≠ hue** — it's a systematic shift of BOTH hue AND saturation, dependent on starting hue
- **Spectral bias**: which end of the spectrum a light favors (short λ = cool, long λ = warm)
- **Cool daylight**: blue atmospheric scatter fills shadows; paint neutral highlights, blue shadows
- **Warm incandescent**: favors long wavelengths including infrared (literally felt as heat)
- **Green and purple** do not map cleanly to warm/cool in the same way as red-orange or blue-cyan; perceived temperature depends strongly on context

## Color Naming — Multiple Systems for Different Registers

| System                | Register                   | Example                            |
| --------------------- | -------------------------- | ---------------------------------- |
| ISCC-NBS              | Scientific precision       | "vivid yellowish green"            |
| Munsell               | Systematic notation        | "5GY 7/10"                         |
| XKCD                  | Common perception          | "ugly yellow", "hospital green"    |
| Traditional Japanese  | Cultural/poetic            | "wasurenagusa-iro" (forget-me-not) |
| RAL                   | Industrial reproducibility | RAL 5002                           |
| Ridgway (1912)        | Ornithological             | 1,115 named colors, public domain  |
| CSS Named Colors      | Web standard               | 147 named colors                   |
| color-description lib | Emotional adjectives       | "pale, delicate, glistening"       |

Use `color-name-lists` npm package for 18 naming systems in one import.

## Historical Corrections

- **Moses Harris (1769)** was first to place RYB at equal 120° — Newton, Boutet, Schiffermüller didn't. His own wheel needed a 4th pigment. The origin of bad color theory.
- **Von Bezold (1874)** killed "indigo" as a spectral color — Newton's "blue" ≈ modern cyan, Newton's "indigo" ≈ modern blue.
- **The word "magenta"** wasn't used for the subtractive primary until 1907 (Carl Gustav Zander). Before: "pink" (Benson 1868), "crimson," "purpur."
- **Amy Sawyer (1911)** patented a CMY wheel (primrose/rose/turquoise) decades before it became mainstream.
- **Elizabeth Lewis (1931)** married trichromatic + opponent process on one wheel, anticipating CIE Lab by 30 years.

## Recommended Tools

### Palette Generation (actual algorithms, not pre-made swatches)

Note: coolors.co does not generate palettes — it picks randomly from 7,821 pre-made palettes hardcoded in its JS bundle.

- **RampenSau** — hue cycling + easing, color space agnostic
- **Poline** — anchor points + per-axis position functions (1.2K stars); ships a `<poline-palette>` web component for interactive controls
- **pro-color-harmonies** — adaptive OKLCH harmony, muddy-zone avoidance, 4 styles × 4 modifiers
- **dittoTones** — extract Tailwind/Radix "perceptual DNA", apply to your hue
- **FarbVelo** — random palettes with dark→light structure
- **IQ Cosine Formula** — `color(t) = a + b*cos(2π(c*t+d))`, 12 floats = infinite palette

### Palette Analysis & Linting

- **Color Buddy** — 38 lint rules (WCAG, CVD, distinctness, fairness, affect)
- **Censor** — Rust CLI, CAM16UCS analysis, 20+ viz widgets
- **Color Palette Shader** — WebGL2 Voronoi, 30+ color models, 11 distance metrics
- **PickyPalette** — interactive sculpting on color space canvas

### Color Libraries (code)

- **Culori** — 30 spaces, 10 distance metrics, gamut mapping, CVD sim
- **@texel/color** — 5–125× faster than Color.js, minimal, for real-time
- **Spectral.js** — open-source K-M pigment mixing (blue+yellow=green)
- **RYBitten** — RGB↔RYB with 26 historical color cubes
- **colorgram** — 1 kB image palette extraction; 64-bucket HLS+luminance quantization, ~15 ms for 340×340, fixed memory
- **Art Palette** — JS palette extraction from `ImageData` + Python/TensorFlow perceptual palette embeddings for search-by-color (Google Arts & Culture, Apache 2.0)
- **random-display-p3-color** — generate random Display P3 colors constrained by named hue/saturation/lightness, zero deps, ESM (by mrmrs / mrmrs.cc)

### Key Online Tools

- **oklch.com** — OKLCH picker
- **Huetone** — accessible color system builder (LCH/OKLCH), by Ardov
- **Ardov Color Lab** — gamut mapping playground, P3 space explorer, harmony generator, 3D color space visualizations, themer (lab.ardov.me)
- **Components.ai Color Scale** — parametric scale generator: 6 spaces, 4 curve methods, WCAG contrast (by mrmrs / mrmrs.cc)
- **View Color** — real-time analysis, WCAG + APCA, CVD preview
- **APCA Calculator** — apcacontrast.com

## Deep References

See `references/INDEX.md` for the detailed files organized as:

- **`historical/`** — Ostwald, Helmholtz, Bezold, Ridgway 1912, ISCC-NBS, Munsell, Albers, Caravaggio's pigments, Moses Harris, Lewis/Ladd-Franklin
- **`contemporary/`** — Ottosson's OKLAB articles, Briggs lectures, Fairchild, Hunt, CIECAM02, MacAdam ellipses, Koenderink 2026 empirical 3D metric field (RGB supports ~1,000 qualitative regions; cool side coarser than warm; chromatic circle is not well-tempered), Pointer's gamut, CIE 1931/standard observer, Pixar Color Science, Acerola, Juxtopposed, Computerphile, bird tetrachromacy, OLO, GenColor paper. Full scrapes: huevaluechroma.com and colorandcontrast.com
- **`techniques/`** — All tools above documented in detail, plus: CSS Color 4/5, ICC workflows, Tyler Hobbs generative color, Harvey Rayner Fontana approach, Goethe edge colors as design hack, mattdesl workshop + K-M simplex, CSS-native generation, IQ cosine presets, Erika Mulvenna interview, Bruce Lindbloom math reference, image extraction tools, Aladdin color analysis
