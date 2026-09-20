import csv
import json
from datetime import datetime
import pandas as pd
from fpdf import FPDF

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

        return self.__df

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
        Retorna a quantidade de registros carregados
        """

        return len(self.__df)

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
    
            return self.__df[target_column].dt.strftime('%d/%m/%Y').to_string()

    def retorna_data_original(self, target_column):
        """
        Retorna a data original dos dados
        """

        return self.__df[target_column].to_string()

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
        return self.__df.drop_duplicates(keep='first')


    def standardize_text(self):
        """
        Remove os espaços extras e coloca os dados em maiùsculo.
        """
        text_columns = self.__df.select_dtypes(include=['object', 'string']).columns

        self.__df[text_columns] = (self.__df[text_columns].apply(lambda column: column.str.strip().str.upper()))
    

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

    def salvando_dados_json(self,path):
        """
        Salva o DataFrame em um arquivo JSON
        """

        self.__df.to_json(path, orient='records', force_ascii=False, indent=4)


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

    def valores_padrao(self):
        """
        Define valores padrão para dados nulos em campos descritivos (dimensões)
        e deriva/marca valores ausentes em campos de medida (fatos).
        """

        # --- Dimensões ---
        self.__df['Produto'] = self.__df['Produto'].fillna('N/A')
        self.__df['Forma de Pagamento'] = self.__df['Forma de Pagamento'].fillna('N/A')
        self.__df['Tipo de Consumo'] = self.__df['Tipo de Consumo'].fillna('N/A')

        # --- Garante a coluna de flag antes de usá-la ---
        if 'valor_imputado' not in self.__df.columns:
            self.__df['valor_imputado'] = False

        # --- Fatos: nunca preencher com 0 ---
        total_nulo = self.__df['Valor Total'].isna()
        quantidade_ok = self.__df['Quantidade'].notna()
        preco_ok = self.__df['Preço Unitário'].notna()

        # Caso 1: deriva quando possível
        pode_derivar = total_nulo & quantidade_ok & preco_ok
        self.__df.loc[pode_derivar, 'Valor Total'] = (
            self.__df.loc[pode_derivar, 'Quantidade'] * self.__df.loc[pode_derivar, 'Preço Unitário']
        )

        # Caso 2: não derivável — Valor Total permanece NULL de propósito
        nao_derivavel = total_nulo & ~pode_derivar
        self.__df.loc[nao_derivavel, 'valor_imputado'] = True

        # Caso 3: Quantidade ou Preço ausentes isoladamente
        quantidade_nulo = self.__df['Quantidade'].isna()
        preco_nulo = self.__df['Preço Unitário'].isna()
        self.__df.loc[quantidade_nulo | preco_nulo, 'valor_imputado'] = True

    def separar_quarentena(self):
        """
        Isola registros que comprometem a integridade do grão da tabela fato.
        Estes não recebem valor padrão — vão para análise/reprocessamento.
        """
        self.__df['is_valid'] = True
        self.__df['quality_issues'] = [[] for _ in range(len(self.__df))]

        sem_data = self.__df['Data da Transação'].isna()
        self.__df.loc[sem_data, 'is_valid'] = False
        self.__df.loc[sem_data, 'quality_issues'] = self.__df.loc[sem_data, 'quality_issues'].apply(
            lambda x: x + ['data_ausente']
        )

        self.__df_quarentena = self.__df[~self.__df['is_valid']].copy()
        self.__df = self.__df[self.__df['is_valid']].copy()
