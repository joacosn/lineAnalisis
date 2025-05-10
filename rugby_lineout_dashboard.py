import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import numpy as np
from pathlib import Path
import base64

# ✅ Set wide layout
st.set_page_config(layout="wide")

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

# ✅ Función para convertir imagen a base64
def image_to_base64(img_path):
    return base64.b64encode(Path(img_path).read_bytes()).decode()

# ✅ Ruta relativa (ideal que esté en una carpeta tipo /assets dentro del proyecto)
logo_base64 = image_to_base64("assets/ipr_logo.png")

# ✅ Título y logo alineados: título a la izquierda, logo a la derecha
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <h1 style="margin: 0;">Analisis Lines 2025</h1>
    <img src="data:image/png;base64,{logo_base64}" style="height: 55px;">
</div>
""", unsafe_allow_html=True)

# ✅ Custom CSS for cards
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

    /* Light theme */
    .light .kpi-card {
        background-color: #f8f9fa;
        color: #212529;
    }

    /* Dark theme */
    .dark .kpi-card {
        background-color: #444;
        color: #f1f1f1;
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

    /* OVERRIDE BUTTON DESIGN FULLY */
    button[kind="secondary"] {
        background-color: #d4d4d4 !important;
        color: black !important;
        padding: 16px 0 !important;
        border: none !important;
        border-radius: 15px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        width: 100% !important;
        text-align: center !important;
        margin-bottom: 12px !important;
    }

    button[kind="secondary"]:hover {
        background-color: #c6c6c6 !important;
        cursor: pointer;
    }

    /* SELECTED BUTTON STATE — BLUE */
    button[data-testid="baseButton"].selected {
    background-color: #b4dfff !important;
    color: black !important;
}


    </style>
""", unsafe_allow_html=True)




# 📂 Upload the Excel file
# uploaded_file = st.file_uploader("Upload your Rugby Data Excel file", type=['xlsx'])
# ✅ Load Excel with multiple matches from file

@st.cache_data
def load_data():
    return pd.read_excel("Lines_IPR.xlsx")  # Make sure this file is in the same directory

df = load_data()
# st.write("🧾 Columns in your data:", df.columns.tolist())

# ✅ Load match options
match_options = sorted(df['partido'].dropna().unique())

# ✅ Always preselect the first valid match (index 0)
selected_match = st.selectbox("Selecciona un partido", match_options, index=0)

if "selected_zone" not in st.session_state:
    st.session_state.selected_zone = "50-22"


# Line type filter
match_filtered_df = df[df['partido'] == selected_match]

if 'tipo_line' in match_filtered_df.columns:
    tipo_values = sorted(match_filtered_df['tipo_line'].dropna().unique())
    tipo_options = ['Todos'] + [tipo.capitalize() for tipo in tipo_values]
    selected_tipo = st.selectbox("Selecciona el tipo de line", tipo_options)

    if selected_tipo != 'Todos':
        filtered_df = match_filtered_df[match_filtered_df['tipo_line'] == selected_tipo.lower()]
    else:
        filtered_df = match_filtered_df
else:
    st.warning("⚠️ Column 'tipo_line' not found. Showing all lineouts.")
    filtered_df = match_filtered_df

# 🧼 Disable typing in dropdowns using CSS/JS hack
st.markdown("""
    <script>
    const boxes = window.parent.document.querySelectorAll('input[type="text"]');
    boxes.forEach(box => box.setAttribute('readonly', true));
    </script>
    <style>
    input[type="text"] {
        caret-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.field-button {
    background-color: #e0e0e0;
    border: none;
    color: black;
    padding: 20px;
    margin-bottom: 15px;
    width: 100%;
    border-radius: 15px;
    font-size: 20px;
    font-weight: 600;
    text-align: center;
    transition: 0.2s;
}

.field-button:hover {
    background-color: #cfcfcf;
    cursor: pointer;
}

.field-button.active {
    background-color: #c2dbff;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# 🚨 KPIs
most_used_player = filtered_df['saltador'].mode()[0]
most_used_position = filtered_df['posicion'].mode()[0]
total_lineouts = filtered_df['cant_line'].count()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Saltador mas utilizado</div>
            <div class="kpi-value">{most_used_player}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Posicion mas utilizada</div>
            <div class="kpi-value">{most_used_position}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Cant. Lines</div>
            <div class="kpi-value">{total_lineouts}</div>
        </div>
    """, unsafe_allow_html=True)

# 📊 Lineouts Overview Section
# st.subheader("Lineouts Overview")

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <hr style="border: none; height: 3px; background-color: #e0e0e0; margin: 20px 0;">
""", unsafe_allow_html=True)


chart_col1, divider_col, chart_col2 = st.columns([1, 0.005, 1])

# ➤ Chart 1: Lineouts per Position
with chart_col1:
    st.markdown("#### 📌 Cant. de lines por torre")

    pos_df = filtered_df[['posicion']].dropna()
    pos_df['posicion'] = pos_df['posicion'].astype(str).str.strip()

    pos_count = (
        pos_df.groupby('posicion')
        .size()
        .reset_index(name='count')
        .sort_values(by='count', ascending=False)
    )
    max_y = int(pos_count['count'].max())
    tick_values = list(range(0, max_y + 2))

    y_axis = alt.Axis(title='Cant. Lines', values=tick_values, format='d')

    base = alt.Chart(pos_count).mark_bar(size=50).encode(
        x=alt.X('posicion:N', title='Torre',
            axis=alt.Axis(labelAngle=0, labelColor='#333')),
        y=alt.Y('count:Q', axis=y_axis),
        tooltip=['posicion', 'count']
    )

    text = alt.Chart(pos_count).mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        x='posicion:N',
        y='count:Q',
        text='count:Q'
    )

    chart = (base + text).properties(
        width='container',
        height=400,
        # title='Number of Lineouts per Position'
    )

    st.altair_chart(chart, use_container_width=True)

with divider_col:
    st.markdown(
        """
        <div style='
            height: 420px;
            border-left: 3px solid #d3d3d3;
            margin: auto;
        '></div>
        """,
        unsafe_allow_html=True
    )


# ➤ Chart 2: Lineouts per Player
with chart_col2:
    st.markdown("#### 🧍 Cant. lines por saltador")

    player_df = filtered_df[['saltador']].dropna()
    player_df['saltador'] = player_df['saltador'].astype(str).str.strip()

    player_count = (
        player_df.groupby('saltador')
        .size()
        .reset_index(name='count')
        .sort_values(by='count', ascending=False)
    )

    max_y = int(player_count['count'].max())
    tick_values = list(range(0, max_y + 2))

    y_axis = alt.Axis(title='Cant. Lines', values=tick_values, format='d')

    base = alt.Chart(player_count).mark_bar(size=50).encode(
        x=alt.X('saltador:N', title='Nro. Saltador',
            axis=alt.Axis(labelAngle=0, labelColor='#333')),
        y=alt.Y('count:Q', axis=y_axis),
        tooltip=['saltador', 'count']
    )


    text = alt.Chart(player_count).mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        x='saltador:N',
        y='count:Q',
        text='count:Q'
    )

    chart = (base + text).properties(
        width='container',
        height=400,
        # title='Number of Lineouts per Player'
    )

    st.altair_chart(chart, use_container_width=True)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <hr style="border: none; height: 3px; background-color: #e0e0e0; margin: 20px 0;">
""", unsafe_allow_html=True)


st.subheader("📍 Eleccion de torre por posicion de cancha")

left_col, divider_col,right_col = st.columns([1, 0.005, 3])

# Initialize session state
if "selected_zone" not in st.session_state:
    st.session_state.selected_zone = "50-22"  # Default

with left_col:
    st.markdown("### Lugar de la cancha")

    if "selected_zone" not in st.session_state:
        st.session_state.selected_zone = "50-22"

    zones = ["50-22", "22-5", "5"]

    for zone in zones:
        clicked = st.button(zone, key=f"btn_{zone}")
        if clicked:
            st.session_state.selected_zone = zone

    st.markdown(f"""
        <script>
        const btns = window.parent.document.querySelectorAll('button[kind="secondary"]');
        btns.forEach(btn => {{
            if (btn.innerText === '{zone}') {{
                btn.classList.remove("selected");
                {"btn.classList.add('selected');" if st.session_state.selected_zone == zone else ""}
            }}
        }});
        </script>
    """, unsafe_allow_html=True)

with divider_col:
    st.markdown(
        """
        <div style='
            height: 420px;
            border-left: 3px solid #d3d3d3;
            margin: auto;
        '></div>
        """,
        unsafe_allow_html=True
    )

with right_col:
    selected_zone = st.session_state.selected_zone

    if selected_zone:
        st.markdown(f"### Torres más utilizadas en {selected_zone} metros")

        zone_df = filtered_df[filtered_df['ubicacion'] == selected_zone]

        if zone_df.empty:
            st.info("⚠️ No data available for this zone.")
        else:
            pie_data = (
                zone_df.groupby('posicion')
                .size()
                .reset_index(name='count')
            )

            fig = px.pie(
                pie_data,
                names='posicion',
                values='count',
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Safe
            )

            # ✅ Update trace to make % labels bolder & bigger
            fig.update_traces(
                textinfo='percent',
                textfont_size=18,
                textfont_color='#333',  # más oscuro
            )

            # ✅ Update layout for bigger legend
            fig.update_layout(
            legend=dict(
                orientation="h",       # Horizontal
                yanchor="bottom",
                y=1.05,                # Un poco arriba del gráfico
                xanchor="center",
                x=0.5,
                font=dict(size=16)
            )
)
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("⬅️ Select a zone on the left to view position usage.")

# 📄 Styled Data Table independiente del resto
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <hr style="border: none; height: 5px; background-color: #e0e0e0; margin: 20px 0;">
""", unsafe_allow_html=True)
st.subheader("Detalle de lines")

# 👉 Base solo filtrada por partido (no tipo_line global)
tabla_df = match_filtered_df.copy()

# --- Filtros para la tabla de lineouts ---

filtros_config = {
    "Tipo de Line": ("tipo_line", "filtro_tabla_tipo"),
    "Torre": ("posicion", "filtro_tabla_torre"),
    "Saltador": ("saltador", "filtro_tabla_saltador"),
    "Ubicación": ("ubicacion", "filtro_tabla_ubicacion"),
}

# Inicializar valores
for _, (_, session_key) in filtros_config.items():
    if session_key not in st.session_state:
        st.session_state[session_key] = "Todos"

# Layout con filtros
col_filtros = st.columns(len(filtros_config))

for idx, (label, (col_name, session_key)) in enumerate(filtros_config.items()):
    with col_filtros[idx]:
        options_raw = sorted(match_filtered_df[col_name].dropna().unique())
        options_labels = ["Todos"] + [str(opt).capitalize() for opt in options_raw]
        value_map = dict(zip(options_labels, ["Todos"] + options_raw))

        selected_label = st.selectbox(
            label,
            options_labels,
            index=options_labels.index(st.session_state[session_key].capitalize() if st.session_state[session_key] != "Todos" else "Todos"),
            key=session_key + "_select"
        )

        st.session_state[session_key] = value_map[selected_label]

# Aplicar filtros
tabla_df = match_filtered_df.copy()
for _, (col_name, session_key) in filtros_config.items():
    valor = st.session_state[session_key]
    if valor != "Todos":
        tabla_df = tabla_df[tabla_df[col_name] == valor]

# ✅ Drop 'partido' column
if "partido" in tabla_df.columns:
    display_df = tabla_df.drop(columns=["partido"])
else:
    display_df = tabla_df.copy()

# ✅ Rename columns
column_renames = {
    "posicion": "Torre",
    "saltador": "Saltador",
    "ubicacion": "Ubicación",
    "cant_line": "Cantidad de Lines",
    "desc": "Descripción",
    "tipo_line": "Tipo de Line"
}
display_df = display_df.rename(columns=column_renames)

# ✅ Force correct column order
ordered_columns = [
    "Torre",
    "Saltador",
    "Ubicación",
    "Cantidad de Lines",
    "Descripción",
    "Tipo de Line"
]
display_df = display_df[ordered_columns]

# ✅ Inject CSS & HTML for styled table with dark mode support
st.markdown("""
<style>
/* Tabla base */
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
}

/* Encabezado */
.custom-table thead th {
    background-color: #f2f2f2;
    color: #212529;
    text-align: left;
    padding: 10px;
    white-space: nowrap;
}

/* Celdas */
.custom-table tbody td {
    padding: 10px;
    border-bottom: 1px solid #ddd;
    white-space: nowrap;
    color: #212529;
    background-color: #ffffff;
}

/* Zebra striping */
.custom-table tbody tr:nth-child(even) td {
    background-color: #fafafa;
}

/* --- DARK MODE OVERRIDE --- */
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


# ✅ Display table
# ✅ Clean pandas inline styles to ensure dark mode CSS applies correctly
html_table = display_df.to_html(classes='custom-table', index=False, escape=False)
html_table = html_table.replace(' style="text-align: right;"', '')
html_table = html_table.replace(' style="text-align: left;"', '')
html_table = html_table.replace(' style="text-align: center;"', '')

# ✅ Display table with dark/light mode support fully working
st.markdown(f"""
<div style="overflow-x: auto;">
    {html_table}
</div>
""", unsafe_allow_html=True)

