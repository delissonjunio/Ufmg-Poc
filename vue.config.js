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
      title: 'POC II - Délisson Silva'
    }
  },
  devServer: {
    proxy: {
      '^/api': {
        target: 'http://localhost:5000/',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/'
        }
      }
    }
  }
}
