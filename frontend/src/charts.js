import { $, escapeHtml } from './dom.js';
const riskScale = { BAJO: 0, MEDIO: 1, ALTO: 2 };

function historyChartMarkup(history, { value, label, axis, kind }) {
  const samples = history.map((item) => ({ item, value: value(item), time: Date.parse(item.created_at) }))
    .filter((sample) => Number.isFinite(sample.value));
  if (!samples.length) return { markup: '<p class="chart-empty">No hay datos para esta gráfica.</p>', latest: null, min: null, max: null };

  const width = 640;
  const height = 240;
  const left = 58;
  const top = 20;
  const plotWidth = 558;
  const plotHeight = 168;
  const times = samples.map((sample) => sample.time);
  const validTimes = times.every(Number.isFinite);
  const firstTime = validTimes ? times.reduce((minimum, time) => Math.min(minimum, time), Infinity) : 0;
  const lastTime = validTimes ? times.reduce((maximum, time) => Math.max(maximum, time), -Infinity) : 0;
  const useTime = lastTime > firstTime;
  const minTime = useTime ? firstTime : 0;
  const timeRange = useTime ? lastTime - minTime : 1;
  const values = samples.map((sample) => sample.value);
  const observedMin = values.reduce((minimum, current) => Math.min(minimum, current), Infinity);
  const observedMax = values.reduce((maximum, current) => Math.max(maximum, current), -Infinity);
  const padding = Math.max(.5, (observedMax - observedMin) * .15);
  const minValue = kind === 'risk' ? 0 : Math.floor((observedMin - padding) * 2) / 2;
  const maxValue = kind === 'risk' ? 2 : Math.ceil((observedMax + padding) * 2) / 2;
  const span = maxValue - minValue || 1;
  const position = (sample, index) => ({
    x: left + plotWidth * (useTime ? (sample.time - minTime) / timeRange : samples.length === 1 ? .5 : index / (samples.length - 1)),
    y: top + plotHeight * (maxValue - sample.value) / span,
  });
  const points = samples.map(position);
  const path = points.map((point, index) => {
    if (index === 0) return `M ${point.x.toFixed(1)} ${point.y.toFixed(1)}`;
    return kind === 'risk'
      ? `H ${point.x.toFixed(1)} V ${point.y.toFixed(1)}`
      : `L ${point.x.toFixed(1)} ${point.y.toFixed(1)}`;
  }).join(' ');
  const ticks = kind === 'risk' ? [2, 1, 0] : [maxValue, (maxValue + minValue) / 2, minValue];
  const grid = ticks.map((tick) => {
    const y = top + plotHeight * (maxValue - tick) / span;
    return `<line class="chart-gridline" x1="${left}" y1="${y.toFixed(1)}" x2="${left + plotWidth}" y2="${y.toFixed(1)}"/><text class="chart-axis" x="${left - 12}" y="${(y + 4).toFixed(1)}" text-anchor="end">${escapeHtml(axis(tick))}</text>`;
  }).join('');
  const dateLabel = (sample, fallback) => Number.isFinite(sample.time)
    ? new Date(sample.time).toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: '2-digit' })
    : fallback;
  const startLabel = dateLabel(samples[0], 'Inicio');
  const endLabel = dateLabel(samples.at(-1), 'Última');
  const latest = samples.at(-1);
  const latestPoint = points.at(-1);
  const latestDate = Number.isFinite(latest.time) ? new Date(latest.time).toLocaleString('es-CO') : 'Fecha no disponible';
  const marker = `<circle class="chart-point ${kind}" cx="${latestPoint.x.toFixed(1)}" cy="${latestPoint.y.toFixed(1)}" r="5"><title>${escapeHtml(`${latestDate}: ${label(latest.value)}`)}</title></circle>`;
  const dates = samples.length === 1
    ? `<text class="chart-axis" x="${latestPoint.x.toFixed(1)}" y="${height - 16}" text-anchor="middle">${escapeHtml(startLabel)}</text>`
    : `<text class="chart-axis" x="${left}" y="${height - 16}">${escapeHtml(startLabel)}</text><text class="chart-axis" x="${left + plotWidth}" y="${height - 16}" text-anchor="end">${escapeHtml(endLabel)}</text>`;
  const description = `${samples.length} mediciones. Desde ${startLabel} hasta ${endLabel}. Última: ${label(latest.value)}. Consulta los valores exactos en la lista inferior.`;
  return {
    markup: `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(description)}"><g>${grid}</g><path class="chart-line ${kind}" d="${path}"/>${marker}${dates}</svg>`,
    latest: latest.value, min: minValue, max: maxValue,
  };
}

export function renderHistoryCharts(history) {
  const chronological = [...history].sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at) || a.measurement_id - b.measurement_id);
  $('#history-charts').hidden = false;
  $('#history-chart-note').hidden = chronological.length !== 1;
  const risk = historyChartMarkup(chronological, {
    kind: 'risk', value: (item) => riskScale[item.risk_level],
    label: (value) => ['BAJO', 'MEDIO', 'ALTO'][value],
    axis: (value) => ['Bajo', 'Medio', 'Alto'][value],
  });
  const temperature = historyChartMarkup(chronological, {
    kind: 'temperature', value: (item) => typeof item.payload?.temperature === 'number' ? item.payload.temperature : NaN,
    label: (value) => `${value.toFixed(1)} °C`, axis: (value) => value.toFixed(1),
  });
  $('#risk-chart').innerHTML = risk.markup;
  $('#risk-chart-latest').textContent = risk.latest === null ? 'Sin datos' : ['Bajo', 'Medio', 'Alto'][risk.latest];
  $('#temperature-chart').innerHTML = temperature.markup;
  $('#temperature-chart-latest').textContent = temperature.latest === null ? 'Sin datos' : `${temperature.latest.toFixed(1)} °C`;
  $('#temperature-chart-range').textContent = temperature.min === null
    ? 'Sin temperaturas registradas'
    : `Eje vertical desde ${temperature.min.toFixed(1)} °C hasta ${temperature.max.toFixed(1)} °C`;
}
