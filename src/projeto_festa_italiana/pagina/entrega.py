# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

import streamlit as st
import polars as pl

from streamlit.column_config import (
    NumberColumn,
    DatetimeColumn,
    TextColumn,
)

if TYPE_CHECKING:
    from ..base import (
        TITULO,
        ler_cardapio,
        ler_itens,
        ler_pedidos,
        salvar_pedidos,
        concluir,
    )
else:
    from base import (
        TITULO,
        ler_cardapio,
        ler_itens,
        ler_pedidos,
        salvar_pedidos,
        concluir,
    )


def entregar_pedido(id_pedido: int) -> None:
    # Ler tabelas
    pedidos = ler_pedidos()
    # Alterar tabela
    pedidos = (
        pedidos.with_columns(_marcador=pl.col("ID") == id_pedido)
        .with_columns(
            Entregue=pl.when("_marcador").then(True).otherwise("Entregue"),
        )
        .drop("_marcador")
    )
    # Salvar tabela
    pedidos.pipe(salvar_pedidos)


@st.fragment
def __main__():
    st.title(f"{TITULO} - Entregar")
    ct = st.container(border=False)

    pedidos = ler_pedidos().filter(
        Pago=True, Preparado=True, Entregue=False
    )

    if pedidos.height == 0:
        ct.success("Sem pedidos a entregar")
        return

    d = ct.dataframe(
        data=pedidos,
        height=(pedidos.height + 1) * 35 + 3,
        use_container_width=True,
        hide_index=True,
        column_order=["ID", "Momento"],
        column_config={
            "ID": NumberColumn("ID", width="small"),
            "Momento": DatetimeColumn(
                "Momento",
                width="medium",
                format="HH:mm:ss DD/MM/YYYY",
            ),
        },
        selection_mode="single-row",
        on_select="rerun",
    )
    selecionados = d["selection"]["rows"]  # type: ignore

    if len(selecionados) != 1:
        return

    selecionado = int(selecionados[0])

    pedido = pedidos[selecionado]
    id_pedido: int = pedido["ID"][0]

    ct.markdown("---")
    ct.subheader("Detalhes do Pedido #%s" % str(id_pedido).zfill(2))

    itens = (
        ler_itens()
        .lazy()
        .filter(pl.col("ID Pedido") == id_pedido)
        .select("ID Cardápio", "Quantidade")
        .join(
            ler_cardapio()
            .lazy()
            .select("ID", "Categoria", "Tipo", "Item"),
            left_on="ID Cardápio",
            right_on="ID",
            how="left",
        )
        .drop("ID Cardápio")
        .collect()
    )
    ct.dataframe(
        data=itens,
        height=(itens.height + 1) * 35 + 3,
        use_container_width=True,
        hide_index=True,
        column_order=["Categoria", "Tipo", "Item", "Quantidade"],
        column_config={
            "Quantidade": NumberColumn("Quantidade", width="small"),
            "Categoria": TextColumn("Categoria", width="medium"),
            "Tipo": TextColumn("Tipo", width="medium"),
            "Item": TextColumn("Item", width="medium"),
        },
    )

    if ct.button("Confirmar"):
        entregar_pedido(id_pedido)
        concluir(ct, "Pedido entregue.")
