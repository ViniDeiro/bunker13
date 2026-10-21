# Salvamento solo — 21/10/2026

Primeira etapa de persistência de U2. Não conclui a reconexão cooperativa prevista no GDD.

## Uso no executável

- A partida solo retoma automaticamente o último checkpoint válido ao abrir.
- F5 salva manualmente; no teclado do Mac, a configuração das teclas de função pode exigir Fn + F5.
- Gravação automática a cada 60 segundos e no encerramento normal da Unreal.
- São preservados mochila, saúde/alimentação/hidratação/energia, conteúdo dos seis armários, itens largados, recursos já retirados, portas (posição e destino do movimento) e estados simples dos demais objetos interativos.
- O jogador retoma acordado. Se salvou deitado, a posição registrada é a saída da cama; reservas de cama e interfaces abertas não são persistidas.
- A posição carregada passa por teste de cápsula e piso. Se obstruída ou sem piso próximo, permanece o ponto de entrada, preservando os recursos restaurados.

## Integridade

Dois arquivos alternados A/B, número crescente de gravação e checksum. Cada nova gravação é reaberta e validada antes da confirmação. Ao iniciar, escolhe-se a gravação válida mais recente; se a outra estiver danificada, antiga ou incompatível, usa-se a válida. Se ambas falharem, preservam-se os arquivos e bloqueia-se a gravação, evitando substituir silenciosamente uma campanha.

Antes de alterar o mundo, validam-se versão, assinatura do layout, estados numéricos, referências de itens, capacidades e IDs únicos nos estoques ativos. Recursos originais recolhidos ficam registrados como inativos, evitando reaparecimento ao recarregar. Itens largados são recriados com o mesmo ID, modelo, materiais e escala. Os armários mantêm estoques apenas no servidor; o salvamento não amplia a visibilidade de inventários aos colegas.

A assinatura atual usa os nomes dos atores salvos no mapa, classe, tipo e posição. Alterações de layout podem invalidar checkpoints; migração entre versões ainda não existe. O esquema exige incremento explícito de versão quando houver mudança incompatível. Checksum detecta dano acidental; não é mecanismo antitrapaça.

Arquivos de uso normal: `C13_SoloCheckpoint_A.sav` e `C13_SoloCheckpoint_B.sav`, na pasta SaveGames gerenciada pela Unreal dentro do contêiner do aplicativo Mac. Os testes usam exclusivamente `C13_AutomatedCheckpoint_A/B` e não leem nem apagam a campanha normal.

## Validação

**Aprovado: 17 passos em 17 processos independentes do executável Mac.** Resultado em `logs/persistence_result.json`, produzido por `scripts/run_persistence_test.py`. O roteiro abre processos independentes do executável empacotado, prepara recursos de teste no servidor e exercita o descarte real e a tecla F5. A produção faz a serialização, validação e aplicação dos dados; o teste não usa uma implementação alternativa de salvamento.

A rodada final verificou F5 pelo input real, restauração e nova gravação, saída normal e reabertura com o último avanço, recuperação da cópia anterior após dano/versão/layout/duplicação, posição obstruída com retorno ao ponto de entrada e bloqueio de gravação quando nenhuma cópia é válida. Mochila, estoque e item largado permaneceram únicos; três recursos originais continuaram inativos; necessidades e portas foram restauradas.

O primeiro roteiro de corrupção danificou a cópia antiga após uma terceira gravação; a restauração da cópia mais recente estava correta. A segunda rodada encontrou uma asserção no preparo do caso de duplicação: o próprio teste tentou acrescentar uma referência de dentro do mesmo array. O preparo foi corrigido com uma cópia independente do item. Essas falhas de roteiro são mantidas nos relatórios `persistence_first_result.json` e `persistence_second_result.json`.

## Limites que continuam abertos

- Salvamento está habilitado apenas em modo solo. Sessões em rede não gravam nem carregam essa campanha. Identidade autenticada dos quatro jogadores, reconexão, restauração de desconectados e encerramento do host ainda precisam de implementação/teste próprios.
- Não existe menu de campanhas, seleção de slots, comando de nova partida ou migração de arquivos incompatíveis. Um checkpoint incompatível bloqueado exige tratamento de recuperação antes de retomar gravações.
- Encerramento forçado, travamento ou queda de energia podem perder o avanço desde o último checkpoint confirmado. O teste de saída usa o caminho de encerramento normal da Unreal.
- Não há seed de eventos, tempo, circuitos, doença ou estados de expedição para persistir: esses sistemas ainda não estão implementados.
- Testes automatizados não substituem sessões longas com quatro humanos. Ainda não há candidato a lançamento, versão Windows validada ou benchmark de desempenho novo.

## Pacote e regressões

Empacotamento Mac Development aprovado em `logs/persistence_package_final.log`; assinatura local verificada. O pacote final reutiliza o conteúdo já processado porque não houve alteração de assets. Hash e resumo em `logs/persistence_execution.json`.

- Quatro processos em rede: todas as 14 verificações de estoque/acesso/capacidade/privacidade aprovadas (`logs/persistence_storage_regression_result.json`); nenhum deles leu ou gravou checkpoints.
- Interações de mãos: quatro ações e cinco frames aprovados (`logs/persistence_hands_regression_result.json`), com coleta, consumo e proteção contra repetição de ID.
- Captura nativa inspecionada: `screenshots/persistence_water_hud.png`. O rodapé F5 é legível e a garrafa permanece azul. Isso não aprova a arte final do ambiente.
