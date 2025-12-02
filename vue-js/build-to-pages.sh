pnpm run build
rm -rf ../docs
cp -r ./dist ../docs
sed -i '' \
  -e 's|src=\"\(/js\)|src=\"/oak-heart-tales\1|g' \
  -e 's|href=\"\(/css\)|href=\"/oak-heart-tales\1|g' ../docs/index.html

app_js_file=$(ls ../docs/js/app.*.js | head -n 1)
echo "Processing $app_js_file"
sed -i '' -e 's|\"\(/data\)|\"/oak-heart-tales\1|g' "$app_js_file"

echo "Build complete. Files copied to ../docs"