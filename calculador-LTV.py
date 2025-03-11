import pandas as pd

# Carregar a planilha de vendas
arquivo = "Vendas-totais-jan25.xlsx"  # Substitua pelo caminho correto do seu arquivo
df = pd.read_excel(arquivo)

# Agrupar os dados por comprador (CPF ou Email)
compradores = df.groupby(["CPF", "Comprador"]).agg(
    total_compras=("ID da venda", "count"),
    valor_total_gasto=("Receita total", "sum"),
    valor_medio_por_compra=("Receita total", "mean"),
    produtos_mais_comprados=("Nome do Produto", lambda x: x.mode()[0] if not x.mode().empty else None)
).reset_index()  # Resetar o índice para manter as colunas acessíveis

compradores = compradores.sort_values(by="total_compras", ascending=False)

# Calcular estatísticas gerais
compras_medias_por_pessoa = compradores["total_compras"].mean()
valor_medio_por_pessoa = compradores["valor_total_gasto"].mean()

# Criar um DataFrame com as métricas gerais
metricas_gerais = pd.DataFrame({
    "Métrica": ["Compras médias por pessoa", "Valor médio gasto por pessoa"],
    "Valor": [compras_medias_por_pessoa, valor_medio_por_pessoa]
})

# Salvar os resultados em um arquivo Excel com múltiplas abas
with pd.ExcelWriter("LTV-jan25.xlsx") as writer:
    compradores.to_excel(writer, sheet_name="Compradores Recorrentes", index=False)
    metricas_gerais.to_excel(writer, sheet_name="Métricas Gerais", index=False)

