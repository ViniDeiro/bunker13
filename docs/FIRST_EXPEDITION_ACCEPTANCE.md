# Marco 4 — primeira reposição externa

Objetivo: uma equipe mantém o abrigo enquanto outra sai, recolhe recursos finitos e volta para recuperar a infraestrutura. Usar somente supermercado, acesso e exterior existentes; nenhuma expansão de bairro.

## Dependências

- Infraestrutura 0.4.0: combustível, peças, cartucho, energia e água têm efeitos reais.
- Parte 1: validar antecâmara com duas folhas, procedimento de pressão e recuperação sem energia no executável.
- Inventário/GUIDs, concorrência, checkpoint e reconexão continuam sendo a única fonte de propriedade dos itens. Não criar uma contabilidade paralela de recursos de expedição.
- Introduzir suprimentos persistentes exige uma migração aditiva explícita: saves 0.4.0 já exigem todas as chaves InfraV1 conhecidas. Não basta acrescentar chaves e relaxar a validação global, nem gerar estoque a cada carregamento.

## Próxima parte executável

1. Auditar os pontos físicos existentes de coleta e a rota de ida e volta. Validar alcance, colisão e circulação; reaproveitar os modelos de combustível/peças/filtro já editáveis no Blender.
2. Criar um conjunto finito de suprimentos com chaves versionadas, independente dos recursos já existentes. Preservar os IDs antigos e fazer backup antes da migração. O conjunto novo é introduzido uma única vez; unidades coletadas, largadas, guardadas ou consumidas não reaparecem ao retomar.
3. Jogadores podem transportar e disputar esses objetos usando o inventário autoritativo existente. Sem recompensas abstratas, teleportar loot para o bunker, avisos globais de mochila ou objetivos que revelem o estado dos exploradores.
4. Voltar fisicamente pela escada e antecâmara, descarregar/guardar ou usar o recurso. Combustível obtido fora deve aumentar o tanque e permitir religar circuitos; peças devem recuperar condição. A coleta inicial continua sendo uma escolha de recursos, não uma autorização para criar estoque infinito depois.
5. Persistir e reconectar durante a saída, após a coleta e depois do retorno. Conferir o mesmo GUID no mundo, na mochila e no consumo final, sem cópia concorrente.

## Aceite do marco completo

- Percurso real de saída, exploração, coleta, retorno e uso de suprimento no jogo, sem teleporte entre esses pontos no ensaio de circulação.
- Falta de energia não impede toda recuperação; falta de espaço/peso impede coleta sem destruir o item.
- Dois jogadores disputando uma unidade produzem um único proprietário. Quatro conexões com latência/perda mantêm o estado do host.
- Migração de checkpoint anterior, retomada em processos independentes e reconexão mantêm estoque, posição, IDs e infraestrutura; nenhum reabastecimento por reiniciar a sessão.
- Capturas reais, FPS, bugs e limitações; teste humano separado da automação. Validar o primeiro percurso antes de ampliar o mapa.

## Fronteira desta etapa

A antecâmara isoladamente não comprova uma expedição. Uma ida de coleta isolada também não comprova todo o ciclo de sobrevivência social: radiação/proteção persistentes, inimigo/combate, morte com equipamento recuperável e comunicação limitada ainda têm marcos próprios. Não trocar essas pendências por novas salas ou decoração.
