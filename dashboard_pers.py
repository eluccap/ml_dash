import streamlit as st
import pandas as pd
import plotly.express as px

# Definição do mês e ano base
mes_ano = "jan25"

# Carregar os dados de vendas
df_inicial = pd.read_excel(f"Vendas-totais-{mes_ano}.xlsx")

# Configuração do layout da página
st.set_page_config(page_title="Marcia Lima - Dashboard KPIs", layout="wide")

# Dicionário para converter nomes dos meses em números
mes_dict = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}

# Criar coluna numérica para ordenar corretamente
df_inicial["Mês_Numérico"] = df_inicial["Mês"].map(mes_dict)

# Ordenação correta por ano e mês
df_inicial = df_inicial.sort_values(["Ano", "Mês_Numérico"])

# Criar filtros na barra lateral
caixa_filtro = st.sidebar.multiselect("Mês", df_inicial["Mês"].unique(), default=df_inicial["Mês"].unique())
caixa_filtro2 = st.sidebar.multiselect("Ano", df_inicial["Ano"].unique(), default=df_inicial["Ano"].unique())
caixa_filtro3 = st.sidebar.multiselect("Plataforma de venda", df_inicial["Plataforma de venda"].unique(), default=df_inicial["Plataforma de venda"].unique())
caixa_filtro4 = st.sidebar.multiselect("Comercial", df_inicial["Comercial"].unique(), default=df_inicial["Comercial"].unique())

# Aplicação dos filtros usando .isin()
df_filtrado = df_inicial[
    (df_inicial["Mês"].isin(caixa_filtro)) &
    (df_inicial["Ano"].isin(caixa_filtro2)) &
    (df_inicial["Plataforma de venda"].isin(caixa_filtro3)) &
    (df_inicial["Comercial"].isin(caixa_filtro4))
]

# --- Função para calcular o LTV ---
def calcular_ltv(df):
    """Calcula o LTV com base no dataframe filtrado."""
    if df.empty:
        return pd.DataFrame(columns=["CPF", "Comprador", "total_compras", "valor_total_gasto", "valor_medio_por_compra", "produtos_mais_comprados"]), pd.DataFrame(columns=["Métrica", "Valor"])

    compradores = df.groupby(["CPF", "Comprador"]).agg(
        total_compras=("ID da venda", "count"),
        valor_total_gasto=("Receita total", "sum"),
        valor_medio_por_compra=("Receita total", "mean"),
        produtos_mais_comprados=("Nome do Produto", lambda x: x.mode()[0] if not x.mode().empty else None)
    ).reset_index()

    compras_medias_por_pessoa = compradores["total_compras"].mean()
    valor_medio_por_pessoa = compradores["valor_total_gasto"].mean()

    metricas_gerais = pd.DataFrame({
        "Métrica": ["Compras médias por pessoa", "Valor médio gasto por pessoa"],
        "Valor": [compras_medias_por_pessoa, valor_medio_por_pessoa]
    })

    return compradores, metricas_gerais

# --- Recalcular métricas de LTV com base nos filtros aplicados ---
compradores_recorrentes, metricas_gerais = calcular_ltv(df_filtrado)

# --- GRÁFICO 1: QUANTIDADE TOTAL DE VENDAS POR MÊS ---
df_vendas = df_filtrado.groupby(["Mês", "Mês_Numérico"], as_index=False).agg({"Nome do Produto": "count"})
df_vendas = df_vendas.sort_values("Mês_Numérico")

fig_vendas = px.bar(df_vendas, x="Mês", y="Nome do Produto", title="Vendas por mês",
                    labels={"Nome do Produto": "Quantidade de Vendas", "Mês": "Mês"},
                    text="Nome do Produto")

fig_vendas.update_traces(textposition="outside")
fig_vendas.update_xaxes(categoryorder="array", categoryarray=list(mes_dict.keys()))

# --- GRÁFICO 2: RECEITA TOTAL POR MÊS ---
df_receita = df_filtrado.groupby(["Mês", "Mês_Numérico"], as_index=False).agg({"Receita total": "sum"})
df_receita = df_receita.sort_values("Mês_Numérico")

fig_receita = px.bar(df_receita, x="Mês", y="Receita total", title="Faturamento por mês",
                     labels={"Receita total": "Faturamento (R$)", "Mês": "Mês"},
                     text="Receita total")

fig_receita.update_traces(textposition="outside")
fig_receita.update_xaxes(categoryorder="array", categoryarray=list(mes_dict.keys()))

# --- GRÁFICO 3: QUANTIDADE TOTAL DE VENDAS POR PRODUTO ---
df_produtos = df_filtrado.groupby("Nome do Produto", as_index=False).agg({"ID da venda": "count"})
df_produtos.rename(columns={"ID da venda": "Quantidade de Vendas"}, inplace=True)

fig_produtos = px.bar(df_produtos, 
                      x="Nome do Produto", 
                      y="Quantidade de Vendas", 
                      title="Vendas por Produto",
                      labels={"Nome do Produto": "Produto", "Quantidade de Vendas": "Total de Vendas"},
                      text="Quantidade de Vendas")

fig_produtos.update_traces(textposition="outside")

# Criar colunas para disposição dos gráficos
col1, col2, col3 = st.columns(3)

# Exibir gráficos no dashboard
col1.plotly_chart(fig_vendas)   # Gráfico de Vendas por Mês
col2.plotly_chart(fig_receita)  # Gráfico de Faturamento por Mês
col3.plotly_chart(fig_produtos) # Gráfico de Vendas por Produto

# --- EXIBIR MÉTRICAS DE LTV NO DASHBOARD ---
st.sidebar.header("📊 Métricas Gerais de LTV")
if not metricas_gerais.empty:
    st.sidebar.metric(label="Compras médias por cliente", value=round(metricas_gerais.loc[metricas_gerais["Métrica"] == "Compras médias por pessoa", "Valor"].values[0], 2))
    st.sidebar.metric(label="Valor médio gasto por cliente", value=f'R$ {round(metricas_gerais.loc[metricas_gerais["Métrica"] == "Valor médio gasto por pessoa", "Valor"].values[0], 2)}')

# Exibir tabela de compradores recorrentes
st.header("🔁 Compradores Recorrentes")
st.dataframe(compradores_recorrentes)
