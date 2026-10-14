# Condomínio 13 — Bunker B1 Unreal Playtest

## Entrega

- Engine: Unreal Engine 5.8.3
- Plataforma: macOS 14 ou superior, Apple Silicon arm64
- Aplicativo: `builds/Mac/Condominio13-B1-Playtest.app`
- Aplicativo otimizado para MacBook: `builds/Mac/Condominio13-B1-Playtest-Lite.app`
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

## Perfil MacBook Lite

- Resolução inicial: 1280 × 720 em janela.
- Limite de 45 FPS com VSync.
- Resolução interna em 70%.
- Sombras virtuais, motion blur, bloom, oclusão de ambiente, profundidade de campo, reflexos em tela e névoa volumétrica desativados.
- Distância de visão em 65%, materiais no nível baixo e pool de texturas limitado a 512 MB.
- Perfil aplicado pelo `Mac DeviceProfile`, inclusive quando há preferências antigas salvas em qualidade Épica.
- Sensibilidade horizontal e vertical reduzida para 0,35 na escala final do controlador; suavização do mouse desativada.
- Aplicativo Lite recompilado, assinado e iniciado com sucesso; o mapa B1 carregou em 0,04 s no teste local, sem erro fatal ou `ensure`.

## Controles

- `W A S D`: caminhar
- Mouse: olhar
- `Espaço`: pular
- `Esc` ou `⌘Q`: sair

## Limites desta etapa

Esta é a versão navegável B1. Interações, inventário, esconder recursos, sistemas de descanso e trabalho, multiplayer para quatro jogadores, áudio final, acabamento visual B2 e mundo externo ainda não foram implementados. Esses itens dependem da aprovação do blockout navegável.
