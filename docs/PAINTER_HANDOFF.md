# Kit de acabamento — Condomínio 13

## Estado atualizado em 19/10/2026

O Painter 12.1.5 está instalado e operacional. Após a ativação informada pelo usuário, a API criou, editou, salvou e reabriu três projetos `.spp`; a barreira anterior de instalação/licença foi resolvida.

Os projetos são `painter/SM_Hero_Bed.spp`, `painter/SM_Hero_Locker.spp` e `painter/SM_Hero_BlastDoor.spp`. Os 33 mapas de textura ficam em `assets/painter/`, separados por modelo. As fontes editáveis grandes permanecem salvas localmente, fora do Git; os scripts, mapas exportados e relatórios são versionados.

## Entregáveis

- Fonte editável: `blender/Bunker_HeroKit_v001.blend`.
- Modelos individuais: `exports/hero_kit/SM_Hero_Bed.fbx`, `SM_Hero_Locker.fbx` e `SM_Hero_BlastDoor.fbx`.
- Prévia de modelagem em estúdio: `screenshots/hero_kit.png` (render Blender, não captura do jogo nem pintura no Painter).
- Relatórios de geração/importação: `logs/hero_kit.json` e `logs/hero_kit_unreal.json`.
- Fonte reproduzível: `scripts/create_hero_kit.py` e `scripts/install_hero_kit.py`.

| Modelo | Triângulos | Dimensão importada | Estado |
|---|---:|---|---|
| Cama | 2632 | 111,5 × 211 × 95 cm | Quatro substituições no dormitório |
| Armário | 3424 | 53,5 × 81,2 × 184 cm | Quatro substituições no dormitório |
| Porta blindada | 2552 | 187 × 40,5 × 240 cm | Asset importado; portas existentes ainda não substituídas |

As partes têm bordas biseladas, materiais separados e UVs gerados e verificados dentro do intervalo 0–1. A porta usa pivô na dobradiça. A verificação do intervalo UV não comprova ausência de sobreposição: inspecionar e fazer bake no Painter antes de aprovar a pintura.

## Build Mac desta revisão

Na revisão final de 19/10, o cook terminou com zero erros e zero avisos, BuildCookRun retornou sucesso e a assinatura do aplicativo atualizado passou em `codesign --verify --deep --strict`. O aplicativo foi atualizado em `builds/Mac/Condominio13-VerticalSlice.app`. A captura nativa da janela voltou a funcionar: o dormitório foi conferido no executável, sem os blocos B1 sob as camas, e as ações E/F foram executadas e observadas. Esse teste confirma entrada/saída do estado de descanso; não confirma animação corporal nem recuperação real de energia, que ainda são sistemas pendentes.

## Trabalho executado no Painter

1. Três projetos em 1024px, normal DirectX e materiais separados pelo FBX.
2. Bake concluído de normal, world-space normal, AO, curvature e position nos onze conjuntos de textura.
3. Materiais inteligentes locais do Painter, com ajustes de cor e redução das camadas de dano: aço pintado verde, aço escuro, lona, linho e borracha. A camada de rasgos foi desativada para manter o tecido habitável.
4. Exportação própria BaseColor/Normal/ORM, 33 arquivos PNG de 1024 × 1024, todos abertos e verificados.
5. Onze materiais na Unreal usam UV0 dos modelos e os mapas exportados; color space e compressão apropriados por mapa.
6. Três `.spp` reabertos e verificados quanto a conjuntos, mapas de bake e camadas C13. Relatórios: `logs/painter_production.json`, `logs/painter_verify.json` e `logs/painter_unreal.json`.

A prévia `screenshots/painter_kit_final.png` é um render Blender dos arquivos exportados pelo Painter. A revisão no jogo revelou os blocos B1 antigos sob camas/armários, que foram removidos do exportador arquitetônico. Ainda pendentes neste kit: placas e textos narrativos próprios, costuras modeladas ou pintadas especificamente e substituição funcional das portas existentes.

## Limites para lançamento

Este kit é avanço de arte, não conclusão do jogo. Permanecem as pendências de gameplay e validação registradas em `PRODUCTION_STATUS.md`, inclusive multiplayer autoritativo, sobrevivência, salvamento, expedição, inimigos, áudio, voz e final de partida. A build Windows e a distribuição Steam precisam de ambiente, configuração e testes próprios.
