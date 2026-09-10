const { MongoClient } = require("mongodb");
const client = new MongoClient(process.env.MONGODB_URI);

let db;

async function connectMongo() {
    await client.connect();

    db = client.db("feiraDeJogosDB");

    console.log("MongoDB conectado!");
}

function getDb() {
    return db;
}

module.exports = {
    connectMongo,
    getDb
};