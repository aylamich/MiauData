# Dashboard do projeto (RA3): indicadores de adoção de gatos do Austin Animal Center.
# Rodar da pasta do projeto: streamlit run dashboard/app.py
# Lê o dataset do RA1 (data/processed/gatos_ra1.csv) e usa o mesmo modelo do notebook do RA3 (src/modelo.py).
# O visual (cores, CSS e as expressões do gatinho) fica em dashboard/kawaii.py e as imagens em dashboard/assets.

import base64
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from sklearn.metrics import accuracy_score, roc_auc_score

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = Path(__file__).resolve().parent / "assets"
sys.path.append(str(RAIZ / "src"))
sys.path.append(str(Path(__file__).resolve().parent))
import kawaii  # noqa: E402
import modelo  # noqa: E402

FAIXAS = ["filhote", "adulto", "idoso"]
CORES_FAIXA = alt.Scale(domain=FAIXAS, range=kawaii.CORES_FAIXAS)
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

st.set_page_config(page_title="MiauData ฅ^•ﻌ•^ฅ", layout="wide")
st.markdown(kawaii.CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- dados e modelo
@st.cache_data
def carregar():
    gatos = modelo.carregar_gatos()
    com_saida = gatos[gatos["desfecho"] != "sem_saida"].copy()
    com_saida["adotado"] = com_saida["desfecho"] == "adocao"
    com_saida["foster"] = com_saida["subtipo_desfecho"] == "Foster"
    # tempo até a adoção: só adoções diretas (o Foster inclui dias em lar temporário)
    com_saida["dias_ate_adocao"] = com_saida["dias_no_abrigo"].where(com_saida["adotado"] & ~com_saida["foster"])
    com_saida["ano"] = com_saida["data_entrada"].dt.year
    com_saida["mes"] = com_saida["data_entrada"].dt.month
    return gatos, com_saida


@st.cache_resource
def treinar_modelo():
    """Random forest sem nome, treinada até 2022 e avaliada em 2023-2024 (igual ao notebook, seção 5.3)."""
    base = modelo.preparar_base_ml(modelo.carregar_gatos())
    treino, teste = modelo.separar_treino_teste(base)
    colunas = modelo.features(usa_nome=False)
    m = modelo.criar_modelo("random_forest", usa_nome=False).fit(treino[colunas], treino["adotado"])
    prob = m.predict_proba(teste[colunas])[:, 1]
    metricas = {
        "AUC": roc_auc_score(teste["adotado"], prob),
        "acurácia": accuracy_score(teste["adotado"], prob >= 0.5),
    }
    return m, metricas, base


@st.cache_data
def imagem_base64(nome):
    return base64.b64encode((ASSETS / nome).read_bytes()).decode()


def indicadores(df, colunas):
    t = df.groupby(colunas, observed=True).agg(
        passagens=("adotado", "size"),
        chance_adocao=("adotado", "mean"),
        mediana_dias=("dias_ate_adocao", "median"),
    ).reset_index()
    t["chance_adocao"] = (100 * t["chance_adocao"]).round(1)
    return t


def fofo(grafico, altura=320):
    """Aplica o estilo do dashboard (fonte, cores suaves e sem bordas) a um gráfico do Altair."""
    return (
        grafico.properties(height=altura)
        .configure(font=kawaii.FONTE, background=kawaii.CARTAO)
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor=kawaii.TEXTO_SUAVE, titleColor=kawaii.TEXTO_SUAVE, gridColor=kawaii.GRADE,
                        domainColor=kawaii.BORDA, tickColor=kawaii.BORDA, labelFontSize=12, titleFontSize=12)
        .configure_legend(labelColor=kawaii.TEXTO, titleColor=kawaii.TEXTO_SUAVE, symbolType="circle")
    )


def balao(texto):
    st.markdown(f'<div class="balao">{texto}</div>', unsafe_allow_html=True)


gatos, com_saida = carregar()

# ---------------------------------------------------------------- filtros
st.sidebar.markdown("## filtrinhos")
ano_min, ano_max = int(com_saida["ano"].min()), int(com_saida["ano"].max())
anos = st.sidebar.slider("ano de entrada", ano_min, ano_max, (ano_min, ano_max))
faixas = st.sidebar.multiselect("faixa etária", FAIXAS, default=FAIXAS)
tipos = st.sidebar.multiselect("tipo de entrada", sorted(com_saida["tipo_entrada"].unique()),
                               default=sorted(com_saida["tipo_entrada"].unique()))
st.sidebar.caption("os filtros valem para as abas de análise. o simulador usa o modelo treinado com 2013-2022.")

dados = com_saida[
    com_saida["ano"].between(*anos) & com_saida["faixa_etaria"].isin(faixas) & com_saida["tipo_entrada"].isin(tipos)
]

# ---------------------------------------------------------------- capa
st.markdown(f"""
<div class="capa">
  <img class="gata" src="data:image/png;base64,{imagem_base64('gata_sorrindo.png')}">
  <div>
    <div class="titulo">MiauData</div>
    <div class="sub"><b>adoção de gatinhos no Austin Animal Center</b> · out/2013 a mai/2025</div>
    <div class="sub">Ayla Micheluzzi e Gabriel Baczinski · Data Analytics 2026/2</div>
    <div class="kaomoji">quem espera mais por um lar?　ฅ^•ﻌ•^ฅ</div>
  </div>
  <img class="andando" src="data:image/gif;base64,{imagem_base64('gatinho_pixel.gif')}">
</div>
""", unsafe_allow_html=True)

if dados.empty:
    st.warning("nenhum gatinho com esses filtros")
    st.stop()

# o gatinho da barra lateral muda de expressão com a chance de adoção dos filtros
chance_geral = dados["adotado"].mean()
humor_geral = kawaii.humor_da_chance(chance_geral)
st.sidebar.markdown(
    f'<div class="humor"><img src="data:image/png;base64,{imagem_base64(f"gato_{humor_geral}.png")}">'
    f'<div class="pct">{100 * chance_geral:.1f}%</div>'
    f'<div class="legenda">chance de adoção com esses filtros</div></div>',
    unsafe_allow_html=True,
)

pretos = dados[dados["is_black"]]
chance_pretos = f"{100 * pretos['adotado'].mean():.1f}%" if len(pretos) else "–"
diferenca_pretos = (f"{100 * (pretos['adotado'].mean() - dados['adotado'].mean()):+.1f} pontos vs. todos"
                    if len(pretos) else "")
cards = [
    (kawaii.ROSA_CLARO, "passagens com saída", f"{len(dados):,}".replace(",", "."), "cada entrada + saída de um gatinho", ""),
    (kawaii.ROSA, "chance de adoção", f"{100 * chance_geral:.1f}%", "das passagens terminam em lar", ""),
    (kawaii.AZUL, "mediana até a adoção", f"{dados['dias_ate_adocao'].median():.0f} dias",
     "metade é adotada até aqui (sem Foster)", ""),
    (kawaii.SALVIA, "chance dos gatinhos pretos", chance_pretos, diferenca_pretos, ""),
]
st.markdown(
    '<div class="cards">' + "".join(
        f'<div class="card" style="--cor:{cor}">{extra}'
        f'<div class="rotulo">{rotulo}</div><div class="valor">{valor}</div><div class="nota">{nota}</div></div>'
        for cor, rotulo, valor, nota, extra in cards
    ) + "</div>",
    unsafe_allow_html=True,
)

aba_geral, aba_carac, aba_mes, aba_ano, aba_sim, aba_stream = st.tabs([
    "visão geral", "características", "temporada de filhotes", "evolução", "simulador", "monitor diário",
])

# ---------------------------------------------------------------- visão geral
with aba_geral:
    esq, dir_ = st.columns(2)
    dias = dados["dias_ate_adocao"].dropna()
    with esq:
        st.markdown("### quanto tempo até o lar?")
        hist = alt.Chart(pd.DataFrame({"dias": dias[dias <= 180]})).mark_bar(
            color=kawaii.ROSA_CLARO, cornerRadiusTopLeft=3, cornerRadiusTopRight=3
        ).encode(
            alt.X("dias:Q", bin=alt.Bin(step=3), title="dias entre a entrada e a adoção"),
            alt.Y("count():Q", title="adoções"),
        )
        regra = alt.Chart(pd.DataFrame({"mediana": [dias.median()]})).mark_rule(
            color=kawaii.TEXTO, strokeDash=[6, 4], strokeWidth=1.5).encode(x="mediana:Q")
        st.altair_chart(fofo(hist + regra), use_container_width=True)
        balao(f"a linha tracejada é a <b>mediana ({dias.median():.0f} dias)</b>. a média é {dias.mean():.1f} dias, "
              f"puxada pelos poucos que esperam meses, por isso usamos a mediana.")
    with dir_:
        st.markdown("### para onde vão os gatinhos")
        destinos = (100 * dados["desfecho"].value_counts(normalize=True)).round(1).rename("pct").reset_index()
        st.altair_chart(fofo(alt.Chart(destinos).mark_bar(
            color=kawaii.AZUL, cornerRadiusTopRight=6, cornerRadiusBottomRight=6
        ).encode(
            alt.X("pct:Q", title="% das passagens com saída"),
            alt.Y("desfecho:N", sort="-x", title=None),
            tooltip=["desfecho", "pct"],
        )), use_container_width=True)
        balao("mais da metade encontra um lar e quase todo o resto é transferido para parceiros do abrigo.")
    st.markdown("### por faixa etária")
    st.table(indicadores(dados, "faixa_etaria").set_index("faixa_etaria").reindex([f for f in FAIXAS if f in faixas]))

# ---------------------------------------------------------------- características
with aba_carac:
    opcoes = {
        "gatinho todo preto (P1)": ("is_black", {True: "preto", False: "outras cores"}),
        "tem nome (P3)": ("tem_nome", {True: "com nome", False: "sem nome"}),
        "castrado na chegada (P4)": ("castrado", {True: "castrado", False: "não castrado"}),
        "condição de entrada (P5)": ("condicao_entrada", None),
        "tipo de entrada (P6)": ("tipo_entrada", None),
        "sexo": ("sexo", None),
    }
    escolha = st.selectbox("comparar por", list(opcoes))
    coluna, rotulos = opcoes[escolha]
    d = dados.dropna(subset=[coluna]).copy()
    d["grupo"] = d[coluna].map(rotulos) if rotulos else d[coluna]
    t = indicadores(d, ["faixa_etaria", "grupo"])
    t = t[t["passagens"] >= 30]  # grupos muito pequenos enganam

    def barras(campo, titulo):
        return fofo(alt.Chart(t).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            alt.X("grupo:N", title=None, axis=alt.Axis(labelAngle=-30)),
            alt.Y(f"{campo}:Q", title=titulo),
            alt.Color("faixa_etaria:N", scale=CORES_FAIXA, title="faixa etária"),
            alt.XOffset("faixa_etaria:N", sort=FAIXAS),
            tooltip=["faixa_etaria", "grupo", "passagens", "chance_adocao", "mediana_dias"],
        ))

    esq, dir_ = st.columns(2)
    esq.markdown("### chance de adoção")
    esq.altair_chart(barras("chance_adocao", "chance de adoção (%)"), use_container_width=True)
    dir_.markdown("### mediana de dias até a adoção")
    dir_.altair_chart(barras("mediana_dias", "dias"), use_container_width=True)
    balao("comparamos <b>dentro de cada faixa etária</b>, porque a idade mexe em quase tudo. grupos com menos de 30 "
          "passagens ficam de fora, e lembrando: são associações, não causas.")

# ---------------------------------------------------------------- temporada
with aba_mes:
    t = indicadores(dados, ["faixa_etaria", "mes"])
    t["mês"] = t["mes"].map(lambda m: MESES[m - 1])
    base_mes = alt.Chart(t).encode(
        alt.X("mês:N", sort=MESES, title=None),
        alt.Color("faixa_etaria:N", scale=CORES_FAIXA, title="faixa etária"),
        tooltip=["faixa_etaria", "mês", "passagens", "chance_adocao", "mediana_dias"],
    )
    linha = dict(point=alt.OverlayMarkDef(size=50, filled=True), strokeWidth=2.5)
    esq, dir_ = st.columns(2)
    esq.markdown("### entradas por mês")
    esq.altair_chart(fofo(base_mes.mark_line(**linha).encode(alt.Y("passagens:Q", title="passagens"))),
                     use_container_width=True)
    dir_.markdown("### mediana de dias até a adoção")
    dir_.altair_chart(fofo(base_mes.mark_line(**linha).encode(alt.Y("mediana_dias:Q", title="dias"))),
                      use_container_width=True)
    balao("de <b>abril a julho</b> chega uma enxurrada de filhotes e a espera de todo mundo aumenta: "
          "é a época que mais precisa de campanhas de adoção e lares temporários.")

# ---------------------------------------------------------------- evolução
with aba_ano:
    t = indicadores(dados, "ano")
    t["transferência"] = (100 * dados.groupby("ano")["desfecho"].apply(lambda s: (s == "transferencia").mean())).round(1).values
    t = t.rename(columns={"chance_adocao": "adoção"})
    longo = t.melt(id_vars="ano", value_vars=["adoção", "transferência"], var_name="indicador", value_name="%")
    st.markdown("### adoção x transferência ao longo dos anos")
    st.altair_chart(fofo(alt.Chart(longo).mark_line(point=alt.OverlayMarkDef(size=50, filled=True), strokeWidth=2.5).encode(
        alt.X("ano:O", title="ano de entrada"),
        alt.Y("%:Q", title="% das passagens com saída"),
        alt.Color("indicador:N", title=None, scale=alt.Scale(range=[kawaii.ROSA, kawaii.AZUL])),
        tooltip=["ano", "indicador", "%"],
    ), altura=360), use_container_width=True)
    balao("a adoção foi ganhando espaço das transferências, então um resultado médio de 12 anos mistura "
          "épocas diferentes. 2020 teve metade das entradas (COVID) e 2025 vai só até maio.")

# ---------------------------------------------------------------- simulador
with aba_sim:
    m, metricas, base = treinar_modelo()
    st.markdown("### qual a chance desse gatinho ser adotado?")
    balao("conta pra gente o que o abrigo sabe <b>na chegada</b> do gatinho. o modelo (random forest, sem o nome) "
          f"aprendeu com 2013-2022 e foi testado em 2023-2024: <b>AUC {metricas['AUC']:.2f}</b>, "
          f"acerta {100 * metricas['acurácia']:.0f}% dos casos.")
    with st.form("simulador"):
        a, b, c = st.columns(3)
        idade_valor = a.number_input("idade", min_value=0.0, max_value=25.0, value=2.0, step=0.5)
        idade_unidade = a.radio("unidade", ["meses", "anos"], horizontal=True)
        sexo = a.selectbox("sexo", ["macho", "femea", "desconhecido"])
        castrado = b.selectbox("castrado na chegada", ["nao", "sim", "desconhecido"])
        cores_lista = sorted(base["cor_principal"].unique())
        cor = b.selectbox("cor principal", cores_lista, index=cores_lista.index("Brown Tabby"))
        todo_preto = b.checkbox("todo pretinho", value=False)
        tipos_lista = sorted(base["tipo_entrada"].dropna().unique())
        tipo = c.selectbox("tipo de entrada", tipos_lista, index=tipos_lista.index("perdido"))
        condicoes = sorted(base["condicao_entrada"].unique())
        condicao = c.selectbox("condição de entrada", condicoes, index=condicoes.index("normal"))
        mes = c.selectbox("mês de entrada", range(1, 13), format_func=lambda i: MESES[i - 1], index=4)
        enviado = st.form_submit_button("calcular chance")

    if enviado:
        if todo_preto:
            cor = "Black"
        gato = pd.DataFrame([{
            "idade_entrada_meses": idade_valor * (12 if idade_unidade == "anos" else 1),
            "mes_entrada": mes, "sexo": sexo, "castrado": castrado, "is_black": todo_preto,
            "cor_principal": cor, "raca": "Domestic Shorthair", "tipo_entrada": tipo, "condicao_entrada": condicao,
        }])
        prob = m.predict_proba(gato[modelo.features(usa_nome=False)])[0, 1]
        media = base["adotado"].mean()
        humor = kawaii.humor_da_chance(prob)
        cor_borda = {"feliz": kawaii.SALVIA, "normal": kawaii.AZUL, "triste": kawaii.ROSA}[humor]
        st.markdown(f"""
        <div class="resultado" style="--cor:{cor_borda}">
          <img src="data:image/png;base64,{imagem_base64(f'gato_{humor}.png')}">
          <div>
            <div class="pct">{100 * prob:.0f}%</div>
            <div class="frase">{kawaii.FRASES[humor]}</div>
            <div class="nota">{100 * (prob - media):+.0f} pontos em relação à média histórica ({100 * media:.0f}%)</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("estimativa de um modelo treinado com 2013-2022: mostra associação, não causa. "
                   "raça fixada em Domestic Shorthair (95% dos gatos).")

# ---------------------------------------------------------------- monitor RA2
with aba_stream:
    pasta = RAIZ / "data" / "streaming" / "adocoes"
    arquivos = sorted(pasta.glob("*.json")) if pasta.exists() else []
    st.markdown("### monitor diário de adoções (simulação do RA2)")
    if not arquivos:
        balao("nenhum lote por aqui ainda. rode a seção do RA2 do notebook projeto_adocao_gatinhos.ipynb "
              "para gerar os lotes simulados em data/streaming/adocoes.")
    else:
        lotes = pd.concat([pd.read_json(a, lines=True).assign(lote=a.stem) for a in arquivos])
        lotes["dia"] = pd.to_datetime(lotes["momento_adocao"]).dt.strftime("%d/%m/%Y")
        # a mesma janela tumbling de 1 dia do RA2, aqui em pandas sobre os lotes que já chegaram
        diario = lotes.groupby("dia").agg(
            adocoes=("id_adocao", "count"),
            gatos_pretos=("is_black", "sum"),
            mediana_dias_espera=("dias_no_abrigo", "median"),
        ).reset_index()
        diario["pct_pretos"] = (100 * diario["gatos_pretos"] / diario["adocoes"]).round(1)
        balao(f"<b>{len(arquivos)} lotes</b> recebidos, <b>{len(lotes)} adoções</b> simuladas, agrupadas na mesma "
              "janela de 1 dia do streaming do RA2.")
        st.altair_chart(fofo(alt.Chart(diario).mark_bar(
            color=kawaii.SALVIA, cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=60
        ).encode(
            alt.X("dia:N", title=None), alt.Y("adocoes:Q", title="adoções no dia"),
            tooltip=list(diario.columns),
        ), altura=260), use_container_width=True)
        st.table(diario.set_index("dia"))

st.markdown('<div class="rodape">feito com carinho por Ayla e Gabriel · dados abertos da prefeitura de Austin · '
            'ฅ^•ﻌ•^ฅ</div>', unsafe_allow_html=True)
