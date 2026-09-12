from Dados import Dados


#Local do arquivo bruto
path = 'data_raw/dirty_cafe_sales.csv'

#1. EXTRACT

# Variável contendo o local do arquivo e o tipo do arquivo
dados_compras = Dados(path,'csv')

dados_compras.qtde_registros()

#2. TRANSFORM

#Mapeamento de tradução das colunas
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

# Mapeamento de tradução dos valores das linhas
value_mapping = {
    'In-store': 'Presencial',
    'Takeaway': 'Para viagem',
    'Coffee': 'Café',
    'Cake': 'Bolo',
    'Cookie': 'Biscoito',
    'Salad': 'Salada',
    'Smoothie': 'Vitamina',
    'Sandwich': 'Lanche',
    'Credit Card': 'Cartão de Crédito',
    'Cash': 'Dinheiro',
    'Digital Wallet': 'Carteira Digital',
    'Juice': 'Suco',
    'Tea': 'Chá',
    'Sandwich': 'Sanduiche',
    'Espresso': 'Expresso'
}

# Renomeia as colunas e imprime métricas do estado atualizado 
dados_compras.rename_columns(key_mapping)
print('\nColunas renomeadas')

# Converte a data da transação para o padrão brasileiro
dados_compras.format_dates('Data da Transação')

# Renomeia os valores e imprime métricas do estado atualizado
dados_compras.rename_values(value_mapping)

# Convertendo colunas com valores inválidos para nulo
dados_compras.clean_missing_values()

print('Valores inválidos tratados')

# Dicionário de tipos de dados
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

# Convertendo os tipos de dados das colunas
dados_compras.cast_types(cast_mapping)

# Localizando dados com Cod_Transacao duplicados.
dados_compras.deduplicate()

# Excluindo dados com Cod_Transacao duplicados.
dados_compras.drop_deduplicate()

# Removendo extras e deixando as informações em maiúsculo.
dados_compras.standardize_text()

# Ajustando o cálculo da coluna Valor Total
dados_compras.tratamento_nulos_valor_total()

print('Dados transformados')

#3. MÉTRICAS

dados_compras.valores_agrupados()

dados_compras.faturamento_por_forma_de_pagamento()

dados_compras.ticket_medio()

dados_compras.faturamento_por_tipo_de_consumo()

dados_compras.analise_temporal_de_vendas()

print('Métricas calculadas')

#4. LOAD

# Local em que o arquivo tratado deve ser salvo
path_dados_transformados = 'data_processed/dados_transformados_virgula.csv'

# Utilizando a função de salvamento de dados 
dados_compras.salvando_dados_virgula(path_dados_transformados)

path_dados_transformados = 'data_processed/dados_transformados_ponto_e_virgula.csv'

dados_compras.salvando_dados_ponto_virgula(path_dados_transformados)

print('\nPipeline executado com sucesso!')
print('\nRelatórios salvos')

print(f'\nFaturamento Total: {dados_compras.faturamento_total()}')
print(f'Ticket médio: ')
print(f'Quantidade de transações: ')
