# Armários, despensa e garrafa azul — 19/10/2026

## Entrega

Quatro armários existentes do dormitório foram convertidos em contêineres e dois armários de suprimentos foram instalados na despensa, usando o modelo refinado com texturas Painter já existente. A arquitetura e os vãos não foram alterados. Os estoques de produção começam vazios: os seis pickups do mapa podem ser coletados e guardados.

A garrafa agora é azul no mundo e na variante de consumo. A fonte Blender e os rótulos foram atualizados, mantendo as dimensões e a identidade dos itens. Os gestos anteriores não receberam novo refinamento nesta etapa.

## Controles

- E olhando para um armário abre o armazenamento.
- TAB alterna entre armário e mochila; setas selecionam; X transfere uma unidade.
- E ou I fecha e libera olhar/movimento.
- A interface mostra a capacidade e o peso de cada lado. Os armários do dormitório comportam 12 unidades/30 kg e os da despensa 24/60 kg, editáveis por ator.

## Rede e privacidade

O servidor valida sessão de acesso, saúde/descanso, distância, linha de visão, revisão do conteúdo, ID e capacidade. A transferência preserva GUID, tipo, malha, materiais e escala; apenas o peso é conferido pela definição autoritativa do item. Nenhuma malha de mundo é duplicada ao guardar/retirar.

Contêineres permitem acesso concorrente. Uma revisão obsoleta é rejeitada e atualizada; uma transação completa altera as duas listas e incrementa a revisão no servidor antes de enviar novas vistas aos observadores autorizados. Os conteúdos não replicam como inventário global: cada jogador recebe somente a vista do armário que abriu. Sair do alcance, morrer ou fechar a tela revoga o acesso e apaga a vista local. Consumo/descarte ficam indisponíveis enquanto o armário está aberto, preservando a consistência da tela.

Todos os armários são compartilhados e destrancados nesta etapa, inclusive os do dormitório. Não há autorização exclusiva por dono, cadeado ou animação de porta abrindo. O modelo físico já refinado é o ponto de interação; os itens guardados são mantidos como unidades do contêiner, sem desenhar cada objeto nas prateleiras internas.

## Evidências

- `logs/storage_install.json`: seis contêineres instalados, vazios no mapa de produção.
- `logs/storage_package.log`: BUILD SUCCESSFUL, ExitCode 0; assinatura do aplicativo verificada.
- `logs/storage_visual_result.json`: PASS no executável. E/TAB/setas/X/I retiraram e devolveram a mesma garrafa, preservando GUID; o kit médico permaneceu na mochila. Ao fechar, a vista ficou vazia e olhar/movimento foram liberados. Três capturas (`storage_2.png`, `storage_4.png`, `storage_8.png`) foram produzidas; a primeira e a última inspecionadas.
- `logs/storage_network_result.json`: PASS com quatro processos reais do executável. Todos abriram a vista inicial. Houve exatamente uma retirada e uma devolução; GUID único em todas as auditorias. Pedidos obsoletos, acesso remoto sem sessão, mochila sem espaços e excesso de peso foram rejeitados. As quatro vistas foram apagadas ao fechar e os controles liberados. Os dados dos contêineres não apareceram como Contents replicado nos clientes.
- `logs/item_validation.json` e `logs/hands_source_validation.json`: fontes Blender reabertas, UVs/dimensões/arquivos verificados após a revisão azul.

O primeiro teste visual escolheu o kit médico depois de TAB porque a seleção direta ocorria antes de o evento de tecla ser processado; o roteiro passou a usar uma seta em um passo separado. A primeira rede executou o roteiro apenas no host porque procurava um nome de ator que difere nos clientes; o cenário passou a localizar o alvo pelo campo replicado. As duas tentativas reprovaram os critérios completos e foram preservadas em `storage_visual_first_result.json` e `storage_network_first_result.json`. As aprovações acima são das repetições corrigidas.

`logs/storage_regression_result.json`: PASS com quatro processos do executável, repetindo coleta/consumo/descarte/recolha, privacidade, mãos locais, exclusividade da cama e abertura/colisão das portas. A mesma malha e GUID sobreviveram ao descarte. `logs/blue_water_hands_result.json`: PASS na repetição dos três consumos e coleta com a revisão azul, preservando os gestos anteriores. As aprovações automatizadas não substituem quatro pessoas jogando.

## Limites

O conteúdo permanece durante a sessão atual. Salvamento após fechar o jogo, reconexão, migração de host e empilhamento ainda não foram implementados. Esta entrega não deve ser interpretada como aprovação de persistência entre partidas ou de teste prolongado com quatro humanos. Não houve benchmark de FPS.

Fontes: `BunkerInventoryTypes.h`, `BunkerContainer.h/.cpp`, `BunkerStorageValidation.cpp`, `scripts/install_storage.py`, `scripts/run_storage_network.py`, `scripts/run_storage_visual.py`. A garrafa continua editável em `blender/Bunker_Items_v001.blend`; a variante aberta em `blender/Bunker_ItemUseVariants_v001.blend`.
