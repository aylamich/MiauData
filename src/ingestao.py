# Baixa as bases de entradas e saidas do Austin Animal Center (portal de dados abertos
# da cidade de Austin) e salva os CSVs brutos em data/raw.
# Rodar da raiz do projeto: python src/ingestao.py

from datetime import date
from pathlib import Path

import pandas as pd
import requests
import truststore

# usa os certificados do sistema operacional; sem isso deu erro de SSL num PC
# com antivirus (AVG) que intercepta o HTTPS
truststore.inject_into_ssl()

PASTA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# IDs dos datasets no portal (Socrata). O export rows.csv mantem os nomes
# originais das colunas ("Animal ID", "DateTime"...), igual ao que aparece no site.
BASES = {
    "intakes": "wter-evkm",
    "outcomes": "9t4d-g238",
}
URL = "https://data.austintexas.gov/api/views/{id}/rows.csv?accessType=DOWNLOAD"


def baixar(nome, dataset_id):
    destino = PASTA_RAW / f"{nome}.csv"
    print(f"Baixando {nome} ({dataset_id})...")

    # arquivo tem dezenas de MB, entao baixa em pedacos em vez de tudo na memoria
    resp = requests.get(URL.format(id=dataset_id), stream=True, timeout=120)
    resp.raise_for_status()
    with open(destino, "wb") as f:
        for pedaco in resp.iter_content(chunk_size=1024 * 1024):
            f.write(pedaco)

    # le de volta so pra conferir se veio inteiro
    df = pd.read_csv(destino, dtype=str)
    print(f"  {len(df):,} linhas x {df.shape[1]} colunas -> {destino.name}")
    return len(df)


if __name__ == "__main__":
    PASTA_RAW.mkdir(parents=True, exist_ok=True)

    linhas = {nome: baixar(nome, id_) for nome, id_ in BASES.items()}

    # guarda quando e quanto foi baixado, ja que o portal pode mudar
    with open(PASTA_RAW / "info_download.txt", "w", encoding="utf-8") as f:
        f.write(f"data do download: {date.today()}\n")
        for nome, n in linhas.items():
            f.write(f"{nome} ({BASES[nome]}): {n} linhas\n")

    print("Pronto!")
