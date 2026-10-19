# Objetos físicos do inventário — 19/10/2026

A interface de mochila não substitui os objetos. Esta etapa cria cinco modelos próprios no Blender e aplica suas malhas e texturas aos seis pickups existentes, sem mudar a arquitetura do bunker ou os efeitos dos consumíveis. Os pickups foram apoiados em móveis reais, fora das rotas.

| Item | Design e geometria | Dimensões aproximadas |
|---|---|---|
| Água | Frasco industrial opaco de 500 mL, ombros, tampa estriada, lacre, anéis e rótulo Defesa Civil | 7,1 × 7,1 × 21,4 cm |
| Alimento | Lata Aurora, costuras enroladas, tampa rebaixada e anel de abertura | 8,7 × 8,7 × 12,6 cm |
| Kit médico | Estojo rígido verde, junta de borracha, fechos, dobradiças, alça e placa de primeiros socorros | 28 × 12,3 × 20,6 cm |
| Pilha | Célula D com capa, isolante e terminais distintos | 3,5 × 3,5 × 6,3 cm |
| Ferramenta | Chave de manutenção com mandíbula aberta, rosca de ajuste, cabo e identificação patrimonial | 7,6 × 26,9 × 2,6 cm |

## Fontes e organização

- `blender/Bunker_Items_v001.blend`: fonte reaberta e validada; coleções ITEM por tipo com peças editáveis preservadas e cópias unidas SM para exportação. Texturas incorporadas.
- `exports/items/SM_Item_*.fbx`: cinco exportações em metros, transformações aplicadas e pivô na base.
- `assets/items/`: quinze mapas de 1024 px: BaseColor, Normal DirectX e ORM. Um material e três texturas por modelo.
- `scripts/create_item_textures.py`: identidade fictícia, tipografia de rótulos, cores e desgaste de superfície reproduzíveis.
- `scripts/create_item_kit.py`: geometria, UVs, materiais, exportação e renders.
- `scripts/validate_item_kit.py`: reabertura e verificação de geometria finita, UVs, escala, peças editáveis, imagens incorporadas e presença dos exports.
- `scripts/install_item_kit.py`: importação Unreal e substituição dos pickups, ajustando o apoio em móveis e preservando a identidade funcional. Regenerar o mapa reaplica este kit.

As texturas desta etapa são originais, produzidas por código e aplicadas no Blender. Não são exports do Substance Painter e não há fontes `.spp` destes cinco itens nesta entrega. Os `.spp` de cama, armário e porta da etapa anterior continuam separados.

## Verificação de arte e importação

As cinco vistas individuais e a vista conjunta foram renderizadas. Vista conjunta e os cinco close-ups inspecionados. Os rótulos, materiais e formas estão presentes nos modelos reais; não são elementos desenhados sobre a interface.

`logs/item_kit.json`, `logs/item_validation.json` e `logs/item_unreal.json` registram malhas, dimensões e importação. São 21.188 triângulos ao todo nos cinco modelos, sem Nanite e sem rigid-body. Na reabertura, o volume assinado das peças fechadas confirmou normais externas. As partes de fabricação se sobrepõem intencionalmente; rótulos são superfícies abertas ligeiramente afastadas da embalagem. Não se exige uma única malha estanque para props de jogo.

## Validação no jogo

O empacotamento Mac Development terminou com `BUILD SUCCESSFUL` e ExitCode 0 (`logs/item_package.log`); assinatura verificada. O executável carregou os cinco modelos com escala 1 e produziu cinco capturas `screenshots/item_game_*.png`, todas inspecionadas. São close-ups por câmera temporária de inspeção no próprio mapa, sem adicionar luzes ou modificar o estado salvo. A iluminação quente/fria do ambiente muda a aparência em relação ao estúdio Blender. O enquadramento inicial cortava a tampa da garrafa; a câmera de inspeção foi ampliada na revisão final.

A primeira inspeção encontrou objetos junto de proxies maiores e câmeras voltadas para a traseira; posicionamento e câmeras foram corrigidos. As duas águas agora ficam na caixa da despensa e na mesa da cozinha; lata na cozinha; estojo no carrinho médico; pilha na mesa do rádio; ferramenta na bancada. Nenhuma parede ou passagem foi alterada.

`logs/items_final_result.json`: PASS, quatro processos reais do executável, três clientes remotos. O ciclo com a garrafa real consumiu uma unidade, resistiu a pedidos repetidos, descartou/recolheu mantendo GUID, malha `SM_Item_Water` e escala 1. A réplica da mochila do dono também manteve a malha; os atributos privados e as regressões de cama/porta passaram. O teste de transações usa a garrafa, não percorre individualmente os cinco tipos. Não substitui uma sessão com quatro humanos.

Após esse teste foram revisadas somente as normais externas das peças (especialmente a mandíbula da chave) e o enquadramento de inspeção; a lógica de interação permaneceu igual.

## Limites

Este é o primeiro conjunto de cinco tipos, não os 12–20 tipos do protótipo nem os 50–80 planejados para lançamento. O frasco é plástico opaco: não usa transparência/refração custosa. LODs específicos e benchmark por hardware ainda não foram feitos. A pilha e a ferramenta têm geometria própria, mas seus sistemas de energia/reparo permanecem pendentes. As mãos e animações de abrir/comer/beber ainda precisam ser produzidas; esta etapa entrega os objetos de mundo, a coleta e o descarte.
