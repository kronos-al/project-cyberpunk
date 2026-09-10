async function handleBombaMessage(topic, dados) {
    console.log("Mensagem recebida da Bomba!");
    console.log("Topic:", topic);
    console.log("Dados:", dados);
}

module.exports = {
    handleBombaMessage
};