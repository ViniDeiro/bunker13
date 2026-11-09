"""Evidence-backed handoff. Run only after the final game captures and checks."""
from pathlib import Path
import json,re,hashlib
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
R=Path(__file__).resolve().parents[1];O=R/'output/pdf/Condominio_13_Sala_Referencia_2026-10-22.pdf';O.parent.mkdir(parents=True,exist_ok=True)
for n,f in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,'/System/Library/Fonts/Supplemental/'+f))
C=colors.HexColor;ink=C('#23373B');teal=C('#28776F');muted=C('#5F7176');bg=C('#EFF4F2');gold=C('#A46F3D');W,H=A4;CW=W-88
style={'body':ParagraphStyle('body',fontName='Body',fontSize=10,leading=14.3,textColor=ink,spaceAfter=7),'small':ParagraphStyle('small',fontName='Body',fontSize=8.2,leading=11.3,textColor=muted,spaceAfter=5),'h':ParagraphStyle('h',fontName='Bold',fontSize=12,leading=16,textColor=teal,spaceBefore=10,spaceAfter=6),'title':ParagraphStyle('title',fontName='Bold',fontSize=23,leading=27,textColor=ink,spaceAfter=12),'k':ParagraphStyle('k',fontName='Bold',fontSize=8.5,leading=12,textColor=gold,spaceAfter=7),'cell':ParagraphStyle('cell',fontName='Body',fontSize=8.6,leading=11.5,textColor=ink),'head':ParagraphStyle('head',fontName='Bold',fontSize=8.4,leading=11,textColor=colors.white)}
S=[]
def p(t,kind='body'):S.append(Paragraph(t,style[kind]))
def page(k,t):
 if S:S.append(PageBreak())
 p(k,'k');p(t,'title')
def h(t):p(t,'h')
def img(path,width=CW,cap=None):
 from PIL import Image as PImage
 path=R/path
 with PImage.open(path) as im:w,hh=im.size
 S.append(Image(str(path),width=width,height=width*hh/w));S.append(Spacer(1,6))
 if cap:p(cap,'small')
def table(head,rows,fracs):
 data=[[Paragraph(escape(str(c)),style['head']) for c in head]]+[[Paragraph(escape(str(c)),style['cell']) for c in row] for row in rows]
 t=Table(data,colWidths=[CW*f for f in fracs],hAlign='LEFT',repeatRows=1);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),teal),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,bg]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.6,teal)]));S.append(t);S.append(Spacer(1,8))
def load(n):return json.loads((R/'logs'/n).read_text())
network=load('reference_network_result.json');video=load('reference_video_result.json');saved=load('reference_save_result.json');integrity=load('reference_art_validation.json');delivery=load('reference_delivery_manifest.json')
assert network['passed'] and video['passed'] and saved['passed'] and integrity['passed'],'Do not publish a failed acceptance report as complete'
def fps(path):
 t=(R/path).read_text(errors='replace');m=re.search(r'C13_REFERENCE_FPS phase=(\w+) samples=(\d+) mean_ms=([\d.]+) median_ms=([\d.]+) p95_ms=([\d.]+) fps=([\d.]+)',t);return m.groups() if m else None
before=fps('logs/reference_before_game.log');after=fps('logs/reference_after_solo.log')
page('DEIROS DEV / 22.10.2026','Convivência\nSala de referência')
p('<b>Condomínio 13 - candidata para avaliação visual e funcional.</b> Escopo: uma sala, um armário físico e as ações relacionadas. Base: relatório de produção de 21/10/2026 e projeto existente.')
img('screenshots/reference_after_hero.png',cap='Captura real do executável Unreal. A aprovação da qualidade visual pertence ao criador; este relatório não declara arte comercial aprovada.')
table(['Entrega','Evidência'],[['Fonte Blender','Montagem editável, biblioteca de modelos e mapas incorporados.'],['Unreal','Sala integrada no mapa existente e executável Mac atualizado.'],['Interação','Porta física, coleta e devolução em slots, sem modal de estoque.'],['Validação','Duas instâncias, vídeo do jogo, persistência e circulação com cápsula real.']],[.25,.75])
p('Os demais ambientes não receberam nova produção de arte. Os outros seis contêineres conservam a interface anterior até a aprovação desta referência.','small')
page('01 / COMPARAÇÃO NO EXECUTÁVEL','Antes e depois')
img('screenshots/reference_before_wide.png',cap='Antes: cores claras, repetição de texturas, volumes antigos do blockout e teto sem leitura.')
img('screenshots/reference_after_wide.png',cap='Depois: móveis construídos, texturas próprias, iluminação social e substituição dos volumes antigos. Mesmo ponto e direção de referência; o piso acrescenta 1 cm de acabamento sobre a zona anterior.')
p('Imagens sem tratamento para simular acabamento. O exemplo de exposição excessiva encontrado durante a integração foi descartado e preservado apenas como diagnóstico.','small')
page('02 / CONSTRUÇÃO E MATERIAIS','Escala e organização')
img('screenshots/reference_blender_top.png',width=400,cap='Vista superior da fonte Blender. As capturas anteriores e posteriores de aprovação são do executável Unreal.')
table(['Elemento','Dimensão / decisão'],[['Sala','Envelope existente de aproximadamente 9 x 7 m; piso interno 8,8 x 6,8 m; altura livre acabada de cerca de 2,78 m sob a laje existente.'],['Mesa / assentos','Tampo de cerca de 2,05 x 0,96 m; quatro cadeiras com assento de aproximadamente 47 cm.'],['Armário','Corpo de 1,20 x 0,54 x 1,96 m; folha e pivô separados; folga lateral de 4 mm.'],['PBR','Mapas de 1024 px por superfície, referência de 1 metro, roughness e metalness distintos.'],['Materiais','Concreto, aço, tinta, borracha, tecido, madeira, papel e cerâmica; sem ferrugem uniforme.']],[.25,.75])
p('Modelos e mapas originais gerados por procedimentos próprios; não são exportações de uma nova sessão no Substance Painter. Os projetos Painter anteriores permanecem preservados.','small')
page('03 / ARMÁRIO FÍSICO','Recursos no mundo')
h('Uso')
p('<b>E na porta:</b> abrir ou fechar. <b>E no objeto:</b> retirar aquela unidade. <b>I e setas:</b> escolher um item na mochila pessoal; fechar a mochila e <b>X no espaço disponível:</b> guardar. A porta fechada bloqueia retirada e depósito. O armário não abre uma lista de estoque.')
h('Identidade e concorrência')
p('Cada unidade conserva seu GUID. A posição física usa um slot estável de 0 a 11; remover um item não renumera os demais. A malha da prateleira é uma representação, não um segundo recurso. O host verifica estado da porta, distância, visada, slot, revisão, propriedade e capacidade antes de mover o item uma única vez.')
table(['Verificação','Resultado'],[[k.replace('_',' '),'PASS' if v else 'FALHOU'] for k,v in network['checks'].items()],[.74,.26])
p('O teste usa um host e um cliente reais no mesmo computador. As ações principais passam pelas teclas do jogo; o cliente envia também uma intenção concorrente por RPC. É automação de teste, não duas pessoas jogando.','small')
page('04 / AÇÕES E CONTINUIDADE','Mãos, observação e salvamento')
h('Apresentação das ações')
p('A mão alcança o ponto de interação e acompanha a folha móvel. Pegar e guardar usam a posição física do objeto. Beber mantém a pegada junto à garrafa; comer utiliza lata e colher. Um ator temporário compartilha a ação com observadores próximos e com visada, sem transmitir a mochila completa ou as necessidades do jogador.')
p('<b>Limite artístico:</b> as mãos usam poses rígidas com movimento procedural. Não há um novo esqueleto de dedos nem uma atuação corporal final. A aprovação de contato, ritmo e naturalidade deve ser feita no vídeo e no executável.')
h('Persistência')
p('O campo de slot foi acrescentado sem trocar os IDs. O novo armário é uma extensão inicialmente vazia do layout: checkpoints anteriores continuam exigindo os mesmos elementos e a mesma assinatura da base, permitindo apenas a ausência deste contêiner novo.')
table(['Teste em novo processo','Resultado'],[[r['phase'].replace('reference_',''),'PASS' if r['passed'] else 'FALHOU'] for r in saved['checks']],[.74,.26])
p('Também foi criado um checkpoint com o executável anterior e carregado na nova implementação, conferindo mochila, contêiner, objeto largado e registros de coleta. Os testes usam arquivos isolados, sem alterar a campanha pessoal.')
h('Modo de avaliação')
p('O lançador da sala abre uma sessão de avaliação que não grava campanha. Água e comida já existentes no mapa são movidas para a prateleira, com os mesmos IDs, para facilitar a avaliação. No jogo normal, o armário novo começa vazio.')
page('05 / DESEMPENHO','Medições e limites')
p('<b>Máquina:</b> Apple M2, 24 GB, macOS 26.6.2. Executável Mac Development, Unreal 5.8.3. Não foi feito benchmark Windows.')
rows=[]
for title,m in [('Antes - 1280 x 720',before),('Depois - 1280 x 720',after)]:
 if m:rows.append([title,f'{float(m[5]):.2f}',f'{float(m[2]):.2f} ms',f'{float(m[4]):.2f} ms',m[1]])
for role,path in [('Host - 960 x 540','logs/reference_video_host.log'),('Cliente - 800 x 450','logs/reference_video_client.log')]:
 t=(R/path).read_text(errors='replace');m=re.search(r'C13_TWO_PLAYER_FPS role=\w+ samples=(\d+) fps=([\d.]+) p95_ms=([\d.]+)',t)
 if m:rows.append([role,m[2],'-',m[3]+' ms',m[1]])
table(['Cenário','FPS médio','Frame médio','Frame p95','Amostras'],rows,[.34,.14,.18,.19,.15])
p('Solo: janela estática de aproximadamente 16 s, após aquecimento, sem capturar imagens durante a medição. Dois jogadores: janela de aproximadamente 5 s antes de iniciar a gravação, com dois processos renderizando no mesmo M2. São amostras curtas, não certificação de desempenho em uma partida completa.')
settings=re.findall(r'C13_REFERENCE_SETTINGS .*',(R/'logs/reference_after_solo.log').read_text(errors='replace'))
if settings:p('Configuração efetiva registrada: '+escape(settings[-1].replace('C13_REFERENCE_SETTINGS ','')),'small')
p('O perfil gráfico anterior é preservado fora da sala. Na convivência, há sombras locais e oclusão de ambiente; três luminárias direcionadas projetam sombras dinâmicas. As luzes de apoio aproximam a iluminação indireta para conter o custo no Mac.')
h('Vídeo')
p('O vídeo contém quadros nativos do jogo com seus intervalos registrados, incluindo as duas perspectivas. A gravação é amostrada em cerca de 6-7 quadros/s; essa cadência é diferente do FPS do jogo. A captura de áudio pela saída do jogo ficou parcial (3,6 s para 34 s de vídeo). O trecho segue separado; os vídeos são silenciosos para evitar som fora de sincronia. O áudio das portas permanece no executável.')
page('06 / PROBLEMAS E PASSAGEM','O que foi corrigido e o que avaliar')
table(['Problema encontrado','Correção'],[['Exposição excessiva','Compensação e intensidade revistas a partir de captura real.'],['Volumes antigos dentro da malha geral','Somente quatro caixas da convivência removidas; 13 folhas nativas e demais peças preservadas.'],['Falha ao replicar duração da ação','Propriedade refletida corretamente; rodada multiplayer repetida.'],['Ação invisível ao colega','Separada a visibilidade local da relevância de rede.'],['E no interior retirava item ao tentar fechar','A automação passa a mirar a maçaneta na posição atual da folha.'],['Passagem junto ao encosto','Quatro cadeiras recolhidas sob o tampo; varredura com cápsula repetida.'],['Objetos flutuando ou penetrando','Apoio ajustado pelos limites reais da malha e pela altura do acabamento.']],[.37,.63])
p('Houve inicializações intermitentes com sinal 11 antes de gerar log. O diagnóstico aponta LLM/alocador da Unreal na consulta do macOS; não foi corrigido. A suíte registra repetições dessas partidas vazias. PASS após repetição não certifica estabilidade de inicialização.','small')
h('Ainda depende de avaliação')
p('O teto ainda apresenta relevo forte; linhas finas serrilham no perfil de 70%, e a vista pela porta tem contraste excessivo. Esses pontos, a naturalidade das mãos e os materiais em movimento precisam de revisão antes de declarar qualidade comercial. Permanecem fora desta entrega: substituição dos demais armários, novos ambientes, minijogos completos, partida completa e lançamento. Não houve teste com dois humanos, internet, Windows ou sessão longa de quatro pessoas.')
h('Arquivos principais')
for t in ['blender/Convivencia_Reference_v001.blend','exports/reference_room/','assets/reference_room/','unreal/Condominio13/Condominio13.uproject','builds/Mac/Condominio13-VerticalSlice.app','builds/Mac/Avaliar-Sala-Convivencia.command','output/video/Condominio13_Armario_Fisico.mp4','docs/REFERENCE_ROOM_REPORT.md','logs/reference_delivery_manifest.json']:p(escape(t),'small')
p('Integridade: Blender '+escape(delivery['blend_sha256'][:20])+'...; executável '+escape(delivery['executable_sha256'][:20])+'... . Manifesto completo e logs ficam no projeto.','small')
def footer(c,doc):
 c.saveState();c.setStrokeColor(C('#D5E0DC'));c.line(44,39,W-44,39);c.setFont('Body',8);c.setFillColor(muted);c.drawString(44,25,'DEIROS DEV / CONDOMÍNIO 13 / SALA DE REFERÊNCIA');c.drawRightString(W-44,25,str(doc.page));c.restoreState()
SimpleDocTemplate(str(O),pagesize=A4,leftMargin=44,rightMargin=44,topMargin=40,bottomMargin=51,title='Condomínio 13 - Sala de referência',author='Deiros Dev').build(S,onFirstPage=footer,onLaterPages=footer)
print(O)
