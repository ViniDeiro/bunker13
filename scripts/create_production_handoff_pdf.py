from pathlib import Path
import json, hashlib
from xml.sax.saxutils import escape
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf/Condominio_13_Relatorio_Producao_e_Logica_2026-10-21.pdf'
for name,file in [('Arial','Arial.ttf'),('Arial-Bold','Arial Bold.ttf'),('Arial-Italic','Arial Italic.ttf')]:
 pdfmetrics.registerFont(TTFont(name,'/System/Library/Fonts/Supplemental/'+file))
C=colors.HexColor
NAVY=C('#18383D');TEAL=C('#347B76');INK=C('#23363A');MUTED=C('#627377');PALE=C('#F0F4F2');GOLD=C('#AC7044')
W,H=A4; LEFT=45; RIGHT=45; WIDTH=W-LEFT-RIGHT
styles={
 'body':ParagraphStyle('Body',fontName='Arial',fontSize=10.5,leading=15.5,spaceAfter=7,textColor=INK),
 'small':ParagraphStyle('Small',fontName='Arial',fontSize=8.5,leading=11.5,spaceAfter=6,textColor=MUTED),
 'title':ParagraphStyle('Title',fontName='Arial-Bold',fontSize=23,leading=27,spaceAfter=14,textColor=NAVY),
 'h2':ParagraphStyle('H2',fontName='Arial-Bold',fontSize=12,leading=15,spaceBefore=10,spaceAfter=6,textColor=TEAL,keepWithNext=True),
 'kicker':ParagraphStyle('Kicker',fontName='Arial-Bold',fontSize=8.5,leading=12,spaceAfter=7,textColor=GOLD),
 'cell':ParagraphStyle('Cell',fontName='Arial',fontSize=9.1,leading=12.7,spaceAfter=0,textColor=INK),
 'thead':ParagraphStyle('Thead',fontName='Arial-Bold',fontSize=8.5,leading=11,textColor=colors.white),
 'callout':ParagraphStyle('Callout',fontName='Arial-Bold',fontSize=10.5,leading=15,textColor=NAVY),
}
PAGES=[]
def page(kicker,title):
 d={'kicker':kicker,'title':title,'blocks':[]};PAGES.append(d);return d

def p(d,text):d['blocks'].append({'type':'p','text':text})
def h(d,text):d['blocks'].append({'type':'h','text':text})
def b(d,text):d['blocks'].append({'type':'p','text':'- '+text})
def note(d,text):d['blocks'].append({'type':'note','text':text})
def table(d,heads,rows,widths):d['blocks'].append({'type':'table','heads':heads,'rows':rows,'widths':widths})
def img(d,path,caption,width=WIDTH):d['blocks'].append({'type':'image','path':path,'caption':caption,'width':width})

x=page('01 / PARECER EXECUTIVO','Condomínio 13\nEstado real e plano de conclusão')
p(x,'<b>Deiros Dev | 21 de outubro de 2026 | Relatório para reunião com desenvolvimento</b>')
note(x,'Existe uma base técnica jogável. Ainda não existe uma partida completa nem uma versão aprovada para lançamento.')
h(x,'O que já foi construído')
p(x,'Bunker navegável na Unreal, arquitetura e mobiliário de base, portas móveis, quatro camas utilizáveis, cinco tipos de itens 3D, mochila, consumo, necessidades, seis estoques, checkpoints e reconexão local. Há executável Mac de desenvolvimento e evidências automatizadas. [S02-S08]')
h(x,'O que sua crítica muda na prioridade')
p(x,'A apresentação ainda não transmite a credibilidade e a qualidade desejadas. Ferrugem, materiais e formas não bastam para dar realismo. A interação de armários por tela não atende à nova orientação: abrir a porta, enxergar os objetos e pegá-los diretamente. Essa orientação foi registrada como requisito de revisão; <b>não foi implementada durante a elaboração deste relatório</b>.')
h(x,'O que impede chamar o jogo de pronto')
p(x,'Faltam início e fim de partida, expedições com risco, inimigos/combate/morte, infraestrutura funcional, minijogos de habilidade, eventos, arte final, áudio, lobby, voz/Steam e validação Windows. A meta é dezembro de 2026, sem dia definido e sem capacidade de entrega da equipe medida. Não há base para garantir essa data. [S01, S09]')
h(x,'Como ler este documento')
p(x,'<b>Existente:</b> implementação encontrada no projeto. <b>Validado em cenário:</b> há relatório de teste, com limites explícitos. <b>Provisório:</b> funciona parcialmente ou apenas como representação. <b>Pendente:</b> requisito sem entrega concluída. <b>Proposta:</b> decisão técnica recomendada, ainda não implementada nem aprovada como regra final.')
p(x,'O GDD define o produto; as propostas abaixo explicam como implementá-lo. A nova orientação do criador sobre interação física prevalece sobre a solução provisória de modal. Não se usa uma porcentagem artificial de conclusão: os sistemas têm pesos e riscos muito diferentes.')

x=page('02 / INVENTÁRIO DA ENTREGA','O que foi feito e o que ainda não é final')
table(x,['Área','Estado confirmado','Limite atual'],[
 ['Bunker e exterior','Base navegável e exterior inicial','Grande parte da composição e dos props ainda é de protótipo.'],
 ['Portas','13 folhas com dobradiça, movimento gradual, colisão e replicação','Ferragens, acabamento, interação da mão e som não estão finalizados.'],
 ['Camas','Quatro pontos de descanso; ocupação exclusiva e recuperação de energia','Entrada reposiciona o personagem; falta uma sequência corporal convincente.'],
 ['Armários','Seis contêineres; transferências autoritativas e capacidade','Modal de duas listas; sem porta animada ou objetos internos visíveis.'],
 ['Itens 3D','Água azul, lata, kit médico, pilha e chave; seis pickups no mapa','Pilha e ferramenta ainda não têm seus sistemas finais de uso.'],
 ['Mochila e consumo','IDs, peso, espaços, usar, largar e recolher','Faltam empilhamento, quantidades/durabilidade completas e manuseio final.'],
 ['Mãos','Gestos locais de coleta, beber, comer e curativo','Pegadas rígidas/procedurais; sem dedos articulados e atuação para terceiros.'],
 ['Necessidades','Saúde, alimentação, hidratação, energia e descanso','Faltam doenças, radiação, ferimentos e balanceamento de uma sessão completa.'],
 ['Persistência','Solo e host; reserva e retorno dos perfis remotos','Perfis locais; sem conta Steam, recuperação amigável ou migração de layouts.'],
 ['Gerador / rádio','Comando liga/desliga e mensagens demonstrativas','Sem combustível/circuitos ou comunicação de voz funcional.'],
 ['Minijogos','Dardos com resultado aleatório ao interagir','Nenhum minijogo de habilidade concluído; cartas não implementadas.'],
 ['Partida e lançamento','Executável Mac Development','Sem loop completo, aprovação Windows ou candidatura a lançamento.'],
 ],[.19,.40,.41])
p(x,'Base: código e relatórios locais [S02-S08]. O avanço técnico não equivale a aprovação visual. Relatórios antigos descrevem marcos históricos; a persistência posterior substitui as antigas notas de que o estoque só durava durante a sessão.',)

x=page('03 / DIREÇÃO VISUAL','Credibilidade material, não ferrugem uniforme')
img(x,'screenshots/persistence_water_hud.png','Captura existente do executável, marco de 21/10. Evidência do aspecto atual; não é uma proposta de arte final.',WIDTH)
p(x,'Na captura há superfícies muito claras, repetição evidente de textura, recortes geométricos simples e contraste de luz que reduz a leitura dos materiais. Essa leitura visual se soma ao seu relato de desgaste/ferrugem pouco convincente. Não houve nova sessão de avaliação jogável nesta revisão documental.')
h(x,'Direção recomendada para aprovação artística')
b(x,'Defesa civil subterrânea habitável: concreto, aço pintado, borracha, vidro, tecido e madeira com respostas materiais distintas. Ferrugem localizada em juntas, vazamentos e bordas expostas; áreas de contato podem estar polidas pelo uso.')
b(x,'Consertar proporções, espessuras, encaixes, dobradiças, parafusos, juntas e bordas antes de aumentar a resolução das texturas. Evitar usar uma única porta pesada esticada para todos os vãos.')
b(x,'Revisar roughness, metalness, normais, escala de textura, exposição e sombras no executável. Luz quente nas áreas sociais e mais fria nas técnicas, sem apagar detalhes nem estourar superfícies.')
p(x,'<b>Decisão de direção:</b> o GDD pede 3D estilizado semi-realista, e você quer maior realismo percebido. Recomenda-se elevar materiais, iluminação e fabricação sem presumir uma mudança para fotorealismo custoso. The Rain é referência de atmosfera; a identidade, os layouts e os assets devem continuar originais. [S01, seção 12]')

x=page('04 / INTERAÇÃO FÍSICA','Portas e armários: experiência desejada')
img(x,'screenshots/storage_2.png','Estado atual: E abre uma interface de estoque sobre o armário fechado. Captura de teste existente; não representa a interação solicitada.',WIDTH*.86)
h(x,'Portas: já há uma base de movimento')
p(x,'O código atual recebe E, valida o jogador e interpola o ângulo da folha. Não é apenas uma troca instantânea de estado. Porém isso não entrega, sozinho, a experiência convincente que você descreve. É preciso reproduzir seu caso no executável e revisar pivô, sentido, velocidade/curva, ferragens, contato da mão e áudio. [S04]')
h(x,'Armários: mudança funcional necessária')
p(x,'<b>E no puxador:</b> a porta abre fisicamente. <b>Olhar para dentro:</b> os objetos aparecem em prateleiras reais. <b>E no objeto:</b> pega aquela unidade. <b>Guardar:</b> coloca o item carregado em uma posição interna válida. A câmera permanece no jogo; não surge modal de estoque.')
h(x,'Cama e demais ações')
p(x,'Preservar a reserva exclusiva e a saída segura da cama, acrescentando transições de deitar/levantar e postura visível aos colegas. Nas portas, impedir atravessamento e esmagamento; no armário, nunca permitir pegar através da folha fechada. A interface pessoal da mochila é uma decisão separada: a retirada do modal do armário não exige removê-la automaticamente.')

x=page('05 / ESPECIFICAÇÃO PARA PROGRAMAR','Armário físico sem perder consistência')
h(x,'Contrato de apresentação - proposta')
p(x,'Separar carcaça, folha, dobradiça, puxador e prateleiras no Blender. Usar estados Fechado, Abrindo, Aberto, Fechando e Bloqueado. O servidor aceita a intenção de abrir/fechar; cada cliente reproduz o movimento. Itens ficam visualmente apoiados, sem centenas de corpos rígidos em rede.')
h(x,'Contrato de dados - reaproveitar a base existente')
p(x,'Cada unidade continua com ID único. Acrescentar posições internas estáveis: ContainerId + SlotId + ItemId. A malha mostrada na prateleira é a representação do item registrado no contêiner, não uma segunda unidade independente. A lista atual muda de índice ao remover itens; portanto o índice do array não deve virar a identidade do slot.')
table(x,['Ação','Validação no host','Resultado único'],[
 ['Abrir','Distância, visada, estado e área de movimento','Estado/tempo de abertura autorizado; observadores elegíveis atualizados.'],
 ['Retirar','Porta suficientemente aberta, slot/ID/revisão, visada e mochila com espaço/peso','Uma transação move contêiner para jogador; representação some uma vez.'],
 ['Guardar','Item do jogador, slot livre, capacidade e área acessível','Uma transação move jogador para contêiner; representação aparece no slot.'],
 ['Disputa / queda','Versão obsoleta ou pedido repetido não reaplica a transferência','Atualizar observadores, revogar acesso e preservar o mesmo ID.'],
 ],[.17,.44,.39])
h(x,'Visibilidade, colisão e salvamento')
p(x,'Adaptar os snapshots privados existentes para observadores próximos com visão do interior aberto, não para um inventário global. Se as malhas forem locais, o host ainda precisa de volumes de consulta dos slots para validar o raio de interação. A porta deve ocultar e bloquear o acesso fechado. Salvar conteúdo, posição lógica, estado de abertura e capacidade; planejar migração dos checkpoints anteriores. [S03, S06]')
note(x,'Aceite: dois jogadores veem o mesmo armário aberto; disputam uma lata e apenas um a recebe; fechá-lo bloqueia a coleta; sair/reconectar e salvar/carregar não duplica nem reorganiza recursos arbitrariamente. Sem modal.')

x=page('06 / LÓGICA DA PARTIDA','O ciclo que o jogo precisa completar')
p(x,'A estrutura vem do GDD [S01, seções 3 e 9]. A organização em estados abaixo é uma proposta técnica para implementá-la; não descreve uma partida já existente.')
table(x,['Estado','Acontecimento e transição'],[
 ['1. Lobby','Host define dificuldade/seed e entrada tardia; participantes configuram personagem, controles e microfone. Início autorizado pelo host.'],
 ['2. Coleta inicial','Supermercado com rotas alternativas e itens distribuídos. Referência: 90 segundos, ajustável entre 60 e 120. Avisos aos 30, 15 e 5 segundos.'],
 ['3. Fechamento','Abrigo encerra acesso normal. Quem ficou fora enfrenta risco e busca alternativa; não morre automaticamente pelo cronômetro.'],
 ['4. Vida no bunker','Guardar e compartilhar recursos, comer, descansar, reparar, conversar e jogar. Tempo e necessidades continuam avançando.'],
 ['5. Preparar expedição','Escolher pessoas, objetivo e equipamento. Executar procedimento físico de antecâmara. Parte do grupo pode ficar no bunker.'],
 ['6. Explorar e retornar','Buscar suprimentos/pistas, enfrentar exposição e ameaças, administrar peso, bateria e retorno. O bunker não conhece magicamente o destino de quem saiu.'],
 ['7. Consequências','Descontaminar, tratar, depositar recursos, lidar com perdas e eventos. Voltar ao estado 4, abrir novos objetivos ou encerrar.'],
 ['8. Vitória / derrota','Objetivo e fuga/resgate, ou ausência de sobreviventes/abrigo viável. Exibir resumo conforme as regras de informação do GDD.'],
 ],[.25,.75])
h(x,'Invariantes para todas as fases')
p(x,'O host controla relógios, regras e mudanças de estado. A semente precisa ser persistida; somente o host sorteia eventos. Pausa é opcional no solo, não no cooperativo. A entrada de pessoas novas deve encerrar no ponto configurado; reconexão de participantes existentes continua possível.')
p(x,'O dia acelerado de 4 minutos é um parâmetro inicial do GDD, não um valor final aprovado. Não concluir balanceamento antes de sessões completas de 60-120 minutos. Missões críticas precisam de alternativa se um item essencial se perder.')

x=page('07 / SOBREVIVÊNCIA E CAUSALIDADE','Necessidades devem alimentar decisões')
table(x,['Sistema','Base atual','Comportamento a concluir'],[
 ['Saúde / necessidades','Saúde, alimentação, água e energia em 0-100; consumo e descanso','Esforço, sintomas, ferimentos, doença, radiação, incapacitação/morte e equilíbrio solo/duo/grupo.'],
 ['Comida e água','Usar água/lata remove uma unidade e aplica efeito do host','Perecíveis, água contaminada, filtragem, reservatório, conservação e risco de intoxicação.'],
 ['Gerador','Alterna comando ligado/desligado','Combustível, condição, reparo, produção de energia, circuitos e dependências.'],
 ['Dispositivos','Modelos e pontos demonstrativos','Iluminação, rádio, geladeira, ventilação e purificação devem reagir à energia disponível.'],
 ['Ferramentas / pilhas','Dois modelos com peso e transporte','Compatibilidade de bateria, carga, desgaste e uso em reparos/equipamentos.'],
 ['Estoque','IDs, peso/espaços e transferência persistente','Slots físicos, empilhar quando permitido, quantidades/durabilidade e contêineres com permissões configuráveis.'],
 ],[.21,.32,.47])
h(x,'Cadeia de exemplo - proposta de implementação')
p(x,'Combustível baixo leva a queda de energia; a refrigeração para e alimentos começam a perder conservação; o rádio deixa de operar; o grupo escolhe economizar, reparar ou enviar alguém ao posto. A falha precisa criar alternativas, não desligar todas as ações e bloquear a partida.')
h(x,'Dados e regras')
p(x,'Manter taxas e efeitos em Data Assets/Data Tables. Cada transação confirma item, quantidade, capacidade e estado antes de aplicar consumo ou reparo. Salvar também condição de equipamento, exposição e temporizadores quando esses sistemas existirem. As taxas atuais não são balanceamento final. [S01, S05]')
p(x,'<b>Separar relógios:</b> animação local apresenta a ação; o host decide o resultado e impede repetição. Se o item foi consumido antes de interromper o gesto, a regra de cancelamento deve ser consistente e comunicada. O comportamento atual aplica o efeito ao aceitar a ação; mudar isso exige uma transação de uso com cancelamento explícito.')

x=page('08 / EXPLORAÇÃO, AMEAÇA E DESFECHO','Dar motivos para sair e querer voltar')
h(x,'Expedição - ainda pendente como loop completo')
p(x,'Concluir primeiro supermercado, estacionamento/rua e um prédio explorável, com caminhos e recursos diferentes. A expansão para bairro, clínica, posto, depósito e mata/estrada é conteúdo posterior do GDD, não o estado atual do mapa. O exterior inicial não comprova que essas zonas estejam jogáveis.')
p(x,'Equipamentos precisam existir e funcionar: mochila, lanterna, rádio, pilhas, filtro, proteção e armas. A antecâmara coordena portas interna/externa, ventilação e descontaminação. O grupo deve poder deixar pessoas trabalhando no bunker enquanto os demais exploram.')
h(x,'Combate e IA previstos no GDD')
b(x,'Primeiro recorte: um inimigo contaminado, uma arma improvisada corpo a corpo e uma arma de fogo simples; fogo amigo desligado no MVP.')
b(x,'IA: patrulhar, investigar ruído, perseguir, atacar, perder o alvo e retornar. Dano, munição e durabilidade são decididos pelo host; ruído pode atrair outras ameaças. Furtividade deve ser uma alternativa.')
h(x,'Morte e informação')
p(x,'A morte é permanente naquela partida. Uma janela de incapacitação/resgate ainda depende de playtest. Corpo e mochila permanecem conforme regras de limpeza; colegas podem recuperá-los. Espectador não pode revelar áreas, transmitir no rádio ou informar posições que o personagem não conheceria. Não enviar aviso global de morte ao bunker.')
h(x,'Objetivos e encerramento')
p(x,'Rotas narrativas do GDD: contato/resgate, veículo de fuga e rota subterrânea. Recomenda-se fechar primeiro uma rota inteira, com início, recursos, contingência e final, antes de expandir para 2-3. Isso é ordem de produção, não remoção automática de conteúdo. Definir derrota, resumo final e recuperação de item-chave perdido. [S01, seções 2, 3, 6 e 8]')

x=page('09 / CONVIVÊNCIA E REJOGABILIDADE','Minijogos e eventos: o que realmente falta')
note(x,'Não há minijogo de habilidade concluído. Os dardos atuais somam um número aleatório de 1 a 20 a cada interação, por três tentativas. É um placeholder, não mira ou arremesso jogável. [S05]')
h(x,'Dardos - proposta para o primeiro minijogo')
p(x,'Entrar olhando para o alvo; mirar, preparar e lançar; o host valida turno, posição, força/limites e impacto em zonas configuráveis. Mostrar o dardo no alvo e a pontuação no espaço. Sair a qualquer momento. Não depender de sorte para substituir a habilidade; simplificar a física de forma determinística em rede.')
h(x,'Cartas - regra ainda a escolher')
p(x,'Escolher um jogo simples original ou de regras genéricas, como memória ou vazas. Definir assentos, baralho, distribuição, ordem, cartas visíveis/ocultas, saída e reconexão. O host guarda a ordem das cartas; cada jogador recebe somente a informação que pode conhecer. Evitar reproduzir marca, arte ou interface de jogos protegidos.')
h(x,'Sinuca e pingue-pongue')
p(x,'São pós-MVP no texto do GDD. Não estão implementados. Exigem decisões próprias de física autoritativa, turnos, impacto e latência; não devem ser tratados como simples adição de uma mesa. A seleção final para lançamento continua uma decisão de produto. [S01, seções 10 e 16]')
h(x,'Eventos e diretor - proposta inicial')
p(x,'Primeiro conjunto sugerido: falha do gerador, visitante pedindo água e alteração na água do reservatório. Cada evento precisa de gatilho, ações, custo, consequência, alternativa e conclusão. O diretor usa seed, pesos por dia/saúde/estoque, progresso e cooldown persistidos; não dispara apenas mensagens aleatórias.')
p(x,'Minijogos não pausam necessidades ou crises e não viram fonte excessiva de recursos essenciais. O aceite mínimo de U4 é um minijogo real e três eventos sistêmicos, ainda pendentes.')

x=page('10 / ARQUITETURA E EVIDÊNCIAS','Rede, persistência e privacidade')
h(x,'Base existente')
p(x,'Listen server de até quatro conexões. O host valida interação, distância/visada, IDs, revisões e capacidade. Mochilas e necessidades são privadas ao proprietário. Os estoques usam snapshots autorizados; os itens preservam identidade ao serem guardados, largados e recolhidos. [S03, S05, S06]')
p(x,'Checkpoints solo e cooperativo em cópias A/B com checksum e validação. O host preserva também os recursos de quem está fora. Cada cliente guarda uma credencial privada por campanha; o host mantém seu hash. Conexão concorrente no mesmo personagem, credencial desconhecida e novo perfil sem vaga são recusados.')
table(x,['Evidência local registrada em 21/10','Resultado e limite'],[
 ['Reconexão / restart do host','23 verificações; 13 processos novos; até quatro conectados. Emulação de 80 ms e 2% de perda de saída. Não são quatro humanos nem teste de internet.'],
 ['Persistência solo','17 passos em processos separados: salvar, reabrir, corrupção, versão/layout, duplicação, posição insegura e bloqueio de dados inválidos.'],
 ['Armários em rede','14 verificações de disputa, revisão, distância, capacidade, privacidade e controles. A interface testada ainda é modal.'],
 ['Portas / passagens','Evidência anterior de 13/13 vãos com cápsula e teste de abertura/fechamento. Não certifica circulação simultânea de quatro pessoas.'],
 ],[.34,.66])
h(x,'O que não pode ser declarado pronto')
p(x,'As credenciais são perfis locais portadores, não identidade de conta Steam. Faltam transporte autenticado/cifrado para distribuição, recuperação de perfil, menu de campanhas e migração de layouts. Jogadores ausentes ficam congelados; a política de simulação de ausência precisa ser decidida. Não há migração de host, conforme o MVP do GDD.')
p(x,'A conferência deste relatório foi documental e de código: os testes acima foram executados em marcos anteriores e seus JSONs foram lidos agora. Não foram repetidos durante a preparação do PDF. O manifesto corrente é <b>logs/reconnect_execution.json</b>.')

x=page('11 / PROGRAMA DO BUNKER','Cada ambiente precisa justificar seu uso')
p(x,'A geometria e o mobiliário de base já existem no projeto. Esta tabela descreve as funções a concluir e revisar, não uma certificação de que cada sala esteja acabada. Dimensões e adjacências continuam subordinadas à circulação real e à escala humana. [S01, seção 7; S02]')
table(x,['Ambiente','Entrega funcional / artística a concluir'],[
 ['Entrada e antecâmara','Portas coordenadas, EPI, inspeção, descontaminação, estado de ventilação e acesso à escada do estoque.'],
 ['Convivência','Mesa, sofá, objetos pessoais e leitura quente; conversa, jogos e rádio com uso físico e espaço para quatro pessoas.'],
 ['Cozinha','Abrir/usar utensílios, pia, preparo/água e conservação; geladeira vinculada à energia.'],
 ['Despensa','Interiores de armários/prateleiras, recursos visíveis, colocar/retirar objetos e esconderijos visuais.'],
 ['Dormitório','Quatro camas, transições de descanso, luzes de leitura e armários físicos; decidir uso compartilhado ou pessoal.'],
 ['Enfermaria','Tratamento com itens e estados de ferimento/doença; bancada e armário de remédios funcionais.'],
 ['Gerador / filtragem','Combustível, manutenção, circuitos, ventilação e consequências observáveis nas outras salas.'],
 ['Oficina','Reparo com ferramenta, peças e tempo; estado de objetos, bancada legível e espaços de apoio.'],
 ['Rádio / comando','Equipamento e bateria/frequência, voz e narrativa; registro de expedições sem informação global indevida.'],
 ['Sanitário','Ambientação coerente, pia/ducha e ligação visual às redes; mecânicas futuras identificadas como tal.'],
 ['Corredores e técnica','Vãos reais, sinalização, dutos, iluminação de orientação, rotas de saída e passagem conjunta sem bloqueio permanente.'],
 ['Recreação / alas lacradas','Recreação posterior conforme seleção de minijogos; alas futuras podem permanecer lacradas sem interior completo no recorte inicial.'],
 ],[.27,.73])
h(x,'Critério espacial')
p(x,'Cozinha perto da despensa, gerador afastado das camas, espaços reservados para cochichos e visibilidade parcial entre salas. Refazer a auditoria com quatro pessoas após incluir portas de armários, itens nas prateleiras e decoração: novos elementos também podem bloquear rotas.')

x=page('12 / PRODUÇÃO DE ARTE E PERFORMANCE','Do modelo editável ao objeto em jogo')
h(x,'Blender')
p(x,'Refinar a silhueta e construção; separar peças móveis e interiores; aplicar escala, eixos, pivôs e colisões adequadas. Revisar normais, UVs e densidade de textura. Manter fonte editável e exportação reproduzível. Para armários, o interior passa a ser parte essencial do asset, não só um volume externo.')
h(x,'Substance Painter e materiais')
p(x,'O kit cama/armário/porta possui projetos Painter: 11 materiais e 33 mapas de 1024 px documentados. Os cinco itens têm 15 mapas próprios de 1024 px gerados por código, não cinco projetos Painter. As seis superfícies-base do ambiente usam mapas de 512 px. Esses números descrevem produção, não aprovação de qualidade. [S02, S07, S08]')
p(x,'Revisar acabamento por material e por uso: tinta, metal exposto, borracha, tecido e plástico. Normal não deve imitar relevo em escala errada; roughness precisa variar com lógica física. Controlar repetição, alinhamento de UV e desgaste. Não aumentar tudo para 4K antes de medir o ganho visual e o custo.')
h(x,'Unreal')
p(x,'Conferir cada asset em uma sala de referência no próprio jogo: escala, acabamento, luz, sombra, interação, som, colisão e visão em primeira pessoa. Manter linguagem comum de materiais e sinalização. Ajustar exposição e contraste antes de tentar corrigir tudo com texturas.')
h(x,'Orçamento a medir')
b(x,'Registrar hardware alvo, resolução, preset, FPS e tempo de frame; observar GPU, CPU, memória, carregamento, draw calls e quantidade de objetos visíveis.')
b(x,'Usar colisão simples e representação determinística de recursos, instâncias e materiais compartilhados quando apropriado. Definir LODs e limitar efeitos/luzes com sombras pelo resultado medido.')
b(x,'Medir com quatro jogadores, portas móveis e armários cheios. O limite configurado de 45 FPS é um teto, não prova de fluidez. Não há novo benchmark neste relatório.')
note(x,'Gate visual proposto: aprovar uma área pequena totalmente finalizada, incluindo armário físico e porta, no hardware alvo. Só então reproduzir o padrão nas demais salas. Isso define qualidade e ordem de trabalho; não elimina ambientes do GDD.')

x=page('13 / EXPERIÊNCIA, SOM E CONTROLES','A atmosfera depende do uso e da resposta')
h(x,'Interface')
p(x,'Retirar o modal de estoque dos armários. Usar indicação contextual curta: alvo, ação e motivo de bloqueio. Evitar avisos de desenvolvimento e nomes em inglês no fluxo de produto. A mochila pessoal pode continuar como interface própria, a revisar separadamente. Não expor estoques, saúde, localização ou morte de aliados sem regra/dispositivo.')
p(x,'Concluir lobby com hospedar/entrar/continuar, erro de conexão, estado de restauração, retorno ao menu e gestão de campanha. O projeto hoje usa comandos técnicos para hospedagem/entrada; isso não é uma experiência pronta para o jogador.')
h(x,'Áudio e animação')
p(x,'Produzir abertura e travamento de portas, puxadores, metal, passos, manuseio, consumo e trabalho. Construir ventilação, gerador, água, chuva, sirenes e rádio; usar silêncio e abafamento por paredes como parte do espaço. Animar com transições curtas e legíveis, incluindo postura corporal vista pelos colegas.')
h(x,'Voz e rádio')
p(x,'Integrar voz por proximidade e canais de rádio com equipamento, frequência, carga e condição. Rádio sem energia não transmite. Distância e paredes precisam afetar a escuta; não informar automaticamente o destino de quem perdeu contato. Steam Networking não entrega essa lógica de voz por si só. [S01, seções 4 e 11]')
h(x,'Acessibilidade e localização')
p(x,'Menu de sensibilidade, FOV, remapeamento, legendas, volumes, push-to-talk, mute/bloqueio, redução de tremor e efeitos fortes, alternativas para daltonismo e sinais visuais de eventos sonoros. A sensibilidade recebeu ajuste básico no projeto; faltam menu e validação de uso contínuo. PT-BR inicial com estrutura para inglês.')
p(x,'Aprovar a resposta de uma interação completa: perceber o objeto, alcançar, acionar, ver/ouvir o resultado e manter controle previsível. Um som decorativo ou uma animação isolada não substitui esse ciclo.')

x=page('14 / BACKLOG PARA A EQUIPE','Prioridades e critérios de entrega')
p(x,'Recomendação atualizada pela crítica do criador. As frentes podem ser distribuídas entre profissionais; a passagem de marco depende de integração e teste, não apenas de arquivos entregues.')
table(x,['Prioridade / frente','Entrega verificável','Perfil responsável'],[
 ['P0 - Qualidade de referência','Uma área com materiais/iluminação aprovados, porta convincente e acabamento coerente no executável.','Arte de ambiente + artista técnico'],
 ['P0 - Armário físico','Folha animada, interior, slots com malhas, pegar/guardar sem modal e teste concorrente sem duplicação.','Blender/arte técnica + gameplay/rede'],
 ['P0 - Uso e navegação','E/F consistentes, cama com transição, colisão segura e circulação com quatro pessoas após os novos props.','Gameplay + animação + QA'],
 ['P0 - Entrada e continuidade','Lobby, continuar campanha, retorno ao menu, credencial/conta e erros recuperáveis. Prova antecipada de build Windows.','Gameplay/rede + integração/build'],
 ['P1 - Sobrevivência causal','Tempo, combustível, circuitos, rádio/geladeira/filtro e efeitos de doença/radiação com dados persistidos.','Sistemas/gameplay + design'],
 ['P1 - Partida completa','Coleta inicial, rua/prédio, equipamento, ameaça/combate, morte/mochila, retorno e um final funcional.','Level design + IA/gameplay + narrativa'],
 ['P1 - Vida social','Dardos de habilidade ou cartas, três eventos, diretor com seed/cooldown, sons e voz funcional.','Gameplay/rede + áudio + design'],
 ['P2 - Conteúdo e fechamento','Ampliação conforme GDD, outros finais, acessibilidade/localização, otimização e regressão final.','Equipe de conteúdo + QA/build'],
 ],[.24,.53,.23])
h(x,'Dependências que precisam começar cedo')
p(x,'Windows, Steam, voz e armazenamento/backup de assets não devem esperar a semana do lançamento. As metas de conteúdo só podem receber datas confiáveis depois de medir a velocidade da equipe com uma entrega integrada. Não há estimativa de esforço aprovada nem composição de equipe confirmada neste relatório.')
p(x,'Proposta de acompanhamento: registrar responsável real, estimativa, dependência, versão testada e critério de aceite para cada tarefa. Bugs de perda/duplicação de recurso, corrupção de save e bloqueio de circulação impedem fechar o marco.')

x=page('15 / ACEITE DO GDD','O que os testes atuais comprovam')
p(x,'Os testes T01-T15 abaixo vêm do GDD. “Parcial” significa que existe evidência para um componente ou cenário, não que o requisito inteiro esteja concluído. [S01, seção 17]')
table(x,['Teste','Situação nesta revisão','O que falta para fechar'],[
 ['T01 Porta compartilhada','Automação registrada','Quatro humanos, experiência visual/sonora e sessões contínuas.'],
 ['T02 Coleta simultânea','Automação registrada','Repetir no armário físico e na coleta inicial final.'],
 ['T03 Consumo escondido','Parcial: consumo e dados privados','Validar observação física, estoque e ausência de revelação indevida numa partida social.'],
 ['T04 Voz por distância','Pendente','Proximidade, oclusão e rádio operacionais.'],
 ['T05 Morte sem telepatia','Pendente','Morte real, ausência de aviso global e espectador restrito.'],
 ['T06 Rádio sem bateria','Pendente','Bateria/rádio/voz vinculados no servidor.'],
 ['T07 Reconexão sem duplicar','Validado em cenário local','Identidade Steam, recuperação de perfil, outros defeitos de rede e sessões longas.'],
 ['T08 Falha de energia','Pendente','Gerador, circuitos e dependentes reagindo juntos.'],
 ['T09 Coletar/retornar/depositar/salvar','Parcial: componentes e checkpoint','Loop completo de expedição e persistência integrada de suas consequências.'],
 ['T10 1-3 sobreviventes','Parcial: 1-4 conexões de base','Partida completa após morte/perda, sem softlock e com equilíbrio por grupo.'],
 ['T11 Circulação de quatro','Parcial: 13 vãos auditados','Quatro pessoas cruzando, usando camas/armários e recuperando bloqueios.'],
 ['T12 Item crítico perdido','Pendente','Objetivos com rota alternativa ou falha narrativa explícita.'],
 ['T13 Controles acessíveis','Pendente como conjunto','Microfone, legendas e remapeamento em teste real.'],
 ['T14 FPS e latência','Parcial: emulação de rede','Benchmark gráfico no hardware alvo e outros perfis de rede. Sem promessa de 60 FPS.'],
 ['T15 Sessão social completa','Pendente','30-60 min com quatro pessoas, telemetria e entrevista; decisões emergentes sem intervenção.'],
 ],[.24,.29,.47])
p(x,'Compilar, importar um modelo e produzir um render não concluem esses testes. A aprovação do jogo exige comportamento funcional, apresentação adequada e experiência humana no executável.')

x=page('16 / ESCOPO E META DE DEZEMBRO','Separar protótipo de lançamento')
table(x,['Conteúdo','Estado atual','Primeiro protótipo / MVP','Planejamento de lançamento'],[
 ['Itens','5 tipos 3D; 6 pickups','12-20 tipos','50-80 tipos balanceados'],
 ['Mundo externo','Exterior inicial','Rua + 1 prédio + supermercado','5-6 zonas compactas'],
 ['Inimigos','Nenhum loop concluído','1 arquétipo','3-4 arquétipos'],
 ['Eventos','Nenhum conjunto sistêmico concluído','3','20-30 eventos/variações'],
 ['Minijogos','Placeholder de dardos','1 simples real','Cartas, sinuca e outros conforme teste'],
 ['Finais','Nenhuma partida com desfecho','1 objetivo completo','2-3 rotas narrativas'],
 ['Comunicação','Mensagem de rádio demonstrativa','Teste de voz por proximidade','Proximidade + rádio + privacidade'],
 ],[.19,.27,.25,.29])
p(x,'Metas de quantidade vêm da seção 16 do GDD e são planejamento sujeito a validação, não promessa de entrega já cumprida. Mudança de escopo precisa de decisão explícita do criador. Não se deve chamar um protótipo de lançamento para caber no calendário.')
h(x,'Gates recomendados para dezembro de 2026')
b(x,'Qualidade de referência aprovada no jogo e armário físico concluído, mantendo FPS medido no hardware definido.')
b(x,'Uma partida completa do lobby ao desfecho, sem recursos críticos ausentes ou bloqueios irrecuperáveis.')
b(x,'Conteúdo selecionado, voz/Steam, Windows, acessibilidade, áudio e todas as dependências de distribuição verificados.')
b(x,'Candidato testado por quatro pessoas durante 30-60 minutos, com regressões de save, reconexão, latência e perda; nenhum bug crítico aberto.')
h(x,'Leitura de prazo')
p(x,'Dezembro permanece a meta do criador, sem dia definido. Hoje faltam sistemas centrais e não há medição de capacidade da equipe; portanto a viabilidade não está comprovada. Se os gates não couberem no mês, apresentar as lacunas e decidir conscientemente entre nova data e revisão formal de escopo. Este relatório não aprova nenhuma redução. [S09]')

x=page('17 / REUNIÃO E RASTREABILIDADE','Decisões e material para os desenvolvedores')
h(x,'Decisões para sair da reunião com responsáveis')
p(x,'1. Aprovar o alvo de realismo e uma sala/armário de referência. 2. Definir pegar/segurar/guardar e teclas, mantendo o armário sem modal. 3. Decidir armários pessoais, trancas e esconderijos. 4. Escolher o primeiro minijogo e suas regras. 5. Confirmar o primeiro objetivo/final. 6. Definir incapacitação e ausência/desconexão. 7. Fixar hardware/preset alvo e critérios medidos. 8. Designar ambiente Windows, integração Steam/voz e guarda dos assets. 9. Medir esforço com a equipe e validar a meta de dezembro.')
h(x,'Fontes verificadas no projeto')
refs=[
 ['S01','references/Condominio_13_GDD_Codex.md','GDD v1.0, 13/10/2026, lido integralmente.'],
 ['S02','docs/PRODUCTION_STATUS.md; docs/REMAINING_FOR_RELEASE.md','Estado consolidado, separando os marcos históricos.'],
 ['S03','docs/STORAGE_REPORT.md; Source/Condominio13/BunkerContainer.*','Armazenamento modal, snapshots privados e ausência de interiores animados.'],
 ['S04','docs/DOORS_AND_INPUT_REPORT.md; Source/Condominio13/BunkerDoor.cpp','Interpolação, colisão, testes e limites das portas.'],
 ['S05','Source/Condominio13/BunkerNetwork.cpp; BunkerSurvival.*','Camas, placeholders de gerador/rádio/dardos, necessidades e consumo.'],
 ['S06','docs/COOP_RECONNECT_REPORT.md; docs/PERSISTENCE_REPORT.md; logs/reconnect_execution.json','Checkpoint, perfis, testes e limitações atuais.'],
 ['S07','docs/ITEM_ART_REPORT.md','Cinco tipos de itens, texturas e revisão da garrafa azul.'],
 ['S08','docs/FIRST_PERSON_ITEM_REPORT.md','Mãos e gestos provisórios, sem atuação corporal completa.'],
 ['S09','docs/RELEASE_TARGET_DECEMBER.md','Calendário por critérios e dependências; sem garantia de data.'],
]
table(x,['Ref.','Arquivo / base','Uso'],refs,[.08,.52,.40])
p(x,'Caminhos Source acima partem de unreal/Condominio13/. Capturas usadas: screenshots/persistence_water_hud.png e screenshots/storage_2.png. Base local: commit <b>8d494ee</b>; executável Mac Development registrado no manifesto, SHA-256 iniciado por <b>d4b6d9c4989f8fb8</b>. Não houve alteração de gameplay ou arte para produzir este PDF.',)

p(x,'<b>Pacote de passagem:</b> código e relatórios não incluem automaticamente todos os binários. Fontes Blender/Painter, exports e aplicativo ficam localmente fora do Git; entregar as fontes e o projeto Unreal/Content com versões e backup definidos. Saves e perfis reais de jogadores não fazem parte do pacote de assets.')

# Stable, editable authoring data for regeneration and handoff.
(ROOT/'output/pdf/Condominio_13_Relatorio_Producao_fonte.json').write_text(json.dumps(PAGES,ensure_ascii=False,indent=2)+'\n')

def para(text,style='body'):
 # Keep report typography predictable and compatible with the PDF renderer.
 return Paragraph(text.replace('\n','<br/>').replace('–','-').replace('—','-').replace('‑','-'),styles[style])

def make_table(block):
 data=[[para(escape(c),'thead') for c in block['heads']]]+[[para(escape(str(c)),'cell') for c in row] for row in block['rows']]
 t=Table(data,colWidths=[WIDTH*f for f in block['widths']],repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),('LINEBELOW',(0,0),(-1,0),.5,NAVY),('LINEBELOW',(0,1),(-1,-1),.35,C('#D8E1DE'))]))
 t.spaceAfter=10;return t

class ReportCanvas(canvas.Canvas):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.states=[]
 def showPage(self):self.states.append(dict(self.__dict__));self._startPage()
 def save(self):
  total=len(self.states)
  for state in self.states:
   self.__dict__.update(state);self.draw_frame(total);super().showPage()
  super().save()
 def draw_frame(self,total):
  self.setStrokeColor(C('#D0DAD5'));self.setLineWidth(.6);self.line(LEFT,H-38,W-RIGHT,H-38);self.line(LEFT,41,W-RIGHT,41)
  self.setFont('Arial-Bold',8);self.setFillColor(TEAL);self.drawString(LEFT,H-27,'DEIROS DEV / CONDOMÍNIO 13')
  self.setFont('Arial',8);self.setFillColor(MUTED);self.drawRightString(W-RIGHT,H-27,'REVISÃO DE PRODUÇÃO | 21.10.2026')
  self.setFont('Arial',7.5);self.drawString(LEFT,27,'Uso interno | GDD, estado local e propostas identificadas')
  self.setFont('Arial-Bold',8);self.drawRightString(W-RIGHT,27,f'{self._pageNumber:02d} / {total:02d}')

flow=[];heights=[]
for index,d in enumerate(PAGES):
 section=[para(d['kicker'],'kicker'),para(d['title'],'title')]
 for block in d['blocks']:
  kind=block['type']
  if kind=='p':section.append(para(block['text']))
  elif kind=='h':section.append(para(block['text'],'h2'))
  elif kind=='table':section.append(make_table(block))
  elif kind=='note':
   t=Table([[para(block['text'],'callout')]],colWidths=[WIDTH]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('LINEBEFORE',(0,0),(0,-1),3,TEAL),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),11)]));t.spaceAfter=10;section.append(t)
  elif kind=='image':
   from PIL import Image as PILImage
   file=ROOT/block['path'];iw,ih=PILImage.open(file).size
   picture=Image(str(file),width=block['width'],height=block['width']*ih/iw);picture.hAlign='LEFT'
   section.extend([picture,Spacer(1,5),para(block['caption'],'small')])
 height=0
 for item in section:
  _,ih=item.wrap(WIDTH,10000);height+=ih+getattr(item,'spaceBefore',0)+getattr(item,'spaceAfter',0)
 heights.append({'section':index+1,'height':round(height,1),'available':H-112})
 flow.extend(section)
 if index<len(PAGES)-1:flow.append(PageBreak())
report=BaseDocTemplate(str(OUT),pagesize=A4,rightMargin=RIGHT,leftMargin=LEFT,topMargin=58,bottomMargin=54,title='Condomínio 13 - Relatório de produção e lógica do jogo',author='Deiros Dev / revisão técnica assistida por Codex',subject='Estado atual, direção visual, interações físicas, lógica, backlog e critérios de lançamento')
report.addPageTemplates(PageTemplate(id="content",frames=[Frame(LEFT,54,WIDTH,H-112,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,id="body")]))
report.build(flow,canvasmaker=ReportCanvas)
(ROOT/'tmp/pdfs/layout_preflight.json').write_text(json.dumps(heights,indent=2))
print(json.dumps({'pdf':str(OUT),'planned_pages':len(PAGES),'layout':heights},indent=2))
