<template>
  <div ref="svgContainer"></div>
</template>

<script>
import { scaleLinear } from 'd3-scale'
import * as d3 from 'd3'
import { annotation, annotationLabel } from 'd3-svg-annotation'
import jStat from 'jstat'

export default {
  name: 'ParametricChart',
  props: {
    mean: Number,
    standardDeviation: Number,
    confidenceInterval: Number,
    var: Number,
    cvar: Number
  },
  data: function() {
    const margin = { top: 20, right: 30, bottom: 30, left: 40 }
    const viewportWidth = 960
    const viewportHeight = 450

    const width = 960
    const height = 350

    return {
      margin,
      width: width - margin.left - margin.right,
      height: height - margin.top - margin.bottom,
      viewportWidth,
      viewportHeight,
      svg: null,
      x: null,
      y: null
    }
  },
  mounted() {
    this.x = this.generateXAxis()
    this.y = this.generateYAxis()
    this.svg = this.generateChart()
    this.updateChart()
  },
  methods: {
    generateXAxis() {
      return scaleLinear()
        .rangeRound([0, this.width])
        .domain([this.minD, this.maxD])
        .nice()
    },
    generateYAxis() {
      return scaleLinear()
        .domain([0, this.maxP])
        .range([this.height, 0])
    },
    generateChart() {
      const svg = d3
        .select(this.$refs.svgContainer)
        .append('svg')
        .attr('preserveAspectRatio', 'xMinYMin meet')
        .attr('viewBox', `0 0 ${this.viewportWidth} ${this.viewportHeight}`)
        .append('g')
        .attr('transform', 'translate(' + this.margin.left + ',' + this.margin.top + ')')

      svg
        .append('g')
        .attr('class', 'xaxis')
        .attr('transform', 'translate(0,' + this.height + ')')
        .style('font-size', '1rem')

      svg
        .append('path')
        .attr('class', 'distribution')
        .style('fill', '#ccc')
        .style('opacity', '0.5')

      svg
        .append('path')
        .attr('class', 'confidencedistribution')
        .style('fill', '#c33')
        .style('opacity', '0.5')

      svg
        .append('line')
        .attr('class', 'annotationvar')
        .attr('stroke', 'red')
        .attr('stroke-width', '3')

      svg
        .append('line')
        .attr('class', 'annotationcvar')
        .attr('stroke', 'red')
        .attr('stroke-width', '3')

      svg.append('g').attr('class', 'annotationsvg')

      svg
        .append('text')
        .attr('class', 'midchart')
        .attr('dy', '0.35em')
        .attr('text-anchor', 'middle')
        .text('Distribuição normal de retornos')

      return svg
    },

    updateChart() {
      this.x = this.x.domain([this.minD, this.maxD]).nice()
      this.y = this.y.domain([0, this.maxP])

      const line = d3
        .line()
        .x(d => this.x(d.q))
        .y(d => this.y(d.p))

      this.svg
        .select('path.distribution')
        .datum(this.normalDistribution)
        .attr('d', line)

      this.svg
        .select('path.confidencedistribution')
        .datum(this.normalDistributionUpToConfidence)
        .attr('d', line)

      const xAxis = d3.axisBottom(this.x).tickFormat(val => this.$options.filters.currency(val))
      this.svg
        .select('.xaxis')
        .call(xAxis)
        .selectAll('text')
        .attr('y', 0)
        .attr('x', 9)
        .attr('dy', '.35em')
        .attr('transform', 'rotate(90)')
        .style('text-anchor', 'start')

      this.svg
        .select('line.annotationvar')
        .attr('y1', this.y(0))
        .attr('y2', this.y(this.YatVar))
        .attr('x1', this.x(this.valueAtVar))
        .attr('x2', this.x(this.valueAtVar))

      this.svg
        .select('line.annotationcvar')
        .attr('y1', this.y(0))
        .attr('y2', this.y(this.YatCvar))
        .attr('x1', this.x(this.valueAtCvar))
        .attr('x2', this.x(this.valueAtCvar))

      const annotations = [
        {
          note: {
            label: `Risco calculado: ${this.$options.filters.currency(this.mean - this.valueAtVar)}`,
            bgPadding: 20,
            title: 'VaR'
          },
          data: { q: this.valueAtVar, p: this.YatVar },
          dy: -80,
          dx: -80
        },
        {
          note: {
            label: `Risco calculado: ${this.$options.filters.currency(this.mean - this.valueAtCvar)}`,
            bgPadding: 20,
            title: 'CVaR'
          },
          data: { q: this.valueAtCvar, p: this.YatCvar },
          dy: -80,
          dx: -80
        }
      ]

      const annotationMaker = annotation()
        .editMode(true)
        .notePadding(15)
        .type(annotationLabel)
        .accessors({ x: d => this.x(d.q), y: d => this.y(d.p) })
        .accessorsInverse({ x: d => this.x.invert(d.q), y: d => this.y.invert(d.p) })
        .annotations(annotations)

      this.svg.select('g.annotationsvg').call(annotationMaker)

      this.svg
        .select('text.midchart')
        .attr('x', d => this.x(this.minD + (this.maxD - this.minD) / 2))
        .attr('y', d => this.y(this.maxP * 0.3))
    }
  },
  computed: {
    normalDistribution() {
      const data = []
      const minIteration = this.mean - 4 * this.standardDeviation
      const maxIteration = this.mean + 4 * this.standardDeviation
      const iterationStep = (maxIteration - minIteration) / 100

      for (let i = minIteration; i < maxIteration; i += iterationStep) {
        const q = i
        const p = jStat.normal.pdf(i, this.mean, this.standardDeviation)
        const arr = {
          q: q,
          p: p
        }
        data.push(arr)
      }

      return data
    },

    normalDistributionUpToConfidence() {
      const data = []
      const minIteration = this.mean - 4 * this.standardDeviation
      const maxIteration = this.valueAtVar
      const iterationStep = (maxIteration - minIteration) / 100

      for (let i = minIteration; i < maxIteration; i += iterationStep) {
        const q = i
        const p = jStat.normal.pdf(i, this.mean, this.standardDeviation)
        const arr = {
          q: q,
          p: p
        }
        data.push(arr)
      }

      data.push({ q: data[data.length - 1].q, p: 0 })

      return data
    },

    minD() {
      return d3.min(this.normalDistribution, d => d.q)
    },

    maxD() {
      return d3.max(this.normalDistribution, d => d.q)
    },

    maxP() {
      return d3.max(this.normalDistribution, d => d.p)
    },

    valueAtVar() {
      return this.mean - this.var
    },

    valueAtCvar() {
      return this.mean - this.cvar
    },

    YatVar() {
      return jStat.normal.pdf(this.valueAtVar, this.mean, this.standardDeviation)
    },

    YatCvar() {
      return jStat.normal.pdf(this.valueAtCvar, this.mean, this.standardDeviation)
    }
  },
  watch: {
    mean: function() {
      this.updateChart()
    },
    standardDeviation: function() {
      this.updateChart()
    },
    confidenceInterval: function() {
      this.updateChart()
    }
  }
}
</script>
