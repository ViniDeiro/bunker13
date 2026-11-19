# Quarto — continuidade de coleta e proximidade — 16/11/2026

## Marco e critérios antes da execução

Dependências: armário físico v002, apresentação cosmética local/remota, inventário/IDs do host e controle de visibilidade ao guardar. Critérios: item permanece no ponto da prateleira durante aproximação; mão e item se encontram antes do recolhimento; observador recebe a mesma trajetória; rejeição pelo host quando longe não altera posse/revisão; coleta/devolução próximas preservam o mesmo ID; regressões do armário original e medição de FPS.

## Alterações

A posição das mãos continua calculada pela curva existente. A posição do item é separada: ao pegar, fica no contato até 34% do gesto e só depois acompanha o recolhimento. A malha cosmética ocupa o lugar do recurso já transferido; não é um novo recurso e não recebe colisão/interação. Ao guardar, permanece o controle existente que oculta a prateleira até a soltura em 88%. A mesma função calcula a posição do item na visão local e nos observadores.

A transferência no quarto exige distância horizontal máxima de 110 cm do centro do jogador ao espaço da prateleira. A verificação ocorre no host antes de alterar os arrays e a revisão. O jogador recebe a instrução de se aproximar. O armário do bunker original mantém seu comportamento anterior. O limite trata a aproximação horizontal; não é uma solução anatômica de alcance vertical, flexão do tronco ou IK.

O esquema do inventário, formato de salvamento, GUIDs e autoridade não foram modificados. A posse continua mudando imediatamente no servidor; a animação é apresentação dessa mudança, não uma segunda transação.

## Validação

Compilação concluída, duas instâncias renderizadas executadas e capturas inspecionadas; resultados abaixo. Não declarar continuidade sem falhas sob latência/reconexão: os snapshots e atores cosméticos ainda trafegam por canais distintos. O teste local não representa rede externa.

A primeira rodada passou em 21 critérios, mas a revisão visual identificou orientação da garrafa dependente da câmera e aviso de distância persistindo após sucesso. A versão final interpola também a rotação: mantém a orientação real do armário durante aproximação e contato, e a orientação de transporte durante recolhimento. O aviso específico é limpo quando a ação de transferência aceita chega ao jogador. As primeiras evidências permanecem em `logs/reach_continuity_first_pass/`.

## Resultado de jogo — versão final

As **23 verificações** passaram com duas instâncias renderizadas simultâneas. O servidor rejeitou a tentativa distante em **204,94 cm**, com revisão zero, inventário vazio e os dois itens ainda guardados. Após aproximar, houve duas retiradas e duas devoluções do mesmo GUID, com revisões finais em 4. Porta bloqueada pelo jogador, rejeição com porta fechada, revisão obsoleta e ausência de modal permaneceram válidas.

A posição real do item na visão do observador foi medida a 0 cm do ponto da prateleira na aproximação, enquanto as mãos ainda estavam a aproximadamente 67 cm. A orientação também coincidiu (erro registrado 0°). A apresentação local registrou erro de posição e orientação zero no mesmo estágio. Isso valida a pose da malha no ensaio; não equivale a contato anatômico dos dedos.

Capturas reais revisadas na Unreal: aproximação com garrafa em pé, contato com luvas e devolução. O aviso específico de distância foi retirado depois da aceitação. Arquivos desta rodada ficam em `screenshots/bedroom_reach_continuity/`; as capturas finais anteriores foram preservadas nos caminhos anteriores.

Desempenho: host **29,59 FPS**, p95 **33,63 ms**, 1.036 amostras; cliente **29,62 FPS**, p95 **33,50 ms**, 1.037 amostras. Limite 30 FPS; janelas 960 × 540 / 800 × 450; resolução interna 70%; sombras e AO desligados. Medição curta em Editor, com entradas roteirizadas e conexão local. Não certifica executável distribuído, qualidade alta, sessão longa ou quatro jogadores.

## Limitações e próxima revisão

As luvas permanecem rígidas e os braços/dedos ainda não têm IK ou articulação final. O limite horizontal reduz a coleta distante, mas não valida todos os níveis das prateleiras nem o alcance vertical do corpo. As mãos cosméticas remotas ainda coexistem com os braços do manequim: falta a solução final de animação corporal/retargeting. Não houve nova autoria Blender, mudança da sala ou aplicação a outros ambientes.

Os canais de snapshots e atores cosméticos ainda podem chegar em momentos diferentes sob latência. Este marco elimina a retirada prematura do item durante a trajetória normal recebida, mas não garante ausência de um frame de transição ou continuidade sob perda de pacotes/reconexão. Isso requer um teste de rede com latência controlada e tratamento de cancelamento. Não foi produzido vídeo novo, novo executável ou publicação GitHub.

## Integridade e salvamento

Passaram as cinco regressões do armário original: criação do checkpoint, recarga, rejeição de slots inválidos, compatibilidade legada e migração. Os checkpoints usam o prefixo de teste `C13_AutomatedCheckpoint`, sem alterar a campanha real. O resultado está em `logs/bedroom_cabinet_save_result.json`.

Os 449 assets da base passaram na conferência de integridade. Fonte Blender do descanso, JSON do rig e da animação, sequência Unreal e mapa v003 conservaram seus hashes. Não foi necessário regenerar os arquivos Blender. Não houve novo teste de descanso, pois seu código e assets ficaram inalterados neste marco.

Evidências consolidadas: `docs/validation/bedroom_reach_continuity_2026-11-16.json`. Prévia existente: `tools/launchers/Ver-Quarto-Animacoes.command` (Unreal instalada, sem salvar campanha). Alterações locais, ainda sem novo pacote distribuível.
