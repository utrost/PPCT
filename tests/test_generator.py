import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET


class TargetGenerationTests(unittest.TestCase):
    def test_default_target_is_a4_svg_with_named_calibration_sections(self):
        from ppct import TargetConfig, generate_svg

        svg = generate_svg(TargetConfig(title="Test sheet", operator="Hermes"))
        root = ET.fromstring(svg)

        self.assertEqual(root.tag.split("}")[-1], "svg")
        self.assertEqual(root.attrib["width"], "210mm")
        self.assertEqual(root.attrib["height"], "297mm")
        self.assertEqual(root.attrib["viewBox"], "0 0 210 297")

        ids = {element.attrib.get("id") for element in root.iter()}
        expected = {
            "ppct-target",
            "section-metadata",
            "section-geometry-reference",
            "section-resolution-wedges",
            "section-hatch-density",
            "section-curves-concentric",
            "section-text-sizes",
            "section-continuous-flow",
            "section-stipple-gradient",
            "section-observation-log",
        }
        self.assertTrue(expected.issubset(ids))
        self.assertNotIn("section-stroke-characterisation", ids)
        self.assertNotIn("section-pen-lift-reliability", ids)

    def test_target_has_readable_axes_and_new_pen_diagnostics(self):
        from ppct import TargetConfig, generate_svg

        svg = generate_svg(TargetConfig(title="Diagnostics"))

        self.assertIn("0.5mm", svg)
        self.assertIn('data-test="hatch-density-0.5mm"', svg)
        self.assertIn('data-test="concentric-spacing-0.5mm"', svg)
        self.assertIn('data-test="text-size-1.0mm"', svg)
        self.assertIn('data-test="stipple-density-80"', svg)
        self.assertIn('data-axis="spacing-mm"', svg)
        self.assertIn('data-axis="text-height-mm"', svg)
        self.assertIn('data-axis="stipple-density-percent"', svg)
        self.assertNotIn("Stroke Characterisation", svg)
        self.assertNotIn("Pen Lift Reliability", svg)

    def test_target_second_pass_is_measurement_oriented(self):
        from ppct import TargetConfig, generate_svg

        svg = generate_svg(TargetConfig(title="Measurement ergonomics"))

        self.assertIn('data-layout="measurement-v2"', svg)
        self.assertIn('data-test="hatch-linear-0.5mm"', svg)
        self.assertIn('data-test="hatch-cross-0.5mm"', svg)
        self.assertIn('data-test="text-size-0.8mm"', svg)
        self.assertIn("Il1 O0 8B", svg)
        self.assertIn('data-test="concentric-closed-0.5mm"', svg)
        self.assertIn('data-test="concentric-spiral-0.5mm"', svg)
        self.assertIn('data-test="stipple-density-90"', svg)
        self.assertIn('data-readout="min-line-spacing"', svg)
        self.assertIn('data-readout="min-hatch-spacing"', svg)
        self.assertIn('data-readout="min-text-size"', svg)
        self.assertIn('data-readout="best-stipple-density"', svg)
        self.assertIn("Min line spacing", svg)
        self.assertIn("Best stipple", svg)

    def test_generation_is_deterministic_for_identical_config(self):
        from ppct import TargetConfig, generate_svg

        config = TargetConfig(title="Deterministic", operator="Uwe", date="2026-07-29")
        first = generate_svg(config)
        second = generate_svg(config)

        self.assertEqual(first, second)
        self.assertEqual(hashlib.sha256(first.encode("utf-8")).hexdigest(), hashlib.sha256(second.encode("utf-8")).hexdigest())

    def test_cli_writes_svg_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "ppct.svg"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ppct.cli",
                    "--output",
                    str(output),
                    "--title",
                    "CLI sheet",
                    "--operator",
                    "Hermes",
                    "--date",
                    "2026-07-29",
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists())
            text = output.read_text(encoding="utf-8")
            self.assertIn("CLI sheet", text)
            self.assertIn("section-geometry-reference", text)
            self.assertIn(str(output), result.stdout)


if __name__ == "__main__":
    unittest.main()
