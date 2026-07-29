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
- Browser template export: A4 PDF with labels, metadata fields, guide boxes, ruler labels, and observation lines

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

## Stroke Characterisation

Purpose: compare basic line behaviour.

Current marks:

- Horizontal strokes at several SVG stroke widths

Look for:

- Consistent width
- Feathering
- Railroading
- Scratchy ink flow
- Pooling
- Visible difference between requested stroke widths

A plotter pen does not always follow SVG stroke width physically. This section still helps reveal how the sender and plotter interpret the file.

## Resolution Wedges

Purpose: find the spacing where separate lines merge or become visually unusable.

Current marks:

- Groups of close parallel lines
- Spacing labels in millimetres

Look for:

- First spacing where white paper disappears
- Ink bridges between lines
- Mechanical wobble
- Paper fibre effects

Record the smallest spacing that remains readable.

## Hatch Density

Purpose: test tone generation with regular hatching.

Current marks:

- Rectangular hatch blocks at different spacing values

Look for:

- Tone evenness
- Banding
- Paper damage
- Ink build-up
- Moire-like effects
- Whether the visual density matches the spacing change

This section matters for plotter art. Some pen/paper combinations look good as outlines and ugly as hatches.

## Curves & Corners

Purpose: test dynamic behaviour during direction changes.

Current marks:

- Curved path
- Corner/radius marks

Look for:

- Overshoot
- Vibration
- Corner pooling
- Dry turns
- Flat spots in curves

Curves often reveal speed and acceleration issues faster than straight lines.

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

## Pen Lift Reliability

Purpose: test repeated starts and stops.

Current marks:

- Grid of small cross marks

Look for:

- Dry starts
- Blobs at pen-down
- Tails at pen-up
- Missed marks
- Repeatability across the grid

This section is sensitive to pen-down delay, pen-up delay, holder friction, and ink type.

## Observation Log

Purpose: capture quick human evaluation on the sheet.

Current fields:

- Line quality
- Start/end
- Feather/bleed
- Suitability

Use this for immediate notes. Put detailed notes in the archived `notes.md` file.

## Suggested archive fields

A future metadata schema should cover these fields.

```yaml
test:
  date: "2026-07-29"
  operator: ""
  ppct_version: "0.1.0"
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
