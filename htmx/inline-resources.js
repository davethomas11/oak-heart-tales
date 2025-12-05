// inline-files.js
const fs = require('fs');
const path = require('path');

let html = fs.readFileSync('.build-file-htmx-oakheart.html', 'utf8');
html = html.replace(/<script type="(text\/plain|application\/json)" src="([^"]+)"><\/script>/g, (match, type, src) => {
    const filePath = path.resolve(src);
    const content = fs.readFileSync(filePath, 'utf8');
    if (type === 'application/json') {
        // Minify JSON content
        return `<script type="text/javascript">\n
            window.game_data_files["${src}"] = "${JSON.stringify(JSON.parse(content)).replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"</script>`;
    } else if (type === 'text/plain') {
        // Escape backticks and backslashes in plain text
        const escapedContent = content.replace(/\\/g, '\\\\').replace(/`/g, '\\`');
        return `<script type="text/javascript">\n
            window.game_data_files["${src}"] = \`\n${escapedContent}\n\`</script>`;
    }
    return `<script type="${type}">\n${content}\n</script>`;
});
fs.writeFileSync('game.html', html);
