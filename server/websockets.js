const WebSocket = require('ws');
const clients = new Map();

function createWesocketServer(httpServer) {
    const wss = new WebSocket.Server({
        noServer: true,
        path: "/websockets"
    });

    httpServer.on("upgrade", (request, socket, head) => {
        wss.handleUpgrade(request, socket, head, (websocket) => {
            wss.emit("connection", websocket, request);
        });
    });

    return wss;
}

module.exports = { createWesocketServer, clients };