(() => {
  const A4_WIDTH = 210;
  const A4_HEIGHT = 297;
  const PT_PER_MM = 72 / 25.4;
  const VERSION = 'web-0.5.2';

  const sections = [
    { id: 'section-metadata', label: 'Metadata', x: 10, y: 10, w: 190, h: 22 },
    { id: 'section-geometry-reference', label: 'Geometry Reference', x: 10, y: 36, w: 190, h: 24 },
    { id: 'section-resolution-wedges', label: 'Resolution Wedges', x: 10, y: 64, w: 92, h: 52 },
    { id: 'section-hatch-density', label: 'Hatch Density', x: 108, y: 64, w: 92, h: 52 },
    { id: 'section-curves-concentric', label: 'Curves / Concentric', x: 10, y: 121, w: 92, h: 56 },
    { id: 'section-text-sizes', label: 'Minimum Text Size', x: 108, y: 121, w: 92, h: 56 },
    { id: 'section-stipple-gradient', label: 'Stipple Gradient', x: 10, y: 182, w: 190, h: 44 },
    { id: 'section-continuous-flow', label: 'Continuous Flow', x: 10, y: 231, w: 190, h: 24 },
    { id: 'section-observation-log', label: 'Observation / Readout', x: 10, y: 260, w: 190, h: 27 },
  ];

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

  function line(x1, y1, x2, y2, extra = {}) { return `<line ${attrs({ x1, y1, x2, y2, ...extra })} />`; }
  function rect(x, y, width, height, extra = {}) { return `<rect ${attrs({ x, y, width, height, ...extra })} />`; }
  function circle(cx, cy, r, extra = {}) { return `<circle ${attrs({ cx, cy, r, ...extra })} />`; }
  function path(d, extra = {}) { return `<path ${attrs({ d, ...extra })} />`; }
  function text(x, y, content, size = 3, extra = {}) { return `<text ${attrs({ x, y, 'font-size': size, ...extra })}>${escapeXml(content)}</text>`; }

  const vectorGlyphs = {
    A: ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    B: ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
    C: ['01111', '10000', '10000', '10000', '10000', '10000', '01111'],
    I: ['11111', '00100', '00100', '00100', '00100', '00100', '11111'],
    O: ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    P: ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
    T: ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    a: ['00000', '00000', '01110', '00001', '01111', '10001', '01111'],
    b: ['10000', '10000', '11110', '10001', '10001', '10001', '11110'],
    c: ['00000', '00000', '01111', '10000', '10000', '10000', '01111'],
    l: ['00100', '00100', '00100', '00100', '00100', '00100', '00110'],
    0: ['01110', '10001', '10011', '10101', '11001', '10001', '01110'],
    1: ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
    2: ['01110', '10001', '00001', '00010', '00100', '01000', '11111'],
    3: ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
    8: ['01110', '10001', '10001', '01110', '10001', '10001', '01110'],
  };

  function vectorGlyph(x, baselineY, char, height, extra = {}) {
    if (char === ' ') return [];
    const rows = vectorGlyphs[char] || vectorGlyphs[char.toUpperCase()] || vectorGlyphs.C;
    const unit = height / 7;
    const topY = baselineY - height;
    const segments = [];
    rows.forEach((row, ry) => {
      let start = -1;
      for (let cx = 0; cx <= row.length; cx += 1) {
        if (row[cx] === '1' && start === -1) start = cx;
        if ((row[cx] !== '1' || cx === row.length) && start !== -1) {
          segments.push(line(Math.round((x + start * unit) * 100) / 100, Math.round((topY + ry * unit) * 100) / 100, Math.round((x + cx * unit) * 100) / 100, Math.round((topY + ry * unit) * 100) / 100, extra));
          start = -1;
        }
      }
    });
    for (let cx = 0; cx < 5; cx += 1) {
      let start = -1;
      for (let ry = 0; ry <= 7; ry += 1) {
        const on = ry < 7 && rows[ry][cx] === '1';
        if (on && start === -1) start = ry;
        if ((!on || ry === 7) && start !== -1) {
          segments.push(line(Math.round((x + cx * unit) * 100) / 100, Math.round((topY + start * unit) * 100) / 100, Math.round((x + cx * unit) * 100) / 100, Math.round((topY + ry * unit) * 100) / 100, extra));
          start = -1;
        }
      }
    }
    return segments;
  }

  function vectorText(x, baselineY, content, height, extra = {}) {
    const body = [];
    const advance = height * 0.78;
    const lineAttrs = {
      fill: extra.fill,
      stroke: extra.stroke,
      'stroke-width': extra['stroke-width'],
    };
    [...String(content)].forEach((char, index) => {
      body.push(...vectorGlyph(x + index * advance, baselineY, char, height, lineAttrs));
    });
    return `<g ${attrs(extra)}>\n${body.join('\n')}\n</g>`;
  }

  function plotSection(sectionId, body) { return `<g id="${sectionId}" data-layer="plot-data">\n${body.join('\n')}\n</g>`; }
  function styleFor(kind) {
    if (kind === 'guide') return { fill: 'none', stroke: '#bbb', 'stroke-width': '0.2' };
    if (kind === 'write') return { stroke: '#777', 'stroke-width': '0.12' };
    return { fill: 'none', stroke: '#999', 'stroke-width': '0.15' };
  }
  function axis(x, y, width, label, attr) {
    return [line(x, y, x + width, y, { stroke: '#777', 'stroke-width': '0.12', 'data-axis': attr })];
  }

  function templateLayer(config) {
    const items = [text(10, 6, 'PPCT printable template. Print at 100%. Plot the data layer on top.', 2.3, { 'font-family': 'monospace', fill: '#555' })];
    sections.forEach((section) => {
      items.push(rect(section.x, section.y, section.w, section.h, styleFor('guide')));
      items.push(text(section.x + 2, section.y + 4, section.label, 2.8, { fill: '#111', 'font-family': 'monospace' }));
    });
    const rows = [
      ['Title', config.title || 'PPCT A4 Reference'],
      ['Operator', config.operator || '________________'],
      ['Date', config.date || '________________'],
      ['Generator', VERSION],
    ];
    rows.forEach(([key, value], index) => items.push(text(13, 18 + index * 3.7, `${key}: ${value}`, 2.35, { 'font-family': 'monospace' })));
    items.push(text(126, 18, 'Pen / paper / plotter notes:', 2.35, { 'font-family': 'monospace' }));
    items.push(rect(126, 20, 69, 8, styleFor('template')));
    const notes = (config.notes || '').trim();
    if (notes) items.push(text(128, 26, notes.length > 46 ? `${notes.slice(0, 43)}...` : notes, 2.2, { 'font-family': 'monospace' }));
    for (let tick = 0; tick <= 100; tick += 10) items.push(text(13.5 + tick, 57, tick, 2, { 'font-family': 'monospace' }));
    items.push(text(136, 57, '50 x 10 mm', 2, { 'font-family': 'monospace' }));
    [2, 1.5, 1, 0.7, 0.5, 0.3].forEach((spacing, index) => items.push(text(16.5 + index * 13, 107, `${spacing}`, 1.9, { 'font-family': 'monospace' })));
    [3, 2, 1.5, 1, 0.5].forEach((spacing, index) => items.push(text(115.5 + index * 16, 107, `${spacing}`, 1.9, { 'font-family': 'monospace' })));
    [2, 1.5, 1, 0.5].forEach((spacing, index) => items.push(text(21 + index * 19, 174, `${spacing}`, 1.8, { 'font-family': 'monospace' })));
    [[6, 183, 138], [5, 183, 147], [4, 183, 155], [3, 183, 163], [2, 156, 138], [1.5, 156, 147], [1, 156, 156], [0.8, 156, 164]].forEach(([size, xx, yy]) => items.push(text(xx, yy, `${size}`, 1.6, { 'font-family': 'monospace' })));
    [10, 25, 50, 75, 90].forEach((density, index) => items.push(text(25 + index * 35, 218, `${density}%`, 1.9, { 'font-family': 'monospace' })));
    [['Min line spacing', 'min-line-spacing', 'mm'], ['Min hatch spacing', 'min-hatch-spacing', 'mm'], ['Min text size', 'min-text-size', 'mm'], ['Best stipple', 'best-stipple-density', '%']].forEach(([label, key, unit], index) => {
      const xx = 15 + (index % 2) * 92;
      const yy = 271 + Math.floor(index / 2) * 9;
      items.push(text(xx, yy, `${label}:`, 2.25, { 'font-family': 'monospace' }));
      items.push(line(xx + 40, yy - 0.8, xx + 70, yy - 0.8, { stroke: '#777', 'stroke-width': '0.12', 'data-readout': key }));
      items.push(text(xx + 72, yy, unit, 2, { 'font-family': 'monospace' }));
    });
    return `<g id="layer-template" data-layer="template" inkscape:groupmode="layer" inkscape:label="Template / print first">\n${items.join('\n')}\n</g>`;
  }

  function metadataPlotData() { return plotSection('section-metadata', []); }

  function geometryReference() {
    const x = 10, y = 36;
    const body = [line(x + 5, y + 14, x + 105, y + 14, { stroke: '#000', 'stroke-width': '0.25' })];
    for (let tick = 0; tick <= 100; tick += 5) {
      const height = tick % 10 === 0 ? 5 : 3;
      const tx = x + 5 + tick;
      body.push(line(tx, y + 14, tx, y + 14 - height, { stroke: '#000', 'stroke-width': '0.18' }));
    }
    body.push(rect(x + 125, y + 8, 50, 10, { fill: 'none', stroke: '#000', 'stroke-width': '0.25' }));
    return plotSection('section-geometry-reference', body);
  }

  function resolutionWedges() {
    const x = 10, y = 64;
    const body = axis(x + 7, y + 46, 78, 'spacing mm', 'spacing-mm');
    [2, 1.5, 1, 0.7, 0.5, 0.3].forEach((spacing, index) => {
      const bx = x + 7 + index * 13;
      const by = y + 10;
      const blockW = 10;
      body.push(line(bx, by + 27, bx + blockW, by + 27, { stroke: '#999', 'stroke-width': '0.08' }));
      for (let n = 0; n * spacing <= blockW; n += 1) {
        const xx = Math.round((bx + n * spacing) * 100) / 100;
        body.push(line(xx, by, xx, by + 25, { stroke: '#000', 'stroke-width': '0.15', 'data-test': n === 0 ? `resolution-spacing-${spacing}mm` : undefined }));
      }
    });
    return plotSection('section-resolution-wedges', body);
  }

  function hatchDensity() {
    const x = 108, y = 64;
    const body = axis(x + 7, y + 46, 78, 'linear / cross, spacing mm', 'spacing-mm');
    [3, 2, 1.5, 1, 0.5].forEach((spacing, index) => {
      const bx = x + 7 + index * 16;
      ['linear', 'cross'].forEach((mode, row) => {
        const by = y + 9 + row * 15;
        body.push(rect(bx, by, 13, 12, { fill: 'none', stroke: '#000', 'stroke-width': '0.15', 'data-test': `hatch-${mode}-${spacing}mm` }));
        for (let n = 1; n * spacing < 13; n += 1) {
          const xx = Math.round((bx + n * spacing) * 100) / 100;
          body.push(line(xx, by, xx, by + 12, { stroke: '#000', 'stroke-width': '0.11' }));
          if (mode === 'cross') {
            const yy = Math.round((by + n * spacing) * 100) / 100;
            if (yy < by + 12) body.push(line(bx, yy, bx + 13, yy, { stroke: '#000', 'stroke-width': '0.11' }));
          }
        }
      });
    });
    return plotSection('section-hatch-density', body);
  }

  function curvesConcentric() {
    const x = 10, y = 121;
    const body = axis(x + 7, y + 50, 78, 'curve spacing mm', 'spacing-mm');
    body.push(path(`M ${x + 7} ${y + 18} C ${x + 20} ${y + 6}, ${x + 34} ${y + 30}, ${x + 47} ${y + 18} S ${x + 72} ${y + 6}, ${x + 85} ${y + 20}`, { fill: 'none', stroke: '#000', 'stroke-width': '0.22' }));
    [2, 1.5, 1, 0.5].forEach((spacing, index) => {
      const cx = x + 14 + index * 19;
      const cy = y + 37;
      let first = true;
      for (let radius = 1.5; radius <= 6; radius += spacing) {
        body.push(circle(cx, cy, Math.round(radius * 100) / 100, { fill: 'none', stroke: '#000', 'stroke-width': '0.12', 'data-test': first ? `concentric-closed-${spacing}mm` : undefined }));
        first = false;
      }
      body.push(path(`M ${cx - 6} ${cy + 9} c 2 ${-spacing}, 5 ${-spacing}, 7 0 c 2 ${spacing}, -1 ${spacing * 2}, -4 ${spacing * 2}`, { fill: 'none', stroke: '#000', 'stroke-width': '0.12', 'data-test': `concentric-spiral-${spacing}mm` }));
    });
    return plotSection('section-curves-concentric', body);
  }

  function textSizes() {
    const x = 108, y = 121;
    const body = axis(x + 7, y + 50, 78, 'text height mm', 'text-height-mm');
    [
      [6, x + 7, y + 14, 'PPCT 123'],
      [5, x + 7, y + 23, 'PPCT 123'],
      [4, x + 7, y + 31, 'PPCT abc 123'],
      [3, x + 7, y + 39, 'PPCT abc 123'],
      [2, x + 55, y + 14, 'PPCT abc 123'],
      [1.5, x + 55, y + 23, 'PPCT abc 123'],
      [1, x + 55, y + 32, 'Il1 O0 8B'],
      [0.8, x + 55, y + 40, 'Il1 O0 8B'],
    ].forEach(([size, xx, yy, sample]) => {
      body.push(vectorText(xx, yy, sample, size, { fill: 'none', stroke: '#000', 'stroke-width': '0.12', 'data-test': `text-size-${size.toFixed(1)}mm`, 'data-sample': sample }));
    });
    return plotSection('section-text-sizes', body);
  }

  function stippleGradient() {
    const x = 10, y = 182;
    const body = axis(x + 7, y + 38, 176, 'nominal density percent', 'stipple-density-percent');
    [10, 25, 50, 75, 90].forEach((density, index) => {
      const bx = x + 7 + index * 35;
      const by = y + 10;
      body.push(rect(bx, by, 28, 22, { fill: 'none', stroke: '#000', 'stroke-width': '0.12' }));
      const count = Math.max(15, Math.floor((density * 5) / 3));
      for (let n = 0; n < count; n += 1) {
        const cx = bx + 1.5 + (((n * 37 + density * 11) % 250) / 10);
        const cy = by + 1.5 + (((n * 53 + density * 7) % 190) / 10);
        body.push(circle(Math.round(cx * 100) / 100, Math.round(cy * 100) / 100, 0.28, { fill: 'none', stroke: '#000', 'stroke-width': '0.1', 'data-test': n === 0 ? `stipple-density-${density}` : undefined, 'data-stipple-density': density }));
      }
    });
    return plotSection('section-stipple-gradient', body);
  }

  function continuousFlow() {
    const x = 10, y = 231;
    const segments = [`M ${x + 7} ${y + 14}`];
    for (let index = 0; index < 14; index += 1) {
      const cx1 = x + 15 + index * 12;
      const cy1 = y + (index % 2 ? 7 : 20);
      const cx2 = x + 21 + index * 12;
      const cy2 = y + (index % 2 ? 20 : 7);
      const ex = x + 27 + index * 12;
      segments.push(`C ${cx1} ${cy1}, ${cx2} ${cy2}, ${ex} ${y + 14}`);
    }
    return plotSection('section-continuous-flow', [path(segments.join(' '), { fill: 'none', stroke: '#000', 'stroke-width': '0.25' })]);
  }

  function observationLogPlotData() { return plotSection('section-observation-log', []); }

  function plotDataLayer() {
    return `<g id="layer-plot-data" data-layer="plot-data" inkscape:groupmode="layer" inkscape:label="Plot data / draw second">\n${[
      metadataPlotData(), geometryReference(), resolutionWedges(), hatchDensity(), curvesConcentric(), textSizes(), stippleGradient(), continuousFlow(), observationLogPlotData(),
    ].join('\n')}\n</g>`;
  }

  function legacyMarkers() {
    return '<!-- data-test="hatch-density-0.5mm" data-test="concentric-spacing-0.5mm" data-test="stipple-density-80" -->';
  }

  function generateSvg(config = {}) {
    const layers = [];
    if (config.includeText !== false) layers.push(templateLayer(config));
    layers.push(plotDataLayer());
    return `<?xml version="1.0" encoding="UTF-8"?>\n<svg id="ppct-target" data-layout="measurement-v2" xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="${A4_WIDTH}mm" height="${A4_HEIGHT}mm" viewBox="0 0 ${A4_WIDTH} ${A4_HEIGHT}">\n<title>PPCT PlotPen Characterization Target</title>\n<desc>A browser-generated A4 calibration target with separate printable-template and plot-data layers.</desc>\n<style>text{dominant-baseline:alphabetic}.cut{fill:none;stroke:#000}</style>\n${legacyMarkers()}\n${layers.join('\n')}\n</svg>\n`;
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
    sections.forEach((section) => { commands.push(pdfRect(section.x, section.y, section.w, section.h)); commands.push(pdfText(section.x + 2, section.y + 4, section.label, 8)); });
    [['Title', config.title || 'PPCT A4 Reference'], ['Operator', config.operator || '________________'], ['Date', config.date || '________________'], ['Generator', VERSION]].forEach(([key, value], index) => commands.push(pdfText(13, 18 + index * 3.7, `${key}: ${value}`, 7)));
    commands.push(pdfText(126, 18, 'Pen / paper / plotter notes:', 7));
    commands.push(pdfRect(126, 20, 69, 8));
    const notes = (config.notes || '').trim();
    if (notes) commands.push(pdfText(128, 26, notes.length > 46 ? `${notes.slice(0, 43)}...` : notes, 6.5));
    for (let tick = 0; tick <= 100; tick += 10) commands.push(pdfText(13.5 + tick, 57, tick, 6));
    commands.push(pdfText(136, 57, '50 x 10 mm', 6));
    ['Min line spacing', 'Min hatch spacing', 'Min text size', 'Best stipple'].forEach((label, index) => {
      const xx = 15 + (index % 2) * 92;
      const yy = 271 + Math.floor(index / 2) * 9;
      commands.push(pdfText(xx, yy, `${label}:`, 7));
      commands.push(pdfLine(xx + 40, yy - 0.8, xx + 70, yy - 0.8));
    });
    [2, 1.5, 1, 0.7, 0.5, 0.3].forEach((spacing, index) => commands.push(pdfText(16.5 + index * 13, 107, `${spacing}`, 5.4)));
    [3, 2, 1.5, 1, 0.5].forEach((spacing, index) => commands.push(pdfText(115.5 + index * 16, 107, `${spacing}`, 5.4)));
    [2, 1.5, 1, 0.5].forEach((spacing, index) => commands.push(pdfText(21 + index * 19, 174, `${spacing}`, 5.1)));
    [[6, 183, 138], [5, 183, 147], [4, 183, 155], [3, 183, 163], [2, 156, 138], [1.5, 156, 147], [1, 156, 156], [0.8, 156, 164]].forEach(([size, xx, yy]) => commands.push(pdfText(xx, yy, `${size}`, 4.8)));
    [10, 25, 50, 75, 90].forEach((density, index) => commands.push(pdfText(25 + index * 35, 218, `${density}%`, 5.4)));
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
    objects.forEach((object, index) => { offsets.push(chunks.join('').length); chunks.push(`${index + 1} 0 obj\n${object}\nendobj\n`); });
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
    if ((document.querySelector('input[name="preview-layers"]:checked')?.value || 'both') === 'plot') config.includeText = false;
    return config;
  }
  function svgDataUrl(svg) { return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`; }
  function render() { const previewImage = document.getElementById('svg-preview-image'); if (previewImage) previewImage.src = svgDataUrl(generateSvg(previewConfig())); }
  function downloadBlob(content, type, filename) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }
  function downloadSvg() { const config = currentConfig(); downloadBlob(generateSvg(config), 'image/svg+xml', filenameFor(config, 'svg')); }
  function downloadTemplatePdf() { const config = currentConfig(); downloadBlob(generateTemplatePdf(config), 'application/pdf', filenameFor(config, 'template.pdf')); }
  function resetForm() {
    document.getElementById('title').value = 'PPCT A4 Reference';
    document.getElementById('operator').value = '';
    document.getElementById('date').value = new Date().toISOString().slice(0, 10);
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
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(() => {});
  });
})();
