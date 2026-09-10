const Joi = require("joi");

const comecarPartidaSchema = Joi.object({
    estado: Joi.string()
        .valid("Começar Partida")
        .required(),

    dados: Joi.object({
        idPartida: Joi.number()
            .integer()
            .positive()
            .required()
    })
    .required()
});

module.exports = comecarPartidaSchema;