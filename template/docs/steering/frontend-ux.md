# Frontend e UX

> **Escopo:** painel/SPA, design system e UX de todas as telas do produto.
> **Gatilho de leitura:** qualquer trabalho no frontend (páginas, componentes, estados, protótipos).
> **Última destilação:** {{DATA}}

## Design system

O frontend tem design system próprio, e todo componente novo se constrói **sobre ele** (não reinventar tokens ou primitivas).

<!-- preencher: design system deste projeto — paleta/tokens semânticos (papéis de cor fixos),
     tipografia, primitivas de componente e eventuais convenções de layout. Se houver um modo de
     inspeção sem autenticação para validar telas (ex.: `?demo=1`), documentar aqui. -->

## Os 4 estados obrigatórios

Toda spec de UI **deve** definir os 4 estados de cada tela/consulta: **loading**, **vazio**, **erro** e **sucesso**. Um PR de UI que não trate explicitamente os 4 estados **não passa em revisão**. Isso vale por tela e por consulta de dados individual, não só para a página como um todo.

## Protótipo antes de código

Página nova exige **protótipo HTML validado pelo humano antes** da implementação. O protótipo é o artefato de aprovação de design; só depois de aprovado se escreve o código do painel.

<!-- preencher: diretório onde ficam os protótipos HTML (ex.: `exploracao/`) e o fluxo de
     aprovação adotado. -->

## Estrutura

<!-- preencher: stack e estrutura do frontend deste projeto (framework/bundler, diretório do
     código, contêiner que o serve, portas e proxies). Referenciar a ADR que fixa a escolha do
     design system, se houver. Remover este steering inteiro se o projeto não tem frontend. -->
