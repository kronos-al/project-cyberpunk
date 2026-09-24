from enum import Enum
from typing import List
from pydantic import BaseModel, Field, model_validator



# Schema interno para o objeto "dados"
class DadosAguardandoPartidaSchema(BaseModel):
    idPartida: int = Field(...)  # O '...' significa que o campo continua sendo obrigatório

# Schema principal para o estado AGUARDANDO_PARTIDA
class AguardandoPartidaSchema(BaseModel):
    estado: str
    dados: DadosAguardandoPartidaSchema

class ComecarPartidaSchema(BaseModel):
    estado: str
    dados: DadosAguardandoPartidaSchema


class CorEnum(str, Enum):
    VERMELHO = "VERMELHO"
    VERDE = "VERDE"
    AZUL = "AZUL"
    LARANJA = "LARANJA"
    MARROM = "MARROM"

class FioSchema(BaseModel):
    posicao: int = Field(..., ge=1, le=5)
    cor: CorEnum


class DadosConfigurarFiosSchema(BaseModel):
    idPartida: int = Field(..., gt=0)  # Equivalente a .positive()
    numeroDeFios: int = Field(..., ge=3, le=5)
    fios: List[FioSchema]

    @model_validator(mode="after")
    def validar_regras_dos_fios(self):
        # Validação 1: Quantidade de fios deve ser igual a numeroDeFios
        if len(self.fios) != self.numeroDeFios:
            raise ValueError(
                "A quantidade de fios deve ser igual a numeroDeFios"
            )

        # Validação 2: As posições não podem se repetir
        posicoes = [fio.posicao for fio in self.fios]
        if len(set(posicoes)) != len(posicoes):
            raise ValueError("As posições dos fios não podem se repetir")

        return self


class ConfigBombSchema(BaseModel):
    estado: str
    dados: DadosConfigurarFiosSchema