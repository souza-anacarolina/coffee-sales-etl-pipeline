import os
import pandas as pd
from fpdf import FPDF


class PipelineMetricas:

    def __init__(self, df: pd.DataFrame):
        self.__df = df

    # =========================================================
    # CÁLCULO DAS MÉTRICAS
    # =========================================================

    def valores_agrupados(self) -> pd.DataFrame:
        """
        Retorna o valor total e a quantidade agrupados por produto.
        """

        resultado = self.__df.groupby('Produto').agg({'Quantidade': 'sum', 
                                                      'Valor Total': 'sum'}).reset_index()

        resultado['Valor Total'] = resultado['Valor Total'].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        return resultado

    def faturamento_total(self) -> pd.DataFrame:
        """
        Retorna o valor total de faturamento.
        """

        total = self.__df['Valor Total'].sum()

        return pd.DataFrame([{'Métrica': 'Faturamento Total', 'Valor': f'R$ {total:,.2f}'}])

    def faturamento_por_forma_de_pagamento(self) -> pd.DataFrame:
        """
        Retorna o total gasto e quantidade por forma de pagamento.
        """

        resultado = self.__df.groupby('Forma de Pagamento').agg({'Valor Total': 'sum', 
                                                                 'Cod_Transacao': 'count'}).rename(columns={'Valor Total': 'Faturamento Total', 
                                                                                                            'Cod_Transacao': 'Quantidade de Transações'}).reset_index()

        resultado['Faturamento Total'] = resultado['Faturamento Total'].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        return resultado

    def ticket_medio(self) -> pd.DataFrame:
        """
        Retorna o valor médio gasto por venda.
        """

        valor_total = self.__df['Valor Total'].sum()

        total_transacoes = self.__df['Cod_Transacao'].nunique()

        media = valor_total / total_transacoes if total_transacoes > 0 else 0

        return pd.DataFrame([{'Métrica': 'Ticket Médio', 'Valor': f'R$ {media:,.2f}'}])

    def total_transacoes(self) -> pd.DataFrame:
        """
        Retorna a quantidade total de transações.
        """

        total = self.__df['Cod_Transacao'].nunique()

        return pd.DataFrame([{'Métrica': 'Total Transações', 'Valor': total}])

    def faturamento_por_tipo_de_consumo(self) -> pd.DataFrame:
        """
        Retorna a proporção do faturamento entre os tipos de consumo.
        """

        resultado = self.__df.groupby('Tipo de Consumo').agg({'Valor Total': 'sum', 
                                                              'Cod_Transacao': 'count'}).rename(columns={'Valor Total': 'Faturamento Total', 
                                                                                                         'Cod_Transacao': 'Quantidade de Transações'}).reset_index()

        resultado['Faturamento Total'] = resultado['Faturamento Total'].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        return resultado

    def analise_temporal_de_vendas(self) -> pd.DataFrame:
        """
        Retorna as vendas agrupadas por dia da semana.
        """

        df_temp = self.__df.copy()

        df_temp['Data da Transação'] = pd.to_datetime(df_temp['Data da Transação'])

        dias = {
            'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }

        ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

        df_temp['Dia_Semana'] = df_temp['Data da Transação'].dt.day_name().map(dias)

        resultado = df_temp.groupby('Dia_Semana')['Valor Total'].sum().reindex(ordem_dias).reset_index()

        resultado['Valor Total'] = resultado['Valor Total'].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        return resultado

    def obter_todas_metricas(self) -> dict:
        """
        Dicionário com o nome da métrica e o seu respectivo DataFrame.
        """

        return {
            'Faturamento Agrupado Por Produto': self.valores_agrupados(),
            'Faturamento Total': self.faturamento_total(),
            'Faturamento Por Forma Pagamento': self.faturamento_por_forma_de_pagamento(),
            'Ticket Médio': self.ticket_medio(),
            'Total Transações': self.total_transacoes(),
            'Faturamento Por Tipo Consumo': self.faturamento_por_tipo_de_consumo(),
            'Análise Temporal': self.analise_temporal_de_vendas()
        }

    # =========================================================
    # GERAÇÃO E EXPORTAÇÃO DOS RELATÓRIOS
    # =========================================================

    def exportar_csvs_separados(self, pasta_destino: str):
        """
        Gera um arquivo CSV individual para cada métrica.
        """

        os.makedirs(pasta_destino, exist_ok=True)
        metricas = self.obter_todas_metricas()

        for nome, df in metricas.items():
            nome_arquivo = nome.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o')
            path = os.path.join(pasta_destino, f'{nome_arquivo}.csv')
            df.to_csv(path, index=False, encoding='utf-8-sig', sep=';', decimal=',')

        print(f"CSVs individuais salvos em: {pasta_destino}")

    def exportar_excel_totalizador(self, path_arquivo: str):
        """
        Gera um arquivo Excel (.xlsx) onde cada aba corresponde a uma métrica.
        """

        os.makedirs(os.path.dirname(path_arquivo), exist_ok=True)
        metricas = self.obter_todas_metricas()

        with pd.ExcelWriter(path_arquivo, engine='openpyxl') as writer:
            for nome_aba, df in metricas.items():
                df.to_excel(writer, sheet_name=nome_aba[:31], index=False)

        print(f"Arquivo Excel com todas as métricas salvo em: {path_arquivo}")

    def exportar_pdfs_separados(self, pasta_destino: str):
        """
        Gera um arquivo PDF individual para cada métrica.
        """

        os.makedirs(pasta_destino, exist_ok=True)
        metricas = self.obter_todas_metricas()

        for nome, df in metricas.items():

            nome_arquivo = nome.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o')

            path = os.path.join(pasta_destino, f'{nome_arquivo}.pdf')

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", style="B", size=14)
            pdf.cell(0, 10, f"Métrica: {nome}", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.ln(5)

            pdf.set_font("Helvetica", size=9)

            largura_coluna = int(190 / max(len(df.columns), 1))

            with pdf.table(col_widths=tuple([largura_coluna] * len(df.columns))) as table:
                header_row = table.row()
                for col in df.columns:
                    header_row.cell(str(col))

                for _, row in df.iterrows():
                    data_row = table.row()
                    for val in row:
                        val_str = f"R$ {val:,.2f}" if isinstance(val, (float, int)) and 'Valor' in str(val) else str(val)
                        data_row.cell(val_str)

            pdf.output(path)
        print(f"PDFs individuais salvos em: {pasta_destino}")

    def exportar_pdf_totalizador(self, path_arquivo: str):
        """
        Gera um único PDF com todas as métricas separadas por títulos.
        """

        os.makedirs(os.path.dirname(path_arquivo), exist_ok=True)
        metricas = self.obter_todas_metricas()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(0, 10, "Relatório Geral de Métricas", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)

        for nome, df in metricas.items():
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.cell(0, 8, f"- {nome}", new_x="LMARGIN", new_y="NEXT", align="L")
            pdf.ln(2)

            pdf.set_font("Helvetica", size=9)
            largura_coluna = int(190 / max(len(df.columns), 1))

            with pdf.table(col_widths=tuple([largura_coluna] * len(df.columns))) as table:
                header_row = table.row()
                for col in df.columns:
                    header_row.cell(str(col))

                for _, row in df.iterrows():
                    data_row = table.row()
                    for val in row:
                        val_str = f"R$ {val:,.2f}" if isinstance(val, (float, int)) and 'Valor' in str(val) else str(val)
                        data_row.cell(val_str)

            pdf.ln(8)

        pdf.output(path_arquivo)
        print(f"PDF consolidado salvo em: {path_arquivo}")