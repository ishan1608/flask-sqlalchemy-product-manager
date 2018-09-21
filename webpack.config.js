const path = require('path');

module.exports = {
    entry: "./static/js/main.js",
    output: {
        path: path.resolve(__dirname, 'static/js'),
        filename: "bundle.js",
    },
    module: {
        loaders: [
            {
                loader: 'babel',
                exclude: /node_modules/
            }
        ]
    }
};
