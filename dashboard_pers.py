import streamlit as st
import pandas as pd
import plotly.express as px

mes_ano = "jan25"

df_inicial = pd.read_excel (f"Vendas-totais-{mes_ano}.xlsx")
df_ltv = pd. read_excel (f"LTV-{mes_ano}.xlsx")

st.set_page_config (layout = "wide")
