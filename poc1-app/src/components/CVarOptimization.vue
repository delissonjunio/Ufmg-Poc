<template>
  <b-container fluid class="mt-3">
    <b-row>
      <b-col sm="5">
        <b-row class="mb-3">
          <b-col sm="5">
            <label for="optimization-invested">Valor investido:</label>
          </b-col>
          <b-col sm="7">
            <b-input-group prepend="R$" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="investedAmount" id="optimization-invested" number type="number"></b-form-input>
            </b-input-group>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <b-col sm="5">
            <label for="optimization-confidence">Intervalo de confiança:</label>
          </b-col>
          <b-col sm="7">
            <b-input-group append="%" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="beta100" id="optimization-confidence" number type="number"></b-form-input>
            </b-input-group>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <b-col sm="5">
            <label for="optimization-method">Selecione um método:</label>
          </b-col>
          <b-col sm="7">
            <b-form-select v-model="method" :options="OPTIMIZATION_METHODS"></b-form-select>
          </b-col>
        </b-row>
      </b-col>
      <b-col size="7">
        <b-row>
          <b-col sm="4">
            <label for="optimization-stock">Selecione um ativo:</label>
          </b-col>
          <b-col sm="5">
            <b-input-group>
              <b-form-input list="optimization-stock-picker" v-model="ticker"></b-form-input>
              <b-form-datalist id="optimization-stock-picker" :options="availableStocks"></b-form-datalist>
              <b-input-group-append>
                <b-button @click=addSelectedStock variant="outline-primary"><b-icon-plus-circle></b-icon-plus-circle></b-button>
              </b-input-group-append>
            </b-input-group>
          </b-col>
        </b-row>
        <b-row class="mt-3">
          <b-col>
            <div v-for="ticker of portfolio" :key="ticker" class="mx-sm-2 d-inline-block">
              <b-button variant="secondary" @click="removeTicker(ticker)">{{ ticker }}</b-button>
            </div>
            <span v-if="!portfolio.length">(todos os ativos da B3)</span>
          </b-col>
        </b-row>
        <b-row class="mt-3">
          <b-col>
            <b-button variant="primary" @click="optimize">Otimizar</b-button>
          </b-col>
        </b-row>
      </b-col>
    </b-row>

    <b-row class="my-3">
      <div class="mt-2" v-if="optimizedCVaR === optimizedCVaR && optimizedCVaR !== 0">
        Para o VaR, com {{ beta100 | percent }} de certeza, esse investimento não irá perder mais do que
        {{ (investedAmount - (optimizedCVaR * investedAmount)) | currency }} em um dia, representando uma perda de {{ ((1 - optimizedCVaR) * 100) | percent }}
      </div>
    </b-row>
  </b-container>
</template>

<script>
import { mapState } from 'vuex'
import _ from 'lodash'

const OPTIMIZATION_METHODS = [
  { value: 'min_cvar', text: 'Minimizar o CVaR' },
  { value: 'efficient_risk', text: 'Maximizar retorno para risco' },
  { value: 'efficient_return', text: 'Minizar risco para retorno' }
]

export default {
  name: 'CVarOptimization',
  data: () => ({
    ticker: '',
    beta100: 95,
    investedAmount: 10000,
    target100: 7,
    portfolio: [],
    optimizedCVaR: 0,
    method: OPTIMIZATION_METHODS[0].value,
    OPTIMIZATION_METHODS
  }),
  async mounted() {
    await this.$store.dispatch('loadApiTickers')
  },
  computed: {
    ...mapState(['apiTickers']),
    availableStocks() {
      return _.pickBy(this.apiTickers, (v, k) => this.portfolio.indexOf(k) === -1)
    }
  },
  methods: {
    async optimize() {
      const payload = {
        beta: this.beta100 / 100.0,
        target: this.target100 / 100.0,
        method: this.method,
        portfolio: this.portfolio,
        value: this.investedAmount
      }

      await this.$store.dispatch('optimizePortfolio', payload)
    },
    addSelectedStock() {
      if (this.ticker) {
        this.portfolio.push(this.ticker)
        this.ticker = ''
      }
    },
    removeTicker(ticker) {
      this.portfolio = this.portfolio.filter(t => t !== ticker)
    }
  }
}
</script>
