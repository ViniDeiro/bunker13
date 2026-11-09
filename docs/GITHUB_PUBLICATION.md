# Publicação do projeto — 09/11/2026

Destino autorizado: [ViniDeiro/bunker13](https://github.com/ViniDeiro/bunker13). O repositório estava vazio na consulta inicial. Publicação do snapshot atual na branch `main`, a partir da branch local `codex/github-publication`, sem force push ou reescrita de commits anteriores.

O snapshot reúne mudanças históricas interdependentes ainda sem commit: sala/planta aberta, ciclo de dias/coleta, infraestrutura, antecâmara, expedição 0.4.2 e preparação de arquitetura/radiação. Não foram inventados commits retrospectivos alegando que cada estágio histórico foi publicado/testado isoladamente. A base de radiação continua sem integração ao gameplay.

Incluídos: código, configuração, Content completo, fontes Blender/Painter, exports, texturas, scripts, testes, relatórios, três capturas reais selecionadas em `docs/media/` e evidências resumidas em `docs/validation/`. As fontes binárias atuais usam LFS. Caches, aplicativos compilados, autosaves, saves e logs brutos ficam fora do snapshot; 67 logs antes rastreados foram retirados somente do índice, com arquivos locais preservados. Os commits antigos continuam contendo seu conteúdo histórico, revisado por busca de padrões de credenciais; isso não equivale a auditoria completa de segredos/licenças.

Pré-publicação: backup Git bundle e índice preservados localmente, revisão do diff, `git lfs fsck`, auditoria de candidatos e testes isolados de radiação. Preparação não altera o executável 0.4.2 nem os checkpoints pessoais.

## Recuperação executada

Clone independente baixado do GitHub e atualizado até `eabcb50` (código compilado em `fa5a448`; depois dele só a configuração de escalabilidade mudou). LFS inicializado no novo clone e objetos baixados explicitamente; ponteiros sem `git lfs pull` não são assets recuperados.

- Git LFS fsck aprovado e **449 assets conferidos por tamanho/SHA-256**.
- 25 verificações de regras de radiação aprovadas no clone.
- Editor Unreal compilado a partir das fontes recuperadas; 29 ações de build, aproximadamente 108 s.
- Mapa `/Game/Bunker/Lvl_CollectionRound` carregado com **502 atores** e cinco dependências explícitas verificadas.
- Commandlet terminou com **0 erros e 0 avisos** depois da correção da configuração. Nenhum mundo/campanha foi salvo.
- Árvore do clone limpa após as verificações. Evidência resumida: [github_recovery_2026-11-09.json](validation/github_recovery_2026-11-09.json).

O teste encontrou configuração de renderer indevidamente repetida em Scalability (métodos de AA/GI/reflexão, já definidos com os mesmos valores em DefaultEngine) e o nome antigo da variável de iluminação translúcida. Foram removidas as entradas ignoradas e atualizado o nome da variável, preservando valor 16. Os dois ensaios que terminaram com erro foram preservados localmente; não foram tratados como aprovação porque o mapa abriu. A repetição após corrigir passou com saída 0.

O clone e o projeto original usam o mesmo Mac e a mesma instalação da engine. A verificação de mapa foi sem renderização, sem entrar em partida e sem benchmark. Isso valida a recuperação das fontes/assets e a compilação, não Windows/Steam, multiplayer na internet, arte comercial ou lançamento. O pacote jogável 0.4.2 não foi recompilado/distribuído nesta publicação.

Instruções para a equipe: [BUILD_AND_RECOVERY](BUILD_AND_RECOVERY.md). Arquitetura: [ARCHITECTURE](ARCHITECTURE.md). Estado funcional: [EXPEDITION_REPORT](EXPEDITION_REPORT.md).
