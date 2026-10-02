import os
import pygame
import math

# ==========================================
# CONFIGURAÇÃO
# ==========================================

ASSETS_PATH = "LabyrinthSprites"

WIDTH = 128
HEIGHT = 128

GRID_X = 6
GRID_Y = 6

CELL_WIDTH = 9
CELL_HEIGHT = 9

CELL_STEP = 18

GRID_OFFSET_X = 15
GRID_OFFSET_Y = 15

# ==========================================
# POSIÇÃO INICIAL DO JOGADOR
# ==========================================

PLAYER_START = {
    1: (3, 2),
    2: (3, 3),
    3: (4, 2),
    4: (2, 4),
    5: (3, 2),
    6: (4, 4)
}

# ==========================================
# INICIAR PYGAME
# ==========================================

pygame.init()

screen = pygame.display.set_mode(
    (0, 0),
    pygame.FULLSCREEN
)

pygame.display.set_caption(
    "BOMB.EXE - Labirinto"
)


# ==========================================
# TELA DO JOGO
# ==========================================

gameScreen = pygame.Surface(
    (WIDTH, HEIGHT)
)


# ==========================================
# CARREGAR BACKGROUND
# ==========================================

background = pygame.image.load(
    os.path.join(
        ASSETS_PATH,
        "Background.png"
    )
).convert_alpha()

# ==========================================
# CARREGAR OBJETIVOS
# ==========================================

objectives = []

for i in range(1, 7):

    objective = pygame.image.load(
        os.path.join(
            ASSETS_PATH,
            f"Objectives/Objective{i}.png"
        )
    ).convert_alpha()

    objectives.append(objective)


# ==========================================
# CARREGAR MAPAS DE PAREDES
# ==========================================

walls = []

for i in range(1, 7):

    wall = pygame.image.load(
        os.path.join(
            ASSETS_PATH,
            f"Walls/Wall{i}.png"
        )
    ).convert_alpha()

    walls.append(wall)

# ==========================================
# CARREGAR JOGADOR
# ==========================================

player = pygame.image.load(
    os.path.join(
        ASSETS_PATH,
        "Player.png"
    )
).convert_alpha()

moveSound = pygame.mixer.Sound(
    os.path.join(
        ASSETS_PATH,
        "move.mp3"
    )
)

wallSound = pygame.mixer.Sound(
    os.path.join(
        ASSETS_PATH,
        "wall.mp3"
    )
)


# ==========================================
# ESCOLHER OBJETIVO
# ==========================================

import random

chosenObjectiveNumber = random.randint(1, 6)

chosenObjective = objectives[
    chosenObjectiveNumber - 1
]

# Mapa de colisão do objetivo escolhido
chosenWall = walls[
    chosenObjectiveNumber - 1
]

playerStart = PLAYER_START[
    chosenObjectiveNumber
]
playerPosition = list(playerStart)
playerDirection = "cima"


# ==========================================
# DETECTAR OBJETIVOS
# ==========================================

def detectarObjetivos(image):

    yellowPixels = []

    for y in range(HEIGHT):
        for x in range(WIDTH):

            r, g, b, a = image.get_at((x, y))

            if r > 180 and g > 150 and b < 100:
                yellowPixels.append((x, y))

    # --------------------------------------
    # Agrupar pixels conectados
    # --------------------------------------

    pixels = set(yellowPixels)
    grupos = []

    while pixels:

        inicio = pixels.pop()
        grupo = [inicio]
        fila = [inicio]

        while fila:

            x, y = fila.pop()

            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):

                    if dx == 0 and dy == 0:
                        continue

                    vizinho = (x + dx, y + dy)

                    if vizinho in pixels:

                        pixels.remove(vizinho)
                        fila.append(vizinho)
                        grupo.append(vizinho)

        grupos.append(grupo)

    # --------------------------------------
    # Converter grupos para células
    # --------------------------------------

    objetivos = []

    for grupo in grupos:

        mediaX = sum(x for x, y in grupo) / len(grupo)
        mediaY = sum(y for x, y in grupo) / len(grupo)

        coluna = round(
            (mediaX - GRID_OFFSET_X) / CELL_STEP
        )

        linha = round(
            (mediaY - GRID_OFFSET_Y) / CELL_STEP
        )

        if 0 <= linha < GRID_Y and 0 <= coluna < GRID_X:

            objetivos.append(
                (linha, coluna)
            )

    return objetivos

objetivos = detectarObjetivos(chosenObjective)
puzzleResolvido = False
animacaoInicio = None
duracaoAnimacao = 1200  # 1,2 segundos

print(
    "Labirinto escolhido:",
    chosenObjectiveNumber
)

print(
    "Player começa em:",
    playerStart
)

print(
    "Objetivos:",
    objetivos
)


# ==========================================
# DETECTAR PAREDES INVISÍVEIS
# ==========================================

def temParede(linhaAtual, colunaAtual, linhaNova, colunaNova):

    # Centro da célula atual
    xAtual = (
        GRID_OFFSET_X
        + colunaAtual * CELL_STEP
        + CELL_WIDTH // 2
    )

    yAtual = (
        GRID_OFFSET_Y
        + linhaAtual * CELL_STEP
        + CELL_HEIGHT // 2
    )

    # Centro da próxima célula
    xNovo = (
        GRID_OFFSET_X
        + colunaNova * CELL_STEP
        + CELL_WIDTH // 2
    )

    yNovo = (
        GRID_OFFSET_Y
        + linhaNova * CELL_STEP
        + CELL_HEIGHT // 2
    )

    # Verificar os pixels entre as duas células
    distancia = max(
        abs(xNovo - xAtual),
        abs(yNovo - yAtual)
    )

    for i in range(1, distancia):

        x = round(
            xAtual + (xNovo - xAtual) * i / distancia
        )

        y = round(
            yAtual + (yNovo - yAtual) * i / distancia
        )

        r, g, b, a = chosenWall.get_at((x, y))

        # Pixels brancos representam paredes
        if a > 0 and r > 180 and g > 180 and b > 180:
            return True

    return False

def moverPlayer(direcao):

    if puzzleResolvido:
        return

    linha, coluna = playerPosition

    if direcao == "cima":
        linha -= 1

    elif direcao == "baixo":
        linha += 1

    elif direcao == "esquerda":
        coluna -= 1

    elif direcao == "direita":
        coluna += 1



    # --------------------------------------
    # Movimento válido
    # --------------------------------------

    if 0 <= linha < GRID_Y and 0 <= coluna < GRID_X:

        if not temParede(
            playerPosition[0],
            playerPosition[1],
            linha,
            coluna
        ):

            playerPosition[0] = linha
            playerPosition[1] = coluna

            moveSound.play()

        else:

            wallSound.play()

    # --------------------------------------
    # Fora do tabuleiro
    # --------------------------------------

    else:

        wallSound.play()

animationSpeed = 0.006
animationAmount = 0.04
# ==========================================
# LOOP
# ==========================================

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_UP:
                moverPlayer("cima")
                playerDirection = "cima"

            if event.key == pygame.K_DOWN:
                moverPlayer("baixo")
                playerDirection = "baixo"

            if event.key == pygame.K_LEFT:
                moverPlayer("esquerda")
                playerDirection = "esquerda"

            if event.key == pygame.K_RIGHT:
                moverPlayer("direita")
                playerDirection = "direita"

            if event.key == pygame.K_RETURN:

                if not puzzleResolvido and tuple(playerPosition) in objetivos:

                    puzzleResolvido = True
                    animacaoInicio = pygame.time.get_ticks()

                    print("PUZZLE RESOLVIDO!")

                elif not puzzleResolvido:

                    print("Você não está em um objetivo!")




    # --------------------------------------
    # Desenhar no tamanho original
    # --------------------------------------

    gameScreen.blit(
        background,
        (0, 0)
    )


    # --------------------------------------
    # Direção do jogador
    # --------------------------------------

    if playerDirection == "cima":

        playerImage = player

    elif playerDirection == "baixo":

        playerImage = pygame.transform.rotate(
            player,
            180
        )

    elif playerDirection == "esquerda":

        playerImage = pygame.transform.rotate(
            player,
            90
        )

    elif playerDirection == "direita":

        playerImage = pygame.transform.rotate(
            player,
            -90
        )


    # --------------------------------------
    # ANIMAÇÃO DO JOGADOR E CONCLUSÃO
    # --------------------------------------

    time = pygame.time.get_ticks()

    # Pulsação normal do jogador
    scale = 1 + math.sin(
        time * animationSpeed
    ) * animationAmount

    # Valores padrão
    progresso = 0
    fadeAlpha = 0

    if puzzleResolvido:

        tempoDecorrido = time - animacaoInicio

        progresso = min(
            tempoDecorrido / duracaoAnimacao,
            1
        )

        # Suavizar a animação com Smoothstep
        progressoSuave = (
            progresso * progresso
            * (3 - 2 * progresso)
        )

        # Diminuir o jogador até desaparecer
        scale *= 1 - progressoSuave

        # Escurecer a tela progressivamente
        fadeAlpha = int(
            progressoSuave * 255
        )

    # Não desenhar quando já desapareceu
    if scale > 0.01:

        animatedPlayer = pygame.transform.scale_by(
            playerImage,
            scale
        )

        playerX = (
            GRID_OFFSET_X
            + playerPosition[1] * CELL_STEP
            + (CELL_WIDTH - animatedPlayer.get_width()) // 2
        )

        playerY = (
            GRID_OFFSET_Y
            + playerPosition[0] * CELL_STEP
            + (CELL_HEIGHT - animatedPlayer.get_height()) // 2
        )

        gameScreen.blit(
            animatedPlayer,
            (playerX, playerY)
        )
    # --------------------------------------
    # Posição do jogador
    # --------------------------------------

    playerX = (
            GRID_OFFSET_X
            + playerPosition[1] * CELL_STEP
            + (CELL_WIDTH - animatedPlayer.get_width()) // 2
    )

    playerY = (
            GRID_OFFSET_Y
            + playerPosition[0] * CELL_STEP
            + (CELL_HEIGHT - animatedPlayer.get_height()) // 2
    )

    gameScreen.blit(
        animatedPlayer,
        (playerX, playerY)
    )

    gameScreen.blit(
        chosenObjective,
        (0, 0)
    )
    # --------------------------------------
    # FADE PARA PRETO
    # --------------------------------------

    if puzzleResolvido:

        blackOverlay = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        blackOverlay.fill((0, 0, 0))
        blackOverlay.set_alpha(fadeAlpha)

        gameScreen.blit(
            blackOverlay,
            (0, 0)
        )
    # --------------------------------------
    # Escalar mantendo proporção
    # --------------------------------------

    screenWidth, screenHeight = screen.get_size()

    scale = min(
        screenWidth / WIDTH,
        screenHeight / HEIGHT
    )

    newWidth = int(WIDTH * scale)
    newHeight = int(HEIGHT * scale)

    scaledScreen = pygame.transform.scale(
        gameScreen,
        (newWidth, newHeight)
    )

    # --------------------------------------
    # Fundo das bordas
    # --------------------------------------

    screen.fill(
        (0, 0, 0)
    )

    # --------------------------------------
    # Centralizar
    # --------------------------------------

    x = (screenWidth - newWidth) // 2
    y = (screenHeight - newHeight) // 2

    screen.blit(
        scaledScreen,
        (x, y)
    )

    pygame.display.flip()


# ==========================================
# FINALIZAR
# ==========================================

pygame.quit()