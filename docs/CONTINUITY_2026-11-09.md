# Continuidade — 09/11/2026

O trabalho desta etapa protege a continuidade do projeto: arquitetura auditada, fontes de arte incluídas na estratégia de versionamento e início isolado das regras do próximo marco. O executável permanece na expedição 0.4.2. Não foi publicada uma nova versão com radiação.

## Realizado

- GDD e parecer de 03/11 relidos. Correções de direção preservadas: salão aberto, exceções privadas/técnicas, garrafa azul e MVP interno em 30/01/2027.
- Arquitetura documentada com fontes de verdade, contratos de autoridade/IDs, dívidas de acoplamento e estratégia de evolução sem quebra geral de saves.
- Regras de radiação implementadas em C++ isolado: exposição, proteção com esgotamento durante o passo, sintomas persistentes no abrigo e tratamento. Ainda sem volumes, equipamento físico, HUD, consumo, save ou RPC ligados a esse modelo.
- 25 verificações com sanitizadores aprovadas; compilação do Editor aprovada; automação `C13.Unit.Radiation.Model` aprovada na Unreal. Diagnósticos anteriores ao início do teste continuam registrados e não foram declarados resolvidos.
- Git LFS 3.8.1 instalado e inicializado neste repositório, regras para Content e fontes de arte, exclusão de caches/backups/autosaves/dados pessoais e README atualizado.
- Inventário de arquivos, hashes dos assets e checagem do histórico gerados por `scripts/audit_repository.py`. Auditoria não faz commit/upload nem garante ausência de segredos/licenças em todo o histórico.

## Conferência no jogo existente

A retomada solo do checkpoint legado migrado passou novamente no aplicativo 0.4.2: fase/cronômetro, inventário e GUID original preservados. Isso é regressão de retomada, não teste de radiação ou novo percurso multiplayer. O hash do executável continua igual ao manifesto aprovado da expedição.

Uma tentativa inicial usou o ensaio cooperativo de expedição sobre os slots isolados deixados pelo último ensaio de migração **solo**. O validador rejeitou a incompatibilidade (Version 1 versus 2), bloqueando gravação; o processo foi interrompido. Foi então executado o cenário solo correto, aprovado. Os registros foram preservados em `logs/architecture_wrong_fixture_host.log` e `logs/architecture_round_regression.log`. Não foi relaxada a validação nem apagada uma campanha pessoal para produzir um resultado verde.

Nenhum benchmark novo: não atribuir os FPS anteriores a esta etapa. Nenhuma nova aprovação visual, vídeo ou playtest humano foi produzido. Checkpoints de teste são compartilhados entre alguns scripts antigos; a pré-condição do ensaio precisa ser respeitada. Isolar namespaces por suíte é dívida de ferramentas para evitar esse erro de preparação.

## Pendências concretas

**Radiação:** implementar equipamento físico próprio com condição por GUID, zonas editáveis, adaptador autoritativo, estado privado, tratamento com recurso, migração e regressões de reconexão. Executar o percurso na Unreal e testes multiplayer, registrar FPS/capturas. Os critérios estão em [RADIATION_ACCEPTANCE](RADIATION_ACCEPTANCE.md).

**GitHub:** definir destino; revisar os arquivos candidatos; retirar do índice somente os logs dispensáveis, preservando o disco; preparar os assets antigos para LFS; commits revisáveis; publicação e clone limpo com abertura/compilação. Nenhuma dessas etapas de publicação foi declarada feita. Ver [GITHUB_HANDOFF](GITHUB_HANDOFF.md).

**Arquitetura:** separar gradualmente estado de ensaio do controlador, HUD das regras e autoria do cenário da infraestrutura, sempre com migração/regressão. Não fazer tudo junto com radiação. Ver [ARCHITECTURE](ARCHITECTURE.md).

O restante do jogo continua com os marcos pendentes já registrados: inimigo/combate, morte/equipamento recuperável, comunicação limitada, eventos, minigame, encerramento, plataforma Windows/Steam e teste humano. Esta etapa não altera o escopo nem a meta em uma promessa de lançamento.
