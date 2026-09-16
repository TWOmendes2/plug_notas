# Segurança e resposta à exposição

O histórico contém uma credencial embutida. Seu valor não é reproduzido aqui.
Commits com atribuição literal de TOKEN: ef73051d738e, 37abb2a6b780, b5eb3f335a1e, 6511e45efd28.

## Ação necessária do responsável

1. Revogue a credencial exposta no painel autenticado do PlugNotas e emita outra.
2. Atualize o segredo no ambiente de execução; nunca em commits, issues ou logs.
3. Consulte os registros de uso e confirme que a credencial anterior foi invalidada.
4. Restrinja o acesso ao CSV real. O exemplo versionado contém apenas dados sintéticos inválidos para emissão.

A rotação não foi executada: esta revisão não tem uma sessão administrativa do provedor.
Excluir a chave do código não a remove de commits, forks ou caches. Após revogação,
combine uma limpeza direcionada do histórico com os colaboradores (git-filter-repo),
renovação dos clones e solicitação de remoção de caches ao GitHub quando cabível.
Essa reescrita destrutiva não faz parte deste PR; o histórico está preservado.

Não registrar payloads, documentos, respostas integrais nem exceções de transporte.
O programa não segue redirecionamentos com a chave e só usa o sandbox fixo.
Não há retries automáticos: em falha parcial ou timeout, reconcilie no painel antes
de reenviar, para evitar duplicidade. Não há garantia de atomicidade entre NFe/NFS-e.
