# User guide

This guide describes one complete PPCT run: generate the target, print it, plot it, inspect it, and archive the result.

PPCT compares a complete plotting setup, not just a pen. Keep that in mind when reading old sheets. A different paper or feed rate can change the result as much as a different pen.

## 1. Generate the SVG

Use the browser generator when it is deployed:

- GitHub Pages: `https://utrost.github.io/PPCT/`
- simiono.com: `https://simiono.com/ppct/`

Fill in title, operator, date, and optional pen/paper/plotter notes, then use **Download SVG**.

The web generator can also omit plotted labels and metadata text. Use that mode for thicker pens or when plotting only the calibration geometry onto a preprinted reference sheet.

Or generate from the repository root:

```bash
python3 -m ppct.cli --output output/ppct-a4.svg
```

With metadata:

```bash
python3 -m ppct.cli \
  --output output/ppct-a4.svg \
  --title "PPCT A4 Reference" \
  --operator "Operator" \
  --date "2026-07-29"
```

The command creates parent directories if needed.

## 2. Print the reference sheet

Print the SVG on A4 paper at 100% scale.

Check the print dialog before committing paper:

- Page size: A4 portrait
- Scale: 100%
- Fit to page: off
- Center on page: on, if available
- Printer margins: default is fine if the full target remains visible

After printing, measure the geometry reference section. The 100 mm ruler should be 100 mm on paper. The 50 x 10 mm box should measure 50 mm by 10 mm.

If the printed ruler is off, fix printing before plotting. Do not compensate in the plotter job unless you are intentionally testing that compensation.

## 3. Record setup metadata

Record enough information to reproduce the run.

Pen:

- Manufacturer
- Model
- Nominal width
- Ink type
- Colour
- Age or usage notes, if relevant

Paper:

- Manufacturer
- Product
- Weight in gsm
- Surface finish
- Colour
- Printed or blank base sheet

Plotter:

- Manufacturer and model
- Firmware or controller version
- Pen holder
- Tool mount or adapter

Motion:

- Feed rate
- Acceleration
- Jerk, if supported
- Pen-up height
- Pen-down height
- Lift and lower speed
- Lift and lower delay

Software:

- PPCT generator version or commit
- Plot sender
- SVG revision
- Date
- Operator

Some of this is boring. That is the point. Boring metadata makes comparison possible later.

## 4. Plot the target

Load the printed A4 sheet into the plotter in portrait orientation.

Before sending the job:

1. Home the plotter.
2. Check paper alignment.
3. Check that the pen is seated consistently.
4. Confirm pen-up and pen-down heights.
5. Confirm that the SVG will plot at 100% scale.
6. Run a dry preview if your sender supports it.

During plotting, do not change speed, pressure, pen height, or paper position. If something goes wrong, mark the sheet as failed and start a new one. Failed sheets are still useful, but not as clean comparison data.

## 5. Inspect the sheet

Use good light. A 10x loupe helps.

Check these things:

- Line start quality: blob, dry start, hook, clean start
- Line end quality: tail, pooling, skip, clean stop
- Stroke consistency: width variation, railroading, feathering
- Close lines: where separate strokes merge or become unreadable
- Hatch blocks: visible banding, uneven tone, paper damage
- Curves and corners: overshoot, corner pooling, vibration, missed ink
- Continuous flow: fading, starvation, skipping, flooding
- Pen lifts: whether repeated starts and stops stay consistent

Use the observation log on the sheet for quick notes. Put longer notes in the archive record.

## 6. Scan and archive

Recommended scan:

- 600 dpi
- Colour
- No automatic sharpening
- No automatic contrast enhancement
- Save as TIFF or high-quality PNG if possible

Archive these files together:

```text
YYYY-MM-DD_pen-paper-plotter/
├── ppct-a4.svg
├── ppct-a4-plotted-scan.png
├── metadata.md
└── notes.md
```

Suggested folder name:

```text
2026-07-29_uniball-0.5_clairefontaine-90gsm_idrawh-a3/
```

The exact naming convention can change. The important rule is one folder per test condition.

## 7. Compare two pens

Compare sheets with the same paper, plotter, and motion settings first. Otherwise the comparison is muddy.

Useful comparison order:

1. Printed geometry reference: confirms the base sheet scale.
2. Stroke characterisation: basic line quality.
3. Resolution wedges: minimum usable spacing.
4. Hatch density: tone behaviour and paper interaction.
5. Curves and corners: motion sensitivity.
6. Continuous flow: long-run reliability.
7. Pen lift reliability: repeated start/stop behaviour.

A pen can pass one section and fail another. That is fine. PPCT is meant to describe behaviour, not award a single grade.

## Current limitations

The current generator produces one fixed A4 layout. Configuration files, A5 targets, paper profiles, and scan analysis are planned but not implemented yet.
