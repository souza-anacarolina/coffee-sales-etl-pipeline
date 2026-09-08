# ☕ Coffee Sales ETL Pipeline

Pipeline de Engenharia de Dados desenvolvido em Python e Pandas com foco em **Programação Orientada a Objetos (POO)**. O objetivo deste projeto é extrair, transformar e carregar (ETL) dados brutos de vendas de uma rede de cafeterias, tratando inconformidades, traduzindo termos e padronizando os tipos de dados para análises futuras.

---

## 📐 Arquitetura do Projeto

```text
pipeline_cafe/
│
├── data_raw/                  # Dados brutos de entrada (dirty_cafe_sales.csv)
├── data_processed/            # Dados limpos e exportados
│   ├── dados_transformados_virgula.csv
│   └── dados_transformados_ponto_e_virgula.csv
├── Dados.py                   # Classe principal (POO) com métodos de ETL
├── main.py                    # Script principal de orquestração do pipeline
├── requirements.txt           # Dependências do projeto
└── README.md                  # Documentação do projeto
```

## 🛠️ Recursos e Funcionalidades
A classe Dados encapsula todas as etapas do ciclo de vida dos dados:

1. **Extração / Leitura Flexível (`Extract`)**:

Suporte nativo para leitura de arquivos CSV, JSON e estruturas em memória (list).

Encapsulamento de atributos de estado do DataFrame (__df).

2. **Transformação (`Transform`)**:
  * **Mapeamento e Tradução:** Renomeação de colunas e tradução de valores em inglês (In-store, Takeaway, nomes de itens) para PT-BR.
  
  * **Limpeza de Ruídos:** Identificação e conversão de textos inválidos (ERROR, UNKNOWN, n/a) para valores nulos padrão do Pandas (pd.NA).
  
  * **Tratamento de Tipos (Type Casting):** Conversão de tipos de dados usando tipos nullable do Pandas (Int64, Float64, string, datetime64[ns]).
  
  * **Desduplicação:** Identificação e remoção de registros duplicados com base na chave primária (Cod_Transacao).
  
  * **Padronização Visual:** Sanitização de strings removendo espaços extras (strip) e ajustando caixa de texto (upper).
  
  * **Métricas Derivadas:** Agrupamento e agregação de vendas por produto.

3. **Carga (`Load`):**
   * **Exportação Multiformato:** Métodos dedicados para geração de arquivos CSV separados por vírgula (`.salvando_dados_virgula`) e por ponto e vírgula (`.salvando_dados_ponto_virgula`).
   * **Compatibilidade Regional:** Suporte ao encoding `utf-8-sig` (ideal para abertura direta no Microsoft Excel), formatação de precisão decimal (`%.2f`), vírgula como separador decimal e padronização de datas (`%d/%m/%Y`).

## 🚀 Como Executar o Projeto
Pré-requisitos
Python 3.10+

Git instalado

1. Clonar o repositório

```bash
git clone https://github.com/souza-anacarolina/coffee-sales-etl-pipeline.git
cd coffee-sales-etl-pipeline
```

2. Criar e ativar o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate   # Windows
```

3. Instalar as dependências

```bash
pip install -r requirements.txt
```
4. Executar o pipeline

```bash
python main.py
```

## 🧰 Tecnologias Utilizadas
Linguagem: Python

Manipulação de Dados: Pandas

Paradigmas: Programação Orientada a Objetos (POO) e ETL

Ambiente de Desenvolvimento: WSL (Ubuntu) / VS Code

---

## 📌 Fonte dos Dados

O conjunto de dados brutos utilizado neste projeto foi obtido na plataforma **[Kaggle]([https://www.kaggle.com/](https://www.kaggle.com/api/v1/datasets/download/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training)**. 

* **Dataset Original:** Vendas de Cafeteria (*Cafe Sales - Dirty Data for Cleaning Training*)
* **Propósito:** O conjunto foi utilizado como base para simulação de um cenário real de Engenharia de Dados, contendo inconformidades deliberadas como datas fora do padrão, termos em inglês, ruídos textuais (`ERROR`, `UNKNOWN`) e registros duplicados.
