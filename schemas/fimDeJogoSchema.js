const Joi = require("joi");

const fimDeJogoSchema = Joi.object({
    estado: Joi.string()
        .valid("FIM_DE_JOGO")
        .required(),

    dados: Joi.object({
        idPartida: Joi.number()
            .integer()
            .positive()
            .required(),

        erros: Joi.number()
            .integer()
            .min(0)
            .max(3)
            .required(),

        tempo: Joi.number()
            .integer()
            .min(0)
            .required(),
        
        resultado: Joi.string()
            .valid("VITORIA", "DERROTA")
            .required(),

        puzzles: Joi.object({
                    chaveDeInicializacao: Joi.boolean()
                        .required(),
        
                    ajusteDeSintonizacao: Joi.boolean()
                        .required(),

                    bussolaDeLeds: Joi.boolean()
                        .required(),

                    labirinto: Joi.boolean()
                        .required(),

                    fios: Joi.boolean()
                        .required()

                })
    })
});

module.exports = fimDeJogoSchema;