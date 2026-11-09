from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
solo=json.loads((R/'logs/open_plan_solo_result.json').read_text());net=json.loads((R/'logs/open_plan_network_result.json').read_text());src=json.loads((R/'logs/open_plan_source.json').read_text());ue=json.loads((R/'logs/open_plan_unreal.json').read_text());art=json.loads((R/'logs/open_plan_editable_validation.json').read_text())
network_text='\n'.join((R/f'logs/open_plan_network_{role}.log').read_text(errors='replace') for role in ('host','client'))
net['checks']['no_stock_modal']=all('modal=0' in l for l in network_text.splitlines() if 'C13_PHYSICAL_STAGE' in l and 'step=13 ' not in l and 'step=16 ' not in l)
net['checks']['consume_water_and_food']='type=Water consume=1' in network_text and 'type=Food consume=1' in network_text
net['checks']['reference_routes_clear']='C13_REFERENCE_CIRCULATION clear=9 total=9' in network_text
net['passed']=net['passed'] and all(net['checks'].values())
net['additional_checks_recomputed_from_recorded_runtime_log']=True
(R/'logs/open_plan_network_result.json').write_text(json.dumps(net,indent=2))
assert solo['passed'] and net['passed'] and art['passed']
fps=next(l.split('C13_REFERENCE_FPS ')[1] for l in solo['markers'][0] if 'C13_REFERENCE_FPS ' in l)
settings=next(l.split('C13_REFERENCE_SETTINGS ')[1] for l in (R/'logs/open_plan_solo_host.log').read_text(errors='replace').splitlines() if 'C13_REFERENCE_SETTINGS ' in l)
manifest={'source_sha256':hashlib.sha256((R/'blender/Bunker_OpenPlan_v001.blend').read_bytes()).hexdigest(),'executable_sha256':hashlib.sha256((R/'builds/Mac/Condominio13-OpenPlan.app/Contents/MacOS/Condominio13').read_bytes()).hexdigest(),'map':'/Game/Bunker/Lvl_Bunker_OpenPlan','original_map_preserved':True,'original_app_preserved':True,'native_root_ids_preserved':ue['native_actor_roots_preserved'],'old_campaign_compatibility':'Not loaded or migrated by this review map; C13Reference disables campaign IO.','checks':{'solo':solo['checks'],'network':net['checks'],'editable':art['passed']},'fps':fps,'settings':settings,'scope':'Architecture comparison only; other integrated zones retain prior art and gameplay limitations.'}
(R/'logs/open_plan_delivery_manifest.json').write_text(json.dumps(manifest,indent=2))
text=f'''# Bunker aberto — versão comparativa

29/10/2026 · Deiros Dev

## O que foi executado

Criada uma planta alternativa no Blender e integrada no mapa Unreal `Lvl_Bunker_OpenPlan`, com um aplicativo próprio. Convivência, cozinha, despensa, oficina, enfermaria e rádio passam a ocupar o mesmo salão. Dormitório, banheiro, antecâmara e gerador continuam fechados, conforme aprovação na conversa. O envelope continua aproximadamente 28 x 20 m: a amplitude vem da abertura, não de aumentar o mapa.

Foram removidos {len(src['removed_partition_objects'])} objetos modulares de divisórias/molduras do derivado arquitetônico e os revestimentos decorativos que fechavam a convivência. Oito folhas interiores legadas foram ocultadas e tiveram a colisão desabilitada somente na alternativa. Seus atores, nomes e raízes continuam presentes. Não são portas invisíveis bloqueando circulação.

O alvo de dardos ganhou um suporte curto e independente, preservando o ponto de interação existente. Sua lógica anterior continua demonstrativa e aleatória. Mobiliário social, armário físico e recursos existentes foram preservados. O piso e o forro foram contínuos e a iluminação foi equalizada para evitar o contraste das antigas salas. Luminárias e pontos de apoio de baixo custo mantêm a leitura dos setores; isso não representa arte final de todos os setores. As folhas retiradas têm uma marca explícita que desativa visual e colisão também ao iniciar em rede.

## Como avaliar

Abrir `builds/Mac/Avaliar-Bunker-Aberto.command`. A avaliação inicia no salão e permite andar livremente. E abre a folha do armário e pega o objeto olhado; I/setas selecionam o item pessoal e X numa posição disponível guarda. A sessão não grava nem carrega a campanha. Uma água e uma comida existentes são movidas para a prateleira no modo de demonstração; não há criação de recursos para a campanha.

A versão anterior e seu lançador de convivência continuam disponíveis. O mapa original não foi substituído. O nome do mapa faz parte da assinatura dos checkpoints; por isso esta comparação não promete carregar saves antigos. Uma promoção futura exigirá migração explícita testada, mantendo GUIDs e conteúdos.

## Validação executada

Aplicativo Mac compilado, empacotado e com assinatura verificada. Teste solo renderizado: as seis zonas comuns são alcançáveis a partir do centro, em uma grade de 50 cm construída com cápsula real de raio 34 cm e meia-altura 96 cm. Cada aresta é conferida com sweep de colisão; também há verificação de piso. Isso valida rotas para uma cápsula, não conforto de quatro pessoas andando juntas. Quatro cápsulas simultâneas cabem sem contato na área central testada.

Teste com host e cliente renderizados: {len(net['checks'])} verificações passaram, incluindo retirada/devolução com mesmo ID, disputa rejeitada, bloqueio da porta fechada, observação da ação e snapshots iguais nas duas conexões. Não houve dois humanos ou internet nesta rodada. Os testes históricos de reconexão de 22/10 não são apresentados como uma nova sessão humana.

FPS registrado: `{fps}`. Janela curta de aproximadamente 16 s, estática, 1280 x 720, Apple M2 / 24 GB. Configuração: `{settings}`. Não é garantia para toda a partida ou para Windows. Capturas reais: `screenshots/reference_openplan_wide.png`, `reference_openplan_reverse.png`, `reference_openplan_hero.png`.

Fonte Blender reaberta em processo independente, conferindo geometria finita, existência das coleções, ausência das divisórias removidas e arquivo de exportação. Planta superior renderizada sem teto e sem dutos para não confundir elementos suspensos com paredes. Fora da convivência, a fonte usa proxies do blockout: não é um arquivo mestre de todos os móveis refinados da Unreal.

## Ainda falta nesta direção

Organizar melhor distâncias e pequenos grupos de móveis, reforçar orientação/sinalização e espalhar a linguagem visual aprovada pelas zonas agora abertas. A enfermaria precisa de privacidade visual por biombo parcial; a voz por proximidade ainda precisa ser implementada e testada, então não se declara privacidade acústica pronta. Esta entrega é a revisão espacial antes desse acabamento.

Permanecem os limites anteriores de animação procedural, áudio capturado parcialmente e inicialização intermitente do Mac sem correção confirmada. Não foram concluídos inimigos, combate, expedição, eventos, minijogo ou final apenas por abrir as divisórias.

## Próxima meta

MVP interno em **30/01/2027**, com férias de **04 a 15/01/2027**. Ver `docs/MVP_TARGET_JANUARY_2027.md`: prévia completa antes das férias, teste humano de quatro pessoas na volta e estabilização entre 25 e 30/01. A meta depende de equipe e Windows; não equivale a promessa de lançamento.

## Fontes

- `blender/Bunker_OpenPlan_v001.blend`
- `exports/Bunker_OpenPlanShell.fbx`
- `unreal/Condominio13/Content/Bunker/Lvl_Bunker_OpenPlan.umap`
- `builds/Mac/Condominio13-OpenPlan.app`
- `scripts/create_open_plan.py`, `install_open_plan.py`, `run_open_plan_validation.py`
- `logs/open_plan_*` e `logs/open_plan_delivery_manifest.json`
'''
(R/'docs/OPEN_PLAN_REPORT.md').write_text(text);print(json.dumps(manifest,indent=2))
