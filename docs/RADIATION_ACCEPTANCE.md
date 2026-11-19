# Marco 5 — radiação e proteção persistentes

09/11/2026. Escopo autorizado: criar consequências na primeira expedição existente. Não ampliar mapa, adicionar combate ou modificar a sala aprovada neste marco.

## Dependências antes da integração

- Expedição 0.4.2 e seus GUIDs/checkpoints/reconexão.
- Zonas de exposição com volumes editáveis, taxa configurável e avaliação no host; não deduzir todo risco apenas pela altura do jogador.
- Equipamento físico próprio, modelado/editável, com GUID e condição persistentes. O cartucho do purificador existente não se transforma silenciosamente em respirador.
- Parâmetros em Data Asset, estado pessoal privado e extensão validada dos registros solo/remotos. Backup e teste de migração de 0.4.2 antes de gravar campanha real.
- Tratamento usa recurso finito, com validação e consumo único; não há botão gratuito que apaga exposição.

## Critérios de aceitação do marco completo

1. Durante a fase de abrigo, entrar/sair de uma zona muda a taxa; ficar no bunker não acumula exposição externa. O host calcula o tempo e a taxa.
2. Proteção equipada reduz exposição e perde condição. Esgotar no meio de um intervalo não protege até o próximo tick. Guardar, transferir, largar e reequipar não repara nem duplica equipamento.
3. Voltar não apaga a carga acumulada. Ultrapassar limiar causa consequência observável pessoal também no abrigo; limites e efeitos vêm de configuração.
4. Tratamento válido consome uma unidade identificada e reduz a carga uma vez; falta de necessidade/recurso, distância inválida ou disputa não destroem nem duplicam unidades.
5. Checkpoint/reinício e reconexão mantêm carga, condição e proprietário do item; ausência de campos antigos tem migração explicitamente testada. Dados inválidos são rejeitados antes da aplicação.
6. Quatro conexões com latência/perda: cliente não define dose/condição; UI pessoal não revela saúde, exposição ou morte dos outros. Sem transmissão global de aviso de exploração.
7. Percurso físico de saída/coleta/retorno com efeitos reais no pacote; capturas, FPS com janela/cenário definidos e bugs registrados. Desconexão não limpa sintomas. Playtest humano continua separado.

Os valores são regras fictícias de sobrevivência, sem pretensão de simular dosimetria ou tratamento médico real. Redução por equipamento será definida como mecânica de contaminação do jogo; não prometer blindagem genérica contra toda radiação.

## Etapa 5A realizada

Implementado o cálculo isolado: carga limitada a 0–100, proteção com desgaste integrado ao longo do passo, sintomas por limiar que continuam em área segura, tratamento sem reparar proteção e rejeição atômica de valores inválidos. Taxas são entradas; nenhum balanceamento foi fixado como configuração final do jogo.

`scripts/test_radiation_model.py` compila o código de produção com AddressSanitizer/UndefinedBehaviorSanitizer. Há 25 verificações, incluindo independência da subdivisão do tempo, esgotamento, limiar, saturação, NaN, infinito e overflow. Teste adicional da engine: `C13.Unit.Radiation.Model`.

Executado em 09/11: 25 verificações aprovadas, compilação do Editor aprovada e teste `C13.Unit.Radiation.Model` aprovado no runner da Unreal. Este último rodou sem renderização e não percorreu o mapa. O log contém mensagens `Condition failed` durante a inicialização, antes de começar o teste nomeado; elas não aparecem nos eventos dele, mas a origem dessas mensagens permanece para investigação. Não declarar a inicialização inteira isenta de erros.

**Marco 5 completo: pendente.** A biblioteca não está conectada ao tick de sobrevivência, volumes, equipamento, HUD, save ou reconexão. Não altera o executável 0.4.2, não causa dano no jogo e não comprova testes multiplayer de radiação. O próximo trabalho é esse adaptador e o equipamento físico, seguido dos ensaios acima. Não declarar essa etapa como radiação jogável.

## Etapa 5B — exposição na rota existente (17/11/2026)

Escopo: integrar o acumulador e os sintomas à expedição 0.4.2, mantendo o estacionamento e a rota física existentes. O host calcula a exposição uma vez por passo de sobrevivência. A caixa de exposição em coordenadas do mundo e os valores de taxa, limiar e dano são editáveis no Data Asset de regras. A acumulação só ocorre na fase de abrigo com a expedição habilitada. Sair da caixa para voltar ao bunker interrompe a acumulação, mas não os sintomas. O HUD mostra apenas a dose pessoal; a replicação usa a condição de proprietário.

A dose entra como campo aditivo com padrão zero nos registros do jogador local e dos participantes. A validação do checkpoint exige valor finito no intervalo 0–100 antes de restaurar. Inventário, GUIDs e versão do checkpoint foram preservados. A gravação e a restauração dos registros remotos foram conectadas, mas precisam de ensaio de reconexão com exposição não nula antes de serem consideradas validadas.

Dependências: mapa de expedição, regras de sobrevivência, persistência e modelo 5A. Critérios desta etapa: alcançar a caixa a pé, observar dose e dano, restaurar a dose após reiniciar, voltar a pé com a dose estável e a saúde diminuindo, consumir os itens coletados para restaurar o gerador e medir FPS. A proteção, tratamento, quatro jogadores expostos e o novo pacote continuam pendentes.

Resultado: 25 verificações do modelo com sanitizadores e build do Editor aprovados. Ensaio com um host renderizado percorreu 11 pontos de saída e 11 de retorno. Dose salva e restaurada após reinício: 31,4893. No abrigo, dose estabilizada em 35,9732 e saúde de 78,9970 para 72,7030. Os seis GUIDs de suprimento foram preservados; combustível e peças recolhidos foram consumidos para religar o gerador. Os 449 assets anteriores passaram na conferência.

FPS em janela 960 × 540, resolução interna de 70%, sombras e AO desligados, limite 30: saída 29,80 FPS (p95 33,84 ms); retorno 29,89 FPS (p95 33,48 ms). Amostras de cerca de 16 s no início de cada trecho, não da rota inteira. Capturas do jogo em `screenshots/radiation_5b/`; evidência consolidada em `docs/validation/radiation_5b_2026-11-17.json`. A primeira compilação dos probes falhou na formatação do perfil de teste do Unreal e foi corrigida antes do ensaio. Na captura clara do exterior, o indicador de exposição fica pouco contrastado acima da faixa do HUD.

O ensaio testa reinício local, sem cliente remoto. Configurar emulação de pacotes nessa execução não comprova rede. Restam reconexão com dose, migração a partir do executável 0.4.2, proteção física, tratamento e ensaio multiplayer antes de aprovar o marco 5 inteiro. Nenhum novo executável publicado.
