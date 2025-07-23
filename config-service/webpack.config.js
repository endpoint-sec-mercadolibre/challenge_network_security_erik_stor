const path = require('path');

module.exports = {
  entry: './src/index.ts',
  target: 'node',
  mode: 'production',
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: [
          {
            loader: 'ts-loader',
            options: {
              configFile: 'tsconfig.build.json',
              compilerOptions: {
                removeComments: false
              }
            }
          }
        ],
        exclude: [
          /node_modules/,
          /test/,
          path.resolve(__dirname, 'test')
        ],
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  output: {
    filename: 'index.js',
    path: path.resolve(__dirname, 'dist/'),
    libraryTarget: 'commonjs2',
  },
  externals: {
    'crypto-js': 'crypto-js',
    'swagger-jsdoc' : 'swagger-jsdoc',
    'swagger-ui-express' : 'swagger-ui-express',
    'cors' : 'cors',
    'libsodium-wrappers' : 'libsodium-wrappers',
  },
  optimization: {
    minimize: false,
  },
}; 
