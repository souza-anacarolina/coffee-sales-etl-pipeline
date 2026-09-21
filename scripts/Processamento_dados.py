"""
Para adicionar uma nova fonte de dados não é necessário alterar este arquivo — basta incluir a entrada em `config_etl.FONTES_DADOS`.
"""

import logging

from Dados import Dados
from PipelineMetricas import PipelineMetricas
from config_etl import FONTES_DADOS, MAPEAMENTO_COLUNAS, MAPEAMENTO_TIPOS

logger = logging.getLogger(__name__)


def extrair_fontes(fontes_config: list) -> dict:
    """Lê cada fonte configurada e retorna {origem: Dados}."""
    fontes = {}
    for fonte in fontes_config:
        origem, path = fonte['origem'], fonte['path']
        dados = Dados(path)  # tipo detectado automaticamente pela extensão
        logger.info("Fonte '%s' carregada: %d registro(s)", origem, dados.qtde_registros())
        fontes[origem] = dados
    return fontes


def transformar(dados_combinados: Dados) -> Dados:
    """Aplica a cadeia de transformação ao conjunto de dados já unificado."""
    return (
        dados_combinados
        .rename_columns(MAPEAMENTO_COLUNAS)
        .format_dates('Data da Transação'))


def main():
    # 1. EXTRACT 
    fontes = extrair_fontes(FONTES_DADOS)
    total_por_fonte = {origem: d.qtde_registros() for origem, d in fontes.items()}

    dados_compras = Dados.unir_fontes(fontes)
    total_inicial = dados_compras.qtde_registros()

    print(f"\nRegistros por fonte: {total_por_fonte}")
    print(f"Registros brutos combinados: {total_inicial}")

    # 2. TRANSFORM
    dados_compras = transformar(dados_compras)
    dados_compras.clean_missing_values()
    dados_compras.cast_types(MAPEAMENTO_TIPOS)

    # Deduplicação: chave de negócio é Cod_Transacao + Origem + Produto. 
    dados_compras.drop_deduplicate(subset=['Cod_Transacao', 'Origem', 'Produto'])
    dados_compras.standardize_text()
    dados_compras.valores_padrao()
    dados_compras.separar_quarentena()

    total_final = dados_compras.qtde_registros()
    descartados = total_inicial - total_final
    percentual_validos = (total_final / total_inicial) * 100 if total_inicial else 0

    print('\nTransformações concluídas!')
    print(f"   • Registros viáveis para uso: {total_final} ({percentual_validos:.1f}% do total)")
    print(f"   • Registros descartados/quarentena: {descartados}")

    # 3. EXPORTAÇÃO DOS DADOS TRATADOS
    dados_compras.salvando_dados_virgula('data_processed/dados_transformados_virgula.csv')
    dados_compras.salvando_dados_ponto_virgula('data_processed/dados_transformados_ponto_e_virgula.csv')
    dados_compras.salvando_dados_json('data_processed/dados_transformados.json')

    if not dados_compras.dados_quarentena.empty:
        Dados(df=dados_compras.dados_quarentena).salvando_dados_virgula(
            'data_processed/quarentena_datas.csv')

    # 4. GERAÇÃO DAS MÉTRICAS E RELATÓRIOS
    pipeline_metricas = PipelineMetricas(dados_compras.dados)

    print('\nGerando relatórios de métricas...\n')
    pipeline_metricas.exportar_pdf_totalizador('data_processed/metricas_consolidadas.pdf')
    pipeline_metricas.exportar_pdfs_separados('data_processed/metricas_pdf')
    pipeline_metricas.exportar_csvs_separados('data_processed/metricas_csv')
    pipeline_metricas.exportar_excel_totalizador('data_processed/metricas_consolidadas.xlsx')

    print('\nPipeline de ETL e geração de métricas finalizado com sucesso!')


if __name__ == '__main__':
    main()
