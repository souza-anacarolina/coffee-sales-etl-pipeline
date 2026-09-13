from Dados import Dados
from PipelineMetricas import PipelineMetricas

# Caminho dos dados brutos
path = 'data_raw/dirty_cafe_sales.csv'

# 1. EXTRACT

dados_compras = Dados(path, 'csv')
dados_compras.qtde_registros()

# 2. TRANSFORM

key_mapping = {
    'Transaction ID': 'Cod_Transacao',
    'Item': 'Produto',
    'Quantity': 'Quantidade',
    'Price Per Unit': 'Preço Unitário',
    'Total Spent': 'Valor Total',
    'Payment Method': 'Forma de Pagamento',
    'Location': 'Tipo de Consumo',
    'Transaction Date': 'Data da Transação'
}

value_mapping = {
    'In-store': 'Presencial',
    'Takeaway': 'Para viagem',
    'Coffee': 'Café',
    'Cake': 'Bolo',
    'Cookie': 'Biscoito',
    'Salad': 'Salada',
    'Smoothie': 'Vitamina',
    'Sandwich': 'Sanduiche',
    'Credit Card': 'Cartão de Crédito',
    'Cash': 'Dinheiro',
    'Digital Wallet': 'Carteira Digital',
    'Juice': 'Suco',
    'Tea': 'Chá',
    'Espresso': 'Expresso'
}

cast_mapping = {
    'Cod_Transacao': 'string',
    'Produto': 'string',
    'Quantidade': 'Int64',
    'Preço Unitário': 'Float64',
    'Valor Total': 'Float64',
    'Forma de Pagamento': 'string',
    'Tipo de Consumo': 'string',
    'Data da Transação': 'datetime64[ns]'
}

dados_compras.rename_columns(key_mapping)
print('\nColunas renomeadas')


dados_compras.format_dates('Data da Transação')
dados_compras.rename_values(value_mapping)

dados_compras.clean_missing_values()
print('Valores inválidos tratados')


dados_compras.cast_types(cast_mapping)
dados_compras.deduplicate()
dados_compras.drop_deduplicate()
dados_compras.standardize_text()
dados_compras.tratamento_nulos_valor_total()

print('\nTransformações concluídas!')

# 3. EXPORTAÇÃO DOS DADOS TRATADOS

dados_compras.salvando_dados_virgula('data_processed/dados_transformados_virgula.csv')
dados_compras.salvando_dados_ponto_virgula('data_processed/dados_transformados_ponto_e_virgula.csv')

# 4. GERAÇÃO DAS MÉTRICAS E RELATÓRIOS

# Instancia o Pipeline de Métricas com o DataFrame tratado contido na classe Dados
pipeline_metricas = PipelineMetricas(dados_compras.dados)

print('\nGerando relatórios de métricas...\n')

# PDF único com todas as métricas
pipeline_metricas.exportar_pdf_totalizador('data_processed/metricas_consolidadas.pdf')

# PDFs individuais para cada métrica
pipeline_metricas.exportar_pdfs_separados('data_processed/metricas_pdf')

# CSVs individuais para cada métrica
pipeline_metricas.exportar_csvs_separados('data_processed/metricas_csv')

# Excel único com todas as métricas
pipeline_metricas.exportar_excel_totalizador('data_processed/metricas_todas_abas.xlsx')

print('\nPipeline de ETL e geração de métricas finalizado com sucesso!')

print(f'\nFaturamento Total: {dados_compras.faturamento_total()}')
print(f'Ticket médio: {dados_compras.ticket_medio()}')
print(f'Quantidade de transações: {dados_compras.total_transacoes()}')