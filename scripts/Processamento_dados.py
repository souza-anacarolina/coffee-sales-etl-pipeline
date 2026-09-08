from Dados import Dados


#Local do arquivo bruto
path = 'data_raw/dirty_cafe_sales.csv'

#1. EXTRACT

# Variável contendo o local do arquivo e o tipo do arquivo
dados_compras = Dados(path,'csv')

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
    'Tea': 'Chá'
}

# Imprime os nomes das colunas originais
print('\nNomes das colunas: ',dados_compras.nomes_colunas)

# Renomeia as colunas e imprime métricas do estado atualizado 
dados_compras.rename_columns(key_mapping)
print('\nRenomeação de nomes das colunas realizado!')
print('\nNomes atualizados das colunas: ',dados_compras.nomes_colunas)

# Imprime a data original dos dados
print('\nPadrão das datas:',dados_compras.retorna_informacao('Data da Transação'))

# Converte a data da transação para o padrão brasileiro
dados_compras.format_dates('Data da Transação')
print('\nDatas formatadas para o padrão brasileiro!')

# Imprime as datas formatadas
print('\nNovo padrão das datas:',dados_compras.retorna_informacao('Data da Transação'))

#Retorna as informações da planilha com os dados originais
print('\nInformações originais:\n',dados_compras.dados)

# Renomeia os valores e imprime métricas do estado atualizado
dados_compras.rename_values(value_mapping)
print('\nInformações atualizadas para PT-BR!')
print('\nInformações atualizadas:\n',dados_compras.dados)

# Retorna dados com valores inválidos.
print('\nValores inválidos:\n',dados_compras.missing_invalid_values())

# Convertendo colunas com valores inválidos para nulo
dados_compras.clean_missing_values()
print('\nValores inválidos convertidos para null!')

# Exibe os dados com os valores inválidos convertidos para nulo
print('\nNovas informações com valores nulos\n',dados_compras.dados)

# Exibindo colunas com valores nulos
print('\nColunas com valores nulos:\n', dados_compras.valores_nulos())

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
print('\nTipos de dados convertidos!')

# Localizando dados com Cod_Transacao duplicados.
dados_compras.deduplicate()
print('\nBusca por Cod_Transacao duplicados realizada!')

# Excluindo dados com Cod_Transacao duplicados.
dados_compras.drop_deduplicate()
print('\nRegistros com Cod_Transacao duplicados excluídos!')

# Removendo extras e deixando as informações em maiúsculo.
dados_compras.standardize_text()
print('\nDados padronizados!')

# Ajustando o cálculo da coluna Valor Total
dados_compras.tratamento_nulos_valor_total()
print('\nProdutos com valor total nulo tratados!')

#3. LOAD

# Local em que o arquivo tratado deve ser salvo
path_dados_transformados = 'data_processed/dados_transformados_virgula.csv'

# Utilizando a função de salvamento de dados e imprimindo o arquivo salvo
dados_compras.salvando_dados_virgula(path_dados_transformados)
print("\nArquivo separado por vírgula gerado com sucesso em:",path_dados_transformados)


path_dados_transformados = 'data_processed/dados_transformados_ponto_e_virgula.csv'

dados_compras.salvando_dados_ponto_virgula(path_dados_transformados)
print("\nArquivo separado por ponto e vírgula gerado com sucesso em:",path_dados_transformados,'\n')


#4. MÉTRICAS

largura = 57

print(f"{'*'*largura}")
print(f"{'Métricas de Negócio':^{largura}}")
print(f"{'*'*largura}")


# Imprime as quantidades vendidas agrupado por produto.
print(f"\n{' QUANTIDADES VENDIDAS AGRUPADO POR PRODUTO ':=^57}")
print(dados_compras.valores_agrupados())

print(f"\n{' FATURAMENTO TOTAL POR FORMA DE PAGAMENTO ':=^57}")
print(dados_compras.faturamento_por_forma_de_pagamento())