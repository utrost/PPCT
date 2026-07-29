# Standard operating procedure

Use this when running one PPCT sheet. Keep it short. If you need more detail, read the user guide.

## Before plotting

1. Generate the SVG.

   ```bash
   python3 -m ppct.cli --output output/ppct-a4.svg
   ```

2. Print the sheet on A4 portrait at 100% scale.
3. Measure the printed geometry reference.
4. Record pen, paper, plotter, and motion metadata.
5. Load the sheet in portrait orientation.
6. Home the plotter.
7. Check pen-up and pen-down heights.
8. Check that the sender will plot the SVG at 100% scale.

Do not continue if the printed ruler is wrong. Fix print scaling first.

## During plotting

1. Start the plot.
2. Do not change feed rate, acceleration, pen height, or paper position.
3. Watch for obvious failures: paper slip, dry pen, pen holder movement, wrong origin.
4. If the run fails, stop it and mark the sheet as failed.
5. Record actual plotting time.

## After plotting

1. Let wet ink dry before scanning or stacking.
2. Inspect under good light.
3. Fill in the observation log.
4. Scan at 600 dpi colour if possible.
5. Copy [`docs/templates/metadata.md`](templates/metadata.md) and [`docs/templates/notes.md`](templates/notes.md) into the archive folder.
6. Record SHA-256 checksums for the SVG, PDF template, and scan.
7. Archive the SVG, PDF template, scan, metadata, and notes in one folder.

## Minimum metadata

Record at least this:

- Date
- Operator
- Pen manufacturer and model
- Ink and colour
- Paper manufacturer, product, and weight
- Plotter model
- Feed rate
- Pen-up and pen-down settings
- Plot sender
- PPCT commit or version

## Pass/fail notes

Do not force one global score. Record the behaviour.

Useful short labels:

- Clean
- Slight feathering
- Heavy feathering
- Dry starts
- End blobs
- Corner pooling
- Skips on long paths
- Close lines merge below stated spacing
- Good enough for plotting
- Not useful for this paper

Failed runs are still worth keeping if the cause is clear.
