(() => {
  const A4_WIDTH = 210;
  const A4_HEIGHT = 297;

  function escapeXml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&apos;');
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

  function path(d, extra = {}) {
    return `<path ${attrs({ d, ...extra })} />`;
  }

  function text(x, y, content, size = 3, extra = {}) {
    return `<text ${attrs({ x, y, 'font-size': size, ...extra })}>${escapeXml(content)}</text>`;
  }

  function group(id, label, x, y, width, height, body) {
    return [
      `<g id="${id}">`,
      rect(x, y, width, height, { fill: 'none', stroke: '#bbb', 'stroke-width': '0.2' }),
      text(x + 2, y + 4, label, 2.8, { fill: '#111', 'font-family': 'monospace' }),
      ...body,
      '</g>',
    ].join('\n');
  }

  function metadataSection(config) {
    const x = 10, y = 10, w = 190, h = 24;
    const rows = [
      ['Title', config.title || 'PPCT A4 Reference'],
      ['Operator', config.operator || '________________'],
      ['Date', config.date || '________________'],
      ['Generator', 'web-0.1.0'],
    ];
    const body = rows.map(([key, value], index) =>
      text(x + 3, y + 9 + index * 4, `${key}: ${value}`, 2.6, { 'font-family': 'monospace' })
    );
    body.push(text(x + 115, y + 9, 'Pen / paper / plotter notes:', 2.6, { 'font-family': 'monospace' }));
    body.push(rect(x + 115, y + 11, 70, 9, { fill: 'none', stroke: '#999', 'stroke-width': '0.15' }));
    return group('section-metadata', 'Metadata', x, y, w, h, body);
  }

  function geometryReference() {
    const x = 10, y = 39, w = 190, h = 28;
    const body = [line(x + 5, y + 16, x + 105, y + 16, { stroke: '#000', 'stroke-width': '0.25' })];
    for (let tick = 0; tick <= 100; tick += 5) {
      const height = tick % 10 === 0 ? 5 : 3;
      const tx = x + 5 + tick;
      body.push(line(tx, y + 16, tx, y + 16 - height, { stroke: '#000', 'stroke-width': '0.18' }));
      if (tick % 10 === 0) body.push(text(tx - 1.5, y + 23, tick, 2.2, { 'font-family': 'monospace' }));
    }
    body.push(rect(x + 125, y + 9, 50, 10, { fill: 'none', stroke: '#000', 'stroke-width': '0.25' }));
    body.push(text(x + 126, y + 23, '50 x 10 mm box', 2.2, { 'font-family': 'monospace' }));
    return group('section-geometry-reference', 'Geometry Reference', x, y, w, h, body);
  }

  function strokeCharacterisation() {
    const x = 10, y = 72, w = 90, h = 42;
    const widths = [0.1, 0.2, 0.3, 0.5, 0.8];
    const body = widths.flatMap((width, index) => {
      const yy = y + 11 + index * 6;
      return [
        line(x + 8, yy, x + 72, yy, { stroke: '#000', 'stroke-width': width }),
        text(x + 74, yy + 0.8, width.toFixed(1), 2, { 'font-family': 'monospace' }),
      ];
    });
    return group('section-stroke-characterisation', 'Stroke Characterisation', x, y, w, h, body);
  }

  function resolutionWedges() {
    const x = 110, y = 72, w = 90, h = 42;
    const spacings = [2, 1.5, 1, 0.7, 0.5, 0.3];
    const body = [];
    spacings.forEach((spacing, index) => {
      const startX = x + 8 + index * 12;
      const yy = y + 10;
      const count = Math.floor(22 / spacing);
      for (let n = 0; n < count; n += 1) {
        const xx = Math.round((startX + n * spacing) * 100) / 100;
        body.push(line(xx, yy, xx, yy + 20, { stroke: '#000', 'stroke-width': '0.15' }));
      }
      body.push(text(startX, y + 35, `${spacing}mm`, 2, { 'font-family': 'monospace' }));
    });
    return group('section-resolution-wedges', 'Resolution Wedges', x, y, w, h, body);
  }

  function hatchDensity() {
    const x = 10, y = 119, w = 90, h = 46;
    const body = [];
    [3, 2, 1.5, 1].forEach((spacing, index) => {
      const bx = x + 8 + index * 19;
      const by = y + 10;
      body.push(rect(bx, by, 15, 24, { fill: 'none', stroke: '#000', 'stroke-width': '0.15' }));
      for (let n = 1; n * spacing < 15; n += 1) {
        const xx = Math.round((bx + n * spacing) * 100) / 100;
        body.push(line(xx, by, xx, by + 24, { stroke: '#000', 'stroke-width': '0.12' }));
      }
      body.push(text(bx + 1, y + 39, `${spacing}mm`, 2, { 'font-family': 'monospace' }));
    });
    return group('section-hatch-density', 'Hatch Density', x, y, w, h, body);
  }

  function curvesCorners() {
    const x = 110, y = 119, w = 90, h = 46;
    const body = [
      path(`M ${x + 10} ${y + 34} C ${x + 22} ${y + 6}, ${x + 38} ${y + 6}, ${x + 50} ${y + 34} S ${x + 70} ${y + 62}, ${x + 80} ${y + 16}`, { fill: 'none', stroke: '#000', 'stroke-width': '0.25' }),
    ];
    [2, 4, 8, 12].forEach((radius, index) => {
      const cx = x + 12 + index * 18;
      body.push(path(`M ${cx} ${y + 18} h 8 a ${radius} ${radius} 0 0 1 ${radius} ${radius} v 8`, { fill: 'none', stroke: '#000', 'stroke-width': '0.2' }));
    });
    return group('section-curves-corners', 'Curves & Corners', x, y, w, h, body);
  }

  function continuousFlow() {
    const x = 10, y = 170, w = 190, h = 39;
    const segments = [`M ${x + 8} ${y + 22}`];
    for (let index = 0; index < 14; index += 1) {
      const cx1 = x + 16 + index * 12;
      const cy1 = y + (index % 2 ? 8 : 34);
      const cx2 = x + 22 + index * 12;
      const cy2 = y + (index % 2 ? 34 : 8);
      const ex = x + 28 + index * 12;
      segments.push(`C ${cx1} ${cy1}, ${cx2} ${cy2}, ${ex} ${y + 22}`);
    }
    return group('section-continuous-flow', 'Continuous Flow', x, y, w, h, [
      path(segments.join(' '), { fill: 'none', stroke: '#000', 'stroke-width': '0.25' }),
    ]);
  }

  function penLiftReliability() {
    const x = 10, y = 214, w = 90, h = 43;
    const body = [];
    for (let row = 0; row < 5; row += 1) {
      for (let col = 0; col < 9; col += 1) {
        const cx = x + 9 + col * 8;
        const cy = y + 11 + row * 6;
        body.push(line(cx - 2, cy, cx + 2, cy, { stroke: '#000', 'stroke-width': '0.18' }));
        body.push(line(cx, cy - 2, cx, cy + 2, { stroke: '#000', 'stroke-width': '0.18' }));
      }
    }
    return group('section-pen-lift-reliability', 'Pen Lift Reliability', x, y, w, h, body);
  }

  function observationLog() {
    const x = 110, y = 214, w = 90, h = 43;
    const body = ['Line quality', 'Start/end', 'Feather/bleed', 'Suitability'].flatMap((label, index) => {
      const yy = y + 12 + index * 7;
      return [
        text(x + 4, yy, `${label}:`, 2.4, { 'font-family': 'monospace' }),
        line(x + 32, yy - 0.8, x + 84, yy - 0.8, { stroke: '#777', 'stroke-width': '0.12' }),
      ];
    });
    return group('section-observation-log', 'Observation Log', x, y, w, h, body);
  }

  function generateSvg(config = {}) {
    const sections = [
      metadataSection(config),
      geometryReference(),
      strokeCharacterisation(),
      resolutionWedges(),
      hatchDensity(),
      curvesCorners(),
      continuousFlow(),
      penLiftReliability(),
      observationLog(),
    ].join('\n');

    return `<?xml version="1.0" encoding="UTF-8"?>\n<svg id="ppct-target" xmlns="http://www.w3.org/2000/svg" width="${A4_WIDTH}mm" height="${A4_HEIGHT}mm" viewBox="0 0 ${A4_WIDTH} ${A4_HEIGHT}">\n<title>PPCT PlotPen Characterization Target</title>\n<desc>A browser-generated A4 calibration target for pen plotter evaluation.</desc>\n<style>text{dominant-baseline:alphabetic}.cut{fill:none;stroke:#000}</style>\n${sections}\n</svg>\n`;
  }

  function filenameFor(config) {
    const date = (config.date || new Date().toISOString().slice(0, 10)).replace(/[^0-9-]/g, '');
    return `ppct-a4-${date}.svg`;
  }

  function currentConfig() {
    return {
      title: document.getElementById('title')?.value || 'PPCT A4 Reference',
      operator: document.getElementById('operator')?.value || '',
      date: document.getElementById('date')?.value || new Date().toISOString().slice(0, 10),
    };
  }

  function render() {
    const preview = document.getElementById('svg-preview');
    if (!preview) return;
    preview.innerHTML = generateSvg(currentConfig());
  }

  function download() {
    const config = currentConfig();
    const blob = new Blob([generateSvg(config)], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filenameFor(config);
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function resetForm() {
    const date = new Date().toISOString().slice(0, 10);
    document.getElementById('title').value = 'PPCT A4 Reference';
    document.getElementById('operator').value = '';
    document.getElementById('date').value = date;
    render();
  }

  window.PPCT = { generateSvg, filenameFor };

  document.addEventListener('DOMContentLoaded', () => {
    resetForm();
    document.getElementById('generator-form').addEventListener('input', render);
    document.getElementById('download-svg').addEventListener('click', download);
    document.getElementById('reset-form').addEventListener('click', resetForm);
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('./sw.js').catch(() => {});
    }
  });
})();
