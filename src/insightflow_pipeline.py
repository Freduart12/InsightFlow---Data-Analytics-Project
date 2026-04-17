import os
import sqlite3
import random
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from faker import Faker
from sklearn.linear_model import LinearRegression



# CONFIGURAÇÕES GERAIS
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

CSV_PATH = DATA_DIR / "ecom_data.csv"
DB_PATH = DATA_DIR / "ecommerce.db"
TABLE_NAME = "vendas"

RANDOM_SEED = 42
N_ROWS = 6000

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
fake = Faker("pt_BR")
Faker.seed(RANDOM_SEED)



# SPRINT 1 - GERAÇÃO DOS DADOS
def gerar_dataset(n_rows: int = N_ROWS) -> pd.DataFrame:
    categorias_produtos = {
        "Eletrônicos": [
            "Notebook", "Mouse", "Teclado", "Monitor", "Headset", "Celular"
        ],
        "Roupas": [
            "Camiseta", "Calça", "Jaqueta", "Tênis", "Vestido", "Boné"
        ],
        "Casa": [
            "Panela", "Luminária", "Cadeira", "Mesa", "Tapete", "Almofada"
        ],
        "Beleza": [
            "Perfume", "Shampoo", "Hidratante", "Sabonete", "Maquiagem", "Protetor Solar"
        ],
        "Esportes": [
            "Bola", "Halter", "Corda", "Luva", "Bicicleta", "Garrafa Térmica"
        ]
    }

    precos_base = {
        "Notebook": 3500.0, "Mouse": 80.0, "Teclado": 150.0, "Monitor": 900.0, "Headset": 250.0, "Celular": 1800.0,
        "Camiseta": 60.0, "Calça": 120.0, "Jaqueta": 220.0, "Tênis": 300.0, "Vestido": 180.0, "Boné": 50.0,
        "Panela": 140.0, "Luminária": 90.0, "Cadeira": 250.0, "Mesa": 650.0, "Tapete": 200.0, "Almofada": 45.0,
        "Perfume": 180.0, "Shampoo": 35.0, "Hidratante": 40.0, "Sabonete": 10.0, "Maquiagem": 95.0, "Protetor Solar": 55.0,
        "Bola": 70.0, "Halter": 130.0, "Corda": 35.0, "Luva": 60.0, "Bicicleta": 1500.0, "Garrafa Térmica": 45.0
    }

    estados_cidades = {
        "MG": ["Belo Horizonte", "Itabira", "Contagem", "Betim"],
        "SP": ["São Paulo", "Campinas", "Santos", "Ribeirão Preto"],
        "RJ": ["Rio de Janeiro", "Niterói", "Petrópolis", "Campos"],
        "BA": ["Salvador", "Feira de Santana", "Ilhéus", "Vitória da Conquista"]
    }

    metodos_pagamento = ["Cartão de Crédito", "Pix", "Boleto", "Cartão de Débito"]
    canais_venda = ["Site", "App", "Marketplace"]

    registros = []

    for transacao_id in range(1, n_rows + 1):
        categoria = random.choice(list(categorias_produtos.keys()))
        produto = random.choice(categorias_produtos[categoria])
        preco_base = precos_base[produto]

        quantidade = random.choice([1, 1, 1, 2, 2, 3, 4, None])
        desconto = random.choice([0, 0, 0, 5, 10, 15, None])

        estado = random.choice(list(estados_cidades.keys()))
        cidade = random.choice(estados_cidades[estado])

        # variação de preço
        valor_unitario = round(preco_base * random.uniform(0.85, 1.15), 2)

        # inconsistências
        valor_unitario_raw = random.choice([
            valor_unitario,
            valor_unitario,
            valor_unitario,
            f"R${valor_unitario}",
            None
        ])

        data_venda = fake.date_between(start_date="-12M", end_date="today")

        registros.append({
            "ID_Transacao": transacao_id,
            "Data_Venda": data_venda,
            "ID_Cliente": random.randint(1000, 2500),
            "Nome_Produto": produto,
            "Categoria_Produto": categoria,
            "Valor_Unitario": valor_unitario_raw,
            "Quantidade": quantidade,
            "Desconto_Pct": desconto,
            "Metodo_Pagamento": random.choice(metodos_pagamento),
            "Canal_Venda": random.choice(canais_venda),
            "Cidade": cidade,
            "Estado": estado
        })

    df = pd.DataFrame(registros)

    duplicatas = df.sample(40, random_state=RANDOM_SEED)
    df = pd.concat([df, duplicatas], ignore_index=True)

    return df



# SPRINT 1 - ETL
def tratar_dados(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    print("\nSPRINT 1 - INGESTÃO E ETL")
    print(f"Linhas antes do tratamento: {len(df)}")

    df = df.drop_duplicates()

    df["Data_Venda"] = pd.to_datetime(df["Data_Venda"], errors="coerce")

    df["Valor_Unitario"] = (
        df["Valor_Unitario"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(",", ".", regex=False)
        .replace("None", np.nan)
    )
    df["Valor_Unitario"] = pd.to_numeric(df["Valor_Unitario"], errors="coerce")

    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce")

    df["Desconto_Pct"] = pd.to_numeric(df["Desconto_Pct"], errors="coerce")

    df["Quantidade"] = df["Quantidade"].fillna(1)
    df["Desconto_Pct"] = df["Desconto_Pct"].fillna(0)
    df["Valor_Unitario"] = df.groupby("Nome_Produto")["Valor_Unitario"].transform(
        lambda s: s.fillna(s.median())
    )

    df["Valor_Unitario"] = df["Valor_Unitario"].fillna(df["Valor_Unitario"].median())

    df = df.dropna(subset=["Data_Venda"])

    df["Quantidade"] = df["Quantidade"].astype(int)
    df["Desconto_Pct"] = df["Desconto_Pct"].astype(float)
    df["Valor_Unitario"] = df["Valor_Unitario"].astype(float)

    df["Valor_Bruto"] = df["Valor_Unitario"] * df["Quantidade"]
    df["Valor_Desconto"] = df["Valor_Bruto"] * (df["Desconto_Pct"] / 100)
    df["Valor_Total"] = df["Valor_Bruto"] - df["Valor_Desconto"]

    df = df.sort_values("Data_Venda").reset_index(drop=True)

    print(f"Linhas após tratamento: {len(df)}")
    print("ETL concluído.")

    return df


def salvar_csv(df: pd.DataFrame, csv_path: Path = CSV_PATH) -> None:
    df.to_csv(csv_path, index=False)
    print(f"CSV salvo em: {csv_path}")


def carregar_sqlite(df: pd.DataFrame, db_path: Path = DB_PATH, table_name: str = TABLE_NAME) -> None:
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Dados carregados no SQLite: {db_path}")



# SPRINT 2 - EDA
def calcular_kpis(df: pd.DataFrame) -> dict:
    kpis = {
        "faturamento_total": round(df["Valor_Total"].sum(), 2),
        "ticket_medio": round(df["Valor_Total"].mean(), 2),
        "total_pedidos": int(df["ID_Transacao"].nunique()),
        "clientes_unicos": int(df["ID_Cliente"].nunique()),
        "quantidade_itens_vendidos": int(df["Quantidade"].sum())
    }
    return kpis


def analise_exploratoria(df: pd.DataFrame) -> None:
    print("\nSPRINT 2 - EDA")
    print("\n[Informações gerais]")
    print(df.info())

    print("\n[Estatísticas descritivas]")
    print(df.select_dtypes(include=[np.number]).describe())

    print("\n[Vendas por categoria - frequência]")
    print(df["Categoria_Produto"].value_counts())

    print("\n[Produtos mais vendidos em quantidade]")
    produtos_qtd = df.groupby("Nome_Produto")["Quantidade"].sum().sort_values(ascending=False).head(10)
    print(produtos_qtd)

    print("\n[KPIs principais]")
    kpis = calcular_kpis(df)
    for chave, valor in kpis.items():
        print(f"{chave}: {valor}")


def executar_consultas_sql(db_path: Path = DB_PATH) -> dict:
    print("\nSPRINT 2 - SQL")

    consultas = {
        "top_clientes_faturamento": """
            SELECT
                ID_Cliente,
                ROUND(SUM(Valor_Total), 2) AS total_gasto
            FROM vendas
            GROUP BY ID_Cliente
            ORDER BY total_gasto DESC
            LIMIT 10;
        """,
        "vendas_por_categoria": """
            SELECT
                Categoria_Produto,
                ROUND(SUM(Valor_Total), 2) AS total_vendas,
                SUM(Quantidade) AS total_itens
            FROM vendas
            GROUP BY Categoria_Produto
            ORDER BY total_vendas DESC;
        """,
        "ticket_medio_por_cliente": """
            SELECT
                ID_Cliente,
                ROUND(AVG(Valor_Total), 2) AS ticket_medio
            FROM vendas
            GROUP BY ID_Cliente
            ORDER BY ticket_medio DESC
            LIMIT 10;
        """,
        "vendas_mensais": """
            SELECT
                strftime('%Y-%m', Data_Venda) AS mes,
                ROUND(SUM(Valor_Total), 2) AS faturamento
            FROM vendas
            GROUP BY mes
            ORDER BY mes;
        """
    }

    resultados = {}
    with sqlite3.connect(db_path) as conn:
        for nome, query in consultas.items():
            resultados[nome] = pd.read_sql(query, conn)
            print(f"\n[{nome}]")
            print(resultados[nome])

    return resultados


def matriz_correlacao(df: pd.DataFrame) -> pd.DataFrame:
    print("\nSPRINT 2 - CORRELAÇÃO ")
    corr = df[["Valor_Unitario", "Quantidade", "Desconto_Pct", "Valor_Total"]].corr(numeric_only=True)
    print(corr)
    return corr


def detectar_outliers(df: pd.DataFrame) -> pd.DataFrame:
    print("\nSPRINT 2 - OUTLIERS")

    q1 = df["Valor_Total"].quantile(0.25)
    q3 = df["Valor_Total"].quantile(0.75)
    iqr = q3 - q1

    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    outliers = df[
        (df["Valor_Total"] < limite_inferior) |
        (df["Valor_Total"] > limite_superior)
    ].copy()

    print(f"Quantidade de outliers encontrados: {len(outliers)}")
    print(outliers[["ID_Transacao", "Nome_Produto", "Valor_Total"]].head())

    return outliers


def segmentacao_rfm(df: pd.DataFrame) -> pd.DataFrame:
    print("\nSPRINT 2 - RFM")

    snapshot_date = df["Data_Venda"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("ID_Cliente").agg({
        "Data_Venda": lambda x: (snapshot_date - x.max()).days,
        "ID_Transacao": "count",
        "Valor_Total": "sum"
    }).reset_index()

    rfm.columns = ["ID_Cliente", "Recencia", "Frequencia", "Monetario"]

    rfm["R_Score"] = pd.qcut(rfm["Recencia"], 4, labels=[4, 3, 2, 1], duplicates="drop")
    rfm["F_Score"] = pd.qcut(rfm["Frequencia"].rank(method="first"), 4, labels=[1, 2, 3, 4], duplicates="drop")
    rfm["M_Score"] = pd.qcut(rfm["Monetario"], 4, labels=[1, 2, 3, 4], duplicates="drop")

    rfm["RFM_Score"] = (
        rfm["R_Score"].astype(str) +
        rfm["F_Score"].astype(str) +
        rfm["M_Score"].astype(str)
    )

    print(rfm.head())

    return rfm



# SPRINT 3 - VISUALIZAÇÃO E DASHBOARD
def salvar_kpis_txt(kpis: dict, output_dir: Path = OUTPUT_DIR) -> None:
    caminho = output_dir / "kpis.txt"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("KPIs PRINCIPAIS\n")
        f.write("====================\n")
        for chave, valor in kpis.items():
            f.write(f"{chave}: {valor}\n")
    print(f"[OK] KPIs salvos em: {caminho}")


def gerar_visualizacoes(df: pd.DataFrame, outliers: pd.DataFrame, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    print("\nSPRINT 3 - VISUALIZAÇÃO E DASHBOARD")

    vendas_tempo = df.groupby("Data_Venda")["Valor_Total"].sum().sort_index()
    vendas_categoria = df.groupby("Categoria_Produto")["Valor_Total"].sum().sort_values(ascending=False)
    top_clientes = df.groupby("ID_Cliente")["Valor_Total"].sum().sort_values(ascending=False).head(10)

    # Tempo
    plt.figure(figsize=(12, 5))
    plt.plot(vendas_tempo.index, vendas_tempo.values)
    plt.title("Vendas ao Longo do Tempo")
    plt.xlabel("Data")
    plt.ylabel("Faturamento")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "grafico_vendas_tempo.png", dpi=150)
    plt.close()

    # categorias
    plt.figure(figsize=(10, 5))
    plt.bar(vendas_categoria.index, vendas_categoria.values)
    plt.title("Faturamento por Categoria")
    plt.xlabel("Categoria")
    plt.ylabel("Faturamento")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "grafico_categoria.png", dpi=150)
    plt.close()

    # Top clientes
    plt.figure(figsize=(10, 5))
    plt.bar(top_clientes.index.astype(str), top_clientes.values)
    plt.title("Top 10 Clientes por Faturamento")
    plt.xlabel("ID Cliente")
    plt.ylabel("Faturamento")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "grafico_top_clientes.png", dpi=150)
    plt.close()

    # outliers
    plt.figure(figsize=(6, 5))
    plt.boxplot(df["Valor_Total"])
    plt.title("Boxplot de Valor Total")
    plt.ylabel("Valor Total")
    plt.tight_layout()
    plt.savefig(output_dir / "boxplot_outliers.png", dpi=150)
    plt.close()

    # Dashboard
    fig, axs = plt.subplots(2, 2, figsize=(14, 9))

    axs[0, 0].plot(vendas_tempo.index, vendas_tempo.values)
    axs[0, 0].set_title("Vendas no Tempo")
    axs[0, 0].tick_params(axis="x", rotation=45)

    axs[0, 1].bar(vendas_categoria.index, vendas_categoria.values)
    axs[0, 1].set_title("Categorias")
    axs[0, 1].tick_params(axis="x", rotation=45)

    axs[1, 0].bar(top_clientes.index.astype(str), top_clientes.values)
    axs[1, 0].set_title("Top Clientes")
    axs[1, 0].tick_params(axis="x", rotation=45)

    axs[1, 1].boxplot(df["Valor_Total"])
    axs[1, 1].set_title("Outliers")

    plt.tight_layout()
    plt.savefig(output_dir / "dashboard_resumo.png", dpi=150)
    plt.close()

    print(f"[OK] Gráficos salvos em: {output_dir}")

    return vendas_tempo.reset_index(name="Valor_Total")



# SPRINT 4 - MODELO PREDITIVO
def modelo_preditivo(vendas_diarias: pd.DataFrame, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    print("\nSPRINT 4 - MODELO PREDITIVO")

    df_model = vendas_diarias.copy()
    df_model["dias"] = np.arange(len(df_model))

    X = df_model[["dias"]]
    y = df_model["Valor_Total"]

    modelo = LinearRegression()
    modelo.fit(X, y)

    df_model["previsao_ajustada"] = modelo.predict(X)

    # prever próximos 30 dias
    dias_futuros = np.arange(len(df_model), len(df_model) + 30).reshape(-1, 1)
    previsoes_futuras = modelo.predict(dias_futuros)

    ultima_data = pd.to_datetime(df_model["Data_Venda"].max())
    datas_futuras = pd.date_range(start=ultima_data + pd.Timedelta(days=1), periods=30)

    previsao_df = pd.DataFrame({
        "Data_Venda": datas_futuras,
        "Previsao_Vendas": previsoes_futuras
    })

    previsao_df.to_csv(output_dir / "previsao_proximo_mes.csv", index=False)

    # gráfico do ajuste + futuro
    plt.figure(figsize=(12, 5))
    plt.plot(df_model["Data_Venda"], df_model["Valor_Total"], label="Real")
    plt.plot(df_model["Data_Venda"], df_model["previsao_ajustada"], label="Regressão")
    plt.plot(previsao_df["Data_Venda"], previsao_df["Previsao_Vendas"], label="Próximos 30 dias")
    plt.title("Previsão de Vendas")
    plt.xlabel("Data")
    plt.ylabel("Faturamento")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "grafico_previsao_vendas.png", dpi=150)
    plt.close()

    print(f"[OK] Previsão salva em: {output_dir / 'previsao_proximo_mes.csv'}")
    return previsao_df



# SPRINT 4 - STORYTELLING
def gerar_storytelling(df: pd.DataFrame, rfm: pd.DataFrame, outliers: pd.DataFrame, previsao_df: pd.DataFrame) -> str:
    faturamento_total = df["Valor_Total"].sum()
    ticket_medio = df["Valor_Total"].mean()
    clientes_unicos = df["ID_Cliente"].nunique()

    categoria_top = (
        df.groupby("Categoria_Produto")["Valor_Total"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    produto_top = (
        df.groupby("Nome_Produto")["Quantidade"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    media_previsao = previsao_df["Previsao_Vendas"].mean()

    storytelling = f"""
RESUMO EXECUTIVO - INSIGHTFLOW

1. O dataset foi gerado com mais de 5.000 registros e passou por um processo completo de ETL,
incluindo tratamento de valores nulos, remoção de duplicatas e padronização de formatos.

2. O faturamento total observado foi de R$ {faturamento_total:,.2f}, com ticket médio de
R$ {ticket_medio:,.2f} e base de {clientes_unicos} clientes únicos.

3. A categoria com maior faturamento foi "{categoria_top}", enquanto o produto com maior volume
de itens vendidos foi "{produto_top}".

4. A análise de outliers identificou {len(outliers)} transações fora do padrão esperado,
o que pode indicar compras atípicas, promoções agressivas ou possíveis inconsistências operacionais.

5. A segmentação RFM permitiu identificar perfis distintos de clientes com base em recência,
frequência e valor monetário, apoiando futuras estratégias de retenção e relacionamento.

6. O modelo preditivo por regressão linear foi utilizado para estimar o comportamento das vendas
nos próximos 30 dias. A média prevista de faturamento diário para esse período foi de
R$ {media_previsao:,.2f}.

7. Como próxims passos, recomenda-se:
   - investir nas categorias mais rentáveis;
   - criar ações para retenção de clientes de maior valor;
   - monitorar transações outliers;
   - usar a previsão de vendas para planejamento de estoque e campanhas.
""".strip()

    print("\nSPRINT 4 - STORYTELLING")
    print(storytelling)

    return storytelling


def salvar_storytelling(texto: str, output_dir: Path = OUTPUT_DIR) -> None:
    caminho = output_dir / "storytelling.txt"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"[OK] Storytelling salvo em: {caminho}")



# AUXILIARES
def salvar_rfm(rfm: pd.DataFrame, output_dir: Path = OUTPUT_DIR) -> None:
    caminho = output_dir / "segmentacao_rfm.csv"
    rfm.to_csv(caminho, index=False)
    print(f"[OK] Segmentação RFM salva em: {caminho}")


def salvar_outliers(outliers: pd.DataFrame, output_dir: Path = OUTPUT_DIR) -> None:
    caminho = output_dir / "outliers_detectados.csv"
    outliers.to_csv(caminho, index=False)
    print(f"[OK] Outliers salvos em: {caminho}")



# FUNÇÃO PRINCIPAL
def main() -> None:
    print("INSIGHTFLOW - PIPELINE DE DATA ANALYTICS")




    # Sprint 1
    df_bruto = gerar_dataset()
    df = tratar_dados(df_bruto)
    salvar_csv(df)
    carregar_sqlite(df)




    # Sprint 2
    analise_exploratoria(df)
    executar_consultas_sql()
    matriz_correlacao(df)
    outliers = detectar_outliers(df)
    rfm = segmentacao_rfm(df)




    # Sprint 3
    kpis = calcular_kpis(df)
    salvar_kpis_txt(kpis)
    vendas_diarias = gerar_visualizacoes(df, outliers)




    # Sprint 4
    previsao_df = modelo_preditivo(vendas_diarias)
    storytelling = gerar_storytelling(df, rfm, outliers, previsao_df)

    salvar_rfm(rfm)
    salvar_outliers(outliers)
    salvar_storytelling(storytelling)


    print("\nProjeto executado com sucesso.")


if __name__ == "__main__":
    main()