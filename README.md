# PPCT -- PlotPen Characterization Target

> **Status:** Draft v0.4\
> **Repository:** `ppct`\
> **License:** MIT (software), documentation/license to be finalized

------------------------------------------------------------------------

# Overview

PPCT (PlotPen Characterization Target) is an open-source toolkit for
generating standardized calibration targets for pen plotters.

The project focuses on **practical, repeatable evaluation** of the
complete plotting system:

-   Pen
-   Ink
-   Paper
-   Plotter
-   Plotting parameters

The goal is not to create a formal standard from the outset.

Instead, PPCT follows a simple engineering philosophy:

> **Keep it small. Make it work. Then improve it.**

The first milestone is a useful tool that can answer a practical
question:

> *"I have a new pen. Is it suitable for plotting, and how does it
> compare to the others I own?"*

------------------------------------------------------------------------

# Project Goals

Version 0.x aims to:

-   Generate an A4 calibration target as SVG
-   Generate SVGs entirely from Python
-   Eliminate manual SVG editing
-   Provide a repeatable workflow
-   Document all relevant plotting parameters
-   Produce comparable results between tests

------------------------------------------------------------------------

# Guiding Principles

-   Python is the single source of truth.
-   SVG files are generated---not edited.
-   Every calibration element measures a specific property.
-   Every generated target shall be reproducible.
-   Practical usefulness takes priority over completeness.

------------------------------------------------------------------------

# Repository Structure

``` text
ppct/
├── README.md
├── docs/
│   ├── specification.md
│   ├── sop.md
│   └── developer-guide.md
├── generator/
├── ppct/
│   ├── geometry/
│   ├── layout/
│   ├── sections/
│   └── assets/
├── output/
├── examples/
└── tests/
```

------------------------------------------------------------------------

# System Architecture

    Python Generator
            │
            ▼
    Generated SVG
            │
            ▼
    Print Reference Sheet
            │
            ▼
    Plot Calibration Geometry
            │
            ▼
    Inspect & Measure
            │
            ▼
    Scan
            │
            ▼
    Archive

The workflow should remain deterministic. Given identical inputs, the
generator should always produce identical output.

------------------------------------------------------------------------

# Why A4?

PPCT v0.x standardizes on **A4 portrait**.

Reasons:

-   Universally printable
-   Large enough for meaningful calibration
-   Suitable for binders and archives
-   Can later be reduced to A5
-   Plenty of room for annotations

------------------------------------------------------------------------

# Generator Philosophy

The generator is the project.

The SVG is merely an output artifact.

Each calibration section is implemented as an independent module
exposing:

-   dimensions
-   preferred placement
-   drawing routine
-   metadata
-   unique identifier

Future targets are created by composing these reusable modules.

------------------------------------------------------------------------

# Initial Calibration Target

Version 0.x consists of the following sections:

  Section                   Purpose
  ------------------------- --------------------------
  Metadata                  Test identification
  Geometry Reference        Dimensional verification
  Stroke Characterisation   Line quality
  Resolution Wedges         Minimum spacing
  Hatch Density             Tone generation
  Curves & Corners          Dynamic behaviour
  Continuous Flow           Long-path reliability
  Pen Lift Reliability      Start/stop consistency
  Observation Log           Manual evaluation

------------------------------------------------------------------------

# Plotter Metadata

Every completed sheet should capture enough information to reproduce the
test.

## Pen

-   Manufacturer
-   Model
-   Nominal width
-   Ink
-   Colour

## Paper

-   Manufacturer
-   Product
-   Weight (gsm)
-   Surface finish
-   Colour

## Plotter

-   Manufacturer
-   Model
-   Firmware
-   Controller
-   Pen holder

## Motion

-   Feed rate
-   Acceleration
-   Jerk (if supported)

## Pen Motion

-   Pen-up height
-   Pen-down height
-   Lift speed
-   Lower speed
-   Lift delay
-   Lower delay

## Job Statistics

-   Estimated plotting time
-   Actual plotting time
-   Total path length
-   Pen-down distance
-   Pen-up travel distance
-   Number of paths
-   Number of pen lifts
-   Number of layers

## Software

-   Generator version
-   Plot sender
-   SVG revision
-   Date
-   Operator

Future versions should automatically generate as much of this metadata
as possible.

------------------------------------------------------------------------

# Standard Operating Procedure (SOP)

## Preparation

1.  Print the PPCT reference page on A4 at **100% scale**.
2.  Verify the printed ruler dimensions.
3.  Record paper metadata.
4.  Install and align the pen.
5.  Record plotter settings.
6.  Home the plotter.

## Plotting

1.  Load the printed sheet.
2.  Verify orientation.
3.  Plot the calibration geometry.
4.  Do not change settings during the job.
5.  Record the actual plotting time.

## Inspection

Inspect under good lighting.

Recommended:

-   10× loupe
-   600 dpi flatbed scan

Evaluate:

-   Line quality
-   Start quality
-   End quality
-   Hatch quality
-   Corner behaviour
-   Ink consistency
-   Feathering
-   Bleeding
-   Drying behaviour
-   Overall suitability

## Archiving

Archive together:

-   Generated SVG
-   Completed calibration sheet
-   600 dpi scan
-   Plotter configuration
-   Notes

Each archived sheet represents exactly one:

**Pen × Paper × Plotter × Configuration**

------------------------------------------------------------------------

# Development Roadmap

## Phase 0 -- Foundation

-   Repository
-   Documentation
-   Generator skeleton

**Exit criterion**

-   SVG generation works.

------------------------------------------------------------------------

## Phase 1 -- Practical Calibration

Implement:

-   Metadata
-   Geometry
-   Stroke tests
-   Resolution wedges
-   Hatch density
-   Curves
-   Continuous flow
-   Pen lift tests

**Exit criterion**

Successfully evaluate at least five different pens.

------------------------------------------------------------------------

## Phase 2 -- Generator Improvements

-   Configurable layouts
-   Optional A5 generation
-   Configuration file
-   Paper profiles

**Exit criterion**

No code changes required for normal customization.

------------------------------------------------------------------------

## Phase 3 -- Automated Analysis

-   Scan workflow
-   OpenCV analysis
-   Automatic measurements
-   Report generation

**Exit criterion**

Selected measurements are extracted automatically.

------------------------------------------------------------------------

# Acceptance Criteria

A new user should be able to:

-   Install the generator
-   Generate an SVG
-   Print the calibration sheet
-   Plot the target
-   Follow the SOP
-   Compare two pens objectively

without additional documentation.

------------------------------------------------------------------------

# Non-Goals (v0.x)

The following are intentionally postponed:

-   Formal standardization
-   Cloud services
-   Online database
-   Community portal
-   QR-based infrastructure

These features may be revisited after the workflow has been validated
through real-world use.

------------------------------------------------------------------------

# Contributing

The project values:

-   Simple solutions
-   Reproducibility
-   Practical testing
-   Clear documentation
-   Incremental improvement

If a proposed feature does not improve the practical usefulness of the
calibration target, it probably belongs in a future release rather than
the current milestone.

------------------------------------------------------------------------

# License

To be finalized.

Suggested:

-   MIT License for software
-   CC BY-SA 4.0 for documentation
