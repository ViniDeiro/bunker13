# Base cooperativa — 19/10/2026

Este relatório registra a primeira entrega da base. A continuação das portas e dos controles está em `DOORS_AND_INPUT_REPORT.md`; o estado cumulativo está em `PRODUCTION_STATUS.md`.

## Implementação

- Um controlador por conexão recebe E/F; a ação segue por RPC do proprietário até o servidor. O antigo ator global de interações foi desativado e removido do mapa.
- O servidor verifica personagem, estado de descanso, intervalo entre ações, alcance e a primeira colisão na direção da câmera. Não aceita simplesmente o objeto indicado pelo cliente.
- Coleta atômica no servidor: GUID por objeto/sessão, reserva do estado ativo e limite de 12 espaços. Uma segunda tentativa não pode inserir a mesma instância novamente. O inventário replica apenas para seu proprietário.
- Ocultação e colisão dos objetos coletados são atualizadas nos clientes por notificação de replicação.
- Camas têm ocupante exclusivo no servidor. Descanso e modo de movimento são sincronizados; F solicita saída para o ponto anterior, com verificação de espaço. Logout libera a reserva.
- O mapa usa o modo cooperativo nativo e quatro pontos de entrada. O Blueprint existente de personagem, a arquitetura e os materiais Painter foram preservados.

## Validação automatizada

O teste inicia processos reais do aplicativo, por loopback, sem renderização. Um teste de desenvolvimento prepara posições e vistas numa área isolada; as transações passam pelo RPC normal de interação. Não simula uma partida humana nem mede desempenho gráfico.

A primeira execução detectou vínculos de teclado inválidos e câmera desatualizada no servidor para jogadores remotos. Os controles foram corrigidos e a autoridade passou a calcular a câmera a partir do personagem atual.

Resultados registrados:

| Execução | Resultado |
|---|---|
| `logs/network_packaged_result.json` | Anfitrião + três clientes: PASS; 4 jogadores, 1 item, 1 GUID único, 1 cama ocupada, item distante ainda ativo |
| `logs/network_clients_final_result.json` | Executável final, anfitrião fora da disputa: PASS; cliente remoto recebe o item, outro recebe recusa por cama ocupada; quatro instâncias confirmam item oculto/sem colisão e cama ocupada |
| `logs/network_package.log` | Compilação, cook e stage concluídos com ExitCode 0 |
| Aplicativo final | Cópia do stage completo e verificação `codesign --verify --deep --strict` concluídas |

O primeiro cenário foi executado antes do último ajuste de sincronização e saída de cama; o cenário exclusivo de clientes foi executado depois dele. O teste reproduzível está em `scripts/run_network_smoke.py`: executar sem argumentos para a disputa comum ou com `--remote-only --tag network_clients_final` para exigir coleta por cliente remoto.

O aplicativo final renderizou na janela normal e a cena mudou durante tentativas de movimentação, mas o controle de foco/teclado da automação não permitiu concluir E/F com evidência confiável. Essa verificação manual da nova versão permanece pendente; o sucesso do teste de rede não a substitui. A instância de inspeção foi encerrada após a conferência. Não foi medido FPS.

Uma tentativa intermediária com `-server` no aplicativo Game não iniciou um servidor dedicado válido (`logs/network_remote_result.json`, FAIL). Não foi usada como evidência multiplayer; foi substituída pelo teste válido de listen server com clientes remotos. Nenhum suporte a servidor dedicado é declarado.

## Limites desta entrega

U1 ainda está parcial. Faltam portas móveis replicadas, interface de sessão, circulação com quatro humanos, teste de capacidade da mochila, reconexão e teste de longa duração com latência/perda. A implementação de liberação de cama na desconexão não substitui seu teste real.

GUIDs e inventários atualmente duram a sessão: não há persistência/reconexão pronta, peso, descarte nem consumo. A cama ainda não possui animação de deitar nem sistema real de energia. Gerador replica o comando, mas ainda não alimenta circuitos. Dardos continuam um protótipo aleatório; painel não apresenta valores falsos de sobrevivência.

Não houve build Windows, integração Steam, voz, teste de 30–60 minutos nem aprovação de arte do bunker inteiro. Não há candidato a lançamento.
