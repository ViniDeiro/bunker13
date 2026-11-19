# Primeiro playtest do Condomínio 13 — 17/11/2026

- **Versão atual do projeto (Mac com Unreal instalada):** `tools/launchers/Jogar-Partida-Atual.command`. Abre diretamente a partida, incluindo radiação e a orientação contextual. Cada abertura é uma sessão nova; o atalho de avaliação não grava a campanha.
- **Executável independente já disponível:** `builds/Mac/Jogar-Expedicao.command` (0.4.2). Tem o ciclo de expedição e recuperação, mas ainda não inclui a radiação nem a orientação nova.
- **Quarto clareado:** `tools/launchers/Ver-Quarto-Visual.command`. O quarto com quadro e duas camas segue como cena de avaliação separada; ele não aparece nessa rota da expedição.

## Uma partida para testar agora

1. Aperte **R** para iniciar a rodada. Use **WASD**, mouse e **E** para se mover, olhar e recolher. Você tem 90 s na partida normal para pegar suprimentos e descer ao abrigo.
2. Depois do fechamento, leia a orientação do dia no topo da tela. Confira o gerador e o sistema de água. Abasteça e faça manutenção com o gerador desligado. Quando tiver energia, acione o circuito de serviços para filtrar água.
3. Se faltar combustível ou peça, saia pela antecâmara. Feche uma folha antes de abrir a outra, espere a equalização e depois prossiga. Procure suprimentos no estacionamento. Se estiver retornando pelo lado de fora sem energia, aguarde a equalização e segure **E** na liberação manual.
4. Volte e use o que coletou no gerador. Na versão atual, confira se você nota a exposição no estacionamento e entende o custo de demorar. **I** abre a mochila; setas selecionam, **U** usa e **G** larga.

O playtest está disponível agora. O que falta para o próximo pacote é uma rodada humana do percurso, revisão de objetivos e balanceamento, uma versão Mac independente com a compilação atual e um teste dessa versão. O que falta para a partida cooperativa completa inclui proteção e tratamento contra exposição, inimigo/combate, morte permanente, comunicação limitada, eventos e fechamento de partida, além de validação com quatro pessoas. Não há estimativa confiável de lançamento sem essas verificações.

## Iluminação do quarto

Foram reforçadas as duas luzes de preenchimento já existentes, sem habilitar sombras nelas. As luminárias principais, a exposição e os materiais do quarto foram preservados. A comparação usa o mesmo enquadramento e perfil da Unreal. A bancada e as superfícies de circulação ficam mais legíveis sem trocar a paleta. Capturas: `screenshots/playtest_bright/before.png` e `screenshots/playtest_bright/after.png`.

O ensaio do quarto passou em descanso, recuperação de energia, transição da câmera, levantar e retornar à passagem. Medição curta de 596 quadros a 960 × 540, escala interna de 85%, limite de 30 FPS: média 29,79 FPS, p95 33,33 ms. Não é teste de sessão longa.

A conferência de integridade encontrou 448 de 449 assets iguais ao manifesto. A divergência é `painter/SM_Hero_BlastDoor.spp`, arquivo de autoria que não foi editado por este trabalho nem é usado em execução pela Unreal.

A rodada automatizada de 17/11 na Unreal passou em uma execução: coleta inicial, fechamento, saída a pé, coleta no estacionamento, retorno a pé e recuperação do gerador com os mesmos IDs de combustível e peças. Dose no retorno: 32,9830, estável no abrigo enquanto a saúde diminuía. A captura `screenshots/playtest_bright/objective.png` mostra a dica com tanque vazio. Uma instância local renderizada, janela 960 × 540, resolução interna 70%, limite 30: 30,00 FPS (p95 33,40 ms) durante as 480 amostras iniciais da crise; não é FPS da rota inteira. O ensaio cria uma crise reproduzível e grava apenas no checkpoint automatizado. O atalho de playtest abre uma sessão sem esse roteiro e sem gravação.

## Orientações que acompanham a mochila

Na fase de abrigo, o HUD usa o estado da infraestrutura e os itens do próprio jogador. Com galão ou peças em mãos no exterior, orienta o retorno em vez de continuar pedindo busca. No abrigo, distingue abastecer, fazer manutenção e acionar o interruptor. Com energia, indica circuito de serviços, bomba desligada, filtro gasto ou consumo de água quando aplicável. As orientações não alteram inventário, autorização do host ou salvamento.

A sessão manual começa com os estoques configurados de uma partida normal. O roteiro automatizado prepara tanque vazio e condição baixa para exercitar a expedição logo após o fechamento. Portanto, passar no teste comprova a sequência das ações, mas não que o ritmo de escassez de uma partida humana esteja pronto.

Revalidação: uma rodada contínua na Unreal passou, com saída e retorno a pé, consumo dos mesmos IDs e energia recuperada. A captura `screenshots/playtest_objectives/return_objective.png` confirma o objetivo de retorno após coletar galão e peças. Dentro do bunker a dose ficou em 32,9970, com a saúde caindo de 79,7005 para 73,4004 no intervalo medido. Uma instância, 29,98 FPS nas 480 amostras iniciais da crise, limite 30; não é medição do percurso inteiro ou de cooperação humana. Os estados alternativos do HUD de água e filtro foram implementados, mas não exercitados nessa rodada.

## HUD e coleta inicial no mercado

Saúde, comida, água e energia aparecem em cartões com ícone, cor, valor e barra proporcional. A dose aparece como cartão adicional quando há exposição. As três mesas de coleta foram convertidas em um expositor refrigerado aberto de luz fria e dois expositores de luz quente. Preservados os 12 atores existentes, suas chaves e seus pontos de coleta; não há geração ou reposição extra de itens. O expositor aberto não simula temperatura.

A Unreal confirmou 12 unidades no mapa e retirada da garrafa azul com E: o mesmo GUID entrou na mochila e a unidade saiu do expositor. A primeira tentativa de teste falhou por desalinhamento da câmera roteirizada; o ensaio corrigido passou, com captura em `screenshots/market_display_hud.png`. O ensaio não cobre todos os itens individualmente, outra máquina ou o pacote independente.

## Tela inicial

O atalho da prévia abre na tela Condomínio 13, com botão **Começar partida** e alternativa **Enter**. A tela só aparece na preparação para o host quando o atalho a ativa. O botão usa o início normal da rodada; ao iniciar a coleta, fecha o menu, esconde o cursor e devolve movimento e câmera. A arte foi desenhada diretamente na interface da Unreal, com corte esquemático do abrigo e layout proporcional ao tamanho da janela. Não é uma sala de convite nem matchmaking.

O teste renderizado `scripts/run_main_lobby_preview.py` confirmou o cursor sobre o botão, o clique pela entrada da Unreal, a entrada na fase de coleta e o retorno dos controles sem gravar a campanha. Captura: `screenshots/main_lobby.png`. O roteiro reduz a coleta para 35 segundos; a prévia manual segue a duração configurada da partida normal.
