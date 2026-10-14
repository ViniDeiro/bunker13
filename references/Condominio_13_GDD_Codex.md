# CONDOMÍNIO 13 — GAME DESIGN DOCUMENT E ESPECIFICAÇÃO DE PRODUÇÃO

**Versão:** 1.0 — 13/10/2026  
**Estúdio:** Deiros Dev  
**Plataforma-alvo:** PC (Windows), distribuição planejada na Steam  
**Engine de jogo:** Unreal Engine 5 (versão estável a definir antes de implementar)  
**Modelagem e montagem de assets:** Blender (versão instalada a registrar)  
**Gênero:** Sobrevivência cooperativa PvE, suspense, exploração, simulação social emergente  
**Jogadores:** 1 a 4 (equilíbrio principal para quatro); cooperação com possibilidade de conflito social não roteirizado  
**Câmera:** Primeira pessoa no MVP; terceira pessoa pode ser avaliada após validação  
**Status:** Especificação inicial, parâmetros de balanceamento sujeitos a playtest  

> **INSTRUÇÃO AO AGENTE CODEX:** Este documento descreve o produto completo e separa expressamente o escopo de lançamento do escopo de protótipo. NÃO tente implementar tudo de uma vez. Comece pela Fase B0 (auditoria do ambiente e planejamento), depois B1 (blockout do bunker em Blender), valide os critérios de aceite e só avance após confirmação. Não confunda modelagem 3D com programação do jogo: Blender cria assets e layout; Unreal implementa gameplay, rede, áudio, IA, salvamento e empacotamento. Não declare recursos como prontos sem execução e teste. Registre suposições e bloqueios.

---

## 1. VISÃO E PILARES

**Elevator pitch:** Quatro sobreviventes dividem um bunker escondido sob um supermercado após um desastre radiológico. O abrigo é relativamente seguro, mas comida, água, remédios e energia acabam. Para sobreviver, precisam sair, explorar um mundo hostil e voltar — se conseguirem. Os companheiros que ficaram não sabem automaticamente o destino dos exploradores. A confiança é tão escassa quanto os recursos.

**Fantasia principal:** viver dentro de um abrigo físico e persistente, com liberdade para cozinhar, descansar, jogar, discutir, compartilhar, esconder ou roubar recursos; tomar decisões difíceis sobre quem sai, quem fica e quem recebe tratamento.

**Pilares inegociáveis:**
1. **O bunker é o protagonista:** local habitável, interativo, reconhecível e importante para a sobrevivência.
2. **Informação limitada:** não há telepatia de interface; comunicação depende de proximidade e rádios.
3. **Recursos materiais:** itens são contáveis, localizados, transportáveis e consumíveis; servidor/host valida todas as transações.
4. **Risco com consequência:** expedições podem causar ferimentos, contaminação, perda de equipamento e morte permanente naquela partida.
5. **Histórias emergentes:** crises geram negociação e conflito; não existe traidor obrigatório.
6. **Sessões rejogáveis:** recursos, ameaças, eventos e objetivos variam entre partidas.
7. **Tom híbrido:** mundo visualmente inquietante, mas com espaço para humor espontâneo e minijogos.

**Não objetivos:** MMO, mundo aberto ilimitado, PvP competitivo balanceado, campanha cinematográfica linear, crafting com centenas de receitas, construção livre de bases, microtransações no lançamento, geração procedural de geografia integral.

**Referências criativas, não para copiar:** 60 Seconds! (pressão de coleta e escassez), Silo (mistério subterrâneo), The 100 e The Rain (sobrevivência e conflitos de grupo). Não reproduzir personagens, layouts, textos, arte, marcas ou interfaces dessas obras.

## 2. PREMISSA NARRATIVA E UNIVERSO

**Cenário:** cidade fictícia de Santa Aurora, isolada após o “Evento Cinza”, uma emergência industrial/radiológica de causa inicialmente incerta. Autoridades anunciaram evacuação, mas comunicações falharam. Sob o antigo supermercado Mercado Aurora há um abrigo de defesa civil reformado secretamente décadas antes.

**Ambiguidade narrativa:** o mundo exterior contém radiação, saqueadores e pessoas infectadas por uma condição desconhecida; no lançamento, evitar afirmar que toda ameaça é zumbi clássico. O jogo pode usar criaturas humanoides contaminadas sem explicar completamente sua origem.

**Mistério central:** quem construiu as alas lacradas do abrigo, por que há registros contraditórios do desastre e se o sinal de resgate é confiável.

**Entrega narrativa:** pistas ambientais, documentos curtos, rádio, fotografias, gravações e eventos jogáveis; não interromper constantemente o fluxo com cutscenes.

**Objetivo macro:** sobreviver e conquistar uma de três saídas: (a) contato e evacuação por resgate, (b) reparo de veículo de fuga, (c) reativação de uma rota subterrânea segura. Nem todos os finais precisam estar presentes no MVP.

## 3. ESTRUTURA DA PARTIDA

### 3.1 Lobby e preparação
- Um jogador hospeda a sessão; até três amigos entram por convite da Steam quando a integração estiver pronta.
- Seleção cosmética de personagem, teste de microfone, controles, acessibilidade e configuração de dificuldade.
- Personagens têm capacidades iniciais equivalentes no MVP; especializações opcionais somente após testes de equilíbrio.
- O host escolhe semente de partida (ou aleatória), dificuldade e se permite entrada tardia antes do fechamento do bunker.
- O jogo suporta 1–4 jogadores, mas o balanceamento primário é para quatro.

### 3.2 Coleta inicial — 90 segundos no protótipo, ajustável entre 60 e 120
- Começa no supermercado ainda acessível. Sirenes indicam iminente fechamento do abrigo.
- Cada jogador corre para coletar alimentos, água, remédios, pilhas, ferramentas, equipamentos e itens recreativos.
- Peso e espaços limitam transporte; objetos grandes ocupam ambas as mãos ou reduzem velocidade.
- A coleta usa interação física: olhar, destacar, pegar, carregar, soltar e colocar em mochila ou carrinho.
- A porta de emergência fecha quando o cronômetro acaba; alertas sonoros em 30, 15 e 5 segundos.
- Quem ficar do lado de fora não é eliminado automaticamente: inicia uma situação de alto risco e precisa procurar uma entrada alternativa ou convencer o grupo a abrir a porta; esta regra será testada.
- O jogo evita softlock: sempre existe ao menos um conjunto mínimo de recursos ou alternativa difícil para manter a partida viável.

### 3.3 Vida no bunker
- Ciclo contínuo de tempo com dias acelerados; valor inicial de teste: 4 minutos por dia, pausas opcionais somente em single-player.
- Necessidades: fome, sede, saúde, fadiga e exposição à radiação. Estresse é uma camada posterior, não requisito do primeiro protótipo.
- Ações físicas: abrir armário, pegar lata, abrir, comer, encher copo, beber, deitar, acender lâmpadas, ligar rádio, reparar gerador, usar kit médico, jogar cartas.
- Estoques pertencem ao mundo, não a uma contabilidade abstrata. Cada item tem ID único, tipo, quantidade/durabilidade e localização autorizada.
- Eventos criam decisões: falha elétrica, ruído na ventilação, doença, pedido de ajuda, vazamento, rádio desconhecido, comida estragada.

### 3.4 Expedição
- Jogadores equipam mochila, proteção, rádio, lanterna, filtro e eventualmente arma.
- A saída exige procedimento físico de antecâmara: fechar porta interna, equalizar/ventilar, abrir porta externa; ações e tempos simplificados por diversão.
- A superfície é um mapa fechado e denso com rotas alternativas, interiores e zonas de risco; não é mundo aberto infinito.
- Explorar envolve procurar suprimentos, evitar ameaças, cumprir objetivos, gerenciar espaço, exposição e retorno.
- Um explorador pode perder rádio, bateria ou consciência. Jogadores no bunker não recebem notificações automáticas de morte.
- Mochila de morto permanece no mundo por período definido; recuperar itens é possível e perigoso.

### 3.5 Fim de partida
- Vitória quando um objetivo final é concluído e pelo menos um sobrevivente consegue escapar ou ser resgatado (configurável por final).
- Derrota quando todos morrem ou o abrigo se torna irrecuperável sem sobreviventes capazes de sair.
- O grupo recebe resumo de eventos, mortes, consumo, expedições e escolhas; revelar segredos individuais somente no encerramento.
- Jogador morto entra em espectador com limitações: não pode interagir, pingar posições, transmitir informações pelo rádio do jogo ou ver áreas não descobertas. Comunicação externa como Discord não é controlável.

## 4. MULTIPLAYER E REDE — REQUISITOS OBRIGATÓRIOS

- Arquitetura inicial: **listen server autoritativo** com host jogador; considerar servidores dedicados somente após validação.
- Todo item, inventário, dano, saúde, porta, gerador, IA, tempo, evento e objetivo deve ser validado pelo servidor.
- Clientes enviam intenções; servidor valida distância, permissões, estado, capacidade e consistência antes de aplicar mudanças.
- Proibir duplicação de itens por interação simultânea, reconexão ou queda de conexão.
- Suportar entrada tardia apenas na preparação/coleta até ponto configurado; depois, reconexão de participante existente.
- Reconexão restaura personagem, inventário e estado persistente sem criar novo jogador ou duplicar recursos.
- Se o host sair, comportamento inicial documentado: sessão encerrada com salvamento consistente; migração de host fica fora do MVP.
- Não confiar em relógio local do cliente; eventos e cronômetros seguem tempo do servidor.
- Testes obrigatórios com 4 instâncias, latência artificial e perda de pacotes.
- A voz por proximidade deve ser integrada por solução compatível com licenças e plataforma, escolhida na fase Unreal; não presumir que Steam Networking implementa voz automaticamente.
- Rádio é canal de voz ativado por equipamento, frequência, bateria e condição física. A transmissão pode sofrer ruído ou interrupção; não mostrar indicador global de morte.
- Privacidade: controles de mute, volume individual, push-to-talk, bloqueio e indicação clara de captação de microfone.

## 5. SISTEMAS DE SOBREVIVÊNCIA

### 5.1 Atributos (valores iniciais para protótipo)
| Atributo | Faixa | Comportamento |
|---|---:|---|
| Saúde | 0–100 | 0 implica morte após regra de incapacitação, se ativada |
| Fome | 0–100 | 100 = alimentado; diminui com tempo/esforço |
| Hidratação | 0–100 | 100 = hidratado; cai mais rápido que fome |
| Energia | 0–100 | Recupera ao dormir; afeta corrida e ações |
| Radiação acumulada | 0–100 | Aumenta em zonas contaminadas; efeitos por limiar |
| Condição de equipamento | 0–100 | Desgaste em filtros, ferramentas e armas |

**Importante:** taxas numéricas são parâmetros em Data Assets/Data Tables, não valores fixos em código. Testar uma partida de 60–120 min antes de balancear.

### 5.2 Comida e água
- Latas, alimentos perecíveis, rações, garrafas, galões e água não tratada.
- Comer e beber exige consumir unidade de inventário/objeto e aplicar efeito validado pelo host.
- Jogador pode comer escondido; estoque compartilhado não se atualiza magicamente na interface de outros.
- Água contaminada pode causar doença; tratamento e filtragem podem reduzir risco.
- Não exigir animações hiper-realistas para cada item no MVP: interação curta e legível basta.

### 5.3 Ferimentos, doença e radiação
- Ferimentos: sangramento, contusão e fratura simplificada.
- Doenças: infecção e intoxicação como estados com duração, sintomas e tratamento.
- Radiação: medidor pessoal, zonas de exposição, filtros, descontaminação e itens protetores.
- Comunicação visual e sonora clara dos estados; evitar efeitos de tela intensos sem opção de acessibilidade.

### 5.4 Energia e infraestrutura
- Gerador consome combustível e exige reparos ocasionais.
- Energia alimenta iluminação, refrigeração, rádio e purificação de água.
- Falha elétrica cria alternativas: lanterna, velas e manutenção; não bloquear automaticamente todas as interações.
- Ventilação e filtragem determinam segurança do bunker durante eventos de contaminação.

### 5.5 Inventário e física
- Mochila com espaços + peso; itens de mundo com malhas simplificadas e interação consistente.
- Contêineres com slots persistentes e acesso concorrente seguro.
- Jogador pode largar, mover, guardar, empilhar e recuperar itens.
- Física divertida é permitida para objetos decorativos, mas **itens críticos devem ter estados de inventário determinísticos** para evitar perda por bugs.
- Não simular centenas de objetos rigid-body simultâneos em rede sem orçamento de desempenho.

## 6. COMBATE, INIMIGOS E MORTE

- O combate é perigoso e limitado por munição, ruído, durabilidade e risco de exposição.
- MVP: uma arma improvisada corpo a corpo, uma arma de fogo simples, um tipo de inimigo contaminado.
- IA possui patrulha, investigação de ruído, perseguição, ataque, perda de alvo e retorno à rota.
- Disparos podem atrair inimigos próximos; furtividade deve ser alternativa real.
- Dano e munição validados pelo servidor; feedback local responsivo com reconciliação quando necessário.
- Fogo amigo: desligado no MVP; opção futura apenas após avaliar griefing.
- Morte permanente na partida. Estado opcional de incapacitação com janela de resgate curta, definido em playtest.
- Corpos e mochilas são persistentes até regras de limpeza; corpos não transmitem informações mágicas ao bunker.

## 7. BUNKER — PROGRAMA ARQUITETÔNICO

**Conceito:** abrigo de defesa civil retroindustrial, concreto armado, tubulações, aço, pintura desgastada, iluminação quente nas áreas sociais e fria nas técnicas. Deve parecer construído e adaptado ao longo de décadas, não uma mansão subterrânea.

**Dimensão inicial de blockout:** envelope aproximado 28 m × 20 m por pavimento, ajustável conforme circulação. Dois pavimentos subterrâneos podem ser adotados, mas começar por UM pavimento funcional para validação. Pé-direito 3 m; corredores principais 2 m; portas internas 1,1 m × 2,2 m; porta blindada 1,8 m × 2,4 m. Todas as medidas são propostas de design, não engenharia real.

**Ambientes obrigatórios do bunker jogável:**
1. **Entrada/antecâmara:** escada do supermercado, duas portas estanques, armário de EPI, bancada de inspeção, ducha fictícia de descontaminação, painel de status.
2. **Sala de convivência (aprox. 9 × 7 m):** mesa central, sofá, rádio, TV antiga, estantes, quadro de avisos, mesa de cartas; ponto de encontro principal.
3. **Cozinha (5 × 5 m):** bancada, pia, fogão, mesa, utensílios, geladeira dependente de energia.
4. **Despensa (6 × 5 m):** prateleiras, armários, caixas, galões e fechadura opcional; esconderijos visuais.
5. **Dormitório (6 × 5 m):** quatro camas, armários pessoais, luz de leitura, objetos narrativos.
6. **Enfermaria (4 × 4 m):** maca, armário de medicamentos, bancada e luz de exame.
7. **Sala do gerador (5 × 4 m):** equipamento principal, combustível, painel elétrico, tubulações e manutenção.
8. **Oficina (5 × 4 m):** bancada, ferramentas, sucata e estação de reparos.
9. **Sala de rádio/comando (4 × 4 m):** transmissor, mapa, painel de energia e registro de expedições.
10. **Sanitário (3 × 3 m):** pia, vaso e ducha; ambientação e mecânicas futuras.
11. **Corredores/áreas técnicas:** conexões sem becos de circulação acidentais, saídas de emergência narrativas.
12. **Sala de recreação (fase posterior):** sinuca e pingue-pongue; não bloquear lançamento do MVP.

**Segredos futuros:** ala médica lacrada, sala de vigilância e túnel antigo. Devem aparecer como portas fechadas no primeiro blockout, sem necessidade de interiores completos.

**Regras de layout:**
- Da entrada à convivência: percurso intuitivo de 10–20 s caminhando.
- Cozinha e despensa próximas; gerador distante do dormitório.
- Dois espaços privados permitem cochichos sem serem ouvidos no centro.
- Portas e corredores permitem passagem sem colisões constantes entre quatro jogadores.
- Visibilidade parcial entre salas; não criar bunker em linha reta com visão de tudo.
- Rotas de fuga e ventilação têm lógica visual, mas não precisam reproduzir engenharia real.
- Sem paredes externas infinitas; a estrutura deve ter limites e colisão coerentes.

## 8. SUPERMERCADO E SUPERFÍCIE

### 8.1 Supermercado Mercado Aurora
- Edifício comercial de porte médio, área inicial de referência ~40 × 30 m.
- Fachada com letreiro fictício, estacionamento, portas de vidro, caixas, corredores de gôndolas, seção de alimentos, farmácia pequena, estoque e área administrativa.
- Acesso ao bunker atrás do estoque, por corredor de serviço e escada com porta reforçada.
- Múltiplas rotas de coleta e distribuição não uniforme de itens; quatro jogadores não devem seguir o mesmo caminho ideal.
- Relógio de coleta, sirene e iluminação de emergência legíveis.
- Após desastre, o mesmo edifício pode ser revisitado, agora danificado, com saqueadores e ameaças.

### 8.2 Mapa externo fechado
**Primeiro recorte jogável:** supermercado + estacionamento + rua + um edifício explorável.  
**Expansão de lançamento:** bairro residencial, clínica, posto de combustível, depósito industrial e trecho de mata/estrada.  
**Barreiras diegéticas:** bloqueios militares, prédios desabados, radiação extrema e túneis obstruídos; evitar paredes invisíveis óbvias.

**Locais e recompensas:**
| Local | Recursos | Ameaça/obstáculo |
|---|---|---|
| Supermercado | Comida, água, pilhas | Contaminados e corredores escuros |
| Clínica | Medicamentos, filtros | Acesso trancado e ambiente contaminado |
| Casas | Ferramentas, roupas, pistas | Emboscadas e moradores hostis |
| Posto | Combustível, peças | Área aberta e barulho |
| Depósito | Ferramentas, componentes | Portões, alarmes e inimigos |
| Mata/estrada | Rotas alternativas, sinais | Baixa visibilidade e exposição |

**Densidade:** preferir áreas menores, interativas e memoráveis a mapas grandes e vazios.

## 9. MISSÕES, EVENTOS E REJOGABILIDADE

**Missões sistêmicas:** reparar rádio, recuperar filtro, buscar antibiótico, encontrar fusível, rastrear transmissão, recuperar mochila de explorador, verificar contaminação de reservatório.

**Eventos no bunker:**
- Gerador falha; escolher gastar peças ou combustível extra.
- Batidas na porta; visitante pede água.
- Ruído no duto; inspeção revela animal, falha ou ameaça.
- Água muda de cor; testar ou arriscar consumo.
- Rádio transmite coordenadas incompletas.
- Alimento estraga após falta de energia.
- Jogador apresenta sintomas após expedição.
- Porta de ala lacrada recebe sinal de atividade.

**Diretor de eventos:** pesos por dia, estoque, saúde do grupo, progresso e dificuldade; cooldown impede repetição imediata. Eventos são sorteados no host com seed persistida.

**Exemplo de cadeia:** transmissão solicita antibiótico → clínica abre como objetivo → expedição encontra sobrevivente → decidir compartilhar recursos ou voltar → consequências no rádio dias depois.

**Não usar quests obrigatórias que exigem item que possa ser destruído sem alternativa.** Toda missão crítica tem rota de recuperação ou falha narrativa explícita.

## 10. MINIGAMES E CONVIVÊNCIA

**MVP:** baralho simplificado (ex.: jogo de vazas ou memória, sem marca de jogo protegido), dardos ou arremesso de objetos; prioridade para interações que funcionem bem em rede.

**Pós-MVP:** sinuca com física simplificada, pingue-pongue, jogo de tabuleiro fictício, rádio com estações diegéticas.

**Regras:**
- Jogadores entram e saem sem travar a partida.
- Minigames não pausam fome, sede, ataques ou eventos.
- Não recompensar minigames com recursos essenciais em excesso.
- Sinuca/pingue-pongue exigem simulação de física autoritativa e testes específicos de latência.
- Privacidade social: distância entre sala de jogos e áreas privadas importa para a voz por proximidade.

## 11. INTERFACE, ÁUDIO E ACESSIBILIDADE

**HUD discreto:** indicadores de necessidades quando relevantes; interação contextual; inventário e mapa físicos ou UI estilizada como equipamentos.

**Informação restrita:** não mostrar localização, vida ou morte global dos aliados sem dispositivo e regra justificável. A lista de participantes pode existir no menu de rede, sem estado vital automático.

**Áudio:** ventilação, estalos de metal, gerador, chuva, sirenes, passos, vozes abafadas por paredes, rádio com estática. Silêncio deve ser ferramenta de tensão.

**Acessibilidade:** legendas, remapeamento de teclas, sensibilidade, FOV, redução de tremor/câmera, opções para daltonismo, indicadores visuais de eventos sonoros importantes, push-to-talk, mute e controles de volume.

**Idiomas:** PT-BR inicial; arquitetura preparada para localização em inglês.

## 12. DIREÇÃO DE ARTE E ASSETS

**Estética:** 3D estilizado semi-realista, proporções humanas levemente simplificadas, silhuetas claras, superfícies gastas e atmosfera cinematográfica. Evitar fotorealismo custoso e aparência de assets sem coesão.

**Paleta:** bunker — cinzas de concreto, ferrugem, verdes desbotados, âmbar de lâmpadas; exterior — azul acinzentado, poeira, névoa e sinais vermelhos de alerta.

**Materiais principais:** concreto, metal pintado, aço escovado, borracha, vidro sujo, madeira laminada, tecido, plástico industrial.

**Escala e exportação:** Blender em metros, Z para cima, transformações aplicadas antes de exportar; verificar orientação/eixos e escala no Unreal com cubo de referência de 1 m. Nomear meshes `SM_`, materiais `M_`, texturas `T_`, colisões conforme pipeline de importação escolhido. Pivôs coerentes: portas no eixo da dobradiça, objetos de chão na base, módulos arquitetônicos em pontos de encaixe.

**Modularidade:** paredes retas, cantos, pisos, tetos, portas e molduras reutilizáveis; preferir medidas em grade de 0,5 m ou 1 m. Geometria limpa, sem faces duplicadas, normais corrigidas e UVs apropriadas.

**Otimização:** LODs/Nanite conforme tipo de asset e versão de Unreal, colisões simplificadas, materiais compartilhados, instancing para objetos repetidos e orçamento de draw calls/performance a medir no protótipo.

**Primeiro inventário de assets:**
- Arquitetura: 8 módulos de parede, 4 de piso, 4 de teto, 3 molduras, 3 portas, escada, corrimão, dutos, tubos, luminárias.
- Móveis: 4 camas, 2 mesas, 6 cadeiras, sofá, 3 armários, 4 estantes, 2 bancadas, pia, fogão, geladeira, maca, bancada de oficina.
- Equipamentos: gerador, painel elétrico, rádio, ventilador/filtro, tanque de água, relógio, quadro de avisos.
- Props: latas, garrafas, caixas, mochila, lanterna, pilhas, kits médicos, ferramentas, cartas, canecas.
- Exterior posterior: fachada, gôndolas, caixas de supermercado, carrinhos, veículos abandonados, postes, barricadas.

## 13. PLANTA FUNCIONAL — PRIMEIRA VERSÃO DO BUNKER

**Planta proposta em um pavimento, não engenharia estrutural:**

```text
                         NORTE
+--------------------------------------------------------+
| SALA DE RÁDIO |  OFICINA  | GERADOR / FILTRAGEM         |
|     4x4       |    5x4    |          5x4                |
+----------+----+-----+-----+-------------+--------------+
| ENFERMARIA 4x4|  CORREDOR TÉCNICO 2m    | DESPENSA 6x5 |
+---------------+------+------------------+--------------+
| DORMITÓRIO 6x5       | SALA DE CONVIVÊNCIA 9x7         |
| quatro camas         | mesa, sofá, rádio, jogos         |
+----------------------+---------------+-----------------+
| SANITÁRIO 3x3        | COZINHA 5x5   | ENTRADA /       |
|                     |               | ANTECÂMARA      |
+---------------------+---------------+--------+---------+
                                               |
                                      ESCADA AO ESTOQUE
                                      DO SUPERMERCADO
```

**ATENÇÃO:** o esquema é relacional, não está em escala. O agente deve gerar uma planta geométrica consistente com paredes sem sobreposição, acessos reais e corredores navegáveis. Antes de detalhar, gerar vista ortográfica superior cotada e um walkthrough simples.

## 14. PIPELINE BLENDER → UNREAL

1. Criar diretório de projeto com `docs/`, `blender/`, `exports/`, `unreal/`, `references/`, `screenshots/`, `scripts/` e `logs/`.
2. Criar arquivo mestre `blender/Bunker_Blockout_v001.blend` com coleções `ARCH_Walls`, `ARCH_Floors`, `ARCH_Ceilings`, `ARCH_Doors`, `ARCH_Stairs`, `PROPS_Blockout`, `LIGHTS_Preview`, `COLLISION`, `REFERENCE`.
3. Criar blockout paramétrico via script Python para Blender (`bpy`), executável novamente sem duplicar objetos.
4. Usar metros, grade de 0,5 m, nomes estáveis e materiais provisórios distintos por função.
5. Gerar câmeras de apresentação: `CAM_Top`, `CAM_Entrance`, `CAM_CommonRoom`, `CAM_Corridor`, `CAM_Storage`.
6. Salvar `.blend`, exportar `.fbx` ou `.glb` por asset/coleção segundo testes de importação, e gerar renders PNG de inspeção.
7. Criar relatório `docs/BLOCKOUT_REPORT.md` com dimensões, lista de objetos, portas, rotas, problemas e evidências de execução.
8. Importar amostra no Unreal e confirmar escala, orientação, pivôs e colisão antes de modelar detalhes.
9. Refinar apenas após validar circulação com quatro cápsulas de personagem e câmera de primeira pessoa.
10. Versionar scripts e documentação em Git; arquivos binários grandes sob Git LFS ou armazenamento de assets apropriado.

**Critérios de aceite B1:**
- `.blend` abre sem erros, coleções organizadas e objetos nomeados.
- Nenhuma sala obrigatória ausente no blockout.
- Há caminho físico contínuo do estoque do supermercado à antecâmara e às salas principais.
- Portas têm vãos reais e dimensões coerentes; sem interseções críticas.
- Escala comprovada por referência humana de 1,75 m.
- Cinco imagens de revisão geradas e arquivos de exportação existentes.
- Script pode ser reexecutado sem duplicar a cena.

## 15. ROADMAP POR MARCOS

**B0 — Preparação (antes de abrir o Blender):** verificar versões, caminhos, permissões, espaço em disco, render disponível, capacidade de executar scripts, ferramentas Unreal, estrutura de pastas e estratégia de backup. Entregável: plano de execução e relatório de ambiente.

**B1 — Bunker blockout:** geometria modular e navegação. Entregável: `.blend`, exports, imagens, relatório e script.

**B2 — Kit visual do bunker:** paredes, portas, iluminação e materiais-base; mobiliário simples. Entregável: assets reutilizáveis com UVs, pivôs e colisões testados.

**B3 — Supermercado blockout:** gôndolas, estoque, acesso e percurso de coleta; cronômetro apenas na Unreal. Entregável: cena Blender e mapa importável.

**U1 — Protótipo multiplayer:** quatro clientes conectados, locomoção, portas e objetos replicados.

**U2 — Loop de sobrevivência:** coleta, inventário, consumo, necessidades, tempo, gerador e salvamento.

**U3 — Expedição vertical slice:** uma rua, um prédio, radiação, um inimigo, rádio, morte e retorno.

**U4 — Evento e minigame:** ao menos três eventos sistêmicos e um minigame simples.

**U5 — Teste fechado:** quatro amigos, 30–60 min, registro de bugs, telemetria de recursos e entrevista pós-partida.

**U6 — Produção de conteúdo:** mais locais, ameaças, eventos, progressão, finais, acessibilidade, localização, otimização e integração Steam.

**Gate de avanço:** só passar ao próximo marco quando entregáveis e critérios de aceite do marco anterior estiverem confirmados. Não prometer prazos sem medir a capacidade real da equipe.

## 16. MVP VERSUS LANÇAMENTO

| Recurso | Primeiro protótipo | Meta de lançamento |
|---|---|---|
| Multiplayer | 4 via conexão de teste | Convites Steam, reconexão robusta |
| Bunker | Blockout + salas essenciais | Arte final + interações completas |
| Supermercado | Área de coleta funcional | Múltiplas rotas e variação de loot |
| Mundo externo | Rua + 1 prédio | 5–6 zonas compactas |
| Necessidades | Fome, sede, saúde | Energia, radiação, doenças e estados |
| Itens | 12–20 tipos | 50–80 tipos balanceados |
| Inimigos | 1 arquétipo | 3–4 arquétipos |
| Eventos | 3 | 20–30 eventos/variações |
| Minigames | 1 simples | Cartas, sinuca e outros conforme teste |
| Finais | 1 objetivo | 2–3 rotas narrativas |
| Voz | Teste de proximidade | Proximidade + rádios + controles |

*Quantidades de lançamento são metas de planejamento, não compromissos irrevogáveis; validar diversão antes de ampliar conteúdo.*

## 17. TESTES DE ACEITE DO JOGO

**T01:** quatro jogadores entram e interagem com a mesma porta sem divergência de estado.  
**T02:** dois jogadores tentam pegar a mesma lata simultaneamente; apenas um obtém o item.  
**T03:** jogador come uma lata escondido; estoque cai para todos, sem revelar autor automaticamente.  
**T04:** explorador sai de alcance de voz e não é ouvido sem rádio.  
**T05:** explorador morre; bunker não recebe mensagem de morte ou posição.  
**T06:** rádio sem bateria não transmite.  
**T07:** jogador reconecta sem duplicar mochila.  
**T08:** gerador desliga; iluminação e dispositivos dependentes reagem de modo consistente.  
**T09:** jogador coleta suprimentos, retorna e deposita itens; persistência funciona após salvar/carregar.  
**T10:** jogo continua com 1, 2 ou 3 sobreviventes.  
**T11:** portas e corredor comportam quatro jogadores sem bloqueio irrecuperável.  
**T12:** missão crítica tem rota alternativa se item-chave se perder.  
**T13:** controles de microfone, legendas e remapeamento funcionam.  
**T14:** medir FPS e latência em máquinas-alvo a definir; não declarar 60 FPS sem benchmark.  
**T15:** partida de teste produz decisões, escassez e pelo menos um momento social memorável sem intervenção de desenvolvedor.

## 18. RISCOS E MEDIDAS

- **Escopo excessivo:** limitar MVP a bunker + supermercado + rua + um prédio.
- **Rede complexa:** começar replicação no U1, nunca adicionar multiplayer no final.
- **Física cara:** usar representação de inventário estável para itens críticos.
- **Morte gera tédio:** testar duração de sessão, espectador restrito e opções de retorno narrativo em modos alternativos.
- **Discord quebra segredo:** projetar regras de informação internas sem prometer bloquear ferramentas externas.
- **Bunker sem atividades:** incluir interações pequenas e eventos recorrentes, não só minigames caros.
- **Griefing excessivo:** opções de lobby, expulsão por voto e limites de sabotagem, conforme testes.
- **Arte antes da diversão:** priorizar blockout e vertical slice.
- **Dependência de plugins pagos:** validar licença, manutenção e compatibilidade antes de adotar.
- **Propriedade intelectual:** criar identidade, nomes, modelos, sons e UI originais.

## 19. ORDEM DE EXECUÇÃO IMEDIATA PARA CODEX

**Tarefa autorizada agora:** SOMENTE B0 e B1. Não modelar mundo externo completo, não criar sistemas Unreal sem confirmação e não baixar assets pagos.

1. Inspecione o ambiente: sistema operacional, versões do Blender e Python, caminho executável, permissões e diretório de trabalho.
2. Mostre um plano curto com arquivos que serão criados; se precisar sobrescrever algo, peça autorização.
3. Crie pastas e script `scripts/create_bunker_blockout.py` com `bpy`, parametrizado e idempotente.
4. Gere planta coerente do bunker, paredes com espessura, pisos, tetos, vãos de portas, escada de acesso, objetos volumétricos simples e referência humana.
5. Distribua ambientes segundo adjacências da seção 7; não copie literalmente a arte ASCII se ela produzir geometrias impossíveis.
6. Configure coleções, nomes, unidades, pivôs e materiais temporários.
7. Configure câmeras e iluminação de preview; gere vistas superior, entrada, convivência, corredor e despensa.
8. Salve `.blend`, exporte amostra em FBX/GLB e faça validação automatizada de objetos, dimensões e arquivos.
9. Registre resultados reais, capturas e limitações em `docs/BLOCKOUT_REPORT.md`.
10. Pare e apresente entregáveis para aprovação antes de detalhar ou avançar para B2.

**Definição de pronto:** os arquivos existem, o `.blend` abre, a planta é navegável e visualmente compreensível, os cômodos e a escada estão conectados, a escala foi validada e o relatório distingue claramente o que foi executado do que permanece planejado.

## 20. DECISÕES A VALIDAR COM PLAYTEST

- 60 ou 90 segundos de coleta inicial.
- Duração ideal de um dia e da partida.
- Primeira pessoa definitiva ou opção de terceira pessoa.
- Dificuldade de solo e duo.
- Morte instantânea ou janela de incapacitação.
- Liberdade de sabotagem e regras anti-griefing.
- Grau de horror versus humor.
- Tamanho final do bunker e número de pavimentos.
- Quais minigames merecem entrar no lançamento.
- Se resgate depende de dias sobrevividos, quests ou combinação.

**Princípio final:** criar primeiro um bunker em que quatro amigos queiram passar tempo juntos; depois criar razões fortes para que precisem sair dele.
