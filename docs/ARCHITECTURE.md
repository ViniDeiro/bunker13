# Arquitetura — estado auditado em 09/11/2026

A base é um módulo C++ de Unreal com listen server autoritativo. Há separação por arquivos e responsabilidades, mas ainda não é uma arquitetura pronta para produção. Não há necessidade demonstrada de plugins/módulos adicionais agora. O maior problema é o acoplamento das classes centrais, não a quantidade de pastas.

## Propriedade dos dados

| Responsabilidade | Fonte de verdade atual | Regra de evolução |
|---|---|---|
| Propriedade dos itens | `FBunkerInventoryEntry`, GUID, mundo/mochila/contêiner | Um proprietário ativo por GUID; preservar tombstones. Não criar inventário de expedição paralelo. |
| Atributos pessoais | `ABunkerPlayerState`, replicação OwnerOnly | Clientes enviam intenções; não enviam valores de saúde/exposição. Não divulgar estado vital global. |
| Interação | `ABunkerPlayerController::ServerInteract`, atores físicos | Validar estado, distância, visada, disponibilidade e cooldown no host. |
| Estoque físico | `BunkerReferenceCabinet` e fluxo legado `BunkerContainer` | Slot/revisão e autoridade; padronizar o fluxo legado gradualmente. |
| Energia/água | `ABunkerInfrastructure` | Dados de infraestrutura persistidos; apresentação reage ao estado do servidor. |
| Partida/antecâmara | `ABunkerRound`, portas físicas | Relógio do host, fechamento sem esmagamento, retorno sem softlock. |
| Checkpoint | `BunkerPersistence`, `UBunkerSaveGame` | Validar antes de mutar mundo; cópias alternadas e checksum; migração aditiva com backup. |
| Reconexão | `BunkerReconnect`, perfil local e registros reservados | Restaurar participante original e sua mochila; não confundir com identidade Steam. |
| Arte | Blender/Painter → exports → Content | Fontes editáveis e assets importados versionados juntos; nenhum editor gráfico pertence ao runtime. |

## Dívidas verificadas

- `BunkerNetwork.cpp` tem 490 linhas e seu header 199, com input, RPCs, apresentação e muitos campos de ensaios. Dividir os `.cpp` de teste ajuda a leitura, mas não isola completamente o estado dos testes da classe de produção.
- `BunkerSurvival.cpp` mistura necessidades, transações de mochila, consumo e desenho do HUD. Separar apresentação de sobrevivência é uma refatoração futura com regressão própria.
- `BunkerInfrastructure.cpp` também cria props e geometria e ajusta iluminação. As posições dos suprimentos/patamar são coordenadas no código. Migrar a autoria para atores/configuração do nível depois de proteger o fingerprint e as chaves; mover tudo agora quebraria saves sem migração.
- `BunkerPersistence.cpp` (488 linhas) depende dos tipos concretos de portas/contêineres. A validação central evita relaxamento acidental, mas exige um contrato explícito para cada extensão.
- Algumas mensagens usam `FString`/textos literais: localização está incompleta. Não afirmar que já há suporte final a inglês.
- Assets antigos estão em Git comum e fontes Blender/Painter antes estavam ignoradas. Sem LFS e um clone limpo, compartilhar só o código não reproduz o trabalho.
- Scripts de integração antigos usam caminhos deste Mac; instalação reproduzível em outra máquina continua pendente. A documentação registra UE 5.8.3 usada aqui, não certifica Windows.

## Decisão adotada para o próximo sistema

O cálculo de radiação fica em `Source/Condominio13/Survival/BunkerRadiationModel.h`, sem dependência de mundo, UI, RPC, inventário ou arquivos. Ele recebe estado/parâmetros e devolve um resultado; não possui equipamento nem consome recursos. O mesmo código é testado em C++ com sanitizadores e pelo runner de automação da Unreal.

O adaptador de gameplay ainda será implementado. Deve obter taxa de volumes de exposição no host, usar parâmetros de Data Asset, buscar o equipamento por GUID no inventário existente e aplicar o resultado ao estado privado persistente. A apresentação lê o estado autorizado. Não será permitido um cliente escolher a dose, a duração ou a condição do equipamento.

Condição deve pertencer ao item por GUID, e não a um campo que reseta ao equipar: guardar, largar, transferir e reconectar precisam carregar o mesmo desgaste. A biblioteca aceita um escalar de condição para calcular o passo; isso **não implementa** esse contrato de propriedade.

## Estratégia de mudança

Não renomear classes refletidas, chaves de mundo, campos serializados ou pastas de Content sem migração específica. Não fazer uma reestruturação geral junto com uma mecânica nova. Introduzir uma responsabilidade isolada, integrar, verificar checkpoint/reconexão e percurso, então avançar.

Testes locais de matemática, compilação da Unreal, automação de engine, pacote Mac, quatro processos e playtest humano são evidências diferentes. Nenhum substitui os outros. A versão jogável 0.4.2 continua sendo a entrega de expedição; esta base não é uma nova versão com radiação funcional.
