# adoção de gatinhos　ฅ^•ﻌ•^ฅ

> PjBL · RA1 · Data Analytics · PUCPR
> ingestão e preparação dos dados de um abrigo de gatos

Existe a crença de que gatos pretos, adultos e sem nome demoram mais pra serem adotados. Este projeto prepara dados reais do **Austin Animal Center** (Texas, EUA) pra investigar **quais características de um gato estão associadas a ele ser adotado mais rápido ou mais devagar**.

No RA1 a gente só deixa os dados limpos e confiáveis. As respostas ficam pro RA2 e RA3　(=^･ω･^=)

---

## perguntas que vamos responder

1. Gatos pretos ficam mais tempo no abrigo?
2. Como a idade na entrada (filhote, adulto, idoso) se relaciona com o tempo até a adoção?
3. Gatos que chegam sem nome esperam mais?
4. Chegar castrado muda a chance ou a velocidade de adoção?
5. A condição e o tipo de entrada influenciam o desfecho?
6. Existe sazonalidade, como uma "temporada de filhotes"?

## de onde vêm os dados　/ᐠ｡ꞈ｡ᐟ\

| base | o que é | registros (gatos) | link |
|---|---|---|---|
| Intakes | cada entrada no abrigo | 173.812 (69.324) | [wter-evkm](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes/wter-evkm) |
| Outcomes | cada saída do abrigo | 173.775 (69.399) | [9t4d-g238](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes/9t4d-g238) |

Portal de dados abertos da prefeitura de Austin, formato CSV, de 01/10/2013 a 05/05/2025.

## o caminho dos dados

```
fontes  →  ingestão  →  compreensão  →  qualidade  →  limpeza  →  dados preparados
           ingestao.py   └──── notebook 01 ────┘     notebook 02    gatos_ra1.csv
```

## como rodar　(=｀ω´=)

Precisa de **Python 3.11+** e **Java 17+** (pro Spark).

```bash
pip install -r requirements.txt
python src/ingestao.py
```

Depois, rode em ordem os notebooks `01_compreensao_e_qualidade.ipynb` e `02_limpeza_e_preparacao.ipynb`. O resultado aparece em `data/processed/gatos_ra1.csv`.

## onde está cada coisa

```
adocao-gatinhos/
├── data/
│   ├── raw/            dados brutos baixados (não editar à mão)
│   └── processed/      gatos_ra1.csv, o dataset final do RA1
├── docs/               documentação completa (ABNT)
├── notebooks/
│   ├── 01_compreensao_e_qualidade.ipynb   o que é o dado e que problemas ele tem (pandas)
│   └── 02_limpeza_e_preparacao.ipynb      tratamentos e dataset final (PySpark + Spark SQL)
├── src/
│   └── ingestao.py     baixa as duas bases
└── requirements.txt
```

## o resultado　≽^•⩊•^≼

`gatos_ra1.csv` tem **69.309 passagens** de **66.239 gatos**, uma linha por passagem pelo abrigo, com 19 colunas limpas: datas, dias no abrigo, idade em meses, faixa etária, sexo, castração, raça, cor principal, `is_black`, se tem nome, tipo e condição de entrada e desfecho.

Os problemas encontrados, cada decisão de limpeza e o dicionário de dados completo estão em [`docs/documentacao_ra1.docx`](docs/documentacao_ra1.docx).

---

<sub>Feito pela equipe do PjBL de Data Analytics · PUCPR · 2026　ฅ(^•ﻌ•^ฅ)</sub>
