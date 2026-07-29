(() => {
  const A4_WIDTH = 210;
  const A4_HEIGHT = 297;
  const PT_PER_MM = 72 / 25.4;

  function escapeXml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&apos;');
  }

  function escapePdf(value) {
    return String(value ?? '')
      .replaceAll('\\', '\\\\')
      .replaceAll('(', '\\(')
      .replaceAll(')', '\\)')
      .replaceAll('\r', ' ')
      .replaceAll('\n', ' ');
  }

  function attrs(values) {
    return Object.entries(values)
      .filter(([, value]) => value !== undefined && value !== null)
      .map(([key, value]) => `${key.replaceAll('_', '-')}="${escapeXml(value)}"`)
      .join(' ');
  }

  function line(x1, y1, x2, y2, extra = {}) {
    return `<line ${attrs({ x1, y1, x2, y2, ...extra })} />`;
  }

  function rect(x, y, width, height, extra = {}) {
    return `<rect ${attrs({ x, y, width, height, ...extra })} />`;
  }

  function circle(cx, cy, r, extra = {}) {
    return `<circle ${attrs({ cx, cy, r, ...extra })} />`;
  }

  function path(d, extra = {}) {
    return `<path ${attrs({ d, ...extra })} />`;
  }

  function text(x, y, content, size = 3, extra = {}) {
    return `<text ${attrs({ x, y, 'font-size': size, ...extra })}>${escapeXml(content)}</text>`;
  }

  function styleFor(kind) {
    if (kind === 'template') return { fill: 'none', stroke: '#999', 'stroke-width': '0.15' };
    if (kind === 'guide') return { fill: 'none', stroke: '#bbb', 'stroke-width': '0.2' };
    if (kind === 'write') return { stroke: '#777', 'stroke-width': '0.12' };
    return { stroke: '#000', 'stroke-width': '0.2' };
  }

  const sections = [
    { id: 'section-metadata', label: 'Metadata', x: 10, y: 10, w: 190, h: 24 },
    { id: 'section-geometry-reference', label: 'Geometry Reference', x: 10, y: 39, w: 190, h: 28 },
    { id: 'section-resolution-wedges', label: 'Resolution Wedges', x: 10, y: 72, w: 90, h: 42 },
    { id: 'section-hatch-density', label: 'Hatch Density', x: 110, y: 72, w: 90, h: 42 },
    { id: 'section-curves-concentric', label: 'Curves / Concentric', x: 10, y: 119, w: 90, h: 46 },
    { id: 'section-text-sizes', label: 'Minimum Text Size', x: 110, y: 119, w: 90, h: 46 },
    { id: 'section-continuous-flow', label: 'Continuous Flow', x: 10, y: 170, w: 190, h: 39 },
    { id: 'section-stipple-gradient', label: 'Stipple Gradient', x: 10, y: 214, w: 90, h: 43 },
    { id: 'section-observation-log', label: 'Observation Log', x: 110, y: 214, w: 90, h: 43 },
  ];

  function templateLayer(config) {
    const items = [
      text(10, 6, 'PPCT printable template. Print at 100%. Plot the data layer on top.', 2.3, { 'font-family': 'monospace', fill: '#555' }),
    ];

    sections.forEach((section) => {
      items.push(rect(section.x, section.y, section.w, section.h, styleFor('guide')));
      items.push(text(section.x + 2, section.y + 4, section.label, 2.8, { fill: '#111', 'font-family': 'monospace' }));
    });

    const mx = 10, my = 10;
    const rows = [
      ['Title', config.title || 'PPCT A4 Reference'],
      ['Operator', config.operator || '________________'],
      ['Date', config.date || '________________'],
      ['Generator', 'web-0.4.0'],
    ];
    rows.forEach(([key, value], index) => {
      items.push(text(mx + 3, my + 9 + index * 4, `${key}: ${value}`, 2.6, { 'font-family': 'monospace' }));
    });
    items.push(text(mx + 115, my + 9, 'Pen / paper / plotter notes:', 2.6, { 'font-family': 'monospace' }));
    items.push(rect(mx + 115, my + 11, 70, 9, styleFor('template')));
    const notes = (config.notes || '').trim();
    if (notes) {
      const shortNotes = notes.length > 46 ? `${notes.slice(0, 43)}...` : notes;
      items.push(text(mx + 117, my + 17, shortNotes, 2.3, { 'font-family': 'monospace' }));
    }

    const gx = 10, gy = 39;
    for (let tick = 0; tick <= 100; tick += 10) {
      items.push(text(gx + 5 + tick - 1.5, gy + 23, tick, 2.2, { 'font-family': 'monospace' }));
    }
    items.push(text(gx + 126, gy + 23, '50 x 10 mm box', 2.2, { 'font-family': 'monospace' }));

    [2, 1.5, 1, 0.7, 0.5, 0.3].forEach((spacing, index) => {
      items.push(text(18 + index * 12, 109, `${spacing}mm`, 2, { 'font-family': 'monospace' }));
    });
    [3, 2, 1.5, 1, 0.5].forEach((spacing, index) => {
      items.push(text(118 + index * 15, 109, `${spacing}mm`, 2, { 'font-family': 'monospace' }));
    });
    [3, 2, 1.5, 1, 0.5].forEach((spacing, index) => {
      items.push(text(21 + index * 15, 162, `${spacing}mm`, 2, { 'font-family': 'monospace' }));
    });
    [4, 3, 2, 1.5, 1].forEach((size, index) => {
      items.push(text(175, 132 + index * 6, `${size}mm`, 2, { 'font-family': 'monospace' }));
    });
    [20, 40, 60, 80].forEach((density, index) => {
      items.push(text(20 + index * 19, 250, `${density}%`, 2, { 'font-family': 'monospace' }));
    });

    ['Line quality', 'Start/end', 'Feather/bleed', 'Suitability'].forEach((label, index) => {
      const yy = 226 + index * 7;
      items.push(text(114, yy, `${label}:`, 2.4, { 'font-family': 'monospace' }));
      items.push(line(142, yy - 0.8, 194, yy - 0.8, styleFor('write')));
    });

    return `<g id="layer-template" data-layer="template" inkscape:groupmode="layer" inkscape:label="Template / print first">\n${items.join('\n')}\n</g>`;
  }

  function plotSection(sectionId, body) {
    return `<g id="${sectionId}" data-layer="plot-data">\n${body.join('\n')}\n</g>`;
  }

  function metadataPlotData() {
    return plotSection('section-metadata', []);
  }

  function geometryReference() {
    const x = 10, y = 39;
    const body = [line(x + 5, y + 16, x + 105, y + 16, { stroke: '#000', 'stroke-width': '0.25' })];
    for (let tick = 0; tick <= 100; tick += 5) {
      const height = tick % 10 === 0 ? 5 : 3;
      const tx = x + 5 + tick;
      body.push(line(tx, y + 16, tx, y + 16 - height, { stroke: '#000', 'stroke-width': '0.18' }));
    }
    body.push(rect(x + 125, y + 9, 50, 10, { fill: 'none', stroke: '#000', 'stroke-width': '0.25' }));
    return plotSection('section-geometry-reference', body);
  }

  function resolutionWedges() {
    const x = 10, y = 72;
    const spacings = [2, 1.5, 1, 0.7, 0.5, 0.3];
    const body = [line(x + 8, y + 34, x + 82, y + 34, { stroke: '#777', 'stroke-width': '0.12', 'data-axis': 'spacing-mm' })];
    spacings.forEach((spacing, index) => {
      const startX = x + 8 + index * 12;
      const yy = y + 10;
      const count = Math.floor(22 / spacing);
      for (let n = 0; n < count; n += 1) {
        const xx = Math.round((startX + n * spacing) * 100) / 100;
        body.push(line(xx, yy, xx, yy + 20, { stroke: '#000', 'stroke-width': '0.15' }));
      }
    });
    return plotSection('section-resolution-wedges', body);
  }

  function hatchDensity() {
    const x = 110, y = 72;
    const body = [line(x + 8, y + 34, x + 84, y + 34, { stroke: '#777', 'stroke-width': '0.12', 'data-axis': 'spacing-mm' })];
    [3, 2, 1.5, 1, 0.5].forEach((spacing, index) => {
      const bx = x + 8 + index * 15;
      const by = y + 10;
      body.push(rect(bx, by, 12, 20, { fill: 'none', stroke: '#000', 'stroke-width': '0.15', 'data-test': `hatch-density-${spacing}mm` }));
      for (let n = 1; n * spacing < 12; n += 1) {
        const xx = Math.round((bx + n * spacing) * 100) / 100;
        body.push(line(xx, by, xx, by + 20, { stroke: '#000', 'stroke-width': '0.12' }));
      }
    });
    return plotSection('section-hatch-density', body);
  }

  function curvesConcentric() {
    const x = 10, y = 119;
    const body = [line(x + 8, y + 39, x + 82, y + 39, { stroke: '#777', 'stroke-width': '0.12', 'data-axis': 'spacing-mm' })];
    body.push(path(`M ${x + 8} ${y + 18} C ${x + 19} ${y + 6}, ${x + 33} ${y + 6}, ${x + 44} ${y + 18} S ${x + 66} ${y + 30}, ${x + 80} ${y + 13}`, { fill: 'none', stroke: '#000', 'stroke-width': '0.22' }));
    [3, 2, 1.5, 1, 0.5].forEach((spacing, index) => {
      const cx = x + 14 + index * 15;
      const cy = y + 30;
      let first = true;
      for (let radius = 1.5; radius <= 6; radius += spacing) {
        body.push(circle(cx, cy, Math.round(radius * 100) / 100, { fill: 'none', stroke: '#000', 'stroke-width': '0.12', 'data-test': first ? `concentric-spacing-${spacing}mm` : undefined }));
        first = false;
      }
    });
    return plotSection('section-curves-concentric', body);
  }

  function textSizes() {
    const x = 110, y = 119;
    const body = [line(x + 8, y + 39, x + 82, y + 39, { stroke: '#777', 'stroke-width': '0.12', 'data-axis': 'text-height-mm' })];
    [4, 3, 2, 1.5, 1].forEach((size, index) => {
      const yy = y + 13 + index * 6;
      body.push(text(x + 8, yy, 'PPCT abc 123', size, { 'font-family': 'monospace', 'data-test': `text-size-${size.toFixed(1)}mm` }));
    });
    return plotSection('section-text-sizes', body);
  }

  function continuousFlow() {
    const x = 10, y = 170;
    const segments = [`M ${x + 8} ${y + 22}`];
    for (let index = 0; index < 14; index += 1) {
      const cx1 = x + 16 + index * 12;
      const cy1 = y + (index % 2 ? 8 : 34);
      const cx2 = x + 22 + index * 12;
      const cy2 = y + (index % 2 ? 34 : 8);
      const ex = x + 28 + index * 12;
      segments.push(`C ${cx1} ${cy1}, ${cx2} ${cy2}, ${ex} ${y + 22}`);
    }
    return plotSection('section-continuous-flow', [
      path(segments.join(' '), { fill: 'none', stroke: '#000', 'stroke-width': '0.25' }),
    ]);
  }

  function stippleGradient() {
    const x = 10, y = 214;
    const body = [line(x + 8, y + 36, x + 82, y + 36, { stroke: '#777', 'stroke-width': '0.12', 'data-axis': 'stipple-density-percent' })];
    [20, 40, 60, 80].forEach((density, index) => {
      const bx = x + 8 + index * 19;
      const by = y + 10;
      body.push(rect(bx, by, 15, 20, { fill: 'none', stroke: '#000', 'stroke-width': '0.12' }));
      for (let n = 0; n < density / 4; n += 1) {
        const cx = bx + 1.5 + ((n * 5) % 12);
        const cy = by + 1.5 + ((n * 7) % 17);
        body.push(circle(Math.round(cx * 100) / 100, Math.round(cy * 100) / 100, 0.28, { fill: 'none', stroke: '#000', 'stroke-width': '0.1', 'data-test': n === 0 ? `stipple-density-${density}` : undefined }));
      }
    });
    return plotSection('section-stipple-gradient', body);
  }

  function observationLogPlotData() {
    return plotSection('section-observation-log', []);
  }

  function plotDataLayer() {
    return `<g id="layer-plot-data" data-layer="plot-data" inkscape:groupmode="layer" inkscape:label="Plot data / draw second">\n${[
      metadataPlotData(),
      geometryReference(),
      resolutionWedges(),
      hatchDensity(),
      curvesConcentric(),
      textSizes(),
      continuousFlow(),
      stippleGradient(),
      observationLogPlotData(),
    ].join('\n')}\n</g>`;
  }

  function generateSvg(config = {}) {
    const includeTemplate = config.includeText !== false;
    const layers = [];
    if (includeTemplate) layers.push(templateLayer(config));
    layers.push(plotDataLayer());

    return `<?xml version="1.0" encoding="UTF-8"?>\n<svg id="ppct-target" xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="${A4_WIDTH}mm" height="${A4_HEIGHT}mm" viewBox="0 0 ${A4_WIDTH} ${A4_HEIGHT}">\n<title>PPCT PlotPen Characterization Target</title>\n<desc>A browser-generated A4 calibration target with separate printable-template and plot-data layers.</desc>\n<style>text{dominant-baseline:alphabetic}.cut{fill:none;stroke:#000}</style>\n${layers.join('\n')}\n</svg>\n`;
  }

  function pdfLine(x1, y1, x2, y2) {
    const px1 = x1 * PT_PER_MM;
    const py1 = (A4_HEIGHT - y1) * PT_PER_MM;
    const px2 = x2 * PT_PER_MM;
    const py2 = (A4_HEIGHT - y2) * PT_PER_MM;
    return `${px1.toFixed(2)} ${py1.toFixed(2)} m ${px2.toFixed(2)} ${py2.toFixed(2)} l S`;
  }

  function pdfRect(x, y, w, h) {
    const px = x * PT_PER_MM;
    const py = (A4_HEIGHT - y - h) * PT_PER_MM;
    return `${px.toFixed(2)} ${py.toFixed(2)} ${(w * PT_PER_MM).toFixed(2)} ${(h * PT_PER_MM).toFixed(2)} re S`;
  }

  function pdfText(x, y, content, size = 8) {
    const px = x * PT_PER_MM;
    const py = (A4_HEIGHT - y) * PT_PER_MM;
    return `BT /F1 ${size.toFixed(1)} Tf ${px.toFixed(2)} ${py.toFixed(2)} Td (${escapePdf(content)}) Tj ET`;
  }

  function generateTemplatePdf(config = {}) {
    const commands = ['0.6 w', '0.45 0.45 0.45 RG'];
    commands.push(pdfText(10, 6, 'PPCT printable template. Print at 100%. Plot the SVG data layer on top.', 6.5));
    sections.forEach((section) => {
      commands.push(pdfRect(section.x, section.y, section.w, section.h));
      commands.push(pdfText(section.x + 2, section.y + 4, section.label, 8));
    });
    const rows = [
      ['Title', config.title || 'PPCT A4 Reference'],
      ['Operator', config.operator || '________________'],
      ['Date', config.date || '________________'],
      ['Generator', 'web-0.4.0'],
    ];
    rows.forEach(([key, value], index) => commands.push(pdfText(13, 19 + index * 4, `${key}: ${value}`, 7)));
    commands.push(pdfText(125, 19, 'Pen / paper / plotter notes:', 7));
    commands.push(pdfRect(125, 21, 70, 9));
    const notes = (config.notes || '').trim();
    if (notes) commands.push(pdfText(127, 27, notes.length > 46 ? `${notes.slice(0, 43)}...` : notes, 6.5));
    for (let tick = 0; tick <= 100; tick += 10) commands.push(pdfText(13.5 + tick, 62, tick, 6));
    commands.push(pdfText(136, 62, '50 x 10 mm box', 6));
    [2, 1.5, 1, 0.7, 0.5, 0.3].forEach((spacing, index) => commands.push(pdfText(18 + index * 12, 109, `${spacing}mm`, 6)));
    [3, 2, 1.5, 1, 0.5].forEach((spacing, index) => commands.push(pdfText(118 + index * 15, 109, `${spacing}mm`, 6)));
    [3, 2, 1.5, 1, 0.5].forEach((spacing, index) => commands.push(pdfText(21 + index * 15, 162, `${spacing}mm`, 6)));
    [4, 3, 2, 1.5, 1].forEach((size, index) => commands.push(pdfText(175, 132 + index * 6, `${size}mm`, 6)));
    [20, 40, 60, 80].forEach((density, index) => commands.push(pdfText(20 + index * 19, 250, `${density}%`, 6)));
    ['Line quality', 'Start/end', 'Feather/bleed', 'Suitability'].forEach((label, index) => {
      const yy = 226 + index * 7;
      commands.push(pdfText(114, yy, `${label}:`, 7));
      commands.push(pdfLine(142, yy - 0.8, 194, yy - 0.8));
    });

    const stream = commands.join('\n');
    const objects = [
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${(A4_WIDTH * PT_PER_MM).toFixed(2)} ${(A4_HEIGHT * PT_PER_MM).toFixed(2)}] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>`,
      '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
      `<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`,
    ];
    const chunks = ['%PDF-1.4\n'];
    const offsets = [0];
    objects.forEach((object, index) => {
      offsets.push(chunks.join('').length);
      chunks.push(`${index + 1} 0 obj\n${object}\nendobj\n`);
    });
    const xrefOffset = chunks.join('').length;
    chunks.push(`xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`);
    offsets.slice(1).forEach((offset) => chunks.push(`${String(offset).padStart(10, '0')} 00000 n \n`));
    chunks.push(`trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`);
    return chunks.join('');
  }

  function filenameFor(config, extension = 'svg') {
    const date = (config.date || new Date().toISOString().slice(0, 10)).replace(/[^0-9-]/g, '');
    return `ppct-a4-${date}.${extension}`;
  }

  function currentConfig() {
    return {
      title: document.getElementById('title')?.value || 'PPCT A4 Reference',
      operator: document.getElementById('operator')?.value || '',
      date: document.getElementById('date')?.value || new Date().toISOString().slice(0, 10),
      notes: document.getElementById('notes')?.value || '',
      includeText: document.getElementById('include-text')?.checked !== false,
    };
  }

  function previewConfig() {
    const config = currentConfig();
    const mode = document.querySelector('input[name="preview-layers"]:checked')?.value || 'both';
    if (mode === 'plot') config.includeText = false;
    return config;
  }

  function svgDataUrl(svg) {
    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
  }

  function render() {
    const previewImage = document.getElementById('svg-preview-image');
    if (!previewImage) return;
    previewImage.src = svgDataUrl(generateSvg(previewConfig()));
  }

  function downloadBlob(content, type, filename) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function downloadSvg() {
    const config = currentConfig();
    downloadBlob(generateSvg(config), 'image/svg+xml', filenameFor(config, 'svg'));
  }

  function downloadTemplatePdf() {
    const config = currentConfig();
    downloadBlob(generateTemplatePdf(config), 'application/pdf', filenameFor(config, 'template.pdf'));
  }

  function resetForm() {
    const date = new Date().toISOString().slice(0, 10);
    document.getElementById('title').value = 'PPCT A4 Reference';
    document.getElementById('operator').value = '';
    document.getElementById('date').value = date;
    document.getElementById('notes').value = '';
    document.getElementById('include-text').checked = true;
    render();
  }

  window.PPCT = { generateSvg, generateTemplatePdf, filenameFor };

  document.addEventListener('DOMContentLoaded', () => {
    resetForm();
    document.getElementById('generator-form').addEventListener('input', render);
    document.querySelectorAll('input[name="preview-layers"]').forEach((input) => input.addEventListener('change', render));
    document.getElementById('download-svg').addEventListener('click', downloadSvg);
    document.getElementById('download-template-pdf').addEventListener('click', downloadTemplatePdf);
    document.getElementById('reset-form').addEventListener('click', resetForm);
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('./sw.js').catch(() => {});
    }
  });
})();
