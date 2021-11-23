const { environment } = require('@rails/webpacker')
const webpack = require('webpack')

environment.config.merge({
  resolve: {
    alias: {
      jquery: 'jquery/src/jquery',
      React: 'react',
      ReactDOM: 'react-dom'
    }
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  }
})

// Add an additional plugin of your choosing : ProvidePlugin
environment.plugins.prepend('Provide', new webpack.ProvidePlugin({
  $: 'jquery',
  JQuery: 'jquery',
  jquery: 'jquery'
}))

module.exports = environment