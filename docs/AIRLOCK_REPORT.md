# Condomínio 13 — antecâmara funcional / 0.4.1

04/11/2026. Primeira parte do marco de expedição, usando o bunker e o supermercado existentes. **Não é uma expedição completa, nem o ciclo de sobrevivência concluído.**

## Resultado

Após a coleta e o fechamento inicial, as duas portas passam a funcionar como antecâmara. Fechar a outra folha e esperar seu fechamento físico é obrigatório antes de equalizar e abrir a porta de destino. Pedidos incompatíveis são rejeitados pelo host, incluindo a tentativa de outro jogador abrir a folha oposta.

Equalização simplificada: 5 s com o circuito de serviços energizado; 12 s com acionamento manual sem energia. São parâmetros do Data Asset, não uma simulação de gases. Se a energia cair durante um ciclo elétrico, o host reinicia um prazo manual completo. O retorno externo mantém a liberação de emergência com E pressionado, inclusive com penalidade por exaustão.

Também é possível fechar a porta externa pelo lado de fora. A proteção existente contra esmagamento continua ativa. Em uma situação herdada com a folha interna aberta e o sobrevivente fora, a liberação solicita seu fechamento seguro; uma pessoa no arco continua bloqueando a movimentação. Um ciclo pronto e abandonado pode ser reiniciado para a outra porta, sem apagar recursos.

O tempo/estado da equalização é replicado. O checkpoint mantém os estados existentes de portas, recursos, calendário e inventário; o procedimento transitório de pressão precisa ser feito novamente após retomar. Nenhuma chave de ator, GUID ou formato de item foi trocado por esta etapa. A versão anterior do aplicativo permanece preservada.

## Testes executados nesta versão

| Ensaio | Resultado e alcance |
|---|---|
| Coleta e fechamento | R inicia a coleta de 35 s no ensaio; porta fecha fisicamente. No jogo normal continuam 90 s. |
| Antecâmara com dois processos | E real, ciclo energizado, tentativa concorrente incompatível e bloqueio da folha oposta. |
| Falta de energia | Ciclo manual, retorno pela liberação externa, queda de energia durante equalização e fechamento interno solicitado de fora. |
| Passagem | CharacterMovement atravessa as folhas para sair e voltar; teste separado desce a rota real da escada em 13 pontos. |
| Checkpoint novo | Outro processo retoma portas fechadas e infraestrutura; equalização inativa. Isso não equivale a um ensaio específico de desligamento no meio do ciclo. |
| Checkpoint 0.4.0 → 0.4.1 | Item coletado, mesmo GUID e cronômetro retomados com a antecâmara habilitada. |
| Retorno legado exausto | No novo executável, modo anterior sem o procedimento adicional: liberação com energia zero, cancelamento, retorno e rejeição de entrada tardia. Não é um ensaio de exaustão através da sequência nova completa. |
| Reconexão legada | Suíte de quatro conexões no mapa legado, com latência/perda, contra o novo executável. Não certifica quatro pessoas fazendo a nova expedição. |

A validação principal executou dois processos Mac renderizados, com 80 ms / 2% de perda simulada. Não foram dois humanos nem duas máquinas. Fixtures posicionam personagens para os testes das folhas e alteram energia para reproduzir falhas; a locomoção nas passagens usa o movimento real do personagem. Não há teste contínuo de exploração e coleta exterior nesta entrega.

O primeiro ensaio sem renderização falhou na queda de energia porque o comando anterior não fechou a porta interna. Os dois personagens haviam sido posicionados no mesmo ponto; o fixture foi separado e recebeu diagnóstico do alvo realmente atingido pela câmera. A nova execução empacotada passou. O ensaio inicial e sua falha foram preservados em `logs/airlock_preflight_first_failure_*`; não foram promovidos a resultado aprovado.

## FPS observado

| Processo | FPS médio | Frame p95 (ms) | Amostras |
|---|---:|---:|---:|
| host | 26.31 | 83.38 | 421 |
| client | 25.78 | 76.75 | 412 |

Apple M2 / 24 GB, duas janelas de 960 × 540, amostra de aproximadamente 16 s incluindo o cenário de teste. A instância antiga foi encerrada normalmente antes do ensaio empacotado. Não é benchmark Windows, sessão longa, teste de 1280 × 720 solo ou garantia de 60 FPS. O ensaio sem renderização anterior não entra nesta tabela. A média abaixo de 30 FPS nesta condição é uma limitação real a investigar antes de aumentar a carga da cena; não foi isolada uma causa nem feito um comparativo controlado com a versão anterior.

Avisos de buffer de áudio sem dados, observados nos logs desta bateria: `{'airlock_package_network_host.log': 1, 'airlock_package_network_client.log': 1, 'round_network_host.log': 2, 'round_network_client.log': 0}`. Indicam interrupções potenciais de áudio; não foram tratados como ausência de problema porque os testes funcionais passaram.

## Como testar

Usar `builds/Mac/Jogar-Antecamara.command`; para rede local, `Hospedar-Antecamara.command` e `Entrar-Antecamara.command`, com a mesma versão dos dois lados. Os atalhos selecionam o mapa e habilitam o procedimento; abrir o aplicativo diretamente ainda usa o mapa padrão legado.

1. R inicia a coleta no host. Depois do fechamento, entrar na antecâmara e fechar a porta atrás de si com E.
2. Olhar para a porta de destino e pressionar E para iniciar a equalização. Esperar o aviso local e usar E novamente. Afastar-se da folha se a colisão impedir o acionamento.
3. Pelo lado de fora, depois de equalizar, manter E pressionado e continuar olhando para a folha para operar a liberação manual. Soltar E cancela essa liberação; não consome um item.
4. Fechar a porta externa antes de equalizar para a interna. Repetir no retorno. F5 salva no host.

Mochila, consumo, manutenção, armário físico e demais comandos anteriores continuam no projeto; esta entrega não os substitui por interfaces de expedição.

## Arquivos e integridade

- Aplicativo: `builds/Mac/Condominio13-Airlock.app`; assinatura local conferida.
- Código: `BunkerRound`, integração de portas em `BunkerNetwork`, HUD em `BunkerSurvival`, parâmetros em `BunkerSurvival.h`; teste nativo em `BunkerAirlockValidation.cpp`.
- Reprodução: `scripts/run_airlock_delivery.py`, `run_airlock_validation.py`, `collect_airlock_delivery.py`.
- Manifesto com hash do executável e resultados: `logs/airlock_delivery_manifest.json`.
- 79 mapas/assets/fontes Blender protegidos permaneceram iguais byte a byte. Não foi necessário gerar outro modelo para reutilizar as folhas existentes. As fontes editáveis continuam em `blender/`, inclusive `Bunker_Infrastructure_v001.blend`.
- Capturas reais: `screenshots/airlock_client_blocked.png`, `airlock_manual.png`, `airlock_return.png`, `airlock_resumed.png`.

## O que continua faltando

Próxima parte: recursos finitos fora, migração aditiva de estoque sem reaparecimento, exploração/retorno contínuos e uso do mesmo item na infraestrutura, incluindo reconexão durante a saída. Critérios em `docs/FIRST_EXPEDITION_ACCEPTANCE.md`. O procedimento de antecâmara não cria sozinho uma missão nem torna o exterior perigoso.

Depois, em marcos separados: proteção/radiação persistente; inimigo e combate; morte e recuperação de equipamento; comunicação por proximidade/rádio sem aviso global de morte. Objetivo de encerramento, eventos, minijogo real, balanceamento social e sessão humana de 30–60 min também permanecem pendentes.

Limitações desta parte: sem simulação de contaminação/descontaminação, animação manual específica ou áudio novo de válvulas/ventilação; reutiliza o som/animação das portas existentes. O reconhecimento da folha interna pressupõe a posição do mapa atual e precisa ser revisto se a arquitetura mudar. O novo procedimento foi testado com duas conexões; falta validar quatro operando a antecâmara ao mesmo tempo e a sequência nova inteira com energia zero. Sem certificação Windows/Steam/internet, vídeo ou aprovação comercial de arte nesta entrega.

A falha histórica intermitente de inicialização nativa no Mac, registrada no relatório de infraestrutura, não foi tratada por esta alteração e continua aberta. Uma bateria que passa não comprova correção desse problema.
