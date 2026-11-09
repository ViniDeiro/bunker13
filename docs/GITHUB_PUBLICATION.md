# Publicação do projeto — 09/11/2026

Destino autorizado: [ViniDeiro/bunker13](https://github.com/ViniDeiro/bunker13). O repositório estava vazio na consulta inicial. Publicação do snapshot atual na branch `main`, a partir da branch local `codex/github-publication`, sem force push ou reescrita de commits anteriores.

O snapshot reúne mudanças históricas interdependentes ainda sem commit: sala/planta aberta, ciclo de dias/coleta, infraestrutura, antecâmara, expedição 0.4.2 e preparação de arquitetura/radiação. Não foram inventados commits retrospectivos alegando que cada estágio histórico foi publicado/testado isoladamente. A base de radiação continua sem integração ao gameplay.

Incluídos: código, configuração, Content completo, fontes Blender/Painter, exports, texturas, scripts, testes, relatórios, três capturas reais selecionadas em `docs/media/` e evidências resumidas em `docs/validation/`. As fontes binárias atuais usam LFS. Caches, aplicativos compilados, autosaves, saves e logs brutos ficam fora do snapshot; 67 logs antes rastreados foram retirados somente do índice, com arquivos locais preservados. Os commits antigos continuam contendo seu conteúdo histórico, revisado por busca de padrões de credenciais; isso não equivale a auditoria completa de segredos/licenças.

Pré-publicação: backup Git bundle e índice preservados localmente, revisão do diff, `git lfs fsck`, auditoria de candidatos e testes isolados de radiação. Preparação não altera o executável 0.4.2 nem os checkpoints pessoais.

Recuperação deve ser verificada com clone remoto independente, LFS, comparação dos hashes dos assets, teste de regras e compilação do Editor. O resultado e o commit publicado serão registrados após a execução. Compilar não certifica partida Windows/Steam, multiplayer na internet ou lançamento.

Instruções para a equipe: [BUILD_AND_RECOVERY](BUILD_AND_RECOVERY.md). Arquitetura: [ARCHITECTURE](ARCHITECTURE.md). Estado funcional: [EXPEDITION_REPORT](EXPEDITION_REPORT.md).
