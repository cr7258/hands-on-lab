// Simple CORS proxy server
const corsAnywhere = require('cors-anywhere');

const host = 'localhost';
const port = 8080;

// Create CORS Anywhere server
corsAnywhere.createServer({
  originWhitelist: [], // Allow all origins
  requireHeader: ['origin', 'x-requested-with'],
  removeHeaders: ['cookie', 'cookie2']
}).listen(port, host, function() {
  console.log(`CORS Anywhere proxy server running on ${host}:${port}`);
  console.log(`To use it, prepend the URL with: http://${host}:${port}/`);
});
