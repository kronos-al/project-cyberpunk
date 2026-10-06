import os
import pygame
import math
import random

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

PLAYER_START = {
    1: (3, 2),
    2: (3, 3),
    3: (4, 2),
    4: (2, 4),
    5: (3, 2),
    6: (4, 4)
}

animationSpeed = 0.006
animationAmount = 0.04
duracaoAnimacao = 1200

# ==========================================
# ESTADO GLOBAL
# ==========================================

screen = None
gameScreen = None

background = None
objectives = []
walls = []
player = None
moveSound = None
wallSound = None

chosenObjectiveNumber = None
chosenObjective = None
chosenWall = None

playerStart = None
playerPosition = None
playerDirection = "cima"

objetivos = []
animacaoInicio = None

partidaAtual = None
partidaAtiva = False
running = False


# ==========================================
# INICIALIZAR PYGAME E CARREGAR RECURSOS
# ==========================================

def iniciarJogo():
    global screen, gameScreen
    global background, objectives, walls
    global player, moveSound, wallSound

    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode(
        (0, 0),
        pygame.FULLSCREEN
    )

    pygame.display.set_caption("BOMB.EXE - Labirinto")

    gameScreen = pygame.Surface((WIDTH, HEIGHT))

    background = pygame.image.load(
        os.path.join(ASSETS_PATH, "Background.png")
    ).convert_alpha()

    objectives = []

    for i in range(1, 7):
        objective = pygame.image.load(
            os.path.join(
                ASSETS_PATH,
                f"Objectives/Objective{i}.png"
            )
        ).convert_alpha()

        objectives.append(objective)

    walls = []

    for i in range(1, 7):
        wall = pygame.image.load(
            os.path.join(
                ASSETS_PATH,
                f"Walls/Wall{i}.png"
            )
        ).convert_alpha()

        walls.append(wall)

    player = pygame.image.load(
        os.path.join(ASSETS_PATH, "Player.png")
    ).convert_alpha()

    moveSound = pygame.mixer.Sound(
        os.path.join(ASSETS_PATH, "move.mp3")
    )

    wallSound = pygame.mixer.Sound(
        os.path.join(ASSETS_PATH, "wall.mp3")
    )


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

    objetivosEncontrados = []

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
            objetivosEncontrados.append((linha, coluna))

    return objetivosEncontrados


# ==========================================
# INICIAR / REINICIAR PARTIDA
# ==========================================

def iniciarPartida(partida):
    global partidaAtual, partidaAtiva
    global chosenObjectiveNumber, chosenObjective, chosenWall
    global playerStart, playerPosition, playerDirection
    global objetivos, animacaoInicio

    if screen is None:
        iniciarJogo()

    partidaAtual = partida

    chosenObjectiveNumber = random.randint(1, 6)

    chosenObjective = objectives[chosenObjectiveNumber - 1]
    chosenWall = walls[chosenObjectiveNumber - 1]

    playerStart = PLAYER_START[chosenObjectiveNumber]
    playerPosition = list(playerStart)
    playerDirection = "cima"

    objetivos = detectarObjetivos(chosenObjective)

    partida.puzzle5 = False
    animacaoInicio = None

    partidaAtiva = True

    print("Labirinto escolhido:", chosenObjectiveNumber)
    print("Player começa em:", playerStart)
    print("Objetivos:", objetivos)


# ==========================================
# DETECTAR PAREDES INVISÍVEIS
# ==========================================

def temParede(linhaAtual, colunaAtual, linhaNova, colunaNova):
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

        if a > 0 and r > 180 and g > 180 and b > 180:
            return True

    return False


def resetPartida():
    global partidaAtiva
    partidaAtiva = False

# ==========================================
# MOVIMENTAR JOGADOR
# ==========================================

def moverPlayer(direcao):
    if partidaAtual.puzzle5:
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
    else:
        wallSound.play()


# ==========================================
# LOOP PRINCIPAL
# ==========================================

def executarJogo():
    global running, partidaAtiva
    global playerDirection, animacaoInicio

    if screen is None:
        iniciarJogo()

    running = True
    partidaAtiva = False

    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if (
                    partidaAtiva
                    and partidaAtual is not None
                    and partidaAtual.falhas <= 3
                ):
                    if event.key == pygame.K_UP:
                        moverPlayer("cima")
                        playerDirection = "cima"

                    elif event.key == pygame.K_DOWN:
                        moverPlayer("baixo")
                        playerDirection = "baixo"

                    elif event.key == pygame.K_LEFT:
                        moverPlayer("esquerda")
                        playerDirection = "esquerda"

                    elif event.key == pygame.K_RIGHT:
                        moverPlayer("direita")
                        playerDirection = "direita"

                    elif event.key == pygame.K_RETURN:
                        if (
                            not partidaAtual.puzzle5
                            and tuple(playerPosition) in objetivos
                        ):
                            partidaAtual.puzzle5 = True
                            animacaoInicio = pygame.time.get_ticks()
                            print("PUZZLE RESOLVIDO!")

                        elif not partidaAtual.puzzle5:
                            print("Você não está em um objetivo!")

        if partidaAtiva and partidaAtual is not None and partidaAtual.falhas <= 3:
            gameScreen.blit(background, (0, 0))

            if playerDirection == "cima":
                playerImage = player
            elif playerDirection == "baixo":
                playerImage = pygame.transform.rotate(player, 180)
            elif playerDirection == "esquerda":
                playerImage = pygame.transform.rotate(player, 90)
            else:
                playerImage = pygame.transform.rotate(player, -90)

            tempoAtual = pygame.time.get_ticks()

            scale = 1 + math.sin(
                tempoAtual * animationSpeed
            ) * animationAmount

            fadeAlpha = 0

            if partidaAtual.puzzle5:
                tempoDecorrido = tempoAtual - animacaoInicio

                progresso = min(
                    tempoDecorrido / duracaoAnimacao,
                    1
                )

                progressoSuave = (
                    progresso * progresso
                    * (3 - 2 * progresso)
                )

                scale *= 1 - progressoSuave
                fadeAlpha = int(progressoSuave * 255)

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

                gameScreen.blit(animatedPlayer, (playerX, playerY))

            gameScreen.blit(chosenObjective, (0, 0))

            if partidaAtual.puzzle5:
                blackOverlay = pygame.Surface((WIDTH, HEIGHT))
                blackOverlay.fill((0, 0, 0))
                blackOverlay.set_alpha(fadeAlpha)
                gameScreen.blit(blackOverlay, (0, 0))

            screenWidth, screenHeight = screen.get_size()

            escalaTela = min(
                screenWidth / WIDTH,
                screenHeight / HEIGHT
            )

            newWidth = int(WIDTH * escalaTela)
            newHeight = int(HEIGHT * escalaTela)

            scaledScreen = pygame.transform.scale(
                gameScreen,
                (newWidth, newHeight)
            )

            screen.fill((0, 0, 0))

            x = (screenWidth - newWidth) // 2
            y = (screenHeight - newHeight) // 2

            screen.blit(scaledScreen, (x, y))

        else:
            screen.fill((0, 0, 0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
