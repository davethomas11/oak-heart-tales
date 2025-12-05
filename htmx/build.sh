echo "Transcrypting python to javascript..."
npm run transcrypt

echo "Compiling for browser with babel..."
npm run compile

echo "Minifying with terser..."
npm run minify

echo "Inlining CSS and HTML into JS..."
npm run inline

echo "Embedding data files..."
npm run embed