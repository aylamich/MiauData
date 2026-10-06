# adoção de gatinhos　ฅ^•ﻌ•^ฅ

> PjBL · Data Analytics · PUCPR
> ingestão e preparação dos dados de um abrigo de gatos

Existe a crença de que gatos pretos, adultos e sem nome demoram mais pra serem adotados. Este projeto prepara dados reais do **Austin Animal Center** (Texas, EUA) pra investigar **quais características de um gato estão associadas a ele ser adotado mais rápido ou mais devagar**.

No RA1 eu só deixo os dados limpos e confiáveis. As respostas ficam pro RA2 e RA3　(=^･ω･^=)

---

## perguntas que quero responder

Cada linha do dataset é uma **passagem** de um gato pelo abrigo (uma entrada + a saída correspondente), de out/2013 a mai/2025. Antes das perguntas, três definições que valem pra todas:

- **tempo até a adoção** = `dias_no_abrigo` das passagens com `desfecho = "adocao"`. As adoções com subtipo `Foster` (cerca de 30%) ficam à parte, porque o tempo delas inclui dias em lar temporário, fora do abrigo.
- **chance de adoção** = % das passagens com saída que terminam em `adocao`. O `rto-adopt` não conta como adoção: num relatório da prefeitura ele aparece somado com a devolução ao dono.
- como o tempo no abrigo é muito assimétrico (a maioria sai em dias, poucos ficam meses), a comparação principal vai ser pela **mediana**, não pela média.

| # | pergunta | o que vai ser comparado | colunas |
|---|---|---|---|
| 1 | Gatos pretos esperam mais pela adoção do que gatos de outras cores? | tempo até a adoção com `is_black` verdadeiro × falso (e os frajolas pela `cor_principal`) | `is_black`, `cor_principal` |
| 2 | Quanto mais velho o gato chega, mais ele espera? | tempo até a adoção por faixa etária (filhote, adulto, idoso) | `idade_entrada_meses`, `faixa_etaria` |
| 3 | Gatos que chegam sem nome esperam mais? | tempo até a adoção com e sem nome | `tem_nome`, `nome_com_asterisco` |
| 4 | Chegar já castrado aumenta a chance de adoção ou encurta a espera? | chance e tempo até a adoção, castrado × não castrado (só sexo conhecido) | `castrado`, `sexo` |
| 5 | Gatos que chegam feridos ou doentes são adotados menos ou esperam mais? | chance e tempo até a adoção por condição de entrada | `condicao_entrada` |
| 6 | Gatos perdidos e gatos entregues pelo dono têm destinos diferentes? | distribuição dos desfechos por tipo de entrada | `tipo_entrada`, `desfecho` |
| 7 | O mês em que o gato entra muda o tempo até a adoção (ex.: a "temporada de filhotes")? | tempo até a adoção por mês de entrada | `data_entrada`, `faixa_etaria` |

Todas usam também `dias_no_abrigo` e `desfecho`.

## de onde vêm os dados　/ᐠ｡ꞈ｡ᐟ\

| base | o que é | registros (gatos) | link |
|---|---|---|---|
| Intakes | cada entrada no abrigo | 173.812 (69.324) | [wter-evkm](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes/wter-evkm) |
| Outcomes | cada saída do abrigo | 173.775 (69.399) | [9t4d-g238](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes/9t4d-g238) |

Portal de dados abertos da prefeitura de Austin (plataforma Socrata). Os dados vêm em CSV e os metadados de cada base em JSON, pela API do portal.

As duas bases estão **congeladas**: cobrem de 01/10/2013 a 05/05/2025, e os metadados mostram que os dados não mudam desde 19/05/2025. Por isso aparecem gatos que entraram e ainda não tinham saído quando a base parou.

## como os dados entram

`python src/ingestao.py` faz tudo de uma vez:

1. baixa o export CSV de cada base em pedaços de 1 MB, sem carregar o arquivo inteiro na memória;
2. baixa os metadados em JSON (título, período, data da última atualização, tipos das colunas);
3. pede pra API a contagem de linhas e compara com o que foi baixado, pra garantir que o download veio inteiro;
4. grava a data do download e as contagens em `data/raw/info_download.txt`.

**Por que em lote e não em streaming?** Como as bases estão congeladas, não chega dado novo, então não existe fluxo pra acompanhar. Uma carga única resolve, e o resultado é sempre o mesmo.

**Por que os dados vêm do CSV e não da API JSON?** O CSV mantém os formatos originais das colunas. Na API, a data das entradas já vem convertida (`2013-10-01T07:51:00.000` em vez de `10/01/2013 07:51:00 AM`), e o campo some do JSON quando está vazio. Essa bagunça de formatos é justamente o que o RA1 precisa avaliar, então faz sentido pegar o dado do jeito que ele é publicado. A API entra onde ela é melhor: metadados e conferência.

## o caminho dos dados

```
fontes  →  ingestão  →  compreensão  →  qualidade  →  limpeza  →  dados preparados
           ingestao.py   └──── notebook 01 ────┘     notebook 02    gatos_ra1.csv
```

## como rodar　(=｀ω´=)

Precisa de **Python 3.11+** e **Java 17+** (pro Spark). Confira o Java antes com `java -version`: é o erro mais comum quando o notebook 02 não roda.

```bash
pip install -r requirements.txt
python src/ingestao.py
jupyter nbconvert --to notebook --execute --inplace notebooks/01_compreensao_e_qualidade.ipynb notebooks/02_limpeza_e_preparacao.ipynb
```

A última linha roda os dois notebooks em ordem, sem precisar abrir o Jupyter (leva uns 3 minutos, quase tudo no 02). Se preferir, dá pra abrir e rodar célula por célula. O resultado aparece em `data/processed/gatos_ra1.csv`.

## onde está cada coisa

```
adocao-gatinhos/
├── data/
│   ├── raw/            dados brutos (CSV) e metadados (JSON) baixados; não editar à mão
│   └── processed/      gatos_ra1.csv, o dataset final do RA1
├── docs/               documentação completa (ABNT)
├── notebooks/
│   ├── 01_compreensao_e_qualidade.ipynb   o que é o dado e que problemas ele tem (pandas)
│   └── 02_limpeza_e_preparacao.ipynb      tratamentos e dataset final (PySpark + Spark SQL)
├── src/
│   └── ingestao.py     baixa as duas bases e confere com a API
└── requirements.txt
```

## o resultado　≽^•⩊•^≼

`gatos_ra1.csv` tem **69.309 passagens** de **66.239 gatos**, uma linha por passagem pelo abrigo, com 19 colunas limpas: datas, dias no abrigo, idade em meses, faixa etária, sexo, castração, raça, cor principal, `is_black`, se tem nome, tipo e condição de entrada e desfecho.

Os problemas encontrados, cada decisão de limpeza e o dicionário de dados completo estão em [`docs/documentacao_ra1.docx`](docs/documentacao_ra1.docx).

---

