# Condomínio 13 — Bunker B1 Unreal Playtest

## Entrega

- Engine: Unreal Engine 5.8.3
- Plataforma: macOS 14 ou superior, Apple Silicon arm64
- Aplicativo: `builds/Mac/Condominio13-B1-Playtest.app`
- Configuração: Development, assinada localmente
- Tamanho: aproximadamente 854 MB
- Mapa inicial: `/Game/Bunker/Lvl_Bunker`

## Conteúdo validado

- Malha arquitetônica real importada do blockout B1, com colisão complexa.
- Dimensões gerais: 28,8 m × 30,3 m × 7,88 m.
- Um único ator de bunker e um único `PlayerStart` no mapa.
- 14 luzes pontuais, uma luz ambiente e oito materiais de blockout editáveis.
- Materiais com cores próprias para concreto, portas, piso, mobiliário, área médica, área social, aço e ambientes técnicos.
- Contraste quente/frio preservado para distinguir áreas sociais e técnicas.
- Movimento em primeira pessoa validado no aplicativo empacotado.
- Assinatura, binário arm64 e contêineres `.pak`, `.ucas` e `.utoc` verificados.

## Controles

- `W A S D`: caminhar
- Mouse: olhar
- `Espaço`: pular
- `Esc` ou `⌘Q`: sair

## Limites desta etapa

Esta é a versão navegável B1. Interações, inventário, esconder recursos, sistemas de descanso e trabalho, multiplayer para quatro jogadores, áudio final, acabamento visual B2 e mundo externo ainda não foram implementados. Esses itens dependem da aprovação do blockout navegável.
