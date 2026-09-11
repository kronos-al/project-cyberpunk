const Joi = require("joi");

const configBombSchema = Joi.object({
    estado: Joi.string()
        .valid("AGUARDANDO_PARTIDA")
        .required(),

    dados: Joi.object({
        idPartida: Joi.number()
            .integer()
            .positive()
            .required(),

        numeroDeFios: Joi.number()
            .integer()
            .min(3)
            .max(5)
            .required(),

        fios: Joi.array()
            .items(
                Joi.object({
                    posicao: Joi.number()
                        .integer()
                        .min(1)
                        .max(5)
                        .required(),

                    cor: Joi.string()
                        .valid(
                            "VERMELHO",
                            "VERDE",
                            "AZUL",
                            "LARANJA",
                            "MARROM"
                        )
                        .required()
                })
            )
            .required()
    })
    .custom((dados, helpers) => {

        // A quantidade de fios deve ser igual a numeroDeFios
        if (dados.fios.length !== dados.numeroDeFios) {
            return helpers.message({
                custom:
                    "A quantidade de fios deve ser igual a numeroDeFios"
            });
        }

        // As posições não podem se repetir
        const posicoes = dados.fios.map(fio => fio.posicao);

        const posicoesUnicas = new Set(posicoes);

        if (posicoesUnicas.size !== posicoes.length) {
            return helpers.message({
                custom:
                    "As posições dos fios não podem se repetir"
            });
        }

        return dados;
    })
});

module.exports = configBombSchema;