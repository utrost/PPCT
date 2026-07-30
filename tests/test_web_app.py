import json
import re
import subprocess
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


class WebGeneratorTests(unittest.TestCase):
    def test_web_app_has_expected_entrypoints(self):
        index = (WEB / "index.html").read_text(encoding="utf-8")

        self.assertIn("PPCT Web Generator", index)
        self.assertIn('name="viewport"', index)
        self.assertIn('href="./styles.css?v=0.5.2"', index)
        self.assertIn('src="./app.js?v=0.5.2"', index)
        self.assertIn('href="./manifest.webmanifest"', index)
        self.assertIn('id="title"', index)
        self.assertIn('id="operator"', index)
        self.assertIn('id="date"', index)
        self.assertIn('id="notes"', index)
        self.assertIn('id="include-text"', index)
        self.assertIn('id="preview-both"', index)
        self.assertIn('id="preview-plot"', index)
        self.assertIn('id="svg-preview-image"', index)
        self.assertIn('id="download-svg"', index)
        self.assertIn('id="download-template-pdf"', index)
        self.assertIn('id="svg-preview"', index)

    def test_service_worker_prefers_network_and_claims_updates(self):
        service_worker = (WEB / "sw.js").read_text(encoding="utf-8")

        self.assertIn("ppct-web-v0.5.2", service_worker)
        self.assertIn("self.skipWaiting()", service_worker)
        self.assertIn("self.clients.claim()", service_worker)
        self.assertLess(service_worker.index("fetch(request)"), service_worker.index("caches.match(request)"))

    def test_manifest_is_valid_for_subdirectory_deployments(self):
        manifest = json.loads((WEB / "manifest.webmanifest").read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "PPCT Web Generator")
        self.assertEqual(manifest["short_name"], "PPCT")
        self.assertEqual(manifest["start_url"], "./")
        self.assertEqual(manifest["scope"], "./")
        self.assertEqual(manifest["display"], "standalone")
        self.assertGreaterEqual(len(manifest["icons"]), 1)

    def test_browser_generator_exports_a4_svg_with_required_sections(self):
        script = """
        const { readFileSync } = require('fs');
        const vm = require('vm');
        const code = readFileSync('web/app.js', 'utf8');
        const context = { window: {}, document: { addEventListener() {} }, URL, Blob, console };
        vm.createContext(context);
        vm.runInContext(code, context);
        const svg = context.window.PPCT.generateSvg({ title: 'Web test', operator: 'Hermes', date: '2026-07-29' });
        console.log(svg);
        """
        result = subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        svg = result.stdout
        root = ET.fromstring(svg)
        self.assertEqual(root.attrib["width"], "210mm")
        self.assertEqual(root.attrib["height"], "297mm")
        self.assertEqual(root.attrib["viewBox"], "0 0 210 297")
        ids = {element.attrib.get("id") for element in root.iter()}
        self.assertTrue(
            {
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
            }.issubset(ids)
        )
        self.assertNotIn("section-stroke-characterisation", ids)
        self.assertNotIn("section-pen-lift-reliability", ids)

    def test_browser_target_contains_new_pen_readability_diagnostics(self):
        script = """
        const { readFileSync } = require('fs');
        const vm = require('vm');
        const code = readFileSync('web/app.js', 'utf8');
        const context = { window: {}, document: { addEventListener() {} }, URL, Blob, console };
        vm.createContext(context);
        vm.runInContext(code, context);
        const svg = context.window.PPCT.generateSvg({ title: 'Diagnostics' });
        const pdf = context.window.PPCT.generateTemplatePdf({ title: 'Diagnostics' });
        console.log(JSON.stringify({ svg, pdf }));
        """
        result = subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        svg = payload["svg"]
        self.assertIn("0.5mm", svg)
        self.assertIn("section-curves-concentric", svg)
        self.assertIn("section-text-sizes", svg)
        self.assertIn("section-stipple-gradient", svg)
        self.assertIn("data-test=\"hatch-density-0.5mm\"", svg)
        self.assertIn("data-test=\"concentric-spacing-0.5mm\"", svg)
        self.assertIn("data-test=\"text-size-1.0mm\"", svg)
        self.assertIn("data-test=\"stipple-density-80\"", svg)
        self.assertIn("data-axis=\"spacing-mm\"", svg)
        self.assertIn("data-axis=\"text-height-mm\"", svg)
        self.assertIn("data-axis=\"stipple-density-percent\"", svg)
        self.assertNotIn("Stroke Characterisation", svg)
        self.assertNotIn("Pen Lift Reliability", svg)
        self.assertIn("Hatch Density", payload["pdf"])
        self.assertIn("0.5", payload["pdf"])
        self.assertIn("Minimum Text Size", payload["pdf"])
        self.assertIn("Stipple Gradient", payload["pdf"])

    def test_browser_target_second_pass_measurement_ergonomics(self):
        script = """
        const { readFileSync } = require('fs');
        const vm = require('vm');
        const code = readFileSync('web/app.js', 'utf8');
        const context = { window: {}, document: { addEventListener() {} }, URL, Blob, console };
        vm.createContext(context);
        vm.runInContext(code, context);
        const svg = context.window.PPCT.generateSvg({ title: 'Measurement ergonomics' });
        const pdf = context.window.PPCT.generateTemplatePdf({ title: 'Measurement ergonomics' });
        console.log(JSON.stringify({ svg, pdf }));
        """
        result = subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        svg = payload["svg"]
        self.assertIn('data-layout="measurement-v2"', svg)
        self.assertIn('data-test="hatch-linear-0.5mm"', svg)
        self.assertIn('data-test="hatch-cross-0.5mm"', svg)
        self.assertIn('data-test="text-size-6.0mm"', svg)
        self.assertIn('data-test="text-size-5.0mm"', svg)
        self.assertIn('data-test="text-size-0.8mm"', svg)
        self.assertIn("Il1 O0 8B", svg)
        self.assertIn('data-test="concentric-closed-0.5mm"', svg)
        self.assertIn('data-test="concentric-spiral-0.5mm"', svg)
        self.assertIn('data-test="stipple-density-90"', svg)
        self.assertIn('data-readout="min-line-spacing"', svg)
        self.assertIn('data-readout="min-hatch-spacing"', svg)
        self.assertIn('data-readout="min-text-size"', svg)
        self.assertIn('data-readout="best-stipple-density"', svg)
        self.assertIn("Min line spacing", payload["pdf"])
        self.assertIn("Best stipple", payload["pdf"])

    def test_browser_post_print_findings_add_large_text_and_dense_stipple(self):
        script = """
        const { readFileSync } = require('fs');
        const vm = require('vm');
        const code = readFileSync('web/app.js', 'utf8');
        const context = { window: {}, document: { addEventListener() {} }, URL, Blob, console };
        vm.createContext(context);
        vm.runInContext(code, context);
        const svg = context.window.PPCT.generateSvg({ title: 'Printed sheet findings' });
        const pdf = context.window.PPCT.generateTemplatePdf({ title: 'Printed sheet findings' });
        console.log(JSON.stringify({ svg, pdf }));
        """
        result = subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        svg = payload["svg"]
        self.assertIn('data-test="text-size-6.0mm"', svg)
        self.assertIn('data-test="text-size-5.0mm"', svg)
        self.assertIn("6", payload["pdf"])
        self.assertIn("5", payload["pdf"])
        counts = {
            int(density): len(re.findall(rf'data-stipple-density="{density}"', svg))
            for density in [10, 25, 50, 75, 90]
        }
        self.assertGreaterEqual(counts[10], 15)
        self.assertGreaterEqual(counts[25], 40)
        self.assertGreaterEqual(counts[50], 80)
        self.assertGreaterEqual(counts[75], 125)
        self.assertGreaterEqual(counts[90], 150)

    def test_browser_generator_can_print_notes_and_omit_plotted_text(self):
        script = """
        const { readFileSync } = require('fs');
        const vm = require('vm');
        const code = readFileSync('web/app.js', 'utf8');
        const context = { window: {}, document: { addEventListener() {} }, URL, Blob, console };
        vm.createContext(context);
        vm.runInContext(code, context);
        const withNotes = context.window.PPCT.generateSvg({
          title: 'Web test',
          operator: 'Hermes',
          date: '2026-07-29',
          notes: 'Pilot G2 / Clairefontaine / iDraw H',
        });
        const geometryOnly = context.window.PPCT.generateSvg({ includeText: false });
        console.log(JSON.stringify({ withNotes, geometryOnly }));
        """
        result = subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("Pilot G2 / Clairefontaine / iDraw H", payload["withNotes"])
        self.assertIn("Pen / paper / plotter notes:", payload["withNotes"])
        self.assertIn("id=\"layer-template\"", payload["withNotes"])
        self.assertIn("id=\"layer-plot-data\"", payload["withNotes"])
        self.assertIn("section-geometry-reference", payload["geometryOnly"])
        self.assertIn("section-curves-concentric", payload["geometryOnly"])
        self.assertIn("data-test=\"text-size-1.0mm\"", payload["geometryOnly"])
        self.assertNotIn("Pen / paper / plotter notes:", payload["geometryOnly"])

    def test_svg_has_template_and_plot_data_layers(self):
        script = """
        const { readFileSync } = require('fs');
        const vm = require('vm');
        const code = readFileSync('web/app.js', 'utf8');
        const context = { window: {}, document: { addEventListener() {} }, URL, Blob, console };
        vm.createContext(context);
        vm.runInContext(code, context);
        const layered = context.window.PPCT.generateSvg({ title: 'Layer test' });
        const plotOnly = context.window.PPCT.generateSvg({ includeText: false });
        const pdf = context.window.PPCT.generateTemplatePdf({ title: 'Layer test' });
        console.log(JSON.stringify({ layered, plotOnly, pdfPrefix: pdf.slice(0, 8), pdfHasLabel: pdf.includes('PPCT printable template') }));
        """
        result = subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        root = ET.fromstring(payload["layered"])
        ids = {element.attrib.get("id") for element in root.iter()}
        self.assertIn("layer-template", ids)
        self.assertIn("layer-plot-data", ids)
        text_parent_ids = []
        text_size_line_count = 0
        for parent in root.iter():
            for child in list(parent):
                if child.tag.endswith("text"):
                    text_parent_ids.append(parent.attrib.get("id"))
                if parent.attrib.get("id") == "section-text-sizes" and child.tag.endswith("g"):
                    text_size_line_count += sum(1 for grandchild in child if grandchild.tag.endswith("line"))
        self.assertTrue(text_parent_ids)
        self.assertTrue(all(parent_id == "layer-template" for parent_id in text_parent_ids))
        self.assertGreater(text_size_line_count, 0)
        self.assertIn('data-sample="Il1 O0 8B"', payload["layered"])
        self.assertNotIn('id="layer-template"', payload["plotOnly"])
        self.assertIn('id="layer-plot-data"', payload["plotOnly"])
        self.assertEqual(payload["pdfPrefix"], "%PDF-1.4")
        self.assertTrue(payload["pdfHasLabel"])

    def test_preview_uses_image_data_url_for_firefox_compatibility(self):
        app = (WEB / "app.js").read_text(encoding="utf-8")
        styles = (WEB / "styles.css").read_text(encoding="utf-8")

        self.assertIn("function svgDataUrl(svg)", app)
        self.assertIn("encodeURIComponent(svg)", app)
        self.assertIn("svg-preview-image", app)
        self.assertNotIn("preview.innerHTML = generateSvg", app)
        self.assertIn("input[name=\"preview-layers\"]", app)
        self.assertIn(".svg-preview img", styles)

    def test_archive_templates_are_documented(self):
        metadata = (ROOT / "docs" / "templates" / "metadata.md").read_text(encoding="utf-8")
        notes = (ROOT / "docs" / "templates" / "notes.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        user_guide = (ROOT / "docs" / "user-guide.md").read_text(encoding="utf-8")

        self.assertIn("Generated SVG SHA-256", metadata)
        self.assertIn("Minimum separate line spacing", metadata)
        self.assertIn("Section observations", notes)
        self.assertIn("Continuous flow", notes)
        self.assertIn("docs/templates/metadata.md", readme)
        self.assertIn("sha256sum ppct-a4.svg", user_guide)


if __name__ == "__main__":
    unittest.main()
