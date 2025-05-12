import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import numpy as np
import base64
from pathlib import Path

# 1. Page configuration
st.set_page_config(page_title="Análisis Lines 2025", layout="wide")

# 2. Styles and fonts
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.kpi-container { display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
.kpi-container .kpi-card { flex: 1 1 0; }
@media (max-width: 600px) { .kpi-container { flex-direction: column; } }
.kpi-card { padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.kpi-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
.kpi-value { font-size: 36px; font-weight: 700; }
.stButton>button { min-width: 100px !important; }
/* Dropdown list border */
div[role="listbox"] { border: 1px solid #ccc !important; border-radius: 4px !important; }
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
    logo_b64 = encode_image('ipr_logo.png')
    st.markdown(
        f"<div style='display:flex;justify-content:space-between;align-items:center;'><h1>Analisis Lines 2025</h1><img src='data:image/png;base64,{logo_b64}' height='55'></div>",
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.title("Análisis Lines 2025")

# 5. Load data
@st.cache_data
def load_data() -> pd.DataFrame:
    try:
        return pd.read_excel('Lines_IPR.xlsx')
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# 6. Primary filters: partido (affects entire app) and tipo_line (affects only charts)
# Filter by partido
partidos = sorted(df['partido'].dropna().unique())
selected_match = st.selectbox('Selecciona un partido', partidos)
# df_match used for table and charts initial dataset
df_match = df[df['partido'] == selected_match]

# Filter by tipo_line for charts only
if 'tipo_line' in df_match.columns:
    tipos = ['Todos'] + sorted(df_match['tipo_line'].dropna().unique())
    selected_tipo = st.selectbox('Tipo de Line', tipos)
    # df_chart used for KPI and charts
    df_chart = df_match[df_match['tipo_line'] == selected_tipo] if selected_tipo != 'Todos' else df_match.copy()
else:
    df_chart = df_match.copy()

# 7. Session for zone
default_zone = '50-22'
if 'zone' not in st.session_state:
    st.session_state.zone = default_zone

# 8. KPIs (using df_chart)
# Assuming `cant_line` holds the number of players per line for this analysis
player_col = 'cant_line'
avg_players = df_chart[player_col].mean()

# helper to get mode or dash
def safe_mode(series: pd.Series):
    s2 = series.dropna()
    return s2.mode().iloc[0] if not s2.empty else '—'

k1 = safe_mode(df_chart['saltador'])
k2 = safe_mode(df_chart['posicion'])
k3 = int(df_chart['cant_line'].count())
generated_kpis = [
    ("Saltador más usado", k1),
    ("Posición más usada", k2),
    ("Total Lineouts", k3),
    ("Promedio Jugadores", f"{avg_players:.1f}")
]

# Render KPI cards
kpi_cards = "<div class='kpi-container'>"
for title, value in generated_kpis:
    kpi_cards += f"<div class='kpi-card'><div class='kpi-title'>{title}</div><div class='kpi-value'>{value}</div></div>"
kpi_cards += "</div>"
st.markdown(kpi_cards, unsafe_allow_html=True)
# Players-per-line distribution (histogram)
st.subheader(f"Distribución de {player_col}")
# Use a histogram for continuous distribution
hist = alt.Chart(df_chart).mark_bar().encode(
    x=alt.X(f"{player_col}:Q", bin=alt.Bin(maxbins=20), title="Número de Jugadores"),
    y=alt.Y('count()', title='Frecuencia'),
    tooltip=[alt.Tooltip(f"{player_col}:Q", title="Jugadores"), alt.Tooltip('count()', title='Frecuencia')]
).properties(height=300)
# Add mean line
mean_val = df_chart[player_col].mean()
rule = alt.Chart(pd.DataFrame({'mean':[mean_val]})).mark_rule(color='red').encode(x='mean:Q')
st.altair_chart(hist + rule, use_container_width=True)
# 10. Bar Charts (using df_chart) Bar Charts (using df_chart)
c1, _, c2 = st.columns([1,0.02,1])
with c1:
    st.subheader('Lines por Posición')
    pc = df_chart['posicion'].value_counts().reset_index(); pc.columns=['pos','cnt']
    chart = alt.Chart(pc).mark_bar(color='#4C78A8').encode(
        x=alt.X('pos:N', title='Torre', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('cnt:Q', title='Cantidad', axis=alt.Axis(format='d'))
    )
    text = chart.mark_text(dy=-5, color='white').encode(text='cnt:Q')
    st.altair_chart((chart+text).properties(height=400), use_container_width=True)
with c2:
    st.subheader('Lines por Saltador')
    sc = df_chart['saltador'].value_counts().reset_index(); sc.columns=['salt','cnt']
    chart2 = alt.Chart(sc).mark_bar(color='#F58518').encode(
        x=alt.X('salt:N', title='Saltador', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('cnt:Q', title='Cantidad', axis=alt.Axis(format='d'))
    )
    text2 = chart2.mark_text(dy=-5, color='white').encode(text='cnt:Q')
    st.altair_chart((chart2+text2).properties(height=400), use_container_width=True)

# 10. Jugadores por zona de cancha
st.subheader('Jugadores utilizados según zona de la cancha')
zone_counts = df_chart.groupby(['ubicacion', player_col]).size().reset_index(name='count')
if not zone_counts.empty:
    area_bar = alt.Chart(zone_counts).mark_bar().encode(
        x=alt.X('ubicacion:N', title='Zona'),
        y=alt.Y('count:Q', title='Frecuencia', axis=alt.Axis(format='d')),
        color=alt.Color(f'{player_col}:N', title='Jugadores'),
        tooltip=['ubicacion', player_col, 'count']
    ).properties(height=350)
    st.altair_chart(area_bar, use_container_width=True)
else:
    st.info('Sin datos para graficar jugadores por zona.')

# 11. Sankey Chart: flow from Torre to Saltador
# Build sankey data
towers = df_chart['posicion'].astype(str)
saltadores = df_chart['saltador'].astype(str)
# Create list of unique labels
labels = list(pd.concat([towers, saltadores]).unique())
# Map labels to indices
label_indices = {label: i for i, label in enumerate(labels)}
# Aggregate counts for each tower-saltador pair
pair_counts = df_chart.groupby(['posicion','saltador']).size().reset_index(name='count')
# Prepare sankey inputs
source = pair_counts['posicion'].astype(str).map(label_indices)
target = pair_counts['saltador'].astype(str).map(label_indices)
value  = pair_counts['count']

import plotly.graph_objects as go
fig_sankey = go.Figure(data=[
    go.Sankey(
        node = dict(
            label = labels,
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5)
        ),
        link = dict(
            source = source,
            target = target,
            value  = value
        )
    )
])
st.subheader('Flujo Torre → Saltador')
st.plotly_chart(fig_sankey, use_container_width=True)

# 11. Zone selector + Pie (using df_chart)
st.subheader('Selecciona la zona de la cancha')
btns, spacer, piec = st.columns([1,0.5,3])
with btns:
    for z in ['50-22','22-5','5']:
        if st.button(z):
            st.session_state.zone = z
with piec:
    st.subheader(f'Torres en {st.session_state.zone}m')
    # Use df_chart so donut also respects tipo_line filter
    zd = df_chart[df_chart['ubicacion'] == st.session_state.zone]
    if zd.empty:
        st.info('Sin datos para esta zona.')
    else:
        pdata = zd['posicion'].value_counts().reset_index()
        pdata.columns = ['pos','cnt']
        fig = px.pie(pdata, names='pos', values='cnt', hole=0.4)
        fig.update_traces(textinfo='percent+value', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)
# 11. Detalle Lines con filtros en cascada (using df_match)
st.subheader('Detalle Lines')
filtered_table = df_match.copy()
# Cascading filters for table
table_filters = [
    ('Tipo','tipo_line'),
    ('Torre','posicion'),
    ('Saltador','saltador'),
    ('Zona','ubicacion')
]
cols = st.columns(len(table_filters))
for (label, col_name), col in zip(table_filters, cols):
    opts = ['Todos'] + sorted(filtered_table[col_name].dropna().unique())
    sel = col.selectbox(label, opts, key=f"tbl_{col_name}")
    if sel != 'Todos':
        filtered_table = filtered_table[filtered_table[col_name] == sel]
# Rename and display
display_df = filtered_table.rename(columns={
    'posicion':'Torre','saltador':'Saltador','ubicacion':'Zona',
    'cant_line':'Cant Lines','desc':'Descripción','tipo_line':'Tipo'
})
st.dataframe(display_df[['Torre','Saltador','Zona','Cant Lines','Descripción','Tipo']].reset_index(drop=True))
