import Vue from 'vue'

import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Vuex from 'vuex'

import MainPage from './MainPage.vue'
import store from './store'

Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.use(Vuex)

Vue.config.productionTip = false

const currencyFormatter = new Intl.NumberFormat('pt-br', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
  currency: 'BRL',
  currencyDisplay: 'symbol',
  style: 'currency'
})

Vue.filter('currency', function(value) {
  return currencyFormatter.format(value)
})

const percentFormatter = new Intl.NumberFormat('pt-br', {
  maximumFractionDigits: 2,
  style: 'percent'
})

Vue.filter('percent', function(value) {
  return percentFormatter.format(value * 0.01)
})

new Vue({
  render: h => h(MainPage),
  store: new Vuex.Store(store)
}).$mount('#app')
