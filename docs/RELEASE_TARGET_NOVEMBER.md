# Meta de entrega — 30 de novembro de 2026

**Histórico: substituído em 21/10/2026 pela meta de dezembro, descrita em `RELEASE_TARGET_DECEMBER.md`.**

Meta solicitada pelo criador em 19/10. Não constitui garantia de lançamento: cada etapa depende dos critérios abaixo. A referência de produto continua sendo o GDD integral; requisitos sem implementação não serão declarados concluídos.

| Período alvo | Entrega | Critério de saída |
|---|---|---|
| 19–25/10 | Base cooperativa U1 | Quatro conexões reais; coleta sem duplicação; camas exclusivas; portas replicadas; circulação e desconexão verificadas |
| 26/10–01/11 | Sobrevivência U2 | Inventário físico, consumo, necessidades, energia/combustível, tempo, contêineres, salvamento e reconexão sem duplicação |
| 02–08/11 | Partida completa U3 | Coleta inicial de 90 segundos; expedição rua/prédio; radiação, inimigo/combate, morte/mochila, retorno e objetivo com encerramento |
| 09–15/11 | Atividades e atmosfera U4 | Minijogo com habilidade, eventos sistêmicos; áudio, animações/interações e acabamento coerentes; comparação visual no executável |
| 16–22/11 | Integração e conteúdo | Voz local e rádio, convites, requisitos de acessibilidade, conteúdo e finais previstos no GDD; build Windows validada |
| 23–30/11 | Candidato a lançamento | Sessões de 30–60 minutos com quatro humanos; latência/perda; saves, desempenho e regressões; correções críticas e aprovação final |

## Bloqueios que precisam de evidência

- A máquina atual produz builds Mac; o alvo Windows requer uma máquina/ambiente Windows com Unreal e teste no hardware de destino.
- Steam, voz e distribuição dependem de configuração real dos serviços, conta do produto e testes. Não há integração comprovada hoje.
- O MacBook já exigiu otimização. Cada lote de arte precisa preservar o orçamento de desempenho, com medição na partida; limitar FPS não demonstra estabilidade.
- O conteúdo completo de lançamento (quantidade de itens, eventos, zonas e finais) é maior que a fatia inicial. Redução de escopo só poderá ocorrer com autorização do criador; eventual atraso será apresentado com requisitos concretos pendentes.

## Rotina de entrega

Cada avanço deve deixar código/fontes, um executável reproduzível quando houver alteração jogável, relatório de testes e pendências explícitas. Uma etapa não passa por ter apenas compilado. O jogo só será considerado pronto depois de concluir os requisitos e os testes correspondentes.
