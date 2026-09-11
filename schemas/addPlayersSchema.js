const Joi = require("joi");

const addPlayersSchema = Joi.object({
    estado: Joi.string()
        .valid("ADICIONAR_JOGADORES")
        .required(),

    dados: Joi.object({
        idPartida: Joi.number()
            .integer()
            .positive()
            .required()
    })
});

module.exports = addPlayersSchema;