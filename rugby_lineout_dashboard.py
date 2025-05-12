import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import plotly.express as px
from pathlib import Path
import base64

# 1. Page configuration
st.set_page_config(page_title="Análisis Lines 2025", layout="wide")

# 2. Inject custom styles and fonts + button styling
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
.custom-table { border-collapse: collapse; width: 100%; font-size: 14px; }
.custom-table th, .custom-table td { padding: 8px; border-bottom: 1px solid #ddd; white-space: nowrap; }
.custom-table th { background-color: #f2f2f2; text-align: left; }
@media (prefers-color-scheme: dark) {
    .custom-table th { background-color: #333; color: #fff; }
    .custom-table td { background-color: #111; color: #eee; border-color: #444; }
}
/* Uniform width for all buttons */
.stButton button {
    min-width: 100px !important;
}
"""
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# 3. Dark-mode inversion (optional) Dark-mode inversion (optional)
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
# KPI container: responsive stack on mobile
st.markdown(
    "<div class='kpi-container'>"
    f"<div class='kpi-card'><div class='kpi-title'>Saltador más usado</div><div class='kpi-value'>{kpi1}</div></div>"
    f"<div class='kpi-card'><div class='kpi-title'>Posición más usada</div><div class='kpi-value'>{kpi2}</div></div>"
    f"<div class='kpi-card'><div class='kpi-title'>Total Lineouts</div><div class='kpi-value'>{kpi3}</div></div>"
    "</div>", unsafe_allow_html=True
)

# 10. Charts Charts
col1, _, col2 = st.columns([1, 0.02, 1])
with col1:
    st.subheader('Lines por Posición')
    pos_count = subset['posicion'].value_counts().reset_index()
    pos_count.columns = ['posicion', 'count']
    base = alt.Chart(pos_count).mark_bar(color='#4C78A8').encode(
        x=alt.X('posicion:N', title='Torre', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('count:Q', title='Cantidad de Lines', axis=alt.Axis(format='d')),
        tooltip=['posicion','count']
    )
    text = alt.Chart(pos_count).mark_text(dy=-5, color='white').encode(
        x='posicion:N', y='count:Q', text=alt.Text('count:Q')
    )
    st.altair_chart((base + text).properties(height=400), use_container_width=True)

with col2:
    st.subheader('Lines por Saltador')
    salt_count = subset['saltador'].value_counts().reset_index()
    salt_count.columns = ['saltador','count']
    base2 = alt.Chart(salt_count).mark_bar(color='#F58518').encode(
        x=alt.X('saltador:N', title='Saltador', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('count:Q', title='Cantidad de Lines', axis=alt.Axis(format='d')),
        tooltip=['saltador','count']
    )
    text2 = alt.Chart(salt_count).mark_text(dy=-5, color='white').encode(
        x='saltador:N', y='count:Q', text=alt.Text('count:Q')
    )
    st.altair_chart((base2 + text2).properties(height=400), use_container_width=True)

# 11. Zone selector buttons and pie chart side by side
container = st.container()
with container:
    btn_col, pie_col = st.columns([1,3])
    with btn_col:
        st.markdown("<div style='display:flex;flex-direction:column;gap:10px;'>", unsafe_allow_html=True)
        for z in ['50-22','22-5','5']:
            clicked = st.button(z, key=z, help="Seleccionar zona", on_click=lambda z=z: st.session_state.update({'zone': z}))
        st.markdown("</div>", unsafe_allow_html=True)
    with pie_col:
        # Align title and pie centrally
        st.markdown(f"<div style='display:flex;flex-direction:column;align-items:center;'>",
                    unsafe_allow_html=True)
        st.markdown(f"<h3>Torres en {st.session_state.zone}m</h3>", unsafe_allow_html=True)
        zone_df = subset[subset['ubicacion'] == st.session_state.zone]
        if zone_df.empty:
            st.info('Sin datos para esta zona.')
        else:
            pie_data = zone_df['posicion'].value_counts().reset_index()
            pie_data.columns = ['posicion','count']
            fig = px.pie(pie_data, names='posicion', values='count', hole=0.4)
            fig.update_traces(textinfo='percent+value', textposition='inside', textfont_size=14)
            fig.update_layout(showlegend=True, legend_title_text='Torre')
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
# 12. Tabla de detalle Tabla de detalle
st.subheader('Detalle Lines')
filters = {'Tipo':'tipo_line','Torre':'posicion','Saltador':'saltador','Zona':'ubicacion'}
filtered = subset.copy()
cols = st.columns(len(filters))
for (label, col), col_obj in zip(filters.items(), cols):
    opts = ['Todos'] + sorted(subset[col].dropna().unique())
    sel = col_obj.selectbox(label, opts, key=col)
    if sel != 'Todos': filtered = filtered[filtered[col]==sel]

# Rename and order columns
display = filtered.rename(columns={
    'posicion':'Torre','saltador':'Saltador','ubicacion':'Zona',
    'cant_line':'Cant Lines','desc':'Descripción','tipo_line':'Tipo'
})
cols_order = ['Torre','Saltador','Zona','Cant Lines','Descripción','Tipo']
st.dataframe(display[cols_order].reset_index(drop=True))
