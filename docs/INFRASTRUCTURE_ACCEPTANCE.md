# Infraestrutura funcional - contrato de entrega de 04/11/2026

Escopo autorizado: infraestrutura dentro do bunker existente. Não expandir o mapa nem implementar expedição, radiação, combate, morte ou voz nesta entrega. Referências: GDD original, seções 3-5 e T08/T09; relatório consolidado de 03/11. O loop completo continua a meta, mas esta etapa apenas cria a crise e sua manutenção local.

## Marco 1 - Gerador

Dependências: transações autoritativas, GUIDs existentes, novos modelos físicos de combustível/peças, regras em Data Asset e migração aditiva de checkpoint.

Aceite: consumo real, tanque limitado, condição com desgaste; falha por esgotamento; abastecer/reparar somente desligado, ao alcance e com visada; trabalho cancelável sem consumir item, item exato consumido uma única vez ao concluir; estado replicado, retomada sem consumo offline, IDs legados preservados.

## Marco 2 - Circuitos

Depende do marco 1 aprovado no executável. Aceite: circuito social e circuito de serviços com controles físicos; lâmpadas e equipamentos reagem nas conexões, lâmpadas de emergência mantêm orientação; desligar cargas reduz consumo, reversão recupera intensidades/materiais originais; não alterar os assets de arte aprovados.

## Marco 3 - Água

Depende do circuito de serviços. Aceite: reservatórios finitos de água bruta/tratada, processamento limitado por energia e filtro; troca de cartucho consome unidade real; beber desconta volume e recupera somente a hidratação necessária; sem produção offline, duplicação ou água negativa; estado persistido.

## Validação e limites

Ensaios por marco em Unreal executando o jogo; repetir no pacote Mac, com quatro conexões, concorrência e emulação de rede, retomada e regressões de inventário/reconexão. Conferir capturas, medir FPS/frame p95 e registrar falhas. Automação não equivale a quatro humanos nem à aprovação visual comercial. Sem Windows ou internet certificados nesta etapa.

O abastecimento externo, coleta de água bruta e a reposição em expedição permanecem pendentes; os estoques iniciais devem ser finitos e documentados. Água do reservatório é um recurso em litros, não uma geração de garrafas ou novos GUIDs.
