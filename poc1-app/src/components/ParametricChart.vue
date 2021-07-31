<template>
  <div ref="svgContainer"></div>
</template>

<script>
import { scaleLinear } from 'd3-scale'
import * as d3 from 'd3'
import jStat from 'jstat'

export default {
  name: 'ParametricChart',
  props: {
    mean: Number,
    standardDeviation: Number,
    confidenceInterval: Number
  },
  data: function() {
    const margin = { top: 20, right: 30, bottom: 30, left: 40 }

    return {
      margin,
      width: 960 - margin.left - margin.right,
      height: 350 - margin.top - margin.bottom,
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
      const totalXExtent = this.width + this.margin.left + this.margin.right
      const totalYExtent = this.width + this.margin.top + this.margin.bottom

      const svg = d3
        .select(this.$refs.svgContainer)
        .append('svg')
        .attr('preserveAspectRatio', 'xMinYMin meet')
        .attr('viewBox', `0 0 ${totalXExtent} ${totalYExtent}`)
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
        .attr('class', 'annotation')
        .attr('stroke', 'red')
        .attr('stroke-width', '3')

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
        .select('line.annotation')
        .attr('y1', this.y(0))
        .attr('y2', this.y(this.YatConfidence))
        .attr('x1', this.x(this.valueAtConfidence))
        .attr('x2', this.x(this.valueAtConfidence))
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
      const maxIteration = this.valueAtConfidence
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

      data.push({ q: data[data.length - 1].q + 1, p: 0 })

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

    valueAtConfidence() {
      console.log('calling valueAtConfidence')
      return jStat.normal.inv(this.confidenceInterval, this.mean, this.standardDeviation)
    },

    YatConfidence() {
      return jStat.normal.pdf(this.valueAtConfidence, this.mean, this.standardDeviation)
    }
  },
  watch: {
    mean: function() {
      this.updateChart()
    },
    standardDeviation: function() {
      this.updateChart()
    }
  }
}
</script>
