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
      Value at Risk (VaR) é um método para avaliar o risco em operações financeiras. O VaR resume, em um número, o risco
      de um produto financeiro ou o risco de uma carteira de investimentos, de um montante financeiro. Esse número
      representa a pior perda esperada em um dado horizonte de tempo e é associado a um intervalo de confiança. [1]
    </div>

    <div class="mt-5">
      O primeiro widget abaixo permite calcular o VaR paramétrico, isso é, assumindo que os retornos de um dado ativo irão
      seguir uma distribuição normal:

      <ParametricVar />
    </div>

    <footer class="mt-5">
      [1] VALUE AT RISK. In: WIKIPÉDIA, a enciclopédia livre. Flórida: Wikimedia Foundation, 2020. Disponível em: &lt;<a
        href="https://pt.wikipedia.org/w/index.php?title=Value_at_Risk&oldid=57329975"
        class="underline text-indigo-600"
      >https://pt.wikipedia.org/w/index.php?title=Value_at_Risk&oldid=57329975</a>.
      Acesso em: 1 fev. 2020.
    </footer>
  </div>
</template>

<script>
import ParametricVar from './components/ParametricVar.vue'

export default {
  name: 'MainPage',
  components: {
    ParametricVar
  }
}
</script>
