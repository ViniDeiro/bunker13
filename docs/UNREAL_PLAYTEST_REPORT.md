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

## Passe de design interno

### Superfícies texturizadas

Seis conjuntos originais de materiais PBR substituem as cores lisas: concreto poroso com juntas, metal pintado e oxidado, madeira, trama de tecido, piso industrial e aço escovado. Cada conjunto contém mapas BaseColor, Normal e ORM (oclusão, rugosidade e metalicidade), com resolução de 512px. São aplicados a 16 materiais por projeção triplanar em escala mundial, evitando esticamento nas primitivas e na arquitetura importada. As fontes ficam em `assets/textures`, com geração reproduzível em `scripts/create_surface_textures.py` e importação em `scripts/apply_surface_materials.py`.

O passe de textura não encerra a arte: silhuetas, bordas, sinalização, narrativa ambiental e iluminação ainda exigem revisão. O estado completo do restante do jogo está em `docs/PRODUCTION_STATUS.md`.

- Corredor principal com nervuras estruturais, dutos retangulares, tubulação de água e energia, juntas técnicas e faixa de orientação no piso.
- Dormitório com quatro conjuntos de cama, cabeceiras, cobertores, travesseiros, sapatos, luminárias pessoais e quatro armários numerados visualmente.
- Sala de convivência com mesa comunitária para seis lugares, cadeiras construídas, sofá com almofadas, tapete, televisão antiga e mural de avisos.
- Cozinha com bancada contínua, cinco módulos inferiores, três armários superiores, pia, fogão com quatro queimadores, geladeira e mesa de refeição.
- Enfermaria com maca construída em camadas, apoio de cabeça, carrinho com rodas, armário médico identificado e monitor iluminado.
- Rádio e comando com banco de três telas, controles, mesa de mapas e arquivo de expedições.
- Oficina com bancada reforçada, painel de ferramentas, morsa e caixas de armazenamento.
- Sala do gerador com três módulos mecânicos, grelhas, escapes, tambores de combustível e piso de advertência.
- Sanitário com divisória e louças; antecâmara com banco, armários de EPI e arco de descontaminação.
- Materiais próprios para aço, concreto, madeira, tecido, borracha, porcelana, telas, vermelho de emergência e verde utilitário.

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

- Mapa: 14 objetos interativos, 95 elementos externos e um passe adicional de mobiliário e infraestrutura em nove ambientes internos.
- Iluminação: 27 luzes; contraste do dormitório e leitura do mercado conferidos no executável.
- Unreal Map Check: 0 erros e 0 avisos.
- Cook e empacotamento: concluídos com 0 erros e 0 avisos.
- Aplicativo: binário arm64, assinatura válida e contêineres `.pak`, `.ucas` e `.utoc` presentes.
- Capturas: `screenshots/runtime/vertical_slice_bedroom.png` e `screenshots/runtime/vertical_slice_market_lit.png`.

## Limites atuais

Esta entrega é a primeira vertical slice jogável. As interações funcionam localmente para um jogador; a autoridade de servidor e a sincronização completa para quatro jogadores ainda precisam ser implementadas. Os sistemas completos de fome, sede, saúde mental, energia, save/load, inimigos, combate, áudio final, animação de deitar e arte final também permanecem para as próximas etapas. A clínica está representada como objetivo externo selado e ainda não possui interior jogável.
