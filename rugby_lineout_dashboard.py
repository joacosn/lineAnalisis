import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
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
def load_data() -> pd.DataFrame:
    return pd.read_excel('Lines_IPR.xlsx')

df = load_data()
if df.empty:
    st.stop()

# 6. Filters
partidos = sorted(df['partido'].dropna().unique())
selected_match = st.selectbox('Selecciona un partido', partidos)
df_match = df[df['partido']==selected_match]
tipos = ['Todos'] + sorted(df_match['tipo_line'].dropna().unique())
selected_tipo = st.selectbox('Tipo de Line', tipos)
df_chart = df_match[df_match['tipo_line']==selected_tipo] if selected_tipo!='Todos' else df_match

# 7. KPIs
player_col = 'cant_line'
avg_players = df_chart[player_col].mean()

def safe_mode(s):
    s2=s.dropna(); return s2.mode().iloc[0] if not s2.empty else '—'

kpis=[
    ("Saltador más usado", safe_mode(df_chart['saltador'])),
    ("Posición más usada", safe_mode(df_chart['posicion'])),
    ("Total Lineouts", df_chart[player_col].count()),
    ("Promedio Jugadores", f"{avg_players:.1f}")
]
html_kpi="<div class='kpi-container'>"+"".join([f"<div class='kpi-card'><div class='kpi-title'>{t}</div><div class='kpi-value'>{v}</div></div>" for t,v in kpis])+"</div>"
st.markdown(html_kpi, unsafe_allow_html=True)

# 8. Bar charts
c1,_,c2=st.columns([1,0.02,1])
with c1:
    st.subheader('Lines por Posición')
    pc=df_chart['posicion'].value_counts().reset_index(name='cnt')
    bar=alt.Chart(pc).mark_bar().encode(x='posicion:N', y=alt.Y('cnt:Q',axis=alt.Axis(format='d')), tooltip=['posicion','cnt'])
    text=bar.mark_text(dy=-5,color='white').encode(text='cnt:Q')
    st.altair_chart((bar+text).properties(height=400),use_container_width=True)
with c2:
    st.subheader('Lines por Saltador')
    sc=df_chart['saltador'].value_counts().reset_index(name='cnt')
    bar2=alt.Chart(sc).mark_bar().encode(x='saltador:N', y=alt.Y('cnt:Q',axis=alt.Axis(format='d')), tooltip=['saltador','cnt'])
    text2=bar2.mark_text(dy=-5,color='white').encode(text='cnt:Q')
    st.altair_chart((bar2+text2).properties(height=400),use_container_width=True)

# 9. Jugadores por zona - corrected
st.subheader('Jugadores utilizados según zona de la cancha')
zone_counts = df_chart.groupby(['ubicacion',player_col]).size().reset_index(name='count')
if not zone_counts.empty:
    base=alt.Chart(zone_counts).mark_bar().encode(
        x='ubicacion:N',
        y=alt.Y('count:Q',stack='zero',axis=None),
        color=alt.Color(f'{player_col}:O'),
        tooltip=['ubicacion',player_col,'count']
    )
    labels=alt.Chart(zone_counts).transform_stack(
        stack='count',
        groupby=['ubicacion'],
        as_=['y0','y1']
    ).transform_calculate(
        mid='(datum.y0+datum.y1)/2'
    ).mark_text(color='white',size=12).encode(
        x='ubicacion:N',
        y='mid:Q',
        text='count:Q'
    )
    st.altair_chart((base+labels).properties(height=350),use_container_width=True)
else:
    st.info('Sin datos')

# 11. Zone selector + Pie
st.subheader('Selecciona la zona de la cancha')
btns, spacer, piec = st.columns([1, 0.5, 3])
with btns:
    for z in ['50-22', '22-5', '5']:
        if st.button(z):
            st.session_state.zone = z
with piec:
    st.subheader(f'Torres en {st.session_state.zone}m')
    zd = df_chart[df_chart['ubicacion'] == st.session_state.zone]
    if zd.empty:
        st.info('Sin datos para esta zona.')
    else:
        pdata = zd['posicion'].value_counts().reset_index()
        pdata.columns = ['pos', 'cnt']
        fig = px.pie(pdata, names='pos', values='cnt', hole=0.4)
        fig.update_traces(textinfo='percent+value', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

# 12. Detalle Lines (cascading filters)
st.subheader('Detalle Lines')
filtered_table = df_match.copy()
filter_cols = [('Tipo','tipo_line'),('Torre','posicion'),('Saltador','saltador'),('Zona','ubicacion')]
cols = st.columns(len(filter_cols))
for (lbl, col_name), col in zip(filter_cols, cols):
    opts = ['Todos'] + sorted(filtered_table[col_name].dropna().unique())
    sel = col.selectbox(lbl, opts, key=f"tbl_{col_name}")
    if sel != 'Todos':
        filtered_table = filtered_table[filtered_table[col_name] == sel]

display = filtered_table.rename(columns={
    'posicion':'Torre',
    'saltador':'Saltador',
    'ubicacion':'Zona',
    'cant_line':'Cant Lines',
    'desc':'Descripción',
    'tipo_line':'Tipo'
})
st.dataframe(display[['Torre','Saltador','Zona','Cant Lines','Descripción','Tipo']].reset_index(drop=True))
