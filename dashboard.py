from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px



# CONFIGURAÇÃO
st.set_page_config(
    page_title="InsightFlow Dashboard",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "ecom_data.csv"
OUTPUT_PATH = BASE_DIR / "outputs" / "previsao_proximo_mes.csv"
RFM_PATH = BASE_DIR / "outputs" / "segmentacao_rfm.csv"
OUTLIERS_PATH = BASE_DIR / "outputs" / "outliers_detectados.csv"



# FUNÇÕES DE CARGA
@st.cache_data
def carregar_dados():
    df = pd.read_csv(DATA_PATH)
    df["Data_Venda"] = pd.to_datetime(df["Data_Venda"])
    return df


@st.cache_data
def carregar_previsao():
    if OUTPUT_PATH.exists():
        prev = pd.read_csv(OUTPUT_PATH)
        prev["Data_Venda"] = pd.to_datetime(prev["Data_Venda"])
        return prev
    return pd.DataFrame()


@st.cache_data
def carregar_rfm():
    if RFM_PATH.exists():
        return pd.read_csv(RFM_PATH)
    return pd.DataFrame()


@st.cache_data
def carregar_outliers():
    if OUTLIERS_PATH.exists():
        out = pd.read_csv(OUTLIERS_PATH)
        if "Data_Venda" in out.columns:
            out["Data_Venda"] = pd.to_datetime(out["Data_Venda"])
        return out
    return pd.DataFrame()


def classificar_cliente_rfm(row):
    r = int(row["R_Score"])
    f = int(row["F_Score"])
    m = int(row["M_Score"])

    if r >= 3 and f >= 3 and m >= 3:
        return "Cliente Premium"
    if r >= 3 and f >= 3:
        return "Cliente Leal"
    if r >= 3 and m >= 3:
        return "Cliente de Alto Valor"
    if r <= 2 and f <= 2:
        return "Cliente em Risco"
    return "Cliente Regular"



# CARGA
df = carregar_dados()
previsao_df = carregar_previsao()
rfm_df = carregar_rfm()
outliers_df = carregar_outliers()

if df.empty:
    st.error("O arquivo data/ecom_data.csv não foi encontrado ou está vazio.")
    st.stop()

if not rfm_df.empty and {"R_Score", "F_Score", "M_Score"}.issubset(rfm_df.columns):
    rfm_df["Segmento"] = rfm_df.apply(classificar_cliente_rfm, axis=1)



# SIDEBAR
st.sidebar.title("Filtros")

categorias = sorted(df["Categoria_Produto"].dropna().unique())
estados = sorted(df["Estado"].dropna().unique())
canais = sorted(df["Canal_Venda"].dropna().unique())
metodos = sorted(df["Metodo_Pagamento"].dropna().unique())

categorias_sel = st.sidebar.multiselect(
    "Categoria",
    options=categorias,
    default=categorias
)

estados_sel = st.sidebar.multiselect(
    "Estado",
    options=estados,
    default=estados
)

canais_sel = st.sidebar.multiselect(
    "Canal de Venda",
    options=canais,
    default=canais
)

metodos_sel = st.sidebar.multiselect(
    "Método de Pagamento",
    options=metodos,
    default=metodos
)

data_min = df["Data_Venda"].min().date()
data_max = df["Data_Venda"].max().date()

periodo = st.sidebar.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

df_filtrado = df[
    (df["Categoria_Produto"].isin(categorias_sel)) &
    (df["Estado"].isin(estados_sel)) &
    (df["Canal_Venda"].isin(canais_sel)) &
    (df["Metodo_Pagamento"].isin(metodos_sel))
].copy()

if isinstance(periodo, tuple) and len(periodo) == 2:
    data_ini, data_fim = periodo
    df_filtrado = df_filtrado[
        (df_filtrado["Data_Venda"].dt.date >= data_ini) &
        (df_filtrado["Data_Venda"].dt.date <= data_fim)
    ]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()



st.title("📊 InsightFlow - Dashboard Interativo")
st.caption("Análise de vendas de e-commerce com KPIs, visualizações, segmentação RFM e previsão de vendas.")



# KPIs
faturamento_total = df_filtrado["Valor_Total"].sum()
ticket_medio = df_filtrado["Valor_Total"].mean()
total_pedidos = df_filtrado["ID_Transacao"].nunique()
clientes_unicos = df_filtrado["ID_Cliente"].nunique()
qtd_itens = df_filtrado["Quantidade"].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")
col2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("Pedidos", f"{total_pedidos}")
col4.metric("Clientes Únicos", f"{clientes_unicos}")
col5.metric("Itens Vendidos", f"{int(qtd_itens)}")



aba1, aba2, aba3, aba4 = st.tabs([
    "Visão Geral",
    "Clientes e RFM",
    "Previsão",
    "Dados"
])



# VISÃO GERAL
with aba1:
    st.subheader("Visão Geral do Negócio")

    vendas_tempo = (
        df_filtrado.groupby("Data_Venda", as_index=False)["Valor_Total"]
        .sum()
        .sort_values("Data_Venda")
    )

    vendas_categoria = (
        df_filtrado.groupby("Categoria_Produto", as_index=False)["Valor_Total"]
        .sum()
        .sort_values("Valor_Total", ascending=False)
    )

    top_clientes = (
        df_filtrado.groupby("ID_Cliente", as_index=False)["Valor_Total"]
        .sum()
        .sort_values("Valor_Total", ascending=False)
        .head(10)
    )

    top_produtos = (
        df_filtrado.groupby("Nome_Produto", as_index=False)["Quantidade"]
        .sum()
        .sort_values("Quantidade", ascending=False)
        .head(10)
    )

    fig_tempo = px.line(
        vendas_tempo,
        x="Data_Venda",
        y="Valor_Total",
        title="Vendas ao Longo do Tempo"
    )

    fig_categoria = px.bar(
        vendas_categoria,
        x="Categoria_Produto",
        y="Valor_Total",
        title="Faturamento por Categoria"
    )

    fig_clientes = px.bar(
        top_clientes,
        x="ID_Cliente",
        y="Valor_Total",
        title="Top 10 Clientes por Faturamento"
    )

    fig_produtos = px.bar(
        top_produtos,
        x="Nome_Produto",
        y="Quantidade",
        title="Top 10 Produtos por Quantidade"
    )

    col_a, col_b = st.columns(2)
    col_a.plotly_chart(fig_tempo, use_container_width=True)
    col_b.plotly_chart(fig_categoria, use_container_width=True)

    col_c, col_d = st.columns(2)
    col_c.plotly_chart(fig_clientes, use_container_width=True)
    col_d.plotly_chart(fig_produtos, use_container_width=True)

    st.subheader("Distribuição do Valor Total")
    fig_box = px.box(df_filtrado, y="Valor_Total", title="Boxplot de Valor Total")
    st.plotly_chart(fig_box, use_container_width=True)

    if not outliers_df.empty:
        st.subheader("Outliers Detectados")
        outliers_filtrados = outliers_df.copy()

        if "Categoria_Produto" in outliers_filtrados.columns:
            outliers_filtrados = outliers_filtrados[
                outliers_filtrados["Categoria_Produto"].isin(categorias_sel)
            ]

        if "Estado" in outliers_filtrados.columns:
            outliers_filtrados = outliers_filtrados[
                outliers_filtrados["Estado"].isin(estados_sel)
            ]

        st.dataframe(
            outliers_filtrados[[
                "ID_Transacao", "Data_Venda", "ID_Cliente",
                "Nome_Produto", "Categoria_Produto", "Valor_Total"
            ]].head(30),
            use_container_width=True
        )



# CLIENTES E RFM
with aba2:
    st.subheader("Segmentação de Clientes (RFM)")

    if rfm_df.empty:
        st.info("Arquivo de RFM não encontrado. Rode o pipeline principal primeiro.")
    else:
        st.metric("Clientes Segmentados", len(rfm_df))

        segmento_count = (
            rfm_df["Segmento"]
            .value_counts()
            .reset_index()
        )
        segmento_count.columns = ["Segmento", "Quantidade"]

        fig_segmentos = px.bar(
            segmento_count,
            x="Segmento",
            y="Quantidade",
            title="Distribuição dos Segmentos de Clientes"
        )
        st.plotly_chart(fig_segmentos, use_container_width=True)

        fig_rfm = px.scatter(
            rfm_df,
            x="Frequencia",
            y="Monetario",
            color="Segmento",
            size="Recencia",
            hover_data=["ID_Cliente", "RFM_Score"],
            title="RFM: Frequência x Monetário"
        )
        st.plotly_chart(fig_rfm, use_container_width=True)

        st.subheader("Tabela de Segmentação")
        st.dataframe(rfm_df.head(50), use_container_width=True)



# PREVISÃO
with aba3:
    st.subheader("Modelo Preditivo de Vendas")

    historico = (
        df_filtrado.groupby("Data_Venda", as_index=False)["Valor_Total"]
        .sum()
        .sort_values("Data_Venda")
    )

    fig_hist = px.line(
        historico,
        x="Data_Venda",
        y="Valor_Total",
        title="Histórico de Vendas"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    if previsao_df.empty:
        st.info("Arquivo de previsão não encontrado. Rode o pipeline principal primeiro.")
    else:
        fig_prev = px.line(
            previsao_df,
            x="Data_Venda",
            y="Previsao_Vendas",
            title="Previsão dos Próximos 30 Dias"
        )
        st.plotly_chart(fig_prev, use_container_width=True)

        combinado = pd.concat([
            historico.rename(columns={"Valor_Total": "Valor"})[["Data_Venda", "Valor"]].assign(Tipo="Histórico"),
            previsao_df.rename(columns={"Previsao_Vendas": "Valor"})[["Data_Venda", "Valor"]].assign(Tipo="Previsão")
        ])

        fig_comb = px.line(
            combinado,
            x="Data_Venda",
            y="Valor",
            color="Tipo",
            title="Histórico + Previsão"
        )
        st.plotly_chart(fig_comb, use_container_width=True)

        media_prev = previsao_df["Previsao_Vendas"].mean()
        st.metric("Média Prevista de Vendas Diárias", f"R$ {media_prev:,.2f}")

        st.dataframe(previsao_df.head(30), use_container_width=True)



# DADOS
with aba4:
    st.subheader("Base Filtrada")
    st.dataframe(df_filtrado.head(100), use_container_width=True)

    st.subheader("Resumo Estatístico")
    st.dataframe(df_filtrado.describe(include="all"), use_container_width=True)