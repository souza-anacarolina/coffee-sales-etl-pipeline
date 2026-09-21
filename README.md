# ☕ Coffee Sales ETL Pipeline

Pipeline de Engenharia de Dados desenvolvido em Python e Pandas com foco em **Programação Orientada a Objetos (POO)**. O objetivo do projeto é extrair, transformar e carregar (ETL) dados brutos de vendas de cafeterias — vindos de **múltiplas fontes, com esquemas diferentes entre si** — tratando inconformidades, unificando colunas, traduzindo termos e padronizando tipos de dados para análises futuras.

---

## 📐 Arquitetura do Projeto

```text
pipeline_cafe/
│
├── data_raw/                          # Dados brutos de entrada (uma ou mais fontes)
│   ├── dirty_cafe_sales.csv           # Fonte 1 — venda simples, colunas em inglês
│   └── Coffee Shop Sales.xlsx         # Fonte 2 — venda por loja/produto, colunas próprias
│
├── data_processed/                    # Dados limpos e relatórios exportados
│   ├── dados_transformados_virgula.csv
│   ├── dados_transformados_ponto_e_virgula.csv
│   ├── dados_transformados.json
│   ├── quarentena_datas.csv           # Registros isolados por falha de qualidade
│   ├── metricas_consolidadas.pdf
│   ├── metricas_consolidadas.xlsx
│   ├── metricas_csv/
│   └── metricas_pdf/
│
├── scripts/
│   ├── Dados.py                       # Engine de ETL (POO), genérica e reutilizável
│   ├── config_etl.py                  # Configuração declarativa: fontes e mapeamentos
│   ├── Processamento_dados.py         # Script de orquestração do pipeline
│   └── PipelineMetricas.py            # Classe (POO) para cálculo de métricas e relatórios
│
├── .gitignore                         # Arquivo para ignorar arquivos locais/temporários
├── requirements.txt                   # Dependências do projeto
└── README.md                          # Documentação do projeto
```

## 🛠️ Recursos e Funcionalidades

### 1. Extração — `Dados.py` (`Extract`)

* **Múltiplos formatos, detecção automática:** CSV, JSON, Excel (`.xlsx`/`.xls`) e listas em memória. O formato é detectado pela extensão do arquivo — não é preciso informá-lo manualmente.
* **União de fontes heterogêneas:** `Dados.unir_fontes({...})` combina duas ou mais fontes com **colunas diferentes entre si** em um único DataFrame. O que uma fonte não possui vira nulo automaticamente (união das colunas, não interseção) — nenhuma fonte precisa ter o esquema completo.
* **Rastreabilidade da origem:** cada linha do dado combinado carrega uma coluna `Origem`, indicando de qual fonte ela veio. Isso permite explicar concentrações de nulos por coluna (ex.: um campo que só existe em uma das fontes) em vez de tratá-las como erro.
* Encapsulamento de atributos de estado do DataFrame (`__df`).

### 2. Transformação — `Dados.py` (`Transform`)

* **Mapeamento e tradução:** renomeação de colunas e tradução de valores em inglês (`In-store`, `Takeaway`, nomes de itens) para PT-BR — o mesmo mapeamento é aplicado a todas as fontes; chaves que não existem em uma fonte específica são ignoradas.
* **Limpeza de ruídos:** identificação e conversão de textos inválidos (`ERROR`, `UNKNOWN`, `n/a`) para o nulo padrão do Pandas (`pd.NA`).
* **Tratamento de tipos (type casting) robusto a múltiplas fontes:** conversão para tipos *nullable* do Pandas (`Int64`, `Float64`, `string`, `datetime64[ns]`) usando `pd.to_numeric`/`pd.to_datetime` com `errors='coerce'` antes do cast final — necessário porque, ao unir fontes, uma mesma coluna pode chegar como número nativo em uma fonte (Excel) e como texto em outra (CSV), o que quebra um `.astype()` direto.
* **Desduplicação configurável:** remoção de registros duplicados por uma chave de negócio explícita (por padrão `Cod_Transacao` + `Produto`, definida em `Processamento_dados.py`) — importante porque o dataset de origem reaproveita o mesmo `Cod_Transacao` em algumas linhas para produtos **diferentes**; deduplicar só pela chave técnica apagaria vendas reais.
* **Padronização visual:** sanitização de strings removendo espaços extras (`strip`) e ajustando caixa de texto (`upper`).
* **Quarentena de qualidade:** registros que comprometem a integridade do grão da tabela (hoje: ausência de data da transação) são isolados em vez de seguir para o restante do pipeline, e exportados separadamente para inspeção.

### 3. Carga — `Dados.py` / `PipelineMetricas.py` (`Load`)

* **Exportação multiformato:** CSV separado por vírgula (`.salvando_dados_virgula`), por ponto e vírgula (`.salvando_dados_ponto_virgula`), JSON (`.salvando_dados_json`) e Excel (`.salvando_dados_excel`).
* **Compatibilidade regional:** encoding `utf-8-sig` (abertura direta no Excel), precisão decimal (`%.2f`), vírgula como separador decimal e datas no formato `%d/%m/%Y`.
* **Relatórios automatizados:** métricas consolidadas em PDF único, PDFs individuais por métrica, CSVs individuais e Excel com uma aba por métrica.

## ⚙️ Adicionando uma Nova Fonte de Dados

Uma das metas deste projeto é que ele funcione com **qualquer número de fontes**, mesmo que tenham colunas diferentes entre si, sem alterar código de orquestração. Para adicionar uma nova fonte (outra planilha, outro CSV, um JSON de outra loja etc.), basta editar `scripts/config_etl.py`:

```python
FONTES_DADOS = [
    {'origem': 'csv_legado', 'path': 'data_raw/dirty_cafe_sales.csv'},
    {'origem': 'xlsx_coffee_shop_sales', 'path': 'data_raw/Coffee Shop Sales.xlsx'},
    # nova fonte:
    {'origem': 'json_loja_centro', 'path': 'data_raw/vendas_loja_centro.json'},
]
```

Se a nova fonte trouxer colunas que ainda não têm tradução, acrescente-as em `MAPEAMENTO_COLUNAS` (e, se forem colunas novas de fato, o tipo correspondente em `MAPEAMENTO_TIPOS`). Nenhuma alteração é necessária em `Dados.py` ou `Processamento_dados.py`.

## 🚀 Como Executar o Projeto

**Pré-requisitos**
* Python 3.10+
* Git instalado

**1. Clonar o repositório**

```bash
git clone https://github.com/souza-anacarolina/coffee-sales-etl-pipeline.git
cd coffee-sales-etl-pipeline
```

**2. Criar e ativar o ambiente virtual**

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows
```

**3. Instalar as dependências**

```bash
pip install -r requirements.txt
```

**4. Executar o pipeline** (a partir da raiz do projeto, para que os caminhos relativos em `config_etl.py` sejam resolvidos corretamente)

```bash
python scripts/Processamento_dados.py
```

## 🧰 Tecnologias Utilizadas

* **Linguagem:** Python
* **Manipulação de Dados:** Pandas
* **Leitura de Excel:** OpenPyXL
* **Geração de Relatórios:** FPDF2, OpenPyXL
* **Paradigmas:** Programação Orientada a Objetos (POO) e ETL
* **Ambiente de Desenvolvimento:** WSL (Ubuntu) / VS Code

---

## 📌 Fonte dos Dados

Este projeto combina duas fontes de dados de vendas de cafeteria, propositalmente com esquemas diferentes entre si, para simular um cenário real de integração de dados heterogêneos:

* **`dirty_cafe_sales.csv`** — obtido no **[Kaggle](https://www.kaggle.com/api/v1/datasets/download/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training)** (*Cafe Sales - Dirty Data for Cleaning Training*). Contém inconformidades deliberadas: datas fora do padrão, termos em inglês, ruídos textuais (`ERROR`, `UNKNOWN`) e `Cod_Transacao` reaproveitado entre vendas distintas.
* **`Coffee Shop Sales.xlsx`** — obtido no **[Kaggle](https://www.kaggle.com/code/ahmedabbas757/coffee-shop-sales)** (*Coffee Shop Sales*). dataset com granularidade por loja e por produto (`store_id`, `product_category`, `product_type`, `product_detail`), sem correspondência direta com todas as colunas do CSV acima. 

**Propósito:** simular um cenário real de Engenharia de Dados em que múltiplas fontes precisam ser combinadas mesmo com esquemas parcialmente distintos — decidindo o que fazer com colunas que existem em uma fonte e não na outra, e com chaves de negócio que nem sempre são únicas dentro de uma mesma fonte.