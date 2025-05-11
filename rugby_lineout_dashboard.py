import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from pathlib import Path
import base64

# 1. Page configuration
st.set_page_config(page_title="Análisis Lines 2025", layout="wide")

# 2. Inject custom styles and fonts
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.kpi-card {
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    flex: 1 1 300px;
    min-width: 240px;
}
.kpi-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
.kpi-value { font-size: 36px; font-weight: 700; }
.table-container { overflow-x: auto; }
.custom-table { border-collapse: collapse; width: 100%; font-size: 14px; }
.custom-table th, .custom-table td { padding: 8px; border-bottom: 1px solid #ddd; white-space: nowrap; }
.custom-table th { background-color: #f2f2f2; text-align: left; }
@media (prefers-color-scheme: dark) {
    .custom-table th { background-color: #333; color: #fff; }
    .custom-table td { background-color: #111; color: #eee; border-color: #444; }
}
"""
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# 3. Dark-mode inversion (optional)
st.markdown(
    "<style>@media (prefers-color-scheme: dark) {html {filter: invert(1) hue-rotate(180deg);} img, video, iframe {filter: invert(1) hue-rotate(180deg)!important;}}</style>",
    unsafe_allow_html=True
)

# 4. Utility to encode image as base64
@st.cache_data
def encode_image(path: str) -> str:
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode()

# 5. Header with logo
try:
    logo_b64 = encode_image('ipr_logo.png')
    st.markdown(
        f"<div style='display:flex;justify-content:space-between;align-items:center;'><h1>Analisis Lines 2025</h1><img src='data:image/png;base64,{logo_b64}' height='55'></div>",
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.title("Analisis Lines 2025")

# 6. Load data
def load_data(filepath: str = 'Lines_IPR.xlsx') -> pd.DataFrame:
    try:
        return pd.read_excel(filepath)
    except Exception as e:
        st.error(f"Error al leer archivo: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# 7. Filters for partido and tipo_line
partidos = sorted(df['partido'].dropna().unique())
selected_match = st.selectbox('Selecciona un partido', partidos)
subset = df[df['partido'] == selected_match]

if 'tipo_line' in subset.columns:
    tipos = ['Todos'] + sorted(subset['tipo_line'].dropna().unique())
    tipo_sel = st.selectbox('Tipo de Line', tipos)
    if tipo_sel != 'Todos':
        subset = subset[subset['tipo_line'] == tipo_sel]

# 8. Session state for zone selection
if 'zone' not in st.session_state:
    st.session_state.zone = '50-22'

# 9. KPIs
def safe_mode(series: pd.Series):
    vals = series.dropna()
    return vals.mode().iloc[0] if not vals.empty else '—'

kpi1 = safe_mode(subset['saltador'])

kpi2 = safe_mode(subset['posicion'])

kpi3 = int(subset['cant_line'].count())

st.markdown("<div style='display:flex;gap:20px;margin-bottom:30px;'>"
            f"<div class='kpi-card'><div class='kpi-title'>Saltador más usado</div><div class='kpi-value'>{kpi1}</div></div>"
            f"<div class='kpi-card'><div class='kpi-title'>Posición más usada</div><div class='kpi-value'>{kpi2}</div></div>"
            f"<div class='kpi-card'><div class='kpi-title'>Total Lineouts</div><div class='kpi-value'>{kpi3}</div></div>"
            "</div>", unsafe_allow_html=True)

# 10. Charts
tab1, _, tab2 = st.columns([1, 0.02, 1])
with tab1:
    st.subheader('Lines por Posición')
    pos_count = subset['posicion'].value_counts().reset_index()
    pos_count.columns = ['posicion', 'count']
    chart = alt.Chart(pos_count).mark_bar().encode(x='posicion:N', y='count:Q', tooltip=['posicion','count'])
    st.altair_chart(chart, use_container_width=True)

with tab2:
    st.subheader('Lines por Saltador')
    salt_count = subset['saltador'].value_counts().reset_index()
    salt_count.columns = ['saltador','count']
    chart2 = alt.Chart(salt_count).mark_bar().encode(x='saltador:N', y='count:Q', tooltip=['saltador','count'])
    st.altair_chart(chart2, use_container_width=True)

# 11. Zone pie chart
st.subheader('Elección de torre por zona')
cols = st.columns([1,3])
with cols[0]:
    for z in ['50-22','22-5','5']:
        if st.button(z): st.session_state.zone = z
with cols[1]:
    data_zone = subset[subset['ubicacion'] == st.session_state.zone]
    if not data_zone.empty:
        pie = alt.Chart(data_zone['posicion'].value_counts().reset_index()).mark_arc(innerRadius=50).encode(
            theta='count:Q', color='posicion:N', tooltip=['posicion','count']
        )
        st.altair_chart(pie, use_container_width=True)
    else:
        st.info('Sin datos para esta zona.')

# 12. Tabla de detalle
st.subheader('Detalle Lines')
filters = {'Tipo': 'tipo_line', 'Torre':'posicion', 'Saltador':'saltador','Zona':'ubicacion'}
filtered = subset.copy()
cols = st.columns(len(filters))
for (label, col), col_obj in zip(filters.items(), cols):
    opts = ['Todos'] + sorted(subset[col].dropna().unique())
    sel = col_obj.selectbox(label, opts, key=col)
    if sel != 'Todos': filtered = filtered[filtered[col]==sel]

display = filtered.rename(columns={'posicion':'Torre','saltador':'Saltador','ubicacion':'Zona','cant_line':'Cant Lines','desc':'Descripción','tipo_line':'Tipo'})
cols_order = ['Torre','Saltador','Zona','cant_line','Descripción','Tipo']
st.dataframe(display[cols_order])
