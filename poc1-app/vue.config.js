const WorkerPlugin = require('worker-plugin')

module.exports = {
  configureWebpack: {
    output: {
      globalObject: 'this'
    },
    plugins: [
      new WorkerPlugin()
    ]
  },
  pages: {
    index: {
      entry: 'src/main.js',
      title: 'POC I - Délisson Silva'
    }
  }

}
