# CRACK como referência — 13/11/2026

Referência indicada pelo criador: [CRACK, de Rafoli, na Steam](https://store.steampowered.com/app/4312190/CRACK/). O pedido é buscar a qualidade visual e a sensação de gameplay apreciadas por ele, aplicadas à ideia do Condomínio 13. Não substitui o GDD nem autoriza ampliar o mapa ou implementar todos os marcos juntos.

## Evidência e limites desta análise

A descrição oficial apresenta cooperação para 1–4 pessoas, um objetivo central compartilhado, descoberta da instalação e melhoria de ferramentas. Esses são os pontos confirmados nesta consulta. A avaliação de que o visual e a gameplay são excelentes é o relato do criador, que jogou.

Na primeira consulta, o acesso às imagens pelo navegador falhou. Depois, o criador forneceu três capturas: quarto/bancada, máquina recreativa com personagens e salão de convivência. Essas capturas foram analisadas visualmente. Também forneceu [este vídeo](https://www.youtube.com/watch?v=2spKNOUI0Fc), que não pôde ser reproduzido/inspecionado nesta sessão. Não houve execução de CRACK, medição de controles, inspeção de seu código ou análise de animação. As capturas não comprovam shaders, técnicas de iluminação, parâmetros de câmera, física, arquitetura de rede ou desempenho.

## Leitura visual das três capturas

A referência é um **3D industrial estilizado**, com superfícies rígidas e volumes robustos. Móveis e arquitetura têm planos largos, molduras espessas e cantos chanfrados/arredondados de forma controlada. As grandes superfícies são limpas; pequenos detalhes e sujeira não dominam a leitura. O tecido da cama é mais macio, mas paredes, caixas e equipamentos não parecem deformáveis.

Na captura do quarto, painéis claros e uma faixa verde organizam as paredes. A cama tem estrutura escura espessa, manta azul-esverdeada e travesseiro claro; bancada, nicho, luminárias e caixas formam uma composição compacta e habitada. Na captura do salão, piso modular, pilares, vigas e tubos têm espessura visual consistente, com pontos de cor nos móveis e equipamentos. As luminárias são visíveis e há gradação de luz/sombra que separa volumes e cantos. As capturas não permitem determinar se esse resultado vem de luz dinâmica, baking, AO ou pós-processamento.

A captura dos personagens reforça silhuetas grandes, peças simplificadas e cores que distinguem partes do equipamento. Não autoriza copiar seus trajes. Os números de FPS visíveis num print não são benchmark do Condomínio 13. A presença da cama também não comprova qual animação ou lógica de sono CRACK utiliza.

## Tradução para nosso jogo

| Intenção | Aplicação no Condomínio 13 | Como avaliar |
|---|---|---|
| Objetivo comum compreensível | A crise de energia/água dá motivo à expedição e ao trabalho de quem permanece. | Em teste sem orientação, o grupo identifica o problema, a necessidade e a alternativa de recuperação. |
| Sensação satisfatória de agir | A mão alcança a peça, a porta responde, o som corresponde e o equipamento muda de estado. | Testar pegar, guardar, abrir/fechar e manter equipamento sem modal desnecessário, bloqueios ou feedback antecipado. |
| Instalação que desperta interesse | Espaços existentes contam o uso cotidiano e sugerem mistério; novas alas continuam fechadas até seu marco. | Sinalização e objetos ajudam a reconhecer função/rota sem adicionar bairros ou missões paralelas. |
| Melhorias com consequência | Manutenção, ferramentas e proteção ampliam possibilidades ou reduzem riscos, com custo físico persistente. | O mesmo recurso/GUID muda de localização, é usado e mantém condição; não criar moeda ou inventário paralelo. |
| Qualidade visual coesa | Formas críveis, espessuras, PBR em escala, desgaste localizado, luz justificada e objetos legíveis. | Comparar capturas reais da mesma área/câmera; manter o acabamento já aprovado e medir custo no Mac. |
| Cooperação espontânea | Decidir quem sai, o que levar e quem recebe recurso/tratamento. | Teste humano sem roteiro; não confundir quatro processos automáticos com cooperação social validada. |

## Direção visual proposta

Manter defesa civil subterrânea com identidade própria, seguindo agora uma linguagem industrial estilizada: concreto de baixa frequência visual, aço pintado, borracha e equipamentos de silhueta robusta; manutenção e reparos convivem com sinais discretos de uso cotidiano. A área social continua quente e habitável, as áreas técnicas mais frias. Evitar ferrugem uniforme, ruído de textura em toda superfície e escuridão que esconda a função dos objetos. A garrafa permanece azul. Isso muda a linguagem dos modelos e da composição, não apenas as texturas.

Para nosso quarto: painéis em marfim quente, verde de defesa civil, ferragens em grafite e acentos de sinalização próprios. Cama com estrutura chanfrada, colchão com espessura, manta com poucas dobras bem colocadas, bancada/nicho/armário com função reconhecível. Madeira, plástico, tecido e metal devem continuar distinguíveis por resposta de material, mesmo com texturas discretas. Tipografia e sinalização serão originais da Deiros Dev; não reproduzir marcas, cartazes, disposição exata ou logotipos da referência.

O acabamento deve aparecer na Unreal, com exposição controlada, contraste que permita ler portas/itens e materiais distinguíveis sob a iluminação real. Não estabelecer uma meta de shader ou polígonos por analogia com CRACK: nosso limite precisa ser medido. Não prometer a mesma performance a partir de requisitos de loja de outro jogo.

## Primeira comparação controlada proposta

Após a ênfase do criador no quarto, a primeira prova visual passa a ser **um quarto/módulo de dormitório de referência**, com cama, bancada, nicho e armazenamento. Preservar o nível e os arquivos atuais; não aplicar o estilo ao bunker inteiro antes da comparação visual na Unreal. Não adicionar uma nova região nem trocar o programa arquitetônico aprovado para acomodar uma cópia do cômodo de CRACK.

O percurso **armário → recurso na mão/mochila → painel do gerador → reação da iluminação** continua como comparação funcional posterior, não como substituto da prova de linguagem visual solicitada. Registrar antes/depois usando câmera e exposição comparáveis.

Dependências: inventário/GUIDs, autoridade, armário físico, ação observada, gerador/circuitos e salvamento existentes. Aceite: transação única confirmada pelo host; objeto/porta/mão/som correspondem à ação; cancelar/falhar não simula conclusão; outro jogador vê a mudança relevante; guardar/reconectar não duplica; capturas e frame time comparáveis. Ausência de som/gesto apropriado deve constar como pendência, não como funcionalidade concluída.

Essa comparação é uma proposta de aplicação da referência, ainda não uma entrega de arte/interação. A prioridade visual indicada pelo criador não torna concluído o marco funcional de **radiação/proteção persistentes**, cuja base matemática existe mas ainda não está ligada ao jogo. O equipamento físico desse marco poderá seguir os mesmos critérios de acabamento e interação.

## Arquitetura preservada

Separar regras, transações autoritativas, estado persistente e apresentação. Feedback local não concede propriedade nem aplica consumo; a confirmação vem do servidor. Equipamento continua identificado por GUID. Não reescrever saves, controlador ou mapas só para perseguir uma referência estética. Não reproduzir layout, personagens, interfaces, sons ou assets de CRACK.

Próximas decisões de câmera, ritmo, som e acabamento precisam de observação de gameplay e validação no nosso executável. Não há nova versão jogável, benchmark, aprovação visual ou publicação GitHub nesta análise.
