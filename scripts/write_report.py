import json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1]
g=json.loads((r/'logs/generation.json').read_text());v=json.loads((r/'logs/validation.json').read_text());rt=json.loads((r/'logs/scale_roundtrip.json').read_text())
idp=json.loads((r/'logs/idempotence.json').read_text()) if (r/'logs/idempotence.json').exists() else {'pass':False}
export_check=json.loads((r/'logs/export_roundtrip.json').read_text())
rows='\n'.join(f"| {n.replace('_',' ')} | {' × '.join(f'{x:g}' for x in p['clear_dimensions_m'])} | {'Sim' if p['reachable_capsule_r030'] else 'Nao'} |" for n,p in g['rooms'].items())
cols='\n'.join(f'| {k} | {n} |' for k,n in g['collection_counts'].items())
text=f'''# Condomínio 13 — B0/B1 / Deiros Dev

Data: 13/10/2026. Fonte: GDD v1.0, lido integralmente, preservado em references/.
Status: primeira versão de blockout entregue para revisão; B2 não autorizado. Gate de importação Unreal pendente.

## Resultado executado

Arquivo mestre: `blender/Bunker_Blockout_v001.blend`. Blender {g['blender']}. Um pavimento de piso 28 × 20 m, envelope externo 28,8 × 20,7 m incluindo espessuras e folgas periféricas. Escada externa a esse envelope liga patamar mínimo do estoque a +3 m. Não foi modelado o supermercado.

{g['objects']} objetos organizados; {g['mesh_data_blocks']} datablocks de malha. Paredes de 0,20 m, pé-direito 3 m, laje de 0,25 m, peças de parede de até 1 m com fechamentos, pisos/tetos de 2 m compartilhados. Grade de inspeção 0,50 m; espessuras, vãos de 1,10 m e folgas de montagem usam subdivisões menores. Folhas com HINGE na dobradiça, móveis com origem na base, módulos com origem no encaixe. UVs de caixa provisórios; UVs finais/lightmaps são B2.

| Ambiente | Dimensões livres (m) | Rota desde entrada |
|---|---|---|
{rows}

Recreação dedicada é posterior conforme GDD; mesa de cartas já tem volume reservado na convivência. Há três frentes fechadas para ala médica, vigilância e túnel; não existem interiores dessas alas. Gerador e dormitório ocupam extremos diferentes; cozinha e despensa ficam na ala leste. Rádio e enfermaria são candidatos a espaços de conversa reservada, mas privacidade acústica ainda não foi implementada nem comprovada.

## Circulação e uso

Acesso contínuo: patamar do estoque → 20 degraus → patamar inferior → porta estanque externa → antecâmara → porta estanque interna → eixo de circulação → salas. Degraus: 0,15 m de espelho, 0,30 m de piso, 1,80 m de largura. A escada é geometria sólida, não uma textura ou rampa visual.

Portas internas: 1,10 × 2,20 m; convivência no eixo: 1,80 × 2,20 m; estanques: 1,80 × 2,40 m. As folhas estão abertas na revisão, as portas futuras estão fechadas. Abertura/fechamento interativo e intertravamento da antecâmara não existem em B1. Portas estreitas são de passagem individual; quatro jogadores não passam lado a lado por um vão de 1,10 m.

Rota da posição de inspeção na antecâmara à convivência: {g['route_entry_common_m']} m, aproximadamente {g['route_entry_common_m']/1.4:.1f} s a 1,4 m/s. Isso é cálculo geométrico, não cronometragem de playtest. O eixo contém faixa livre de 2 m e foi testado para passagem em dois sentidos. Quatro volumes de referência de 1,75 m, diâmetro 0,60 m, cabem simultaneamente na área de encontro.

Volumes de uso: quatro camas, quatro armários pessoais, mesa social e seis assentos, sofá, TV, rádio, mesa de cartas, bancada/pia/fogão/geladeira, três estantes na despensa e volume de esconderijo, galões, maca/medicamentos, oficina, gerador/combustível/filtro/tanque, sanitário/ducha, EPI/inspeção/status. São proxies para validar espaço, sem interação ou arte final. O inventário artístico completo da seção 12 permanece como backlog B2, não como assets finais entregues.

## Validação executada

- Reabertura independente do .blend: executada.
- Testes automatizados: **{v['passed']} aprovados; {v['failed']} falhos**. Evidência: `logs/validation.json` e `logs/validation.log`.
- Grade de circulação 0,10 m contra limites mundiais reais das malhas e obstáculos expandidos por 0,30 m. Todas as dez salas têm áreas acessíveis. Método conservador em planta; não substitui física UE.
- Referência humana, quatro camas, cinco câmeras, coleções, escalas aplicadas, vértices finitos, malhas fechadas sem faces degeneradas, passos da escada, portas, arquivos e ausência de sobreposição volumétrica entre paredes: checados.
- Cubo FBX exportado e reimportado em nova cena: dimensões {rt['dimensions_m']} m; resultado {rt['pass']}.
- Reexecução idempotente: {idp.get('pass')}; comparação de nomes, tipos, posições, dimensões e contagens de vértices em `logs/idempotence.json`.
- Reimportação final em cenas novas: GLB {export_check['glb']['pass']} e FBX {export_check['fbx']['pass']}; 777 malhas visuais preservadas, sem dimensões divergentes ou materiais ausentes. FBX contém também 777 caixas UCX. Evidência: `logs/export_roundtrip.json`. Isso não confirma reconhecimento das colisões pela Unreal.
- Teste manual via interface: arquivo aberto, operador B1 Navegar registrado, movimento WASD da antecâmara através da porta norte até a circulação observado. Não foi realizado playtest com quatro pessoas.
- Cinco PNGs de revisão: superior cotada, entrada, convivência, corredor, despensa. Luzes apenas provisórias, quentes no social e frias no técnico.
- Câmera `CAM_Walkthrough`: trajeto animado até a convivência, {g['walk_frames']} frames a 30 fps. A ferramenta `walk_bunker.py` permite inspeção livre com colisão simplificada e altura de escada; instruções em `docs/NAVIGATION.md`.

## Exportação e edição

FBX do bunker com caixas UCX separadas e GLB visual com hierarquia; amostra FBX de 1 m. Arquivos em `exports/`. A exportação FBX usa cópias temporárias de malhas compartilhadas para contornar avisos de slots de material desse exportador; a cena mestre mantém módulos vinculados. Validar pivôs, orientação, hierarquia e reconhecimento de colisões na Unreal antes de produzir arte final.

| Coleção | Objetos |
|---|---:|
{cols}

Inventário nominal: `logs/object_inventory.json`; portas e rotas: `exports/navigation.json`; mobiliário e contagens: `logs/generation.json`; hashes: `logs/artifact_manifest.json`.

## Correções realizadas durante B1

Foi detectado e corrigido isolamento do sanitário (passagem adicional na convivência e reposicionamento do sofá), avanço de portas sobre o corredor, paredes duplicadas no encontro gerador/despensa, cruzamentos na junção escada/perímetro e fendas de circulação entre ambientes técnicos. Volumes técnicos fecham as fendas. Também foram corrigidos o apoio contínuo no patamar inferior e a orientação externa das faces. A cena foi regenerada após essas correções.

## Limitações e gate

Unreal Editor não localizado na auditoria: não houve importação na UE5, teste de CharacterMovement, rede, voz, oclusão acústica ou quatro clientes. Nenhum FPS-alvo foi declarado. Alternativa apresentada: concluir inspeção Blender agora e validar importação em instalação Unreal posteriormente, mantendo engine e escopo do GDD.

A atmosfera aqui é estudo de luz e distribuição; desgaste, tubulação detalhada, utensílios, props pequenos, modelos finais, áudio e interação aguardam B2/U1. As áreas técnicas vazias e o volume fechado ao nordeste são reserva estrutural, não novos ambientes de gameplay. Ferramenta de navegação tem colisão conservadora por caixas, portas fixas e ausência de gravidade física: serve para avaliar escala/circulação.

Scripts e documentação sob Git local; .blend, exports e PNGs ficam fora do Git e possuem hashes. Adotar LFS ou armazenamento de assets antes de distribuição. Não foi publicado nada.

**Próxima decisão:** revisar layout B1 e resolver a validação Unreal; só avançar para detalhamento B2 após aprovação explícita do usuário.
'''
(r/'docs/BLOCKOUT_REPORT.md').write_text(text)
files=[p for folder in ['blender','exports','screenshots','scripts','docs'] for p in (r/folder).glob('*') if p.is_file() and not p.name.endswith('.blend1')]
(r/'logs/artifact_manifest.json').write_text(json.dumps({str(p.relative_to(r)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files},indent=2))
