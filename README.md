# PPCT - PlotPen Characterization Target

PPCT generates SVG calibration targets for pen plotters.

The first target is A4 portrait. It is meant to answer a practical question: is this pen, ink, paper, plotter, and motion setup usable, and how does it compare to the last one?

The project is early. The generator exists, the first target layout exists, and the documentation now describes the workflow well enough to run a repeatable test.

## Status

- Project stage: draft v0.5
- Current milestone: generator foundation and first practical A4 target
- License: MIT
- Default target: A4 portrait SVG
- Python: 3.11+

## Install or run from the repository

Clone the repository:

```bash
git clone https://github.com/utrost/PPCT.git
cd PPCT
```

Generate the default target from the command line:

```bash
python3 -m ppct.cli --output output/ppct-a4.svg
```

Or use the browser generator after deployment:

- GitHub Pages: `https://utrost.github.io/PPCT/`
- simiono.com: `https://simiono.com/ppct/`

The browser generator supports live preview, SVG download, optional pen/paper/plotter notes, a two-layer SVG output, and a printable template PDF. The SVG contains a template layer and a plot-data layer. Turn the template layer off when you need a plot-data-only SVG for software that cannot hide layers.

Generate a target with printed metadata:

```bash
python3 -m ppct.cli \
  --output output/ppct-a4.svg \
  --title "PPCT A4 Reference" \
  --operator "Operator" \
  --date "2026-07-29"
```

Open or print the SVG at 100% scale. Do not fit to page. Scaling defeats the geometry reference.

A generated example is included at [`examples/ppct-a4.svg`](examples/ppct-a4.svg).

## Physical test references

- [`docs/test-results/2026-07-31-hema-0-4-fineliner.md`](docs/test-results/2026-07-31-hema-0-4-fineliner.md): actual A4 reference run with a purple HEMA 0.4 mm fineliner. The photo shows the first useful thing PPCT caught: a heavy ink blob at the starting/fill area.
- [`docs/test-results/2026-07-31-hema-2mm.md`](docs/test-results/2026-07-31-hema-2mm.md): actual A4 reference run with a magenta HEMA 2 mm marker. Large marks are usable; fine text and dense panels get crowded quickly.

## What the target contains

The current A4 sheet contains these sections:

- Metadata: test identification and notes
- Geometry Reference: ruler ticks and a known-size rectangle
- Resolution Wedges: separated mini-panels for close parallel lines from 2 to 0.3 mm
- Hatch Density: linear and cross-hatch samples, down to 0.5 mm spacing
- Curves / Concentric: curve behaviour plus closed/spiral concentric samples
- Minimum Text Size: single-line stroke text from 6 to 0.8 mm, including ambiguous characters
- Continuous Flow: long-path ink consistency
- Stipple Gradient: dense small-circle stipple samples from 10 to 90 percent
- Observation / Readout: hand-written parameter fields for the useful thresholds

The SVG is generated from Python. Do not edit generated SVG files by hand; change the generator and regenerate.

## Documentation

- [`docs/user-guide.md`](docs/user-guide.md): how to generate, print, plot, inspect, and archive a test
- [`docs/sop.md`](docs/sop.md): short operating procedure for running one PPCT sheet
- [`docs/calibration-target.md`](docs/calibration-target.md): what each section measures
- [`docs/templates/metadata.md`](docs/templates/metadata.md): copyable metadata record for one plotted sheet
- [`docs/templates/notes.md`](docs/templates/notes.md): copyable observation notes for one plotted sheet
- [`docs/developer-guide.md`](docs/developer-guide.md): project structure and development workflow
- [`docs/roadmap.md`](docs/roadmap.md): current phases and next work
- [`CONTRIBUTING.md`](CONTRIBUTING.md): contribution rules and pull request checklist

## Repository structure

```text
PPCT/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── docs/
│   ├── calibration-target.md
│   ├── developer-guide.md
│   ├── roadmap.md
│   ├── sop.md
│   ├── templates/
│   │   ├── metadata.md
│   │   └── notes.md
│   └── user-guide.md
├── examples/
│   └── ppct-a4.svg
├── ppct/
│   ├── __init__.py
│   ├── cli.py
│   └── target.py
├── web/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   ├── manifest.webmanifest
│   ├── sw.js
│   └── icons/
│       └── icon.svg
├── tests/
│   ├── test_generator.py
│   └── test_web_app.py
└── output/              # local generated files, ignored by git
```

## Development

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Build package artifacts:

```bash
uv build
```

The generator should remain deterministic. Given the same inputs, it should produce the same SVG bytes.

## Roadmap snapshot

- Phase 0: foundation, generator, docs, tests
- Phase 1: improve the practical A4 target through real pen tests
- Phase 2: configuration files, layout profiles, A5 support
- Phase 3: scan and measurement workflow

See [`docs/roadmap.md`](docs/roadmap.md) for the current plan.

## Non-goals for v0.x

- Formal standardization
- Cloud services
- Online database
- Community portal
- QR-based infrastructure

Those can wait. First the sheet has to be useful.

## License

MIT. See [`LICENSE`](LICENSE).
