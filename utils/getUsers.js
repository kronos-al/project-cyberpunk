const axios = require("axios");

const FEIRA_API = "https://feira-de-jogos.dev.br/api/v2";

class ErroFeira extends Error {
    constructor(status, mensagem) {
        super(mensagem);
        this.status = status;
    }
}

/**
 * Busca um usuário na Feira de Jogos (POST /getUser).
 * O token é o ID token do Google do operador (o mesmo de req.token).
 *
 * Retorna { id, nome }. Em caso de falha lança ErroFeira com
 * status HTTP e mensagem prontos para devolver ao admin.
 */
async function buscarUsuario(token, userId, papel) {
    try {
        const { data } = await axios.post(
            `${FEIRA_API}/getUser`,
            { userId },
            {
                headers: { Authorization: `Bearer ${token}` },
                timeout: 10000
            }
        );

        if (!data?.id || !data?.name) {
            throw new ErroFeira(
                502,
                `Resposta inválida da Feira de Jogos ao buscar o ${papel}.`
            );
        }

        return { id: data.id, nome: data.name };
    } catch (err) {
        if (err instanceof ErroFeira) throw err;

        const status = err.response?.status;

        if (status === 404) {
            throw new ErroFeira(404, `Jogador ${papel} (id ${userId}) não encontrado.`);
        }

        if (status === 401 || status === 403) {
            throw new ErroFeira(status, "Usuário não autorizado.");
        }

        console.error(
            `Erro ao buscar ${papel} (id ${userId}) na Feira de Jogos:`,
            err.response?.data || err.message
        );

        throw new ErroFeira(
            502,
            `Não foi possível consultar o jogador ${papel} na Feira de Jogos.`
        );
    }
}

module.exports = { buscarUsuario, ErroFeira };