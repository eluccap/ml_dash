import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração correta da página
st.set_page_config(page_title="Marcia Lima - Dashboard KPIs", page_icon="📊", layout="wide")

# Definição do mês e ano base
mes_ano = "jan25"

# Carregar os dados de vendas
df_inicial = pd.read_excel(f"Vendas-totais-{mes_ano}.xlsx")

# Dicionário para converter nomes dos meses em números
mes_dict = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}

df_inicial["Mês_Numérico"] = df_inicial["Mês"].map(mes_dict)

# Ordenação correta por ano e mês
df_inicial = df_inicial.sort_values(["Ano", "Mês_Numérico"])

# Criar filtros na barra lateral
caixa_filtro = st.sidebar.multiselect("Mês", df_inicial["Mês"].unique(), default=df_inicial["Mês"].unique())
caixa_filtro2 = st.sidebar.multiselect("Ano", df_inicial["Ano"].unique(), default=df_inicial["Ano"].unique())
caixa_filtro3 = st.sidebar.multiselect("Plataforma de venda", df_inicial["Plataforma de venda"].unique(), default=df_inicial["Plataforma de venda"].unique())
caixa_filtro4 = st.sidebar.multiselect("Comercial", df_inicial["Comercial"].unique(), default=df_inicial["Comercial"].unique())

# Aplicação dos filtros
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
        return pd.DataFrame(columns=["CPF", "Comprador", "Total de Compras", "Valor total gasto", "Valor médio por compra", "Produtos mais comprados"]), pd.DataFrame(columns=["Métrica", "Valor"])

    compradores = df.groupby(["CPF", "Comprador"]).agg(
        **{
            "Total de Compras": ("ID da venda", "count"),
            "Valor total gasto": ("Receita total", "sum"),
            "Valor médio por compra": ("Receita total", "mean"),
            "Produtos mais comprados": ("Nome do Produto", lambda x: x.mode()[0] if not x.mode().empty else None)
        }
    ).reset_index()

    # Ordenando por total de compras (maior primeiro)
    compradores = compradores.sort_values(by="Total de Compras", ascending=False)

    # Formatando os valores monetários
    compradores["Valor total gasto"] = compradores["Valor total gasto"].apply(lambda x: f'R$ {x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
    compradores["Valor médio por compra"] = compradores["Valor médio por compra"].apply(lambda x: f'R$ {x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))

    compras_medias_por_pessoa = compradores["Total de Compras"].mean()
    valor_medio_por_pessoa = df["Receita total"].sum() / df["CPF"].nunique() if df["CPF"].nunique() > 0 else 0

    metricas_gerais = pd.DataFrame({
        "Métrica": ["Compras médias por pessoa", "Valor médio gasto por pessoa"],
        "Valor": [compras_medias_por_pessoa, f'R$ {valor_medio_por_pessoa:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")]
    })

    return compradores, metricas_gerais

# --- Recalcular métricas de LTV ---
compradores_recorrentes, metricas_gerais = calcular_ltv(df_filtrado)

# Definição da cor personalizada
cor_personalizada = "#CAA55F"

# --- Gráfico: QUANTIDADE TOTAL DE VENDAS POR MÊS ---
df_vendas = df_filtrado.groupby(["Mês", "Mês_Numérico"], as_index=False).agg({"Nome do Produto": "count"})
df_vendas = df_vendas.sort_values("Mês_Numérico")

fig_vendas = px.bar(df_vendas, x="Mês", y="Nome do Produto", title="Vendas por mês",
                    labels={"Nome do Produto": "Quantidade de Vendas", "Mês": "Mês"},
                    text="Nome do Produto", color_discrete_sequence=[cor_personalizada])

fig_vendas.update_traces(textposition="outside")

# --- Gráfico: RECEITA TOTAL POR MÊS ---
df_receita = df_filtrado.groupby(["Mês", "Mês_Numérico"], as_index=False).agg({"Receita total": "sum"})
df_receita = df_receita.sort_values("Mês_Numérico")

fig_receita = px.bar(df_receita, x="Mês", y="Receita total", title="Faturamento por mês",
                     labels={"Receita total": "Faturamento (R$)", "Mês": "Mês"},
                     text="Receita total", color_discrete_sequence=[cor_personalizada])

fig_receita.update_traces(textposition="outside")

# --- Gráfico: QUANTIDADE TOTAL DE VENDAS POR PRODUTO ---
df_produtos = df_filtrado.groupby("Nome do Produto", as_index=False).agg({"ID da venda": "count"})
df_produtos.rename(columns={"ID da venda": "Quantidade de Vendas"}, inplace=True)

fig_produtos = px.bar(df_produtos, x="Nome do Produto", y="Quantidade de Vendas", title="Vendas por Produto",
                      labels={"Nome do Produto": "Produto", "Quantidade de Vendas": "Total de Vendas"},
                      text="Quantidade de Vendas", color_discrete_sequence=[cor_personalizada])

fig_produtos.update_traces(textposition="outside")

# Criar colunas para disposição dos gráficos
col1, col2, col3 = st.columns(3)

# Exibir gráficos no dashboard
col1.plotly_chart(fig_vendas)
col2.plotly_chart(fig_receita)
col3.plotly_chart(fig_produtos)

# --- EXIBIR MÉTRICAS DE LTV ---
st.sidebar.header("📊 Métricas Gerais de LTV")
if not metricas_gerais.empty:
    try:
        compras_medias = round(float(str(metricas_gerais.loc[0, "Valor"]).replace("R$ ", "").replace(".", "").replace(",", ".")), 3)
        valor_medio_gasto = str(metricas_gerais.loc[1, "Valor"])

        st.sidebar.metric(label="Compras médias por cliente", value=f"{compras_medias:.3f}")
        st.sidebar.metric(label="Valor médio gasto por cliente", value=valor_medio_gasto)
    except (KeyError, IndexError, ValueError) as e:
        st.sidebar.error("Erro ao calcular as métricas de LTV. Verifique os dados.")


# Exibir tabela de compradores recorrentes
st.header("🔁 Compradores Recorrentes")
st.dataframe(compradores_recorrentes)
