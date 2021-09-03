<template>
  <b-container fluid class="mt-3">
    <b-row>
      <b-col sm="5">
        <b-row class="my-3">
          <b-col sm="5">
            <label for="historicvar-invested">Valor investido:</label>
          </b-col>
          <b-col sm="5">
            <b-input-group prepend="R$" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="investedAmount" id="historicvar-invested" number type="number"></b-form-input>
            </b-input-group>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <b-col sm="5">
            <label for="historicvar-confidence">Intervalo de confiança:</label>
          </b-col>
          <b-col sm="5">
            <b-input-group append="%" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="confidenceInterval" id="historicvar-confidence" number type="number"></b-form-input>
            </b-input-group>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <b-col sm="5">
            <label for="historicvar-stock">Selecione um ativo:</label>
          </b-col>
          <b-col sm="5">
            <b-form-input list="historicvar-stock-picker" v-model="pickedStock"></b-form-input>
            <b-form-datalist id="historicvar-stock-picker" :options="availableStocks"></b-form-datalist>
          </b-col>
          <b-col sm="2">
            <b-button @click=addSelectedStock variant="outline-primary">Adicionar</b-button>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <b-col sm="5">
            <label for="historicvar-stock">Selecione um ativo:</label>
          </b-col>
          <b-col sm="5">
            <b-form-input list="historicvar-stock-picker" v-model="pickedStock"></b-form-input>
            <b-form-datalist id="historicvar-stock-picker" :options="availableStocks"></b-form-datalist>
          </b-col>
          <b-col sm="2">
            <b-button @click=addSelectedStock variant="outline-primary">Adicionar</b-button>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <div class="mt-2" v-if="parametricVar === parametricVar">
            Para o VaR, com {{ confidenceInterval | percent }} de certeza, esse investimento não irá perder mais do que
            {{ parametricVar | currency }} no período calculado, representando uma perda de {{ (varLossPercentage * 100) | percent }}
          </div>

          <div class="mt-2" v-if="parametricCvar === parametricCvar">
            Já para o CVaR, com {{ confidenceInterval | percent }} de certeza, esse investimento não irá perder mais do que
            {{ parametricCvar | currency }} no período calculado, representando uma perda de {{ (cvarLossPercentage * 100) | percent }}
          </div>
        </b-row>
      </b-col>
      <b-col sm="7">
        <ParametricChart
          :mean="investedAmount"
          :standard-deviation="investedAmount * (standardDeviation / 100.0)"
          :confidence-interval="1 - unitConfidenceInterval"
          :var="parametricVar"
          :cvar="parametricCvar"
        ></ParametricChart>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import { inverseErrorFunction } from 'simple-statistics'
import ParametricChart from '@/components/ParametricChart'
import { mapState } from 'vuex'

export default {
  name: 'HistoricVarCVar',
  components: { ParametricChart },
  data: () => ({
    confidenceInterval: 95,
    investedAmount: 15000,
    standardDeviation: 7,
    selectedStocks: {},
    pickedStock: null
  }),
  computed: {
    varZScore() {
      if (this.confidenceInterval && this.investedAmount && this.standardDeviation) {
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

    parametricVar() {
      if (this.varZScore) {
        return this.investedAmount * this.varZScore * (this.standardDeviation / 100.0)
      }

      return 0.0
    },

    varLossPercentage() {
      if (this.parametricVar && this.investedAmount) {
        return 1 - (this.investedAmount - this.parametricVar) / this.investedAmount
      }

      return 0.0
    },

    cvarLossPercentage() {
      if (this.parametricCvar && this.investedAmount) {
        return 1 - (this.investedAmount - this.parametricCvar) / this.investedAmount
      }

      return 0.0
    },

    unitConfidenceInterval() {
      if (this.confidenceInterval) {
        return this.confidenceInterval / 100.0
      }

      return 1
    },

    parametricCvar() {
      if (this.cvarZScore) {
        return this.investedAmount * this.cvarZScore * (this.standardDeviation / 100.0)
      }

      return 0.0
    },
    ...mapState(['availableStocks', 'availableYears'])
  },
  methods: {
    addSelectedStock() {
      if (this.pickedStock) {
        this.selectedStocks[this.pickedStock] = 0
        this.pickedStock = null
      }
    }
  }
}
</script>
