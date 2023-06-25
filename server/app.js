const path = require('path');
const express = require('express');
const http = require('http');
const cors = require('cors');
const app = express();
const spawn = require("child_process").spawn;
const db = require('./db');
const uuidv4 = require('./helpers/uuidv4');
const { createWesocketServer, clients } = require('./websockets');
const { isDevelopment, PORT, PODCASTS_PATH } = require('./env');

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/public', express.static(path.join(__dirname, 'public')));
app.use('/podcasts', express.static(PODCASTS_PATH));

app.use(function (req, res, next) {
    req.db = db;
    next();
});

if (isDevelopment()) {
    console.log('In development mode');

    app.use(function (err, req, res, next) {
        if (err) {
            res.status(err.status || 500);
            res.json({
                message: err.message,
                error: err
            });
        }

        next();
    });
}

app.use('/',  require('./routes/index'));
app.use('/api/tags', require('./routes/tags'));
app.use('/api/itunes', require('./routes/itunes'));
app.use('/api/podcasts', require('./routes/podcasts'));
app.use('/api/podcasts', require('./routes/episodes'));

const httpServer = http.createServer(app);

httpServer.listen(PORT || 80, function () {
    console.log('Express server listening on port ' + (PORT || 80));
});

const wss = createWesocketServer(httpServer);
wss.on('connection', (ws) => {
    const id = uuidv4();
    metadata = { id }
    clients.set(ws, metadata);

    ws.on('message', (msg) => {
        const getPodpy = require('./helpers/os').getPodpy;
        const message = JSON.parse(msg);

        if (message.command === 'download') {
            let commands = ['download']

            if (typeof message.id !== 'undefined') {
                commands = ['podcast', message.id, 'download']
            }

            var proc = spawn(path.join(__dirname, getPodpy()), commands);
            proc.stdout.on('data', function (data) {
                ws.send(JSON.stringify({
                    success: true,
                    data: {
                        type: 'stdout',
                        msg: data.toString()
                    }
                }));
            });
            proc.stderr.on('data', function (data) {
                ws.send(JSON.stringify({
                    success: false,
                    data: {
                        type: 'stderr',
                        msg: data.toString()
                    }
                }));
            });
            proc.on('exit', code => {
                ws.send(JSON.stringify({
                    success: (code === 0),
                    data: {
                        type: 'exit',
                        msg: parseInt(code)
                    }
                }));
            });
        }
    });
});

wss.on('close', (ws) => {
    clients.delete(ws);
});

