import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import plotly.express as px
from pathlib import Path
import base64

# 1. Page configuration
st.set_page_config(page_title="Análisis Lines 2025", layout="wide")

# 2. Styles and fonts
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.kpi-container { display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
.kpi-container .kpi-card { flex: 1 1 0; min-width: 0; }
@media (max-width: 600px) { .kpi-container { flex-direction: column; } }
.kpi-card { padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.kpi-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
.kpi-value { font-size: 36px; font-weight: 700; }
.stButton>button { min-width: 100px !important; }
"""
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# 3. Dark-mode inversion (optional)
st.markdown(
    "<style>@media (prefers-color-scheme: dark) {html {filter: invert(1) hue-rotate(180deg);} img, video, iframe {filter: invert(1) hue-rotate(180deg)!important;}}</style>",
    unsafe_allow_html=True
)

# 4. Load logo
@st.cache_data
def encode_image(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()

try:
    logo = encode_image('ipr_logo.png')
    st.markdown(
        f"<div style='display:flex;justify-content:space-between;align-items:center;'><h1>Analisis Lines 2025</h1><img src='data:image/png;base64,{logo}' height='55'></div>",
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.title("Analisis Lines 2025")

# 5. Load data
def load_data():
    try:
        return pd.read_excel('Lines_IPR.xlsx')
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty: st.stop()

# 6. Filters
partidos = sorted(df['partido'].dropna().unique())
sel_partido = st.selectbox('Selecciona un partido', partidos)
df = df[df['partido']==sel_partido]
if 'tipo_line' in df:
    tipos = ['Todos'] + sorted(df['tipo_line'].dropna().unique())
    sel_tipo = st.selectbox('Tipo de Line', tipos)
    if sel_tipo!='Todos': df = df[df['tipo_line']==sel_tipo]

# 7. Session for zone
defaul = '50-22'
if 'zone' not in st.session_state: st.session_state.zone = defaul

# 8. KPIs
def safe_mode(s):
    s2 = s.dropna()
    return s2.mode().iloc[0] if not s2.empty else '—'

k1, k2, k3 = safe_mode(df['saltador']), safe_mode(df['posicion']), df['cant_line'].count()
st.markdown(
    "<div class='kpi-container'>"
    f"<div class='kpi-card'><div class='kpi-title'>Saltador más usado</div><div class='kpi-value'>{k1}</div></div>"
    f"<div class='kpi-card'><div class='kpi-title'>Posición más usada</div><div class='kpi-value'>{k2}</div></div>"
    f"<div class='kpi-card'><div class='kpi-title'>Total Lineouts</div><div class='kpi-value'>{k3}</div></div>"
    "</div>", unsafe_allow_html=True
)

# 9. Bar Charts
c1, _, c2 = st.columns([1,0.02,1])
with c1:
    st.subheader('Lines por Posición')
    pc = df['posicion'].value_counts().reset_index(); pc.columns=['pos','cnt']
    chart = alt.Chart(pc).mark_bar(color='#4C78A8').encode(
        x=alt.X('pos:N', title='Torre', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('cnt:Q', title='Cantidad', axis=alt.Axis(format='d'))
    )
    text=chart.mark_text(dy=-5,color='white').encode(text='cnt:Q')
    st.altair_chart((chart+text).properties(height=400),use_container_width=True)
with c2:
    st.subheader('Lines por Saltador')
    sc = df['saltador'].value_counts().reset_index(); sc.columns=['salt','cnt']
    chart2 = alt.Chart(sc).mark_bar(color='#F58518').encode(
        x=alt.X('salt:N',title='Saltador',axis=alt.Axis(labelAngle=0)),
        y=alt.Y('cnt:Q',title='Cantidad',axis=alt.Axis(format='d'))
    )
    text2=chart2.mark_text(dy=-5,color='white').encode(text='cnt:Q')
    st.altair_chart((chart2+text2).properties(height=400),use_container_width=True)

# 10. Zone selector + Pie
# Use responsive flex container for buttons
st.subheader('Selecciona la zona de la cancha')
container = st.container()
with container:
    btns_html = ['50-22','22-5','5']
    # Render buttons with custom container
    st.markdown(
        "<div class='zone-buttons'>" +
        "".join([
            f"<button class='zone-btn' onclick='window.dispatchEvent(new CustomEvent(\"streamlit:setComponentValue\", {{}}, {{detail:{{key: \"zone\", value: \"{z}\"}}}}))'>{z}</button>" for z in btns_html
        ]) +
        "</div>", unsafe_allow_html=True
    )
    st.session_state.zone = st.session_state.get('zone', '50-22')
    # Pie chart next to buttons
    pie_col = st.columns([3,1])[0]
    with pie_col:
        st.subheader(f'Torres en {st.session_state.zone}m')
        zd = df[df['ubicacion'] == st.session_state.zone]
        if zd.empty:
            st.info('Sin datos para esta zona.')
        else:
            pdata = zd['posicion'].value_counts().reset_index(); pdata.columns = ['pos','cnt']
            fig = px.pie(pdata, names='pos', values='cnt', hole=0.4)
            fig.update_traces(textinfo='percent+value', textposition='inside')
            st.plotly_chart(fig, use_container_width=True)
# 11. Tabla. Tabla
st.subheader('Detalle Lines')
filters={'Tipo':'tipo_line','Torre':'posicion','Saltador':'saltador','Zona':'ubicacion'}
tab=df.copy()
cols=st.columns(len(filters))
for (lbl,cn),col in zip(filters.items(),cols):
    opts=['Todos']+sorted(df[cn].dropna().unique())
    sel=col.selectbox(lbl,opts)
    if sel!='Todos': tab=tab[tab[cn]==sel]

tab=tab.rename(columns={'posicion':'Torre','saltador':'Saltador','ubicacion':'Zona','cant_line':'Cant Lines','desc':'Descripción','tipo_line':'Tipo'})
st.dataframe(tab[['Torre','Saltador','Zona','Cant Lines','Descripción','Tipo']].reset_index(drop=True))
