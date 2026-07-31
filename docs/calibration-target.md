# Calibration target reference

This page documents the current A4 target. It describes what each section is for and what to look for after plotting.

The target is not a formal standard. It is a practical sheet for comparing pens and plotting setups.

## Sheet format

- Paper: A4 portrait
- SVG size: 210 mm x 297 mm
- SVG viewBox: `0 0 210 297`
- Units: millimetres
- Default output: `output/ppct-a4.svg`
- Browser SVG layers: `Template / print first` and `Plot data / draw second`
- Browser template export: A4 PDF with labels, metadata fields, guide boxes, ruler labels, axes, and readout fields

The printed and plotted sheet should remain at 100% scale.

## Sections

## Metadata

Purpose: identify the test.

Look for:

- Title
- Operator
- Date
- Generator version
- Space for pen, paper, and plotter notes

The current generator accepts title, operator, and date from the CLI. More metadata automation will come later.

## Geometry Reference

Purpose: verify print and plot scale.

Current marks:

- 100 mm ruler with 5 mm and 10 mm ticks
- 50 x 10 mm reference rectangle

Use this section first. If geometry is wrong, later measurements are suspect.

## Resolution Wedges

Purpose: find the spacing where separate lines merge or become visually unusable.

Current marks:

- Separate mini-panels of close parallel lines at 2, 1.5, 1, 0.7, 0.5, and 0.3 mm
- A spacing axis labelled in millimetres

Look for:

- First spacing where white paper disappears
- Ink bridges between lines
- Mechanical wobble
- Paper fibre effects

Record the smallest spacing that remains readable.

## Hatch Density

Purpose: test tone generation with regular hatching.

Current marks:

- Two rows of hatch blocks at 3, 2, 1.5, 1, and 0.5 mm spacing
- Linear hatching in the first row and cross-hatching in the second row
- A spacing axis labelled in millimetres

Look for:

- Tone evenness
- Banding
- Paper damage
- Ink build-up
- Moire-like effects
- Whether the visual density matches the spacing change

This section matters for plotter art. Some pen/paper combinations look good as outlines and ugly as hatches.

## Curves / Concentric

Purpose: test dynamic behaviour during direction changes and compare curved/closed-line spacing.

Current marks:

- Curved path
- Closed concentric circles at 2, 1.5, 1, and 0.5 mm spacing
- Small spiral-like continuous curves at the same spacing values
- A spacing axis labelled in millimetres

Look for:

- Overshoot
- Vibration
- Corner pooling
- Dry turns
- Flat spots in curves

Curves often reveal speed and acceleration issues faster than straight lines. Concentric circles also show when closely spaced closed curves visually fill in.

## Minimum Text Size

Purpose: find the smallest usable plotted single-line text size for this pen/paper/plotter setup.

Current marks:

- Stroke-glyph `PPCT 123` at 6 and 5 mm text sizes, added after the first printed sheet showed that larger readability anchors were useful
- Stroke-glyph `PPCT abc 123` at 4, 3, 2, and 1.5 mm text sizes
- Stroke-glyph `Il1 O0 8B` at 1 and 0.8 mm text sizes
- The plotted letters use continuous path strokes rather than dot-matrix/pixel-glyph segments, so the diagnostic is closer to realistic pen lettering
- A text-height axis labelled in millimetres

Look for:

- First size where counters close up
- First size where digits become ambiguous
- Whether small text becomes fuzzy, scratchy, or over-inked

## Continuous Flow

Purpose: test long-path reliability.

Current marks:

- One long flowing path across the page

Look for:

- Fading
- Starvation
- Skipping
- Flooding after pauses
- Ink consistency from start to finish

This is the section that catches pens that seem fine in short samples but fail during a real plot.

## Stipple Gradient

Purpose: preview how stippled tonal fields look with this pen.

Current marks:

- Larger small-circle stipple boxes at 10, 25, 50, 75, and 90 percent nominal density
- Stipple count is intentionally about five times denser than the first measurement-v2 sheet, because the printed gradient was too sparse
- A density axis labelled in percent

Look for:

- Whether tiny circles stay open or fill in
- Tone smoothness versus visible dot pattern
- Ink build-up in dense samples
- Paper damage or tearing from repeated small circles

## Observation / Readout

Purpose: turn the plotted sheet into a measurement instrument instead of a loose sample sheet.

Current fields:

- Min line spacing: smallest readable parallel-line spacing in millimetres
- Min hatch spacing: smallest usable hatch spacing in millimetres
- Min text size: smallest usable plotted text size in millimetres
- Best stipple: preferred stipple density in percent

Use this for immediate threshold values. Put detailed qualitative notes in the archived `notes.md` file.

## Suggested archive fields

A future metadata schema should cover these fields.

```yaml
test:
  date: "2026-07-29"
  operator: ""
  ppct_version: "0.5.3"
  svg_file: "ppct-a4.svg"
pen:
  manufacturer: ""
  model: ""
  nominal_width_mm: ""
  ink: ""
  colour: ""
paper:
  manufacturer: ""
  product: ""
  weight_gsm: ""
  surface: ""
plotter:
  manufacturer: ""
  model: ""
  firmware: ""
  controller: ""
motion:
  feed_rate: ""
  acceleration: ""
  pen_up_height: ""
  pen_down_height: ""
  lift_delay_ms: ""
  lower_delay_ms: ""
results:
  actual_plot_time: ""
  smallest_readable_spacing_mm: ""
  overall_notes: ""
```

## Known gaps

- No machine-readable metadata block yet
- No per-section layout API yet
- No automatic path length or pen lift statistics yet
- No scan analysis yet
- No scoring rubric yet

Those are planned. The current sheet is meant to be plotted and improved from real use.
