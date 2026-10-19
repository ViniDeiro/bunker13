# Mochila utilizável e necessidades — 19/10/2026

## Funcionalidade desta etapa

- I abre/fecha a mochila; setas selecionam; U usa o recurso; G larga; E recolhe do mundo; F levanta da cama.
- Mochila com espaços e peso, ambos validados no servidor. Parâmetros iniciais: 12 espaços e 20 kg.
- Água restaura hidratação, alimento restaura alimentação e kit médico restaura saúde. Pilhas e ferramentas permanecem recursos não consumíveis nesta etapa.
- Consumo exige uma instância válida na mochila do solicitante, remove uma unidade e aplica seu efeito no servidor. Repetir a solicitação do mesmo GUID não pode criar outro efeito.
- Descarte procura piso, verifica linha de visão e espaço, restaura a malha/material/escala e mantém o GUID. Os itens críticos não usam simulação de rigid-body.
- Saúde, alimentação, hidratação e energia replicam apenas ao dono. A HUD não revela inventário ou atributos dos colegas.
- Alimentação/hidratação/energia diminuem com o tempo; dormir recupera energia. Necessidades continuam passando durante a mochila. Energia baixa amplia o intervalo entre ações. Fome/sede zeradas podem reduzir saúde; incapacitação, morte, resgate e mochila de cadáver continuam pendentes em U3.

## Dados editáveis

`/Game/Bunker/Data/DA_SurvivalRules` contém pesos, efeitos, capacidade e taxas. A hidratação cai mais rápido que a alimentação. O instalador preserva valores existentes para permitir ajustes de balanceamento no editor, sem recompilar ou perder alterações ao regenerar o mapa.

As taxas são de protótipo e não foram balanceadas numa sessão de 60–120 minutos. Os seis recursos existentes do mapa receberam tipos explícitos; isso não equivale a completar o inventário de conteúdo do lançamento.

## Verificações

O teste de quatro processos foi estendido: consumo via teclas reais da Unreal; repetição do GUID; descarte; repetição do descarte; coleta do objeto restaurado; comparação do GUID final; verificação de privacidade. Também repete a coleta/cama/porta da etapa anterior.

A primeira execução no editor confirmou consumo e descarte/recolha com GUID preservado, mas reprovou a contagem de hidratação porque o anfitrião observador não havia recebido os atributos iniciais do cenário. O estado inicial de todos os participantes do cenário foi corrigido. A repetição no executável empacotado passou com quatro processos reais (`logs/survival_final_result.json`): consumo único, repetição sem duplicação, descarte/recolha preservando GUID, atributos privados e regressões de coleta/cama/porta. A compilação e o empacotamento terminaram com ExitCode 0 (`logs/survival_package.log`); a assinatura do aplicativo foi verificada.

A captura `screenshots/inventory.png`, produzida pelo próprio executável, foi inspecionada: painel, seleção, peso, necessidades e controles legíveis, sem recortes em 1280×720. Não houve teste humano prolongado nem medição de desempenho nesta etapa.

## Limites

Ainda faltam pilhas/empilhamento, contêineres, animações/sons de uso, descarte físico mais elaborado, salvamento, reconexão, tempo/dias, combustível, circuitos e condições de saúde/radiação. Não há persistência entre partidas; a integridade observada aqui é durante a sessão.

A interface é uma primeira versão funcional, não arte final. A inspeção visual usa um cenário temporário com três itens e necessidades reduzidas; não muda os recursos ou o mapa salvos.
