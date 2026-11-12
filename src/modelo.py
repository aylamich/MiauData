# Preparação dos dados e criação do modelo de ML do RA3.
# Usado pelo notebook notebooks/ra3_analise.ipynb e pelo dashboard (dashboard/app.py),
# para que os dois usem exatamente as mesmas features e o mesmo modelo.

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CSV_RA1 = Path(__file__).resolve().parent.parent / "data" / "processed" / "gatos_ra1.csv"

# features: só o que se sabe na chegada do gato (nada da saída, para não vazar a resposta)
NUMERICAS = ["idade_entrada_meses", "mes_entrada"]
CATEGORICAS = ["sexo", "castrado", "is_black", "cor_principal", "raca", "tipo_entrada", "condicao_entrada"]
# o nome parece ser dado pelo abrigo a quem vai para adoção (RA3, seção 3.3): fica opcional
NOME = ["tem_nome", "nome_com_asterisco"]

# separação temporal: treina no passado e testa em gatos "novos"
# (2025 fica de fora: as passagens ainda sem saída deixariam o teste só com saídas rápidas)
FIM_TREINO = "2023-01-01"
FIM_TESTE = "2025-01-01"


def carregar_gatos(caminho=CSV_RA1):
    return pd.read_csv(caminho, parse_dates=["data_entrada", "data_saida"])


def preparar_base_ml(gatos):
    """Passagens com saída, com o target `adotado` (1/0) e as features prontas."""
    base = gatos[gatos["desfecho"] != "sem_saida"].dropna(subset=["idade_entrada_meses"]).copy()
    base["adotado"] = (base["desfecho"] == "adocao").astype(int)
    base["mes_entrada"] = base["data_entrada"].dt.month
    # castração desconhecida vira uma categoria própria, em vez de apagar 5 mil linhas
    base["castrado"] = base["castrado"].map({True: "sim", False: "nao"}).fillna("desconhecido")
    return base


def separar_treino_teste(base):
    treino = base[base["data_entrada"] < FIM_TREINO]
    teste = base[(base["data_entrada"] >= FIM_TREINO) & (base["data_entrada"] < FIM_TESTE)]
    return treino, teste


def features(usa_nome):
    return NUMERICAS + CATEGORICAS + (NOME if usa_nome else [])


def criar_modelo(tipo, usa_nome):
    """Pipeline: padroniza os números, transforma as categorias em colunas 0/1 e treina o modelo."""
    categoricas = CATEGORICAS + (NOME if usa_nome else [])
    preparo = ColumnTransformer([
        ("numericas", StandardScaler(), NUMERICAS),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), categoricas),
    ])
    if tipo == "regressao_logistica":
        modelo = LogisticRegression(max_iter=2000)
    elif tipo == "random_forest":
        # folhas com no mínimo 20 gatos: evita decorar casos isolados
        modelo = RandomForestClassifier(n_estimators=300, min_samples_leaf=20, n_jobs=-1, random_state=42)
    else:
        raise ValueError(tipo)
    return make_pipeline(preparo, modelo)
