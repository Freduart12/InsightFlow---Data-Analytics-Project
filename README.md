# 📊 InsightFlow - Data Analytics Project

## Visão Geral

Este projeto simula a atuação de um analista de dados na empresa **InsightFlow**, com o objetivo de transformar dados brutos de um e-commerce em **insights estratégicos para tomada de decisão**.

O trabalho cobre **todo o ciclo de análise de dados**, desde a geração e tratamento dos dados até a construção de um dashboard interativo e um modelo preditivo.

---

## Problema de Negócio

A análise foi guiada pelas seguintes perguntas:

* Qual é o perfil de consumo dos clientes?
* Quais categorias e produtos têm maior desempenho?
* Onde estão os principais padrões e anomalias?
* É possível prever o volume de vendas do próximo mês?

---

## Metodologia

O projeto foi estruturado em **4 sprints**, seguindo um fluxo real de Data Analytics:

---

# Sprint 1 — Ingestão e ETL

### Objetivo

Preparar os dados para análise.

### Atividades realizadas

* Geração de dataset com +5000 registros
* Inserção de inconsistências simulando dados reais
* Tratamento de:

  * valores nulos
  * duplicatas
  * formatos de moeda
* Padronização de datas
* Criação de variáveis:

  * `Valor_Bruto`
  * `Valor_Desconto`
  * `Valor_Total`
* Carga no banco SQLite

### Saídas

* `data/ecom_data.csv`
* `data/ecommerce.db`

---

# Sprint 2 — EDA e SQL

### Objetivo

Explorar os dados e extrair insights.

### Atividades realizadas

#### Estatísticas

* média, mediana, desvio padrão
* distribuição de vendas

#### KPIs

* faturamento total
* ticket médio
* número de pedidos
* clientes únicos

#### SQL

Consultas utilizando:

* `GROUP BY`
* `SUM`
* `AVG`
* ordenação e ranking

#### Outliers

* detecção via método IQR

#### RFM (Segmentação de clientes)

* Recência
* Frequência
* Monetário

---

### Saídas

* `outputs/kpis.txt`
* `outputs/segmentacao_rfm.csv`
* `outputs/outliers_detectados.csv`

---

# Sprint 3 — Visualização e Dashboard

### Objetivo

Transformar dados em informação visual.

### Visualizações geradas

* vendas ao longo do tempo
* faturamento por categoria
* top clientes
* top produtos
* boxplot de outliers

### Dashboard interativo

Foi desenvolvido com **Streamlit**, contendo:

#### Filtros

* Categoria
* Estado
* Canal de venda
* Método de pagamento
* Período

#### Métricas exibidas

* Faturamento total
* Ticket médio
* Total de pedidos
* Clientes únicos
* Itens vendidos

#### Abas do dashboard

* Visão geral
* Clientes e RFM
* Previsão de vendas
* Dados

---

### Saídas

* gráficos `.png` em `outputs/`
* `dashboard.py`

---

# Sprint 4 — Modelo Preditivo e Storytelling

### Objetivo

Prever vendas futuras e gerar recomendações.

### Atividades realizadas

* Regressão linear
* Previsão para os próximos 30 dias
* Interpretação dos resultados
* Construção de narrativa analítica

### Saídas

* `outputs/previsao_proximo_mes.csv`
* `outputs/grafico_previsao_vendas.png`
* `outputs/storytelling.txt`

---

# Como executar o projeto
## No terminal, execute:

git clone https://github.com/Freduart12/InsightFlow---Data-Analytics-Project.git
cd InsightFlow---Data-Analytics-Project

## Instalar as dependências
Opção recomendada

Se o arquivo requirements.txt já estiver no projeto:

pip install -r requirements.txt
Dependências esperadas

pandas
numpy
matplotlib
scikit-learn
faker
jupyter
streamlit
plotly

## Certifique-se de que esses arquivos existem:

src/insightflow_pipeline.py
dashboard.py
requirements.txt

As pastas data/ e outputs/ podem ser criadas automaticamente pelo pipeline.


## Executar o pipeline principal

Esse é o passo que gera o dataset, trata os dados, cria o banco, produz os gráficos, faz a previsão e exporta os resultados.

No terminal:

python src/insightflow_pipeline.py
O que esse comando faz

### Ao rodar o pipeline, o projeto executa as 4 sprints automaticamente:

* gera o dataset com mais de 5.000 linhas
* trata valores nulos, duplicatas e inconsistências
* salva o CSV final
* carrega os dados em SQLite
* calcula KPIs
* executa análises e consultas SQL
* detecta outliers
* faz segmentação RFM
* gera gráficos
* cria previsão para os próximos 30 dias
* exporta arquivos finais em outputs/

## Verificar os arquivos gerados

Depois de rodar o pipeline, você deverá ter:

* Na pasta data/
* ecom_data.csv
* ecommerce.db
* Na pasta outputs/
* kpis.txt
* previsao_proximo_mes.csv
* grafico_vendas_tempo.png
* grafico_categoria.png
* grafico_top_clientes.png
* boxplot_outliers.png
* dashboard_resumo.png
* grafico_previsao_vendas.png
* segmentacao_rfm.csv
* outliers_detectados.csv
* storytelling.txt

## Abrir o dashboard interativo

Depois de rodar o pipeline, inicie o dashboard com:

streamlit run dashboard.py

O Streamlit abrirá o painel no navegador. Se não abrir sozinho, copie o endereço exibido no terminal, geralmente:

http://localhost:8501

## O que o dashboard mostra

O dashboard interativo contém:

* Filtros
* categoria
* estado
* canal de venda
* método de pagamento
* período
* KPIs
* faturamento total
* ticket médio
* total de pedidos
* clientes únicos
* itens vendidos
* Abas
* Visão Geral
* Clientes e RFM
* Previsão
* Dados
* Gráficos
* vendas ao longo do tempo
* faturamento por categoria
* top clientes
* top produtos
* boxplot de outliers
* gráfico de previsão

# Dashboard Interativo

## Como executar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

---

### 2. Rodar o pipeline

```bash
python src/insightflow_pipeline.py
```

Isso irá gerar:

* dataset limpo
* banco de dados
* arquivos de saída
* previsão
* RFM
* gráficos

---

### 3. Abrir o dashboard

```bash
streamlit run dashboard.py
```

---

### 4. Acessar no navegador

```text
http://localhost:8501
```

---

## Observação importante

O dashboard depende dos arquivos gerados pelo pipeline:

* `data/ecom_data.csv`
* `outputs/previsao_proximo_mes.csv`
* `outputs/segmentacao_rfm.csv`
* `outputs/outliers_detectados.csv`

Se não rodar o pipeline antes, o dashboard ficará incompleto.

---

# Tecnologias Utilizadas

* Python
* Pandas
* NumPy
* Matplotlib
* SQLite
* Scikit-learn
* Streamlit
* Plotly
* Faker

  
# Principais arquivos do projeto

src/insightflow_pipeline.py

Script principal responsável por executar o pipeline completo.

dashboard.py

Aplicação Streamlit para visualização interativa dos resultados.

data/ecom_data.csv

Dataset final tratado.

data/ecommerce.db

Banco de dados SQLite com a tabela de vendas.

outputs/

Pasta com gráficos, previsões, segmentação e resultados exportados.


---

# Estrutura do Projeto

```bash
insightflow/
│
├── src/
│   └── insightflow_pipeline.py
├── data/
│   ├── ecom_data.csv
│   └── ecommerce.db
├── outputs/
│   ├── kpis.txt
│   ├── previsao_proximo_mes.csv
│   ├── grafico_vendas_tempo.png
│   ├── grafico_categoria.png
│   ├── grafico_top_clientes.png
│   ├── boxplot_outliers.png
│   ├── dashboard_resumo.png
│   ├── grafico_previsao_vendas.png
│   ├── segmentacao_rfm.csv
│   ├── outliers_detectados.csv
│   └── storytelling.txt
├── dashboard.py
├── requirements.txt
└── README.md
```

# Resultados esperados

Ao final, o projeto entrega:

* um pipeline completo de Data Analytics
* um dataset estruturado
* análise exploratória e SQL
* segmentação de clientes
* gráficos e dashboard interativo
* previsão de vendas
* documentação completa

---

# Principais Insights

* O faturamento apresenta tendência consistente ao longo do tempo
* Algumas categorias concentram maior volume de vendas
* Existe concentração de receita em poucos clientes
* Foram identificados comportamentos atípicos (outliers)
* A segmentação RFM permite identificar clientes estratégicos
* O modelo preditivo indica tendência futura das vendas

---

# Conclusão

Este projeto demonstra a aplicação completa de um pipeline de Data Analytics em um cenário de e-commerce, integrando:

* engenharia de dados (ETL)
* análise exploratória
* SQL
* visualização
* machine learning
* storytelling

---

# Autor

**Frederico Matheus Costa Duarte**
