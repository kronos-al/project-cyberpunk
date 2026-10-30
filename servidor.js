require("dotenv").config();
const { app, httpServer } = require("./http-server.js");
const port = process.env.PORT || 3000;
const postWatingMatch = require("./routes/postWaitingMatch.js");
const postAddPlayer = require("./routes/postAddPlayer.js");
const postConfigBomb = require("./routes/postConfigBomb.js");

const { connectMongo, getDb } = require("./database/mongodb.js");
const { criarIndices } = require("./database/indices.js");
const { iniciarWebSocket } = require("./websocket/websocket-server.js");


require("./mqtt/mqtt-client.js");

app.use(postWatingMatch);
app.use(postConfigBomb);
app.use(postAddPlayer);
app.use("/partidas", require("./routes/getPartidas.js"));
app.use("/stats", require("./routes/getStats.js"));


async function startServer() {
    try {
        await connectMongo();
        await criarIndices(getDb());

        iniciarWebSocket(httpServer);

        httpServer.listen(port, () => {
            console.log("Server running!");
        });

    } catch (error) {
        console.error("Erro ao iniciar o servidor:", error);
        process.exit(1);
    }
}


startServer();