# Portas funcionais e controles — 19/10/2026

## Alteração jogável

Treze folhas que estavam fundidas na arquitetura foram substituídas por atores de porta com dobradiça, movimento gradual, colisão e estado controlados pelo servidor. Os batentes e três portas lacradas permanecem na arquitetura. As portas começam abertas para preservar a circulação inicial; E alterna abertura e fechamento.

O modelo e os materiais da porta do kit Painter foram aproveitados. As versões estreitas usam ajuste de escala e ainda precisam de refinamento próprio de ferragens; isso não representa aprovação final da arte.

O servidor verifica o alcance e a linha de visão antes de aceitar a interação. Há intervalo entre comandos concorrentes. O arco completo é consultado contra cápsulas de jogadores antes de iniciar e o próximo trecho é verificado durante o movimento. A geometria física da folha é separada do volume visual da roda de fechamento.

## Circulação real

A primeira auditoria encontrou 8/13 travessias livres. Os bloqueios vieram do acabamento: painéis sobre o acesso externo da antecâmara, suportes em frente ao dormitório e à despensa, carrinho médico avançado sobre a entrada e piso decorativo elevado no gerador.

Esses elementos foram reposicionados ou ajustados; suas colisões não foram desativadas para obter aprovação. A repetição no editor passou em 13/13 usando a cápsula real de raio 34 cm e meia altura 96 cm. O ensaio varre a cápsula através do centro de cada passagem aberta; não comprova todas as rotas da partida nem passagem simultânea de quatro jogadores.

## Entrada e rede

O teste ampliado envia E/F pelo sistema de entrada da Unreal e observa os callbacks reais. Assim cobre o vínculo das teclas, seleção local de alvo, RPC do proprietário e decisão do servidor. A solicitação propositalmente distante continua usando o RPC diretamente para verificar a rejeição.

Sequência: quatro conexões; disputa por coleta e cama; F libera a cama; cliente remoto abre a porta; consulta física confirma passagem aberta; cliente fecha; consulta física confirma barreira fechada. As quatro instâncias precisam confirmar os estados replicados. O cenário isolado de testes recebeu piso para que o personagem não caísse após levantar; esse piso não pertence ao mapa de produção.

Evidências finais:

| Verificação no executável Mac | Resultado |
|---|---|
| `logs/doors_final_v2_result.json` | PASS: 4 processos reais; E coletando/ocupando cama; F liberando; clientes abrindo/fechando; estados confirmados nas quatro instâncias |
| `logs/door_capsule_packaged_result.json` | PASS: 13/13 travessias livres; raio 34 cm, meia altura 96 cm; recusa de movimento com personagem no arco |
| `logs/doors_package.log` | Compilação/cook/stage concluídos com ExitCode 0 |
| Aplicativo copiado do stage completo | Integridade verificada com codesign; não é build Windows |

O cenário de testes inicialmente sobrepunha as cápsulas dos jogadores; a saída foi corretamente recusada por falta de espaço. As posições foram separadas e a repetição validou a saída livre. Resultados intermediários `doors_editor_result.json` e `doors_final_result.json` ficam preservados como execuções reprovadas, sem substituir a aprovação final.

Capturas produzidas pelo executável e copiadas para o projeto:

- `screenshots/door_open.png`: antecâmara com porta aberta a 90°.
- `screenshots/door_ajar.png`: porta em movimento, a 17,5°. A primeira solicitação tinha nome de arquivo `door_closed`, mas a porta já estava abrindo no instante da captura; por isso não é apresentada como fechamento completo. O fechamento a 0° com colisão foi confirmado no teste de rede, não nessa imagem.

O aplicativo Mac usa sandbox do sistema e grava capturas em sua própria pasta Saved/Screenshots. O coletor `scripts/collect_door_audit.py` registra no projeto o JSON emitido pelo teste no log, sem alterar as proteções do aplicativo.

## Fontes e reprodução

- `scripts/export_unreal_playtest.py`: exclui apenas folhas móveis do derivado FBX e registra dobradiças/dimensões em `logs/doors_layout.json`.
- `scripts/install_network_doors.py`: preserva materiais e mapa, instala os atores e corrige obstáculos; pode ser repetido.
- `scripts/setup_unreal_playtest.py`: inclui as correções para futuras regenerações.
- `scripts/run_network_smoke.py --remote-only --tag doors_final`: ensaio de rede ampliado.
- Executável com `-C13DoorAudit -C13ArtifactRoot=/Users/vini_deiro/bankers -nullrhi`: auditoria das passagens e proteção do arco.
- Executável com `-C13DoorVisual -C13ArtifactRoot=/Users/vini_deiro/bankers`: solicita capturas reais da antecâmara em dois instantes e registra o ângulo observado; encerra a instância após a captura. Essas opções de inspeção funcionam apenas em builds de desenvolvimento e não modificam o mapa salvo.

## Pendências

Ainda faltam sessão de 30–60 minutos com quatro humanos, teste manual contínuo de mouse/sensibilidade, latência/perda, reconexão e desconexão enquanto uma cama está ocupada. Não houve medição gráfica de desempenho nesta etapa. Inventário persistente, consumo/sobrevivência, expedições e restante do GDD continuam pendentes.
