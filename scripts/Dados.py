import json
import logging
import os
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence, Union, cast

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

FORMATOS_SUPORTADOS = {
    '.csv': 'csv',
    '.json': 'json',
    '.xlsx': 'excel',
    '.xls': 'excel',
}


class Dados:

    pd.options.display.float_format = 'R$ {:,.2f}'.format

    def __init__(
        self,
        path: Optional[Union[str, list]] = None,
        tipo_dados: Optional[str] = None,
        df: Optional[pd.DataFrame] = None,
    ):
        self.__path = path
        self.__tipo_dados = tipo_dados or self.__detectar_tipo(path)
        self.__df = df.copy() if df is not None else self.__leitura_dados()

    # =========================================================
    # DETECÇÃO AUTOMÁTICA DE FORMATO
    # =========================================================

    @staticmethod
    def __detectar_tipo(path) -> Optional[str]:
        """Detecta o tipo de leitura a partir da extensão do arquivo."""
        if not isinstance(path, str):
            return None
        extensao = Path(path).suffix.lower()
        return FORMATOS_SUPORTADOS.get(extensao)

    # =========================================================
    # PROPRIEDADES DE ACESSO
    # =========================================================

    @property
    def dados(self) -> pd.DataFrame:
        """Retorna o DataFrame."""
        return self.__df

    @property
    def nomes_colunas(self) -> list:
        """Retorna os nomes das colunas."""
        return list(self.__df.columns)

    @property
    def path(self):
        """Retorna o caminho de origem dos dados."""
        return self.__path

    @property
    def tipo_dados(self) -> Optional[str]:
        """Retorna o tipo de leitura utilizado"""
        return self.__tipo_dados

    # =========================================================
    # LEITURA DOS DADOS
    # =========================================================

    def __path_como_arquivo(self) -> str:
        
        if not isinstance(self.__path, str):
            raise TypeError(
                f"Esperava um caminho de arquivo (str) para tipo_dados="
                f"'{self.__tipo_dados}', recebeu {type(self.__path)}."
            )
        return self.__path

    def __leitura_json(self) -> pd.DataFrame:
        with open(self.__path_como_arquivo(), 'r', encoding='utf-8') as file:
            return pd.DataFrame(json.load(file))
 
    def __leitura_csv(self) -> pd.DataFrame:
        return pd.read_csv(self.__path_como_arquivo(), encoding='utf-8')

    def __leitura_excel(self) -> pd.DataFrame:
        return pd.read_excel(self.__path)

    def __leitura_lista(self) -> pd.DataFrame:
        if not isinstance(self.__path, list):
            raise TypeError(
                f'Tipo de dado incorreto: esperava uma lista, recebeu {type(self.__path)}'
            )
        dados = self.__path
        self.__path = 'lista em memória'
        return pd.DataFrame(dados)

    def __leitura_dados(self) -> pd.DataFrame:
        leitores = {
            'csv': self.__leitura_csv,
            'json': self.__leitura_json,
            'excel': self.__leitura_excel,
            'list': self.__leitura_lista,
        }
 
        if self.__tipo_dados is None:
            raise ValueError(
                "Não foi possível detectar o tipo de leitura automaticamente "
                f"a partir de '{self.__path}'. Informe `tipo_dados` explicitamente "
                f"(um de {sorted(leitores)}) ou use uma extensão suportada: "
                f"{sorted(FORMATOS_SUPORTADOS)}."
            )
 
        leitor = leitores.get(self.__tipo_dados)
 
        if leitor is None:
            raise ValueError(
                f"Tipo de arquivo não suportado: '{self.__tipo_dados}'. "
                f"Suportados: {sorted(leitores)} "
                f"(ou uma das extensões {sorted(FORMATOS_SUPORTADOS)} com detecção automática)."
            )
 
        logger.info("Lendo dados (%s) de: %s", self.__tipo_dados, self.__path)
        df = leitor()
        logger.info("Registros lidos: %d | Colunas: %s", len(df), list(df.columns))
        return df

    def qtde_registros(self) -> int:
        """Retorna a quantidade de registros carregados."""
        return len(self.__df)

    # =========================================================
    # UNIÃO DE MÚLTIPLAS FONTES (esquemas diferentes)
    # =========================================================

    @classmethod
    def unir_fontes(
        cls,
        fontes: Mapping[str, "Dados"],
        coluna_origem: str = 'Origem',
    ) -> "Dados":
        
        if not fontes:
            raise ValueError('É necessário informar ao menos uma fonte para unir.')

        partes = []
        for rotulo, fonte in fontes.items():
            parte = fonte.dados.copy()
            parte[coluna_origem] = rotulo
            partes.append(parte)

        df_unificado = pd.concat(partes, ignore_index=True, sort=False)

        colunas_por_fonte = {rotulo: fonte.nomes_colunas for rotulo, fonte in fontes.items()}
        logger.info(
            "Fontes unidas: %s | Registros totais: %d | Colunas finais: %d",
            list(fontes), len(df_unificado), len(df_unificado.columns),
        )
        logger.debug("Colunas por fonte: %s", colunas_por_fonte)

        return cls(df=df_unificado)

    # =========================================================
    # TRANSFORMAÇÃO DOS DADOS
    # =========================================================

    def rename_columns(self, key_mapping: Mapping[str, str]) -> "Dados":
        """
        Renomeia as colunas do DataFrame.
        """
        mapeamento_aplicavel = {k: v for k, v in key_mapping.items() if k in self.__df.columns}
        self.__df.rename(columns=mapeamento_aplicavel, inplace=True)
        return self

    _TIPOS_NUMERICOS = {'Int8', 'Int16', 'Int32', 'Int64', 'Float32', 'Float64'}

    def cast_types(self, cast_mapping: Mapping[str, str]) -> "Dados":
        """
        Converte o tipo de dado das colunas para os tipos nullable do pandas.
        """
        for coluna, tipo in cast_mapping.items():
            if coluna not in self.__df.columns:
                continue
 
            if tipo in self._TIPOS_NUMERICOS:
                self.__df[coluna] = pd.to_numeric(self.__df[coluna], errors='coerce').astype(cast(Any, tipo))
            elif tipo.startswith('datetime64'):
                self.__df[coluna] = pd.to_datetime(self.__df[coluna], errors='coerce')
            else:
                self.__df[coluna] = self.__df[coluna].astype(cast(Any, tipo))
 
        return self

    def retorna_data_formatada(self, target_column: str) -> str:
        """Retorna a data formatada para o padrão brasileiro."""
        return self.__df[target_column].dt.strftime('%d/%m/%Y').to_string()

    def retorna_data_original(self, target_column: str) -> str:
        """Retorna a data original dos dados."""
        return self.__df[target_column].to_string()

    def format_dates(self, target_column: str) -> "Dados":
        """Converte os valores da coluna para o tipo datetime."""
        if target_column in self.__df.columns:
            self.__df[target_column] = pd.to_datetime(self.__df[target_column], errors='coerce')
        return self

    def deduplicate(self, subset: Optional[Sequence[str]] = None) -> pd.DataFrame:
        """
        Localiza registros cuja chave (por padrão, ``Cod_Transacao`` + ``Origem`` + ``Produto``) esteja
        informada mais de uma vez. 
        """
        subset = self.__subset_existente(subset or ['Cod_Transacao', 'Origem', 'Produto'])
        duplicadas = self.__df.duplicated(subset=subset, keep=False)
        return self.__df[duplicadas]

    def drop_deduplicate(self, subset: Optional[Sequence[str]] = None) -> "Dados":
        """
        Remove as duplicadas mantendo a primeira ocorrência, considerando por
        padrão a chave ``Cod_Transacao`` + ``Origem`` + ``Produto``.
        """
        subset = self.__subset_existente(subset or ['Cod_Transacao', 'Origem', 'Produto'])
        antes = len(self.__df)
        self.__df = self.__df.drop_duplicates(subset=subset, keep='first')
        removidos = antes - len(self.__df)
        if removidos:
            logger.info("Registros duplicados removidos (chave=%s): %d", subset, removidos)
        return self

    def standardize_text(self) -> "Dados":
        """Remove espaços extras e converte colunas de texto para maiúsculo."""
        text_columns = self.__df.select_dtypes(include=['object', 'string']).columns
        self.__df[text_columns] = self.__df[text_columns].apply(
            lambda coluna: coluna.str.strip().str.upper()
        )
        return self

    def __subset_existente(self, subset: Sequence[str]) -> list:
        """Filtra `subset` mantendo apenas colunas que existem no DataFrame."""
        existentes = [c for c in subset if c in self.__df.columns]
        if not existentes:
            raise KeyError(
                f"Nenhuma das colunas informadas em subset={list(subset)} existe no DataFrame.")
        return existentes

    # =========================================================
    # SALVAMENTO
    # =========================================================

    @staticmethod
    def __garantir_diretorio(path: str) -> None:
        diretorio = os.path.dirname(path)
        if diretorio:
            os.makedirs(diretorio, exist_ok=True)

    def salvando_dados_virgula(self, path: str) -> None:
        """Salva o DataFrame em um arquivo CSV separado por vírgula."""
        self.__garantir_diretorio(path)
        self.__df.to_csv(
            path, index=False, encoding='utf-8-sig', float_format='%.2f', date_format='%d/%m/%Y'
        )
        logger.info("Dados salvos (CSV, vírgula): %s", path)

    def salvando_dados_ponto_virgula(self, path: str) -> None:
        """Salva o DataFrame em um arquivo CSV separado por ponto e vírgula."""
        self.__garantir_diretorio(path)
        self.__df.to_csv(
            path, index=False, encoding='utf-8-sig', sep=';', decimal=',',
            float_format='%.2f', date_format='%d/%m/%Y',
        )
        logger.info("Dados salvos (CSV, ponto e vírgula): %s", path)

    def salvando_dados_json(self, path: str) -> None:
        """Salva o DataFrame em um arquivo JSON."""
        self.__garantir_diretorio(path)
        self.__df.to_json(path, orient='records', force_ascii=False, indent=4)
        logger.info("Dados salvos (JSON): %s", path)

    def salvando_dados_excel(self, path: str) -> None:
        """Salva o DataFrame em um arquivo Excel (.xlsx)."""
        self.__garantir_diretorio(path)
        self.__df.to_excel(path, index=False)
        logger.info("Dados salvos (Excel): %s", path)

    # =========================================================
    # TRATAMENTO DE VALORES AUSENTES
    # =========================================================

    def missing_invalid_values(self) -> list:
        """Retorna a lista de textos tratados como valor ausente disfarçado."""
        return ['UNKNOWN', 'unknown', 'error', 'ERROR', 'n/a', 'N/A', 'nan']

    def clean_missing_values(self) -> str:
        """Converte valores considerados inválidos em nulos reconhecidos pelo pandas."""
        self.__df.replace(self.missing_invalid_values(), pd.NA, inplace=True)
        return self.valores_nulos()

    def valores_nulos(self) -> str:
        """Retorna a quantidade de valores nulos por coluna."""
        return self.__df.isna().sum().to_string()

    # =========================================================
    # REGRAS DE NEGÓCIO
    # =========================================================

    def valores_padrao(self) -> "Dados":
        """
        Define valores padrão para dados nulos em campos descritivos (dimensões)
        e deriva/marca valores ausentes em campos de medida (fatos).
        """
        colunas_dimensao = ['Produto', 'Forma de Pagamento', 'Tipo de Consumo']
        for coluna in colunas_dimensao:
            if coluna in self.__df.columns:
                self.__df[coluna] = self.__df[coluna].fillna('N/A')

        if 'valor_imputado' not in self.__df.columns:
            self.__df['valor_imputado'] = False

        colunas_fato = {'Valor Total', 'Quantidade', 'Preço Unitário'}
        if colunas_fato.issubset(self.__df.columns):
            total_nulo = self.__df['Valor Total'].isna()
            quantidade_ok = self.__df['Quantidade'].notna()
            preco_ok = self.__df['Preço Unitário'].notna()

            # Caso 1: deriva Valor Total quando possível (Quantidade x Preço)
            pode_derivar = total_nulo & quantidade_ok & preco_ok
            self.__df.loc[pode_derivar, 'Valor Total'] = (
                self.__df.loc[pode_derivar, 'Quantidade'] * self.__df.loc[pode_derivar, 'Preço Unitário']
            )

            # Caso 2: não derivável — Valor Total permanece nulo de propósito
            nao_derivavel = total_nulo & ~pode_derivar
            self.__df.loc[nao_derivavel, 'valor_imputado'] = True

            # Caso 3: Quantidade ou Preço ausentes isoladamente
            quantidade_nulo = self.__df['Quantidade'].isna()
            preco_nulo = self.__df['Preço Unitário'].isna()
            self.__df.loc[quantidade_nulo | preco_nulo, 'valor_imputado'] = True

        return self

    def separar_quarentena(self) -> "Dados":
        """
        Isola registros que comprometem a integridade do grão da tabela fato
        (hoje: ausência de data da transação).
        """
        self.__df['is_valid'] = True
        self.__df['quality_issues'] = [[] for _ in range(len(self.__df))]

        if 'Data da Transação' in self.__df.columns:
            sem_data = self.__df['Data da Transação'].isna()
            self.__df.loc[sem_data, 'is_valid'] = False
            self.__df.loc[sem_data, 'quality_issues'] = self.__df.loc[sem_data, 'quality_issues'].apply(
                lambda issues: issues + ['data_ausente']
            )

        self.__df_quarentena = self.__df[~self.__df['is_valid']].copy()
        self.__df = self.__df[self.__df['is_valid']].copy()
        logger.info(
            "Quarentena: %d registro(s) isolado(s) | %d seguem no fluxo principal",
            len(self.__df_quarentena), len(self.__df),
        )
        return self

    @property
    def dados_quarentena(self) -> pd.DataFrame:
        """Retorna os registros isolados por `separar_quarentena`."""
        return getattr(self, '_Dados__df_quarentena', pd.DataFrame())
