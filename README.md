# adoção de gatinhos　ฅ^•ﻌ•^ฅ

> PjBL · Data Analytics · PUCPR · Ayla Micheluzzi e Gabriel Baczinski
> 
> ingestão, preparação e streaming dos dados de um abrigo de gatos

Abrigos recebem milhares de gatos por ano: uns são adotados em dias, outros esperam meses. Cada dia a mais ocupa uma vaga que outro gato precisaria, aumenta o custo do abrigo e o risco de o gato adoecer lá dentro. Existe a crença de que gatos pretos, adultos e sem nome são os que mais esperam. Se isso for verdade, os dados embasam campanhas de conscientização contra o preconceito na adoção e ajudam o abrigo a dar mais visibilidade a esses gatos.

Este projeto prepara dados reais do **Austin Animal Center** (Texas, EUA) pra investigar **quais características de um gato, quando ele chega ao abrigo, estão associadas à chance de ele ser adotado e ao tempo que ele espera até a adoção**. As características são idade, cor, sexo, castração, ter nome, condição e tipo de entrada, e o mês em que ele chega.

A raça ficou de fora: 95% dos gatos são SRD (`Domestic Shorthair`, `Medium Hair` ou `Longhair`), então quase não tem variação pra comparar. A coluna `raca` continua no dataset só como descrição.

No RA1 deixamos os dados limpos e confiáveis e no RA2 simulamos a chegada de novas adoções com Spark Structured Streaming. As respostas das perguntas ficam pras próximas etapas　(=^･ω･^=)

---

## perguntas que queremos responder

Cada linha do dataset é uma **passagem** de um gato pelo abrigo (uma entrada + a saída correspondente), de out/2013 a mai/2025. Antes das perguntas, as regras que valem pra todas:

- **tempo até a adoção** = `dias_no_abrigo` das passagens com `desfecho = "adocao"`. As adoções com subtipo `Foster` (cerca de 30%) ficam à parte, porque o tempo delas inclui dias em lar temporário, fora do abrigo.
- **chance de adoção** = % das passagens com saída que terminam em `adocao`. O `rto-adopt` não conta como adoção: num relatório da prefeitura ele aparece somado com a devolução ao dono.
- **tempo e chance andam juntos.** O tempo só conta quem foi adotado: se um grupo for mais transferido, os gatos que iam demorar saem da conta e o grupo parece adotado mais rápido. Por isso toda comparação de tempo vem junto com a chance de adoção do mesmo grupo.
- **comparação dentro da faixa etária.** Filhote é adotado mais rápido e também chega mais sem nome, sem castração e na primavera e no verão. Sem separar por idade, a diferença que aparece pode ser só a idade. Por isso as perguntas 1 e 3 a 7 comparam dentro de cada `faixa_etaria`.
- como o tempo no abrigo é muito assimétrico (a maioria sai em dias, poucos ficam meses), a comparação principal vai ser pela **mediana**, não pela média.

| # | pergunta | o que vai ser comparado | colunas |
|---|---|---|---|
| 1 | Gatos pretos esperam mais e são adotados menos do que gatos de outras cores? | chance e tempo até a adoção com `is_black` verdadeiro × falso (e os frajolas pela `cor_principal`) | `is_black`, `cor_principal` |
| 2 | Quanto mais velho o gato chega, mais ele espera? | chance e tempo até a adoção por faixa etária (filhote, adulto, idoso) | `idade_entrada_meses`, `faixa_etaria` |
| 3 | Gatos que chegam sem nome esperam mais? | chance e tempo até a adoção com e sem nome | `tem_nome`, `nome_com_asterisco` |
| 4 | Chegar já castrado aumenta a chance de adoção ou encurta a espera? E isso muda entre machos e fêmeas? | chance e tempo até a adoção, castrado × não castrado, separando machos e fêmeas | `castrado`, `sexo` |
| 5 | Gatos que chegam feridos ou doentes são adotados menos ou esperam mais? | chance e tempo até a adoção por condição de entrada | `condicao_entrada` |
| 6 | Gatos perdidos e gatos entregues pelo dono têm destinos diferentes? | distribuição dos desfechos por tipo de entrada | `tipo_entrada`, `desfecho` |
| 7 | O mês em que o gato entra muda o tempo até a adoção (ex.: a "temporada de filhotes")? | tempo até a adoção por mês de entrada | `data_entrada` |

Todas usam também `dias_no_abrigo`, `desfecho` e `faixa_etaria`.

**Até onde dá pra concluir:** os dados são de um abrigo só, de uma cidade dos EUA e de política no-kill (quase não sacrifica animais), então os resultados valem pra esse abrigo e não pra todos. E os dados mostram associação, não causa: se gato preto esperar mais, isso não prova que é por ser preto.

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

Tudo fica num notebook só, `notebooks/projeto_adocao_gatinhos.ipynb`, no formato do template da disciplina (seções 1 a 7 do RA1 e 8 a 12 do RA2):

```
fontes  →  ingestão  →  exploração e qualidade  →  limpeza  →  transformação  →  dados preparados  →  streaming
           seção 2       seção 3 (pandas)          seção 4     seção 5           seção 6             seções 8 a 12
           ingestao.py                             └──── PySpark + Spark SQL ────┘ gatos_ra1.csv    (RA2)
```

## como rodar　(=｀ω´=)

Precisa de **Python 3.11+** e **Java 17+** (pro Spark). Confira o Java antes com `java -version`: é o erro mais comum quando o Spark não sobe.

**No Windows**, o streaming do RA2 grava um checkpoint em disco, e pra isso o Spark precisa de dois arquivos do Hadoop: `winutils.exe` e `hadoop.dll`. Baixe os dois da pasta `hadoop-3.3.6/bin` do repositório [cdarlint/winutils](https://github.com/cdarlint/winutils) e coloque em `C:\hadoop\bin`. O notebook aponta pra essa pasta sozinho. Sem eles, o RA1 roda, mas o RA2 dá erro `HADOOP_HOME and hadoop.home.dir are unset`. No Linux e no Mac não precisa de nada.

```bash
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace notebooks/projeto_adocao_gatinhos.ipynb
```

A segunda linha roda o notebook inteiro sem abrir o Jupyter (leva uns 5 minutos). Se os dados brutos ainda não existirem, o próprio notebook chama o `src/ingestao.py` pra baixar; pra baixar de novo, rode `python src/ingestao.py`. O resultado do RA1 aparece em `data/processed/gatos_ra1.csv`.

Pra entregar, o notebook vira PDF: `jupyter nbconvert --to html notebooks/projeto_adocao_gatinhos.ipynb` e depois imprimir o HTML em PDF pelo navegador.

## RA2: adoções chegando em streaming　ᓚᘏᗢ

A base é estática, então simulamos a chegada de novas adoções (cenário A da disciplina). Os registros são artificiais, mas coerentes com o abrigo: as características (faixa etária, se é preto, dias de espera) são sorteadas, com semente fixa, entre as adoções reais do último ano, e a quantidade por dia segue a média real (~8 adoções de gatos por dia).

- **chegada:** 32 adoções de 06 a 08/05/2025 (logo depois que a base parou), divididas em 4 lotes que são gravados um de cada vez numa pasta, em JSON. Um lote traz uma adoção atrasada de um dia anterior.
- **processamento:** Spark Structured Streaming lendo a pasta (`readStream`, um arquivo por micro-lote).
- **janela:** tumbling de 1 dia sobre o momento da adoção, com a quantidade de adoções, quantos eram gatos pretos e a mediana de dias de espera.
- **conferência:** no fim, o resultado do streaming é comparado com a mesma conta feita em lote: tem que dar igual.

## onde está cada coisa

```
adocao-gatinhos/
├── data/
│   ├── raw/            dados brutos (CSV) e metadados (JSON) baixados; não editar à mão
│   ├── processed/      gatos_ra1.csv, o dataset final do RA1
│   └── streaming/      lotes simulados e checkpoint do RA2 (recriados a cada execução, fora do git)
├── docs/               documentação completa (template da disciplina)
├── notebooks/
│   └── projeto_adocao_gatinhos.ipynb      RA1 (ingestão, qualidade, limpeza, dataset final) e RA2 (streaming)
├── src/
│   └── ingestao.py     baixa as duas bases e confere com a API
└── requirements.txt
```

## o resultado　≽^•⩊•^≼

`gatos_ra1.csv` tem **69.309 passagens** de **66.239 gatos**, uma linha por passagem pelo abrigo, com 19 colunas limpas: datas, dias no abrigo, idade em meses, faixa etária, sexo, castração, raça, cor principal, `is_black`, se tem nome, tipo e condição de entrada e desfecho.

Os problemas encontrados, cada decisão de limpeza e o dicionário de dados completo estão em [`docs/documentacao_ra1.docx`](docs/documentacao_ra1.docx).

---

