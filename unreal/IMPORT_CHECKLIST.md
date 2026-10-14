# Gate pendente — Unreal Engine 5

Nenhuma versão da Unreal foi escolhida ou executada neste ambiente. Estes são procedimentos de validação futura, não resultados.

1. Definir versão estável com o responsável e criar mapa de teste vazio.
2. Importar Scale_1m.fbx, escala 1, e comparar com cubo UE de 100 cm.
3. Importar Bunker_Blockout_v001.fbx sem combinar meshes, reconhecendo UCX por mesh. Conferir orientação, posições e nomes. GLB é alternativa visual de intercâmbio, não carrega contrato de colisão UE.
4. Verificar colisão de pisos, tetos e degraus e configurar conforme pipeline escolhido. As UCX incluídas correspondem às paredes, portas, móveis, pisos, tetos e escadas; conferir o reconhecimento e a separação por mesh na engine. Não ativar Nanite indiscriminadamente.
5. Conferir pivôs de módulos e relação das folhas de porta com HINGE. A hierarquia GLB preserva os pivôs; pipeline FBX de static meshes deve ser testado antes de usar portas interativas.
6. Testar cápsula de 60 cm de diâmetro, 175 cm de altura, eye height 165 cm. Portas internas de 110 cm são passagem individual; corredores permitem passagem em dois sentidos. Não prometer passagem simultânea de quatro lado a lado nas portas.
7. Executar quatro instâncias apenas no marco U1 autorizado. B1 contém quatro referências espaciais, sem rede.
8. Medir tempo entrada–convivência e latência/perda de pacotes no marco correspondente. Voz e oclusão acústica ainda não existem.

B2 exige aprovação do usuário; este projeto não contém mundo externo nem sistemas de gameplay.
