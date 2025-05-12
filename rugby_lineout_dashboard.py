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

# 6. Primary filters
partidos = sorted(df['partido'].dropna().unique())
selected_match = st.selectbox('Selecciona un partido', partidos)
df_match = df[df['partido'] == selected_match]

tipos = ['Todos'] + sorted(df_match['tipo_line'].dropna().unique()) if 'tipo_line' in df_match.columns else ['Todos']
selected_tipo = st.selectbox('Tipo de Line', tipos)

df_chart = df_match[df_match['tipo_line'] == selected_tipo] if selected_tipo != 'Todos' else df_match.copy()

# 7. Zone session
if 'zone' not in st.session_state:
    st.session_state.zone = '50-22'

# 8. KPIs
player_col = 'cant_line'
avg_players = df_chart[player_col].mean()

def safe_mode(s):
    s2 = s.dropna(); return s2.mode().iloc[0] if not s2.empty else '—'

kpis = [
    ("Saltador más usado", safe_mode(df_chart['saltador'])),
    ("Posición más usada", safe_mode(df_chart['posicion'])),
    ("Total Lineouts", int(df_chart[player_col].count())),
    ("Promedio Jugadores", f"{avg_players:.1f}")
]
html_kpi = "<div class='kpi-container'>" + "".join([
    f"<div class='kpi-card'><div class='kpi-title'>{t}</div><div class='kpi-value'>{v}</div></div>" for t,v in kpis]) + "</div>"
st.markdown(html_kpi, unsafe_allow_html=True)

# 9. Bar Charts
c1, _, c2 = st.columns([1,0.02,1])
with c1:
    st.subheader('Lines por Posición')
    pc = df_chart['posicion'].value_counts().reset_index(); pc.columns=['pos','cnt']
    bar = alt.Chart(pc).mark_bar(color='#4C78A8').encode(
        x=alt.X('pos:N', title='Torre'),
        y=alt.Y('cnt:Q', title='Cantidad', axis=alt.Axis(format='d'))
    )
    txt = bar.mark_text(dy=-5,color='white').encode(text='cnt:Q')
    st.altair_chart((bar+txt).properties(height=400), use_container_width=True)
with c2:
    st.subheader('Lines por Saltador')
    sc = df_chart['saltador'].value_counts().reset_index(); sc.columns=['salt','cnt']
    bar2 = alt.Chart(sc).mark_bar(color='#F58518').encode(
        x=alt.X('salt:N', title='Saltador'),
        y=alt.Y('cnt:Q', title='Cantidad', axis=alt.Axis(format='d'))
    )
    txt2 = bar2.mark_text(dy=-5,color='white').encode(text='cnt:Q')
    st.altair_chart((bar2+txt2).properties(height=400), use_container_width=True)

# 10. Jugadores por zona de cancha (stacked bar Absolute count labels)
st.subheader('Jugadores utilizados según zona de la cancha')
zone_counts = df_chart.groupby(['ubicacion', player_col]).size().reset_index(name='count')
if not zone_counts.empty:
    # Absolute stacked bar with labels per segment
    base = alt.Chart(zone_counts).mark_bar().encode(
        x=alt.X('ubicacion:N', title='Zona'),
        y=alt.Y('count:Q', title=None, axis=None),
        color=alt.Color(f'{player_col}:N', title='Jugadores'),
        tooltip=['ubicacion', player_col, 'count']
    )
    # Text labels centered in each segment
    text = alt.Chart(zone_counts).mark_text(color='black', size=12).encode(
        x=alt.X('ubicacion:N'),
        y=alt.Y('count:Q', stack='center'),
        text=alt.Text('count:Q', format='d')
    )
    st.altair_chart((base + text).properties(height=350), use_container_width=True)
else:
    st.info('Sin datos para graficar jugadores por zona.')
# 11. Zone selector + Pie. Zone selector + Pie (df_chart)
st.subheader('Selecciona la zona de la cancha')
btns, spacer, piec = st.columns([1,0.5,3])
with btns:
    for z in ['50-22','22-5','5']:
        if st.button(z):
            st.session_state.zone = z
with piec:
    st.subheader(f'Torres en {st.session_state.zone}m')
    zd = df_chart[df_chart['ubicacion'] == st.session_state.zone]
    if zd.empty:
        st.info('Sin datos para esta zona.')
    else:
        pdata = zd['posicion'].value_counts().reset_index(); pdata.columns=['pos','cnt']
        fig = px.pie(pdata, names='pos', values='cnt', hole=0.4)
        fig.update_traces(textinfo='percent+value', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

# 12. Detalle Lines (cascading filters)
st.subheader('Detalle Lines')
filtered_table = df_match.copy()
filter_cols = [('Tipo','tipo_line'),('Torre','posicion'),('Saltador','saltador'),('Zona','ubicacion')]
cols = st.columns(len(filter_cols))
for (lbl,col_name),col in zip(filter_cols,cols):
    opts = ['Todos'] + sorted(filtered_table[col_name].dropna().unique())
    sel = col.selectbox(lbl, opts, key=f"tbl_{col_name}")
    if sel!='Todos':
        filtered_table = filtered_table[filtered_table[col_name]==sel]

display = filtered_table.rename(columns={
    'posicion':'Torre','saltador':'Saltador','ubicacion':'Zona','cant_line':'Cant Lines','desc':'Descripción','tipo_line':'Tipo'
})
st.dataframe(display[['Torre','Saltador','Zona','Cant Lines','Descripción','Tipo']].reset_index(drop=True))
