# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

import streamlit as st
from streamlit_antd_components import menu, MenuItem

if TYPE_CHECKING:
    from .base import TITULO, init

    init()

    from .pagina.pedido import __main__ as pg_pedido
    from .pagina.cobranca import __main__ as pg_cobranca
    from .pagina.preparacao import __main__ as pg_preparacao
    from .pagina.entrega import __main__ as pg_entrega
else:
    from base import TITULO, init

    init()

    from pagina.pedido import __main__ as pg_pedido
    from pagina.cobranca import __main__ as pg_cobranca
    from pagina.preparacao import __main__ as pg_preparacao
    from pagina.entrega import __main__ as pg_entrega


with st.sidebar:
    pagina = menu(
        format_func="title",
        open_all=True,
        size=15,
        color="green",
        return_index=False,
        items=[
            MenuItem("Pedido"),
            MenuItem("Cobrança"),
            MenuItem("Conferir e preparar"),
            MenuItem("Entregar e fechar"),
        ],
    )

match pagina:
    case "Pedido":
        pg_pedido()
    case "Cobrança":
        pg_cobranca()
    case "Conferir e preparar":
        pg_preparacao()
    case "Entregar e fechar":
        pg_entrega()
    case _:
        st.title(TITULO)
        st.write("Nenhuma página selecionada")
