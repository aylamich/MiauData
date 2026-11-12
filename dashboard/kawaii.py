# Visual do dashboard: paleta, CSS e a escolha da expressão do gatinho
# conforme a chance de adoção (imagens em dashboard/assets/gato_*.png).

# ---------------------------------------------------------------- paleta
# tons suaves e pouco saturados, com fundo acinzentado (sem branco puro), para não cansar a vista
FUNDO = "#ECE9EB"
CARTAO = "#F6F4F5"
BORDA = "#E0DADD"
TEXTO = "#3E3A3C"
TEXTO_SUAVE = "#7A7276"
ROSA = "#D9799B"
ROSA_CLARO = "#EBC3D1"
AZUL = "#9FC0D6"
SALVIA = "#A9CDB3"
AREIA = "#E3C9A8"
GRADE = "#E6E0E3"

# cores das faixas etárias nos gráficos
CORES_FAIXAS = [ROSA_CLARO, AZUL, SALVIA]

FONTE = "M PLUS Rounded 1c"


# ---------------------------------------------------------------- expressões do gatinho
def humor_da_chance(prob):
    # a média histórica é ~51%: abaixo de 50% já é triste, a partir de 55% já é feliz
    if prob >= 0.55:
        return "feliz"
    if prob >= 0.50:
        return "normal"
    return "triste"


FRASES = {
    "feliz": "chance alta, esse gatinho deve achar um lar logo",
    "normal": "chance no meio do caminho, um empurrãozinho ajuda",
    "triste": "chance baixa, esse gatinho precisa de mais visibilidade (fotos, redes sociais, feiras de adoção)",
}

# ---------------------------------------------------------------- CSS
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800&display=swap');

html, body, .stApp, .stMarkdown, p, li, label, input, button, textarea, td, th {{
    font-family: '{FONTE}', sans-serif !important;
    color: {TEXTO};
}}
h1, h2, h3, h4 {{ font-family: '{FONTE}', sans-serif !important; font-weight: 800 !important; color: {TEXTO} !important; }}
h3 {{ font-size: 1.15rem !important; }}

.stApp {{ background: {FUNDO}; }}
[data-testid="stHeader"] {{ background: transparent; }}
/* menos espaço vazio no topo da página e da barra lateral */
[data-testid="stMainBlockContainer"], .block-container {{ padding-top: 1.6rem !important; }}
[data-testid="stSidebarHeader"] {{ height: 2.2rem !important; min-height: 0 !important; padding: .4rem 1rem 0 !important; }}
[data-testid="stSidebarUserContent"] {{ padding-top: 0 !important; }}
[data-testid="stSidebarUserContent"] h2 {{ margin-top: 0 !important; padding-top: 0 !important; }}
[data-testid="stSidebar"] {{ background: #F1EEF0; border-right: 1px solid {BORDA}; }}

/* cabeçalho */
.capa {{
    display: flex; align-items: center; gap: 20px; background: {CARTAO};
    border: 1px solid {BORDA}; border-radius: 22px; padding: 14px 26px; margin-bottom: 16px;
}}
.capa img.gata {{ width: 96px; }}
.capa .titulo {{ font-weight: 800; font-size: 2rem; line-height: 1.1; color: {ROSA}; }}
.capa .sub {{ font-size: .95rem; color: {TEXTO_SUAVE}; margin-top: 2px; }}
.capa .kaomoji {{ font-size: 1rem; color: {ROSA}; font-weight: 700; margin-top: 4px; }}
.capa img.andando {{ height: 120px; margin-left: auto; image-rendering: pixelated; }}

/* cards dos indicadores */
.cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 8px; }}
.card {{
    background: {CARTAO}; border: 1px solid {BORDA}; border-top: 4px solid var(--cor);
    border-radius: 18px; padding: 12px 18px;
}}
.card .rotulo {{ font-size: .85rem; font-weight: 700; color: {TEXTO_SUAVE}; }}
.card .valor {{ font-size: 1.9rem; font-weight: 800; color: {TEXTO}; line-height: 1.2; }}
.card .nota {{ font-size: .78rem; color: {TEXTO_SUAVE}; }}
@media (max-width: 900px) {{ .cards {{ grid-template-columns: repeat(2, 1fr); }} }}

/* abas */
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {BORDA}; }}
.stTabs [data-baseweb="tab"] {{ padding: 6px 14px; font-weight: 700; color: {TEXTO_SUAVE}; }}
.stTabs [aria-selected="true"] {{ color: {ROSA} !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: {ROSA}; }}
.stTabs [data-baseweb="tab-border"] {{ display: none; }}

/* textos explicativos, gráficos e tabelas */
.balao {{
    background: {CARTAO}; border-left: 4px solid {ROSA_CLARO}; border-radius: 10px;
    padding: 10px 16px; margin: 6px 0 14px; color: {TEXTO};
}}
[data-testid="stVegaLiteChart"] {{ background: {CARTAO}; border: 1px solid {BORDA}; border-radius: 18px; padding: 8px; }}
[data-testid="stTable"] table {{ border-collapse: collapse; width: 100%; background: {CARTAO}; border-radius: 14px; overflow: hidden; }}
[data-testid="stTable"] th {{ background: #EADFE4; color: {TEXTO} !important; font-weight: 700; }}
[data-testid="stTable"] td, [data-testid="stTable"] th {{ padding: 6px 12px; border: none; border-bottom: 1px solid {BORDA}; }}

/* simulador */
[data-testid="stForm"] {{ background: {CARTAO}; border: 1px solid {BORDA}; border-radius: 20px; }}
.stButton > button, [data-testid="stFormSubmitButton"] > button {{
    background: {ROSA}; color: #FFFFFF !important; border: none; border-radius: 999px; font-weight: 700; padding: 6px 24px;
}}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {{ background: #C9688A; }}
.resultado {{
    display: flex; align-items: center; gap: 26px; background: {CARTAO}; border: 1px solid {BORDA};
    border-left: 6px solid var(--cor); border-radius: 20px; padding: 16px 26px; margin-top: 12px;
}}
.resultado img {{ width: 130px; }}
.resultado .pct {{ font-size: 3rem; font-weight: 800; color: {ROSA}; line-height: 1; }}
.resultado .frase {{ font-size: 1.05rem; font-weight: 700; margin-top: 6px; }}
.resultado .nota {{ font-size: .85rem; color: {TEXTO_SUAVE}; margin-top: 4px; }}

/* gatinho da barra lateral */
.humor {{ text-align: center; margin-top: 24px; }}
.humor img {{ width: 140px; transition: transform .3s; }}
.humor img:hover {{ transform: scale(1.06) rotate(-3deg); }}
.humor .pct {{ font-weight: 800; font-size: 1.4rem; color: {ROSA}; margin-top: 6px; }}
.humor .legenda {{ font-size: .8rem; color: {TEXTO_SUAVE}; }}

.rodape {{ text-align: center; font-size: .85rem; color: {TEXTO_SUAVE}; margin-top: 26px; }}
</style>
"""
