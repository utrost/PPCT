# Contributing

PPCT is early. Small, tested changes are better than broad rewrites.

## What belongs here

Good contributions:

- Improve the generated calibration target
- Make the generator more deterministic or easier to use
- Add tests for generator behaviour
- Improve the SOP or user guide from actual plotting experience
- Add examples from real pen and paper tests
- Fix unclear documentation

Changes that should wait:

- Cloud services
- Online database features
- Formal standardization language
- Large framework rewrites
- Automated scoring without enough plotted evidence

## Development setup

Clone the repository:

```bash
git clone https://github.com/utrost/PPCT.git
cd PPCT
```

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Generate a target:

```bash
python3 -m ppct.cli --output output/ppct-a4.svg
```

Build package artifacts:

```bash
uv build
```

## Pull request checklist

Before opening a pull request:

- Tests pass
- Generated SVG output was regenerated if generator output changed
- README or docs were updated if behaviour changed
- New target sections have stable SVG IDs
- The change keeps A4 output deterministic for identical input
- The change is based on a practical plotting need

## Documentation style

Write plainly.

Prefer:

- Short paragraphs
- Copyable commands
- Specific limitations
- Real workflow notes

Avoid:

- Marketing prose
- Claims that PPCT is a standard
- Vague future promises
- Overly neat philosophy sections

If something only sounds useful in theory, put it in the roadmap or backlog. If it helped with an actual plotted sheet, document it in the guide.

## Commit style

Use conventional commit prefixes where possible:

```text
feat: add new calibration section
fix: correct SVG dimensions
docs: update user guide
test: cover CLI output path
chore: update project metadata
```

## Generated files

`output/` is ignored. It is for local generated files.

`examples/ppct-a4.svg` is tracked. It should represent the current default/reference output. If generator output changes intentionally, update this file in the same pull request.
