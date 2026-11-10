const Joi = require("joi");

// A Unity só confirma o idPartida; os jogadores já foram salvos pelo postAddPlayer
const cadastrarJogadoresSchema = Joi.object({
    estado: Joi.string()
        .valid("CADASTRAR_JOGADORES")
        .required(),

    dados: Joi.object({
        idPartida: Joi.number()
            .integer()
            .positive()
            .required()
    }).required()
});

module.exports = cadastrarJogadoresSchema;