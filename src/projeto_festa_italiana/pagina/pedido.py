# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING
from datetime import datetime

import streamlit as st
import polars as pl

from streamlit import session_state as ss
from streamlit.column_config import NumberColumn, TextColumn

if TYPE_CHECKING:
    from polars._typing import SchemaDict

    from ..base import (
        TITULO,
        SCHEMA_PEDIDO,
        SCHEMA_PEDIDOS_ITENS,
        FMT_DINHEIRO,
        ler_cardapio,
        ler_pedidos,
        ler_itens,
        salvar_pedidos,
        salvar_itens,
        concluir,
    )
else:
    from base import (
        TITULO,
        SCHEMA_PEDIDO,
        SCHEMA_PEDIDOS_ITENS,
        FMT_DINHEIRO,
        ler_cardapio,
        ler_pedidos,
        ler_itens,
        salvar_pedidos,
        salvar_itens,
        concluir,
    )


def salvar_pedido(pedido: pl.DataFrame) -> int:
    # Ler tabelas
    pedidos = ler_pedidos()
    itens = ler_itens()

    # Anexar pedido às tabelas
    id_pedido: int = int(pedidos["ID"].max() or 0) + 1  # type: ignore
    pedidos = pedidos.vstack(
        pl.DataFrame(
            {
                "ID": [id_pedido],
                "Momento": [None],
                "Preço": [pedido["sub_total"].sum()],
                "Dinheiro": [0.0],
                "PIX": [0.0],
                "Cartão Débito": [0.0],
                "Cartão Crédito": [0.0],
                "Outra forma": [0.0],
                "Pago": [False],
                "Preparado": [False],
                "Entregue": [False],
            },
            schema=SCHEMA_PEDIDO,
        ).with_columns(Momento=datetime.now())
    )

    id_pedido_item: int = int(itens["ID"].max() or 0) + 1  # type: ignore
    schema: SchemaDict = SCHEMA_PEDIDOS_ITENS
    _pedido = (
        pedido.select(
            pl.lit(id_pedido).alias("ID Pedido"),
            pl.col("ID").alias("ID Cardápio"),
            pl.col("qtd").alias("Quantidade"),
            pl.col("Preço").alias("Preço"),
        )
        .with_row_index("ID", id_pedido_item)
        .cast(schema)  # type: ignore
    )
    itens = itens.vstack(_pedido)

    # Salvar pedido
    pedidos.pipe(salvar_pedidos)
    itens.pipe(salvar_itens)

    return id_pedido


@st.fragment
def __main__():
    """
    Pagina de realizar o pedido.

    - Mostra o cardapio em uma tabela editável
    - Mostra um resumo dos itens com quantidade maior que zero
    - Mostra o total do pedido
    - Salva o pedido no arquivo `Controle.ods`
    """
    st.title(f"{TITULO} - Pedido")
    ct = st.container(border=False)

    cardapio = ler_cardapio().with_columns(qtd=pl.lit(0))

    selecionados: pl.DataFrame = ct.data_editor(
        data=cardapio,
        height=(cardapio.height + 1) * 35 + 3,
        use_container_width=True,
        hide_index=True,
        column_order=["qtd", "Categoria", "Tipo", "Item", "Preço"],
        column_config={
            "ID": NumberColumn("ID", width="small"),
            "qtd": NumberColumn(
                "Quantidade", min_value=0, default=0, width="small"
            ),
            "Categoria": TextColumn(
                "Categoria", disabled=True, width="small"
            ),
            "Tipo": TextColumn("Tipo", disabled=True, width="small"),
            "Item": TextColumn("Item", disabled=True, width="small"),
            "Preço": NumberColumn(
                "Preço",
                disabled=True,
                **FMT_DINHEIRO,  # type: ignore
            ),
        },
        key="pedido_cardapio_%d" % int(ss["pedido_num"]),
    )

    selecionados = selecionados.filter(pl.col("qtd") > 0)
    if selecionados.height == 0:
        return

    ct.markdown("---")
    ct.markdown("## Resumo")

    selecionados = selecionados.with_columns(
        sub_total=(pl.col("qtd") * pl.col("Preço")),
    )
    ct.dataframe(
        data=selecionados,
        height=(selecionados.height + 1) * 35 + 3,
        use_container_width=True,
        hide_index=True,
        column_order=[
            "qtd",
            "Categoria",
            "Tipo",
            "Item",
            "Preço",
            "sub_total",
        ],
        column_config={
            "qtd": NumberColumn("Quantidade", width="small"),
            "Categoria": TextColumn("Categoria", width="small"),
            "Tipo": TextColumn("Tipo", width="small"),
            "Item": TextColumn("Item", width="small"),
            "Preço": NumberColumn("Preço", **FMT_DINHEIRO),  # type: ignore
            "sub_total": NumberColumn("Sub-Total", **FMT_DINHEIRO),  # type: ignore
        },
    )
    ct.markdown("---")
    ct.markdown("## Total")
    ct.markdown(
        f"Total do pedido: R$ {selecionados["sub_total"].sum():.2f}"
    )

    if ct.button("Confirmar pedido"):
        id_pedido = salvar_pedido(selecionados)
        ss["pedido_num"] = id_pedido + 1
        concluir(ct, "Pedido confirmado.")
