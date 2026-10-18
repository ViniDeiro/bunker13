# Kit de acabamento — Condomínio 13

## Estado verificado em 18/10/2026

O Creative Cloud está instalado e conectado. A página Substance 3D Painter 12.1.5 mostra “Teste grátis” e “Comprar”; o executável do Painter não foi encontrado em Applications nem pelo índice do macOS. Nenhum teste ou assinatura foi ativado pelo agente. A etapa de licença depende do titular da conta.

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

O cook terminou com zero erros e zero avisos, BuildCookRun retornou sucesso e a assinatura do aplicativo atualizado passou em `codesign --verify --deep --strict`. O aplicativo foi atualizado em `builds/Mac/Condominio13-VerticalSlice.app`. A tentativa de inspeção da janela pelo controle de interface retornou “screen capture size is invalid (0.0, 0.0)”; a validação visual em execução e o teste de deitar/levantar desta revisão permanecem pendentes. O render do kit não substitui esses testes.

## Trabalho no Painter após a ativação

1. Criar projeto por modelo com o FBX correspondente, normal DirectX e resolução inicial 1024.
2. Fazer bake de normal, world-space normal, AO, curvature e position; conferir artefatos em cada conjunto de textura.
3. Aplicar aço nas partes expostas e pintura verde desbotada nas chapas. Restringir desgaste às bordas e áreas de uso; ferrugem em fixações e regiões de acúmulo, evitando cobertura uniforme.
4. Cama: tecido de trama fina, costuras e manchas discretas; armário: placa de identificação, riscos próximos ao puxador e poeira nas venezianas; porta: borracha da vedação, marca de inspeção e desgaste no volante.
5. Exportar mapas para Unreal em BaseColor, Normal DirectX e ORM. Validar resolução e canais antes de substituir os materiais provisórios.
6. Salvar os projetos `.spp` e validar os modelos dentro do executável. Nenhum `.spp` foi criado nesta etapa.

## Limites para lançamento

Este kit é avanço de arte, não conclusão do jogo. Permanecem as pendências de gameplay e validação registradas em `PRODUCTION_STATUS.md`, inclusive multiplayer autoritativo, sobrevivência, salvamento, expedição, inimigos, áudio, voz e final de partida. A build Windows e a distribuição Steam precisam de ambiente, configuração e testes próprios.
