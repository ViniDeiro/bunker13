# Primeira expedição — parte 1: antecâmara

Dependências verificadas: mapa Lvl_CollectionRound existente, portas físicas com proteção contra esmagamento, infraestrutura 0.4.0, autoridade do host, checkpoint e reconexão. Sem expansão do mapa e sem alteração dos assets aprovados.

Aceite desta parte: após a coleta, fechar as duas folhas antes de abrir a porta de destino; aguardar equalização no relógio do servidor; rejeitar pedidos concorrentes incompatíveis; 5 s com serviços energizados, 12 s por procedimento manual sem energia, parametrizados no Data Asset. Perda de energia durante o ciclo reinicia o prazo manual. Fechar uma porta permanece permitido. A liberação externa de emergência continua disponível após equalizar, inclusive exausto. Nenhum dano ou eliminação automática.

Carregar um checkpoint preserva folhas/IDs/estoques e reinicia apenas a equalização transitória. Checkpoints antigos com duas folhas abertas permitem fechar as portas; o novo procedimento não altera posições nem renomeia atores. Nova versão de teste separada da infraestrutura já entregue.

Verificação: compilar, executar E no jogo com host/cliente, observar bloqueio e estados replicados, caminhar através das folhas, testar falta de energia, salvar/carregar, repetir regressões de coleta e circulação. Registrar capturas, FPS e falhas. Automação local não é teste humano ou internet.

A expedição completa ainda exige suprimentos externos finitos, migração aditiva segura desses recursos, coleta/retorno/uso com GUID preservado e validação cooperativa. Radiação, inimigo, combate e morte permanecem em marcos posteriores. Esta parte não deve ser chamada de expedição completa.
