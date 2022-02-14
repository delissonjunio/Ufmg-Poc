<template>
  <b-container fluid class="mt-3">
    <b-row>
      <b-col sm="5">
        <b-row class="mb-3">
          <b-col sm="5">
            <label for="historicvar-invested">Valor investido:</label>
          </b-col>
          <b-col sm="7">
            <b-input-group prepend="R$" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="investedAmount" id="historicvar-invested" number type="number"></b-form-input>
            </b-input-group>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <b-col sm="5">
            <label for="historicvar-confidence">Intervalo de confiança:</label>
          </b-col>
          <b-col sm="7">
            <b-input-group append="%" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="confidenceInterval" id="historicvar-confidence" number type="number"></b-form-input>
            </b-input-group>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <b-col sm="5">
            <label for="historicvar-period">Período de simulação:</label>
          </b-col>
          <b-col sm="7">
            <b-input-group append="último(s) ano(s)" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="simulationPeriodYears" id="historicvar-period" number type="number" min="1" max="10"></b-form-input>
            </b-input-group>
          </b-col>
        </b-row>
      </b-col>
      <b-col size="7">
        <b-row>
          <b-col sm="4">
            <label for="historicvar-stock">Selecione um ativo:</label>
          </b-col>
          <b-col sm="5">
            <b-input-group>
              <b-form-input list="historicvar-stock-picker" v-model="pickedStock"></b-form-input>
              <b-form-datalist id="historicvar-stock-picker" :options="availableStocks"></b-form-datalist>
              <b-input-group-append>
                <b-button @click=addSelectedStock variant="outline-primary"><b-icon-plus-circle></b-icon-plus-circle></b-button>
              </b-input-group-append>
            </b-input-group>
          </b-col>
        </b-row>
        <b-row class="mt-3 inline-flex">
          <div class="stock-input-box" v-for="stockName in Object.keys(selectedStocks)" :key="stockName">
            <b-input-group :prepend="stockName" append="%" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="selectedStocks[stockName]" number type="number" min="0" max="100"></b-form-input>
            </b-input-group>
          </div>
        </b-row>
      </b-col>
    </b-row>

    <b-row class="my-3">
      <div class="mt-2" v-if="historicVar === historicVar && historicVar !== 0">
        Para o VaR, com {{ confidenceInterval | percent }} de certeza, esse investimento não irá perder mais do que
        {{ (investedAmount - (historicVar * investedAmount)) | currency }} em um dia, representando uma perda de {{ ((1 - historicVar) * 100) | percent }}
      </div>

      <div class="mt-2" v-if="historicCvar === historicCvar && historicCvar !== 0">
        Já para o CVaR, com {{ confidenceInterval | percent }} de certeza, esse investimento não irá perder mais do que
        {{ (investedAmount - (historicCvar * investedAmount)) | currency }} em um dia, representando uma perda de {{ ((1 - historicCvar) * 100) | percent }}
      </div>
    </b-row>
  </b-container>
</template>

<style>
  .inline-flex {
    display: inline-flex;
  }

  .stock-input-box {
    width: 250px;
  }
</style>

<script>
import { inverseErrorFunction } from 'simple-statistics'
import { mapState } from 'vuex'
import _ from 'lodash'

export default {
  name: 'HistoricVarCVar',
  data: () => ({
    confidenceInterval: 95,
    investedAmount: 15000,
    selectedStocks: {},
    simulationPeriodYears: 2,
    pickedStock: null
  }),
  async mounted() {
    await this.$store.dispatch('load')
  },
  computed: {
    bottomPercent() {
      return (1 - this.unitConfidenceInterval)
    },

    varZScore() {
      if (this.confidenceInterval && this.investedAmount) {
        return inverseErrorFunction((this.confidenceInterval / 100.0 - 0.5) / 0.5) * Math.sqrt(2)
      }

      return 0.0
    },

    cvarZScore() {
      if (this.varZScore) {
        return (1.0 / (1 - this.unitConfidenceInterval)) * (1.0 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * this.varZScore)
      }

      return 0.0
    },

    unitConfidenceInterval() {
      if (this.confidenceInterval) {
        return this.confidenceInterval / 100.0
      }

      return 1
    },

    historicCvar() {
      if (this.historicVar) {
        const tailReturns = this.weightedReturns.filter(r => r < this.historicVar)
        return tailReturns.reduce((a, b) => a + b, 0) / tailReturns.length
      }

      return 0.0
    },

    historicVar() {
      if (this.weightedReturns.length) {
        return this.weightedReturns[Math.ceil(this.bottomPercent * this.weightedReturns.length)]
      }

      return 0.0
    },
    weightedReturns() {
      let allReturns = []

      if (!this.simulationPeriodYears || !Object.keys(this.selectedStocks).length) {
        return []
      }

      for (const year of this.availableYears.slice(this.availableYears.length - this.simulationPeriodYears)) {
        // Find out how many max trading days this is
        const tradingDays = Math.max(...Object.keys(this.selectedStocks).map(t => (this.stockReturns[t][year] || []).length))

        // Calculate each stocks' weighted return ratio
        const weightedReturns = Object.entries(this.selectedStocks).map(([t, w]) => _.range(tradingDays).map(i => ((this.stockReturns[t][year] || [])[i] || 1.0) * (w / 100.0)))

        // Calculate the final return ratio
        let finalReturns = _.fill(_.range(tradingDays), 0)
        for (const stockReturn of weightedReturns) {
          finalReturns = finalReturns.map((v, i) => stockReturn[i] + v)
        }

        // Add back to the main list
        allReturns = [...allReturns, ...finalReturns]
      }

      // Find the bottom percent of returns
      allReturns.sort((a, b) => a - b)
      return allReturns
    },
    ...mapState(['availableStocks', 'availableYears', 'stockReturns'])
  },
  methods: {
    async addSelectedStock() {
      if (this.pickedStock) {
        this.$set(this.selectedStocks, this.pickedStock, 0)
        this.pickedStock = null

        for (const pickedStock of Object.keys(this.selectedStocks)) {
          this.$set(this.selectedStocks, pickedStock, 100.0 / Object.keys(this.selectedStocks).length)
        }
      }
    }
  }
}
</script>
