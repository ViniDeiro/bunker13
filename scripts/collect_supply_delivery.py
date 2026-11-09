"""Publish only after final-binary functional checks and the actual exterior image review."""
from pathlib import Path
import json, hashlib, subprocess, shutil
R=Path(__file__).resolve().parents[1]
def load(name):return json.loads((R/'logs'/name).read_text())
manifest=load('supply_delivery_manifest.json');assert manifest['passed']
exe=R/'builds/Mac/Condominio13-Expedition.app/Contents/MacOS/Condominio13'
assert hashlib.sha256(exe.read_bytes()).hexdigest()==manifest['executable_sha256']
baseline=load('airlock_asset_baseline.json');assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in baseline.items())
assert hashlib.sha256((R/'builds/Mac/Condominio13-Airlock.app/Contents/MacOS/Condominio13').read_bytes()).hexdigest()==load('airlock_delivery_manifest.json')['executable_sha256']
assert load('supply_blender_validation.json')['passed']
check=subprocess.run(['codesign','--verify','--deep','--strict',str(R/'builds/Mac/Condominio13-Expedition.app')],capture_output=True,text=True);assert check.returncode==0,check.stderr
for mode in ('seed','continue','full'):
 text=(R/f'logs/supply_package_{mode}_host.log').read_text(errors='replace')
 assert 'C13_SUPPLY_PARKING_FIXED count=1' in text, 'Final lighting fix was not tested'
for role in ('client1','client2','client3'):
 text=(R/f'logs/supply_package_continue_{role}.log').read_text(errors='replace')
 assert text.rfind('C13_INFRA_POWER light=1 services=1')>text.find('C13_INFRA_POWER light=0 services=0')>=0
for name in ('supply_exterior.png','supply_power_restored.png','supply_bunker_client.png','supply_resumed.png','supply_exterior_before_lighting.png'):
 assert (R/'screenshots'/name).stat().st_size>1000
rows=[]
for case,label in (('seed','4 conexões: saída'),('continue','4 conexões: retorno'),('solo','1 instância')):
 d=load(f'supply_verified_{case}.json')
 for row in d['fps']:rows.append(dict(scenario=label,resolution=d['resolution'],**row))
fps='\n'.join(f"| {r['scenario']} / {r['role']} | {r['resolution']} | {r['fps']:.2f} | {r['p95_ms']:.2f} |" for r in rows)
manifest['artifact_checks']=dict(codesign=True,original_assets_unchanged=len(baseline),editable_blend_reopened=True,parking_channel_fixed_in_final_binary=True,three_clients_observed_power_off_then_on=True)
manifest['fps']=rows
(R/'logs/supply_delivery_manifest.json').write_text(json.dumps(manifest,indent=2))
audio={f.name:f.read_text(errors='replace').count('Audio Buffer Underrun') for f in (R/'logs').glob('supply_package_*_*.log')};audio={k:v for k,v in audio.items() if v}
report=f'''# Condomínio 13 — primeira reposição externa / 0.4.2

05/11/2026 — America/Sao_Paulo. Agora há um percurso funcional de reposição: sair do bunker, subir ao mercado, explorar o estacionamento, recolher combustível e peças, voltar pela antecâmara e recuperar energia. **Isso não conclui o jogo, nem a vertical slice U3 completa do GDD:** radiação, inimigos, combate, morte e comunicação limitada ainda não foram implementados.

## O que mudou

O estacionamento existente contém seis objetos físicos: dois galões de 2 L, dois conjuntos de peças e dois cartuchos de água. São os mesmos três tipos/modelos da infraestrutura, com PBR e interação por E; não são seis tipos novos. O projeto continua com oito tipos definidos, abaixo da meta de 12–20 do MVP.

Cada unidade possui chave de mundo e GUID próprios. Coletar remove a unidade do chão e usa a mochila existente; peso, slots e concorrência são validados pelo host. Voltar não concede uma recompensa abstrata: o jogador precisa transportar e usar o item no painel real. No ensaio, o combustível levou o tanque de 0 a 2 L e as peças elevaram a condição de 20 a 60%; ligar o gerador restaurou circuitos, luzes e filtragem, com desgaste/consumo retomados.

Não há abastecimento automático ao sair, carregar ou começar outro dia. O estoque externo é finito e introduzido uma única vez por campanha atualizada. Também pode ser alcançado durante a coleta inicial: não criamos uma trava artificial para obrigar uma expedição. As reservas locais anteriores continuam existentes. A escassez e a cooperação espontânea ainda precisam de balanceamento e sessão humana.

## Dois problemas encontrados no jogo e corrigidos

1. **Queda ao retornar:** havia um vão entre a borda do piso do mercado e o estacionamento. A ida passou, mas a volta caiu abaixo do mapa. Foi adicionado um patamar de 12,4 × 3 × 0,18 m dentro do acesso existente, com degrau de 18,45 cm para o mercado. O percurso corrigido passou sem salto. Não foi criado um novo prédio ou região.
2. **Estacionamento preto nas capturas:** uma regra antiga classificava o piso externo como parte do bunker pela altura da raiz do objeto, atribuindo o canal de luz errado. Restauramos o canal externo do estacionamento. As imagens foram verificadas no jogo; não bastou o teste de lógica passar. A sala aprovada e os materiais existentes não foram substituídos.

O patamar é instanciado em runtime, com colisão real e material externo existente com projeção em escala física. A fonte Blender e o FBX do módulo permitem editar sua geometria; posição/dimensões atuais também estão no código. O nível salvo não foi regravado. A iluminação externa existente é independente do gerador do bunker; sua alimentação/reserva externa ainda não é simulada.

Antes da correção de canal: `screenshots/supply_exterior_before_lighting.png`. Depois: `screenshots/supply_exterior.png`. O exterior ainda é um recorte de protótipo, sem aprovação comercial de arte.

## Salvamento e autoridade

O novo marcador `bExternalSupplies` permite ausência das seis chaves somente ao ler um checkpoint anterior à introdução do estoque. Depois disso todas são obrigatórias, inclusive os registros dos objetos já recolhidos/consumidos. O fingerprint e as chaves legadas foram mantidos; os IDs antigos não foram trocados.

Antes da migração, as duas cópias originais são copiadas integralmente para slots `_PreSupplyV1_`, com verificação dos bytes. A primeira gravação introduz os objetos uma vez; um segundo processo retomou os mesmos seis GUIDs. Os aplicativos anteriores foram preservados, mas não devem abrir a campanha já migrada; a recuperação exige o backup anterior. Não há menu de rollback automático. A bateria conferiu também checksum do arquivo e preservação do GUID do item da versão 0.4.1. Checkpoints incompletos, misturados ou com chave duplicada foram rejeitados em ensaios do validador, sem gravar esses casos inválidos sobre a campanha.

Inventário privado, salvamento alternado e reconexão continuam sendo os sistemas existentes. Não há contabilidade paralela de expedição, mensagem global de coleta ou aviso automático de morte.

## Validação executada no aplicativo Mac

| Ensaio | Resultado |
|---|---|
| Concorrência com quatro conexões | Um cliente remoto recebeu a unidade; somente um proprietário. |
| Mochila cheia / peso excedido | E foi rejeitado, mantendo o mesmo objeto no chão. Inventários cheios são fixtures de teste. |
| Saída e coleta | Coleta inicial/fechamento executados, antecâmara sem energia, escada, mercado e estacionamento por movimento real. |
| Reinício do host fora | Checkpoint no estacionamento com dois itens; host retomou naquele local, e os três participantes reconectaram. |
| Retorno e manutenção | Retorno físico; os mesmos dois GUIDs foram consumidos uma vez; os três clientes observaram energia desligada e depois ligada. |
| Retomada após consumo | Mesmos seis GUIDs, dois registros consumidos/inativos; estoque não reapareceu. |
| Percurso contínuo com uma instância | Ida, coleta, retorno e recuperação em uma execução, a 1280×720. |
| Migração real 0.4.1 → 0.4.2 | ID antigo e cronômetro preservados; backups brutos verificados; seis novos IDs persistiram em outro carregamento. |

Foram quatro processos locais com 80 ms / 2% de perda simulada: dois renderizados e dois sem renderização, para limitar a carga do Mac. Não foram quatro humanos ou quatro computadores. A expedição cooperativa testada usa o host como explorador e três participantes no bunker; o teste de concorrência comprova coleta por cliente remoto, mas não equivale a uma expedição inteira com um cliente remoto como explorador.

A crise é preparada pelo fixture (tanque vazio e condição 20), depois do fechamento real. Só o posicionamento inicial é preparado por teleporte. Entre saída, coleta e retorno, o personagem utiliza CharacterMovement; a retomada de checkpoint restaura a posição salva. A duração de coleta nos testes é 35 s; no jogo normal continuam 90 s. Os atalhos de jogar não ativam fixtures nem inventários artificiais.

## Desempenho e falhas reais

| Cenário / processo | Janela | FPS médio | Frame p95 (ms) |
|---|---|---:|---:|
{fps}

Apple M2 / 24 GB. Amostras de aproximadamente 16 s no início da antecâmara durante a crise, com iluminação principal desligada; **não são medições do percurso inteiro**, do cenário normal totalmente iluminado, Windows ou quatro máquinas. A execução com uma instância é um host local sem outros participantes. Não comparar estes valores como ganho de otimização sobre relatórios anteriores, que usaram outras vistas/cargas. A carga de quatro processos no mesmo Mac continua alta e não há garantia de 60 FPS.

Houve falha nativa antes de gerar logs em uma tentativa de retomada; só esse padrão conhecido foi repetido automaticamente, com a falha preservada em `logs/supply_*_startup_failure_*`. O problema de inicialização do Mac continua aberto. Avisos de falta de dados no buffer de áudio nesta bateria: `{audio}`. São limitações reais; testes funcionais aprovados não certificam estabilidade de lançamento.

## Como jogar esta versão

Abrir **`builds/Mac/Jogar-Expedicao.command`**. Para rede local, usar `Hospedar-Expedicao.command` e `Entrar-Expedicao.command`, com a mesma versão dos dois lados. Os atalhos escolhem o mapa e o modo corretos; abrir o `.app` diretamente ainda inicia o mapa padrão legado.

R inicia a coleta no host. Depois do fechamento, administrar combustível e manutenção; para sair, fechar a outra folha, usar E na porta de destino, esperar equalização e usar E novamente. No retorno pelo lado de fora, após equalizar, manter E pressionado para a liberação manual. Os recursos estão no estacionamento, depois da saída frontal do mercado. Olhar para o objeto e E recolhe; I abre a mochila. Não é preciso um modal de estoque para esses objetos.

Voltar e desligar o gerador antes de abastecer/reparar. E nos controles de combustível ou peças inicia o trabalho; manter distância/visada até concluir. Ligar o gerador depois. F5 salva no host. Reservas anteriores e o fluxo normal não foram substituídos por uma missão obrigatória.

## Arquivos

- Aplicativo: `builds/Mac/Condominio13-Expedition.app`, assinatura local verificada; versões 0.4.0/0.4.1 preservadas.
- Blender editável: `blender/Bunker_ExpeditionSupplies_v001.blend`, reaberto e validado; seis props com dois UVs e texturas incorporadas, mais o patamar PBR. Fontes originais de itens continuam em `Bunker_Infrastructure_v001.blend`.
- Módulo: `exports/expedition/SM_MarketEntryApron.fbx`; itens reutilizam os FBXs/importações anteriores. O runtime instancia geometria equivalente ao patamar, com o material externo existente.
- Scripts: `create_supply_layout.py`, `run_supply_validation.py`, `run_supply_delivery.py`, `collect_supply_delivery.py` em `scripts/`.
- Manifesto: `logs/supply_delivery_manifest.json`; identidade: `supply_identity_result.json`; migração: `supply_migration_result.json`; fonte Blender: `supply_blender_validation.json`.
- Capturas reais em `screenshots/supply_*.png`. Nenhum vídeo foi produzido nesta entrega.
- {len(baseline)} arquivos de mapas, assets aprovados e fontes anteriores permanecem iguais byte a byte. Os ajustes de acesso/iluminação são adicionais em runtime.

## O que falta e o próximo marco

Esta entrega fecha a reposição funcional de combustível/peças no recorte existente. Não conclui o U3 completo do GDD nem valida a sobrevivência social em uma sessão humana. Faltam radiação/proteção persistentes, inimigo/combate, morte e recuperação de equipamento, voz por distância/rádio, eventos, minijogo real e um objetivo com encerramento. Também faltam Windows/Steam/internet, testes humanos de 30–60 min, arte final do exterior e balanceamento para 1–4 pessoas.

Próximo marco proposto: **radiação e proteção no mesmo recorte**, com consequências que persistam ao voltar e ao reconectar. Dependências: este percurso, estados privados do jogador, equipamento físico e salvamento; aceite deve incluir acúmulo no host, proteção com desgaste, tratamento e retomada sem apagar exposição. Não iniciar inimigo/combate ou ampliar o mapa junto com esse marco.
'''
(R/'docs/EXPEDITION_REPORT.md').write_text(report)
for kind in ('Jogar','Hospedar','Entrar'):
 source=(R/f'builds/Mac/{kind}-Antecamara.command').read_text().replace('Condominio13-Airlock.app','Condominio13-Expedition.app')
 dest=R/f'builds/Mac/{kind}-Expedicao.command';dest.write_text(source);dest.chmod(0o755)
 alias=R/f'builds/Mac/{kind}-Coleta-MVP.command'
 if alias.exists():
  backup=R/'logs/supply_prior'/alias.name
  if not backup.exists():shutil.copy2(alias,backup)
  alias.write_text(source);alias.chmod(0o755)
status=R/'docs/PRODUCTION_STATUS.md';marker='## 05/11/2026 — Reposição externa / 0.4.2'
if marker not in status.read_text():
 with status.open('a') as f:f.write('\n\n'+marker+'\n\nPrimeiro percurso de reposição funcional no estacionamento existente: coleta física, antecâmara, retorno e uso dos mesmos GUIDs para recuperar o gerador. Estoque finito e migração aditiva verificados; quatro conexões com reinício do host e execução contínua com uma instância. Corrigidos vão no acesso e canal de luz do piso externo. Relatório: `docs/EXPEDITION_REPORT.md`; manifesto: `logs/supply_delivery_manifest.json`. Não marcar U3/MVP como concluído: radiação, inimigo/combate, morte, comunicação, eventos e encerramento continuam pendentes; sem expansão de mapa.\n')
print(json.dumps(dict(passed=True,report='docs/EXPEDITION_REPORT.md',fps=rows),indent=2))
