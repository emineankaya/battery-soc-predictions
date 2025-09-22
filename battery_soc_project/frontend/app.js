const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const fetch = require('node-fetch');

const PORT = 3001;
const API_URL = 'http://localhost:5000';

const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    
    // API proxy endpoint'leri
    if (pathname.startsWith('/api/')) {
        try {
            const apiPath = pathname.replace('/api', '');
            const apiUrl = API_URL + apiPath;
            
            let options = {
                method: req.method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };
            
            // POST istekleri için body ekle
            if (req.method === 'POST') {
                const body = await getRequestBody(req);
                options.body = body;
            }
            
            const response = await fetch(apiUrl, options);
            const data = await response.text();
            
            // JSON mı yoksa HTML hata mı döndüğünü kontrol et
            try {
                const jsonData = JSON.parse(data);
                res.writeHead(response.status, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(jsonData));
            } catch (e) {
                // JSON parse edilemezse HTML hata sayfası dönmüş demektir
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ 
                    error: 'API hatası', 
                    message: 'API geçersiz yanıt döndü',
                    status: 'error'
                }));
            }
        } catch (error) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ 
                error: 'API bağlantı hatası', 
                message: error.message,
                status: 'error' 
            }));
        }
        return;
    }
    
    // Ana sayfa
    if (pathname === '/' || pathname === '/index.html') {
        serveFile(res, 'index.html', 'text/html');
        return;
    }
    
    // Diğer statik dosyalar
    const ext = path.extname(pathname);
    if (ext === '.js') {
        serveFile(res, pathname.substring(1), 'application/javascript');
    } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Sayfa bulunamadı', status: 'error' }));
    }
});

function serveFile(res, filename, contentType) {
    const filePath = path.join(__dirname, filename);
    
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Dosya bulunamadı', status: 'error' }));
            return;
        }
        
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(data);
    });
}

function getRequestBody(req) {
    return new Promise((resolve) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            resolve(body);
        });
    });
}

server.listen(PORT, () => {
    console.log(`🚀 Frontend sunucusu başlatıldı: http://localhost:${PORT}`);
    console.log(`🔗 API URL: ${API_URL}`);
    console.log('📝 Not: API\'nin ayrıca çalıştığından emin olun (http://localhost:5000)');
});