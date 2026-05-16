<template>
  <div class="chart-wrapper" ref="wrapperRef">
    <div class="chart-container" :aria-label="$t('transparency.live_chart')">
      <h2>{{ $t('transparency.live_chart') }} — Proceso {{ processId }}</h2>
      <svg ref="svgRef" :width="width" :height="height" role="img" :aria-label="ariaLabel" aria-hidden="false" />
      <p class="sr-only" aria-live="polite">{{ ariaLabel }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as d3 from 'd3'

const props = defineProps<{ processId: string }>()
const wrapperRef = ref<HTMLDivElement | null>(null)
const svgRef = ref<SVGSVGElement | null>(null)
const width = ref(700)
const height = ref(400)
const margin = { top: 20, right: 30, bottom: 40, left: 60 }

interface VoteData { option: string; count: number }
const data = ref<VoteData[]>([])
const ariaLabel = ref('Sin datos aún.')
let ws: WebSocket | null = null
let resizeObserver: ResizeObserver | null = null

function updateDimensions() {
  if (!wrapperRef.value) return
  const rect = wrapperRef.value.getBoundingClientRect()
  const w = Math.max(320, rect.width - 48) // padding compensation
  width.value = w
  height.value = Math.min(400, Math.max(250, w * 0.55))
}

function renderChart() {
  if (!svgRef.value || !data.value.length) return
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()

  const innerWidth = width.value - margin.left - margin.right
  const innerHeight = height.value - margin.top - margin.bottom

  const x = d3.scaleBand()
    .domain(data.value.map(d => d.option))
    .range([0, innerWidth])
    .padding(0.3)

  const y = d3.scaleLinear()
    .domain([0, d3.max(data.value, d => d.count) ?? 10])
    .nice()
    .range([innerHeight, 0])

  const g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  g.append('g').selectAll('rect')
    .data(data.value).join('rect')
    .attr('x', d => x(d.option)!)
    .attr('y', d => y(d.count))
    .attr('height', d => innerHeight - y(d.count))
    .attr('width', x.bandwidth())
    .attr('fill', '#3b82f6')
    .attr('rx', 4)

  g.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(x))
    .selectAll('text')
    .style('font-size', '12px')
    .style('fill', 'var(--text-main)')

  g.append('g')
    .call(d3.axisLeft(y).ticks(6))
    .selectAll('text')
    .style('font-size', '12px')
    .style('fill', 'var(--text-main)')

  g.selectAll('.domain, .tick line')
    .style('stroke', 'var(--panel-border)')

  ariaLabel.value = data.value.map(d => `${d.option}: ${d.count} votos`).join(', ')
}

onMounted(() => {
  updateDimensions()
  resizeObserver = new ResizeObserver(() => {
    updateDimensions()
    renderChart()
  })
  if (wrapperRef.value) resizeObserver.observe(wrapperRef.value)

  const apiUrl = import.meta.env.VITE_API_URL || 'ws://localhost:8000'
  const wsUrl = apiUrl.replace(/^http/, 'ws')
  ws = new WebSocket(`${wsUrl}/ws/results/${props.processId}`)
  ws.onmessage = (e) => {
    data.value = JSON.parse(e.data)
    renderChart()
  }
})

onUnmounted(() => {
  ws?.close()
  resizeObserver?.disconnect()
})
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  overflow-x: auto;
}
.chart-container {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1rem;
  min-width: 320px;
}
.chart-container h2 {
  margin-bottom: 1rem;
  font-size: 1.2rem;
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
