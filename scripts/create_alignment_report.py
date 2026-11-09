"""Production audit, explicit evidence dates and GDD comparison. Generate after runtime validation."""
from pathlib import Path
import json,hashlib,re
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
R=Path(__file__).resolve().parents[1];O=R/'output/pdf/Condominio13_Direcao_e_Producao_2026-11-03.pdf';O.parent.mkdir(parents=True,exist_ok=True)
clock=json.loads((R/'logs/clock_result.json').read_text());network=json.loads((R/'logs/round_network_result.json').read_text());reg=json.loads((R/'logs/clock_regressions.json').read_text())
assert clock['passed'] and network['passed'] and reg['passed']
for n,f in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,'/System/Library/Fonts/Supplemental/'+f))
W,H=A4;CW=W-88;C=colors.HexColor;ink=C('#21363A');teal=C('#276A64');muted=C('#607378');bg=C('#EFF4F2')
styles={k:ParagraphStyle(k,fontName='Bold' if k in ('title','h','head','k') else 'Body',fontSize=fs,leading=lead,textColor=col,spaceAfter=sp) for k,fs,lead,col,sp in [('title',23,28,ink,13),('h',12,16,teal,8),('body',10,14.3,ink,8),('small',8,11,muted,6),('cell',8.5,11.5,ink,0),('head',8.5,11.5,colors.white,0),('k',9,12,teal,8)]}
S=[];md=[]
def p(t,k='body'):
 S.append(Paragraph(t,styles[k]));md.append(t.replace('<b>','').replace('</b>','').replace('<br/>','\n'))
def page(n,title):
 if S:S.append(PageBreak())
 p('DEIROS DEV / 03 NOV 2026 / '+n,'k');p(title,'title');md.append('\n## '+title+'\n')
def h(t):p(t,'h')
def table(head,rows,fracs):
 d=[[Paragraph(escape(str(x)),styles['head']) for x in head]]+[[Paragraph(escape(str(x)),styles['cell']) for x in row] for row in rows]
 t=Table(d,colWidths=[CW*f for f in fracs],repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),teal),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,bg]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));S.append(t);S.append(Spacer(1,10));md.extend([' | '.join(map(str,head))]+[' | '.join(map(str,row)) for row in rows])
def img(name,caption):
 from PIL import Image as PIL
 f=R/name
 with PIL.open(f) as im:w,hh=im.size
 S.append(Image(str(f),width=CW*.84,height=CW*.84*hh/w));S.append(Spacer(1,7));p(caption,'small');md.append('Imagem: '+name)
page('01 / PARECER','Condomínio 13<br/>Direção e estado real')
p('<b>A ideia original foi preservada no projeto, mas ainda não foi comprovada como uma partida completa.</b> Existe uma base técnica de abrigo, itens físicos, necessidades, rede e coleta. Ainda falta o que faz essa base gerar histórias: escassez com decisões, expedição perigosa, comunicação limitada, consequências, eventos e um encerramento.')
p('O jogo não está pronto para lançamento. Este relatório compara o GDD v1.0 de 13/10, as mudanças autorizadas na conversa, o código atual e os registros locais. Não usa quantidade de arquivos ou scripts executados como medida de conclusão.')
h('O que avançou nesta entrega')
p('Ciclo de dias acelerados integrado ao modo de coleta: um dia equivale a quatro minutos reais por padrão; começa após o fechamento físico do abrigo, segue o relógio do host e continua ao abrir a mochila ou descansar. O checkpoint preserva o tempo sobrevivido; tempo com o jogo fechado não é consumido. Checkpoints anteriores deste mapa começam o calendário no Dia 1, sem trocar IDs ou apagar recursos.')
h('Meta vigente')
p('MVP interno em 30/01/2027; férias do criador de 04 a 15/01/2027. Essa meta substitui a antiga referência a lançamento em dezembro. Não é uma promessa de publicação na Steam. Não existe automação trabalhando durante férias nem capacidade de equipe medida neste relatório.')
p('Leitura: páginas 2-3 explicam o jogo; 4-5 inventariam os sistemas; 6 avalia fidelidade; 7 registra esta entrega; 8 apresenta os testes do GDD; 9 organiza os próximos passos; 10 lista fontes e limites.','small')
page('02 / VISÃO ORIGINAL','O jogo que você propôs')
p('Um a quatro sobreviventes dividem um abrigo de defesa civil sob o Mercado Aurora, em Santa Aurora, depois do Evento Cinza. O bunker é relativamente seguro, mas seus recursos acabam. O grupo precisa decidir como viver junto, quem sai, quem fica e quanto arriscar para voltar.')
p('O mistério envolve alas lacradas, registros contraditórios do desastre e a confiabilidade de um sinal de resgate. As saídas planejadas são resgate, veículo de fuga ou rota subterrânea; o MVP precisa de uma. A cadeia narrativa ainda não está implementada.','small')
table(['Pilar','Como deve aparecer na partida'],[
('Bunker protagonista','Conversar, descansar, trabalhar, cozinhar, tratar ferimentos, esconder e compartilhar itens em lugares reconhecíveis.'),('Informação limitada','Voz por distância e rádio condicionado a equipamento/bateria. O abrigo não recebe aviso mágico de morte do explorador.'),('Recursos materiais','Unidades físicas localizadas, com IDs e transações validadas pelo servidor. Mochila privada e armazenamento no mundo.'),('Risco com consequência','Ferimentos, exposição, perda de equipamento e morte naquela partida. Mochila recuperável em situação perigosa.'),('Histórias emergentes','Conflito surge de decisões e escassez; não existe traidor obrigatório nem tarefa linear constante.'),('Rejogabilidade e tom','Seed, eventos e recursos variam; suspense externo convive com humor e atividades sociais.')],[.27,.73])
p('A referência The Rain orienta atmosfera de abrigo habitado, escala e tensão; identidade, arquitetura, objetos e narrativa devem continuar próprios da Deiros Dev. O GDD pede semi-realismo coeso; seu pedido posterior elevou o acabamento da sala de referência. Isso precisa ser avaliado no jogo e compatível com o Mac de teste.','small')
page('03 / FLUXO','Como uma partida deve funcionar')
table(['Momento','Proposta do GDD','Situação atual'],[
('1. Preparar','Host, amigos, personagem, microfone, dificuldade e seed.','Conexão local e retomada; faltam lobby e configurações acessíveis.'),('2. Coletar','90 s, pegar recursos sob limites de mochila e voltar.','Jogável: avisos 30/15/5 e relógio do servidor.'),('3. Fechar','Porta física; quem fica fora enfrenta risco e alternativa de retorno.','Fechamento seguro e liberação manual. Perigo externo ainda ausente.'),('4. Viver','Consumir, dormir, organizar, manter energia e água, resolver crises.','Consumo, descanso, parte do armazenamento e calendário; infraestrutura incompleta.'),('5. Sair e voltar','Equipamento, antecâmara, rua/prédio, radiação e inimigo.','Não há expedição completa; abertura da porta não é sistema de expedição.'),('6. Concluir','Objetivo de resgate, fuga ou rota subterrânea; derrota e resumo.','Nenhuma rota com encerramento implementada.')],[.15,.44,.41])
h('Como testar hoje')
p('Abrir Jogar-Coleta-MVP.command; R inicia a coleta no host; WASD/mouse movem e olham; E interage; I abre a mochila, setas selecionam, U usa e G larga. F5 salva no host. F sai da cama. No armário de referência, E abre/pega e X guarda o item selecionado em um espaço livre, sem modal de estoque.')
p('Hospedar-Coleta-MVP.command e Entrar-Coleta-MVP.command permitem teste na mesma rede com IP. Os aplicativos precisam da mesma versão. Ainda faltam convites Steam e fluxo de internet validado. Depois da coleta o jogo continua como sandbox; o Dia 2 não dispara uma missão nem uma vitória automática.','small')
page('04 / INVENTÁRIO TÉCNICO','O que existe e seus limites')
table(['Sistema','Implementação e evidência','O que falta'],[
('Arquitetura','Bunker conectado, escala e colisões verificadas; fontes Blender/exports.','Conforto com quatro humanos, acabamento consistente e sinalização.'),('Planta aberta','Seis zonas comuns; dormitórios, banheiro, antecâmara e gerador isolados.','Biombo/organização da enfermaria, pequenos grupos e teste acústico.'),('Arte','Sala de referência PBR, kit de cama/armário/porta, três fontes Painter.','Arte final do bunker inteiro, exterior e personagens; LODs/orçamento amplo.'),('Portas e camas','Folhas móveis replicadas, colisão; cama ocupa jogador e recupera energia.','Animação corporal final, som/acessibilidade mais completos.'),('Itens','Cinco tipos físicos: água azul, comida, remédio, pilha e ferramenta. Mais 12 unidades na coleta.','MVP pede 12-20 tipos utilizáveis. Pilha/ferramenta ainda sem sistemas de destino completos.'),('Mochila e consumo','Espaços/peso, ID, comer/beber/curar e largar, validação no host.','Carregar grandes volumes, carrinho, empilhar, receitas e variantes.'),('Armazenamento','Armário de referência abre e expõe objetos; transações por slot e revisão.','Padronizar os contêineres legados; ainda existem fluxos de estoque com interface.')],[.19,.43,.38])
p('Não contar unidades como tipos: doze objetos adicionais não são doze itens diferentes. Ter um modelo de rádio, pilha, ferramenta ou gerador também não comprova sua mecânica final.','small')
page('05 / GAMEPLAY E REDE','O que é funcional e o que é demonstração')
table(['Sistema','Estado real','Pendência'],[
('Necessidades','Fome, sede, saúde e energia no host; atributos privados.','Radiação, doenças, ferimentos, balanceamento de sessão longa.'),('Tempo','Novo ciclo persistido e compartilhado; quatro minutos por dia.','Eventos por dia, pausa solo opcional e ajuste de dificuldade.'),('Coleta/retorno','90 s normais; fechamento físico e retorno manual mesmo exausto.','Variação de loot, rotas equivalentes para quatro e ameaça externa.'),('Save/reconexão','Cópias alternadas, checksum, validação e reserva de recursos desconectados.','Menu de campanhas, recuperação de perfil, Steam e testes de internet.'),('Rede','Listen server; quatro conexões em testes históricos com latência/perda.','Quatro humanos por 30-60 min; duas máquinas e transporte final.'),('Gerador','Somente alterna estado e exibe comando ligado/desligado.','Combustível, reparo e circuitos que mudam luzes/dispositivos de verdade.'),('Rádio/voz','Rádio exibe texto fixo.','Voz por proximidade, bateria, frequência, ruído, mute/PTT e privacidade.'),('Dardos/eventos','Dardos sorteiam pontuação; sem diretor de eventos.','Minijogo de habilidade e três eventos com seed/cooldown.'),('Expedição/final','Exterior inicial, sem ciclo completo.','IA, combate, morte/mochila, espectador restrito e vitória/derrota.')],[.19,.41,.40])
p('As ações das mãos são procedurais com gestos de alcance e consumo; observadores próximos podem enxergar ações relevantes. Ainda não são uma atuação corporal final ou um rig articulado dos dedos.','small')
page('06 / FIDELIDADE','Onde seguimos sua linha e onde há lacunas')
h('Mudanças autorizadas, sem perda de função')
p('O salão aberto substituiu a divisão original de convivência, cozinha, despensa, oficina, enfermaria e rádio. As funções continuam obrigatórias. Os quatro ambientes isolados foram confirmados por você. A garrafa azul e o acabamento menos enferrujado seguem suas correções. A meta é janeiro de 2027 para MVP, não lançamento comercial em dezembro.')
h('O maior risco de desvio')
p('Hoje o projeto oferece espaço, objetos e ferramentas de teste, mas ainda poucas razões para o grupo negociar, sair ou temer uma perda. Se a produção continuar apenas decorando salas, a fantasia de sobrevivência social não se confirma. É preciso conectar manutenção, consumo, expedição e consequências antes de ampliar o mapa.')
h('Diferenças que precisam ficar explícitas')
p('A liberação manual externa é uma solução provisória coerente com evitar softlock; ainda não oferece o alto risco prometido porque faltam ameaças. A escolha de começar o Dia 1 após fechar o abrigo é uma decisão de implementação para avaliação; o GDD não fixa esse instante. Checkpoints antigos começam esse calendário em zero porque não guardavam tempo anterior.')
p('Os atributos ainda caem por minuto real, como antes. Adicionar dias não rebalanceou fome nem criou escassez suficiente. Desconectados continuam com atributos congelados e recursos reservados; isso não é morte nem mochila abandonada. Personagem padrão, trechos escuros e geometria provisória do exterior impedem declarar qualidade comercial global.')
h('Parecer')
p('<b>Não mudamos de gênero ou premissa, mas ainda não construímos o núcleo completo que a comprova.</b> O próximo investimento deve tornar o bunker necessário, o exterior perigoso e a comunicação incompleta, mantendo a referência artística e o desempenho.')
page('07 / ENTREGA DE HOJE','Calendário de sobrevivência validado')
p('Versão 0.3.1. Relógio compartilhado calculado a partir do tempo do servidor. O host escolhe a duração no Data Asset; o cliente não define dias por relógio de parede nem envia uma transação para avançar o tempo. O HUD mostra dia e hora simulada sem revelar a posição, saúde ou mochila de colegas.')
p('Preparação, coleta e carregamento não avançam o calendário. Ao fechar fisicamente a porta, começa o Dia 1 às 00:00. Quatro minutos reais equivalem a 24 h simuladas. Descansar ou abrir a mochila não pausa o mundo. Salvar captura segundos sobrevividos e duração do dia; carregar retoma desse ponto, sem cobrar tempo offline. O horário representa tempo de partida, não clima ou sol externo.')
table(['Teste nesta versão','Resultado'],[({'seed_exit':'Processo de gravação encerrado','load_exit':'Processo de retomada encerrado','real_collection_and_closure':'Coleta e fechamento físicos','day_advanced':'Virada de dia','same_saved_elapsed':'Tempo salvo preservado','resumed_and_ticking':'Relógio retomado e avançando','valid_checkpoint':'Checkpoint válido'}[k],'APROVADO' if v else 'FALHOU') for k,v in clock['checks'].items()],[.76,.24])
p('O ensaio de calendário passa pela coleta e fechamento reais. A duração do dia é reduzida a 8 s somente com duas flags de desenvolvimento, em slots de teste isolados. Isso exercita virada de dia sem esperar uma sessão longa. O teste em dois processos confirma o mesmo tempo/dia no host e cliente. Não é teste com dois humanos.','small')
img('screenshots/clock_resumed.png','Captura do executável após retomar o checkpoint do ensaio acelerado. A duração normal continua quatro minutos; o ensaio não define balanceamento final.')
page('08 / ACEITE DO GDD','O que os testes comprovam')
table(['Teste','Leitura atual'],[
('T01 / T02','Portas e concorrência têm evidências automatizadas. Conforto conjunto de quatro humanos continua pendente.'),('T03','Consumo validado e mochila privada; falta provar o comportamento social de comer escondido em sessão humana.'),('T04 / T05 / T06','Pendentes: voz, morte sem notificação global e rádio dependente de bateria.'),('T07','Reconexão local sem duplicar inventário validada; identidade Steam/internet não certificadas.'),('T08','Pendente: o comando do gerador ainda não altera os circuitos reais.'),('T09','Há testes separados de coleta, estoque e retomada de IDs; o fluxo humano completo ainda precisa de sessão longa.'),('T10','Conexões e solo testados; continuidade após mortes não existe como regra final.'),('T11','Rotas, cápsulas e escada conferidas; ainda falta circulação espontânea de quatro humanos.'),('T12','Retorno externo evita softlock; nenhuma missão final está implementada para testar sua recuperação.'),('T13','Pendente conjunto completo de acessibilidade, remapeamento e microfone.'),('T14','Amostras curtas no M2; não equivalem a benchmark Windows nem partida longa.'),('T15','Pendente playtest social de 30-60 minutos sem intervenção de desenvolvedor.')],[.23,.77])
fps=[]
for role in ('host','client'):
 m=re.search(r'C13_ROUND_FPS role=\w+ samples=(\d+) fps=([\d.]+) p95_ms=([\d.]+)',(R/f'logs/round_network_{role}.log').read_text(errors='replace'))
 assert m;fps.append((role,m[2]+' FPS',m[3]+' ms',m[1]))
table(['03/11 / instância','Média','Frame p95','Amostras'],fps,[.34,.23,.23,.20])
p('Duas janelas 960 x 540 no mesmo Apple M2 / 24 GB, aproximadamente 16 s, incluindo captura. A medição de 30/10 foi cerca de 62 FPS. A diferença não foi isolada em benchmark controlado, portanto não se atribui sua causa ao calendário nem se garante desempenho de uma sessão inteira.','small')
p('Em 30/10, coleta: 25 verificações; regressões de persistência, estoque, reconexão e armário passaram. Nesta entrega esses sistemas foram reexecutados no novo pacote conforme os logs do manifesto de 03/11. A inicialização intermitente histórica do Mac continua um problema aberto; não foi declarada corrigida por uma execução bem-sucedida.','small')
page('09 / PRODUÇÃO','O que fazer a seguir para chegar ao MVP')
table(['Ordem','Trabalho concreto','Aceite para avançar'],[
('1. Infraestrutura','Gerador com combustível/reparo/circuitos; água e filtragem. Modelar os novos recursos antes de chamá-los de itens prontos.','Desligar muda luzes/dispositivos; falta de recurso tem alternativa, save e rede consistentes.'),('2. Partida acessível','Menu de nova campanha/retomada e lobby; padronizar armários; 12-20 tipos úteis.','Amigos entram e jogam sem console; nenhum recurso duplicado ou perdido na retomada.'),('3. Expedição mínima','Procedimento de antecâmara, rua e um prédio, lanterna/filtro, radiação e tratamento.','Grupo sai, coleta, se expõe e retorna com consequências.'),('4. Risco e informação','Um inimigo, arma improvisada e arma simples; morte/mochila; voz/rádio.','Explorador pode falhar sem revelar seu destino magicamente ao bunker.'),('5. Motivo para continuar','Três eventos, um minijogo real, objetivo e encerramento.','Sessão tem decisões, atividade social e resultado, sem item único que trave tudo.'),('6. Estabilização','Windows, duas máquinas, quatro humanos, controles, áudio e desempenho.','30-60 min em solo/duo/trio/quarteto; corrigir bloqueadores antes de expandir conteúdo.')],[.19,.43,.38])
p('A ordem é técnica, não autorização para ampliar bairros ou declarar arte aprovada. Refinar novas zonas deve continuar com revisão visual. Sinuca, pingue-pongue, novas regiões, 50-80 tipos e outros finais ficam no backlog de lançamento, sem serem apagados do GDD.','small')
p('Riscos para 30/01: volume grande de sistemas ainda ausentes, disponibilidade de equipe não medida, ausência de ambiente Windows validado e teste humano ainda não realizado. Antes das férias de 04/01, o ideal continua ser uma sessão integral; de 16 a 24/01, testes e correções; de 25 a 30/01, estabilização. São metas condicionais, não capacidade já demonstrada.','small')
page('10 / FONTES E LIMITES','Arquivos, evidências e revisão')
h('Documentos de referência')
p('GDD: references/Condominio_13_GDD_Codex.md (427 linhas, relido integralmente). Planejamento: docs/MVP_TARGET_JANUARY_2027.md. Entregas anteriores: BLOCKOUT_REPORT, REFERENCE_ROOM_REPORT, OPEN_PLAN_REPORT, COLLECTION_ROUND_REPORT, PERSISTENCE_REPORT e COOP_RECONNECT_REPORT, na pasta docs/. Afirmações históricas são identificadas como tal; não representam novo teste humano.')
h('Código conferido')
p('BunkerNetwork.cpp: autoridade, portas, cama e placeholders de gerador/dardos/rádio. BunkerSurvival: atributos, mochila, consumo e HUD. BunkerReferenceCabinet: prateleiras e transações. BunkerPersistence / BunkerReconnect / BunkerSaveGame: checkpoints, identidade local e reconexão. BunkerRound: fases, fechamento, retorno e calendário. Todos em unreal/Condominio13/Source/Condominio13/.')
h('Fontes de arte existentes')
p('Blender: Bunker_Blockout_v001, Convivencia_Reference_v001, Bunker_OpenPlan_v001 e Bunker_CollectionRound_v001, em blender/. Painter: SM_Hero_Bed.spp, SM_Hero_Locker.spp e SM_Hero_BlastDoor.spp, em painter/. A fonte arquitetônica de planta aberta contém proxies fora da convivência; não é um arquivo mestre de todo móvel refinado da Unreal.')
h('Pacote e testes desta entrega')
p('Aplicativo: builds/Mac/Condominio13-MVP-0.3.1.app. Versão anterior preservada. Manifesto: logs/clock_delivery_manifest.json. Testes: clock_result.json, clock_round_*_result.json e clock_regressions.json. Captura: screenshots/clock_resumed.png. Scripts reproduzíveis em scripts/. Checkpoints pessoais e credenciais não são distribuídos no relatório.')
h('O que este documento não certifica')
p('Lançamento, aprovação comercial de arte, sessão humana completa, Windows, internet/Steam, microfone funcional ou desempenho garantido. Nenhuma porcentagem de conclusão é usada: faltam sistemas inteiros cujo custo não foi medido. A decisão criativa continua sua; este inventário permite confirmar a direção sem confundir intenção com execução.')
def footer(c,doc):
 c.setStrokeColor(C('#CDDAD7'));c.line(44,40,W-44,40);c.setFont('Body',8);c.setFillColor(muted);c.drawString(44,27,'CONDOMÍNIO 13  |  AUDITORIA DE PRODUÇÃO  |  03/11/2026');c.drawRightString(W-44,27,str(doc.page))
SimpleDocTemplate(str(O),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=42,bottomMargin=54,title='Condomínio 13 - Direção e produção',author='Deiros Dev').build(S,onFirstPage=footer,onLaterPages=footer)
(R/'docs/DIRECTION_AND_PRODUCTION_2026-11-03.md').write_text('\n\n'.join(md)+'\n')
print(O)
