# Condomínio 13 — Deiros Dev

Jogo cooperativo de sobrevivência em desenvolvimento na Unreal Engine 5. Especificação: [GDD](references/Condominio_13_GDD_Codex.md). A versão atual é uma fatia jogável; ainda não contém a partida completa nem está aprovada para lançamento.

## Executável local

`builds/Mac/Condominio13-VerticalSlice.app` — versão Mac de desenvolvimento. WASD move, mouse olha, E interage, F levanta da cama, I abre a mochila. Na mochila: setas selecionam, U usa e G larga. Em armários: TAB troca o lado e X transfere.

No modo solo e no host, F5 salva (Fn + F5 conforme a configuração do Mac), há gravação automática a cada minuto e no encerramento normal; a próxima execução retoma o checkpoint válido. A hospedagem também preserva os três participantes remotos, que retornam com seus perfis privados locais. Consulte [persistência solo](docs/PERSISTENCE_REPORT.md) e [checkpoint/reconexão cooperativa](docs/COOP_RECONNECT_REPORT.md). Lobby e identidade Steam continuam pendentes.

## Produção e evidências

- [Estado atual](docs/PRODUCTION_STATUS.md) e [pendências para lançamento](docs/REMAINING_FOR_RELEASE.md).
- [Meta de dezembro de 2026](docs/RELEASE_TARGET_DECEMBER.md), sem dia definido nem redução autorizada do GDD.
- [Inventário e sobrevivência](docs/SURVIVAL_INVENTORY_REPORT.md), [armários e garrafa azul](docs/STORAGE_REPORT.md), [mãos e uso de itens](docs/FIRST_PERSON_ITEM_REPORT.md).
- [Rede](docs/NETWORK_FOUNDATION_REPORT.md) e [portas/circulação](docs/DOORS_AND_INPUT_REPORT.md).

Quatro processos automatizados não substituem quatro pessoas jogando. O executável Mac não valida a plataforma Windows prevista no GDD. Binários, projetos Blender/Painter e exportações ficam localmente fora do Git; precisam de armazenamento de assets apropriado antes de compartilhar a produção.

## Fontes do bunker

- Mestre inicial: `blender/Bunker_Blockout_v001.blend`.
- Geração: `scripts/create_bunker_blockout.py`; validação: `scripts/validate_bunker.py`.
- [Navegação do blockout](docs/NAVIGATION.md), [relatório B1](docs/BLOCKOUT_REPORT.md) e [auditoria inicial](docs/ENVIRONMENT_REPORT.md).
- Projeto jogável: `unreal/Condominio13/Condominio13.uproject`.
