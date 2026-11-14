# Documentação do RA3: análise estatística, visualização e Machine Learning

**Projeto:** Adoção de gatos no Austin Animal Center: características associadas à adoção
**Equipe:** Ayla Micheluzzi e Gabriel Baczinski · Bacharelado em Sistemas de Informação, 6º período, turma U · 2026/2 · Profa. Marina de Lara

Este documento resume as técnicas que usamos no RA3, os resultados e o que eles significam. O detalhe de cada passo, com o código, as tabelas e os gráficos, está em [`notebooks/ra3_analise.ipynb`](../notebooks/ra3_analise.ipynb).

---

## 1. Objetivo e dados

O RA1 definiu o problema: **quais características do gato na chegada ao abrigo estão associadas à chance de adoção e ao tempo até a adoção?** O RA1 preparou os dados e o RA2 simulou a chegada de novas adoções em streaming. No RA3 respondemos às perguntas P1 a P7.

Usamos o dataset final do RA1, `data/processed/gatos_ra1.csv`: 69.309 passagens de gatos pelo abrigo, de out/2013 a mai/2025. A partir dele montamos três recortes:

| recorte | linhas | para quê |
|---|---|---|
| passagens com saída | 68.899 | chance de adoção e Machine Learning |
| adoções | 35.433 | perfil dos adotados |
| adoções sem Foster | 25.409 | tempo até a adoção (o Foster inclui dias em lar temporário) |

Regras que valem para toda a análise (definidas no RA1):
- **chance de adoção** = % das passagens com saída que terminam em adoção;
- **tempo até a adoção** = `dias_no_abrigo` das adoções sem Foster, medido pela **mediana**;
- as comparações são feitas **dentro de cada faixa etária** (filhote, adulto, idoso), porque a idade interfere em quase todas as outras características.

## 2. Técnicas utilizadas

| técnica | onde | por que usamos |
|---|---|---|
| frequência absoluta e relativa, moda | notebook 2.1 | o desfecho é categórico |
| média, mediana, desvio-padrão, quartis, IQR, amplitude, assimetria | notebook 2.2 | descrever o tempo até a adoção e a idade, e mostrar por que a média engana |
| distribuição de frequência por faixas de dias + histograma | notebook 2.3 | ver a forma da distribuição (cauda longa) |
| comparação de grupos dentro da faixa etária (chance e mediana) | notebook 3 | responder P1 a P7 sem misturar o efeito da idade |
| diferença em relação a um grupo de referência (pontos percentuais e dias) | notebook 3.3 | comparar várias características num gráfico só |
| análise da representatividade por ano | notebook 4 | entender o que a base representa e quais vieses ela tem |
| classificação binária com separação temporal de treino e teste | notebook 5, `src/modelo.py` | prever, na chegada, se o gato vai ser adotado |
| baseline, regressão logística e random forest | notebook 5.2 | comparar um modelo simples, um linear e um que capta combinações |
| acurácia, precisão, recall, F1, AUC, matriz de confusão | notebook 5.2 e 5.3 | avaliar o modelo por vários ângulos |
| importância por permutação | notebook 5.3 | saber quais características o modelo mais usa |
| dashboard interativo (Streamlit + Altair) | `dashboard/app.py` | apresentar os indicadores, as respostas e o modelo de forma visual |

Bibliotecas: pandas, matplotlib, scikit-learn, Streamlit e Altair (versões em `requirements.txt`).

## 3. Estatística descritiva

**Desfecho.** 51,4% das passagens terminam em adoção e 38,6% em transferência para organizações parceiras. Os dois somam 90% das saídas. A moda é a adoção.

**Tempo até a adoção (sem Foster).**

| medida | valor |
|---|---|
| média | 24,7 dias |
| mediana | 13 dias |
| desvio-padrão | 29,8 dias |
| Q1 a Q3 (IQR) | 6 a 35 dias (29) |
| amplitude | 0 a 579 dias |
| assimetria | 3,7 |

**Interpretação.** A média é quase o dobro da mediana porque poucos gatos que esperam meses puxam a média para cima. Por isso usamos a mediana: metade dos gatos é adotada em até 13 dias. **71% são adotados em até 30 dias** e 97% em até 3 meses. As adoções Foster têm mediana de 55 dias, o que confirma que deviam ficar separadas. A idade também é muito assimétrica: a mediana é de 2 meses, porque dois terços dos gatos chegam filhotes.

## 4. Respostas às perguntas (visualizações)

O notebook tem 5 gráficos: o histograma do tempo e um gráfico para cada bloco de perguntas. Cada gráfico mostra lado a lado a chance de adoção e a mediana de espera.

| pergunta | resultado | interpretação |
|---|---|---|
| **P2 · idade** | chance de 57% (filhote), 40% (adulto) e 35% (idoso); mediana de 12, 14 e 20 dias | a idade é o fator que mais pesa; parte dos idosos não adotados volta ao dono (17%) ou é eutanasiada (16%) |
| **P1 · gato preto** | em todas as faixas, de 3,6 a 5,1 pontos a menos de chance; filhotes esperam 17 dias contra 11 | a crença se confirma, mas o efeito é moderado perto da idade e da saúde |
| **P3 · nome** | sem nome, a chance cai 51 pontos | é a maior diferença, mas parece **consequência** do processo: o abrigo dá nome a quem vai para adoção |
| **P4 · castração** | chegar castrado dá +6,5 pontos (filhotes) e +9,9 (adultos), e menos espera | parte do efeito pode vir de o gato castrado já ter tido dono |
| **P5 · saúde** | ferido ou doente: de 15 a 24 pontos a menos e de 9 a 18 dias a mais | precisam se recuperar antes de ficar disponíveis |
| **P6 · tipo de entrada** | perdido tem 24 (filhotes) e 36 (adultos) pontos a menos que o entregue pelo dono | não é rejeição: o perdido pode voltar ao dono ou ser transferido |
| **P7 · mês de entrada** | filhotes que entram de jan a mar esperam 5 dias; os que entram em maio, 27 | existe uma **temporada de filhotes** (abril a julho) que lota o abrigo |

Em todas as comparações, o sentido da diferença é o mesmo para filhotes e adultos, o que dá mais segurança ao resultado. São **associações, não causas**.

## 5. Amostragem e representatividade

Não usamos amostragem: as análises usam a base inteira do abrigo. Para a pergunta "o que se associa à adoção **neste abrigo**", os dados são representativos, porque são a população inteira e há milhares de casos em quase todos os grupos. Os resultados não valem automaticamente para outros abrigos.

Limitações e vieses:
- **o abrigo mudou com o tempo:** a chance de adoção subiu de 36,7% (2014) para 66,2% (2022), e as transferências caíram;
- **2020 (COVID):** metade das entradas de um ano normal, e 55% das adoções foram Foster;
- **dados censurados em 2025:** 372 passagens ainda sem saída quando a base parou;
- **um único abrigo, no-kill, no hemisfério norte:** no Brasil, a temporada de filhotes cairia em outra época;
- **colunas sem dicionário oficial:** o sentido de `*` no nome, `Disposal` e `Foster` foi deduzido por nós no RA1;
- **dados observacionais:** mostram associação, não causa.

## 6. Machine Learning

**Problema.** Quando um gato chega ao abrigo, dá para prever se ele **vai ser adotado**? Isso ajudaria o abrigo a identificar logo na entrada os gatos que precisam de mais visibilidade.

- **Tipo:** classificação binária. Descartamos a regressão dos dias porque o tempo é muito assimétrico e só existe para quem foi adotado.
- **Target:** `adotado` (1 se o desfecho é adoção).
- **Features:** só o que se sabe na chegada: idade, mês de entrada, sexo, castração, `is_black`, cor principal, raça, tipo e condição de entrada. Deixamos de fora `dias_no_abrigo`, `data_saida` e `subtipo_desfecho`, que só existem depois da saída (vazamento de dados).
- **Nome:** testado à parte, porque pode carregar a resposta (seção 4, P3).
- **Treino e teste por tempo:** o treino usa 2013 a 2022 (55.971 passagens, 48,9% adotadas) e o teste usa 2023 e 2024 (11.628 passagens, 63,2% adotadas). Isso simula o uso real, em que se aprende com o passado para prever gatos novos.
- **Preparação:** padronização das numéricas e one-hot das categóricas, num pipeline do scikit-learn (`src/modelo.py`).

**Resultados no teste (2023 e 2024).**

| versão | modelo | acurácia | precisão | recall | F1 | AUC |
|---|---|---|---|---|---|---|
| sem nome | baseline | 0,368 | 0,000 | 0,000 | 0,000 | 0,500 |
| sem nome | regressão logística | 0,716 | 0,776 | 0,775 | 0,775 | 0,747 |
| sem nome | **random forest** | **0,708** | **0,860** | **0,642** | **0,735** | **0,796** |
| com nome | regressão logística | 0,766 | 0,871 | 0,738 | 0,799 | 0,854 |
| com nome | random forest | 0,791 | 0,879 | 0,775 | 0,824 | 0,887 |

**Interpretação.**
- O **baseline** sempre prevê "não adotado", a classe mais comum no treino, e acerta só 37% no teste. Em 2023 e 2024 a adoção virou maioria: é a mudança ao longo do tempo da seção 5 aparecendo no modelo.
- **Escolhemos a random forest sem nome:** é a de maior AUC (0,80) entre os modelos que só usam o que se sabe na chegada.
- **Com nome**, o AUC sobe para 0,89. Isso confirma que o nome carrega parte da resposta, então essa versão superestima o desempenho real.
- **Importância:** idade, depois condição de entrada, tipo de entrada e castração. É a mesma ordem vista nos gráficos. `is_black` quase não muda o AUC, porque o efeito da cor é pequeno.
- **Ponto fraco:** a matriz de confusão mostra que o modelo acerta 82% dos não adotados, mas deixa passar 2.631 adotados (recall de 64%). Como aprendeu com anos em que se adotava menos, ele é pessimista com os gatos recentes. Isso se resolveria ajustando o corte de 50% ou retreinando com dados recentes.

## 7. Dashboard

O dashboard em Streamlit (`dashboard/app.py`) reúne os resultados numa interface para o abrigo consultar:
- **filtros** de ano, faixa etária e tipo de entrada; os indicadores e o gatinho da barra lateral mudam conforme a chance de adoção do recorte (média histórica, não o modelo);
- **abas:** visão geral, características (P1 a P6), temporada de filhotes (P7) e evolução por ano;
- **simulador:** o abrigo preenche os dados de um gato na chegada e a random forest do notebook (mesmo `src/modelo.py`) calcula a chance de adoção;
- **monitor diário:** mostra os lotes de adoções simulados no streaming do RA2.

## 8. Conclusões

- Metade das passagens termina em adoção (51%), e metade dos adotados sai em até 13 dias.
- As características na chegada mais associadas a menor chance e maior espera são, em ordem: **idade, saúde, tipo de entrada, não ser castrado e ser todo preto**.
- A **temporada de filhotes** (abril a julho) multiplica a espera por cinco.
- A crença sobre **gatos pretos se confirma**, mas com efeito moderado.
- O modelo ordena bem os gatos pela chance de adoção (AUC 0,80) e serve para sinalizar logo na entrada quem precisa de mais visibilidade.
- **Sugestão ao abrigo:** concentrar as campanhas nos adultos e idosos, nos gatos feridos ou doentes e no período de abril a julho.

## 9. Como executar e verificar

Pré-requisito: Python 3.11+ e o dataset do RA1 (`data/processed/gatos_ra1.csv`; se não existir, rode antes o notebook do RA1, conforme o README). O RA3 não precisa de Spark nem de Java.

```bash
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace notebooks/ra3_analise.ipynb
streamlit run dashboard/app.py
```

- A segunda linha executa o notebook inteiro, em menos de 1 minuto. Os números deste documento devem aparecer iguais nas saídas das células, porque a separação de treino e teste é fixa e a random forest usa `random_state=42`.
- A terceira abre o dashboard em `http://localhost:8501`. Para conferir o simulador, informe um idoso de 12 anos, doente e perdido: a chance sai baixa. Depois, um filhote de 2 meses, normal, entregue pelo dono e castrado: a chance sai alta.
- A aba "monitor diário" só mostra dados depois que o notebook do RA2 gera os lotes em `data/streaming/`.

| arquivo | conteúdo |
|---|---|
| `notebooks/ra3_analise.ipynb` | estatística, gráficos, representatividade, ML e conclusões |
| `src/modelo.py` | preparação dos dados, separação temporal e modelos (usado pelo notebook e pelo dashboard) |
| `dashboard/app.py`, `dashboard/kawaii.py`, `dashboard/assets/` | dashboard, visual e imagens |
| `.streamlit/config.toml` | tema do dashboard |
