# Checkpoint cooperativo e reconexão — 21/10/2026

Extensão da persistência para o listen server de até quatro jogadores. O salvamento solo anterior continua separado e compatível. Este marco não conclui U1/U2 nem aprova lançamento.

## Comportamento implementado

- O host grava mochila e necessidades próprias, mundo, armários e registros dos três participantes remotos, conectados ou não.
- Cada campanha possui um identificador. Ao entrar pela primeira vez, o participante recebe uma credencial privada emitida pelo servidor; o cliente a grava e verifica antes de ganhar acesso ao personagem.
- A credencial retoma o mesmo registro da campanha, com os mesmos IDs de itens e necessidades. Nomes de jogador e IDs de conexão temporários não concedem acesso a uma mochila.
- Quem desconecta deixa os recursos reservados no servidor. A captura acontece antes que a Unreal destrua ou desassocie o personagem; depois a mochila transitória é esvaziada e a cama liberada.
- Duas conexões não podem assumir o mesmo registro. Credencial inválida e novo participante quando os três registros já estão reservados são recusados.
- Movimentação e transações ficam bloqueadas durante a restauração. A mochila não pode abrir nesse intervalo; interfaces e bloqueios de controle são limpos ao concluir a entrada.
- A posição é testada com cápsula e piso; em local obstruído, mantém-se o ponto de entrada. O personagem retoma acordado, sem reservar uma cama por referência antiga.
- O host grava ao autorizar entrada/retorno, na desconexão, a cada minuto, por F5 e no encerramento normal. A próxima hospedagem retoma a campanha e seus registros remotos. Não há migração de host.

## Dados e integridade

`C13_CoopCheckpoint_A/B` usa esquema 2 e inclui o roster remoto. `C13_SoloCheckpoint_A/B` continua no esquema 1. Ambos usam cópias alternadas, checksum e validação antes de alterar o mundo. A validação de IDs cobre mochila do host, participantes online/offline, contêineres e recursos ativos do mapa conjuntamente.

As credenciais ficam em `C13_ReconnectProfile_A/B`, na pasta SaveGames do aplicativo de cada cliente. Cada emissão escreve uma cópia verificada e espelha o conteúdo imediatamente na outra, pois a primeira credencial também precisa de reserva utilizável. Os arquivos possuem checksum e validação; dano às duas cópias impede entrada, preservando os arquivos. Até 32 campanhas podem ser registradas no perfil atual. O host persiste somente o hash BLAKE3 da credencial; não publica a credencial nem o roster em replicação global ou logs.

Os registros de quem está fora ficam congelados: não simulam fome, energia ou avatar ausente. Política de ausência e balanceamento ainda precisam ser definidos quando tempo, risco e morte estiverem implementados. Recursos reservados não substituem as mochilas físicas de personagens mortos, que continuam pendentes no GDD.

**Aprovado: 23 verificações de reconexão, em 13 processos novos, com no máximo quatro conexões simultâneas.** Os três clientes também registraram a perda da sessão ao fechar o host.

## Teste reproduzível

`scripts/run_reconnect_test.py` usa o executável Mac, até quatro conexões simultâneas e processos novos para reconexão e reinício do host. A Unreal aplica 80 ms de atraso e 2% de perda de pacotes de saída em cada processo; isso não representa medição de ping real nem todas as condições de rede.

O preparo Development distribui seis modelos reais: quatro mochilas, um estoque e um item largado; registra um participante em cama. O restante usa os mesmos métodos de credencial, serialização, validação, desconexão e restauração de uso normal. O teste inclui credencial corrompida, tentativa de conexão duplicada, credencial desconhecida, novo perfil sem vaga, tentativa de gravar recurso duplicado entre estoques e retomada dos três perfis depois de fechar/reabrir o host.

Os arquivos de teste usam exclusivamente `C13_TestCoopCheckpoint` e `C13_TestReconnectProfile_0..8`. As instâncias recusadas que retornam ao mapa inicial também ficam impedidas de acessar checkpoints normais. Resultados em `logs/reconnect_result.json`; o resumo do pacote e das regressões está em `logs/reconnect_execution.json`.

O primeiro roteiro não conseguiu confirmar a gravação final por logs após SIGTERM: o handler do Mac coloca o logger em modo Panic. O relatório dessa rodada foi preservado em `logs/reconnect_first_result.json`. A saída final é solicitada pelo caminho normal de encerramento da Unreal, com confirmação adicional pela campanha carregada em outro processo. A inspeção do código da engine também motivou antecipar a captura do personagem para antes de `APlayerController::Destroyed`, em vez de depender apenas de `Logout`.

## Pendências concretas

- É uma credencial portadora local, não autenticação de conta Steam. O transporte atual não comprova autenticação/cifragem para internet; essa integração é necessária antes da distribuição. Perder as duas cópias do perfil exige um fluxo de recuperação ainda não implementado.
- Hospedagem/entrada continuam por `C13Host` e `C13Join`; faltam lobby acessível, lista de campanhas, nova partida, recuperação e mensagens finais de desconexão no menu.
- Ainda não existe fase de preparação/coleta para encerrar entrada de novos participantes no momento previsto no GDD. A reserva de três registros é permanente nesta campanha; a regra por fase deve ser integrada ao loop de partida.
- Desligamento forçado/travamento do host pode perder alterações desde o último checkpoint confirmado. Não há migração de host, recuperação por nuvem ou migração entre layouts incompatíveis.
- Faltam testes longos com quatro humanos, outros perfis de latência/perda, integração Steam/voz e build Windows. Não houve novo benchmark de desempenho ou aprovação da arte final neste marco.

## Pacote final e regressões

Executável Mac atualizado e assinatura verificada. Empacotamento aprovado em `logs/reconnect_package_final.log`, reutilizando assets já processados e inalterados. O hash atual em `logs/reconnect_execution.json` substitui, para o caminho do executável atual, o manifesto do marco solo anterior.

- Reconexão: 23/23 verificações aprovadas; 13 processos novos e até quatro conexões simultâneas (`logs/reconnect_result.json`).
- Solo: 17/17 etapas em processos separados (`logs/reconnect_solo_regression.json`).
- Armários: 14/14 verificações com quatro processos (`logs/reconnect_storage_regression.json`).

Nenhum diagnóstico anterior do Painter foi alterado. Fontes Blender e texturas não mudaram neste marco.
