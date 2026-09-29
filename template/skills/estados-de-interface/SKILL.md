---
name: estados-de-interface
description: >-
  Use quando criar ou alterar tela, página, componente de interface ou consulta que alimenta a
  tela; ao escrever spec de interface; e antes de abrir PR que mexa em frontend.
---

# Os quatro estados de toda interface

A maior parte do defeito visível de interface não está no caminho feliz. Está no que a tela faz
enquanto espera, quando não há dado, e quando algo falhou. Esses três costumam ser escritos
depois, sob pressão, e é por isso que ficam ruins.

## A regra

Toda spec de interface define os quatro estados de **cada tela e de cada consulta**, e não
apenas da página como um todo. Uma página com três consultas tem doze estados a definir.

| Estado | A pergunta que ele responde |
|---|---|
| **Carregando** | O que a pessoa vê enquanto espera, e a partir de quanto tempo |
| **Vazio** | O que aparece quando não há nada, e qual é a próxima ação sugerida |
| **Erro** | O que houve, o que a pessoa pode fazer, e como tentar de novo |
| **Sucesso** | O conteúdo, que é a parte que todo mundo já escreve |

PR de interface que não trate os quatro explicitamente não passa em revisão.

## Estado vazio não é estado de erro

Vazio é a situação normal de quem acabou de começar. É a primeira tela que muita gente vê, e ela
convida a agir: diz o que aparecerá ali e qual o caminho para criar o primeiro item. Uma tela
vazia que só diz "nenhum resultado" desperdiça o melhor momento de ensinar o sistema.

## Erro descreve e orienta

A mensagem diz o que aconteceu e o que fazer. Ela não se desculpa, não culpa a pessoa e não
mostra rastro de pilha. Quando a recuperação depende de alguém, diga de quem.

## Protótipo antes do código

Página nova exige protótipo validado por uma pessoa **antes** da implementação. O protótipo é o
artefato de aprovação de design, e revisar um protótipo custa minutos enquanto revisar uma
página implementada custa uma rodada inteira.

## Parâmetros deste projeto

Leia `docs/steering/frontend-ux.md` para o design system adotado, os tokens semânticos, o
diretório dos protótipos e a estrutura do frontend.

Se esse arquivo não existir, não invente um design system: pergunte qual usar. Componente novo
se constrói sobre o que já existe, e não reinventando token nem primitiva.

## Erros comuns

| Erro | O que acontece |
|---|---|
| Definir os estados só da página | Cada consulta falha sozinha e a tela fica em estado inconsistente |
| Carregando sem limite de tempo | A espera infinita é indistinguível de travamento |
| Vazio tratado como erro | A pessoa nova acha que quebrou |
| Erro mostrando exceção crua | Ninguém sabe o que fazer, e vaza detalhe interno |
