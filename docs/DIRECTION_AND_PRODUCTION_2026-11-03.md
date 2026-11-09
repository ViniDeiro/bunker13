DEIROS DEV / 03 NOV 2026 / 01 / PARECER

Condomínio 13
Direção e estado real


## Condomínio 13<br/>Direção e estado real


A ideia original foi preservada no projeto, mas ainda não foi comprovada como uma partida completa. Existe uma base técnica de abrigo, itens físicos, necessidades, rede e coleta. Ainda falta o que faz essa base gerar histórias: escassez com decisões, expedição perigosa, comunicação limitada, consequências, eventos e um encerramento.

O jogo não está pronto para lançamento. Este relatório compara o GDD v1.0 de 13/10, as mudanças autorizadas na conversa, o código atual e os registros locais. Não usa quantidade de arquivos ou scripts executados como medida de conclusão.

O que avançou nesta entrega

Ciclo de dias acelerados integrado ao modo de coleta: um dia equivale a quatro minutos reais por padrão; começa após o fechamento físico do abrigo, segue o relógio do host e continua ao abrir a mochila ou descansar. O checkpoint preserva o tempo sobrevivido; tempo com o jogo fechado não é consumido. Checkpoints anteriores deste mapa começam o calendário no Dia 1, sem trocar IDs ou apagar recursos.

Meta vigente

MVP interno em 30/01/2027; férias do criador de 04 a 15/01/2027. Essa meta substitui a antiga referência a lançamento em dezembro. Não é uma promessa de publicação na Steam. Não existe automação trabalhando durante férias nem capacidade de equipe medida neste relatório.

Leitura: páginas 2-3 explicam o jogo; 4-5 inventariam os sistemas; 6 avalia fidelidade; 7 registra esta entrega; 8 apresenta os testes do GDD; 9 organiza os próximos passos; 10 lista fontes e limites.

DEIROS DEV / 03 NOV 2026 / 02 / VISÃO ORIGINAL

O jogo que você propôs


## O jogo que você propôs


Um a quatro sobreviventes dividem um abrigo de defesa civil sob o Mercado Aurora, em Santa Aurora, depois do Evento Cinza. O bunker é relativamente seguro, mas seus recursos acabam. O grupo precisa decidir como viver junto, quem sai, quem fica e quanto arriscar para voltar.

O mistério envolve alas lacradas, registros contraditórios do desastre e a confiabilidade de um sinal de resgate. As saídas planejadas são resgate, veículo de fuga ou rota subterrânea; o MVP precisa de uma. A cadeia narrativa ainda não está implementada.

Pilar | Como deve aparecer na partida

Bunker protagonista | Conversar, descansar, trabalhar, cozinhar, tratar ferimentos, esconder e compartilhar itens em lugares reconhecíveis.

Informação limitada | Voz por distância e rádio condicionado a equipamento/bateria. O abrigo não recebe aviso mágico de morte do explorador.

Recursos materiais | Unidades físicas localizadas, com IDs e transações validadas pelo servidor. Mochila privada e armazenamento no mundo.

Risco com consequência | Ferimentos, exposição, perda de equipamento e morte naquela partida. Mochila recuperável em situação perigosa.

Histórias emergentes | Conflito surge de decisões e escassez; não existe traidor obrigatório nem tarefa linear constante.

Rejogabilidade e tom | Seed, eventos e recursos variam; suspense externo convive com humor e atividades sociais.

A referência The Rain orienta atmosfera de abrigo habitado, escala e tensão; identidade, arquitetura, objetos e narrativa devem continuar próprios da Deiros Dev. O GDD pede semi-realismo coeso; seu pedido posterior elevou o acabamento da sala de referência. Isso precisa ser avaliado no jogo e compatível com o Mac de teste.

DEIROS DEV / 03 NOV 2026 / 03 / FLUXO

Como uma partida deve funcionar


## Como uma partida deve funcionar


Momento | Proposta do GDD | Situação atual

1. Preparar | Host, amigos, personagem, microfone, dificuldade e seed. | Conexão local e retomada; faltam lobby e configurações acessíveis.

2. Coletar | 90 s, pegar recursos sob limites de mochila e voltar. | Jogável: avisos 30/15/5 e relógio do servidor.

3. Fechar | Porta física; quem fica fora enfrenta risco e alternativa de retorno. | Fechamento seguro e liberação manual. Perigo externo ainda ausente.

4. Viver | Consumir, dormir, organizar, manter energia e água, resolver crises. | Consumo, descanso, parte do armazenamento e calendário; infraestrutura incompleta.

5. Sair e voltar | Equipamento, antecâmara, rua/prédio, radiação e inimigo. | Não há expedição completa; abertura da porta não é sistema de expedição.

6. Concluir | Objetivo de resgate, fuga ou rota subterrânea; derrota e resumo. | Nenhuma rota com encerramento implementada.

Como testar hoje

Abrir Jogar-Coleta-MVP.command; R inicia a coleta no host; WASD/mouse movem e olham; E interage; I abre a mochila, setas selecionam, U usa e G larga. F5 salva no host. F sai da cama. No armário de referência, E abre/pega e X guarda o item selecionado em um espaço livre, sem modal de estoque.

Hospedar-Coleta-MVP.command e Entrar-Coleta-MVP.command permitem teste na mesma rede com IP. Os aplicativos precisam da mesma versão. Ainda faltam convites Steam e fluxo de internet validado. Depois da coleta o jogo continua como sandbox; o Dia 2 não dispara uma missão nem uma vitória automática.

DEIROS DEV / 03 NOV 2026 / 04 / INVENTÁRIO TÉCNICO

O que existe e seus limites


## O que existe e seus limites


Sistema | Implementação e evidência | O que falta

Arquitetura | Bunker conectado, escala e colisões verificadas; fontes Blender/exports. | Conforto com quatro humanos, acabamento consistente e sinalização.

Planta aberta | Seis zonas comuns; dormitórios, banheiro, antecâmara e gerador isolados. | Biombo/organização da enfermaria, pequenos grupos e teste acústico.

Arte | Sala de referência PBR, kit de cama/armário/porta, três fontes Painter. | Arte final do bunker inteiro, exterior e personagens; LODs/orçamento amplo.

Portas e camas | Folhas móveis replicadas, colisão; cama ocupa jogador e recupera energia. | Animação corporal final, som/acessibilidade mais completos.

Itens | Cinco tipos físicos: água azul, comida, remédio, pilha e ferramenta. Mais 12 unidades na coleta. | MVP pede 12-20 tipos utilizáveis. Pilha/ferramenta ainda sem sistemas de destino completos.

Mochila e consumo | Espaços/peso, ID, comer/beber/curar e largar, validação no host. | Carregar grandes volumes, carrinho, empilhar, receitas e variantes.

Armazenamento | Armário de referência abre e expõe objetos; transações por slot e revisão. | Padronizar os contêineres legados; ainda existem fluxos de estoque com interface.

Não contar unidades como tipos: doze objetos adicionais não são doze itens diferentes. Ter um modelo de rádio, pilha, ferramenta ou gerador também não comprova sua mecânica final.

DEIROS DEV / 03 NOV 2026 / 05 / GAMEPLAY E REDE

O que é funcional e o que é demonstração


## O que é funcional e o que é demonstração


Sistema | Estado real | Pendência

Necessidades | Fome, sede, saúde e energia no host; atributos privados. | Radiação, doenças, ferimentos, balanceamento de sessão longa.

Tempo | Novo ciclo persistido e compartilhado; quatro minutos por dia. | Eventos por dia, pausa solo opcional e ajuste de dificuldade.

Coleta/retorno | 90 s normais; fechamento físico e retorno manual mesmo exausto. | Variação de loot, rotas equivalentes para quatro e ameaça externa.

Save/reconexão | Cópias alternadas, checksum, validação e reserva de recursos desconectados. | Menu de campanhas, recuperação de perfil, Steam e testes de internet.

Rede | Listen server; quatro conexões em testes históricos com latência/perda. | Quatro humanos por 30-60 min; duas máquinas e transporte final.

Gerador | Somente alterna estado e exibe comando ligado/desligado. | Combustível, reparo e circuitos que mudam luzes/dispositivos de verdade.

Rádio/voz | Rádio exibe texto fixo. | Voz por proximidade, bateria, frequência, ruído, mute/PTT e privacidade.

Dardos/eventos | Dardos sorteiam pontuação; sem diretor de eventos. | Minijogo de habilidade e três eventos com seed/cooldown.

Expedição/final | Exterior inicial, sem ciclo completo. | IA, combate, morte/mochila, espectador restrito e vitória/derrota.

As ações das mãos são procedurais com gestos de alcance e consumo; observadores próximos podem enxergar ações relevantes. Ainda não são uma atuação corporal final ou um rig articulado dos dedos.

DEIROS DEV / 03 NOV 2026 / 06 / FIDELIDADE

Onde seguimos sua linha e onde há lacunas


## Onde seguimos sua linha e onde há lacunas


Mudanças autorizadas, sem perda de função

O salão aberto substituiu a divisão original de convivência, cozinha, despensa, oficina, enfermaria e rádio. As funções continuam obrigatórias. Os quatro ambientes isolados foram confirmados por você. A garrafa azul e o acabamento menos enferrujado seguem suas correções. A meta é janeiro de 2027 para MVP, não lançamento comercial em dezembro.

O maior risco de desvio

Hoje o projeto oferece espaço, objetos e ferramentas de teste, mas ainda poucas razões para o grupo negociar, sair ou temer uma perda. Se a produção continuar apenas decorando salas, a fantasia de sobrevivência social não se confirma. É preciso conectar manutenção, consumo, expedição e consequências antes de ampliar o mapa.

Diferenças que precisam ficar explícitas

A liberação manual externa é uma solução provisória coerente com evitar softlock; ainda não oferece o alto risco prometido porque faltam ameaças. A escolha de começar o Dia 1 após fechar o abrigo é uma decisão de implementação para avaliação; o GDD não fixa esse instante. Checkpoints antigos começam esse calendário em zero porque não guardavam tempo anterior.

Os atributos ainda caem por minuto real, como antes. Adicionar dias não rebalanceou fome nem criou escassez suficiente. Desconectados continuam com atributos congelados e recursos reservados; isso não é morte nem mochila abandonada. Personagem padrão, trechos escuros e geometria provisória do exterior impedem declarar qualidade comercial global.

Parecer

Não mudamos de gênero ou premissa, mas ainda não construímos o núcleo completo que a comprova. O próximo investimento deve tornar o bunker necessário, o exterior perigoso e a comunicação incompleta, mantendo a referência artística e o desempenho.

DEIROS DEV / 03 NOV 2026 / 07 / ENTREGA DE HOJE

Calendário de sobrevivência validado


## Calendário de sobrevivência validado


Versão 0.3.1. Relógio compartilhado calculado a partir do tempo do servidor. O host escolhe a duração no Data Asset; o cliente não define dias por relógio de parede nem envia uma transação para avançar o tempo. O HUD mostra dia e hora simulada sem revelar a posição, saúde ou mochila de colegas.

Preparação, coleta e carregamento não avançam o calendário. Ao fechar fisicamente a porta, começa o Dia 1 às 00:00. Quatro minutos reais equivalem a 24 h simuladas. Descansar ou abrir a mochila não pausa o mundo. Salvar captura segundos sobrevividos e duração do dia; carregar retoma desse ponto, sem cobrar tempo offline. O horário representa tempo de partida, não clima ou sol externo.

Teste nesta versão | Resultado

Processo de gravação encerrado | APROVADO

Processo de retomada encerrado | APROVADO

Coleta e fechamento físicos | APROVADO

Virada de dia | APROVADO

Tempo salvo preservado | APROVADO

Relógio retomado e avançando | APROVADO

Checkpoint válido | APROVADO

O ensaio de calendário passa pela coleta e fechamento reais. A duração do dia é reduzida a 8 s somente com duas flags de desenvolvimento, em slots de teste isolados. Isso exercita virada de dia sem esperar uma sessão longa. O teste em dois processos confirma o mesmo tempo/dia no host e cliente. Não é teste com dois humanos.

Captura do executável após retomar o checkpoint do ensaio acelerado. A duração normal continua quatro minutos; o ensaio não define balanceamento final.

Imagem: screenshots/clock_resumed.png

DEIROS DEV / 03 NOV 2026 / 08 / ACEITE DO GDD

O que os testes comprovam


## O que os testes comprovam


Teste | Leitura atual

T01 / T02 | Portas e concorrência têm evidências automatizadas. Conforto conjunto de quatro humanos continua pendente.

T03 | Consumo validado e mochila privada; falta provar o comportamento social de comer escondido em sessão humana.

T04 / T05 / T06 | Pendentes: voz, morte sem notificação global e rádio dependente de bateria.

T07 | Reconexão local sem duplicar inventário validada; identidade Steam/internet não certificadas.

T08 | Pendente: o comando do gerador ainda não altera os circuitos reais.

T09 | Há testes separados de coleta, estoque e retomada de IDs; o fluxo humano completo ainda precisa de sessão longa.

T10 | Conexões e solo testados; continuidade após mortes não existe como regra final.

T11 | Rotas, cápsulas e escada conferidas; ainda falta circulação espontânea de quatro humanos.

T12 | Retorno externo evita softlock; nenhuma missão final está implementada para testar sua recuperação.

T13 | Pendente conjunto completo de acessibilidade, remapeamento e microfone.

T14 | Amostras curtas no M2; não equivalem a benchmark Windows nem partida longa.

T15 | Pendente playtest social de 30-60 minutos sem intervenção de desenvolvedor.

03/11 / instância | Média | Frame p95 | Amostras

host | 49.88 FPS | 33.03 ms | 798

client | 48.43 FPS | 34.70 ms | 774

Duas janelas 960 x 540 no mesmo Apple M2 / 24 GB, aproximadamente 16 s, incluindo captura. A medição de 30/10 foi cerca de 62 FPS. A diferença não foi isolada em benchmark controlado, portanto não se atribui sua causa ao calendário nem se garante desempenho de uma sessão inteira.

Em 30/10, coleta: 25 verificações; regressões de persistência, estoque, reconexão e armário passaram. Nesta entrega esses sistemas foram reexecutados no novo pacote conforme os logs do manifesto de 03/11. A inicialização intermitente histórica do Mac continua um problema aberto; não foi declarada corrigida por uma execução bem-sucedida.

DEIROS DEV / 03 NOV 2026 / 09 / PRODUÇÃO

O que fazer a seguir para chegar ao MVP


## O que fazer a seguir para chegar ao MVP


Ordem | Trabalho concreto | Aceite para avançar

1. Infraestrutura | Gerador com combustível/reparo/circuitos; água e filtragem. Modelar os novos recursos antes de chamá-los de itens prontos. | Desligar muda luzes/dispositivos; falta de recurso tem alternativa, save e rede consistentes.

2. Partida acessível | Menu de nova campanha/retomada e lobby; padronizar armários; 12-20 tipos úteis. | Amigos entram e jogam sem console; nenhum recurso duplicado ou perdido na retomada.

3. Expedição mínima | Procedimento de antecâmara, rua e um prédio, lanterna/filtro, radiação e tratamento. | Grupo sai, coleta, se expõe e retorna com consequências.

4. Risco e informação | Um inimigo, arma improvisada e arma simples; morte/mochila; voz/rádio. | Explorador pode falhar sem revelar seu destino magicamente ao bunker.

5. Motivo para continuar | Três eventos, um minijogo real, objetivo e encerramento. | Sessão tem decisões, atividade social e resultado, sem item único que trave tudo.

6. Estabilização | Windows, duas máquinas, quatro humanos, controles, áudio e desempenho. | 30-60 min em solo/duo/trio/quarteto; corrigir bloqueadores antes de expandir conteúdo.

A ordem é técnica, não autorização para ampliar bairros ou declarar arte aprovada. Refinar novas zonas deve continuar com revisão visual. Sinuca, pingue-pongue, novas regiões, 50-80 tipos e outros finais ficam no backlog de lançamento, sem serem apagados do GDD.

Riscos para 30/01: volume grande de sistemas ainda ausentes, disponibilidade de equipe não medida, ausência de ambiente Windows validado e teste humano ainda não realizado. Antes das férias de 04/01, o ideal continua ser uma sessão integral; de 16 a 24/01, testes e correções; de 25 a 30/01, estabilização. São metas condicionais, não capacidade já demonstrada.

DEIROS DEV / 03 NOV 2026 / 10 / FONTES E LIMITES

Arquivos, evidências e revisão


## Arquivos, evidências e revisão


Documentos de referência

GDD: references/Condominio_13_GDD_Codex.md (427 linhas, relido integralmente). Planejamento: docs/MVP_TARGET_JANUARY_2027.md. Entregas anteriores: BLOCKOUT_REPORT, REFERENCE_ROOM_REPORT, OPEN_PLAN_REPORT, COLLECTION_ROUND_REPORT, PERSISTENCE_REPORT e COOP_RECONNECT_REPORT, na pasta docs/. Afirmações históricas são identificadas como tal; não representam novo teste humano.

Código conferido

BunkerNetwork.cpp: autoridade, portas, cama e placeholders de gerador/dardos/rádio. BunkerSurvival: atributos, mochila, consumo e HUD. BunkerReferenceCabinet: prateleiras e transações. BunkerPersistence / BunkerReconnect / BunkerSaveGame: checkpoints, identidade local e reconexão. BunkerRound: fases, fechamento, retorno e calendário. Todos em unreal/Condominio13/Source/Condominio13/.

Fontes de arte existentes

Blender: Bunker_Blockout_v001, Convivencia_Reference_v001, Bunker_OpenPlan_v001 e Bunker_CollectionRound_v001, em blender/. Painter: SM_Hero_Bed.spp, SM_Hero_Locker.spp e SM_Hero_BlastDoor.spp, em painter/. A fonte arquitetônica de planta aberta contém proxies fora da convivência; não é um arquivo mestre de todo móvel refinado da Unreal.

Pacote e testes desta entrega

Aplicativo: builds/Mac/Condominio13-MVP-0.3.1.app. Versão anterior preservada. Manifesto: logs/clock_delivery_manifest.json. Testes: clock_result.json, clock_round_*_result.json e clock_regressions.json. Captura: screenshots/clock_resumed.png. Scripts reproduzíveis em scripts/. Checkpoints pessoais e credenciais não são distribuídos no relatório.

O que este documento não certifica

Lançamento, aprovação comercial de arte, sessão humana completa, Windows, internet/Steam, microfone funcional ou desempenho garantido. Nenhuma porcentagem de conclusão é usada: faltam sistemas inteiros cujo custo não foi medido. A decisão criativa continua sua; este inventário permite confirmar a direção sem confundir intenção com execução.
