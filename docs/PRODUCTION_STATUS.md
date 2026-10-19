# Estado real da produção

A solicitação atual autoriza avançar no acabamento e nos sistemas do GDD. O documento continua sendo a especificação do produto; sua restrição histórica a B0/B1 já foi superada pelas autorizações posteriores do usuário.

## Arte

- Arquitetura navegável e mobiliário construído: existentes; muitas silhuetas ainda são primitivas geométricas.
- Texturas do ambiente: seis superfícies procedurais com BaseColor, Normal e ORM em 512px, geração reproduzível e aplicação em escala mundial.
- Kit refinado: cama, armário e porta com UVs, bordas biseladas e três projetos Painter `.spp`. Onze materiais e 33 mapas de 1024px produzidos no Painter, exportados e aplicados por UV na Unreal. Quatro camas e quatro armários substituídos no dormitório; porta ainda é um asset sem substituição funcional.
- Em 19/10, o kit foi conferido no executável e E/F testados na cama. Essa validação não aprova a arte do bunker inteiro nem encerra os marcos de gameplay.
- Ainda pendentes: modelos com bordas e silhuetas refinadas, UVs por asset quando necessários, decalques narrativos, sinalização legível, acabamento externo e aprovação visual em perspectivas representativas.

## Sistemas

As interações anteriores são protótipos locais. Não representam conclusão do GDD:

| Marco | Estado real e trabalho restante |
|---|---|
| U1 | Personagem navegável existente; implementar servidor autoritativo, quatro jogadores, portas, transações de itens e testes concorrentes |
| U2 | Coleta local e cama existentes; faltam inventário com capacidade, consumo, fome/sede/saúde/energia, tempo, combustível, contêineres, salvamento e reconexão |
| U3 | Exterior inicial existe; faltam prédio explorável, radiação, equipamento, inimigo, combate, morte, mochila e retorno |
| U4 | Dardos são uma pontuação aleatória por interação; faltam mira jogável, cartas e três eventos sistêmicos |
| U5 | Pendente teste de 30–60 min com quatro jogadores, latência e perda de pacotes |
| U6 | Pendentes voz por proximidade e rádio, Steam, acessibilidade, áudio, conteúdo de lançamento e finais |

Map Check verifica a estrutura do mapa; não prova circulação com quatro jogadores nem execução de gameplay. Compilar e empacotar não comprova qualidade visual nem uma partida completa. O limite configurado de 45 FPS não é um benchmark.

## Ordem de conclusão

1. Validar texturas no executável e refinar os ambientes com evidência visual.
2. Implementar U1 antes de ampliar transações locais de itens.
3. Completar U2 com salvamento e anti-duplicação.
4. Fechar uma partida de ponta a ponta em U3/U4, incluindo objetivo e encerramento.
5. Executar U5 e corrigir os problemas antes do conteúdo adicional de U6.

Não há build Windows validada neste Mac. Uma entrega Windows exige compilação e teste em ambiente Windows apropriado. Convites Steam e voz exigem configuração e testes reais das respectivas integrações.
