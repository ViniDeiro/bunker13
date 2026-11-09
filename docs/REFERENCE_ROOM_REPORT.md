# Condomínio 13 - sala de referência

22/10/2026 · Deiros Dev · versão de desenvolvimento 0.2.0

## Resultado e aprovação

Sala de convivência integrada na Unreal, com kit editável no Blender, armário físico e gestos observáveis em rede. Os testes abaixo passaram no executável. Isso não equivale a aprovação visual comercial: a avaliação artística continua com o criador. Nenhum outro ambiente recebeu nova produção de arte.

## Como avaliar

Abrir `builds/Mac/Avaliar-Sala-Convivencia.command`. A sessão abre direto na sala, não grava campanha e move uma água e uma comida já existentes no mapa para o armário. O executável normal preserva o checkpoint e começa com o armário novo vazio.

E abre/fecha a porta; E no objeto pega. I e setas selecionam um item da mochila pessoal; fechar a mochila e X num espaço livre guarda. A interação do armário não abre estoque em modal. WASD e mouse mantêm a sensibilidade anterior.

## Arte e construção

- 20 meshes de referência, 10 materiais Unreal e 30 mapas PBR originais de 1024 px; 30 mapas usados e incorporados na fonte Blender.
- Biblioteca de assets e montagem em coleções separadas; FBX por asset, materiais e áudio em pastas próprias. Atores Unreal agrupados por função. O forro acabado ficou com cerca de 2,78 m livres, ajustado abaixo da laje já existente do supermercado.
- Concreto, aço, tinta, tecido, borracha, madeira, papel e cerâmica com respostas diferentes; escala de mapeamento de 1 metro, variação ampla e desgaste contido.
- Piso interno de 8,8 x 6,8 m dentro do envelope existente de aproximadamente 9 x 7 m. Mesa com cerca de 74 cm de altura; quatro cadeiras e sofá.
- Folha, corpo e prateleiras do armário separados; pivô na dobradiça, folga lateral de 4 mm e colisão própria para a folha. Apoio de cada item calculado pela base real da malha.
- Os quatro volumes antigos Mesa_Cartas, Radio_Social, Estante_Social e Quadro_Avisos foram retirados de uma cópia derivada da malha geral. Original preservado; 32 vértices e 24 faces de caixa removidos; demais materiais e 13 portas nativas preservados.
- Iluminação motivada por luminárias visíveis; luz social quente e apoio mais neutro. Três luminárias direcionadas com sombras dinâmicas, apoio de baixo custo e oclusão local.
- Novos mapas e foley são procedurais originais; não são uma nova exportação do Painter. Os projetos Painter anteriores não foram sobrescritos.

## Contrato físico e dados

- GUID de cada unidade preservado em mochila, contêiner e mundo. Slot 0-11 é estável e não depende do índice do array.
- Host valida abertura suficiente, distância, raio real da câmera, revisão, GUID, ocupação, capacidade e peso. A transação acontece uma única vez no servidor.
- Observadores próximos com visada recebem a representação do interior; a mochila continua privada. A coleta permanece limitada ao alcance de interação.
- Durante a devolução, a representação da prateleira aguarda a mão liberar o objeto, evitando duas cópias visuais. O resultado de inventário é aceito no início da ação, sem reembolso por interrupção cosmética.
- A mão acompanha o puxador móvel; colher e malha aberta acompanham o consumo. Gestos são compartilhados com observadores próximos e com visada.
- Checkpoints anteriores podem omitir apenas o novo armário, inicialmente vazio. IDs, atores antigos e assinatura da base continuam obrigatórios. Versões de save 1/2 mantidas; protocolo de rede atualizado pela versão do projeto.

## Testes nesta versão

| Verificação | Resultado |
|---|---|
| two_players | PASS |
| unique_ownership | PASS |
| no_stock_modal | PASS |
| take | PASS |
| put | PASS |
| closed_rejection | PASS |
| drink_eat | PASS |
| put_preserves_id | PASS |
| competing_request_rejected | PASS |
| remote_actions_visible | PASS |
| circulation | PASS |
| final_empty | PASS |
| snapshots_agree | PASS |

Além das 13 verificações do cenário físico: cinco processos independentes de save/slot/migração; regressões de persistência solo, estoque anterior e reconexão cooperativa. Checkpoint criado pelo executável anterior e carregado na implementação nova, sem perder mochila, contêiner, objeto largado ou registros de coleta.

Automação usa dois processos realmente renderizados no mesmo computador. Host usa os comandos de entrada do jogo; cliente faz também um pedido concorrente por RPC. Não houve dois humanos ou teste de internet. Regressão cooperativa anterior usa quatro conexões e emulação de 80 ms / 2% de perda; os logs desta execução estão no projeto.

A fonte Blender foi reaberta em um processo independente. Foram verificados escala, vértices finitos, faces válidas, UVs, dimensões, exports, mapas incorporados e correspondência das posições com a Unreal. A validação detectou faces sem área na mesa/caneca; elas foram removidas e os assets reimportados.

## FPS e captura

Apple M2, 24 GB, macOS 26.6.2. Mac Development, Metal.

| Cenário | FPS médio | Frame médio | Mediana | p95 | Amostras |
|---|---|---|---|---|---|
| Antes, janela 1280 x 720 | 60.13 | 16.630 ms | 16.593 ms | 17.310 ms | 962 |
| Depois, janela 1280 x 720 | 58.89 | 16.981 ms | 16.289 ms | 18.835 ms | 942 |
| Dois processos, host | 42.20 | - | - | 51.114 ms | 211 |
| Dois processos, client | 56.50 | - | - | 25.082 ms | 241 |

Solo: cerca de 16 s após aquecimento, sem capturas durante a janela. Dois processos: cerca de 5 s antes da captura do vídeo, nas janelas host 960 x 540 e cliente 800 x 450. A carga inclui as duas renderizações no mesmo M2; não representa dois computadores separados. São amostras curtas, não garantia de FPS numa sessão completa.

Configuração efetiva: `screen_pct=70.0 shadow_quality=2 max_fps=0.0 vsync=1`.

Vídeos usam screenshots nativos com os intervalos registrados, em cerca de 6-7 amostras/s, uma cadência diferente do FPS do jogo. O áudio capturado pela saída do jogo ficou parcial (aproximadamente 3,6 s para 34 s de vídeo); foi entregue separadamente e não inserido fora de sincronia. O vídeo final é silencioso. Os sons de portas continuam implementados no executável. Companion file mostra a perspectiva do cliente.

## Problemas corrigidos e limites

Corrigidos durante a execução: exposição excessiva; volumes antigos sobrepostos; propriedade de duração ausente na replicação; ocultação local afetando relevância de rede; automação mirando interior ao tentar fechar; cálculo da mira usando olhos em vez da câmera real; encosto estreitando a passagem; apoio vertical e pivôs; faces degeneradas.

As capturas ainda mostram limitações visuais: teto com normal aparente demais, serrilhado/cintilação nas linhas finas no perfil de 70% e forte contraste na vista para fora da sala. Esses pontos impedem declarar o critério comercial concluído sem revisão. Duas rodadas de persistência tiveram inicializações vazias com sinal 11. O diagnóstico nativo aponta a pilha LLM/alocador da Unreal durante consulta do macOS; a causa não foi corrigida. Foram preservados logs e diagnóstico sanitizado em logs/reference_startup_crash_summary.json. A suíte registra repetições apenas quando o processo não chegou a produzir saída; passar após repetição não comprova estabilidade de inicialização. Permanecem para aprovação/refino: naturalidade das mãos rígidas/procedurais, produção de dedos articulados e atuação corporal final; revisão humana de materiais e iluminação em movimento; foley gravado final; sessões longas de quatro pessoas e Windows. TV e mesa de cartas não viraram novos sistemas de jogo. Rádio e alvo preservam os comandos demonstrativos anteriores; dardos ainda usam pontuação aleatória. Os seis estoques antigos conservam modal até aprovação desta referência.

## Entregáveis

- `blender/Convivencia_Reference_v001.blend`
- `exports/reference_room/` e `exports/Bunker_ReferenceShell.fbx`
- `assets/reference_room/`
- `unreal/Condominio13/Content/Bunker/ReferenceRoom/` e mapa `Bunker/Lvl_Bunker`
- `builds/Mac/Condominio13-VerticalSlice.app`
- `builds/Mac/Avaliar-Sala-Convivencia.command`
- `screenshots/reference_before_*.png`, `reference_after_*.png` e vistas Blender
- `output/video/Condominio13_Armario_Fisico.mp4` e perspectiva cliente
- `output/pdf/Condominio_13_Sala_Referencia_2026-10-22.pdf`
- `logs/reference_delivery_manifest.json` e relatórios de execução

## Integridade

Blender SHA-256: `5db5e85ff06ab55a025f72b592dce1d1dec7218a53579565b376211ab9224cea`
Executável SHA-256: `939334df5ae8a093529da553fa4db0c91db49c77ad2ebf5877074c05f2836b64`

Assinatura Mac verificada. Scripts e fontes salvos no projeto; checkpoint pessoal e credenciais reais não fazem parte do pacote.
