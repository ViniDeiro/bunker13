# Bunker aberto — versão comparativa

29/10/2026 · Deiros Dev

## O que foi executado

Criada uma planta alternativa no Blender e integrada no mapa Unreal `Lvl_Bunker_OpenPlan`, com um aplicativo próprio. Convivência, cozinha, despensa, oficina, enfermaria e rádio passam a ocupar o mesmo salão. Dormitório, banheiro, antecâmara e gerador continuam fechados, conforme aprovação na conversa. O envelope continua aproximadamente 28 x 20 m: a amplitude vem da abertura, não de aumentar o mapa.

Foram removidos 151 objetos modulares de divisórias/molduras do derivado arquitetônico e os revestimentos decorativos que fechavam a convivência. Oito folhas interiores legadas foram ocultadas e tiveram a colisão desabilitada somente na alternativa. Seus atores, nomes e raízes continuam presentes. Não são portas invisíveis bloqueando circulação.

O alvo de dardos ganhou um suporte curto e independente, preservando o ponto de interação existente. Sua lógica anterior continua demonstrativa e aleatória. Mobiliário social, armário físico e recursos existentes foram preservados. O piso e o forro foram contínuos e a iluminação foi equalizada para evitar o contraste das antigas salas. Luminárias e pontos de apoio de baixo custo mantêm a leitura dos setores; isso não representa arte final de todos os setores. As folhas retiradas têm uma marca explícita que desativa visual e colisão também ao iniciar em rede.

## Como avaliar

Abrir `builds/Mac/Avaliar-Bunker-Aberto.command`. A avaliação inicia no salão e permite andar livremente. E abre a folha do armário e pega o objeto olhado; I/setas selecionam o item pessoal e X numa posição disponível guarda. A sessão não grava nem carrega a campanha. Uma água e uma comida existentes são movidas para a prateleira no modo de demonstração; não há criação de recursos para a campanha.

A versão anterior e seu lançador de convivência continuam disponíveis. O mapa original não foi substituído. O nome do mapa faz parte da assinatura dos checkpoints; por isso esta comparação não promete carregar saves antigos. Uma promoção futura exigirá migração explícita testada, mantendo GUIDs e conteúdos.

## Validação executada

Aplicativo Mac compilado, empacotado e com assinatura verificada. Teste solo renderizado: as seis zonas comuns são alcançáveis a partir do centro, em uma grade de 50 cm construída com cápsula real de raio 34 cm e meia-altura 96 cm. Cada aresta é conferida com sweep de colisão; também há verificação de piso. Isso valida rotas para uma cápsula, não conforto de quatro pessoas andando juntas. Quatro cápsulas simultâneas cabem sem contato na área central testada.

Teste com host e cliente renderizados: 12 verificações passaram, incluindo retirada/devolução com mesmo ID, disputa rejeitada, bloqueio da porta fechada, observação da ação e snapshots iguais nas duas conexões. Não houve dois humanos ou internet nesta rodada. Os testes históricos de reconexão de 22/10 não são apresentados como uma nova sessão humana.

FPS registrado: `phase=openplan samples=962 mean_ms=16.638 median_ms=16.557 p95_ms=17.510 fps=60.11`. Janela curta de aproximadamente 16 s, estática, 1280 x 720, Apple M2 / 24 GB. Configuração: `screen_pct=70.0 shadow_quality=0 max_fps=0.0 vsync=1`. Não é garantia para toda a partida ou para Windows. Capturas reais: `screenshots/reference_openplan_wide.png`, `reference_openplan_reverse.png`, `reference_openplan_hero.png`.

Fonte Blender reaberta em processo independente, conferindo geometria finita, existência das coleções, ausência das divisórias removidas e arquivo de exportação. Planta superior renderizada sem teto e sem dutos para não confundir elementos suspensos com paredes. Fora da convivência, a fonte usa proxies do blockout: não é um arquivo mestre de todos os móveis refinados da Unreal.

## Ainda falta nesta direção

Organizar melhor distâncias e pequenos grupos de móveis, reforçar orientação/sinalização e espalhar a linguagem visual aprovada pelas zonas agora abertas. A enfermaria precisa de privacidade visual por biombo parcial; a voz por proximidade ainda precisa ser implementada e testada, então não se declara privacidade acústica pronta. Esta entrega é a revisão espacial antes desse acabamento.

Permanecem os limites anteriores de animação procedural, áudio capturado parcialmente e inicialização intermitente do Mac sem correção confirmada. Não foram concluídos inimigos, combate, expedição, eventos, minijogo ou final apenas por abrir as divisórias.

## Próxima meta

MVP interno em **30/01/2027**, com férias de **04 a 15/01/2027**. Ver `docs/MVP_TARGET_JANUARY_2027.md`: prévia completa antes das férias, teste humano de quatro pessoas na volta e estabilização entre 25 e 30/01. A meta depende de equipe e Windows; não equivale a promessa de lançamento.

## Fontes

- `blender/Bunker_OpenPlan_v001.blend`
- `exports/Bunker_OpenPlanShell.fbx`
- `unreal/Condominio13/Content/Bunker/Lvl_Bunker_OpenPlan.umap`
- `builds/Mac/Condominio13-OpenPlan.app`
- `scripts/create_open_plan.py`, `install_open_plan.py`, `run_open_plan_validation.py`
- `logs/open_plan_*` e `logs/open_plan_delivery_manifest.json`
