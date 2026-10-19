# Primeira pessoa: mãos e uso de itens — 19/10/2026

## Escopo

Primeira versão de gestos curtos para coleta, beber água, comer com colher e aplicar curativo. O servidor continua validando a transação; somente uma confirmação aceita chama a apresentação do dono. A mochila fecha ao usar o item para liberar a visão e os controles.

As luvas são modelos reais produzidos no Blender, com punho, palma, dedos dobrados, polegar, reforços e costuras. Esta versão usa poses de pegada fixas e transformações procedurais de braços/objetos. Não é um rig com dedos articulados e não inclui animações do corpo vistas pelos colegas.

## Fontes

- `blender/Bunker_Hands_v001.blend`: peças editáveis e malhas exportadas de luvas esquerda/direita, colher e rolo de gaze.
- `blender/Bunker_ItemUseVariants_v001.blend`: recipientes abertos derivados das peças originais, sem mudar os pickups de mundo.
- `exports/hands/`: seis FBXs; `/Game/Bunker/Hands`: malhas correspondentes.
- `scripts/create_first_person_hands.py`, `scripts/create_item_use_variants.py`, `scripts/install_first_person_hands.py`: pipeline reproduzível.
- As luvas e acessórios na Unreal reutilizam os materiais texturizados de tecido, borracha, linho e aço do kit Painter anterior. Não foram criados novos projetos Painter nesta etapa. O render Blender usa materiais procedurais de avaliação.

## Comportamento

- E: após uma coleta válida, gesto breve de recolher o objeto.
- I, seleção, U: o servidor aceita o consumo, remove a unidade e aplica o efeito. A interface fecha e aparece o gesto correspondente.
- Garrafa e lata trocam para variantes abertas durante a elevação. A tampa/lacre não têm uma animação separada de remoção nesta versão.
- I durante o gesto abre a mochila e encerra a apresentação. Isso não devolve o recurso já consumido.
- Morte/descanso interrompem a apresentação. Olhar e movimento não são travados pelo gesto.
- Mãos e objeto de apresentação não têm colisão, rigid-body ou replicação global. Duas luzes sem sombras e de alcance curto iluminam apenas o canal da apresentação, evitando que as luzes fortes do bunker estourem as luvas. O objeto largado no mundo continua usando o sistema autoritativo anterior.
- Durações de uso e coleta são campos editáveis de `DA_SurvivalRules`; o uso também controla o intervalo mínimo para outra transação do mesmo jogador.

## Evidências

- `logs/hands_source_validation.json`: PASS; duas fontes Blender reabertas, seis malhas com geometria finita, UVs válidas, escala aplicada e exports verificados por hash. As duas luvas têm 9.392 triângulos no total, além dos acessórios.
- `logs/hands_unreal.json`: seis malhas importadas em centímetros e materiais texturizados resolvidos.
- `logs/hands_package.log`: BUILD SUCCESSFUL, ExitCode 0; aplicativo instalado e assinatura verificada.
- `logs/hands_playtest_result.json`: PASS no executável final; quatro ações confirmadas (três usos e uma coleta), cinco capturas durante gestos ativos e meshes de ambas as luvas presentes. Alimentação/hidratação chegaram a aproximadamente 75, saúde a 80; repetir o GUID médico consumido não disparou outra apresentação nem efeito. Mochila fechada e olhar liberado na auditoria final.
- Cinco capturas `screenshots/hands_*.png` inspecionadas. As luvas, utensílios e variantes abertas são geometria da cena, não desenhos na HUD. Os gestos e o contato das mãos ainda são uma primeira aproximação.

A primeira execução visual reprovou: o auxiliar de teclas só permitia outro cenário de desenvolvimento e ignorava I/U/E. O portão foi corrigido somente para o novo cenário. A inspeção também corrigiu o enquadramento, os punhos, o sentido da colher e o gargalo obstruído por um cilindro de lacre. Evidência em `logs/hands_first_result.json`.

A primeira tentativa com quatro processos terminou por comandos de saída antes da auditoria final (sem falha fatal identificada), durante outra etapa de produção. Não foi considerada aprovação. A repetição final rodou sem empacotamento simultâneo e com RenderOffScreen: `logs/hands_network_final_result.json` PASS, quatro processos reais do executável. Consumo único, descarte/recolha com GUID e malha preservados, privacidade, cama e porta passaram; quatro confirmações de apresentação ocorreram em controladores locais com ambas as luvas carregadas. A tentativa incompleta foi preservada em `logs/hands_network_result.json`. Não foi determinada a origem dos pedidos de saída na primeira tentativa. Não houve teste com quatro humanos nem benchmark de FPS.

## Pendências de acabamento

Animações articuladas, som de manuseio, transições de tampa/anel, sincronização da atuação corporal para terceiros e benchmark permanecem pendentes. O gesto curto atende à apresentação funcional inicial, não encerra a produção de animação do jogo.
