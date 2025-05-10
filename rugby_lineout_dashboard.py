import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import numpy as np
from pathlib import Path
import base64

# ✅ Set wide layout
st.set_page_config(layout="wide")

# ✅ Optional Dark Mode Inversion (keep or remove if undesired)
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) {
        html {
            filter: invert(1) hue-rotate(180deg);
        }
        img, video, iframe {
            filter: invert(1) hue-rotate(180deg) !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ✅ Load and encode logo
def image_to_base64(img_path):
    return base64.b64encode(Path(img_path).read_bytes()).decode()

logo_base64 = image_to_base64("ipr_logo.png")

# ✅ Title with logo
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <h1 style="margin: 0;">Analisis Lines 2025</h1>
    <img src="data:image/png;base64,{logo_base64}" style="height: 55px;">
</div>
""", unsafe_allow_html=True)

# ✅ Custom font and card styles
st.markdown("""
    <style>
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
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-title {
        font-size: 16px;
        margin-bottom: 10px;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 38px;
        font-weight: 700;
    }
    @media (prefers-color-scheme: dark) {
        .kpi-card {
            background-color: #444;
            color: #f1f1f1;
        }
    }
    @media (prefers-color-scheme: light) {
        .kpi-card {
            background-color: #f8f9fa;
            color: #212529;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ✅ Load data
@st.cache_data
def load_data():
    return pd.read_excel("Lines_IPR.xlsx")

df = load_data()
match_options = sorted(df['partido'].dropna().unique())
selected_match = st.selectbox("Selecciona un partido", match_options, index=0)

if "selected_zone" not in st.session_state:
    st.session_state.selected_zone = "50-22"

match_filtered_df = df[df['partido'] == selected_match]

# ✅ Tipo de Line filter
if 'tipo_line' in match_filtered_df.columns:
    tipo_values = sorted(match_filtered_df['tipo_line'].dropna().unique())
    tipo_options = ['Todos'] + [tipo.capitalize() for tipo in tipo_values]
    selected_tipo = st.selectbox("Selecciona el tipo de line", tipo_options)
    filtered_df = match_filtered_df[match_filtered_df['tipo_line'] == selected_tipo.lower()] if selected_tipo != 'Todos' else match_filtered_df
else:
    st.warning("⚠️ Column 'tipo_line' not found.")
    filtered_df = match_filtered_df

# ✅ Disable dropdown typing
st.markdown("""
<script>
const boxes = window.parent.document.querySelectorAll('input[type="text"]');
boxes.forEach(box => box.setAttribute('readonly', true));
</script>
<style>
input[type="text"] { caret-color: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ✅ KPI section - responsive
most_used_player = filtered_df['saltador'].mode()[0]
most_used_position = filtered_df['posicion'].mode()[0]
total_lineouts = filtered_df['cant_line'].count()

st.markdown("""
<style>
.kpi-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: space-between;
    margin-bottom: 30px;
}
.kpi-card-wrapper {
    flex: 1 1 300px;
    min-width: 240px;
}
</style>
<div class="kpi-container">
    <div class="kpi-card-wrapper">
        <div class="kpi-card">
            <div class="kpi-title">Saltador más utilizado</div>
            <div class="kpi-value">""" + str(most_used_player) + """</div>
        </div>
    </div>
    <div class="kpi-card-wrapper">
        <div class="kpi-card">
            <div class="kpi-title">Posición más utilizada</div>
            <div class="kpi-value">""" + str(most_used_position) + """</div>
        </div>
    </div>
    <div class="kpi-card-wrapper">
        <div class="kpi-card">
            <div class="kpi-title">Cant. Lines</div>
            <div class="kpi-value">""" + str(total_lineouts) + """</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ✅ Chart Section
chart_col1, divider_col, chart_col2 = st.columns([1, 0.005, 1])

with chart_col1:
    st.markdown("#### 📌 Cant. de lines por torre")
    pos_df = filtered_df[['posicion']].dropna().astype(str).apply(lambda x: x.str.strip())
    pos_count = pos_df.value_counts().reset_index(name='count').rename(columns={'posicion': 'posicion'})
    base = alt.Chart(pos_count).mark_bar(size=50).encode(
        x=alt.X('posicion:N', title='Torre', axis=alt.Axis(labelAngle=0, labelColor='#333')),
        y=alt.Y('count:Q', title='Cant. Lines'),
        tooltip=['posicion', 'count']
    )
    text = alt.Chart(pos_count).mark_text(
        align='center', baseline='bottom', dy=-5
    ).encode(x='posicion:N', y='count:Q', text='count:Q')
    st.altair_chart((base + text).properties(height=400), use_container_width=True)

with chart_col2:
    st.markdown("#### 🧍 Cant. lines por saltador")
    saltador_df = filtered_df[['saltador']].dropna().astype(str).apply(lambda x: x.str.strip())
    saltador_count = saltador_df.value_counts().reset_index(name='count').rename(columns={'saltador': 'saltador'})
    base = alt.Chart(saltador_count).mark_bar(size=50).encode(
        x=alt.X('saltador:N', title='Nro. Saltador', axis=alt.Axis(labelAngle=0, labelColor='#333')),
        y=alt.Y('count:Q', title='Cant. Lines'),
        tooltip=['saltador', 'count']
    )
    text = alt.Chart(saltador_count).mark_text(
        align='center', baseline='bottom', dy=-5
    ).encode(x='saltador:N', y='count:Q', text='count:Q')
    st.altair_chart((base + text).properties(height=400), use_container_width=True)

# ✅ Pie Chart by zone
st.subheader("📍 Eleccion de torre por posicion de cancha")
left_col, _, right_col = st.columns([1, 0.01, 3])

with left_col:
    st.markdown("### Lugar de la cancha")
    zones = ["50-22", "22-5", "5"]
    for zone in zones:
        if st.button(zone, key=f"zone_{zone}"):
            st.session_state.selected_zone = zone

with right_col:
    selected_zone = st.session_state.selected_zone
    st.markdown(f"### Torres más utilizadas en {selected_zone} metros")
    zone_df = filtered_df[filtered_df['ubicacion'] == selected_zone]
    if zone_df.empty:
        st.info("⚠️ No data available for this zone.")
    else:
        pie_data = zone_df['posicion'].value_counts().reset_index()
        pie_data.columns = ['posicion', 'count']
        fig = px.pie(pie_data, names='posicion', values='count', hole=0.3)
        fig.update_traces(textinfo='percent', textfont_size=18, textfont_color='#333')
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=16)))
        st.plotly_chart(fig, use_container_width=True)

# ✅ Data Table Filters
st.subheader("Detalle de lines")
tabla_df = match_filtered_df.copy()

filtros_config = {
    "Tipo de Line": ("tipo_line", "filtro_tabla_tipo"),
    "Torre": ("posicion", "filtro_tabla_torre"),
    "Saltador": ("saltador", "filtro_tabla_saltador"),
    "Ubicación": ("ubicacion", "filtro_tabla_ubicacion"),
}

for _, (_, session_key) in filtros_config.items():
    if session_key not in st.session_state:
        st.session_state[session_key] = "Todos"

col_filtros = st.columns(len(filtros_config))

for idx, (label, (col_name, session_key)) in enumerate(filtros_config.items()):
    with col_filtros[idx]:
        options_raw = sorted(match_filtered_df[col_name].dropna().unique())
        options_labels = ["Todos"] + [str(opt).capitalize() for opt in options_raw]
        value_map = dict(zip(options_labels, ["Todos"] + options_raw))

        try:
            index = options_labels.index(
                str(st.session_state[session_key]).capitalize()
                if st.session_state[session_key] != "Todos"
                else "Todos"
            )
        except ValueError:
            index = 0

        selected_label = st.selectbox(label, options_labels, index=index, key=session_key + "_select")
        st.session_state[session_key] = value_map[selected_label]

# ✅ Apply filters
for _, (col_name, session_key) in filtros_config.items():
    val = st.session_state[session_key]
    if val != "Todos":
        tabla_df = tabla_df[tabla_df[col_name] == val]

# ✅ Clean up for display
if "partido" in tabla_df.columns:
    tabla_df = tabla_df.drop(columns=["partido"])

column_renames = {
    "posicion": "Torre",
    "saltador": "Saltador",
    "ubicacion": "Ubicación",
    "cant_line": "Cantidad de Lines",
    "desc": "Descripción",
    "tipo_line": "Tipo de Line"
}
tabla_df = tabla_df.rename(columns=column_renames)

ordered_columns = ["Torre", "Saltador", "Ubicación", "Cantidad de Lines", "Descripción", "Tipo de Line"]
tabla_df = tabla_df[ordered_columns]

# ✅ Custom CSS Table Styles
st.markdown("""
<style>
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
}
.custom-table thead th {
    background-color: #f2f2f2;
    color: #212529;
    text-align: left;
    padding: 10px;
    white-space: nowrap;
}
.custom-table tbody td {
    padding: 10px;
    border-bottom: 1px solid #ddd;
    white-space: nowrap;
    color: #212529;
    background-color: #ffffff;
}
.custom-table tbody tr:nth-child(even) td {
    background-color: #fafafa;
}
@media (prefers-color-scheme: dark) {
    .custom-table thead th {
        background-color: #2e2e2e !important;
        color: #ffffff !important;
    }
    .custom-table tbody td {
        background-color: #111111 !important;
        color: #ffffff !important;
        border-bottom: 1px solid #444444 !important;
    }
    .custom-table tbody tr:nth-child(even) td {
        background-color: #1e1e1e !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ✅ Render Table
html_table = tabla_df.to_html(classes='custom-table', index=False, escape=False)
html_table = html_table.replace(' style="text-align: right;"', '')
st.markdown(f"<div style='overflow-x: auto;'>{html_table}</div>", unsafe_allow_html=True)
