# Compilar e recuperar o projeto

O repositório contém fontes e assets, não o aplicativo compilado nem a instalação da Unreal. A base foi compilada neste Mac com Unreal 5.8.3, Xcode e ferramenta Metal compatíveis; fontes Blender foram geradas com Blender 5.2.2. Windows continua sem certificação.

## Clone com todos os assets

```sh
git lfs install
git clone https://github.com/ViniDeiro/bunker13.git
cd bunker13
git lfs pull
git lfs fsck
python3 scripts/verify_asset_manifest.py
python3 scripts/test_radiation_model.py
```

Instalar Unreal/Xcode/Metal e aceitar os termos dos respectivos fornecedores. Não copiar a instalação de engine para dentro do projeto. Para compilar no Mac, fornecer o diretório instalado, por exemplo:

```sh
python3 scripts/unreal_project.py build-editor --engine '/Users/Shared/Epic Games/UE_5.8'
python3 scripts/unreal_project.py edit-expedition --engine '/Users/Shared/Epic Games/UE_5.8'
```

O diretório é um argumento, não um caminho obrigatório da máquina do autor. Se o ambiente exigir `DEVELOPER_DIR` ou `TOOLCHAINS`, configurar os valores correspondentes à instalação local antes do comando. A entrada `edit-expedition` abre o mapa correto no Editor; não inicia automaticamente uma partida nem cria campanha de teste. Iniciar Play no Editor é uma verificação separada, não substituída pela compilação.

O manifesto confere 449 assets da publicação inicial, incluindo fontes editáveis, imports e três capturas. Ao alterar esses assets no desenvolvimento, atualizar o manifesto em um novo marco revisado; não esperar que as versões modificadas mantenham os hashes de 09/11.

Após compilar, também é possível verificar o carregamento sem renderização/partida pelo executável `Engine/Binaries/Mac/UnrealEditor-Cmd`, passando o caminho do `.uproject`, `-run=pythonscript`, `-script=` com o caminho absoluto de `scripts/verify_unreal_recovery.py`, e `-unattended -nullrhi -nosound`. O marcador esperado é `C13_REMOTE_RECOVERY`; isso carrega o mapa/dependências, não valida animações, multiplayer ou FPS.

Projeto: `unreal/Condominio13/Condominio13.uproject`. Mapa da expedição: `/Game/Bunker/Lvl_CollectionRound`. Flags usadas no modo existente: `-C13Round -C13Expedition`. O mapa padrão legado continua configurado; não confundir abrir o Editor ou um app sem flags com testar a expedição.

Os atalhos `.command` que ficam em `builds/Mac/` pertencem ao pacote local distribuído separadamente. O clone não contém esse pacote, portanto os scripts de teste de aplicativo exigem primeiro empacotamento e o caminho da versão correta. Scripts antigos de geração/teste ainda contêm caminhos locais e pré-condições de saves isolados; revisar antes de executar. Não rodar a bateria de integração sobre campanhas pessoais.

## Fontes de arte

Blender: `blender/`; Painter: `painter/`; exports: `exports/`; assets importados: `unreal/Condominio13/Content/`. Não executar novamente todos os scripts de geração como etapa obrigatória de clone: os assets importados já estão incluídos e scripts históricos podem gerar outra versão. Salvar a edição de arte, exportar seletivamente e reimportar com os mesmos caminhos/chaves.

Nenhum save pessoal ou ticket de reconexão faz parte da distribuição. Campanhas locais precisam de backup separado. O projeto não tem licença open-source concedida por esta publicação; não inferir direitos de redistribuição pelo acesso ao repositório. Templates e dependências da Unreal seguem os termos dos respectivos titulares.
