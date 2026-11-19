# Quarto de referência industrial estilizado — v001

13/11/2026. Primeiro estudo 3D próprio na linguagem solicitada a partir dos prints de CRACK. Não é substituição do bunker nem aprovação comercial de arte. A cena foi gerada em Blender e avaliada renderizando o mapa na Unreal, em modo de jogo do Editor.

## Criado

Quarto com 4,4 × 4,6 m de área interna, pé-direito de 2,8 m e entrada aberta de 1,20 m. Paredes, piso, teto, vigas, molduras e móveis possuem espessura real e colisão na cena. O piso de acesso externo prolonga a área de circulação; a caixa geométrica do grupo arquitetônico mede aproximadamente 4,60 × 6,25 × 2,94 m incluindo paredes e esse acesso, não o tamanho interno do quarto.

São 183 peças editáveis no Blender, organizadas em arquitetura, teto, cama, mobiliário, detalhes, sinalização e luminárias; 44.960 triângulos no total. Os sete grupos exportados/importados não são uma biblioteca final de cada móvel independente. A fonte mantém as peças para edição seletiva. Treze materiais PBR distinguem tinta, metal, borracha, tecido, madeira e piso; dois mapas normais próprios incorporados fornecem microdetalhe de pintura/tecido. Dois conjuntos UV por peça; não certificamos um atlas combinado pronto para bake de lightmap. Não há LODs finais nem Nanite validado.

Cama com estrutura chanfrada, colchão, travesseiro e manta moldada; bancada com monitor apoiado, teclado, banco e nichos; armário aberto com caixas apoiadas; criado-mudo, garrafa azul decorativa, tubulação, grelha e sinalização original de defesa civil. Não foram usados modelos, texturas, marcas ou cartazes do outro jogo.

## O que funciona e o que é visual

A cama usa a classe nativa existente: olhar e E inicia descanso, a energia aumenta, F levanta e libera a ocupação. Isso **não acrescenta animação corporal de deitar**, cobertor animado ou mãos articuladas. Bancada, monitor, caixas, garrafa e armário aberto são decoração nesta cena; não há novo estoque ou novos itens coletáveis. Não contar essas peças como tipos utilizáveis do MVP.

O estudo tem uma cama para avaliar o acabamento. Não substitui o dormitório de quatro jogadores nem comprova circulação simultânea de quatro humanos. As luminárias são constantes nesta cena isolada; ainda não estão ligadas aos circuitos da campanha. Energia, expedição e persistência do mapa principal não foram modificadas.

## Validação real

- Fonte Blender salva, reaberta e conferida: 183 meshes, mínimo de dois UVs e duas imagens incorporadas.
- Sete FBXs importados, materiais atribuídos, escala da arquitetura conferida em centímetros e colisões complexas configuradas. Pivô da cama exportado na base/centro para o ator nativo, sem deslocar seu componente raiz.
- Build do Editor aprovado. Novo ensaio de desenvolvimento isolado em `BedroomStudyValidation.cpp`, despachado pelo arquivo de validação existente; não adiciona campos ao controlador nem altera transações de produção.
- Dois ensaios renderizados aprovados após correções: E descansa e aumenta energia; F libera cama; caminhada real do personagem até a entrada; sem commit de campanha.
- A preparação posiciona o personagem para as capturas e o teste da cama. Só a caminhada posterior é teste de locomoção; não chamar os posicionamentos de exploração real.
- Os 449 assets do manifesto anterior continuam iguais por tamanho/hash, incluindo mapas e fontes originais. O aplicativo de expedição 0.4.2 foi preservado; nenhum pacote novo foi gerado.

Não houve novo teste multiplayer, reconexão ou salvamento desta cena. As transações da cama foram reaproveitadas, mas reutilização de código não equivale a certificação de rede do novo layout. Não foram produzidos vídeo ou benchmark de sessão longa.

## Problemas encontrados durante a revisão

A primeira revisão de imagem revelou apoios faltantes e caixas acima das prateleiras; foram corrigidos suporte do monitor, pés do armário e contatos dos objetos. A primeira execução na Unreal mostrou exposição excessiva e cama fora do local: mover um componente raiz não cria um offset local independente do ator. Foi corrigido o pivô no FBX, reimportado o mapa e reduzida a exposição do estudo.

O primeiro driver também acompanhou o executável intermediário da Unreal, que redireciona para o `.app`; houve timeout e ausência dos marcadores no arquivo acompanhado. O driver agora abre o executável nativo do aplicativo e usa log absoluto. O resultado inicial reprovado e a captura com exposição errada foram preservados em `logs/bedroom_first_result.json` e `screenshots/bedroom_unreal_first_exposure.png`. As execuções seguintes comprovaram descanso, liberação e caminhada.

O render offline inicial foi interrompido para reduzir a carga; posteriormente a fonte foi reaberta e as duas vistas foram renderizadas em configuração leve. Não confundir o render Cycles com captura da Unreal. A imagem com sombras dinâmicas ainda tem sombras duras, diferenças de iluminação em relação ao Blender e serrilhado; esse acabamento precisa de refinamento antes de aprovação comercial.

## FPS observado

Apple Silicon / 24 GB, uma janela 1280 × 720, modo de jogo do Unreal Editor, limite mantido em 45 FPS. Janela de amostragem de aproximadamente 20 s durante enquadramentos, descanso e captura; não é benchmark do percurso do jogo completo. Outros aplicativos permaneceram abertos. O teste evita o modo ocioso quando a janela está fora de foco.

| Perfil | Resolução interna / sombras / AO | Média | Frame p95 |
|---|---|---:|---:|
| Leve | 70% / desligadas / desligado | 41,06 FPS | 49,92 ms |
| Referência visual | 100% / qualidade 2, resolução 512 / nível 1 | 31,78 FPS | 84,82 ms |

Os valores mostram uma limitação real de fluidez, principalmente no perfil visual; não declarar otimização concluída ou 60 FPS. São duas rodadas curtas, não isolamento estatístico do custo de cada efeito. Os overrides são apenas do processo de referência. As configurações leves do bunker não foram alteradas.

## Abrir e revisar

- `tools/launchers/Ver-Quarto-Referencia-Leve.command`: recomendado para começar no Mac, com o perfil leve medido.
- `tools/launchers/Ver-Quarto-Referencia.command`: perfil com sombras/AO e resolução interna completa, para comparação visual.
- Ambos usam a Unreal instalada, não um executável novo empacotado. São cenas locais de avaliação sem gravação de campanha. WASD/mouse, E na cama, F para levantar. F5 não salva nesta cena isolada.
- `blender/Bedroom_StyleStudy_v001.blend`: fonte editável com câmeras de perspectiva e superior.
- `exports/bedroom_study/`: sete FBXs, normais e manifesto. `unreal/Condominio13/Content/Bunker/BedroomStudy/`: mapa e assets novos.
- `screenshots/bedroom_unreal_overview.png` e `bedroom_unreal_rest.png`: capturas reais. `bedroom_blender.png` e `bedroom_top.png`: renders de revisão do Blender.
- Scripts: geração, correção de apoios/pivô, reabertura/render, importação e teste em `scripts/*bedroom*`.

Os novos arquivos permanecem locais para revisão visual; não houve push desta etapa. O manifesto da publicação anterior não foi alterado para fingir que novos assets já estavam naquele snapshot. Próximo passo depende da avaliação deste quarto: refinar iluminação e custo do perfil escolhido antes de integrar o estilo ao bunker. Armário físico completo, animações e conexão aos circuitos continuam pendentes neste estudo; não avançar para outros ambientes antes da aprovação visual.


## Continuidade — transição do descanso

Foi adicionada uma apresentação de câmera exclusiva do mapa de estudo: ao receber o estado de descanso existente, a visão se desloca até o travesseiro durante 1,15 s, com interpolação suave de posição e orientação. Ao levantar, volta à visão normal pelo mesmo tipo de transição. A implementação não altera a transação autoritativa de ocupação, o ganho de energia, os IDs ou os checkpoints. O reposicionamento do personagem no servidor permanece como antes.

Isso é uma transição em primeira pessoa; **não é uma animação corporal de deitar**, nem demonstra mãos apoiando na cama ou um corpo deitado visível para outro jogador. Essas animações e sua validação em rede continuam pendentes. Compilação e ensaio renderizado aprovados; os resultados desta rodada ficam em `docs/validation/bedroom_rest_2026-11-13.json`.

Antes do próximo marco (armário físico deste quarto), as dependências são: modelo com corpo e folha separados, pivô compatível com a dobradiça, espaço livre para a porta e reaproveitamento das transações de armazenamento existentes. Os critérios de aceitação são abrir/fechar com E sem modal; bloquear a folha contra o jogador; pegar e guardar o mesmo ID em prateleira; manter revisões e autoridade do host; e comprovar as mudanças em duas instâncias. A configuração atual do armário nativo contém uma chave fixa de persistência: ela precisa ser tratada antes de inserir um segundo armário, preservando a chave do armário original. O armário decorativo desta cena não atende esses critérios.


### Resultado da rodada de continuidade

Nove verificações aprovadas no jogo renderizado: encerramento limpo, energia aumentando, liberação da cama, caminhada, ausência de commit da campanha, captura geral, posição final da câmera, ponto intermediário da interpolação e registro de FPS. O ponto intermediário foi medido a 170,77 cm do destino; a posição final ficou dentro da tolerância de 2 cm. A revisão da captura confirmou que o corpo não atravessa mais a câmera: os componentes esqueléticos do próprio jogador usam ocultação para o dono durante o descanso, com restauração dos valores anteriores ao completar a saída.

Amostra de aproximadamente 20 s: **43,86 FPS**, frame p95 **22,23 ms**, 877 amostras, janela 1280 × 720, resolução interna 100%, sombras 2/512 e AO 1. O limite de 45 FPS foi aplicado explicitamente no processo. Não interpretar a diferença em relação às rodadas anteriores como ganho de otimização: carga da máquina e configuração efetiva do limite variaram. A rodada anterior sem limite explícito mediu 58,87 FPS apesar da configuração nominal de 45; por isso os atalhos agora também o aplicam explicitamente. Não foi alterado o perfil global do bunker.

Falhas corrigidas durante esta continuação: ambiente do processo sem seleção do Metal Toolchain já instalado; binário do ensaio sem o novo marcador intermediário (confirmado pela inspeção do módulo e resolvido com recompilação após alteração do ensaio); partes do corpo em pé visíveis na câmera de descanso. O teste intermediário agora usa tempo relativo à entrada no descanso. Logs da primeira falha e da rodada parcial foram preservados. Os 449 assets da publicação anterior passaram novamente pela conferência de hashes.

Ainda pendentes: animação corporal de deitar/levantar e sua apresentação em rede; armário físico adaptado ao novo quarto; iluminação menos serrilhada; conexão desta cena aos circuitos; vídeo e testes com dois e quatro jogadores. A cena permanece um estudo isolado e não substitui o executável de expedição existente.


## Versão posterior preservando este estudo

O quarto v002, em outro mapa, agora possui armário físico e validação de armazenamento com dois jogadores. O armário deste mapa v001 continua decorativo. Consulte `BEDROOM_CABINET.md` para os arquivos, controles e limitações da versão posterior.
