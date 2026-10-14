# Inspeção B1 — Condomínio 13

Abra `blender/Bunker_Blockout_v001.blend` no Blender 5.2.2.

## Primeira pessoa com colisão simplificada
1. Na área Scripting, selecione o texto `walk_bunker.py` já incluído no arquivo e clique Run Script.
2. Coloque o cursor sobre uma vista 3D. Pressione F3 e procure **B1 Navegar**.
3. WASD move, mouse olha, Shift reduz a velocidade, Esc sai.

O inspector usa cápsula aproximada de 0,60 m de diâmetro e 1,75 m de altura, olhos a 1,65 m e velocidade 1,4 m/s. Faz teste conservador de caixas expandidas e segue a altura dos degraus. Portas estão abertas e permanecem estáticas. Não é um jogo, controlador Unreal, simulação multiplayer ou teste de física da engine.

## Percurso de câmera
Selecione `CAM_Walkthrough` como câmera ativa e reproduza a linha do tempo. Há um percurso do patamar do estoque à convivência, passando pela escada e antecâmara. Para exploração livre sem colisão, o Walk Navigation nativo do Blender também está disponível (Shift + acento grave, conforme o mapa de teclado).

## Edição
As coleções separam arquitetura, portas, escadas, móveis, luzes, colisões e referências. Tetos podem ser ocultados para inspeção superior. As portas são filhos de objetos HINGE; gire esses objetos no eixo Z. Móveis são volumes de reserva de uso, não assets finais. As paredes usam peças de até 1 m com fechamentos dimensionais; pisos/tetos usam peças de 2 m com dados compartilhados.

## Reprodução
Execute o Blender com `--background --python scripts/create_bunker_blockout.py` a partir da pasta do projeto. `-- --no-render` reconstrói sem renderizar as cinco imagens. A cena é reconstruída integralmente: não execute sobre alterações manuais que deseja preservar sem salvá-las em outra versão. O arquivo .blend1 preserva a última gravação, não um histórico completo.

Execute `--background --python scripts/validate_bunker.py` para reabrir o arquivo e repetir os testes. Logs e JSON de resultados estão em logs/.
