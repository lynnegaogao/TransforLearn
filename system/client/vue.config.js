const config = {
  configureWebpack: {
    resolve: {
      // .mjs needed for https://github.com/graphql/graphql-js/issues/1272
      extensions: ['*', '.mjs', '.js', '.vue', '.json', '.gql', '.graphql']
    },
    module: {
      rules: [ // fixes https://github.com/graphql/graphql-js/issues/1272
        {
          test: /\.mjs$/,
          include: /node_modules/,
          type: 'javascript/auto'
        }
      ]
    },
    devServer: {
      // host:'0.0.0.0',
      // sockHost: 'http://103.21.143.204:8083',
      // disableHostCheck: true,
      port: 8090,
      proxy: {
        ["/api"]: {
          target: 'http://127.0.0.1:8090',
          ws: true,
          changeOrigin: true,
          pathRewrite: {
            "^/api": "",
          }
        }
      },
    }
  }
}

module.exports = config