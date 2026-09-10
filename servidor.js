require("dotenv").config();
const { app, httpServer } = require("./http-server.js");
const port = process.env.PORT || 3000;
const postWatingMatch = require("./routes/postWaitingMatch.js");
const postAddPlayer = require("./routes/postAddPlayer.js");
const postConfigBomb = require("./routes/postConfigBomb.js");

const { connectMongo } = require("./database/mongodb.js");
const { iniciarWebSocket } = require("./websocket/websocket-server.js");

require("./mqtt/mqtt-client.js");

app.use(postWatingMatch);
app.use(postConfigBomb);
app.use(postAddPlayer);


async function startServer() {
    try {
        await connectMongo();

        iniciarWebSocket(httpServer);

        httpServer.listen(port, () => {
            console.log("Server running!");
        });

    } catch (error) {
        console.error("Erro ao conectar ao MongoDB:", error);
        process.exit(1);
    }
}


startServer();