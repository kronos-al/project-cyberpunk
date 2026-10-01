import os
import random
import pygame


class Labyrinth:

    # ==========================================
    # GRID
    # ==========================================

    GRID_X = 6
    GRID_Y = 6

    CELL_WIDTH = 9
    CELL_HEIGHT = 9

    CELL_STEP = 18

    GRID_OFFSET_X = 15
    GRID_OFFSET_Y = 15

    # ==========================================
    # CONFIGURAÇÕES DOS LABIRINTOS
    # ==========================================

    CONFIGURACOES = {

        1: {
            "playerStart": (0, 0),
        },

        2: {
            "playerStart": (0, 0),
        },

        3: {
            "playerStart": (0, 0),
        },

        4: {
            "playerStart": (0, 0),
        },

        5: {
            "playerStart": (0, 0),
        },

        6: {
            "playerStart": (0, 0),
        }

    }

    # ==========================================
    # INICIALIZAÇÃO
    # ==========================================

    def __init__(self, assetsPath):

        self.assetsPath = assetsPath

        self.configuracao = None

        self.playerPosition = None

        self.objectivePositions = []

        self.completed = False

        # ------------------------------------------
        # Carregar Background
        # ------------------------------------------

        self.background = pygame.image.load(
            os.path.join(
                self.assetsPath,
                "Background.png"
            )
        ).convert_alpha()

        # ------------------------------------------
        # Carregar Objectives
        # ------------------------------------------

        self.objectives = {}

        for numero in range(1, 7):

            caminho = os.path.join(
                self.assetsPath,
                "Objectives",
                f"Objective{numero}.png"
            )

            self.objectives[numero] = pygame.image.load(
                caminho
            ).convert_alpha()

    # ==========================================
    # INICIAR LABIRINTO
    # ==========================================

    def iniciar(self, configuracao=None):

        if configuracao is None:
            configuracao = random.randint(1, 6)

        self.configuracao = configuracao

        # ------------------------------------------
        # Posição inicial do Player
        # ------------------------------------------

        self.playerPosition = (
            self.CONFIGURACOES[configuracao]["playerStart"]
        )

        # ------------------------------------------
        # Descobrir os objetivos pela imagem
        # ------------------------------------------

        objectiveImage = self.objectives[configuracao]

        self.objectivePositions = (
            self.detectarObjetivos(objectiveImage)
        )

        self.completed = False

        print(
            f"Labirinto escolhido: {self.configuracao}"
        )

        print(
            f"Player começa em: {self.playerPosition}"
        )

        print(
            f"Objetivos: {self.objectivePositions}"
        )

    # ==========================================
    # DETECTAR OBJETIVOS
    # ==========================================

    def detectarObjetivos(self, image):

        largura = image.get_width()
        altura = image.get_height()

        pixels = pygame.PixelArray(image)

        visitados = set()
        centros = []

        # ------------------------------------------
        # Verificar se o pixel é amarelo
        # ------------------------------------------

        def ehAmarelo(x, y):

            color = image.unmap_rgb(
                pixels[x, y]
            )

            return (
                    color.r > 180
                    and color.g > 180
                    and color.b < 100
            )

        # ------------------------------------------
        # Procurar os objetivos
        # ------------------------------------------

        for y in range(altura):

            for x in range(largura):

                if (x, y) in visitados:
                    continue

                if not ehAmarelo(x, y):
                    continue

                fila = [(x, y)]
                visitados.add((x, y))

                pixelsObjetivo = []

                while fila:

                    px, py = fila.pop()

                    pixelsObjetivo.append(
                        (px, py)
                    )

                    # ----------------------------------
                    # 8 vizinhos
                    # ----------------------------------

                    for dx in (-1, 0, 1):

                        for dy in (-1, 0, 1):

                            if dx == 0 and dy == 0:
                                continue

                            vx = px + dx
                            vy = py + dy

                            if not (
                                    0 <= vx < largura
                                    and
                                    0 <= vy < altura
                            ):
                                continue

                            if (vx, vy) in visitados:
                                continue

                            if not ehAmarelo(vx, vy):
                                continue

                            visitados.add(
                                (vx, vy)
                            )

                            fila.append(
                                (vx, vy)
                            )

                # ------------------------------------------
                # Centro do objetivo
                # ------------------------------------------

                if pixelsObjetivo:
                    centroX = sum(
                        p[0] for p in pixelsObjetivo
                    ) / len(pixelsObjetivo)

                    centroY = sum(
                        p[1] for p in pixelsObjetivo
                    ) / len(pixelsObjetivo)

                    centros.append(
                        (centroX, centroY)
                    )

        del pixels

        # ------------------------------------------
        # Converter centro para Grid
        # ------------------------------------------

        positions = []

        for centroX, centroY in centros:
            coluna = round(
                (
                        centroX
                        - self.GRID_OFFSET_X
                        - self.CELL_WIDTH / 2
                )
                / self.CELL_STEP
            )

            linha = round(
                (
                        centroY
                        - self.GRID_OFFSET_Y
                        - self.CELL_HEIGHT / 2
                )
                / self.CELL_STEP
            )

            positions.append(
                (linha, coluna)
            )

        return positions

    # ==========================================
    # POSIÇÃO DA CÉLULA EM PIXELS
    # ==========================================

    def getCellPosition(self, row, column):

        x = (
            self.GRID_OFFSET_X
            + column * self.CELL_STEP
        )

        y = (
            self.GRID_OFFSET_Y
            + row * self.CELL_STEP
        )

        return x, y

    # ==========================================
    # DESENHAR
    # ==========================================

    def draw(self, screen):

        # Background
        screen.blit(
            self.background,
            (0, 0)
        )

        # Objective
        screen.blit(
            self.objectives[self.configuracao],
            (0, 0)
        )