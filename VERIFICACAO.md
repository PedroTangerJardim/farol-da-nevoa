# Verificação do projeto

Verificado em 30/10/2026, com Python 3.12.14, PgZero 1.2.1 e a dependência
interna Pygame 2.6.1. A janela real também foi aberta e inspecionada.

## Requisitos técnicos verificados

| Requisito | Implementação |
| --- | --- |
| Bibliotecas permitidas | `import pgzrun` e `from pygame import Rect`; nenhuma outra importação no jogo |
| Gênero permitido | Platformer de visão lateral com gravidade e saltos |
| Menu clicável | Começar, ligar/desligar música e sons, saída |
| Música e efeitos | Uma trilha OGG em loop; cinco efeitos WAV |
| Vários inimigos perigosos | Quatro sentinelas; contato retira uma vida |
| Territórios de patrulha | Limites próprios por sentinela; pausa e inversão nas extremidades |
| Classes próprias | `AnimatedCharacter`, `Player`, `Sentinel` |
| Animação parado e andando | Quatro quadros por estado e direção, para ambos os personagens |
| Nomes em inglês e PEP8 | Verificação com pycodestyle, sem ocorrências |
| Mecânica coerente | Coleta de cinco cristais, farol bloqueado antes disso, três vidas, derrota e reinício |

## Resultados

Um programa de validação externo ao projeto executou **81 asserções** com
os objetos reais do PgZero. Passaram as verificações de:

- Importações permitidas e carregamento de todos os efeitos e da música.
- Pausa e retomada real da música, inclusive pelos botões e pela tecla M.
- Clique esquerdo, clique direito ignorado, início e saída.
- Imagens distintas nos ciclos de animação parado/andando e esquerda/direita.
- Apoio estável no chão, gravidade, pouso e bloqueio de salto no ar.
- Saltos entre os trechos da rota e um salto entre ilhas do chão.
- Movimento e animação das quatro patrulhas, incluindo pausas e limites.
- Dano por contato, proteção temporária, queda, derrota e reinício.
- Coleta dos cinco cristais e bloqueio do farol enquanto faltam cristais.
- Vitória, retorno ao menu e dez segundos de jogo parado sem falha.

Uma segunda verificação completou a partida **sem teletransportar o herói,
retirar inimigos ou alterar a cena**. Foram usados os controles normais de
andar e pular, com atualizações de 1/120 de segundo. Resultado: cinco cristais,
três vidas e vitória após aproximadamente **7,2 segundos de simulação**.
Isso comprova uma rota possível com as patrulhas ativas; não é uma estimativa
de duração para quem joga pela primeira vez.

As telas de menu, partida, derrota e vitória foram renderizadas e inspecionadas.
As ferramentas de criação e validação ficaram fora da pasta entregue; não
adicionam bibliotecas ou imports ao jogo.
