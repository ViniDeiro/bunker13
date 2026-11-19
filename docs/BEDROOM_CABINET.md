# Quarto v002 — armário físico

## Escopo

Um armário funcional no mesmo quarto de referência. O mapa v001, o bunker principal e o executável de expedição anterior foram preservados. Não houve expansão para outros ambientes.

Fonte editável: `blender/Bedroom_StyleStudy_v002.blend`. Mapa: `/Game/Bunker/BedroomCabinet/Lvl_Bedroom_Study_Cabinet`. Exportações: `exports/bedroom_cabinet/`. Novo atalho: `tools/launchers/Ver-Quarto-Armario.command`.

## Comportamento

- E na porta ou estrutura abre/fecha, com movimento da folha e sons existentes de abertura/fechamento.
- Com o armário aberto, E no objeto o retira da prateleira e o transfere para a mochila.
- Para guardar, selecione o item na mochila, feche a mochila, olhe para um espaço vazio e pressione X.
- Não aparece modal de estoque. A interface da mochila continua disponível por I.
- O host valida alcance, visada, porta aberta, espaço/peso, ID e revisão da solicitação. A folha verifica o volume da cápsula dos jogadores antes de movimentar.
- As alterações são enviadas aos observadores próximos e elegíveis. As mãos e ações remotas reutilizam as apresentações existentes; não são animações corporais novas.

Este é um mapa de avaliação sem gravação da campanha: os dois recursos iniciais reaparecem ao iniciar outra sessão. O novo atalho depende da Unreal instalada; não é um pacote distribuível novo.

## Geometria e materiais

Corpo: 1,20 × 0,54 × 1,975 m, com cinco superfícies horizontais, laterais, fundo, cobertura e apoios. Porta separada, dobradiças visíveis e puxador; pivô local em (-57,6; 27; 0) cm compatível com a colisão e o mecanismo nativo. O armário foi afastado do pilar traseiro para não intersectá-lo. Doze endereços lógicos de armazenamento permanecem alinhados ao componente existente.

Corpo e folha somam 27 peças editáveis e 4.740 triângulos. A edição mantém os materiais próprios do quarto e dois canais UV. Foram removidos o armário decorativo e seus objetos incorporados das novas exportações de Furniture/Details. Água e alimento são meshes reais do inventário existente, desenhados em tempo de execução, e não duplicatas permanentes dentro do FBX. A garrafa do inventário mantém seu visual azul.

A iluminação do novo mapa inclui uma luz leve que aproxima a reflexão das luminárias nas paredes, porque o perfil do Mac desliga a iluminação global. É uma aproximação artística de luz indireta, sem alterar o perfil global do bunker. Os canais de luz dos itens agora acompanham o corpo do armário; o armário antigo continua usando seu próprio canal.

## Arquitetura e compatibilidade

Foi reutilizado `ABunkerReferenceCabinet`, sem criar um segundo sistema de inventário. A configuração `PersistentKey` conserva por padrão `C13_Reference_CommonCabinet_v1`, preservando o endereço do armário antigo. A nova instância usa `C13_Bedroom_Cabinet_v002`.

Os recursos iniciais são dados de autoria separados (`FBunkerCabinetSeed`). Só o servidor os converte para as entradas existentes durante BeginPlay; não há alteração no formato `FBunkerInventoryEntry` nem no esquema de salvamento. O carregamento de checkpoint continua substituindo o conteúdo do recipiente, inclusive quando vazio. A inicialização não é repetida ao abrir a porta.

A criação rejeita sementes sem ID/mesh, slots fora do intervalo e repetição de ID/slot dentro do mesmo armário. A transação também rejeita entradas sem mesh antes de alterar a propriedade do item, evitando desreferência nula. A nova instância exige sua chave e IDs próprios; a validação de autoria de vários armários em um mapa futuro ainda precisa ser ampliada antes dessa integração.

## Validação

Os resultados consolidados ficam em `docs/validation/bedroom_cabinet_2026-11-13.json`. O ensaio usa dois processos renderizados do Unreal Editor, com comandos E/X, RPCs de preparação e auditorias no host. As preparações posicionam os participantes: não equivalem a uma caminhada humana até o armário. A obstrução da porta usa a cápsula real do personagem.

As verificações cobrem abertura, duas retiradas e duas devoluções da mesma garrafa, solicitação repetida com revisão antiga, propriedade única, rejeição com a porta fechada, bloqueio da folha pelo jogador, ausência de modal e atualizações de conteúdo/porta nos dois processos. As capturas mostram as prateleiras antes/depois da transferência.

Os checkpoints de regressão usam apenas o prefixo de teste `C13_AutomatedCheckpoint` no mapa original: criação, recuperação, rejeição de slot duplicado, geração de dado legado e migração. Isso testa a compatibilidade do componente antigo; não certifica reconexão nem persistência da nova cena em campanha.

## Limites

Não é aprovação comercial do quarto inteiro. Permanecem pendentes: animação corporal completa ao deitar/levantar, refinamento das mãos, teste com quatro jogadores, reconexão da nova cena, sessão prolongada, integração aos circuitos do bunker, lobby/Steam e novo executável empacotado. O estilo e os sistemas não foram aplicados aos outros ambientes.

Os testes locais não representam latência ou perda de pacotes de uma conexão pela internet. O vídeo usa quadros reais capturados em baixa cadência e áudio do jogo; sua cadência não deve ser confundida com o FPS medido.


## Problemas encontrados nesta etapa

A importação inicial falhou ao construir o GUID e ao tentar preencher campos internos da entrada de inventário pela API Python. A correção usa a conversão documentada em [GuidLibrary, documentação oficial da Epic](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/GuidLibrary.html?application_version=5.6) e um tipo de dados próprio para a autoria das sementes, sem expor nem modificar o esquema antigo de inventário. As falhas ficaram nos logs de instalação anteriores.

A primeira execução com dois jogadores passou. Na rodada com captura de vídeo, a segunda instância caiu antes de entrar no mapa: asserção `RefCount.load(...) == 0` em `InheritedContext.cpp`, com pilha no módulo `DevHttp` da Unreal. Essa rodada foi reprovada como teste multiplayer. Os registros foram preservados em `logs/bedcab_recording_failure/`; o vídeo dessa execução demonstra somente as interações do host, com um único jogador conectado. Não é evidência de multiplayer.

A captura produziu 233 imagens ao longo de 34,64 s, solicitadas a 8 quadros/s. O áudio exportado continha somente 3,73 s e foi omitido para evitar sincronização falsa. Os sons de porta estão atribuídos ao componente e seu acionamento foi mantido, mas a gravação não valida a experiência sonora. A rodada de captura mediu 18,88 FPS no host, com frame p95 de 90,62 ms; o custo do registro de imagens no Mac é uma limitação real. A regressão multiplayer final é executada separadamente, sem essa captura contínua.


O HUD da prévia ainda mostra o atalho F5, embora o salvamento esteja desabilitado nessa sessão. É uma inconsistência de apresentação pendente; o launcher e este relatório explicitam que a cena não grava a campanha. O personagem remoto continua usando o manequim existente da Unreal, sem nova arte corporal.


## Resultado final de 13/11

Build do Editor aprovado, fonte Blender reaberta (193 meshes / 46.504 triângulos / dois UVs por peça / duas imagens incorporadas) e 14 verificações do ensaio final de dois jogadores aprovadas. As cinco regressões de salvamento/migração do mapa original passaram. A conferência de 449 assets anteriores passou e os hashes do mapa e da fonte do quarto v001 permaneceram iguais.

| Processo | Janela | Resolução interna | Limite | Média | Frame p95 |
|---|---|---|---|---|---|
| Host | 960 × 540 | 70% | 30 FPS | 27,05 FPS | 34,95 ms |
| Cliente | 800 × 450 | 70% | 30 FPS | 26,51 FPS | 36,76 ms |

Sombras e AO desligados. Janela curta de amostragem de aproximadamente 35 s do tempo do jogo, incluindo capturas pontuais e possíveis engasgos. Dois processos no mesmo Mac, sem captura contínua de vídeo nesta medição; não é benchmark de sessão longa, de quatro jogadores ou de pacote distribuído. O perfil do aplicativo principal não foi alterado.

Capturas finais: `screenshots/bedcab_host_02.png` (aberto com dois itens), `bedcab_host_05.png` (garrafa retirada), `bedcab_host_08.png` (devolvida), `bedcab_client_08.png` (mesmo conteúdo na visão remota) e pares de revisão final `bedcab_*_23.png`. Vídeo local: `output/Condominio13_Armario_Interacoes.mp4`, 34,64 s, sem áudio, demonstração do host com um jogador. A amostra foi decodificada para conferência visual e o contêiner verificado por ffprobe.

Os arquivos desta etapa permanecem locais; não houve push ao GitHub nem substituição do executável de expedição. Próximo marco no mesmo quarto: animações corporais e refinamento do contato das mãos, mantendo os testes de armazenamento como regressão.
