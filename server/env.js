const path = require('path');
const dotenv = require('dotenv');

parsed = dotenv.config({
    path: path.join(__dirname, `.env.${process.env.NODE_ENV.trim()}`)
}).parsed;

function isDevelopment() {
    return (process.env.NODE_ENV.trim() === 'development');
}

module.exports = { isDevelopment, PORT: parsed.PORT, PODCASTS_PATH: parsed.PODCASTS_PATH, CONFIG_PATH: parsed.CONFIG_PATH };

