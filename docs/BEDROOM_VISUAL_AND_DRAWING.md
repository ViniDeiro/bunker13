# Condomínio 13 — quarto com dois leitos e quadro

A prévia abre somente o quarto. Mapa da Unreal: `/Game/Bunker/BedroomVisual/Lvl_Bedroom_Study_Rest_Visual`. A cena original v003, os arquivos de autoria Blender e os materiais compartilhados continuam separados. O mapa novo é editável no Editor; o instalador Python documenta as decisões de montagem.

- O primeiro leito permanece no fundo. O segundo usa a mesma malha e o mesmo sistema de descanso, com orientação e câmera ajustadas à parede da entrada. A abertura de 1,20 m do quarto não recebeu geometria nova.
- As luminárias usam temperaturas distintas e raios menores. Dois apoios de luz local sem sombras recuperam detalhe da bancada e da entrada. A manta usa um verde azulado mais profundo, com resposta fosca e o normal de tecido existente.
- O quadro e a caneta têm geometria real e materiais separados. Olhe para o quadro a até 1,45 m e aperte **E**. Segure **mouse esquerdo** enquanto move a mira pela superfície, **R** limpa com a caneta em uso e a mira no quadro, e **E** devolve. Na cama, **E** deita e **F** levanta.
- Os traços são instâncias agrupadas com limite de 1.200 marcas. Soltar o botão ou perder contato encerra o segmento; pular rapidamente de um lado a outro não une os extremos. Somente a prévia local aceita desenho. O quadro não grava campanha, não replica rabiscos e não fornece um item de inventário. Ainda não há animação esquelética da mão segurando a caneta: a malha física acompanha a mira e encosta no quadro.

Prévia: `tools/launchers/Ver-Quarto-Visual.command`. Usa a Unreal instalada; ainda não é um executável distribuível.

## Evidência e limites

A comparação antes/depois foi capturada em jogo com o mesmo enquadramento, 960 × 540, escala interna 85%, sombras nível 2, resolução máxima de sombras 512 e limite de 30 FPS. Antes: 29,12 FPS (p95 de 41,65 ms), variante: 29,82 FPS (33,34 ms). O teste do segundo leito registrou 29,74 FPS (33,47 ms). Cada amostra do quarto tem cerca de 20 segundos; os valores não isolam um ganho de otimização.

O teste do quadro registrou 120 marcas, confirmação de interrupção do traço, limpeza e devolução; durante quatro segundos de desenho foram 29,99 FPS (p95 33,34 ms). O teste usa uma trajetória roteirizada e a mesma função de atualização que recebe comandos manuais. Não foi medido quadro cheio, sessão longa, controles em outra máquina ou desenho em multiplayer. Ambos os leitos foram testados separadamente, com recuperação de energia, chegada da câmera ao travesseiro, liberação do leito e retorno ao ponto de circulação; não houve ocupação simultânea. O armário foi preservado, mas o multiplayer do armário não foi repetido nesta variante.

Problemas detectados e corrigidos: excesso de sombra no primeiro estudo; montante atravessando a vista do quadro; aviso de material sem suporte a instâncias; caneta perpendicular demais à superfície. Antes da última rodada, houve um encerramento da janela de controle e outra rodada em que o foco não acertou a cama. As rodadas finais de comparação suprimem a entrada externa do mouse durante o roteiro. Os 449 assets da base e os hashes do mapa e fontes do v003 foram conferidos.

Capturas reais: `screenshots/bedroom_visual/before_overview.png`, `after_overview.png`, `drawing.png` e `bed02_rest.png`. Evidência estruturada em `docs/validation/bedroom_visual_and_drawing.json`. Próximas decisões do quarto: avaliação manual da pegada e dos controles, mão articulada, ocupação simultânea de camas e sincronização de desenho se ele fizer parte da sessão cooperativa.
