const Joi = require("joi");

const addPlayersSchema = Joi.object({
    estado: Joi.string()
        .valid("ADICIONAR_JOGADORES")
        .required(),

    dados: Joi.object({
        idPartida: Joi.number()
            .integer()
            .positive()
            .required(),

        // id do usuário (Feira de Jogos) que será o EDE
        ede: Joi.number()
            .integer()
            .positive()
            .required(),

        // id do usuário (Feira de Jogos) que será o EIT (joga no manual)
        eit: Joi.number()
            .integer()
            .positive()
            .required()
    }).required()
});

module.exports = addPlayersSchema;