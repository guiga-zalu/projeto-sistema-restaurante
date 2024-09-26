# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

import streamlit as st
import polars as pl

from streamlit import session_state as ss
from streamlit.column_config import NumberColumn, DatetimeColumn

if TYPE_CHECKING:
    from ..base import (
        TITULO,
        FMT_DINHEIRO,
        ler_pedidos,
        salvar_pedidos,
        concluir,
    )
else:
    from base import (
        TITULO,
        FMT_DINHEIRO,
        ler_pedidos,
        salvar_pedidos,
        concluir,
    )


def salvar_cobranca(cobranca: dict) -> bool:
    valores = [
        cobranca["Dinheiro"],
        cobranca["PIX"],
        cobranca["Cartão Débito"],
        cobranca["Cartão Crédito"],
        cobranca["Outra forma"],
    ]
    if abs(cobranca["Preço"] - sum(valores)) > 0.01 or min(valores) < 0.0:
        # st.write(cobranca["Preço"])
        # st.write(
        #     (
        #         cobranca["Dinheiro"]
        #         + cobranca["PIX"]
        #         + cobranca["Cartão Débito"]
        #         + cobranca["Cartão Crédito"]
        #         + cobranca["Outra forma"]
        #     )
        # )
        return False

    # Ler tabelas
    pedidos = ler_pedidos()

    # Alterar pedido nas tabelas
    id_pedido: int = cobranca["ID"]
    cobranca["Pago"] = True

    pedidos = (
        pedidos.with_columns(_marcador=pl.col("ID") == id_pedido)
        .with_columns(
            *(
                pl.when("_marcador")
                .then(pl.lit(cobranca[coluna]))
                .otherwise(coluna)
                .alias(coluna)
                for coluna in [
                    "Dinheiro",
                    "PIX",
                    "Cartão Débito",
                    "Cartão Crédito",
                    "Outra forma",
                    "Pago",
                ]
            )
        )
        .drop("_marcador")
    )

    # Salvar tabela
    pedidos.pipe(salvar_pedidos)

    return True


@st.fragment
def __main__():
    st.title(f"{TITULO} - Cobrança")
    ct = st.container(border=False)

    pedidos = ler_pedidos().filter(Pago=False)

    if pedidos.height == 0:
        ct.success("Sem pedidos a cobrar")
        return

    d = ct.dataframe(
        data=pedidos,
        height=(pedidos.height + 1) * 35 + 3,
        use_container_width=True,
        hide_index=True,
        column_order=[
            "ID",
            "Momento",
            "Preço",
        ],
        column_config={
            "ID": NumberColumn("ID", width="small"),
            "Momento": DatetimeColumn(
                "Momento",
                width="medium",
                format="HH:mm:ss DD/MM/YYYY",
            ),
            "Preço": NumberColumn("Preço", **FMT_DINHEIRO),  # type: ignore
        },
        selection_mode="single-row",
        on_select="rerun",
    )
    selecionados = d["selection"]["rows"]

    if len(selecionados) != 1:
        return

    selecionado: int = int(selecionados[0])
    pedido = pedidos[selecionado]
    id_pedido: int = pedido["ID"][0]
    vl_preco: float = pedido["Preço"][0]

    ct.markdown("---")
    ct.subheader("Cobrança do Pedido #%s" % str(id_pedido).zfill(2))

    ct.markdown("Preço total: `R$ %.2f`" % vl_preco)

    pagamento: pl.DataFrame = ct.data_editor(
        data=pedido,
        height=2 * 35 + 3,
        use_container_width=True,
        hide_index=True,
        column_order=[
            "Dinheiro",
            "PIX",
            "Cartão Débito",
            "Cartão Crédito",
            "Outra forma",
        ],
        column_config={
            "Dinheiro": NumberColumn(
                "Dinheiro",
                **FMT_DINHEIRO,  # type: ignore
                max_value=vl_preco,
            ),
            "PIX": NumberColumn("PIX", **FMT_DINHEIRO, max_value=vl_preco),  # type: ignore
            "Cartão Débito": NumberColumn(
                "C. Débito",
                **FMT_DINHEIRO,  # type: ignore
                max_value=vl_preco,
            ),
            "Cartão Crédito": NumberColumn(
                "C. Crédito",
                **FMT_DINHEIRO,  # type: ignore
                max_value=vl_preco,
            ),
            "Outra forma": NumberColumn(
                "Outra forma",
                **FMT_DINHEIRO,  # type: ignore
                max_value=vl_preco,
            ),
        },
        key="cobranca_pedido_%d" % int(ss["cobranca_num"]),
    )
    cobranca = pagamento.to_dicts()[0]

    vl_pago = (
        cobranca["Dinheiro"]
        + cobranca["PIX"]
        + cobranca["Cartão Débito"]
        + cobranca["Cartão Crédito"]
        + cobranca["Outra forma"]
    )
    ct.markdown("Total pago: `R$ %.2f`" % vl_pago)
    vl_pendente = vl_preco - vl_pago
    ct.markdown("Total pendente: `R$ %.2f`" % vl_pendente)

    if vl_pendente > 0.01:
        return

    if ct.button("Confirmar"):
        if salvar_cobranca(cobranca):
            ss["cobranca_num"] = id_pedido + 1
            concluir(ct, "Pedido cobrado.")
        else:
            ct.error("Erro ao cobrar o pedido.\nOs valores não fecham.")
