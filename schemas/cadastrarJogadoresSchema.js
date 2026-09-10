const Joi = require("joi");

const cadastrarJogadoresSchema = Joi.object({
    estado: Joi.string()
        .valid("cadastrar jogadores")
        .required(),

    dados: Joi.object({
        idPartida: Joi.number()
            .integer()
            .positive()
            .required(),

        EDE: Joi.object({
            id: Joi.number()
                .integer()
                .positive()
                .required(),

            nome: Joi.string()
                .trim()
                .min(1)
                .max(100)
                .required()
        })
        .required(),

        EIT: Joi.object({
            id: Joi.number()
                .integer()
                .positive()
                .required(),

            nome: Joi.string()
                .trim()
                .min(1)
                .max(100)
                .required()
        })
        .required()
    })
    .required()
});

module.exports = cadastrarJogadoresSchema;