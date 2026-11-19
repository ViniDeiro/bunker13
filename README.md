# Condomínio 13 — Deiros Dev

Jogo cooperativo de sobrevivência em desenvolvimento na Unreal Engine 5. Especificação: [GDD](references/Condominio_13_GDD_Codex.md). A versão atual é uma fatia jogável; ainda não contém a partida completa nem está aprovada para lançamento.

## Recuperar o projeto

Repositório: [ViniDeiro/bunker13](https://github.com/ViniDeiro/bunker13). Instalar Git LFS, clonar e executar `git lfs pull`. Código, Content, fontes Blender/Painter e exports pertencem ao projeto; aplicativos compilados e saves pessoais são distribuídos separadamente. Consulte [compilação e recuperação](docs/BUILD_AND_RECOVERY.md).

## Executável local

Abrir `builds/Mac/Jogar-Expedicao.command` — versão Mac de desenvolvimento 0.4.2. O atalho seleciona o mapa e o modo corretos; abrir o `.app` diretamente ainda usa o mapa padrão legado. WASD move, mouse olha, E interage, F levanta da cama, I abre a mochila. Na mochila: setas selecionam, U usa e G larga. R inicia a coleta no host. Para rede local, usar `Hospedar-Expedicao.command` e `Entrar-Expedicao.command`.

No modo solo e no host, F5 salva (Fn + F5 conforme a configuração do Mac), há gravação automática a cada minuto e no encerramento normal; a próxima execução retoma o checkpoint válido. A hospedagem também preserva os três participantes remotos, que retornam com seus perfis privados locais. Consulte [persistência solo](docs/PERSISTENCE_REPORT.md) e [checkpoint/reconexão cooperativa](docs/COOP_RECONNECT_REPORT.md). Lobby e identidade Steam continuam pendentes.

## Produção e evidências

- [Quarto industrial estilizado: estudo separado, capturas e limites](docs/BEDROOM_STYLE_STUDY.md).

- [CRACK como referência de experiência, sem substituir o GDD](docs/REFERENCE_CRACK.md).

- [Estado atual](docs/PRODUCTION_STATUS.md) e [pendências para lançamento](docs/REMAINING_FOR_RELEASE.md).
- [Meta vigente: MVP interno em 30/01/2027](docs/MVP_TARGET_JANUARY_2027.md); documentos de dezembro são históricos, sem promessa de lançamento comercial.
- [Primeira expedição 0.4.2](docs/EXPEDITION_REPORT.md), [infraestrutura](docs/INFRASTRUCTURE_REPORT.md) e [antecâmara](docs/AIRLOCK_REPORT.md).
- [Arquitetura auditada](docs/ARCHITECTURE.md), [próximo marco de radiação](docs/RADIATION_ACCEPTANCE.md) e [preparação para GitHub](docs/GITHUB_HANDOFF.md).
- [Inventário e sobrevivência](docs/SURVIVAL_INVENTORY_REPORT.md), [armários e garrafa azul](docs/STORAGE_REPORT.md), [mãos e uso de itens](docs/FIRST_PERSON_ITEM_REPORT.md).
- [Rede](docs/NETWORK_FOUNDATION_REPORT.md) e [portas/circulação](docs/DOORS_AND_INPUT_REPORT.md).

Quatro processos automatizados não substituem quatro pessoas jogando. O executável Mac não valida a plataforma Windows prevista no GDD. Fontes Blender/Painter, exports e Content usam Git LFS. Binários e caches ficam fora do repositório. A radiação funciona no projeto na Unreal; o executável independente continua na expedição 0.4.2.

## Fontes do bunker

- Mestre inicial: `blender/Bunker_Blockout_v001.blend`.
- Geração: `scripts/create_bunker_blockout.py`; validação: `scripts/validate_bunker.py`.
- [Navegação do blockout](docs/NAVIGATION.md), [relatório B1](docs/BLOCKOUT_REPORT.md) e [auditoria inicial](docs/ENVIRONMENT_REPORT.md).
- Projeto jogável: `unreal/Condominio13/Condominio13.uproject`.


O quarto v002 adiciona armário físico com itens reais, porta móvel e armazenamento compartilhado. Veja [escopo e controles](docs/BEDROOM_CABINET.md) e `tools/launchers/Ver-Quarto-Armario.command`. É uma cena de avaliação na Unreal instalada, sem gravação da campanha e sem novo executável empacotado.


O [quarto v003](docs/BEDROOM_REST_ANIMATION.md) adiciona a primeira animação corporal replicada de descanso. Prévia: `tools/launchers/Ver-Quarto-Animacoes.command`. Validação final com host renderizado e cliente sem janela; ainda não é aprovação comercial nem novo pacote distribuível.


Refinamento de 16/11: fases de contato ao pegar/guardar, iluminação das mãos no alcance e redução de avaliações redundantes no descanso. [Resultados e limitações](docs/BEDROOM_INTERACTION_POLISH_2026-11-16.md). As prévias existentes do quarto usam essas alterações; ainda não fazem parte do executável distribuído.


Continuação do quarto: item permanece na prateleira durante aproximação, com posição/rotação coerentes, e host valida proximidade. [Validação de continuidade e salvamento](docs/BEDROOM_REACH_CONTINUITY_2026-11-16.md): 23 critérios de interação e cinco regressões de checkpoint. Ainda utiliza luvas provisórias e a prévia na Unreal instalada.

Para testar a partida atual na Unreal ou jogar a 0.4.2 sem Editor, veja o [roteiro do primeiro playtest](docs/PLAYTEST_GAMEPLAY.md).

Menu 3D cinematográfico isolado: [escopo, testes e limitações](docs/CINEMATIC_MAIN_MENU.md). Prévia pela Unreal instalada em `tools/launchers/Ver-Menu-Cinematico.command`. A referência não é usada como fundo 2D.
