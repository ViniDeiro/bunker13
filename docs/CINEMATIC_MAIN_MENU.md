# Menu cinematográfico — ÚLTIMO ABRIGO

## Pedido e escopo

A referência fornecida foi preservada em `references/main_menu_reference.png` e usada como guia de composição, não importada para o cenário como imagem de fundo. O trabalho desta etapa limita-se ao mapa `/Game/Bunker/MainMenu/L_MainMenu`, sua interface e a transição para o fluxo solo existente.

A composição tem mesa/radio/documentos à esquerda, corredor modular com piso, teto e tubulações reais ao centro e porta blindada B-13, luz vermelha, caixa e máscara à direita. A máscara, a luminária de mesa, os tubos com flanges e o rotor foram modelados no Blender e exportados como malhas. O resto reaproveita geometria e PBR já existentes no próprio projeto. Não foram baixados assets de terceiros; não foi aplicado o print como cenário.

Fonte nova: `blender/Menu_Respirator_v001.blend` contém os props novos editáveis. Cena montada na Unreal e reproduzível por `scripts/install_cinematic_menu.py`. A porta utiliza os mapas existentes do Painter, com uma variante grafite exclusiva do menu, preservando roughness e normal originais.

## Sistemas separados

- **Cena:** meshes e luzes no mapa independente, sem alterar os níveis da partida.
- **Interface:** `UCinematicMenuWidget`, árvore UMG real, não o HUD Canvas anterior. Widgets fixos na tela, com estados de botão, transição suave de escala no hover e som mecânico de interface.
- **Câmera:** perspectiva a 48°, referência inicial guardada no controlador, interpolação a 2,5. Translação máxima de 6 cm no eixo lateral e 4 cm no vertical (norma máxima de aproximadamente 7,2 cm), yaw de 1,2° e pitch de 0,7°. O mouse movimenta a câmera, nunca os botões.
- **Abertura:** bloqueio de cliques adicionais, opacidade da interface diminuindo em 0,65 s, avanço para a porta em 2,8 s e fade para preto antes da viagem de mapa. A camada UMG é removida na viagem. O mapa da partida recebe a opção `C13MenuStart` e inicia o fluxo normal de coleta após carregar.
- **Ambiente:** luz vermelha com pulso lento, rotor e partículas 3D discretas, zumbido original em loop e ruído sintético ocasional de rádio. Partículas são geometria pequena de baixo custo em posições do mundo; não são simulação volumétrica de fumaça.
- **Acessibilidade:** painel UMG permite desligar parallax e pulso/rotor/partículas separadamente. As opções valem para esta sessão de menu.
- **Ações:** Iniciar usa a partida solo real. Sair fecha a prévia. Grupo e Diário estão visivelmente indisponíveis; não há matchmaking ou diário persistente fingidos.

A variante do menu não muda inventários, GUIDs ou checkpoints. O lançador de revisão usa o modo sem save já existente. A integração de início automático só é ativada pela opção do menu.

## Como abrir

`tools/launchers/Ver-Menu-Cinematico.command`, com a Unreal instalada neste Mac. O atalho anterior da partida foi preservado para não substituir a experiência anterior antes da revisão visual. O mapa e os assets novos ainda precisam ser incluídos explicitamente no cook antes de gerar um executável independente.

## Comparação com a referência e limites artísticos

A avaliação verificou a distribuição mesa/corredor/porta, o contraste âmbar/grafite e a interface central. As primeiras capturas mostraram a mesa excessivamente cortada, a face errada da porta, cor verde demais, tubos retangulares, pouca leitura do fundo e título pequeno. Corrigidos em passes sucessivos.

Ainda há diferenças importantes: a tipografia é a fonte Bold disponível na engine, não o lettering industrial envelhecido da referência; os botões e a máscara têm acabamento mais simples; a densidade e a história dos papéis/cartazes ainda são menores. A superfície do cenário mantém um aspecto mais limpo que o print. Não considerar a fidelidade ou qualidade comercial aprovadas automaticamente porque os testes funcionais passaram. O cenário usa iluminação de baixo custo para este Mac; o resultado precisa da avaliação visual do criador.

A malha tem profundidade de verdade, mas não é uma sala navegável de gameplay: colisões de cenografia estão desligadas no mapa de menu. Não há mudança de nome definitivo do jogo nem expansão de outros ambientes.

## Validação funcional e renderização

O roteiro testa os eventos UMG dos botões de início/saída e as funções de configurações. Ele não substitui um teste humano com mouse. Grupo e Diário permanecem desabilitados. As capturas foram produzidas com widgets incluídos, não montadas externamente.

Full HD: 30,00 FPS, p95 33,35 ms, 150 amostras. 1440p final: 29,42 FPS, p95 36,79 ms, 147 amostras. Perfil do menu: escala de renderização 85%, sombras 2, resolução máxima de sombras 512, AO 1 e limite 30. Amostras curtas de cinco segundos com um processo renderizado; não comprovam uso prolongado, pacote distribuído ou outro computador.

O ensaio do movimento da câmera verifica deslocamento observado maior que 0,1 cm e menor que 8 cm. A geometria é inspecionável no mapa, com dezenas de atores em coordenadas diferentes. O painel de acessibilidade é aberto, as duas opções desligadas, o estado conferido e as opções restauradas. O início de partida via evento do botão produz a viagem real e a fase de coleta 1; a rotina de saída é executada em outro processo.

Gravar screenshots do movimento reduz significativamente o FPS (aproximadamente 17 FPS na rodada inicial de gravação), por isso essa medição não deve ser confundida com o perfil sem gravação. O vídeo é uma sequência de capturas nativas solicitadas a 8 FPS com timestamps, sem áudio ou interpolação inventada. O som ambiente é executado pelo jogo; não foi certificado por uma captura sonora sincronizada.

Comparação lado a lado: `output/menu_review/comparison.html`. Ainda falta validação humana do mouse, teclas de navegação, experiência sonora e aprovação artística. Não foi criado um executável independente nem alterado o mapa padrão do projeto.

## Arquivos e preservação

Novos: `CinematicMenu.h/.cpp`, `Content/Bunker/MainMenu/`, fonte Blender dos props, exports FBX, sons sintéticos originais, instalador e runners do menu, vídeo/capturas e lançador de revisão. Alterados: dependências UMG/Slate no Build.cs, integração de entrada automática em BunkerNetwork.cpp e provas de carregamento no BunkerRoundValidation.cpp. Os restantes arquivos já modificados no checkout pertencem às etapas anteriores desta conversa; não foram descartados ou resetados.

Apenas a geometria necessária à tela foi construída; não houve produção de novos ambientes de gameplay. Os assets de parede, piso, mesa, rádio, caneca, documentos e porta vêm das fontes do próprio projeto. Fonte de interface Roboto disponível com a engine; não foi comprado ou baixado um pacote de assets. O zumbido e o ruído de rádio foram gerados sinteticamente, sem voz gravada ou mídia de terceiros.

O aviso de mobilidade do rotor observado numa gravação intermediária foi corrigido para Movable antes da rodada final. A sequência final também corrige o reinício indevido do fade e remove o widget antigo antes de trocar de mapa.


## Evidência final

As rodadas finais em 720p (com gravação), 1080p e 1440p passaram em parallax, configurações, ações desabilitadas, fade/avanço, viagem e início da coleta; sem commits de campanha. O ensaio separado de saída também passou. A fonte Blender foi reaberta com quatro objetos mesh e UVs. A gravação final tem 56 capturas reais em 9,68 s e ficou silenciosa. O arquivo de validação é `docs/validation/cinematic_main_menu.json`; ele distingue aprovação funcional de aprovação visual, que permanece pendente.

Nesta rodada final não houve aviso de mobilidade nos logs. O registro intermediário do rotor parado foi preservado em `logs/cinematic_rotor_static_issue/`. Antes do passe final também foram corrigidos erros de compilação no nome de componente, strings de texto e iteradores, além da transformação da API Python. Esses erros não constituíram versões entregues.
