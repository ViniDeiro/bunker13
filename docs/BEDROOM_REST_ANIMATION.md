# Quarto v003 — animação corporal de descanso

## Escopo e arquivos

A apresentação do descanso foi adicionada somente à terceira versão do mesmo quarto. O bunker principal e os quartos v001/v002 permanecem preservados. O inventário, os IDs, o cálculo de energia e o formato do salvamento não foram substituídos.

- Mapa: `/Game/Bunker/BedroomRest/Lvl_Bedroom_Study_Rest`.
- Fonte editável da animação: `blender/Bedroom_Rest_Animation_v001.blend`.
- Fonte do ambiente, preservada: `blender/Bedroom_StyleStudy_v002.blend`.
- Dados de referência e curvas: `exports/bedroom_rest_rig.json` e `exports/bedroom_rest_animation.json`.
- Asset nativo: `/Game/Bunker/BedroomRest/A_Bedroom_Rest`.
- Prévia manual: `tools/launchers/Ver-Quarto-Animacoes.command`, E na cama e F para levantar.

O atalho usa a Unreal instalada e abre uma sessão de avaliação sem gravar a campanha. Não é um novo executável empacotado. A própria câmera continua usando a transição anterior; para conferir o corpo deitado, é necessária a visão de outro jogador.

## Implementação

O rig de autoria preserva os 89 ossos de referência do manequim existente. A ação tem quatro poses principais e 36 amostras a 30 Hz, com rotação da raiz e articulação dos braços e pernas. O modelo real dentro da Unreal continua sendo a malha esquelética existente: o corpo é deformado pelos ossos, em vez de apenas girar uma malha rígida. A fonte Blender contém rig, ação editável e proxies ponderados para autoria; não contém uma cópia editável da malha completa do manequim. Esses proxies não são assets do jogo.

O erro máximo de ida e volta das posições de referência foi 0,00050 cm. A ação é amostrada no Blender e importada por curvas na API de animação da Unreal, evitando a exportação FBX esquelética que falhou neste ambiente. O clipe nominal tem 35 intervalos a 30 Hz; sua apresentação é remapeada para uma transição de 1,15 s.

`ABedroomRestPose` é uma camada cosmética replicada. O servidor inicia a apresentação e distribui personagem, cama, transformação inicial e horário. Cada instância avalia a mesma ação pelo relógio do servidor; não são transmitidos 89 ossos a cada quadro. Ao levantar, a ação é revertida, inclusive quando interrompida antes de deitar completamente. O destino visual acompanha o personagem caso ele já esteja se movendo após a saída. A classe e a transformação originais da malha são restauradas ao encerrar a apresentação.

A ocupação, recuperação de energia, liberação e busca de um ponto de saída continuam no sistema de cama existente. A cápsula de colisão permanece a original do personagem; esta entrega não implementa física corporal deitada, ragdoll ou interação de tecido com o colchão.

## Critérios de validação

O ensaio alterna host e cliente na cama. Confere ossos reais da cabeça e dos pés na posição deitada, uma pose intermediária ao entrar e outra ao sair, recuperação de energia, recusa de uma cama ocupada, ausência de mudança no inventário, restauração da animação/locomoção e limpeza dos atores cosméticos. Também testa levantar antes do fim da entrada.

Os participantes são preparados por reposicionamentos de teste. Isso não demonstra caminhada humana até a cama. A animação e os comandos E/F são executados pelo fluxo real do jogo. Os resultados consolidados ficam em `docs/validation/bedroom_rest_body_2026-11-13.json`.

## Limitações e problemas encontrados

A exportação FBX esquelética da Unreal caiu em `GetCPUSkinnedVertices`/`MeshObject`, inclusive em tentativas com renderização. A execução com renderização explícita também iniciou uma compilação longa de shaders e foi interrompida. Foi adotada a extração direta do esqueleto no runtime e a importação das curvas; a malha do personagem não foi substituída. Os logs das tentativas foram preservados.

Capturas normais do Editor tentavam completar materiais de diagnóstico de Buffer Visualization, causando longas pausas. A pilha foi conferida com amostragem do processo. O ensaio desativa apenas essa lista de diagnóstico, sem mudar os materiais, luzes ou qualidade global do bunker. O início das ações agora depende da confirmação dos dois participantes por um relógio replicado de teste, em vez de um atraso fixo.

A tentativa com duas janelas renderizadas não foi concluída: houve timeout/conexão perdida durante a preparação. A alternativa validada usa um host renderizado e um cliente sem janela para reduzir a carga. As imagens reais do host mostram o personagem remoto; o cliente sem janela não produz imagens. Isso não certifica desempenho ou apresentação de duas telas simultâneas.

Ainda precisam de revisão: naturalidade do movimento de sentar/reclinar, contato anatômico fino das mãos, IK no colchão, reação do tecido, som de cama/roupa e arte final do personagem. O manequim existente é provisório. A apresentação funcional não é aprovação comercial das animações.

Não houve nesta etapa teste com quatro jogadores, internet/Steam, reconexão da nova cena, sessão longa, novo vídeo ou novo pacote. A experiência sonora e o bloqueio físico do ponto de saída não foram revalidados neste cenário. O HUD da prévia ainda mostra F5 apesar de não gravar a campanha.


## Resultado final — 13/11/2026

As **18 verificações** da rodada final passaram. Foram observadas duas poses intermediárias reais no cliente: entrada com progresso 0,493 e cabeça a 153,68 cm; saída com progresso 0,597 e cabeça a 111,93 cm. A pose final colocou a cabeça em (117; -388,575; 72,661) cm e a média dos pés em (117; -234,417; 66,028) cm. O ajuste final baixou o apoio dos pés em aproximadamente 8,6 cm em relação à primeira versão e aproximou as mãos do colchão. A captura foi revisada na Unreal.

A primeira rodada após esse ajuste reprovou verificações baseadas em horários fixos: o ator ainda não tinha chegado ou o comando de saída ainda não tinha sido recebido. A versão final exige observar o estado real e uma altura intermediária dos ossos, sem remover essas verificações. Logs da rodada reprovada ficaram em `logs/restpose_contact_timing/`; o primeiro passe anterior foi preservado em `logs/restpose_first_pass/`.

Medição curta, incluindo capturas pontuais: host renderizado em 960 × 540, resolução interna 70%, sombras/AO desligados, limite 30 FPS, **25,08 FPS**, frame p95 **48,79 ms**, 587 amostras. O cliente sem janela registrou 27,11 ticks/s e p95 de 44,30 ms; isso **não é FPS de uma segunda tela renderizada**. A carga e o tempo de abertura variaram bastante entre as rodadas. Não inferir otimização concluída ou desempenho de um pacote distribuído.

Fonte Blender reaberta e ação reexportada: 89 ossos, 36 amostras, erro de posição zero em relação aos dados importados e erro máximo de produto escalar dos quaternions de aproximadamente 0,00000013. O exportador separado permite editar a ação existente sem regenerá-la. Os 449 assets anteriores passaram novamente na conferência, e os hashes dos mapas e fontes dos quartos v001/v002 permaneceram iguais. As regressões de salvamento do marco anterior não foram repetidas nesta rodada; formato de save e transações de armazenamento não foram alterados.

Capturas: `screenshots/restpose_host_09.png` mostra o cliente deitado na visão do host; `restpose_host_standing.png` mostra o retorno à situação normal e `restpose_host_04.png` a visão do próprio jogador descansando. O cliente sem janela não gerou capturas. Não foi produzido vídeo novo nesta etapa.

## Continuar a autoria

Salve as alterações da ação em `Bedroom_Rest_Animation_v001.blend` e execute `scripts/export_bedroom_rest_animation.py` no Blender. Esse exportador conserva as poses editadas; `create_bedroom_rest_animation.py` é o gerador e reconstrói a ação original. Em seguida, `install_bedroom_rest_animation.py` atualiza o asset e o mapa v003 na Unreal. Preserve os nomes dos ossos e a escala métrica; ajuste a ação no modo de pose. O deslocamento para a cama é controlado pela apresentação na Unreal.

Os arquivos permanecem locais para revisão. Próximo refinamento no mesmo quarto: naturalidade da entrada/saída, apoio das mãos e desempenho; não aplicar aos demais ambientes antes da aprovação visual.


Antes de gerar um pacote desta prévia, será necessário incluir explicitamente o mapa v003 e o diretório `BedroomRest` no cook: a animação é carregada por caminho em tempo de execução. A configuração de empacotamento atual continua restrita aos mapas/diretórios anteriores. Ela não foi ampliada nesta etapa de avaliação visual.
