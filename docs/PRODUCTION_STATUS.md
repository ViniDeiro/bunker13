# Estado real da produção

A solicitação atual autoriza avançar no acabamento e nos sistemas do GDD. O documento continua sendo a especificação do produto; sua restrição histórica a B0/B1 já foi superada pelas autorizações posteriores do usuário.

## Arte

- Arquitetura navegável e mobiliário construído: existentes; muitas silhuetas ainda são primitivas geométricas.
- Texturas do ambiente: seis superfícies procedurais com BaseColor, Normal e ORM em 512px, geração reproduzível e aplicação em escala mundial.
- Kit refinado: cama, armário e porta com UVs, bordas biseladas e três projetos Painter `.spp`. Onze materiais e 33 mapas de 1024px produzidos no Painter, exportados e aplicados por UV na Unreal. Quatro camas e quatro armários substituídos no dormitório; porta agora equipa 13 folhas móveis com colisão e movimento replicado; as três lacradas permanecem fixas.
- Em 19/10, o kit foi conferido no executável e E/F testados na cama. Essa validação não aprova a arte do bunker inteiro nem encerra os marcos de gameplay.
- Ainda pendentes: modelos com bordas e silhuetas refinadas, UVs por asset quando necessários, decalques narrativos, sinalização legível, acabamento externo e aprovação visual em perspectivas representativas.

## Sistemas

A base de interações passou a usar um controlador por conexão e decisões no servidor. Isso ainda não representa conclusão do GDD:

| Marco | Estado real e trabalho restante |
|---|---|
| U1 | Base de servidor autoritativo para coleta e camas implementada; quatro pontos de entrada e RPCs por proprietário. Treze portas físicas replicadas instaladas; 13/13 travessias passaram com a cápsula real. Checkpoint do host e reconexão local validados em `COOP_RECONNECT_REPORT.md`. Lobby, circulação conjunta com humanos, identidade Steam e testes completos ainda pendentes; evidências em `NETWORK_FOUNDATION_REPORT.md` e `DOORS_AND_INPUT_REPORT.md` |
| U2 | Mochila com interface, IDs preservados nos checkpoints solo e cooperativo, espaços/peso, consumo e descarte; necessidades e recuperação de energia na cama validadas no executável com quatro instâncias automatizadas (SURVIVAL_INVENTORY_REPORT.md). Regras em Data Asset; atributos privados ao dono. Salvamento solo e cooperativo com retomada dos participantes implementados; ver `PERSISTENCE_REPORT.md` e `COOP_RECONNECT_REPORT.md`. Faltam empilhamento, tempo, combustível/circuitos, autenticação Steam, recuperação de perfis e testes prolongados |
| U3 | Exterior inicial existe; faltam prédio explorável, radiação, equipamento, inimigo, combate, morte, mochila e retorno |
| U4 | Dardos são uma pontuação aleatória por interação; faltam mira jogável, cartas e três eventos sistêmicos |
| U5 | Pendente teste de 30–60 min com quatro jogadores, latência e perda de pacotes |
| U6 | Pendentes voz por proximidade e rádio, Steam, acessibilidade, áudio, conteúdo de lançamento e finais |

Map Check verifica a estrutura do mapa; não prova circulação com quatro jogadores nem execução de gameplay. Compilar e empacotar não comprova qualidade visual nem uma partida completa. O limite configurado de 45 FPS não é um benchmark.

## Ordem de conclusão

1. Preservar a validação do kit Painter no executável e completar a base cooperativa U1.
2. Teste ampliado de E/F, portas e saída das camas aprovado no executável; ainda executar sessões com quatro humanos e encerrar as pendências de U1.
3. Completar U2 com salvamento e anti-duplicação.
4. Fechar uma partida de ponta a ponta em U3/U4, incluindo objetivo e encerramento.
5. Executar U5 e corrigir os problemas antes do conteúdo adicional de U6.

Não há build Windows validada neste Mac. Uma entrega Windows exige compilação e teste em ambiente Windows apropriado. Convites Steam e voz exigem configuração e testes reais das respectivas integrações.

## Meta de calendário

A meta solicitada agora é dezembro de 2026, sem dia definido. Sequência e critérios de saída em `RELEASE_TARGET_DECEMBER.md`. Não há garantia de lançamento nem autorização implícita para remover requisitos do GDD para caber no prazo.

## Objetos físicos do inventário — 19/10/2026

Cinco modelos próprios (água, lata, kit médico, pilha e chave) criados no Blender com peças editáveis, UVs e texturas originais. Aplicados aos seis recursos existentes do mapa. Fonte, renders e limites estão em `ITEM_ART_REPORT.md`; não substituem a produção dos demais tipos, mãos ou animações de uso.

## Primeira pessoa: interações com itens — 19/10/2026

Mãos enluvadas e acessórios próprios, gestos locais de coleta/consumo e variantes abertas de garrafa/lata. A confirmação vem do servidor e a mochila fecha para mostrar a ação. Fonte e limites em `FIRST_PERSON_ITEM_REPORT.md`. Ainda não há rig articulado dos dedos, som de manuseio ou atuação em terceira pessoa.

## Armários e despensa — 19/10/2026

Seis contêineres físicos, transferências com ID preservado, validação de revisão/capacidade/acesso e vistas privadas por jogador. A garrafa passou a azul. Evidências e limites em `STORAGE_REPORT.md`; o armazenamento é da sessão atual, com salvamento/reconexão ainda pendentes.

## Persistência solo — 21/10/2026

Mochila, necessidades, contêineres, recursos do mapa, itens largados e portas passaram a compor um checkpoint versionado, com duas cópias alternadas. F5, gravação automática e encerramento normal; restauração ao iniciar. Evidências e limites em `PERSISTENCE_REPORT.md`. Isso não conclui o salvamento de sessões cooperativas nem a reconexão.

## Checkpoint cooperativo e reconexão local — 21/10/2026

Até quatro conexões, reserva dos recursos desconectados, credenciais privadas locais e retomada dos três perfis após reinício do host. A rodada com 80 ms/2% de emulação preservou seis recursos únicos e bloqueou credenciais inválidas/duplicadas. Relatório em `COOP_RECONNECT_REPORT.md`; ainda não equivale a autenticação Steam, lobby acessível ou teste prolongado com humanos.
