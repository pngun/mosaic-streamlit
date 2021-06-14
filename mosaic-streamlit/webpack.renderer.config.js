const webpack = require('webpack')
const rules = require('./webpack.rules')

rules.push({
  test: /\.css$/,
  use: [{ loader: 'style-loader' }, { loader: 'css-loader' }],
})

module.exports = {
  module: {
    rules,
  },
  plugins: [
    new webpack.DefinePlugin({
      "process.type": '"renderer"',
    })
  ],
  resolve: {
    fallback: {
      "fs": false,
      "path": false,
    }
  },
  externals: {
    electron: "commonjs electron"
  }
}
