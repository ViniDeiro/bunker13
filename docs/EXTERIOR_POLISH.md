# Expedição — primeiro passe visual da área de carga

O estacionamento existente agora tem três baias de madeira e aço, bordas de segurança, marcas de aproximação no patamar entre mercado e estacionamento, placa de carga e luz fria de apoio. Os seis recursos continuam nos mesmos pontos, com as mesmas chaves de persistência. A decoração é criada localmente em cada mundo de expedição; não é salva, não tem colisão e não adiciona itens. O gerador não controla a luz externa.

A revisão concentrou-se no ponto de coleta e na sua aproximação. O interior do mercado e a antecâmara continuam com a arte existente; fachada, piso externo, profundidade do fundo e acabamento geral ainda precisam de revisão. O mapa não foi expandido. Esta etapa não fornece uma atualização para o executável 0.4.2.

O atalho `tools/launchers/Jogar-Partida-Atual.command` agora inicia uma sessão normal da expedição, sem ler nem gravar checkpoints. Detectamos que a opção anterior impedia a partida de sair da preparação com **R**; a opção nova separa a prontidão da partida da gravação em disco.

## Validação

Primeiro passe: ciclo integral em uma instância renderizada da Unreal, com coleta inicial, saída e retorno a pé, exposição, coleta de dois itens e consumo dos mesmos GUIDs para recuperar o gerador. Medição inicial da crise: 29,94 FPS, p95 33,49 ms, 480 amostras, janela 960 × 540, escala 70%, sombras e AO desligados, limite 30. Não é medição da rota completa.

A revisão da captura mostrou que o contraste da placa não era suficiente. A cor da inscrição foi ajustada e recapturada num ensaio curto da opção sem save. Esse ensaio verifica o comando R, a criação das três baias e a ausência de gravação. A captura curta reposiciona o jogador; o teste contínuo anterior valida a caminhada. Não houve reteste com clientes nesta revisão.

## Segundo passe — Mercado Aurora e pátio

- Entrada: moldura visual verde e aço, letreiro Mercado Aurora e sinalização de saída para carga. Oculta apenas a malha da placa laranja antiga, preservando sua colisão original. Dois pontos de preenchimento sem sombras dão leitura ao trecho dos caixas.
- Estacionamento: quatro vagas sugeridas por seis faixas e quatro batentes cenográficos, além de uma divisória baixa com faixa de segurança e identificação do pátio. As peças são visuais, não obstáculos; permanecem atrás e nas laterais da rota jogável.
- A inspeção em jogo mostrou a primeira fachada com letreiros sobrepostos e caixas muito escuros. Corrigidos a sobreposição, o preenchimento e o enquadramento. Novas capturas em `screenshots/exterior_polish/market.png` e `parking.png`. A captura do teste curto reposiciona a câmera somente para mostrar a arte.
- Continua sendo um passe na chegada e na leitura do espaço. O miolo do mercado, materiais de piso, céu/horizonte e acabamento de toda a fachada ainda não estão em qualidade final. A prévia continua usando a Unreal instalada.

Validação do segundo passe: a rodada completa passou com saída e retorno a pé, combustível e peças consumidos com os IDs recolhidos e o gerador religado. Um host renderizado, 480 amostras no começo da crise: 29,99 FPS, p95 33,42 ms (limite 30). Depois do ensaio contínuo, a correção somente visual da placa e das luzes foi compilada e recapturada na Unreal; início sem save também conferido. Não houve reteste em rede nem novo pacote.

## Caixas e leitura da circulação

Acabamento dos dois caixas junto à saída, identificação 03/04 e continuidade da faixa de carga do lado interno. Sem colisões novas. A prévia renderizada confirmou carregamento, captura e início com R sem escrita de campanha. A auditoria das portas no próprio mapa da expedição confirmou 13 de 13 passagens abertas livres para a cápsula do jogador e bloqueio do movimento na presença de jogador no arco da folha ensaiada. Os giros das portas não foram alterados. Evidência: `docs/validation/door_clearance_current_round.json`.
