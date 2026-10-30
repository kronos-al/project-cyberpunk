/**
 * Chame uma vez depois de conectar no MongoDB:
 *
 *   const { criarIndices } = require("./database/indices.js");
 *   await criarIndices(getDb());
 *
 * E monte as rotas no app principal:
 *
 *   app.use("/partidas", require("./routes/partidas.js"));
 *   app.use("/stats", require("./routes/stats.js"));
 */
async function criarIndices(db) {
    const partidas = db.collection("partidas");

    await Promise.all([
        partidas.createIndex({ createdAt: -1 }),
        partidas.createIndex({ estado: 1, createdAt: -1 }),
        partidas.createIndex({ estado: 1, resultado: 1 }),
        partidas.createIndex({ "jogadores.EDE.id": 1, createdAt: -1 }),
        partidas.createIndex({ "jogadores.EIT.id": 1, createdAt: -1 }),
    ]);

    console.log("Índices de partidas garantidos.");
}

module.exports = { criarIndices };
