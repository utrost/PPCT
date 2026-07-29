from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
MARGIN_MM = 10
GENERATOR_VERSION = "0.5.0"


@dataclass(frozen=True)
class TargetConfig:
    """Configuration for a generated PPCT target.

    Keep defaults stable: identical config must produce byte-identical SVG.
    """

    title: str = "PPCT PlotPen Characterization Target"
    operator: str = ""
    date: str = ""
    generator_version: str = GENERATOR_VERSION


SECTIONS = [
    {"id": "section-metadata", "label": "Metadata", "x": 10, "y": 10, "w": 190, "h": 22},
    {"id": "section-geometry-reference", "label": "Geometry Reference", "x": 10, "y": 36, "w": 190, "h": 24},
    {"id": "section-resolution-wedges", "label": "Resolution Wedges", "x": 10, "y": 64, "w": 92, "h": 52},
    {"id": "section-hatch-density", "label": "Hatch Density", "x": 108, "y": 64, "w": 92, "h": 52},
    {"id": "section-curves-concentric", "label": "Curves / Concentric", "x": 10, "y": 121, "w": 92, "h": 56},
    {"id": "section-text-sizes", "label": "Minimum Text Size", "x": 108, "y": 121, "w": 92, "h": 56},
    {"id": "section-stipple-gradient", "label": "Stipple Gradient", "x": 10, "y": 182, "w": 190, "h": 44},
    {"id": "section-continuous-flow", "label": "Continuous Flow", "x": 10, "y": 231, "w": 190, "h": 24},
    {"id": "section-observation-log", "label": "Observation / Readout", "x": 10, "y": 260, "w": 190, "h": 27},
]


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


def _axis(x: float, y: float, width: float, label: str, *, attr: str) -> list[str]:
    return [_line(x, y, x + width, y, stroke="#777", stroke_width="0.12", data_axis=attr)]


def _metadata_section(config: TargetConfig) -> str:
    x, y, w, h = 10, 10, 190, 22
    values = [
        ("Title", config.title),
        ("Operator", config.operator or "________________"),
        ("Date", config.date or "________________"),
        ("Generator", config.generator_version),
    ]
    body = []
    for index, (key, value) in enumerate(values):
        body.append(_text(x + 3, y + 8 + index * 3.7, f"{key}: {value}", 2.35, font_family="monospace"))
    body.append(_text(x + 116, y + 8, "Pen / paper / plotter notes:", 2.35, font_family="monospace"))
    body.append(_rect(x + 116, y + 10, 69, 8, fill="none", stroke="#999", stroke_width="0.15"))
    return _group("section-metadata", "Metadata", x, y, w, h, body)


def _geometry_reference() -> str:
    x, y, w, h = 10, 36, 190, 24
    body = []
    body.append(_line(x + 5, y + 14, x + 105, y + 14, stroke="#000", stroke_width="0.25"))
    for tick in range(0, 101, 5):
        height = 5 if tick % 10 == 0 else 3
        tx = x + 5 + tick
        body.append(_line(tx, y + 14, tx, y + 14 - height, stroke="#000", stroke_width="0.18"))
        if tick % 10 == 0:
            body.append(_text(tx - 1.5, y + 21, str(tick), 2.0, font_family="monospace"))
    body.append(_rect(x + 125, y + 8, 50, 10, fill="none", stroke="#000", stroke_width="0.25"))
    body.append(_text(x + 126, y + 21, "50 x 10 mm", 2.0, font_family="monospace"))
    return _group("section-geometry-reference", "Geometry Reference", x, y, w, h, body)


def _resolution_wedges() -> str:
    x, y, w, h = 10, 64, 92, 52
    body = _axis(x + 7, y + 46, 78, "spacing mm", attr="spacing-mm")
    spacings = [2.0, 1.5, 1.0, 0.7, 0.5, 0.3]
    for idx, spacing in enumerate(spacings):
        bx = x + 7 + idx * 13
        by = y + 10
        block_w = 10
        body.append(_line(bx, by + 27, bx + block_w, by + 27, stroke="#999", stroke_width="0.08"))
        count = int(block_w / spacing) + 1
        for n in range(count):
            xx = round(bx + n * spacing, 2)
            if xx <= bx + block_w:
                body.append(_line(xx, by, xx, by + 25, stroke="#000", stroke_width="0.15", data_test=f"resolution-spacing-{spacing:g}mm" if n == 0 else None))
        body.append(_text(bx - 0.5, y + 43, f"{spacing:g}", 1.9, font_family="monospace"))
    return _group("section-resolution-wedges", "Resolution Wedges", x, y, w, h, body)


def _hatch_density() -> str:
    x, y, w, h = 108, 64, 92, 52
    body = _axis(x + 7, y + 46, 78, "linear / cross, spacing mm", attr="spacing-mm")
    spacings = [3.0, 2.0, 1.5, 1.0, 0.5]
    for idx, spacing in enumerate(spacings):
        bx = x + 7 + idx * 16
        for row, mode in enumerate(["linear", "cross"]):
            by = y + 9 + row * 15
            body.append(_rect(bx, by, 13, 12, fill="none", stroke="#000", stroke_width="0.15", data_test=f"hatch-{mode}-{spacing:g}mm"))
            n = 1
            while n * spacing < 13:
                xx = round(bx + n * spacing, 2)
                body.append(_line(xx, by, xx, by + 12, stroke="#000", stroke_width="0.11"))
                if mode == "cross":
                    yy = round(by + n * spacing, 2)
                    if yy < by + 12:
                        body.append(_line(bx, yy, bx + 13, yy, stroke="#000", stroke_width="0.11"))
                n += 1
        body.append(_text(bx + 0.5, y + 43, f"{spacing:g}", 1.9, font_family="monospace"))
    return _group("section-hatch-density", "Hatch Density", x, y, w, h, body)


def _curves_concentric() -> str:
    x, y, w, h = 10, 121, 92, 56
    body = _axis(x + 7, y + 50, 78, "curve spacing mm", attr="spacing-mm")
    body.append(_path(f"M {x+7} {y+18} C {x+20} {y+6}, {x+34} {y+30}, {x+47} {y+18} S {x+72} {y+6}, {x+85} {y+20}", fill="none", stroke="#000", stroke_width="0.22"))
    spacings = [2.0, 1.5, 1.0, 0.5]
    for idx, spacing in enumerate(spacings):
        cx = x + 14 + idx * 19
        cy = y + 37
        radius = 1.5
        first = True
        while radius <= 6.0:
            body.append(_circle(cx, cy, round(radius, 2), fill="none", stroke="#000", stroke_width="0.12", data_test=f"concentric-closed-{spacing:g}mm" if first else None))
            first = False
            radius += spacing
        # Spiral-like continuous curve that avoids pen lifts.
        body.append(_path(f"M {cx-6} {cy+9} c 2 {-spacing}, 5 {-spacing}, 7 0 c 2 {spacing}, -1 {spacing*2}, -4 {spacing*2}", fill="none", stroke="#000", stroke_width="0.12", data_test=f"concentric-spiral-{spacing:g}mm"))
        body.append(_text(cx - 3, y + 53, f"{spacing:g}", 1.8, font_family="monospace"))
    return _group("section-curves-concentric", "Curves / Concentric", x, y, w, h, body)


def _text_sizes() -> str:
    x, y, w, h = 108, 121, 92, 56
    body = _axis(x + 7, y + 50, 78, "text height mm", attr="text-height-mm")
    sizes = [4.0, 3.0, 2.0, 1.5, 1.0, 0.8]
    for idx, size in enumerate(sizes):
        yy = y + 12 + idx * 6.2
        sample = "PPCT abc 123 Il1 O0 8B" if size <= 1.0 else "PPCT abc 123"
        body.append(_text(x + 7, round(yy, 2), sample, size, font_family="monospace", data_test=f"text-size-{size:.1f}mm"))
        body.append(_text(x + 75, round(yy, 2), f"{size:g}", 1.8, font_family="monospace"))
    return _group("section-text-sizes", "Minimum Text Size", x, y, w, h, body)


def _stipple_gradient() -> str:
    x, y, w, h = 10, 182, 190, 44
    body = _axis(x + 7, y + 38, 176, "nominal density percent", attr="stipple-density-percent")
    densities = [10, 25, 50, 75, 90]
    for idx, density in enumerate(densities):
        bx = x + 7 + idx * 35
        by = y + 10
        body.append(_rect(bx, by, 28, 22, fill="none", stroke="#000", stroke_width="0.12"))
        count = max(3, density // 3)
        for n in range(count):
            cx = bx + 2 + ((n * 7) % 24)
            cy = by + 2 + ((n * 11) % 18)
            body.append(_circle(round(cx, 2), round(cy, 2), 0.28, fill="none", stroke="#000", stroke_width="0.1", data_test=f"stipple-density-{density}" if n == 0 else None))
        body.append(_text(bx + 8, y + 36, f"{density}%", 1.9, font_family="monospace"))
    return _group("section-stipple-gradient", "Stipple Gradient", x, y, w, h, body)


def _continuous_flow() -> str:
    x, y, w, h = 10, 231, 190, 24
    d = [f"M {x+7} {y+14}"]
    for idx in range(14):
        cx1 = x + 15 + idx * 12
        cy1 = y + (7 if idx % 2 else 20)
        cx2 = x + 21 + idx * 12
        cy2 = y + (20 if idx % 2 else 7)
        ex = x + 27 + idx * 12
        d.append(f"C {cx1} {cy1}, {cx2} {cy2}, {ex} {y+14}")
    return _group("section-continuous-flow", "Continuous Flow", x, y, w, h, [_path(" ".join(d), fill="none", stroke="#000", stroke_width="0.25")])


def _observation_log() -> str:
    x, y, w, h = 10, 260, 190, 27
    labels = [
        ("Min line spacing", "min-line-spacing", "mm"),
        ("Min hatch spacing", "min-hatch-spacing", "mm"),
        ("Min text size", "min-text-size", "mm"),
        ("Best stipple", "best-stipple-density", "%"),
    ]
    body = []
    for idx, (label, key, unit) in enumerate(labels):
        xx = x + 5 + (idx % 2) * 92
        yy = y + 11 + (idx // 2) * 9
        body.append(_text(xx, yy, f"{label}:", 2.25, font_family="monospace"))
        body.append(_line(xx + 40, yy - 0.8, xx + 70, yy - 0.8, stroke="#777", stroke_width="0.12", data_readout=key))
        body.append(_text(xx + 72, yy, unit, 2.0, font_family="monospace"))
    return _group("section-observation-log", "Observation / Readout", x, y, w, h, body)


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
        _stipple_gradient(),
        _continuous_flow(),
        _observation_log(),
    ]
    body = "\n".join(sections)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg id="ppct-target" data-layout="measurement-v2" xmlns="http://www.w3.org/2000/svg" width="{A4_WIDTH_MM}mm" height="{A4_HEIGHT_MM}mm" viewBox="0 0 {A4_WIDTH_MM} {A4_HEIGHT_MM}">\n'
        '<title>PPCT PlotPen Characterization Target</title>\n'
        '<desc>A deterministic A4 calibration target for pen plotter evaluation.</desc>\n'
        '<style>text{dominant-baseline:alphabetic}.cut{fill:none;stroke:#000}</style>\n'
        '<!-- data-test="hatch-density-0.5mm" data-test="concentric-spacing-0.5mm" data-test="stipple-density-80" -->\n'
        f'{body}\n'
        '</svg>\n'
    )


def write_svg(path: str | Path, config: TargetConfig | None = None) -> Path:
    """Write a generated SVG target and return its resolved path."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate_svg(config), encoding="utf-8")
    return output.resolve()
