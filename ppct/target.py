from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
MARGIN_MM = 10


@dataclass(frozen=True)
class TargetConfig:
    """Configuration for a generated PPCT target.

    Keep defaults stable: identical config must produce byte-identical SVG.
    """

    title: str = "PPCT PlotPen Characterization Target"
    operator: str = ""
    date: str = ""
    generator_version: str = "0.1.0"


def _attrs(**attributes: object) -> str:
    parts: list[str] = []
    for key, value in attributes.items():
        if value is None:
            continue
        attr = key.rstrip("_").replace("_", "-")
        parts.append(f'{attr}="{escape(str(value))}"')
    return " ".join(parts)


def _line(x1: float, y1: float, x2: float, y2: float, **attrs: object) -> str:
    return f"<line {_attrs(x1=x1, y1=y1, x2=x2, y2=y2, **attrs)} />"


def _text(x: float, y: float, content: str, size: float = 3.0, **attrs: object) -> str:
    return f"<text {_attrs(x=x, y=y, font_size=size, **attrs)}>{escape(content)}</text>"


def _rect(x: float, y: float, width: float, height: float, **attrs: object) -> str:
    return f"<rect {_attrs(x=x, y=y, width=width, height=height, **attrs)} />"


def _path(d: str, **attrs: object) -> str:
    return f"<path {_attrs(d=d, **attrs)} />"


def _group(group_id: str, label: str, x: float, y: float, width: float, height: float, body: list[str]) -> str:
    parts = [f'<g id="{group_id}">']
    parts.append(_rect(x, y, width, height, fill="none", stroke="#bbb", stroke_width="0.2"))
    parts.append(_text(x + 2, y + 4, label, 2.8, fill="#111", font_family="monospace"))
    parts.extend(body)
    parts.append("</g>")
    return "\n".join(parts)


def _metadata_section(config: TargetConfig) -> str:
    x, y, w, h = 10, 10, 190, 24
    values = [
        ("Title", config.title),
        ("Operator", config.operator or "________________"),
        ("Date", config.date or "________________"),
        ("Generator", config.generator_version),
    ]
    body = []
    for index, (key, value) in enumerate(values):
        body.append(_text(x + 3, y + 9 + index * 4, f"{key}: {value}", 2.6, font_family="monospace"))
    body.append(_text(x + 115, y + 9, "Pen / paper / plotter notes:", 2.6, font_family="monospace"))
    body.append(_rect(x + 115, y + 11, 70, 9, fill="none", stroke="#999", stroke_width="0.15"))
    return _group("section-metadata", "Metadata", x, y, w, h, body)


def _geometry_reference() -> str:
    x, y, w, h = 10, 39, 190, 28
    body = []
    body.append(_line(x + 5, y + 16, x + 105, y + 16, stroke="#000", stroke_width="0.25"))
    for tick in range(0, 101, 5):
        height = 5 if tick % 10 == 0 else 3
        tx = x + 5 + tick
        body.append(_line(tx, y + 16, tx, y + 16 - height, stroke="#000", stroke_width="0.18"))
        if tick % 10 == 0:
            body.append(_text(tx - 1.5, y + 23, str(tick), 2.2, font_family="monospace"))
    body.append(_rect(x + 125, y + 9, 50, 10, fill="none", stroke="#000", stroke_width="0.25"))
    body.append(_text(x + 126, y + 23, "50 x 10 mm box", 2.2, font_family="monospace"))
    return _group("section-geometry-reference", "Geometry Reference", x, y, w, h, body)


def _stroke_characterisation() -> str:
    x, y, w, h = 10, 72, 90, 42
    body = []
    widths = [0.1, 0.2, 0.3, 0.5, 0.8]
    for idx, width in enumerate(widths):
        yy = y + 11 + idx * 6
        body.append(_line(x + 8, yy, x + 72, yy, stroke="#000", stroke_width=width))
        body.append(_text(x + 74, yy + 0.8, f"{width:.1f}", 2.0, font_family="monospace"))
    return _group("section-stroke-characterisation", "Stroke Characterisation", x, y, w, h, body)


def _resolution_wedges() -> str:
    x, y, w, h = 110, 72, 90, 42
    body = []
    spacings = [2.0, 1.5, 1.0, 0.7, 0.5, 0.3]
    for idx, spacing in enumerate(spacings):
        start_x = x + 8 + idx * 12
        yy = y + 10
        count = int(22 / spacing)
        for n in range(count):
            xx = start_x + n * spacing
            body.append(_line(round(xx, 2), yy, round(xx, 2), yy + 20, stroke="#000", stroke_width="0.15"))
        body.append(_text(start_x, y + 35, f"{spacing:g}", 2.0, font_family="monospace"))
    return _group("section-resolution-wedges", "Resolution Wedges", x, y, w, h, body)


def _hatch_density() -> str:
    x, y, w, h = 10, 119, 90, 46
    body = []
    spacings = [3.0, 2.0, 1.5, 1.0]
    for idx, spacing in enumerate(spacings):
        bx = x + 8 + idx * 19
        by = y + 10
        body.append(_rect(bx, by, 15, 24, fill="none", stroke="#000", stroke_width="0.15"))
        n = 1
        while n * spacing < 15:
            body.append(_line(round(bx + n * spacing, 2), by, round(bx + n * spacing, 2), by + 24, stroke="#000", stroke_width="0.12"))
            n += 1
        body.append(_text(bx + 1, y + 39, f"{spacing:g}mm", 2.0, font_family="monospace"))
    return _group("section-hatch-density", "Hatch Density", x, y, w, h, body)


def _curves_corners() -> str:
    x, y, w, h = 110, 119, 90, 46
    body = []
    body.append(_path(f"M {x+10} {y+34} C {x+22} {y+6}, {x+38} {y+6}, {x+50} {y+34} S {x+70} {y+62}, {x+80} {y+16}", fill="none", stroke="#000", stroke_width="0.25"))
    for idx, radius in enumerate([2, 4, 8, 12]):
        cx = x + 12 + idx * 18
        body.append(_path(f"M {cx} {y+18} h 8 a {radius} {radius} 0 0 1 {radius} {radius} v 8", fill="none", stroke="#000", stroke_width="0.2"))
    return _group("section-curves-corners", "Curves & Corners", x, y, w, h, body)


def _continuous_flow() -> str:
    x, y, w, h = 10, 170, 190, 39
    body = []
    d = [f"M {x+8} {y+22}"]
    for idx in range(14):
        cx1 = x + 16 + idx * 12
        cy1 = y + (8 if idx % 2 else 34)
        cx2 = x + 22 + idx * 12
        cy2 = y + (34 if idx % 2 else 8)
        ex = x + 28 + idx * 12
        ey = y + 22
        d.append(f"C {cx1} {cy1}, {cx2} {cy2}, {ex} {ey}")
    body.append(_path(" ".join(d), fill="none", stroke="#000", stroke_width="0.25"))
    return _group("section-continuous-flow", "Continuous Flow", x, y, w, h, body)


def _pen_lift_reliability() -> str:
    x, y, w, h = 10, 214, 90, 43
    body = []
    for row in range(5):
        for col in range(9):
            cx = x + 9 + col * 8
            cy = y + 11 + row * 6
            body.append(_line(cx - 2, cy, cx + 2, cy, stroke="#000", stroke_width="0.18"))
            body.append(_line(cx, cy - 2, cx, cy + 2, stroke="#000", stroke_width="0.18"))
    return _group("section-pen-lift-reliability", "Pen Lift Reliability", x, y, w, h, body)


def _observation_log() -> str:
    x, y, w, h = 110, 214, 90, 43
    body = []
    labels = ["Line quality", "Start/end", "Feather/bleed", "Suitability"]
    for idx, label in enumerate(labels):
        yy = y + 12 + idx * 7
        body.append(_text(x + 4, yy, f"{label}:", 2.4, font_family="monospace"))
        body.append(_line(x + 32, yy - 0.8, x + 84, yy - 0.8, stroke="#777", stroke_width="0.12"))
    return _group("section-observation-log", "Observation Log", x, y, w, h, body)


def generate_svg(config: TargetConfig | None = None) -> str:
    """Return a deterministic A4 portrait PPCT SVG string."""

    config = config or TargetConfig()
    sections = [
        _metadata_section(config),
        _geometry_reference(),
        _stroke_characterisation(),
        _resolution_wedges(),
        _hatch_density(),
        _curves_corners(),
        _continuous_flow(),
        _pen_lift_reliability(),
        _observation_log(),
    ]
    body = "\n".join(sections)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg id="ppct-target" xmlns="http://www.w3.org/2000/svg" width="{A4_WIDTH_MM}mm" height="{A4_HEIGHT_MM}mm" viewBox="0 0 {A4_WIDTH_MM} {A4_HEIGHT_MM}">\n'
        '<title>PPCT PlotPen Characterization Target</title>\n'
        '<desc>A deterministic A4 calibration target for pen plotter evaluation.</desc>\n'
        '<style>text{dominant-baseline:alphabetic}.cut{fill:none;stroke:#000}</style>\n'
        f'{body}\n'
        '</svg>\n'
    )


def write_svg(path: str | Path, config: TargetConfig | None = None) -> Path:
    """Write a generated SVG target and return its resolved path."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate_svg(config), encoding="utf-8")
    return output.resolve()
