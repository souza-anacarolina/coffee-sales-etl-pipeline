import csv
import json
from datetime import datetime
import pandas as pd


class Dados:

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

    def retorna_informacao(self, target_column):
            """
            Retorna a data no formato original
            """
    
            return self.__df[target_column].head(5)

    def format_dates(self, target_column):
        """
        Converte datas de YYYY-MM-DD para DD/MM/YYYY.
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
        Cria uma coluna temporária chamada Valor Total Linha
        Agrupa por produto e soma a Quantidade e o Valor Total
        Remove a coluna temporária do DataFrame
        Renomeia a coluna final para Valor Total
        """

        self.__df['Valor Total Linha'] = self.__df['Quantidade'] * self.__df['Preço Unitário']
        
        resultado = self.__df.groupby('Produto').agg({'Quantidade': 'sum',
            'Valor Total Linha': 'sum'}).reset_index()
        
        self.__df.drop(columns=['Valor Total Linha'], inplace=True)
        
        resultado.rename(columns={'Valor Total Linha': 'Valor Total'}, inplace=True)
        
        return resultado

    # =========================================================
    # SALVAMENTO
    # =========================================================

    def salvando_dados(self, path):
        """
        Salva o DataFrame em um arquivo CSV.
        """

        self.__df.to_csv(path,index=False,encoding='utf-8-sig',date_format='%d/%m/%Y')

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

        return self.__df.isna().sum()

    def tratamento_nulos(self):
        """
        Preenche valores nulos com valores padrão.
        """

        valores_padrao = {
            'Cod_Transacao': 'NÃO INFORMADO',
            'Produto': 'NÃO INFORMADO',
            'Quantidade': 0,
            'Preço Unitário': 0.0,
            'Valor Total': 0.0,
            'Forma de Pagamento': 'NÃO INFORMADO',
            'Tipo de Consumo': 'NÃO INFORMADO'
        }
        self.__df.fillna(value=valores_padrao,inplace=True)
