# Roadmap

PPCT should grow from a useful single-sheet generator into a repeatable pen plotting test workflow. Slowly. The next feature should improve actual comparison work, not just make the project look larger.

## Phase 0: foundation

Status: in progress.

Goal: a repository that can generate a deterministic A4 SVG target and explain how to use it.

Done:

- Repository created
- MIT license added
- Python package skeleton added
- CLI added
- Deterministic A4 SVG generation added
- Initial calibration sections added
- Example SVG added
- Tests added
- README and documentation set added

Remaining:

- Add a small release process
- Decide documentation license, if different from code license
- Add generated SVG checksum to release notes

Exit criterion:

- A new user can clone the repository, generate the SVG, run tests, and understand the current workflow from the docs.

## Phase 1: practical calibration

Goal: validate the A4 target with real pens and improve the sheet based on plotted results.

Planned work:

- Plot at least five different pens on the same paper and plotter setup
- Record what each target section reveals
- Adjust section geometry where the first layout is too dense, too sparse, or not useful
- Add a simple result template for archived tests
- Add a clearer scoring vocabulary without collapsing everything into one number
- Add optional title/date/operator fields that are easier to use from the CLI
- Add path statistics if they can be calculated reliably from generated geometry

Exit criterion:

- Five pen tests can be compared without extra explanation outside the repository.

## Phase 2: configurable generator

Goal: normal customization should not require code edits.

Planned work:

- Add a YAML or TOML config file
- Support paper profiles
- Support named target profiles
- Add optional A5 output
- Add section enable/disable switches
- Add configurable margins
- Add stable metadata schema
- Split `target.py` into SVG, layout, and section modules if useful

Exit criterion:

- Common changes can be made through config and still produce deterministic output.

## Phase 3: archive workflow

Goal: make test results easier to store and compare.

Planned work:

- Add metadata file template
- Add archive folder naming helper
- Add result notes template
- Add scan naming conventions
- Add a simple index file for a collection of tests
- Add optional checksum capture for generated SVGs and scans

Exit criterion:

- A set of PPCT runs can be stored consistently and reviewed later without guessing what each file means.

## Phase 4: scan-assisted analysis

Goal: extract a small number of useful measurements from scans.

Planned work:

- Define scan requirements
- Add OpenCV proof of concept
- Detect geometry reference scale
- Estimate line spacing readability in resolution wedges
- Measure hatch density variance
- Generate a simple report

Exit criterion:

- Selected measurements can be extracted automatically from a controlled scan.

## Backlog

Potential future work:

- QR or machine-readable metadata on the sheet
- Multiple page sizes
- Plotter-specific sender notes
- Inkscape export checks
- HPGL or G-code export exploration
- Visual diff between two scans
- Web gallery for archived tests

## Non-goals for now

- Formal standardization
- Cloud database
- Online community portal
- Large dependency stack
- Automated grading without human inspection

PPCT should stay small until plotted sheets prove what needs to grow.
