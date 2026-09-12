import csv
import json
from datetime import datetime
import pandas as pd

class Dados:

    pd.options.display.float_format = 'R$ {:,.2f}'.format

    def __init__(self, path, tipo_dados):
        self.__path = path
        self.__tipo_dados = tipo_dados
        self.__df = self.__leitura_dados()

    # =========================================================
    # PROPRIEDADES DE ACESSO
    # =========================================================


    @property
    def dados(self):
        """Retorna o DataFrame."""

        return self.__df.head(5)

    @property
    def nomes_colunas(self):
        """Retorna os nomes das colunas."""

        return list(self.__df.columns)

    @property
    def path(self):
        """Retorna o caminho dos dados."""

        return self.__path

    # =========================================================
    # LEITURA DOS DADOS
    # =========================================================

    def __leitura_json(self):
        with open(self.__path, 'r', encoding='utf-8') as file:
            return pd.DataFrame(json.load(file))

    def __leitura_csv(self):
        return pd.read_csv(self.__path,encoding='utf-8')

    def __leitura_lista(self):
        if not isinstance(self.__path, list):
            raise TypeError(
                f'Tipo de dado incorreto: {self.__tipo_dados}')

        dados = self.__path
        self.__path = 'lista em memória'

        return pd.DataFrame(dados)

    def __leitura_dados(self):

        if self.__tipo_dados == 'csv':
            return self.__leitura_csv()

        elif self.__tipo_dados == 'json':
            return self.__leitura_json()

        elif self.__tipo_dados == 'list':
            return self.__leitura_lista()

        else:
            raise ValueError(f'Tipo de arquivo não suportado: {self.__tipo_dados}')

    def qtde_registros(self):
        """
        Retorna a quanttidade de registros carregados
        """

        print(f"\nDados carregados: {len(self.__df)} registros")

    # =========================================================
    # TRANSFORMAÇÃO DOS DADOS
    # =========================================================

    def rename_columns(self, key_mapping):
        """
        Renomeia as colunas do DataFrame.
        """

        self.__df.rename(columns=key_mapping,inplace=True)

    def rename_values(self, value_mapping):
        """
        Substitui valores dentro do DataFrame.
        """

        self.__df.replace(value_mapping,inplace=True)

    def cast_types(self,cast_mapping):
            """
            Covertendo tipo de dados das colunas
            """
            self.__df = self.__df.astype(cast_mapping)

    def retorna_data_formatada(self, target_column):
            """
            Retorna a data formatada para o padrão brasileiro.
            """
    
            return self.__df[target_column].head(5).dt.strftime('%d/%m/%Y').to_string()

    def retorna_data_original(self, target_column):
        """
        Retorna a data original dos dados
        """

        return self.__df[target_column].head(5).to_string()

    def format_dates(self, target_column):
        """
        Converte os valores da coluna para o tipo datetime
        """

        self.__df[target_column] = pd.to_datetime(
            self.__df[target_column],errors='coerce')

    def deduplicate(self):
        """
        Localiza dados em que o Cod_Transacao esteja informado mais de uma vez
        """
        duplicadas = self.__df.duplicated(subset=['Cod_Transacao'], keep=False)
        linhas_duplicadas = self.__df[duplicadas]
              
        return linhas_duplicadas

    def drop_deduplicate(self):
        """ 
        Remove as duplicadas mantendo a primeira ocorrência 
        """
        return self.__df.drop_duplicates(subset=['Cod_Transacao'], inplace=True)


    def standardize_text(self):
        """
        Remove os espaços extras e coloca os dados em maiùsculo.
        """
        text_columns = self.__df.select_dtypes(include=['object', 'string']).columns

        self.__df[text_columns] = (self.__df[text_columns].apply(lambda column: column.str.strip().str.upper()))


    # =========================================================
    # CRIAÇÃO DE NOVAS MÉTRICAS
    # =========================================================

    def valores_agrupados(self):
        """
        Retorna o valor total e a quantidade agrupados por produto
        """

        resultado = self.__df.groupby('Produto').agg({'Quantidade': 'sum',
                                                      'Valor Total':'sum'})

        resultado = resultado.rename(columns={'Valor Total': 'Valor Total'})

        
        return resultado.reset_index()

    def faturamento_total(self):
        """
        Retorna o valor total de faturamento
        """
        total = self.__df['Valor Total'].sum()

        resultado = f'{total:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        return f'R$ {resultado}'

    def faturamento_por_forma_de_pagamento(self):
        """
        Retorna o total gasto e a quantidade de transações separados por forma de pagamento
        """

        resultado = self.__df.groupby('Forma de Pagamento').agg({'Valor Total' : 'sum',
                                                                'Cod_Transacao': 'count' })

        resultado = resultado.rename(columns={'Valor Total': 'Faturamento Total', 'Cod_Transacao': 'Quantidade de Transações'})

        return resultado.reset_index()

    def ticket_medio(self):
        """
        Retorna o valor médio gasto por venda
        """

        valor_total = self.__df['Valor Total'].sum()

        total_transacoes = self.__df['Cod_Transacao'].nunique()

        return round(valor_total / total_transacoes,2)

    def faturamento_por_tipo_de_consumo(self):
        """
        Retorna a proporção do faturamento entre os tipos de consumo
        """

        resultado = self.__df.groupby('Tipo de Consumo').agg({'Valor Total': 'sum',
                                                              'Cod_Transacao': 'count'})

        resultado = resultado.rename(columns={'Faturamento Total':'Faturamento Total', 'Cod_Transacao': 'Quantidade de Transações'})

        return resultado.reset_index()

    def analise_temporal_de_vendas(self):

        self.__df['Data da Transação'] = pd.to_datetime(self.__df['Data da Transação'])

        dias = {
            'Monday': 'Segunda-feira',
            'Tuesday': 'Terça-feira',
            'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }

        ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

        resultado = self.__df.groupby(self.__df['Data da Transação'].dt.day_name().map(dias))['Valor Total'].sum()

        resultado.index = pd.Categorical(resultado.index,categories=ordem_dias,ordered=True)

        return resultado.sort_index().to_string()

    # =========================================================
    # SALVAMENTO
    # =========================================================

    def salvando_dados_virgula(self, path):
        """
        Salva o DataFrame em um arquivo CSV em que os dados são separados por vírgula.
        """

        self.__df.to_csv(path,index=False,encoding='utf-8-sig',float_format='%.2f',date_format='%d/%m/%Y')


    def salvando_dados_ponto_virgula(self, path):
        """
         Salva o DataFrame em um arquivo CSV em que os dados são separados por ponto e vírgula.
        """

        self.__df.to_csv(path,index=False,encoding='utf-8-sig',sep=';',decimal=',',float_format='%.2f',date_format='%d/%m/%Y')

    # =========================================================
    # TRATAMENTO DE VALORES AUSENTES
    # =========================================================

    def missing_invalid_values(self):
        """
        Identifica valores considerados inválidos.
        """
        invalid_values = ['UNKNOWN','unknown','error','ERROR','n/a','N/A','nan']
        return invalid_values

    
    def clean_missing_values(self):
        """
        Identifica valores considerados inválidos e os transforma em valores ausentes.
        """
        
        self.__df.replace(self.missing_invalid_values(),pd.NA,inplace=True)
        return self.valores_nulos()

    def valores_nulos(self):
        """
        Retorna a quantidade de valores nulos por coluna.
        """

        return self.__df.isna().sum().to_string()

    def tratamento_nulos_valor_total(self):
        """
        Em dados com nulo na coluna Valor Total realiza o cálculo de quantidade * preço unitário
        """

        quantidade = self.__df['Quantidade'].fillna(0)
        preco_unitario = self.__df['Preço Unitário'].fillna(0)
        nulo = self.__df['Valor Total'].isna()

        calculo = quantidade * preco_unitario

        self.__df.loc[nulo,'Valor Total'] = calculo

