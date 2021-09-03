const TEST_STOCKS = ['ABC', 'XYZ']
const GENERATE_RANDOM_RETURN = (k) => [...Array(366).keys()].map(i => (Math.random() - 0.5) * (k || 10))

export default {
  state: {
    availableStocks: TEST_STOCKS,
    availableYears: [2021, 2020, 2019, 2018, 2017],
    stockReturns: {
      ABC: {
        2021: GENERATE_RANDOM_RETURN(),
        2020: GENERATE_RANDOM_RETURN(),
        2019: GENERATE_RANDOM_RETURN(),
        2018: GENERATE_RANDOM_RETURN(),
        2017: GENERATE_RANDOM_RETURN()
      },
      XYZ: {
        2021: GENERATE_RANDOM_RETURN(),
        2020: GENERATE_RANDOM_RETURN(),
        2019: GENERATE_RANDOM_RETURN(),
        2018: GENERATE_RANDOM_RETURN(),
        2017: GENERATE_RANDOM_RETURN()
      }
    }
  },
  mutations: {}
}
