const webpack = require('webpack')

module.exports = {
  entry: './src/main.js',
  module: {
    rules: require('./webpack.rules'),
  },
  plugins: [
    new webpack.DefinePlugin({
      "process.type": '"browser"',
    }),
  ],
  externals: {
    electron: "commonjs electron"
  }
}
