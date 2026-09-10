const Joi = require("joi");

const addPlayersSchema = Joi.object({
    estado: Joi.string()
        .valid("Adicionar Jogadores")
        .required(),

    dados: Joi.object({
        idPartida: Joi.number()
            .integer()
            .positive()
            .required()
    })
});

module.exports = addPlayersSchema;