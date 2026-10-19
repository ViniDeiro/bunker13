# Acabamento do kit no Painter — 19/10/2026

## Entrega

Substance 3D Painter 12.1.5 usado efetivamente na produção de cama, armário e porta blindada. Três fontes `.spp` salvas em `painter/`, onze conjuntos de textura e 33 mapas BaseColor/Normal DirectX/ORM de 1024px em `assets/painter/`.

## Processo e integridade

- Bake de normal, world-space normal, AO, curvature e position: sucesso nos três modelos.
- Materiais inteligentes fornecidos localmente pelo Painter, com camadas nomeadas C13 e ajustes de cor/desgaste; os nomes das bases e as árvores de camadas constam nos manifests.
- Revisão 2: tecido sem a camada de rasgos, desgaste de bordas mais suave e sujeira reduzida.
- Três arquivos `.spp` reabertos; conjuntos 4/4/3, mapas de apoio presentes e camadas editáveis preservadas.
- Todos os 33 PNGs foram abertos e verificados em 1024 × 1024.
- Onze materiais importados na Unreal, com texturas de cor em sRGB, normal comprimida como Normalmap e ORM sem sRGB. Projeção UV0, sem substituir o restante do bunker.
- O teste visual no executável mostrou as texturas aplicadas às camas e revelou geometria antiga sob elas. O exportador foi corrigido para excluir oito proxies B1 de camas e armários. As dimensões da arquitetura permanecem 28,8 × 30,3 × 7,88 m.

## Fontes e evidências

- `scripts/painter_production.py`: criação, baking, camadas, exportação, salvamento e reabertura.
- `scripts/c13_painter_bridge.py`: entrada local pelo menu Python do Painter; executa somente o script fixo do projeto.
- `scripts/import_painter_kit.py`: texturas e materiais UV na Unreal.
- `scripts/render_painter_kit.py`: render de revisão com os arquivos reais exportados.
- `logs/painter_production.json`, `logs/painter_verify.json`, `logs/painter_unreal.json`.
- `screenshots/painter_kit_final.png`: render de revisão, não captura do executável.

## Validação da revisão final no executável

Cook com zero erros e zero avisos, BuildCookRun concluído e assinatura verificada. Mapa `/Game/Bunker/Lvl_Bunker` carregado no Mac. Conferência pela captura nativa da janela confirmou os materiais e a retirada dos proxies sob as camas. E entrou no estado de descanso (mensagem contextual observada); F saiu dele e restabeleceu a movimentação. O teste não equivale a uma animação de deitar nem prova recuperação de energia. O aplicativo atualizado ficou aberto para inspeção do usuário.

## Limites da entrega

O acabamento deste kit não encerra a arte do bunker. A porta está disponível como asset, ainda sem substituir as portas arquitetônicas existentes. Gameplay, rede, salvamento, IA e lançamento continuam sujeitos aos marcos e testes descritos em `PRODUCTION_STATUS.md`. Não foi medido benchmark de FPS nesta etapa.
