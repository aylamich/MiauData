# Baixa as bases de entradas e saidas do Austin Animal Center (portal de dados abertos
# da cidade de Austin) e salva os arquivos brutos em data/raw.
# Rodar da raiz do projeto: python src/ingestao.py
#
# Para cada base sao duas coisas:
#   - os dados, pelo export CSV do portal (mantem os nomes e formatos originais das colunas)
#   - os metadados, pela API JSON do portal (periodo coberto, ultima atualizacao, tipos das colunas)
# No fim, conferimos a contagem baixada com a contagem que a API informa.

import json
from datetime import date, datetime
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
PORTAL = "https://data.austintexas.gov"
URL_CSV = PORTAL + "/api/views/{id}/rows.csv?accessType=DOWNLOAD"
URL_METADADOS = PORTAL + "/api/views/{id}.json"
URL_API = PORTAL + "/resource/{id}.json"


def baixar_csv(nome, dataset_id):
    destino = PASTA_RAW / f"{nome}.csv"
    print(f"Baixando {nome} ({dataset_id})...")

    # arquivo tem dezenas de MB, entao baixa em pedacos em vez de tudo na memoria
    resp = requests.get(URL_CSV.format(id=dataset_id), stream=True, timeout=120)
    resp.raise_for_status()
    with open(destino, "wb") as f:
        for pedaco in resp.iter_content(chunk_size=1024 * 1024):
            f.write(pedaco)

    # conta as linhas lendo em blocos, pelo mesmo motivo: nao precisa do arquivo inteiro na memoria
    linhas = sum(len(bloco) for bloco in pd.read_csv(destino, dtype=str, chunksize=50_000))
    print(f"  {linhas:,} linhas -> {destino.name}")
    return linhas


def baixar_metadados(nome, dataset_id):
    # JSON com o "cadastro" do dataset no portal: titulo, descricao, colunas e datas de atualizacao
    meta = requests.get(URL_METADADOS.format(id=dataset_id), timeout=60).json()
    with open(PASTA_RAW / f"metadados_{nome}.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    atualizado = datetime.fromtimestamp(meta["rowsUpdatedAt"]).date()
    print(f"  metadados: \"{meta['name']}\", dados atualizados em {atualizado}")
    return atualizado


def linhas_no_portal(dataset_id):
    # a API aceita consultas no estilo SQL (SoQL); aqui so pedimos a contagem
    resp = requests.get(URL_API.format(id=dataset_id), params={"$select": "count(*)"}, timeout=60)
    return int(resp.json()[0]["count"])


if __name__ == "__main__":
    PASTA_RAW.mkdir(parents=True, exist_ok=True)

    resumo = []
    for nome, id_ in BASES.items():
        baixadas = baixar_csv(nome, id_)
        atualizado = baixar_metadados(nome, id_)
        no_portal = linhas_no_portal(id_)

        # se o download tivesse sido cortado no meio, a contagem nao bateria
        situacao = "ok" if baixadas == no_portal else "DIFERENTE, baixar de novo"
        print(f"  portal informa {no_portal:,} linhas: {situacao}")
        resumo.append(f"{nome} ({id_}): {baixadas} linhas | portal: {no_portal} | "
                      f"dados atualizados no portal em {atualizado}")

    # guarda quando e quanto foi baixado, ja que o portal pode mudar
    with open(PASTA_RAW / "info_download.txt", "w", encoding="utf-8") as f:
        f.write(f"data do download: {date.today()}\n")
        f.write("\n".join(resumo) + "\n")

    print("Pronto!")
