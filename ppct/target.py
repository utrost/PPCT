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


def _circle(cx: float, cy: float, r: float, **attrs: object) -> str:
    return f"<circle {_attrs(cx=cx, cy=cy, r=r, **attrs)} />"


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


def _resolution_wedges() -> str:
    x, y, w, h = 10, 72, 90, 42
    body = [_line(x + 8, y + 34, x + 82, y + 34, stroke="#777", stroke_width="0.12", data_axis="spacing-mm")]
    spacings = [2.0, 1.5, 1.0, 0.7, 0.5, 0.3]
    for idx, spacing in enumerate(spacings):
        start_x = x + 8 + idx * 12
        yy = y + 10
        count = int(22 / spacing)
        for n in range(count):
            xx = start_x + n * spacing
            body.append(_line(round(xx, 2), yy, round(xx, 2), yy + 20, stroke="#000", stroke_width="0.15"))
        body.append(_text(start_x, y + 37, f"{spacing:g}mm", 2.0, font_family="monospace"))
    return _group("section-resolution-wedges", "Resolution Wedges", x, y, w, h, body)


def _hatch_density() -> str:
    x, y, w, h = 110, 72, 90, 42
    body = [_line(x + 8, y + 34, x + 84, y + 34, stroke="#777", stroke_width="0.12", data_axis="spacing-mm")]
    spacings = [3.0, 2.0, 1.5, 1.0, 0.5]
    for idx, spacing in enumerate(spacings):
        bx = x + 8 + idx * 15
        by = y + 10
        body.append(_rect(bx, by, 12, 20, fill="none", stroke="#000", stroke_width="0.15", data_test=f"hatch-density-{spacing:g}mm"))
        n = 1
        while n * spacing < 12:
            body.append(_line(round(bx + n * spacing, 2), by, round(bx + n * spacing, 2), by + 20, stroke="#000", stroke_width="0.12"))
            n += 1
        body.append(_text(bx, y + 37, f"{spacing:g}mm", 2.0, font_family="monospace"))
    return _group("section-hatch-density", "Hatch Density", x, y, w, h, body)


def _curves_concentric() -> str:
    x, y, w, h = 10, 119, 90, 46
    body = [_line(x + 8, y + 39, x + 82, y + 39, stroke="#777", stroke_width="0.12", data_axis="spacing-mm")]
    body.append(_path(f"M {x+8} {y+18} C {x+19} {y+6}, {x+33} {y+6}, {x+44} {y+18} S {x+66} {y+30}, {x+80} {y+13}", fill="none", stroke="#000", stroke_width="0.22"))
    for idx, spacing in enumerate([3.0, 2.0, 1.5, 1.0, 0.5]):
        cx = x + 14 + idx * 15
        cy = y + 30
        radius = 1.5
        first = True
        while radius <= 6.0:
            body.append(_circle(cx, cy, round(radius, 2), fill="none", stroke="#000", stroke_width="0.12", data_test=f"concentric-spacing-{spacing:g}mm" if first else None))
            first = False
            radius += spacing
        body.append(_text(cx - 3, y + 43, f"{spacing:g}mm", 2.0, font_family="monospace"))
    return _group("section-curves-concentric", "Curves / Concentric", x, y, w, h, body)


def _text_sizes() -> str:
    x, y, w, h = 110, 119, 90, 46
    body = [_line(x + 8, y + 39, x + 82, y + 39, stroke="#777", stroke_width="0.12", data_axis="text-height-mm")]
    for idx, size in enumerate([4.0, 3.0, 2.0, 1.5, 1.0]):
        yy = y + 13 + idx * 6
        body.append(_text(x + 8, yy, "PPCT abc 123", size, font_family="monospace", data_test=f"text-size-{size:.1f}mm"))
        body.append(_text(x + 65, yy, f"{size:g}mm", 2.0, font_family="monospace"))
    return _group("section-text-sizes", "Minimum Text Size", x, y, w, h, body)


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


def _stipple_gradient() -> str:
    x, y, w, h = 10, 214, 90, 43
    body = [_line(x + 8, y + 36, x + 82, y + 36, stroke="#777", stroke_width="0.12", data_axis="stipple-density-percent")]
    for idx, density in enumerate([20, 40, 60, 80]):
        bx = x + 8 + idx * 19
        by = y + 10
        body.append(_rect(bx, by, 15, 20, fill="none", stroke="#000", stroke_width="0.12"))
        for n in range(density // 4):
            cx = bx + 1.5 + ((n * 5) % 12)
            cy = by + 1.5 + ((n * 7) % 17)
            body.append(_circle(round(cx, 2), round(cy, 2), 0.28, fill="none", stroke="#000", stroke_width="0.1", data_test=f"stipple-density-{density}" if n == 0 else None))
        body.append(_text(bx + 2, y + 35, f"{density}%", 2.0, font_family="monospace"))
    return _group("section-stipple-gradient", "Stipple Gradient", x, y, w, h, body)


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
        _resolution_wedges(),
        _hatch_density(),
        _curves_concentric(),
        _text_sizes(),
        _continuous_flow(),
        _stipple_gradient(),
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
