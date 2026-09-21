import os
from typing import Optional
import pandas as pd
from fpdf import FPDF


class PipelineMetricas:

    def __init__(
            self, 
            df: pd.DataFrame,
            total_bruto: 'int | None' = None, 
            qtde_quarentena: 'int | None' = None,
            ):

        """
            Parameters
            ----------
            df:
                DataFrame já tratado pelo pipeline de ETL.
            total_bruto:
                Opcional. Total de registros antes da separação em quarentena —
                usado apenas por `indice_qualidade_dados()`. 
            qtde_quarentena:
                Opcional. Quantidade de registros isolados em quarentena.
            """
        
        self.__df = df
        self.__total_bruto = total_bruto
        self.__qtde_quarentena = qtde_quarentena

    @staticmethod
    def __formatar_valor_celula(nome_coluna: str, valor) -> str:
        """
        Formata células para exibição em PDF.
        """
        return str(valor)

    @staticmethod
    def __formatar_moeda(serie: pd.Series) -> pd.Series:
        """Formata uma série numérica como moeda em padrão brasileiro (R$ 1.234,56)."""
        return serie.map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def __mascara_preenchida(self, coluna: pd.Series) -> pd.Series:
        """
        Retorna a máscara de valores genuinamente preenchidos em uma coluna
        de dimensão 
        """
        return coluna.notna() & (coluna != 'N/A')

    def __coluna_disponivel(self, coluna: str) -> bool:
        """Verifica se uma coluna existe e tem ao menos um valor não nulo."""
        return coluna in self.__df.columns and self.__df[coluna].notna().any()

    @staticmethod
    def __aviso_indisponivel(motivo: str) -> pd.DataFrame:
        """Retorna uma métrica 'vazia' com uma explicação, em vez de quebrar o pipeline."""
        return pd.DataFrame([{'Aviso': motivo}])

    def __linha_cobertura(self, coluna_categoria: str, coluna_grupo: str) -> dict:
        """
        Monta uma linha de rodapé indicando qual % do faturamento total uma
        métrica agrupada por `coluna_grupo` de fato cobre. Usada nas
        métricas que dependem de uma coluna disponível em apenas uma das
        fontes de dados.
        """
        mascara = self.__mascara_preenchida(self.__df[coluna_grupo])
        faturamento_coberto = self.__df.loc[mascara, 'Valor Total'].sum()
        faturamento_total = self.__df['Valor Total'].sum()
        pct = (faturamento_coberto / faturamento_total * 100) if faturamento_total else 0
 
        if 'Origem' in self.__df.columns:
            fontes = sorted(self.__df.loc[mascara, 'Origem'].dropna().unique())
            descricao_fonte = f"disponível apenas em: {', '.join(fontes)}" if fontes else "fonte não identificada"
        else:
            descricao_fonte = "dado parcialmente preenchido"
 
        return {
            coluna_categoria: '[!] Cobertura desta métrica',
            'Faturamento Total': f"{pct:.1f}% do faturamento total ({descricao_fonte})",
        }

    # =========================================================
    # CÁLCULO DAS MÉTRICAS
    # =========================================================

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

        if not self.__coluna_disponivel('Forma de Pagamento'):
            return self.__aviso_indisponivel(
                'Sem dados de forma de pagamento disponíveis (coluna Forma de Pagamento ausente ou vazia).'
            )
 
        df_filtrado = self.__df[self.__mascara_preenchida(self.__df['Forma de Pagamento'])]
 
        resultado = df_filtrado.groupby('Forma de Pagamento').agg(
            **{
                'Faturamento Total': ('Valor Total', 'sum'),
                'Quantidade de Transações': ('Cod_Transacao', 'count'),
            }
        ).reset_index()
 
        resultado['Faturamento Total'] = self.__formatar_moeda(resultado['Faturamento Total'])
 
        linha_cobertura = self.__linha_cobertura('Forma de Pagamento', 'Forma de Pagamento')
        return pd.concat([resultado, pd.DataFrame([linha_cobertura])], ignore_index=True)

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

        if not self.__coluna_disponivel('Tipo de Consumo'):
            return self.__aviso_indisponivel(
                'Sem dados de tipo de consumo disponíveis (coluna Tipo de Consumo ausente ou vazia).'
            )
 
        df_filtrado = self.__df[self.__mascara_preenchida(self.__df['Tipo de Consumo'])]
 
        resultado = df_filtrado.groupby('Tipo de Consumo').agg(
            **{
                'Faturamento Total': ('Valor Total', 'sum'),
                'Quantidade de Transações': ('Cod_Transacao', 'count'),
            }
        ).reset_index()
 
        resultado['Faturamento Total'] = self.__formatar_moeda(resultado['Faturamento Total'])
 
        linha_cobertura = self.__linha_cobertura('Tipo de Consumo', 'Tipo de Consumo')
        return pd.concat([resultado, pd.DataFrame([linha_cobertura])], ignore_index=True)

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

    def media_itens_por_transacao(self):
        """
        Retorna a quantidade média de produtos levados em uma única transação
        """

        produtos_por_transacao = self.__df.groupby('Cod_Transacao')['Quantidade'].sum()

        resultado = int(produtos_por_transacao.mean())

        return pd.DataFrame([{'Métrica': 'Média de itens por compra', 'Valor': resultado}])

    def perc_nulos_por_coluna(self):
            """
            Retorna o percentual de dados nulos de cada coluna do DataFrame
            """
    
            resultado = (self.__df.isna().mean() * 100).reset_index()
    
            resultado.columns = ['Coluna', 'Porcentagem Nulos']

            resultado['Porcentagem Nulos'] = resultado['Porcentagem Nulos'].map(lambda x: f"{x:.2f}%")
    
            return resultado

    def cont_reg_duplicados(self):
        """
        Retorna um DataFrame com a contagem total de linhas duplicadas.
        """
        total_duplicados = self.__df.duplicated(subset=['Cod_Transacao', 'Origem', 'Produto']).sum()
        
        resultado = pd.DataFrame([{
            'Métrica': 'Total de Registros Duplicados',
            'Valor': total_duplicados
        }])
        
        return resultado

    # =========================================================
    # MÉTRICAS DE NEGÓCIO 
    # =========================================================

    def faturamento_por_loja(self) -> pd.DataFrame:
        """
        Faturamento, quantidade de transações e ticket médio por loja.
 
        Decisão de negócio que apoia: identificar as lojas de melhor e pior
        desempenho — para replicar o que funciona bem em uma unidade, ou
        investigar quedas de faturamento numa unidade específica.
        """
        if not self.__coluna_disponivel('Localizacao_Loja'):
            return self.__aviso_indisponivel(
                'Sem dados de loja disponíveis (coluna Localizacao_Loja ausente ou vazia).'
            )
 
        resultado = self.__df.groupby('Localizacao_Loja').agg(
            **{
                'Faturamento Total': ('Valor Total', 'sum'),
                'Quantidade de Transações': ('Cod_Transacao', 'nunique'),
            }
        ).reset_index()
 
        resultado['Ticket Médio'] = resultado['Faturamento Total'] / resultado['Quantidade de Transações']
        resultado = resultado.sort_values('Faturamento Total', ascending=False).reset_index(drop=True)
 
        resultado['Faturamento Total'] = self.__formatar_moeda(resultado['Faturamento Total'])
        resultado['Ticket Médio'] = self.__formatar_moeda(resultado['Ticket Médio'])
 
        return resultado.rename(columns={'Localizacao_Loja': 'Loja'})

    def faturamento_por_categoria_produto(self) -> pd.DataFrame:
        """
        Faturamento e quantidade vendida por categoria de produto ordenado do maior para o menor.
 
        Decisão de negócio que apoia: definir o mix de produtos a priorizar
        em compras/estoque e em promoções, e identificar categorias com
        baixa representatividade que podem ser descontinuadas.
        """
        if not self.__coluna_disponivel('Categoria do Produto'):
            return self.__aviso_indisponivel(
                'Sem dados de categoria de produto disponíveis '
                '(coluna Categoria do Produto ausente ou vazia).'
            )
 
        resultado = self.__df.groupby('Categoria do Produto').agg(
            **{
                'Faturamento Total': ('Valor Total', 'sum'),
                'Quantidade Vendida': ('Quantidade', 'sum'),
            }
        ).reset_index()
 
        total_geral = resultado['Faturamento Total'].sum()
        resultado['% do Faturamento'] = (resultado['Faturamento Total'] / total_geral * 100).round(1)
        resultado = resultado.sort_values('Faturamento Total', ascending=False).reset_index(drop=True)
 
        resultado['Faturamento Total'] = self.__formatar_moeda(resultado['Faturamento Total'])
        resultado['% do Faturamento'] = resultado['% do Faturamento'].map(lambda x: f"{x:.1f}%")
 
        return resultado

    def ranking_produtos_mais_vendidos(self, top_n: int = 10) -> pd.DataFrame:
        """
        Top N produtos por quantidade vendida, com faturamento associado.
 
        Decisão de negócio que apoia: priorização de estoque/insumos dos
        produtos de maior giro, e identificação de candidatos a combo/
        promoção cruzada com itens de menor saída.
        """
        coluna_produto = 'Detalhe do Produto' if self.__coluna_disponivel('Detalhe do Produto') else 'Produto'
 
        if not self.__coluna_disponivel(coluna_produto):
            return self.__aviso_indisponivel('Sem dados de produto disponíveis para ranquear.')
 
        resultado = self.__df.groupby(coluna_produto).agg(
            **{
                'Quantidade Vendida': ('Quantidade', 'sum'),
                'Faturamento Total': ('Valor Total', 'sum'),
            }
        ).reset_index()
 
        resultado = resultado.sort_values('Quantidade Vendida', ascending=False).head(top_n).reset_index(drop=True)
        resultado.insert(0, 'Ranking', range(1, len(resultado) + 1))
        resultado['Faturamento Total'] = self.__formatar_moeda(resultado['Faturamento Total'])
 
        return resultado.rename(columns={coluna_produto: 'Produto'})

    def vendas_por_faixa_horaria(self) -> pd.DataFrame:
        """
        Faturamento e quantidade de transações por hora do dia.
 
        Decisão de negócio que apoia: dimensionamento de equipe por horário
        de pico, definição de horário de funcionamento e janelas ideais
        para promoções fora do horário de pico.
        """
        if not self.__coluna_disponivel('Hora da Transação'):
            return self.__aviso_indisponivel(
                'Sem dados de horário disponíveis (coluna Hora da Transação ausente ou vazia).'
            )
 
        df_temp = self.__df.copy()
        df_temp['Hora'] = pd.to_datetime(
            df_temp['Hora da Transação'], format='%H:%M:%S', errors='coerce'
        ).dt.hour
        df_temp = df_temp.dropna(subset=['Hora'])
 
        resultado = df_temp.groupby('Hora').agg(
            **{
                'Faturamento Total': ('Valor Total', 'sum'),
                'Quantidade de Transações': ('Cod_Transacao', 'nunique'),
            }
        ).reset_index().sort_values('Hora')
 
        resultado['Hora'] = resultado['Hora'].astype(int).map(lambda h: f"{h:02d}h")
        resultado['Faturamento Total'] = self.__formatar_moeda(resultado['Faturamento Total'])
 
        return resultado.reset_index(drop=True)

    def indice_qualidade_dados(self) -> pd.DataFrame:
        """
        Indicadores sobre a confiabilidade dos dados usados nas demais
        métricas: quanto foi descartado em quarentena, quanto teve valor
        derivado/imputado em vez de vindo diretamente da fonte, e a
        participação de cada fonte de dados no total.
 
        Decisão de negócio que apoia: dimensionar o quanto confiar nos
        números acima antes de agir sobre eles — e, do lado de engenharia,
        apontar onde vale investir para melhorar a captura de dados na
        origem (ex.: uma fonte com muito valor imputado tem um problema de
        qualidade que vale corrigir antes da próxima carga).
        """
        linhas = []
 
        if self.__total_bruto:
            qtde_quarentena = self.__qtde_quarentena or 0
            pct_quarentena = qtde_quarentena / self.__total_bruto * 100
            linhas.append({
                'Indicador': 'Registros descartados em quarentena',
                'Valor': f"{qtde_quarentena} ({pct_quarentena:.2f}% do total bruto)",
            })
 
        if 'valor_imputado' in self.__df.columns:
            pct_imputado = self.__df['valor_imputado'].mean() * 100
            linhas.append({
                'Indicador': 'Registros com Valor Total imputado/derivado',
                'Valor': f"{pct_imputado:.2f}%",
            })
 
        if 'Origem' in self.__df.columns:
            participacao = self.__df['Origem'].value_counts(normalize=True).mul(100).round(2)
            for origem, pct in participacao.items():
                linhas.append({'Indicador': f'Participação da fonte "{origem}"', 'Valor': f"{pct:.2f}%"})
 
        if not linhas:
            return self.__aviso_indisponivel(
                'Sem informações de qualidade disponíveis (instancie PipelineMetricas '
                'com total_bruto/qtde_quarentena para o indicador de quarentena).'
            )
 
        return pd.DataFrame(linhas)

    def obter_metricas_negocio(self) -> dict:
        """
        Métricas voltadas para decisão de negócio: faturamento, produto,
        loja, horário. Público-alvo: gestores e áreas de negócio.
        """
        return {
            'Faturamento Total': self.faturamento_total(),
            'Ticket Médio': self.ticket_medio(),
            'Total Transações': self.total_transacoes(),
            'Faturamento Por Loja': self.faturamento_por_loja(),
            'Faturamento Por Categoria de Produto': self.faturamento_por_categoria_produto(),
            'Ranking de Produtos Mais Vendidos': self.ranking_produtos_mais_vendidos(),
            'Análise Temporal': self.analise_temporal_de_vendas(),
            'Vendas Por Faixa Horária': self.vendas_por_faixa_horaria(),
            'Média de Itens por Compra': self.media_itens_por_transacao(),
            'Faturamento Por Forma Pagamento': self.faturamento_por_forma_de_pagamento(),
            'Faturamento Por Tipo Consumo': self.faturamento_por_tipo_de_consumo(),
        }

    def obter_metricas_qualidade(self) -> dict:
        """
        Métricas de observabilidade do pipeline de dados. Público-alvo: o
        time de dados/engenharia
        """
        return {
            'Índice de Qualidade dos Dados': self.indice_qualidade_dados(),
            'Percentual de Nulos por Coluna': self.perc_nulos_por_coluna(),
            'Contagem de Registros Duplicados': self.cont_reg_duplicados(),
        }

    def obter_todas_metricas(self) -> dict:
        """
        Combina métricas de negócio e de qualidade em um só dicionário.
        Uso interno/depuração.
        """
        return {**self.obter_metricas_negocio(), **self.obter_metricas_qualidade()}
    

    # =========================================================
    # GERAÇÃO E EXPORTAÇÃO DOS RELATÓRIOS
    # =========================================================

    def exportar_csvs_separados(self, pasta_destino: str, metricas: Optional[dict] = None):
        """
        Gera um arquivo CSV individual para cada métrica.
        """

        os.makedirs(pasta_destino, exist_ok=True)
        metricas = metricas if metricas is not None else self.obter_todas_metricas()

        for nome, df in metricas.items():
            nome_arquivo = nome.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o')
            path = os.path.join(pasta_destino, f'{nome_arquivo}.csv')
            df.to_csv(path, index=False, encoding='utf-8-sig', sep=';', decimal=',')

        print(f"CSVs individuais salvos em: {pasta_destino}")

    def exportar_excel_totalizador(self, path_arquivo: str, metricas: Optional[dict] = None):
        """
        Gera um arquivo Excel (.xlsx) onde cada aba corresponde a uma métrica.
        """

        os.makedirs(os.path.dirname(path_arquivo), exist_ok=True)
        metricas = metricas if metricas is not None else self.obter_todas_metricas()

        with pd.ExcelWriter(path_arquivo, engine='openpyxl') as writer:
            for nome_aba, df in metricas.items():
                df.to_excel(writer, sheet_name=nome_aba[:31], index=False)

        print(f"Arquivo Excel com todas as métricas salvo em: {path_arquivo}")

    def exportar_pdfs_separados(self, pasta_destino: str, metricas: Optional[dict] = None):
        """
        Gera um arquivo PDF individual para cada métrica.
        """

        os.makedirs(pasta_destino, exist_ok=True)
        metricas = metricas if metricas is not None else self.obter_todas_metricas()

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
                    for coluna, val in row.items():
                        data_row.cell(self.__formatar_valor_celula(coluna, val))

            pdf.output(path)
        print(f"PDFs individuais salvos em: {pasta_destino}")

    def exportar_pdf_totalizador(self, path_arquivo: str, titulo: str = "Relatório Geral de Métricas",
        metricas: Optional[dict] = None,):
        """
        Gera um único PDF com todas as métricas separadas por títulos.
        """

        os.makedirs(os.path.dirname(path_arquivo), exist_ok=True )
        metricas = metricas if metricas is not None else self.obter_todas_metricas()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(0, 10, titulo, new_x="LMARGIN", new_y="NEXT", align="C")
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
                    for coluna, val in row.items():
                        data_row.cell(self.__formatar_valor_celula(coluna, val))

            pdf.ln(8)

        pdf.output(path_arquivo)
        print(f"PDF consolidado salvo em: {path_arquivo}")