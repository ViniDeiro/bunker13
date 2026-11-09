# Sala de referência - reprodução e limites

Base: projeto Unreal existente, relatório de 21/10/2026 e GDD. Este pacote trata somente da convivência e de um armário de referência. Aprovação visual humana continua necessária.

## Fontes e ordem

Os scripts Blender usam metros. Rodar com `/Applications/Blender.app/Contents/MacOS/Blender -b --python CAMINHO`:

1. `create_reference_room.py` - biblioteca e montagem inicial.
2. `create_reference_details.py` - TV, avisos, relógio e rádio.
3. `refine_reference_leaf.py` - folgas da folha e pivô de base da caneca.
4. `refine_reference_sofa.py` - apoio sob as almofadas.
5. `create_reference_native_props.py` - alvo e variantes visuais compatíveis com raízes legadas; UV físico adicional.
6. `clean_reference_geometry.py` - remover faces sem área.
7. `export_reference_shell.py` - cópia da malha-base retirando somente quatro volumes antigos da convivência.

Com Python normal: `create_reference_textures.py` gera a biblioteca original PBR e foley. Não sobrescreve projetos Painter.

Compilar o módulo Editor atualizado antes da instalação. Rodar `install_reference_room.py` pelo Python da Unreal. Ele integra meshes/materiais e chama os ajustes de raízes, iluminação e organização. A instalação preserva os nomes/posições dos atores nativos antigos e reutiliza o armário novo, sem criar unidades de recurso. A malha geral original permanece preservada; a versão derivada remove apenas Mesa_Cartas, Radio_Social, Estante_Social e Quadro_Avisos.

Após exportar `scene_placements.json`, rodar no Blender `assemble_reference_blend.py` e `validate_reference_art.py`. O arquivo editável final tem biblioteca e montagem separadas, mapas incorporados e câmeras. As luzes Blender são de prévia; a avaliação de iluminação de entrega é no executável Unreal.

## Execução e testes

Empacotar Mac Development com BuildCookRun (`-cook -build -stage -pak -iostore`). Nunca atualizar o pacote enquanto ele está executando. Preservar cópia do aplicativo anterior.

- `run_reference_validation.py --mode after`: enquadramentos reais e janela de FPS sem capturas.
- `run_reference_validation.py --mode network`: host e cliente renderizados, pedidos concorrentes, snapshots iguais, bloqueios, consumo e varredura de circulação.
- `run_reference_validation.py --mode video`: o mesmo cenário com screenshots nativos e saída de áudio do jogo. A cadência de captura não é o FPS.
- `run_reference_save_validation.py`: slot, porta, rejeição de slot duplicado e migração em processos novos.
- Regressões: `run_persistence_test.py`, `run_storage_network.py`, `run_reconnect_test.py`.
- `encode_reference_video.py`: preservar intervalos reais dos frames e validar áudio.
- `collect_reference_delivery.py` e `create_reference_report_pdf.py`: só publicar depois de todos os resultados requeridos passarem.

Os testes e a avaliação usam flags que desabilitam o salvamento de campanha normal. O lançador de avaliação move duas unidades existentes para a prateleira; o jogo normal não ganha recursos novos e o armário começa vazio.

## Dados que não podem ser alterados inadvertidamente

GUID do item; WorldKey dos atores antigos; enumeração de interações; formatos de save 1/2 e credenciais. O slot físico é uma identidade estável, nunca o índice de um array que compacta. Alterações da mochila continuam validadas pelo host. Snapshot visual não cria um recurso.

As variantes de rádio/alvo compensam a escala/posição visual dentro da malha, preservando a raiz antiga usada pelo checkpoint. Elas não concluem voz por rádio nem um minijogo de habilidade.
