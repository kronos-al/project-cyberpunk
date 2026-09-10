const { getDb } = require("./mongodb.js");

async function getNextSequence(name) {
    const db = getDb();

    const result = await db.collection("counters").findOneAndUpdate(
    { _id: name },
    { $inc: { seq: 1 } },
    {
        upsert: true,
        returnDocument: "after"
    }
);

return result.value.seq;
}

module.exports = {
    getNextSequence
};