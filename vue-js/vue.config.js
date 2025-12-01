const {defineConfig} = require('@vue/cli-service');

class IgnoreGameErrorsPlugin {
    apply(compiler) {
        compiler.hooks.done.tap('IgnoreGameErrorsPlugin', (stats) => {
            stats.compilation.errors = stats.compilation.errors.filter(
                err => {
                    // Only keep errors NOT from engine/game/*.js
                    const resource = err.module && err.module.resource;
                    return !(resource && /src\/game\/.*\.js$/.test(resource));
                }
            );
        });
    }
}

module.exports = defineConfig({
    transpileDependencies: true,
    configureWebpack: {
        ignoreWarnings: [
            (warning) => {
                return warning.module && /src\/game\/.*\.js$/.test(warning.module.resource);
            }
        ],
        plugins: [
            new IgnoreGameErrorsPlugin()
        ]
    }
})
