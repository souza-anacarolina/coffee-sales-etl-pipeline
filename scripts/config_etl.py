
FONTES_DADOS = [
    {'origem': 'csv_dirty_cafe_sales', 'path': 'data_raw/dirty_cafe_sales.csv'},
    {'origem': 'xlsx_coffee_shop_sales', 'path': 'data_raw/Coffee Shop Sales.xlsx'},
]

# ---------------------------------------------------------------------------
# MAPEAMENTO DE COLUNAS
# ---------------------------------------------------------------------------
MAPEAMENTO_COLUNAS = {
    'Transaction ID': 'Cod_Transacao',
    'Transaction Date': 'Data da Transação',
    'Transaction Time': 'Hora da Transação',
    'Quantity': 'Quantidade',
    'store_id': 'Cod_Loja',
    'store_location': 'Localizacao_Loja',
    'product_id': 'Cod_Produto',
    'Price Per Unit': 'Preço Unitário',
    'product_category': 'Categoria do Produto',
    'product_type': 'Tipo do Produto',
    'product_detail': 'Detalhe do Produto',
    'Item': 'Produto',
    'Total Spent': 'Valor Total',
    'Payment Method': 'Forma de Pagamento',
    'Location': 'Tipo de Consumo',
}

# ---------------------------------------------------------------------------
# MAPEAMENTO DE TIPOS
# ---------------------------------------------------------------------------
MAPEAMENTO_TIPOS = {
    'Cod_Transacao': 'string',
    'Produto': 'string',
    'Quantidade': 'Int64',
    'Preço Unitário': 'Float64',
    'Valor Total': 'Float64',
    'Forma de Pagamento': 'string',
    'Tipo de Consumo': 'string',
    'Data da Transação': 'datetime64[ns]',
    'Hora da Transação': 'string',
    'Cod_Loja': 'string',
    'Localizacao_Loja': 'string',
    'Cod_Produto': 'Int64',
    'Categoria do Produto': 'string',
    'Tipo do Produto': 'string',
    'Detalhe do Produto': 'string',
}
