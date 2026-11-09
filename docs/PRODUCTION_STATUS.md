# Estado real da produção

A solicitação atual autoriza avançar no acabamento e nos sistemas do GDD. O documento continua sendo a especificação do produto; sua restrição histórica a B0/B1 já foi superada pelas autorizações posteriores do usuário.

## Arte

- Arquitetura navegável e mobiliário construído: existentes; muitas silhuetas ainda são primitivas geométricas.
- Texturas do ambiente: seis superfícies procedurais com BaseColor, Normal e ORM em 512px, geração reproduzível e aplicação em escala mundial.
- Kit refinado: cama, armário e porta com UVs, bordas biseladas e três projetos Painter `.spp`. Onze materiais e 33 mapas de 1024px produzidos no Painter, exportados e aplicados por UV na Unreal. Quatro camas e quatro armários substituídos no dormitório; porta agora equipa 13 folhas móveis com colisão e movimento replicado; as três lacradas permanecem fixas.
- Em 19/10, o kit foi conferido no executável e E/F testados na cama. Essa validação não aprova a arte do bunker inteiro nem encerra os marcos de gameplay.
- Ainda pendentes: modelos com bordas e silhuetas refinadas, UVs por asset quando necessários, decalques narrativos, sinalização legível, acabamento externo e aprovação visual em perspectivas representativas.

## Sistemas

A base de interações passou a usar um controlador por conexão e decisões no servidor. Isso ainda não representa conclusão do GDD:

| Marco | Estado real e trabalho restante |
|---|---|
| U1 | Base de servidor autoritativo para coleta e camas implementada; quatro pontos de entrada e RPCs por proprietário. Treze portas físicas replicadas instaladas; 13/13 travessias passaram com a cápsula real. Checkpoint do host e reconexão local validados em `COOP_RECONNECT_REPORT.md`. Lobby, circulação conjunta com humanos, identidade Steam e testes completos ainda pendentes; evidências em `NETWORK_FOUNDATION_REPORT.md` e `DOORS_AND_INPUT_REPORT.md` |
| U2 | Mochila com interface, IDs preservados nos checkpoints solo e cooperativo, espaços/peso, consumo e descarte; necessidades e recuperação de energia na cama validadas no executável com quatro instâncias automatizadas (SURVIVAL_INVENTORY_REPORT.md). Regras em Data Asset; atributos privados ao dono. Salvamento solo e cooperativo com retomada dos participantes implementados; ver `PERSISTENCE_REPORT.md` e `COOP_RECONNECT_REPORT.md`. Gerador, circuitos e água integrados em 04/11 no modo de coleta; faltam empilhamento, autenticação Steam, recuperação de perfis e testes prolongados |
| U3 | Exterior inicial existe; faltam prédio explorável, radiação, equipamento, inimigo, combate, morte, mochila e retorno |
| U4 | Dardos são uma pontuação aleatória por interação; faltam mira jogável, cartas e três eventos sistêmicos |
| U5 | Pendente teste de 30–60 min com quatro jogadores, latência e perda de pacotes |
| U6 | Pendentes voz por proximidade e rádio, Steam, acessibilidade, áudio, conteúdo de lançamento e finais |

Map Check verifica a estrutura do mapa; não prova circulação com quatro jogadores nem execução de gameplay. Compilar e empacotar não comprova qualidade visual nem uma partida completa. O limite configurado de 45 FPS não é um benchmark.

## Ordem de conclusão

1. Preservar a validação do kit Painter no executável e completar a base cooperativa U1.
2. Teste ampliado de E/F, portas e saída das camas aprovado no executável; ainda executar sessões com quatro humanos e encerrar as pendências de U1.
3. Completar U2 com salvamento e anti-duplicação.
4. Fechar uma partida de ponta a ponta em U3/U4, incluindo objetivo e encerramento.
5. Executar U5 e corrigir os problemas antes do conteúdo adicional de U6.

Não há build Windows validada neste Mac. Uma entrega Windows exige compilação e teste em ambiente Windows apropriado. Convites Steam e voz exigem configuração e testes reais das respectivas integrações.

## Meta de calendário

A meta atual, informada em 29/10/2026, é um **MVP interno até 30/01/2027**, substituindo a referência anterior de lançamento em dezembro. Férias do criador: **04–15/01/2027**. Sequência, critérios e riscos em `MVP_TARGET_JANUARY_2027.md`. Não há garantia de lançamento nem autorização implícita para remover requisitos do GDD para caber no prazo. `RELEASE_TARGET_DECEMBER.md` permanece apenas como registro histórico.

## Planta aberta — 29/10/2026

O criador aprovou a evolução visual da convivência e solicitou um ambiente comum mais amplo. Convivência, cozinha, despensa, oficina, enfermaria e rádio serão zonas conectadas; dormitório, banheiro, antecâmara e gerador permanecem isolados, conforme confirmação explícita. A versão comparativa usa `Lvl_Bunker_OpenPlan`, sem substituir o mapa original nem migrar checkpoints implicitamente. Os resultados executados desta revisão ficam em `OPEN_PLAN_REPORT.md`; o planejamento de janeiro não significa que os sistemas pendentes já foram implementados.

## Objetos físicos do inventário — 19/10/2026

Cinco modelos próprios (água, lata, kit médico, pilha e chave) criados no Blender com peças editáveis, UVs e texturas originais. Aplicados aos seis recursos existentes do mapa. Fonte, renders e limites estão em `ITEM_ART_REPORT.md`; não substituem a produção dos demais tipos, mãos ou animações de uso.

## Primeira pessoa: interações com itens — 19/10/2026

Mãos enluvadas e acessórios próprios, gestos locais de coleta/consumo e variantes abertas de garrafa/lata. A confirmação vem do servidor e a mochila fecha para mostrar a ação. Fonte e limites em `FIRST_PERSON_ITEM_REPORT.md`. Ainda não há rig articulado dos dedos, som de manuseio ou atuação em terceira pessoa.

## Armários e despensa — 19/10/2026

Seis contêineres físicos, transferências com ID preservado, validação de revisão/capacidade/acesso e vistas privadas por jogador. A garrafa passou a azul. Evidências e limites em `STORAGE_REPORT.md`; o armazenamento é da sessão atual, com salvamento/reconexão ainda pendentes.

## Persistência solo — 21/10/2026

Mochila, necessidades, contêineres, recursos do mapa, itens largados e portas passaram a compor um checkpoint versionado, com duas cópias alternadas. F5, gravação automática e encerramento normal; restauração ao iniciar. Evidências e limites em `PERSISTENCE_REPORT.md`. Isso não conclui o salvamento de sessões cooperativas nem a reconexão.

## Checkpoint cooperativo e reconexão local — 21/10/2026

Até quatro conexões, reserva dos recursos desconectados, credenciais privadas locais e retomada dos três perfis após reinício do host. A rodada com 80 ms/2% de emulação preservou seis recursos únicos e bloqueou credenciais inválidas/duplicadas. Relatório em `COOP_RECONNECT_REPORT.md`; ainda não equivale a autenticação Steam, lobby acessível ou teste prolongado com humanos.

## Coleta inicial e fechamento — 30/10/2026

Entregue um modo separado `Lvl_CollectionRound` no aplicativo `Condominio13-MVP.app` (0.3.0): preparação, coleta normal de 90 segundos, alertas, fechamento físico sem esmagamento e retorno por liberação manual, inclusive com energia zero. A escada ganhou abertura real no piso, proteção lateral e iluminação. Foram adicionadas 12 unidades físicas de quatro tipos já existentes; isso não significa 12 novos tipos de itens.

O pacote passou em 25 verificações de caminhada, coleta, retomada com o mesmo GUID e cenário de dois jogadores. Também passaram as regressões de persistência, estoque, reconexão e armário físico. O primeiro ensaio do armário falhou por interferência do mouse na mira automatizada; a repetição com entrada física bloqueada na fixture passou, preservando o registro da falha. Testes locais automatizados não substituem quatro humanos ou internet.

Fonte Blender reaberta e validada, capturas reais e desempenho curto documentados em `COLLECTION_ROUND_REPORT.md`; hashes e resultados em `logs/round_delivery_manifest.json`. A comparação de planta aberta permanece preservada. Não é o MVP completo: sistemas e limites pendentes continuam no relatório e em `MVP_TARGET_JANUARY_2027.md`.

## Calendário e auditoria de direção - 03/11/2026

Versão 0.3.1, aplicativo separado `Condominio13-MVP-0.3.1.app`; os lançadores de coleta apontam para ele e o binário 0.3.0 foi preservado e conferido por hash. Ciclo de quatro minutos por dia, após o fechamento físico, segue o tempo do servidor e persiste sem avanço offline. A mochila ou o descanso não pausam o calendário. Saves 0.3.0 deste mapa foram carregados preservando ID e inventário; campos novos começam em zero/240 s. Não houve migração entre mapas nem alteração das taxas de fome/sede.

Passaram: compatibilidade anterior, caminhada, coleta/retomada, dois processos em rede com o mesmo dia, virada acelerada de dias, retomada do tempo e duração normal de 240 s. Regressões de persistência, estoque concorrente, reconexão e armário físico passaram no novo pacote. Registros em `logs/clock_delivery_manifest.json`. Testes automatizados não substituem sessão humana, internet ou Windows.

Amostra curta com duas janelas 960x540: host 49,88 FPS / p95 33,03 ms; cliente 48,43 FPS / p95 34,70 ms. Diferença para outubro não isolada por benchmark controlado. Ainda não há garantia de desempenho de partida longa.

Auditoria consolidada em `DIRECTION_AND_PRODUCTION_2026-11-03.md` e PDF em `output/pdf/Condominio13_Direcao_e_Producao_2026-11-03.pdf`. A ideia de sobrevivência social continua, mas o ciclo inteiro não existe. Gerador é comando sem circuitos; rádio é frase fixa; dardos sorteiam pontos. Próxima dependência: infraestrutura real, seguida de partida acessível, expedição, risco/informação, eventos, minijogo e encerramento. Esta entrega não modifica arte nem considera outros ambientes aprovados.

## Infraestrutura funcional - 04/11/2026

Primeira entrega exclusivamente de infraestrutura, versão 0.4.0, com contratos e gates em `INFRASTRUCTURE_ACCEPTANCE.md` e resultados em `INFRASTRUCTURE_REPORT.md`. Não houve expansão do mapa nem implementação de expedição, radiação, combate, morte ou voz.

Gerador consome combustível e condição, aceita galões e peças reais por GUID e cancela trabalho sem débito se perder acesso. Circuitos desligam/restauram iluminação real e serviços; iluminação de emergência mantém operação. A filtragem depende de energia e de cartucho; água bruta/tratada são volumes finitos, e beber desconta água e recupera hidratação no host. As taxas de fome/sede anteriores foram preservadas; escassez e pressão social não foram aprovadas em sessão humana.

Modelo de autoridade e namespaces de campanhas de coleta mantidos. Migração 0.3.1 testada com backup dos bytes antigos, GUID preservado e novos estoques introduzidos uma única vez. Estado de infraestrutura persistido; trabalho parcial cancelado ao retomar e sem consumo offline. Fontes novas: `blender/Bunker_Infrastructure_v001.blend`, sete meshes, UVs e 15 texturas incorporadas; biblioteca visual anterior não foi alterada.

Testes no pacote passaram para gerador, desgaste, circuitos, economia, água, retomada exata de estado e quatro conexões com 80 ms/2% de emulação. Nesse cenário duas instâncias renderizaram e duas usaram NullRHI. Passaram as regressões de coleta/retorno, calendário, persistência, estoque, reconexão e armário físico. Falhas de inicialização/roteiro e medições anteriores foram preservadas, não descartadas como aprovação. Manifesto: `logs/infra_delivery_manifest.json`.

Amostra final curta: host 31,52 FPS/p95 57,25 ms e cliente 32,43 FPS/p95 51,24 ms, duas janelas 960x540 entre quatro processos locais. Não estima uma única instância nem quatro computadores. A tentativa inicial com quatro janelas teve 11-17 FPS, com outra instância do jogo ativa; amostra não controlada. Persistem instabilidade pré-log no Mac, ausência de teste humano prolongado e de Windows/internet certificados. Existe uma manutenção cronometrada por vez e reserva de emergência sem esgotamento.

Aplicativo novo `Condominio13-Infrastructure.app`; lançadores de infraestrutura e coleta apontam para ele. Versões anteriores preservadas. O próximo marco deve usar o exterior existente para validar a primeira saída-coleta-retorno antes de ampliar o mapa.


## 04/11/2026 — Antecâmara / 0.4.1

Parte inicial do marco de expedição: intertravamento, equalização dependente de energia e recuperação externa, validados no pacote Mac com duas conexões; checkpoint anterior e regressão de reconexão preservados. Assets anteriores iguais. Relatório: `docs/AIRLOCK_REPORT.md`; manifesto: `logs/airlock_delivery_manifest.json`. A coleta externa/retorno/uso de recursos ainda não foi implementada; não marcar expedição como concluída.


## 05/11/2026 — Reposição externa / 0.4.2

Primeiro percurso de reposição funcional no estacionamento existente: coleta física, antecâmara, retorno e uso dos mesmos GUIDs para recuperar o gerador. Estoque finito e migração aditiva verificados; quatro conexões com reinício do host e execução contínua com uma instância. Corrigidos vão no acesso e canal de luz do piso externo. Relatório: `docs/EXPEDITION_REPORT.md`; manifesto: `logs/supply_delivery_manifest.json`. Não marcar U3/MVP como concluído: radiação, inimigo/combate, morte, comunicação, eventos e encerramento continuam pendentes; sem expansão de mapa.
# Continuidade — 09/11/2026

Publicação autorizada posteriormente em [ViniDeiro/bunker13](https://github.com/ViniDeiro/bunker13), branch main. Fontes, Content e assets LFS enviados; clone remoto independente com 449 hashes conferidos, Editor compilado e mapa carregado sem erros/avisos no commandlet. [Registro e limites](GITHUB_PUBLICATION.md). O parágrafo de preparação abaixo descreve o estado anterior ao envio. Não houve nova versão jogável com radiação.

Auditoria de arquitetura e preparação para GitHub: [arquitetura](ARCHITECTURE.md), [publicação](GITHUB_HANDOFF.md). Git LFS instalado/configurado localmente; fontes Blender/Painter e exports deixaram de ser ignorados, com regras LFS. Sem remoto, commit ou upload nesta etapa. Assets antigos ainda exigem preparação no índice; logs já rastreados exigem revisão. O README agora aponta para 0.4.2 e para a meta vigente de janeiro.

Radiação etapa 5A: modelo de regras isolado com 25 verificações C++/sanitizadores, build do Editor e automação `C13.Unit.Radiation.Model` aprovados. [Dependências, critérios e limite](RADIATION_ACCEPTANCE.md). Ainda sem integração ao gameplay/persistência/equipamento; não é radiação jogável. Aplicativo 0.4.2 preservado.

Regressão da retomada no pacote 0.4.2 aprovada no modo solo correspondente ao checkpoint da migração, preservando GUID/cronômetro. Uma primeira tentativa selecionou listen server para o checkpoint solo e foi bloqueada pelo validador; o ensaio foi interrompido e a causa registrada. Não houve redefinição dos saves pessoais. Nenhum FPS novo medido nesta etapa.
