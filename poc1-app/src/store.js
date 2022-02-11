import _ from 'lodash'

export default {
  state: {
    availableStocks: [],
    availableYears: [],
    stockReturns: {},
    apiTickers: {},
    optimizationResults: {}
  },
  mutations: {
    loadReturns(state, returns) {
      state.stockReturns = returns
    },
    loadTickers(state, tickers) {
      state.availableStocks = tickers
    },
    loadYears(state, years) {
      state.availableYears = years
    },
    loadApiTickers(state, tickers) {
      state.apiTickers = tickers
    },
    loadOptimizationResults(state, results) {
      state.optimizationResults = results
    }
  },
  actions: {
    async load({ commit, dispatch }) {
      const response = await fetch('assets/b3_stocks_1994_2020.json')
      const data = await response.json()

      commit('loadReturns', data.dailyReturnsByStock)
      commit('loadTickers', data.availableStocks)
      commit('loadYears', data.availableYears.sort())
    },

    async loadApiTickers({ commit }) {
      const response = await fetch('api/tickers')
      const body = await response.json()
      commit('loadApiTickers', body.tickers)
    },

    async optimizePortfolio({ commit }, { beta, target, method, value, portfolio = [] }) {
      const params = {
        beta,
        target,
        value
      }

      if (portfolio && portfolio.length) {
        params.portfolio = portfolio.join(',')
      }

      const response = await fetch(`/api/optimize/${method}?` + new URLSearchParams(params))
      const body = await response.json()
      commit('loadOptimizationResults', body)
    },

    calculateBottomPercentOfReturns({ state }, { selectedStocks, simulationPeriodYears, bottomPercent }) {
      let allReturns = []

      for (const year of state.availableYears.slice(state.availableYears.length - simulationPeriodYears)) {
        // Find out how many max trading days this is
        const tradingDays = Math.max(...Object.keys(selectedStocks).map(t => (state.stockReturns[t][year] || []).length))

        // Calculate each stocks' weighted return ratio
        const weightedReturns = Object.entries(selectedStocks).map(([t, w]) => _.range(tradingDays).map(i => (state.stockReturns[t][year][i] || 1.0) * (w / 100.0)))

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
      const bottomPercentOfReturns = allReturns[Math.ceil(bottomPercent * allReturns.length)]
      return bottomPercentOfReturns
    }
  }
}
