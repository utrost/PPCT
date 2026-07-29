import json
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
        self.assertIn('href="./styles.css"', index)
        self.assertIn('src="./app.js"', index)
        self.assertIn('href="./manifest.webmanifest"', index)
        self.assertIn('id="title"', index)
        self.assertIn('id="operator"', index)
        self.assertIn('id="date"', index)
        self.assertIn('id="notes"', index)
        self.assertIn('id="include-text"', index)
        self.assertIn('id="download-svg"', index)
        self.assertIn('id="download-template-pdf"', index)
        self.assertIn('id="svg-preview"', index)

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
                "section-stroke-characterisation",
                "section-resolution-wedges",
                "section-hatch-density",
                "section-curves-corners",
                "section-continuous-flow",
                "section-pen-lift-reliability",
                "section-observation-log",
            }.issubset(ids)
        )

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
        self.assertNotIn("Curves &amp; Corners", payload["geometryOnly"])
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
        for parent in root.iter():
            for child in list(parent):
                if child.tag.endswith("text"):
                    text_parent_ids.append(parent.attrib.get("id"))
        self.assertTrue(text_parent_ids)
        self.assertTrue(all(parent_id == "layer-template" for parent_id in text_parent_ids))
        self.assertNotIn('id="layer-template"', payload["plotOnly"])
        self.assertIn('id="layer-plot-data"', payload["plotOnly"])
        self.assertEqual(payload["pdfPrefix"], "%PDF-1.4")
        self.assertTrue(payload["pdfHasLabel"])


if __name__ == "__main__":
    unittest.main()
