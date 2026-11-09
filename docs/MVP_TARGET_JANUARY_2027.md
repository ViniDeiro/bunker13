# Condomínio 13 — MVP interno até 30 de janeiro de 2027

Atualizado em 29/10/2026. Substitui a meta histórica de lançamento em dezembro como referência de calendário. A meta atual é uma base jogável completa para teste, não o lançamento comercial na Steam. Férias do criador: 04–15/01/2027. Datas são metas de trabalho e dependem de capacidade, testes humanos e disponibilidade de Windows; não são garantia de entrega.

## Direção aprovada nesta conversa

O bunker passa a ter um grande espaço comum: convivência, cozinha, despensa, oficina, enfermaria e rádio/comando são zonas de um mesmo salão. Dormitório, banheiro, antecâmara e gerador continuam fechados. A convivência de 22/10 é a referência visual aprovada para continuidade, com limitações ainda registradas no relatório anterior. A mudança de planta foi autorizada pelo criador e substitui a separação original dessas seis salas no GDD; suas funções continuam obrigatórias.

Não transformar tudo em um hangar vazio: delimitar usos com mobiliário, tapetes de manutenção, bancadas, luz e pequenos anteparos, preservando a sensação de abrigo de defesa civil. Manter apoios para conversar em pequenos grupos, guardar recursos fora da vista e descansar. Privacidade acústica e pontos de cochicho precisam de playtest quando houver voz; planta aberta não resolve essa regra sozinha. A enfermaria poderá usar um biombo parcial, sem virar um novo quarto.

## O que a base de janeiro precisa permitir

Uma sessão de 1–4 pessoas com início, decisões de sobrevivência, uma saída perigosa e um encerramento. O recorte continua o MVP do GDD: bunker + supermercado + estacionamento/rua + um prédio explorável, sem cinco bairros novos.

| Parte | Critério de saída |
|---|---|
| Entrar e retomar | Host e até três participantes; entrada permitida antes do fechamento, reconexão do mesmo participante, mochila intacta e saída do host com checkpoint consistente. Identidade de teste local não é autenticação Steam. |
| Coleta inicial | Temporizador do servidor, referência de 90 s, avisos em 30/15/5 s, limite de peso/espaços e procedimento de fechamento. Quem ficar fora tem alternativa difícil de entrada; não morre automaticamente. |
| Viver no abrigo | Comer, beber, descansar, guardar/retirar fisicamente, passar tempo, operar rádio e manter energia. Dia acelerado e parâmetros editáveis. Necessidades e itens validados pelo host. |
| Recursos | 12–20 tipos realmente utilizáveis, IDs estáveis, efeitos e pesos configuráveis, nenhuma duplicação em concorrência/reconexão. Modelos reais para os objetos, não apenas nomes. |
| Infraestrutura | Combustível, reparo e falha do gerador alteram luzes e dispositivos; filtragem/ventilação e tratamentos mínimos de contaminação têm consequências jogáveis. |
| Expedição | Antecâmara, lanterna/proteção/filtro, radiação e tratamento; um inimigo com patrulha, investigação, perseguição, ataque e perda de alvo. Uma arma improvisada e uma arma de fogo simples. |
| Informação e morte | Voz por proximidade em teste, rádio dependente de bateria/equipamento; bunker não recebe aviso global de morte. Morte naquela partida, mochila recuperável e espectador restrito. |
| Vida social | Um minijogo de habilidade em rede, substituindo o resultado aleatório atual; três eventos sistêmicos com seed/cooldown. Eventos não podem bloquear a partida por perda de um único item. |
| Encerramento | Um objetivo completo com vitória/derrota, alternativa para item crítico perdido e resumo final. As outras rotas narrativas continuam backlog do GDD. |
| Usabilidade | Sensibilidade, volume, legendas relevantes, remapeamento e controles claros de microfone/mute. Medir FOV e conforto em playtest. |
| Entrega | Executável Windows testado no hardware-alvo e Mac de avaliação, fontes salvas, instruções para entrar em rede e lista honesta de pendências. Convites Steam e lançamento comercial não são automaticamente prometidos para esta base. |

## Sequência com datas-alvo

| Período | Trabalho e entrega revisável | Gate |
|---|---|---|
| 29/10–08/11 | Planta aberta comparável à atual; circulação, zonas de uso e orientação. Corrigir estabilidade de inicialização e confirmar orçamento visual do salão. | Avaliação visual do criador e percurso real antes de detalhar as outras zonas. |
| 09–22/11 | Concluir base de rede acessível, padronizar armários físicos e ações; parâmetros de tempo/necessidades; ampliar itens concretos. | Quatro conexões, concorrência sem duplicação, saves antigos preservados ou migração explícita testada. |
| 23/11–06/12 | Coleta de 90 s, fechamento/entrada alternativa, gerador e circuitos, combustível, água/filtragem. | Fluxo supermercado → bunker → consumo → manutenção → salvar/retomar. |
| 07–20/12 | Rua + um prédio, inimigo, combate mínimo, radiação, morte/mochila, voz e rádio. | Expedição completa com retorno e perda de comunicação; teste em duas máquinas. |
| 21/12–03/01 | Três eventos, um minijogo, objetivo e encerramento; prévia integral antes das férias. | Uma sessão inteira jogável; escolher problemas bloqueadores e congelar conteúdo. |
| 04–15/01 | Férias do criador. Janela para equipe corrigir bugs previamente acordados, documentar e preparar builds; nenhuma decisão visual crítica deve depender da presença dele. | Se não houver equipe disponível, este intervalo não conta como capacidade produtiva. Não foi criado agendamento automático de trabalho. |
| 16–24/01 | Playtests com quatro humanos, 30–60 min, solo/duo/trio, latência/perda, Windows e conforto. | Gravar problemas, medir recursos/FPS e repetir os cenários corrigidos. |
| 25–30/01 | Estabilização e pacote do MVP; nenhuma zona ou sistema novo. | Critérios abaixo aprovados; se algum falhar, registrar o MVP como incompleto. |

## Aceite: reutilizar T01–T15 do GDD

- T01–T03, T07 e T09: estado comum de portas/estoques, retirada concorrente, consumo sem revelar autor, reconexão e persistência. Rodadas automatizadas ajudam, mas não substituem teste humano.
- T04–T06: voz deixa de ser ouvida fora do alcance, rádio exige bateria e morte não gera aviso global.
- T08: desligar gerador muda os dispositivos dependentes; não apenas uma mensagem.
- T10–T12: partida viável com menos sobreviventes, circulação conjunta e recuperação de missão sem softlock.
- T13: controles de microfone, legendas e remapeamento funcionam na build entregue.
- T14: FPS/frame p95 e latência nas máquinas-alvo; janela curta no M2 não certifica sessão longa ou Windows.
- T15: quatro amigos jogam 30–60 minutos e tomam decisões sociais sem intervenção do desenvolvedor.

## Riscos que precisam de decisão cedo

1. Não há disponibilidade de equipe medida. A sequência inclui trabalho grande ainda inexistente: inimigo, combate, expedição, voz, eventos, minijogo e encerramento. Reavaliar a previsão em cada gate, sem remover requisitos em silêncio.
2. Windows requer ambiente Windows e pelo menos uma máquina de teste disponibilizada antes de dezembro. O Mac não prova uma build Windows.
3. A inicialização intermitente com sinal 11 registrada em 22/10 ainda é problema aberto; passar uma repetição não é correção.
4. O salão aumenta visibilidade, luzes e custo de renderização. Precisamos medir o espaço aberto no executável e manter iluminação econômica; não aumentar o mapa para simular amplitude.
5. Mãos e ações continuam procedurais. Melhorar contato e leitura antes de investir em dezenas de animações; qualidade final precisa de avaliação em movimento.
6. A planta alternativa tem outro nome de mapa e não carrega checkpoints da campanha anterior. O lançador de avaliação desabilita saves; uma promoção futura exige migração explícita, nunca renomear o mapa sobre a campanha.

O GDD continua como backlog completo. Sinuca, pingue-pongue, novos bairros, múltiplos finais e conteúdo de lançamento não foram apagados nem apresentados como prontos.
