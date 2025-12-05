echo "Transcrypting python to javascript..."
npm run transcrypt

if [ $? -ne 0 ]; then
    echo "Transcrypting failed. Exiting."
    exit 1
fi

sed -i '' '1i\
import '\''babel-polyfill'\''
' js/game.js

sed -i '' '1i\
import '\''babel-polyfill'\''
' js/action.js

echo "Compiling for browser with babel..."
npm run compile

if [ $? -ne 0 ]; then
    echo "Babel compilation failed. Exiting."
    exit 1
fi

echo "Bundling with browserify..."
npm run browserify

if [ $? -ne 0 ]; then
    echo "Browserify bundling failed. Exiting."
    exit 1
fi

echo "Minifying with terser..."
npm run minify

if [ $? -ne 0 ]; then
    echo "Terser minification failed. Exiting."
    exit 1
fi

echo "Inlining CSS and HTML into JS..."
npm run inline

if [ $? -ne 0 ]; then
    echo "Inlining failed. Exiting."
    exit 1
fi

echo "Embedding data files..."
npm run embed

if [ $? -ne 0 ]; then
    echo "Embedding data files failed. Exiting."
    exit 1
fi