<template>
  <div class="p-4 container mx-auto">
    <div class="text-center">
      <h3>Trabalho de Conclusão de Curso</h3>
      <h2>Délisson Junio Gonçalves Silva</h2>
      <h3>Universidade Federal de Minas Gerais</h3>
      <h4>Instituto de Ciências Exatas</h4>
      <h5>Departamento de Ciência da Computação</h5>
    </div>

    <div class="mt-5">
      <p>
        Value at Risk (VaR) é um método para avaliar o risco em operações financeiras. O VaR resume, em um número, o risco de um produto
        financeiro ou o risco de uma carteira de investimentos, de um montante financeiro. No cálculo paramétrico, esse número representa a
        pior perda esperada em um dado horizonte de tempo e é associado a um intervalo de confiança. [1]
      </p>

      <p>
        Já o CVaR (Conditional VaR), introduzido por Rockafellar e Uryasev [2], funciona de forma similar porém possui propriedade
        matemáticas mais úteis e estima as perdas possíveis caso um processo passe do limite inferior dado pelo VaR. Dessa forma, ele pode
        ser mais útil para estimar risco em situações onde riscos podem ser compostos (por ex., ter uma perda significativa traz mais perdas
        significativas).
      </p>
    </div>

    <div class="mt-5">
      O primeiro widget abaixo permite calcular o VaR e CVaR paramétrico, isso é, assumindo que os retornos de um dado ativo irão seguir uma
      distribuição normal:

      <ParametricVarCVar />
    </div>

    <div class="mt-5">
      Já o próximo widget utiliza dados extraídos do site da B3 para fazer o cálculo de VaR/CVaR para um ou mais ativos. Os dados disponíveis são
      blablabla.

      <HistoricVarCVar />
    </div>

    <footer>
      <p>
        [1] VALUE AT RISK. In: WIKIPÉDIA, a enciclopédia livre. Flórida: Wikimedia Foundation, 2020. Disponível em: &lt;<a
          href="https://pt.wikipedia.org/w/index.php?title=Value_at_Risk&oldid=57329975"
          class="underline text-indigo-600"
          >https://pt.wikipedia.org/w/index.php?title=Value_at_Risk&oldid=57329975</a
        >. Acesso em: 1 fev. 2020.
      </p>
      <p>[2] Rockafellar, R & Uryasev, Stan. (2000). Optimization of Conditional Value-At-Risk. Journal of risk. 2. 21-42.</p>
    </footer>
  </div>
</template>

<script>
import ParametricVarCVar from './components/ParametricVarCVar.vue'
import HistoricVarCVar from './components/HistoricVarCVar.vue'

export default {
  name: 'MainPage',
  components: {
    ParametricVarCVar, HistoricVarCVar
  }
}
</script>
