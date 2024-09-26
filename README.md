# Sistema de Restaurante

## Problema

No evento "2ª Festa Italiana", em Ribeirão Pires, estavam preparados para fazer a gestão de pedidos via comandas em papel.  
Como modernização, pensavam em colocar telas de controle nas áreas relevantes: pedido, cobrança, preparação e entrega.

## Solução

Criei um servidor via `streamlit`, que possua uma "página" para cada tela, com suas devidas funções, na forma de:

1. Ler
2. Exibir
3. Receber interação
4. Salvar
5. Reiniciar

Utilizei de um arquivo geral para o controle do fluxo (escolher página), e um para funções comuns e constantes.

### Banco de dados

Para o armazenamento de dados, utilizei arquivos _Excel_ (`.xlsx`), com um arquivo por tabela (devido a limitações do `polars`).  
Na modelagem, escolhi uma simples para pedidos:

- Itens possíveis: `cardápio.xlsx`
- Pedidos feitos: `pedidos.xlsx`
  - Armazena o momento do pedido.
  - Armazena as informações de pagamento junto, como as formas de pagamento.
  - Armazena o estado com colunas booleanas, pois operar com estados (`a cobrar`, `a montar`, `a entregar`, `concluído`) não era necessário para a complexidade do projeto.
- Relação de itens por pedido: `itens.xlsx`
  - Contém quantia, cópia verdadeira do preço por item (oriundo do cardápio), e subtotal.
    Assim, mesmo se o preço mudasse durante o evento, isso seria rastreável.

### Fluxo de dados

Os pedidos são criados na página de `pedido`, cobrados na página de `cobranca`, marcados como preparados na página de `preparacao` e entregues na página de `entrega`.

A página de `cobranca` não exibe informações dos itens do pedido, pois não há necessidade disso para cobrar.

## Limitações

O fluxo de dados é unidirecional, não permitindo um pedido voltar em uma página, ou sequer ser cancelado.
