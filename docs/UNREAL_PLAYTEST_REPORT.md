# Condomínio 13 — Vertical Slice do Bunker

## Entrega

- Engine: Unreal Engine 5.8.3
- Plataforma: macOS 14 ou superior, Apple Silicon arm64
- Aplicativo: `builds/Mac/Condominio13-VerticalSlice.app`
- Configuração: Development, assinada localmente
- Tamanho: aproximadamente 832 MB
- Mapa inicial: `/Game/Bunker/Lvl_Bunker`

## Conteúdo desta versão

- Bunker B1 navegável preservado, com arquitetura real, colisão complexa, corredores, portas, escadas e ambientes conectados.
- Tratamento B2 inicial inspirado em instalações escandinavas de defesa civil: concreto modular, aço escuro, faixas de segurança, luz âmbar nas áreas sociais e luz fria nas áreas técnicas.
- Dormitório estilizado com quatro camas funcionais, colchões, travesseiros e luzes individuais.
- Seis recursos coletáveis: água, comida, kit médico, baterias e ferramenta.
- Minigame de dardos em rodadas de três arremessos.
- Rádio com pista narrativa, gerador alternável e painel de situação do bunker.
- Primeira área externa conectada: Mercado Aurora, estacionamento, rua, clínica selada e borda da floresta.
- Mercado com vinte módulos de prateleira, quatro caixas e iluminação própria.

## Controles e interações

- `W A S D`: caminhar
- Mouse: olhar
- `Espaço`: pular
- `E`: interagir com o objeto mirado
- `F`: levantar da cama
- `Esc` ou `⌘Q`: sair

Ao mirar em um objeto utilizável a até 3,5 metros, o jogo mostra sua ação. Recursos coletados somem do cenário e entram na mochila local. A cama imobiliza o personagem até `F`. O alvo de dardos soma três jogadas e encerra a rodada.

## Perfil MacBook

- Resolução inicial: 1280 × 720 em janela.
- Limite de 45 FPS com VSync e resolução interna em 70%.
- Sombras virtuais, motion blur, bloom, oclusão de ambiente, profundidade de campo, reflexos em tela e névoa volumétrica desativados.
- Luzes adicionais do exterior não projetam sombras, reduzindo o custo no MacBook.
- Distância de visão em 65%, materiais no nível baixo e pool de texturas limitado a 512 MB.
- Sensibilidade horizontal e vertical em 0,35; suavização do mouse desativada.

## Validação

- Mapa: 184 atores, 14 objetos interativos e 95 elementos externos.
- Iluminação: 27 luzes; contraste do dormitório e leitura do mercado conferidos no executável.
- Unreal Map Check: 0 erros e 0 avisos.
- Cook e empacotamento: concluídos com 0 erros e 0 avisos.
- Aplicativo: binário arm64, assinatura válida e contêineres `.pak`, `.ucas` e `.utoc` presentes.
- Capturas: `screenshots/runtime/vertical_slice_bedroom.png` e `screenshots/runtime/vertical_slice_market_lit.png`.

## Limites atuais

Esta entrega é a primeira vertical slice jogável. As interações funcionam localmente para um jogador; a autoridade de servidor e a sincronização completa para quatro jogadores ainda precisam ser implementadas. Os sistemas completos de fome, sede, saúde mental, energia, save/load, inimigos, combate, áudio final, animação de deitar e arte final também permanecem para as próximas etapas. A clínica está representada como objetivo externo selado e ainda não possui interior jogável.
