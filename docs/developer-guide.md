# Developer guide

This guide explains how the current generator is put together and how to change it without breaking the basic promises of the project.

## Design rules

1. Python is the source of truth.
2. Generated SVG files are output artifacts.
3. The generator must be deterministic for identical input.
4. Coordinates are in millimetres.
5. A4 portrait is the default v0.x target.
6. Every target section should have a stable SVG `id`.
7. Tests should cover behaviour before code changes land.

## Project layout

```text
PPCT/
├── ppct/
│   ├── __init__.py       # public package exports
│   ├── cli.py            # command line entry point
│   └── target.py         # current A4 SVG generator
├── tests/
│   └── test_generator.py # generator and CLI tests
├── examples/
│   └── ppct-a4.svg       # generated reference output
└── docs/                 # user and developer documentation
```

## Running tests

```bash
python3 -m unittest discover -s tests -v
```

The current tests check:

- A4 SVG dimensions
- Required section IDs
- Deterministic output for identical config
- CLI output file creation

## Building

```bash
uv build
```

Build artifacts are written to `dist/`, which is ignored by git.

## Generating the example SVG

```bash
python3 -m ppct.cli \
  --output examples/ppct-a4.svg \
  --title "PPCT A4 Reference" \
  --operator "" \
  --date "2026-07-29"
```

If the generator changes intentionally, regenerate the example and include it in the same commit.

## Current generator structure

`ppct/target.py` contains:

- `TargetConfig`: immutable configuration for one SVG run
- `generate_svg(config)`: returns the SVG string
- `write_svg(path, config)`: writes the SVG and returns the resolved path
- private helpers for SVG primitives and target sections

The current implementation is intentionally dependency-free. It writes SVG directly. That keeps the first version easy to inspect and easy to run.

## Adding or changing a section

Use this workflow:

1. Add or update a test in `tests/test_generator.py`.
2. Run the focused test and confirm it fails for the expected reason.
3. Change the generator.
4. Run the test again.
5. Run the full test suite.
6. Regenerate `examples/ppct-a4.svg` if output changed.
7. Update docs if behaviour changed.

Every section should have:

- Stable SVG group ID, for example `section-resolution-wedges`
- Clear label on the sheet
- Known purpose
- Layout bounds in millimetres
- Simple geometry that survives common plotter senders

Avoid clever SVG features until they are tested on real plotter software. Plain lines, rectangles, paths, and text are boring. Boring is portable.

## Determinism

Identical `TargetConfig` input should produce identical SVG bytes.

Avoid:

- Uncontrolled timestamps
- Randomness
- Dictionary iteration where ordering matters
- Environment-dependent defaults
- Floating point formatting that changes across paths

The CLI may default to today's date, because that is user-facing behaviour. Tests pass an explicit date when byte stability matters.

## Coordinate conventions

- Origin: top-left of page
- X axis: right
- Y axis: down
- Unit: millimetres
- Page: 210 x 297

Keep margins conservative. Some printers and plotters cannot reach the full paper area.

## Documentation rules

Documentation should be practical and plain.

Prefer:

- Commands that can be copied
- Short explanations
- Concrete checks
- Known limitations

Avoid:

- Manifesto language
- Claims of standardization before the sheet has been validated
- Promising future analysis before it exists
- Over-polished marketing phrasing

## Release checklist

Before tagging a release:

1. Run tests.
2. Build with `uv build`.
3. Regenerate example SVG.
4. Check README quick-start.
5. Check docs links.
6. Confirm license text.
7. Add release notes.

## Near-term refactoring ideas

The current `target.py` is fine for the first working version. Once sections start changing often, split it into modules:

```text
ppct/
├── geometry.py
├── svg.py
├── layout.py
└── sections/
    ├── metadata.py
    ├── geometry_reference.py
    ├── stroke_characterisation.py
    └── ...
```

Do that when it reduces friction, not before.
