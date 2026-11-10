const axios = require("axios");
 
// Ajuste se o caminho da rota na Feira de Jogos for diferente
const FEIRA_API = "https://feira-de-jogos.dev.br/api/v2";
 
// ==========================================
// TABELA DE PREMIAÇÃO (TJL)
// Cada faixa vai "até" X segundos; valores = [0 erros, 1 erro, 2 erros]
// ==========================================
const FAIXAS = [
    { ate: 120, valores: [700, 650, 600] },        // até 2min
    { ate: 180, valores: [550, 500, 450] },        // 2min01s a 3min
    { ate: 240, valores: [450, 400, 350] },        // 3min01s a 4min
    { ate: 300, valores: [350, 300, 300] },        // 4min01s a 5min
    { ate: Infinity, valores: [300, 250, 200] }    // acima de 5min
];
 
/**
 * Valor (TJL) que CADA jogador recebe.
 * Bomba explodida (qualquer resultado diferente de VITORIA) = 0.
 */
function calcularCreditos({ resultado, tempo, erros }) {
    if (resultado !== "VITORIA") return 0;
 
    const segundos = Number.isFinite(tempo) ? tempo : Infinity;
    const faixa = FAIXAS.find((f) => segundos <= f.ate);
 
    // Vitória só acontece com 0, 1 ou 2 erros (3 = explosão)
    const indice = Math.min(Math.max(Number(erros) || 0, 0), 2);
 
    return faixa.valores[indice];
}
 
// Chama a rota gameCredit da Feira de Jogos. Retorna o operationId.
async function creditarJogador(userId, price) {
    const { data } = await axios.post(
        `${FEIRA_API}/gameCredit`,
        { userId, price },
        {
            headers: { Authorization: `Bearer ${process.env.FEIRA_SECRET}` },
            timeout: 10000
        }
    );
 
    return data.operationId;
}
 
/**
 * Credita EDE e EIT ao fim da partida e registra o resultado na partida
 * (campo "creditos"), para dar para auditar e reprocessar falhas.
 * Nunca lança erro: uma falha aqui não pode atrapalhar o fim de jogo.
 */
async function creditarPartida(db, idPartida, jogadores, dadosFim) {
    const valor = calcularCreditos(dadosFim);
    const creditos = { valor, EDE: null, EIT: null };
 
    try {
        if (valor > 0) {
            await Promise.all(
                ["EDE", "EIT"].map(async (papel) => {
                    const userId = jogadores?.[papel]?.id;
 
                    if (!userId) {
                        creditos[papel] = { ok: false, erro: "jogador não cadastrado" };
                        return;
                    }
 
                    try {
                        const operationId = await creditarJogador(userId, valor);
                        creditos[papel] = { ok: true, userId, operationId };
                    } catch (err) {
                        const motivo = err.response?.status
                            ? `HTTP ${err.response.status}`
                            : err.message;
 
                        console.error(
                            `Falha ao creditar ${papel} (id ${userId}) na partida ${idPartida}: ${motivo}`
                        );
                        creditos[papel] = { ok: false, userId, erro: motivo };
                    }
                })
            );
        }
 
        await db.collection("partidas").updateOne(
            { _id: idPartida },
            { $set: { creditos } }
        );
 
        console.log(`Créditos da partida ${idPartida}:`, JSON.stringify(creditos));
    } catch (err) {
        console.error(`Erro ao registrar créditos da partida ${idPartida}:`, err);
    }
 
    return creditos;
}
 
module.exports = { calcularCreditos, creditarPartida };