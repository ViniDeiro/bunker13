# Quarto de referência — contato e custo de animação — 16/11/2026

## Escopo e critérios

Continuação do quarto existente, sem ampliar o mapa, substituir materiais ou alterar o inventário. Dependências: armário físico v002, apresentação local/remota e pose replicada v003. Aceitação: aproximação com mãos vazias ao pegar, contato no ponto real do item, recolhimento após guardar, duas instâncias concordando sobre posse/IDs e regressão de descanso com restauração da caminhada.

## Implementação

A apresentação de pegar agora separa aproximação (0–25%), contato (25–34%) e recolhimento (34–100%). Guardar aproxima até 72%, mantém contato até 88% e recolhe a mão depois de soltar. O item da apresentação aparece após o contato ao pegar e desaparece ao soltar. Jogador e observadores usam a mesma função de trajetória, somente nos mapas de estudo do quarto. A mão permanece uma malha rígida: isso não implementa dedos articulados nem IK anatômico.

A pose de descanso evita reaplicar transformações idênticas e avaliar explicitamente os ossos quando o tempo amostrado permanece igual. O componente esquelético continua com seu funcionamento normal: esta mudança não elimina todo o custo de animação e não comprova melhora de FPS por si só.

Nenhuma mudança no formato de save, GUIDs, protocolo de transferência, validação do host ou materiais. A posse continua transferida pelo servidor imediatamente. A apresentação não atrasa a transação: ainda pode existir uma pequena lacuna visual entre o desaparecimento da prateleira e o contato da mão ao pegar. Resolver uma transferência visual perfeitamente contínua exige coordenar também a malha da prateleira; não foi declarado concluído aqui.

## Validação

Regressão do descanso: 18 verificações passaram com host renderizado e cliente sem janela. Foram testados corpo real deitado, entrada/saída intermediária, cama ocupada, recuperação de energia, interrupção e restauração de caminhada/Animation Blueprint. Host: 29,69 FPS, p95 33,54 ms, 683 amostras; cliente sem renderização: 29,92 ticks/s (não FPS de segunda tela). Perfil: host 960 × 540, resolução interna 70%, sombras/AO desligados, limite 30. A rodada anterior registrou 25,08 FPS, mas carga e condições de inicialização variaram; esta comparação não isola o efeito da alteração.

Primeiro ensaio do armário passou logicamente, mas a inspeção da captura mostrou mãos escuras na prateleira. Causa identificada no código: luzes exclusivas das mãos ficavam junto da câmera, com raio de 90 cm, enquanto o alcance se estendia além disso. A correção mantém essas luzes acompanhando o alcance e habilita iluminação do ambiente nas malhas locais do quarto. As luzes auxiliares continuam isoladas dos objetos do mundo. Logs e capturas reprovadas visualmente preservados em `logs/bedcab_dark_contact_2026-11-16/`. A revisão do roteiro também removeu três verificações duplicadas, deixando 18 critérios distintos. A prévia continua dependente do Editor Unreal instalado; não constitui atualização do executável distribuído.

## Arquitetura preservada e próximos riscos

A curva compartilhada `BedroomReachMotion` calcula somente posições e visibilidade. `BunkerItemPresentation` continua responsável pela visão do dono; `BunkerObservedAction` pela apresentação dos demais. O servidor continua sendo o único responsável pela mudança de posse. Nenhum ator cosmético recebe um ID utilizável como inventário. A pose da cama permanece um ator cosmético separado do sistema de energia/ocupação.

Ainda faltam sincronização visual integral na retirada da prateleira, mãos articuladas, avaliação humana das animações, quatro participantes, reconexão nessa cena e um novo pacote testado. A prioridade de sobrevivência cooperativa continua sendo validar infraestrutura e depois uma expedição completa; este polimento não representa entrega desses marcos nem avanço para outros ambientes.

## Resultado final

Armário: **18 critérios distintos passaram**, com duas instâncias renderizadas simultâneas e comandos roteirizados. Foram observadas duas retiradas e duas devoluções do mesmo GUID, rejeição de revisão obsoleta, rejeição com porta fechada, bloqueio da porta pelo corpo, ausência de modal e concordância dos itens visíveis. As novas verificações medem aproximação sem item, pivô no ponto de contato ao pegar/guardar e ocultação do item após soltar. Elas não medem contato dos dedos com a superfície.

Host: **29,86 FPS**, p95 **33,50 ms**, 1.045 amostras; cliente renderizado: **29,94 FPS**, p95 **33,46 ms**, 1.048 amostras. Perfil: janelas 960 × 540 / 800 × 450, resolução interna 70%, sombras/AO desligados, limite 30. Inspeção real das capturas confirmou garrafa azul e luvas iluminadas após a correção. O ensaio inicial escuro foi mantido como falha visual, apesar de ter passado logicamente.

O teste da cama (18 verificações) foi concluído antes da última recompilação, que alterou somente a iluminação da apresentação de itens. O armário foi reexecutado após essa recompilação. Os 449 assets anteriores passaram na conferência e os cinco hashes de fonte/dados/animação/mapa do descanso permaneceram idênticos aos de 13/11. Não houve alteração da cena ou da fonte Blender nesta etapa: os arquivos editáveis anteriores continuam válidos.

Evidências consolidadas: `docs/validation/bedroom_interactions_2026-11-16.json`. Capturas reais: `screenshots/bedcab_contact_take.png`, `screenshots/bedcab_contact_store.png` e `screenshots/restpose_host_09.png`. Não foi produzido vídeo novo.

Próxima etapa no mesmo ambiente: braços/mãos com alcance plausível, grip por tipo de objeto e continuidade da malha na retirada. A versão atual ainda permite um alcance visual longo e usa luvas sem braços articulados; portanto não está aprovada como animação comercial final. As alterações continuam locais, sem publicação no GitHub ou novo executável empacotado.
