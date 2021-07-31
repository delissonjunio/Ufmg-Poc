<template>
  <b-container fluid class="mt-3">
    <b-row>
      <b-col sm="5">
        <b-row class="my-3">
          <b-col sm="5">
            <label for="parametricvar-invested">Valor investido:</label>
          </b-col>
          <b-col sm="5">
            <b-input-group prepend="R$" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="investedAmount" id="parametricvar-invested" number type="number"></b-form-input>
            </b-input-group>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <b-col sm="5">
            <label for="parametricvar-confidence">Intervalo de confiança:</label>
          </b-col>
          <b-col sm="5">
            <b-input-group append="%" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="confidenceInterval" id="parametricvar-confidence" number type="number"></b-form-input>
            </b-input-group>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <b-col sm="5">
            <label for="parametricvar-deviation">Desvio padrão:</label>
          </b-col>
          <b-col sm="5">
            <b-input-group append="%" class="mb-2 mr-sm-2 mb-sm-0">
              <b-form-input v-model="standardDeviation" id="parametricvar-deviation" number type="number"></b-form-input>
            </b-input-group>
          </b-col>
        </b-row>

        <b-row class="my-3">
          <div class="mt-2" v-if="parametricVar === parametricVar">
            Com {{ confidenceInterval | percent }} de certeza, esse investimento não irá perder mais do que
            {{ parametricVar | currency }} no período calculado.
          </div>
        </b-row>
      </b-col>
      <b-col sm="7">
        <ParametricChart
          :mean="investedAmount"
          :standard-deviation="investedAmount * (standardDeviation / 100.0)"
          :confidence-interval="1 - confidenceInterval / 100.0"
        ></ParametricChart>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import { inverseErrorFunction } from 'simple-statistics'
import ParametricChart from '@/components/ParametricChart'

export default {
  name: 'ParametricVar',
  components: { ParametricChart },
  data: () => ({
    confidenceInterval: 95,
    investedAmount: 15000,
    standardDeviation: 7
  }),
  computed: {
    parametricVar() {
      if (this.confidenceInterval && this.investedAmount && this.standardDeviation) {
        const ZScore = inverseErrorFunction((this.confidenceInterval / 100.0 - 0.5) / 0.5) * Math.sqrt(2)
        return this.investedAmount * ZScore * (this.standardDeviation / 100.0)
      }

      return 0.0
    }
  }
}
</script>
