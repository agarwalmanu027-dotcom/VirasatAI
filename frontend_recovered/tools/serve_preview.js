const http = require('http');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..', 'build', 'web');
const mime = {
  '.css': 'text/css',
  '.html': 'text/html',
  '.ico': 'image/x-icon',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.wasm': 'application/wasm',
  '.webp': 'image/webp',
};

http.createServer((request, response) => {
  const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
  const file = path.resolve(root, '.' + pathname);
  if (file !== root && !file.startsWith(root + path.sep)) {
    response.writeHead(403).end();
    return;
  }
  const target = fs.existsSync(file) && fs.statSync(file).isFile()
    ? file
    : path.join(root, 'index.html');
  response.setHeader('Cache-Control', 'no-store');
  response.setHeader('Content-Type', mime[path.extname(target)] || 'application/octet-stream');
  fs.createReadStream(target).pipe(response);
}).listen(8766, '0.0.0.0', () => {
  console.log('VirasatAI preview: http://0.0.0.0:8766');
});
