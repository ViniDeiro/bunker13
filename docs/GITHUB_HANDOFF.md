# Compartilhar o projeto no GitHub

Preparação inicial em 09/11/2026, seguida de autorização para publicar em `https://github.com/ViniDeiro/bunker13.git`. O destino foi verificado vazio. A preparação de LFS e a retirada dos logs do índice preservam as cópias locais e não reescrevem commits antigos. O resultado do envio e da recuperação deve ser conferido no [registro de publicação](GITHUB_PUBLICATION.md).

## O que vai junto

- Código C++/C#, configuração Unreal, `.uproject`, scripts, testes, GDD e documentação.
- Content completo, incluindo mapas, ExternalActors e ExternalObjects; não selecionar só a pasta Bunker e perder dependências.
- Fontes `.blend` e `.spp`, exports e texturas: regras LFS em `.gitattributes`.
- Executáveis ficam como entregas separadas; caches, Intermediate, Saved, saves pessoais, credenciais, backups Blender e autosaves Painter não entram.
- Evidências precisam de seleção: guardar relatórios revisados; não publicar logs brutos de perfis/tickets. Os dados de auditoria local ficam em `logs/repository_audit.json`.

LFS foi instalado (3.8.1) e inicializado somente neste repositório. As regras foram criadas; isso não converte automaticamente assets antigos já presentes no índice/histórico. [Documentação oficial LFS](https://git-lfs.com/) e [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage).

## Auditoria local

Executar `python3 scripts/audit_repository.py`. A primeira execução encontrou 446 assets candidatos, aproximadamente 319 MB (304 MiB), com regras LFS. Havia 271 assets rastreados no índice como Git comum e 67 JSONs de logs já rastreados; a preparação posterior converteu os assets atuais e retirou somente os logs do índice. Novas regras de ignore sozinhas não fazem essa retirada. Nenhum blob alcançável acima de 100 MiB foi encontrado no histórico; isso não torna a revisão de privacidade/licença dispensável.

O script lê candidatos, calcula SHA-256 dos assets, verifica regras, arquivos grandes no histórico, existência de LFS e remotes. Procura algumas assinaturas de credenciais em textos candidatos sem imprimir valores; **não é auditoria completa de segredos, histórico ou licenças**. Ele não modifica índice/histórico nem publica. `ready_to_publish=false` é esperado até concluir os passos abaixo.

## Sequência para publicar

1. Definir URL/conta e visibilidade do repositório. Conferir se o destino já tem commits; não sobrescrever trabalho de ninguém. Confirmar autenticação e capacidade de armazenamento/tráfego LFS na conta.
2. Fechar/salvar Blender e Painter para estabilizar as fontes. Revisar assets e direitos de uso, além do diff de fontes/configuração e dos documentos de evidência escolhidos.
3. Revisar os 67 caminhos `ignored_but_tracked`. Remover **somente do índice** os logs dispensáveis, mantendo as cópias locais. Não apagar toda a pasta do disco e não usar uma limpeza geral de cache como substituto da revisão.
4. Adicionar `.gitattributes` e preparar a conversão dos assets atuais com `git add --renormalize` nos caminhos revisados, além de adicionar os assets novos. Isso cria ponteiros LFS no próximo commit sem reescrever commits antigos. Conferir `git lfs status`, `git lfs ls-files`, `git diff --cached --stat` e `git diff --cached --check` antes de confirmar.
5. Fazer commits revisáveis por responsabilidade: infraestrutura/antecâmara, expedição, preparação de arquitetura/LFS e base de radiação. O estado atual contém mudanças de várias entregas ainda sem commit; não afirmar que o histórico já representa essas etapas.
6. Rodar `git lfs fsck` e auditoria, configurar o remoto e publicar a branch de integração. Não usar push forçado. Migrar o histórico inteiro para LFS só se necessário e autorizado separadamente, porque muda hashes; não é obrigatório apenas por haver assets antigos pequenos.
7. Fazer clone limpo em outro diretório, obter LFS, conferir hashes/arquivos e compilar/abrir o projeto. Publicação aprovada só depois dessa recuperação; abrir aqui no Mac não prova que o clone está completo.
8. Distribuir o app testado como entrega separada com versão, hash e relatório, conforme os limites do serviço. Windows/Steam ainda não foram validados. Não empacotar nem redistribuir a instalação da Unreal.

## Para a equipe

Instalar Git + LFS, executar `git lfs install`, clonar e executar `git lfs pull`. Abrir `unreal/Condominio13/Condominio13.uproject` na versão compatível com a usada na produção (UE 5.8.3 neste Mac); regenerar arquivos de projeto e compilar. Engine/plugins/ferramentas são pré-requisitos, não conteúdo do repositório. Consultar os scripts antes de executar: os antigos ainda têm caminhos locais.

Combinar quem edita cada mapa/fonte binária para evitar duas versões incompatíveis. Não prometer merge textual de `.umap`, `.blend` ou `.spp`; locking LFS e fluxo de checkout da equipe ainda precisam ser combinados. Código e configuração devem passar por revisão e pelos testes do sistema afetado.
