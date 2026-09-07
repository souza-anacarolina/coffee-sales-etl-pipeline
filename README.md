# ☕ Coffee Sales ETL Pipeline

Pipeline de Engenharia de Dados desenvolvido em Python e Pandas com foco em **Programação Orientada a Objetos (POO)**. O objetivo deste projeto é extrair, transformar e carregar (ETL) dados brutos de vendas de uma rede de cafeterias, tratando inconformidades, traduzindo termos e padronizando os tipos de dados para análises futuras.

---

## 📐 Arquitetura do Projetos

```text
pipeline_cafe/
│
├── data_raw/                  # Dados brutos de entrada (dirty_cafe_sales.csv)
├── data_processed/            # Dados limpos e transformados (dados_transformados.csv)
├── Dados.py                   # Classe principal (POO) com métodos de ETL
├── main.py                    # Script principal de orquestração do pipeline
├── requirements.txt           # Dependências do projeto
└── README.md                  # Documentação do projeto

## 🛠️ Recursos e Funcionalidades

A classe Dados encapsula todas as etapas do ciclo de vida dos dados:

Extração / Leitura Flexível (Extract):

Suporte nativo para leitura de arquivos CSV, JSON e estruturas em memória (list).

Encapsulamento de atributos de estado do DataFrame (__df).

Transformação (Transform):

Mapeamento e Tradução: Renomeação de colunas e tradução de valores em inglês (In-store, Takeaway, nomes de itens) para PT-BR.

Limpeza de Ruídos: Identificação e conversão de textos inválidos (ERROR, UNKNOWN, n/a) para valores nulos padrão do Pandas (pd.NA).

Tratamento de Tipos (Type Casting): Conversão de tipos de dados usando tipos nullable do Pandas (Int64, Float64, string, datetime64[ns]).

Desduplicação: Identificação e remoção de registros duplicados com base na chave primária (Cod_Transacao).

Padronização Visual: Sanitização de strings removendo espaços extras (strip) e ajustando caixa de texto (upper).

Métricas Derivadas: Agrupamento e agregação de vendas por produto.

Carga (Load):

Exportação dos dados tratados para diretório de saída com formatação adequada de enconding e datas (%d/%m/%Y).

## 🚀 Como Executar o Projeto
Pré-requisitos
Python 3.10+

Git instalado

1. Clonar o repositório

```bash
git clone [https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git](https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git)
cd NOME-DO-REPOSITORIO
```

2. Criar e ativar o ambiente virtual

```bash`
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate   # Windows
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

