# Game Design Document


> GDD - Bomb.exe

- Overview
  - Theme / Setting / Genre
  - Core Gameplay Mechanics Brief
  - Targeted platforms
  - Monetization model (Brief/Document)
  - Project Scope
  - Influences (Brief)
    - Keep Talking and Nobody Explodes
    - Bombanana
    - Ponto Cego
    - Matrix
    - Mr. Robot
  - The elevator Pitch
  - Project Description (Brief)
  - Project Description (Detailed)
- What sets this project apart?
  - Core Gameplay Mechanics (Detailed)
    - Comunicação e cooperação assimétrica
    - Desarme dos cinco módulos
    - Informações e elementos aleatórios
    - Limite de tempo e sistema de falhas
- Story and Gameplay
  - Story (Brief)
  - Story (Detailed)
  - Gameplay (Brief)
  - Gameplay (Detailed)
- Assets Needed
  - 2D
  - 3D
  - Sound
  - Code
  - Animation
- Schedule
  - Planejamento e prototipação
  - Desenvolvimento dos módulos
  - Desenvolvimento da interface e terminal
  - Integração, testes e apresentação


# Overview

## Theme / Setting / Genre

**Bomb.exe** é um jogo cooperativo de desarme de bombas ambientado em uma sociedade futurista no ano de **2149**.

O jogo combina elementos de **ficção científica, suspense, tecnologia e investigação**, apresentando uma estética inspirada em terminais computacionais antigos, sistemas militares e interfaces tecnológicas através de uma narrativa que acompanha dois agentes da Agência Nacional de Segurança (ANS) durante uma situação de emergência.

O gênero principal é **jogo cooperativo de resolução de puzzles**, com foco em comunicação, interpretação de informações e trabalho em equipe.

## Core Gameplay Mechanics Brief

- Comunicação obrigatória entre dois jogadores com informações diferentes.
- Interpretação de instruções e protocolos presentes no manual.
- Desarme de cinco módulos independentes.
- Elementos dos módulos gerados aleatoriamente a cada partida.
- Limite de cinco minutos para concluir a missão.
- Sistema de três falhas que resulta na detonação da bomba.

## Targeted platforms

## Targeted platforms

- **Dispositivo físico:** Bomba física utilizada como principal meio de interação durante a partida.
- **Notebook:** Utilizado para executar o manual interativo digital que acompanha a bomba física.
- **Sistema operacional:** Linux.
- **Engine:** Unity.

O projeto é composto por uma experiência híbrida, combinando um dispositivo físico com um manual interativo digital, que  será desenvolvido na Unity e executado em um computador acadêmico com sistema operacional Linux.

## Monetization model (Brief/Document)

- **Modelo:** Venda do jogo físico + software complementar gratuito.
- **Produto:** Kit físico contendo a bomba e todos os componentes necessários para jogar.
- **Preço estimado:** R$ 90,00 a R$ 110,00 por kit.
- **Software:** Aplicação gratuita para computador, utilizada como manual interativo durante as partidas.
- **Modelo de negócio:** Venda unitária do produto físico, sem anúncios, microtransações ou assinatura.

A proposta de monetização segue o modelo tradicional de jogos físicos comercializados no varejo, especialmente em lojas de brinquedos e jogos, onde o consumidor adquire o kit físico por um valor estimado entre R$ 90,00 e R$ 110,00, contendo a estrutura da bomba e os componentes necessários para realizar as partidas. Assim, após adquirir o produto, o jogador instala gratuitamente o aplicativo complementar em um celular(versão comercial para dispositivos mobile). A aplicação funciona como o manual interativo do jogo e é necessária para a experiência cooperativa completa, trabalhando em conjunto com a bomba física.

## Project Scope

### Game Time Scale

- **Custo:** Projeto acadêmico desenvolvido sem fins lucrativos.
- **Tempo de desenvolvimento:** 15 semanas, até o dia 5 de novembro.
- **Escopo:** Protótipo jogável contendo os cinco módulos de desarme, terminal tático, sistema de tempo, sistema de falhas e elementos aleatórios.

### Team Size

### Core Team

#### Desenvolvimento de Software e Hardware

Responsável pelo desenvolvimento técnico do projeto, abrangendo tanto a aplicação digital quanto a programação e integração dos componentes eletrônicos do dispositivo físico.

- Desenvolvimento da aplicação interativa utilizando Unity.
- Implementação das mecânicas e sistemas do jogo.
- Desenvolvimento da interface e do manual interativo digital.
- Programação dos componentes eletrônicos do dispositivo físico.
- Integração entre software e hardware.
- Implementação dos módulos e sistemas de interação.
- Desenvolvimento do sistema de comunicação entre os componentes.
- Integração dos sensores, botões, LEDs, potenciômetros e demais componentes.
- Testes, depuração e manutenção dos sistemas.

#### Montagem Física e Design do Protótipo

Responsável pela concepção, construção e acabamento do dispositivo físico, além do desenvolvimento de ideias e soluções para a interação dos jogadores.

- Concepção e desenvolvimento das ideias para os módulos físicos.
- Projeto e montagem da estrutura da bomba.
- Seleção e organização dos componentes eletrônicos.
- Soldagem e montagem dos circuitos.
- Instalação e organização dos componentes no dispositivo.
- Desenvolvimento dos mecanismos físicos de interação.
- Acabamento e organização visual do protótipo.
- Testes físicos e ajustes dos mecanismos.
- Integração da estrutura física com os sistemas eletrônicos e digitais.

### Marketing Team

O jogo será apresentado em um **ambiente interativo que simula uma cena de crime**, utilizando elementos visuais e físicos para despertar a curiosidade do público, criando uma presença visual que possa ser identificada à distância e incentivando o público a se aproximar para descobrir o que está acontecendo. Entre os elementos planejados estão:

- Ambientação inspirada em uma cena de crime.
- Utilização de pó neon e marcas visuais nas paredes para criar pontos de atenção.
- Iluminação, efeitos visuais e sonoros associados à bomba.
- LEDs e componentes luminosos no dispositivo para chamar a atenção do público.
- Elementos físicos e tecnológicos expostos para despertar curiosidade.
- Identidade visual consistente entre o ambiente, a bomba e o manual interativo.

#### Total Costs with breakdown

O custo estimado para a construção do protótipo considera os componentes eletrônicos, a estrutura física da bomba e a ambientação necessária para a apresentação do projeto. Equipamentos de informática não são contabilizados, considerando a utilização de recursos já disponíveis.

#### Hardware e eletrônica

| Item | Quantidade | Custo unitário | Custo estimado |
|---|---:|---:|---:|
| Teclado matricial | 1 | R$ 30,00 | R$ 30,00 |
| Ventoinha | 1 | R$ 5,00 | R$ 5,00 |
| LEDs de sucesso | 5 | R$ 1,00 | R$ 5,00 |
| LEDs de erro | 3 | R$ 1,00 | R$ 3,00 |
| LEDs dos controladores | 6 | R$ 1,00 | R$ 6,00 |
| Potenciômetro | 1 | R$ 10,00 | R$ 10,00 |
| Knob | 1 | R$ 8,00 | R$ 8,00 |
| Conectores borne | 5 | R$ 3,00 | R$ 15,00 |
| Displays LCD 16x2 | 2 | R$ 20,00 | R$ 40,00 |
| Display LCD 128x128 | 1 | R$ 35,00 | R$ 35,00 |
| Display 7 segmentos 4 dígitos I2C | 1 | R$ 10,00 | R$ 10,00 |
| Arduino Mega | 1 | R$ 80,00 | R$ 80,00 |
| Shield Wi-Fi | 1 | R$ 50,00 | R$ 50,00 |
| Fios, cabos, resistores e componentes auxiliares | - | - | R$450,00 |
| **Subtotal** | | | **R$ 337,00** |

#### Estrutura física da bomba

| Item | Custo estimado |
|---|---:|
| Estrutura e materiais para construção | R$ 50,00 |
| Materiais de acabamento | R$ 30,00 |
| Fixadores, suportes e componentes mecânicos | R$ 20,00 |
| **Subtotal** | **R$ 100,00** |

#### Cenário e ambientação

| Item | Custo estimado |
|---|---:|
| Estrutura para montagem do cenário | R$ 00,00 |
| Materiais de caracterização | R$ 50,00 |
| Iluminação | R$ 00,00 |
| Pó neon e materiais para efeitos visuais | R$ 26,00 |
| **Subtotal** | **R$ 76,00** |

#### Software e ferramentas

| Item | Custo estimado |
|---|---:|
| Unity | R$ 0,00 |
| Ferramentas de desenvolvimento | R$ 0,00 |
| Ferramentas de criação de conteúdo | R$ 0,00 |
| **Subtotal** | **R$ 0,00** |

\* Utilização de versões gratuitas, acadêmicas ou ferramentas já disponíveis pela equipe.

### Resumo dos custos

| Categoria | Custo estimado |
|---|---:|
| Hardware e eletrônica | R$ 337,00 |
| Estrutura física da bomba | R$ 100,00 |
| Cenário e ambientação | R$ 76,00 |
| Software e ferramentas | R$ 0,00 |
| **TOTAL ESTIMADO** | **R$ 513,00** |

### Total Costs with breakdown

O projeto acadêmico prioriza a utilização de ferramentas e recursos disponíveis pela equipe, mas pensando na possibilidade em que teria que comprar tudo:

O custo estimado para a construção do protótipo completo fica aproximadamente **R$ 513,00**, considerando a aquisição dos componentes eletrônicos, construção da bomba física e preparação do cenário de apresentação.

## Influences (Brief)

### Keep Talking and Nobody Explodes

- **Tipo:** Jogo eletrônico.
- É a principal referência de gameplay do projeto, em que se tem a estrutura de dois jogadores com informações diferentes, no qual um jogador opera o dispositivo enquanto o outro consulta um manual e fornece instruções, serve como base para a experiência cooperativa do Bomb.exe.

### Bombanana

- **Tipo:** Jogo eletrônico.
- Influencia a temática de desarme de dispositivos explosivos e a utilização de diferentes mecanismos para compor a experiência de jogo.

### Ponto Cego

- **Tipo:** Série de televisão.
- É uma série policial com episódios relacionado a desarme de bombas no mesmo estilo.

### Matrix

- **Tipo:** Filme.
- Influencia a ambientação futurista e tecnológica do universo, especialmente a utilização de interfaces digitais, sistemas computacionais e elementos visuais associados à tecnologia.

### Mr. Robot

- **Tipo:** Série de televisão.
- Influencia a estética de sistemas operacionais, terminais, interfaces computacionais e a representação de tecnologia como parte importante da narrativa.

## The elevator Pitch

**Bomb.exe é um jogo cooperativo para dois jogadores em que um agente opera uma bomba física enquanto seu parceiro consulta o sistema de desarme da ANS(Agência Nacional de Segurança) para interpretar protocolos e guiá-lo através de cinco módulos antes que o tempo acabe.**

## Project Description (Brief)

Bomb.exe é um jogo cooperativo para dois jogadores ambientado no ano de 2149, que se passa durante um grande evento público realizado em uma escola, onde um dispositivo explosivo de origem desconhecida é localizado e Sem tempo suficiente para evacuar o local, uma equipe especializada da Agência Nacional de Segurança é enviada para neutralizar a ameaça.

Cada jogador assume uma função diferente, o Especialista em Desarme de Explosivos (EDE) possui acesso direto ao dispositivo, enquanto o Especialista em Inteligência Tática (EIT) utiliza o Terminal Tático da ANS para consultar os protocolos necessários para o desarme.

## Project Description (Detailed)

A experiência é baseada na comunicação entre o Especialista em Desarme de Explosivos, que consegue visualizar e operar os componentes físicos do dispositivo e o Especialista em Inteligência Tática, que possui acesso aos protocolos e diagramas da ANS, dando suporte ao EDE. Nenhum dos jogadores possui sozinho todas as informações necessárias para concluir a missão.

O dispositivo explosivo é composto por cinco módulos independentes, cada um apresenta um mecanismo diferente e exige que os jogadores interpretem corretamente as informações presentes no dispositivo e no manual.

Para aumentar a rejogabilidade, diversos elementos dos módulos são determinados aleatoriamente no início de cada partida, fazendo com que os jogadores precisem interpretar as informações novamente a cada missão, evitando que uma sequência fixa possa ser simplesmente memorizada.

A missão possui duração máxima de cinco minutos e um sistema de falhas compartilhado. Cada solução incorreta gera uma falha e ao atingir três falhas, o dispositivo é imediatamente detonado. A partida termina quando os cinco módulos são desarmados ou quando o tempo chega a zero.

# What sets this project apart?

- **Cooperação assimétrica:** cada jogador possui informações e responsabilidades diferentes.
- **Interação entre software e hardware:** a experiência utiliza um dispositivo físico representando a bomba junto ao sistema operacional do EIT.
- **Rejogabilidade:** elementos dos módulos são gerados aleatoriamente a cada partida.
- **Pressão constante:** o limite de cinco minutos, junto dos efeitos sonoros e do sistema de três falhas tornam a comunicação e a tomada de decisão essenciais.
- **Universo próprio:** o jogo apresenta a ANS, seus agentes, protocolos e o sistema ANS-SECURE OS como elementos de uma mesma narrativa.
- **Experiência para dois jogadores:** o jogo é projetado para exigir a participação ativa dos dois jogadores.

## Core Gameplay Mechanics (Detailed)

### Comunicação e cooperação assimétrica

#### Details

A mecânica central de Bomb.exe é a comunicação entre o EDE e o EIT, onde os dois jogadores possuem acesso a informações diferentes e precisam compartilhar essas informações verbalmente para resolver os módulos.

O EDE possui acesso visual ao dispositivo e aos seus componentes e o EIT possui acesso aos protocolos de desarme.

#### How it works

O EDE descreve ao EIT as informações apresentadas no módulo, e o EIT interpreta essas informações utilizando o manual e informa ao EDE quais ações devem ser realizadas. A comunicação precisa ser precisa, pois informações incorretas podem levar a uma solução errada e gerar uma falha.

### Desarme dos cinco módulos

#### Details

A bomba é composta por cinco módulos independentes, cada um utilizando uma lógica de resolução diferente:

1. Chave de Inicialização.
2. Ajuste de Sintonização.
3. Bússola de LEDs.
4. Fios Conectados.
5. Labirinto.

#### How it works

Os jogadores precisam resolver os cinco módulos antes do término do cronômetro, em que cada módulo possui um procedimento específico descrito no manual do EIT.

> **OBS:** Um módulo é considerado concluído quando seu respectivo indicador de desarme é ativado.

### Informações e elementos aleatórios

#### Details

Os módulos possuem elementos que são determinados aleatoriamente a cada partida, como números de série, frequências, configurações de LEDs, fios e labirintos.

#### How it works

No início de cada partida, os elementos necessários para os módulos são gerados, fazendo com que os jogadores devam analisar a configuração atual e aplicar as regras correspondentes do manual. Impedindo assim que uma solução única seja reutilizada em todas as partidas.

### Limite de tempo e sistema de falhas

#### Details

A missão possui um cronômetro de cinco minutos e um limite de três falhas.

#### How it works

O cronômetro começa no início da missão e continua durante o processo de desarme. Quando uma solução incorreta é executada, uma falha é registrada.

Ao atingir três falhas, a bomba é detonada imediatamente e caso o cronômetro chegue a zero antes da conclusão dos cinco módulos, a missão também é encerrada.

# Story and Gameplay

## Story (Brief)

No ano de 2149, um dispositivo explosivo de tecnologia desconhecida é localizado em uma escola durante um grande evento de jogos aberto ao público e a evacuação do local não é considerada viável devido ao tempo limitado.

A Agência Nacional de Segurança envia sua melhor equipe para neutralizar a ameaça, um agente opera diretamente o dispositivo enquanto o outro utiliza o sistema de inteligência da ANS para interpretar os protocolos e orientar o desarme.

## Story (Detailed)

A história de Bomb.exe acontece em NeoCity, no ano de 2149, em uma sociedade altamente dependente de tecnologia e sistemas computacionais. Durante um grande evento de jogos realizado em uma escola, um dispositivo explosivo de origem desconhecida é encontrado no local.

A situação apresenta um problema crítico: o local está ocupado por um grande número de pessoas e não existe tempo suficiente para realizar uma evacuação completa antes de uma possível detonação.

Após a confirmação da ameaça, a Agência Nacional de Segurança (ANS) envia uma equipe especializada para realizar a neutralização do dispositivo.

A operação é dividida entre dois agentes: O Especialista em Desarme de Explosivos (EDE),que consegue observar os módulos, manipular seus componentes e executar as ações necessárias para o desarme, sendo responsável pela interação direta com a bomba.

O segundo agente é o Especialista em Inteligência Tática (EIT), que permanece com acesso ao sistema operacional especial da ANS(ANS-SECURE OS), ele contém os protocolos, regras e diagramas necessários para interpretar os diferentes mecanismos da bomba.

Como os agentes possuem informações diferentes, a comunicação entre eles é essencial. O EDE deve descrever corretamente o dispositivo ao EIT, enquanto o EIT deve interpretar essas informações e transmitir instruções precisas para o operador.

A missão termina quando os cinco módulos são neutralizados, quando o tempo se esgota ou quando ocorrem três falhas, provocando a detonação imediata do dispositivo.

## Gameplay (Brief)

O EDE vê e opera a bomba, O EIT consulta o manual e orienta o EDE. Os jogadores devem identificar, interpretar e resolver cinco módulos diferentes enquanto evitam três falhas.

## Gameplay (Detailed)

No início da partida, a bomba é configurada com diferentes elementos gerados aleatoriamente, o dispositivo apresenta cinco módulos que precisam ser resolvidos.

### Módulo 1 - Chave de Inicialização

A bomba apresenta um número de série gerado aleatoriamente, o EDE informa o número ao EIT e ele utiliza as regras do protocolo para interpretar o número de série e determinar a senha necessária para desbloquear o módulo.

### Módulo 2 - Ajuste de Sintonização

O módulo começa com um ruido grande.

O EDE deve operar o potenciômetro e ajustar a frequência apresentada até atingir o valor correto e sintonizar de maneira adequada para desarmar o módulo.

### Módulo 3 - Bússola de LEDs

O módulo apresenta seis LEDs em diferentes estados e um knob com quatro posições.

O EDE descreve ao EIT a configuração dos LEDs, dessa forma o EIT consulta o protocolo para determinar a orientação correta do knob e informa a posição ao EDE. Assim, o EDE ajusta o knob para a posição indicada e confirma a operação pressionando o botão

### Módulo 4 - Fios Conectados

O módulo apresenta entre três a cinco fios.

O EDE informa ao EIT as características dos fios e o número de série da bomba, assim o EIT utiliza as regras do protocolo para identificar qual fio deve ser cortado.

### Módulo 5 - Labirinto

O módulo apresenta um labirinto selecionado aleatoriamente.

O EDE informa ao EIT a posição dos dois objetivos circulados apresentados no dispositivo. O EIT identifica, no banco de diagramas do manual, o labirinto correspondente.

Depois de identificar o diagrama correto, o EDE informa a posição inicial do cursor e a posição do objetivo e o EIT utiliza o diagrama para indicar os movimentos necessários até o objetivo.

As paredes do labirinto não são visíveis para o EDE, dessa maneira cada colisão com uma parede conta como uma falha.

### Condições de partida

- **Vitória:** os cinco módulos são desarmados antes do fim do cronômetro.
- **Derrota por tempo:** o cronômetro chega a zero.
- **Derrota por falhas:** três falhas são acumuladas.
- **Falha individual:** uma solução incorreta é executada ou ocorre uma colisão que resulte em erro.

# Assets Needed

## 2D

- Interface do ANS-SECURE OS.
- Interface do terminal de inteligência.
- Elementos gráficos dos módulos.
- Ícones e elementos do sistema.
- Diagramas dos labirintos.
- Diagramas e tabelas dos protocolos.
- Efeitos visuais de terminal, como ruído e glitch.

## Environmental Art Lists

- Dispositivo Explosivo Improvisado.
- Estrutura física dos cinco módulos.
- Componentes eletrônicos.
- Potenciômetro.
- Knob.
- LEDs.
- Fios.

## Sound


### Sound List - Bomb

- Ativação do dispositivo.
- Registro de falha.
- Alarme de detonação.
- Detonação.

### Sound List - Gameplay

- Ruido ou som de frequência sintonizada.

## Code

### Core Systems

- Gerenciamento da partida.
- Cronômetro de cinco minutos.
- Sistema de login.
- Sistema de crédito para os jogadores.
- Sistema de falhas.
- Sistema de vitória e derrota.
- Gerenciamento dos cinco módulos.
- Geração aleatória dos elementos dos módulos.

### Terminal / ANS-SECURE OS

- Sistema de inicialização do terminal.
- Simulação de boot.
- Sistema de login.
- Sistema de leitura das instruções.
- Navegação pelos protocolos.
- Interface do EIT.

### Bomb Modules

- Script da Chave de Inicialização.
- Script do Ajuste de Sintonização.
- Script da Bússola de LEDs.
- Script dos Fios Conectados.
- Script do Labirinto.

### Interface

- Sistema de LEDs de status.
- Indicadores de falha.
- Cronômetro.

## Animation

### Environment Animations

- Movimento do cursor no labirinto.

# Schedule

## Planejamento e prototipação

- **Time Scale**
  - Definição do conceito e universo.
  - Definição dos cinco módulos.
  - Definição das regras.
  - Prototipação das principais mecânicas.
  - Definição da arquitetura do projeto.

## Desenvolvimento dos módulos

- **Time Scale**
  - Implementação da Chave de Inicialização.
  - Implementação do Ajuste de Sintonização.
  - Implementação da Bússola de LEDs.
  - Implementação dos Fios Conectados.
  - Implementação do Labirinto.
  - Implementação da geração aleatória.
  - Integração dos módulos com o sistema de falhas.

## Desenvolvimento da interface e terminal

- **Time Scale**
  - Desenvolvimento do ANS-SECURE OS.
  - Implementação do sistema de login.
  - Implementação do boot.
  - Implementação do terminal.
  - Desenvolvimento dos protocolos.
  - Desenvolvimento dos diagramas.

## Integração, testes e apresentação

- **Time Scale**
  - Integração dos sistemas.
  - Testes individuais dos módulos.
  - Testes completos de partidas.
  - Testes de geração aleatória.
  - Testes do sistema de falhas.
  - Testes de tempo.
  - Correção de bugs.
  - Ajustes de interface e feedback visual.
  - Preparação da versão final para apresentação.
