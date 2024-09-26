# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING
from pathlib import Path
from time import sleep

if TYPE_CHECKING:
    from polars._typing import SchemaDict
    from streamlit.delta_generator import DeltaGenerator

import streamlit as st
import polars as pl

from streamlit import session_state as ss


TITULO: str = ":green[2ª] Festa :red[Italiana]"

PASTA_RAIZ: Path = (
    Path(__file__)
    # projeto_...
    .parent
    # src
    .parent
    # raíz
    .parent
)


SCHEMA_CARDAPIO: "SchemaDict" = {
    "ID": pl.UInt16,
    "Categoria": pl.String,
    "Tipo": pl.String,
    "Item": pl.String,
    "Preço": pl.Float32,
}
SCHEMA_PEDIDO: "SchemaDict" = {
    "ID": pl.UInt16,
    "Momento": pl.Datetime,
    "Preço": pl.Float32,
    "Dinheiro": pl.Float32,
    "PIX": pl.Float32,
    "Cartão Débito": pl.Float32,
    "Cartão Crédito": pl.Float32,
    "Outra forma": pl.Float32,
    "Pago": pl.Boolean,
    "Preparado": pl.Boolean,
    "Entregue": pl.Boolean,
}
SCHEMA_PEDIDOS_ITENS: "SchemaDict" = {
    "ID": pl.UInt16,
    "ID Pedido": pl.UInt16,
    "ID Cardápio": pl.UInt16,
    "Quantidade": pl.UInt16,
    "Preço": pl.Float32,
}

FMT_DINHEIRO = dict(
    min_value=0,
    default=0,
    step=0.01,
    format="R$ %.2f",
    width="small",
)


def init():
    print("Iniciando...")
    ss["pedido_num"] = 1
    ss["cobranca_num"] = 1


def ler(arquivo: str, planilha: str, schema: "SchemaDict") -> pl.DataFrame:
    return pl.read_excel(
        (PASTA_RAIZ / "dados" / arquivo).read_bytes(),
        sheet_name=planilha,
        schema_overrides=schema,
    )


def ler_cardapio() -> pl.DataFrame:
    return ler("cardápio.xlsx", "Cardápio", SCHEMA_CARDAPIO)


def ler_pedidos() -> pl.DataFrame:
    return ler("pedidos.xlsx", "Pedidos", SCHEMA_PEDIDO)


def ler_itens() -> pl.DataFrame:
    return ler("pedidos_itens.xlsx", "Pedidos Itens", SCHEMA_PEDIDOS_ITENS)


def salvar_pedidos(pedidos: pl.DataFrame) -> None:
    pedidos.write_excel(
        PASTA_RAIZ / "dados" / "pedidos.xlsx",
        worksheet="Pedidos",
        autofit=True,
    )


def salvar_itens(itens: pl.DataFrame) -> None:
    itens.write_excel(
        PASTA_RAIZ / "dados" / "pedidos_itens.xlsx",
        worksheet="Pedidos Itens",
        autofit=True,
    )


def concluir(ct: "DeltaGenerator", texto: str):
    ct.success(texto)
    sleep(1.5)
    st.rerun(scope="fragment")
