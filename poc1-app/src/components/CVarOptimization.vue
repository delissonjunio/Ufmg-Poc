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

        <b-row class="my-3" v-if="method === 'efficient_risk' || method === 'efficient_return'">
          <b-col sm="5">
            <label for="optimization-target">
              <template v-if="method === 'efficient_risk'">Risco máximo</template><template v-else>Retorno</template> desejado:
            </label>
          </b-col>
          <b-col sm="7">
            <b-input-group append="%" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="target100" id="optimization-target" number type="number"></b-form-input>
            </b-input-group>
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
      <div class="mt-2" v-if="optimizationResults.conditional_value_at_risk">
        Para o CVaR, com {{ optimizationResults.beta * 100 | percent }} de certeza, esse investimento não irá perder mais do que
        {{ optimizationResults.conditional_value_at_risk * optimizationResults.invested | currency }} em um dia, representando uma perda de {{ optimizationResults.conditional_value_at_risk * 100 | percent }}.
        O retorno anual esperado para esse portfólio é de {{ optimizationResults.expected_annual_return * 100 | percent }}, ou {{ optimizationResults.expected_annual_return * optimizationResults.invested | currency }}.
      </div>

      <b-alert show v-if="optimizationResults.error && optimizationResults.code && !busy" variant="warning">
        Não foi possível otimizar um portfólio. Tente aumentar o risco/diminuir o retorno esperado.
      </b-alert>

      <div class="mt-2" v-if="(!optimizationResults.error && !optimizationResults.code) || busy">
        <b-table
          striped
          hover
          :busy="busy"
          :items="resultPortfolio"
          :fields="OPTIMIZATION_RESULT_FIELDS"
          :foot-clone="true"
          :label-sort-asc="''"
          :label-sort-clear="''"
          :label-sort-desc="''"
          :no-footer-sorting="true">
          <template #cell(price)="data">
            {{ apiTickers[data.item.ticker] | currency }}
          </template>

          <template #cell(totalInvested)="data">
            {{ apiTickers[data.item.ticker] * data.item.count | currency }}
          </template>

          <template #foot(totalInvested)>
            <span v-if="optimizationResults.leftover">{{ investedAmount - optimizationResults.leftover | currency }}</span>
          </template>

          <template #foot()>
            <i></i>
          </template>

          <template #table-busy>
            <div class="text-center my-2">
              <b-spinner class="align-middle"></b-spinner>
            </div>
          </template>
        </b-table>
      </div>
    </b-row>
  </b-container>
</template>

<script>
import { mapState } from 'vuex'
import _ from 'lodash'

const OPTIMIZATION_METHODS = [
  { value: 'min_cvar', text: 'Minimizar o risco' },
  { value: 'efficient_risk', text: 'Maximizar retorno para risco' },
  { value: 'efficient_return', text: 'Minimizar risco para retorno' }
]

const OPTIMIZATION_RESULT_FIELDS = [
  {
    key: 'ticker',
    label: 'Nome do ativo',
    sortable: true
  },
  {
    key: 'count',
    label: 'Quantidade',
    sortable: true,
    thClass: 'text-end',
    tdClass: 'text-end'
  },
  {
    key: 'price',
    label: 'Valor unitário',
    sortable: false,
    thClass: 'text-end',
    tdClass: 'text-end'
  },
  {
    key: 'totalInvested',
    label: 'Total a investir',
    sortable: true,
    thClass: 'text-end',
    tdClass: 'text-end'
  }
]

export default {
  name: 'CVarOptimization',
  data: () => ({
    ticker: '',
    beta100: 95,
    investedAmount: 10000,
    target100: 7,
    portfolio: [],
    busy: false,
    method: OPTIMIZATION_METHODS[0].value,
    OPTIMIZATION_METHODS,
    OPTIMIZATION_RESULT_FIELDS
  }),
  async mounted() {
    await this.$store.dispatch('loadApiTickers')
  },
  computed: {
    ...mapState(['apiTickers', 'optimizationResults']),
    availableStocks() {
      return _.pickBy(this.apiTickers, (v, k) => this.portfolio.indexOf(k) === -1)
    },
    resultPortfolio() {
      if (this.optimizationResults.portfolio) {
        return Object.entries(this.optimizationResults.portfolio).map(([k, v]) => ({ ticker: k, count: v }))
      }

      return []
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

      this.busy = true
      try {
        await this.$store.dispatch('optimizePortfolio', payload)
      } finally {
        this.busy = false
      }
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
