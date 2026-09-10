const { WebSocketServer } = require("ws");
const { getDb } = require("../database/mongodb.js");

const wss = new WebSocketServer({
    noServer: true
});

function iniciarWebSocket(httpServer) {

    httpServer.on("upgrade", async (request, socket, head) => {

        try {

            const url = new URL(
                request.url,
                `http://${request.headers.host}`
            );

            // Só aceita /admin/UUID
            if (!url.pathname.startsWith("/admin/")) {
                socket.destroy();
                return;
            }

            const uuid = url.pathname.substring("/admin/".length);

            // UUID v4
            const uuidRegex =
                /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

            if (!uuidRegex.test(uuid)) {
                socket.destroy();
                return;
            }

            const db = getDb();

            const partida = await db.collection("partidas").findOne({
                uuid: uuid
            });

            if (!partida) {
                socket.destroy();
                return;
            }

            wss.handleUpgrade(
                request,
                socket,
                head,
                (ws) => {

                    wss.emit(
                        "connection",
                        ws,
                        request,
                        partida
                    );
                }
            );

        } catch (error) {

            console.error(
                "Erro ao processar conexão WebSocket:",
                error
            );

            socket.destroy();
        }
    });


    wss.on("connection", (ws, request, partida) => {

        console.log(
            `Administrador conectado à partida ${partida._id}`
        );

        ws.send(JSON.stringify({
            estado: "Conectado",
            dados: {
                idPartida: partida._id
            }
        }));
    });


    console.log("Servidor WebSocket iniciado.");
}

module.exports = {
    iniciarWebSocket
};