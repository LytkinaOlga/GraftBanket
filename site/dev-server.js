// Local preview with the same /api/order route used in production.
const http = require('http');
const fs = require('fs');
const path = require('path');
if (fs.existsSync(path.join(__dirname, '.env.local'))) process.loadEnvFile(path.join(__dirname, '.env.local'));
const handler = require('./api/order');
const root = __dirname;
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.png': 'image/png', '.svg': 'image/svg+xml' };
const port = Number(process.env.PORT) || 8080;
http.createServer(async (req, res) => {
  if (req.url === '/api/order') {
    let raw = '';
    req.on('data', chunk => { raw += chunk; if (raw.length > 12000) req.destroy(); });
    req.on('end', async () => {
      res.status = code => { res.statusCode = code; return res; };
      res.json = data => { res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(data)); };
      req.body = raw;
      await handler(req, res);
    });
    return;
  }
  const pathname = decodeURIComponent((req.url || '/').split('?')[0]);
  const file = path.resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
  if (!file.startsWith(root + path.sep) && file !== path.join(root, 'index.html')) { res.writeHead(403); res.end(); return; }
  fs.readFile(file, (err, content) => {
    if (err) { res.writeHead(404); res.end('Not found'); return; }
    res.setHeader('Content-Type', (types[path.extname(file).toLowerCase()] || 'application/octet-stream') + '; charset=utf-8');
    res.end(content);
  });
}).listen(port, '127.0.0.1', () => console.log('Draft Banket preview: http://127.0.0.1:' + port));
