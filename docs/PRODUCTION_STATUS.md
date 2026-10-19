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
| U1 | Base de servidor autoritativo para coleta e camas implementada; quatro pontos de entrada e RPCs por proprietário. Treze portas físicas replicadas instaladas; 13/13 travessias passaram com a cápsula real. Lobby, circulação conjunta, desconexão e testes completos ainda pendentes; evidências em `NETWORK_FOUNDATION_REPORT.md` e `DOORS_AND_INPUT_REPORT.md` |
| U2 | Mochila com interface, IDs por sessão, espaços/peso, consumo e descarte; necessidades e recuperação de energia na cama validadas no executável com quatro instâncias automatizadas (SURVIVAL_INVENTORY_REPORT.md). Regras em Data Asset; atributos privados ao dono. Faltam empilhamento, tempo, combustível/circuitos, contêineres, salvamento e reconexão |
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

A meta solicitada é 30/11/2026. Sequência e critérios de saída em `RELEASE_TARGET_NOVEMBER.md`. Não há garantia de lançamento nem autorização implícita para remover requisitos do GDD para caber no prazo.
