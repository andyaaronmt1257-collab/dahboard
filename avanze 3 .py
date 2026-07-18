import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config("SST-MCON", "🦺", layout="wide")

st.markdown("""
<style>
/* Fondo general y eliminación de la franja blanca superior */
html, body, .stApp, [data-testid="stAppViewContainer"]{
    background:#07111f !important;
    color:#f4f7fb !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], #MainMenu, footer{
    display:none !important;
}
.block-container{padding-top:1rem !important}

/* Barra lateral con letras más visibles */
[data-testid="stSidebar"]{
    background:#0b1727 !important;
    border-right:1px solid #263850;
}
[data-testid="stSidebar"] *{
    color:#f2f5f9 !important;
    opacity:1 !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span{
    color:#e8edf4 !important;
    font-weight:600 !important;
}
div[role="radiogroup"] label{
    padding:8px 10px !important;
    border-radius:7px !important;
}
div[role="radiogroup"] label:hover{
    background:#15253a !important;
}

/* Selectores oscuros, sin cuadros blancos */
div[data-baseweb="select"] > div{
    background:#111d2d !important;
    border:1px solid #30445f !important;
    color:white !important;
}
div[data-baseweb="select"] span{color:white !important}
div[data-baseweb="popover"]{background:#111d2d !important}

/* Encabezado como la segunda imagen */
.encabezado{
    background:#0b1727;
    border:1px solid #263850;
    border-left:6px solid #ff7a21;
    border-radius:10px;
    padding:18px 22px;
    margin-bottom:18px;
}
.encabezado h1{
    margin:0;color:white;font-size:30px;font-weight:800;
}
.encabezado p{
    margin:6px 0 0;color:#c7d0dc;
}

/* Tarjetas */
.card{
    background:#101c2d;border:1px solid #263850;border-radius:12px;
    padding:18px;text-align:center;
}
.card h2{margin:0;font-size:30px;color:white}
.card p{margin:8px 0 0;color:#d6deea;font-weight:700}
div[data-testid="stVerticalBlockBorderWrapper"]{
    background:#101c2d;border:1px solid #263850;border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def crear_datos():
    np.random.seed(26)
    n = 400
    reportes = pd.DataFrame({
        "Código":[f"INC-{i+1:04d}" for i in range(n)],
        "Fecha":pd.to_datetime(np.random.choice(pd.date_range("2026-01-01","2026-05-31"), n)),
        "Sede":np.random.choice(["Línea 2 Metro","Antamina","Marcona","Aeropuerto","Puerto Paita"], n),
        "Área":np.random.choice(["Operaciones","Mantenimiento","Almacén","Túneles"], n),
        "Tipo":np.random.choice(["Condición insegura","Acto subestándar","Equipo defectuoso","Riesgo ambiental"], n),
        "Criticidad":np.random.choice(["Alto","Medio","Bajo"], n, p=[.20,.45,.35]),
        "Estado":np.random.choice(["Nuevo","Validando","En acción","Completado","Rechazado"], n,
                                  p=[.12,.18,.25,.40,.05]),
        "Tiempo respuesta":np.round(np.random.uniform(1,10,n),2)
    })

    trabajadores = pd.DataFrame({
        "Trabajador":[f"TRAB-{i+1:03d}" for i in range(90)],
        "Estado médico":np.random.choice(["Apto","No Apto","Apto con restricciones"],90,p=[.68,.12,.20]),
        "Sede":np.random.choice(reportes["Sede"].unique(),90)
    })

    epp = pd.DataFrame({
        "EPP":np.random.choice(["Casco","Guantes","Arnés","Lentes","Respirador"],120),
        "Estado":np.random.choice(["Vigente","Por renovar","Vencido","Stock crítico"],120,
                                  p=[.55,.20,.15,.10]),
        "Sede":np.random.choice(reportes["Sede"].unique(),120)
    })

    simulacros = pd.DataFrame({
        "Sede":reportes["Sede"].unique(),
        "Tiempo objetivo":[6,7,8,6,7],
        "Tiempo real":[5.8,8.4,7.5,6.9,9.1]
    })
    simulacros["Resultado"] = np.where(
        simulacros["Tiempo real"] <= simulacros["Tiempo objetivo"],
        "Aprobado","Deficiente"
    )
    return reportes, trabajadores, epp, simulacros

reportes, trabajadores, epp, simulacros = crear_datos()

with st.sidebar:
    st.markdown("## 🦺 SST-MCON")
    modulo = st.radio("Módulo",[
        "Resumen Ejecutivo","Seguridad Operacional",
        "Salud Ocupacional","Gestión EPP","Emergencias"
    ])
    st.divider()
    sede = st.selectbox("Sede",["Todas"]+sorted(reportes["Sede"].unique()))
    criticidad = st.selectbox("Criticidad",["Todas","Alto","Medio","Bajo"])

df = reportes.copy()
if sede != "Todas":
    df = df[df["Sede"]==sede]
if criticidad != "Todas":
    df = df[df["Criticidad"]==criticidad]

def card(valor, titulo):
    st.markdown(f"<div class='card'><h2>{valor}</h2><p>{titulo}</p></div>",
                unsafe_allow_html=True)

def estilo(fig, alto=310):
    fig.update_layout(
        height=alto,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f4f7fb"),
        title_font=dict(color="#ffffff", size=17),
        legend=dict(font=dict(color="#e7edf5")),
        margin=dict(l=10,r=10,t=48,b=10)
    )
    fig.update_xaxes(
        tickfont=dict(color="#dce4ee"),
        title_font=dict(color="#dce4ee"),
        gridcolor="rgba(220,228,238,.25)"
    )
    fig.update_yaxes(
        tickfont=dict(color="#dce4ee"),
        title_font=dict(color="#dce4ee"),
        gridcolor="rgba(220,228,238,.25)"
    )
    return fig

st.markdown("""
<div class="encabezado">
    <h1>DASHBOARD EJECUTIVO SST - MCON</h1>
    <p>Gestión Integral de Seguridad y Salud en el Trabajo</p>
</div>
""", unsafe_allow_html=True)

if modulo == "Resumen Ejecutivo":
    total = len(df)
    altos = len(df[(df["Criticidad"]=="Alto") & (df["Estado"]!="Completado")])
    tiempo = df["Tiempo respuesta"].mean() if total else 0
    no_aptos = (trabajadores["Estado médico"]=="No Apto").sum()
    epp_alerta = epp["Estado"].isin(["Vencido","Stock crítico"]).sum()

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: card(total,"REPORTES")
    with c2: card(altos,"RIESGOS ALTOS")
    with c3: card(f"{tiempo:.1f} h","TIEMPO RESPUESTA")
    with c4: card(no_aptos,"NO APTOS")
    with c5: card(epp_alerta,"ALERTAS EPP")

    a,b,c = st.columns(3)
    with a:
        x=df["Sede"].value_counts().reset_index()
        x.columns=["Sede","Reportes"]
        fig=px.bar(x,x="Reportes",y="Sede",orientation="h",
                   title="Reportes por sede",color_discrete_sequence=["#1768e5"])
        st.plotly_chart(estilo(fig),use_container_width=True)
    with b:
        x=df["Criticidad"].value_counts().reset_index()
        x.columns=["Criticidad","Reportes"]
        fig=px.pie(x,names="Criticidad",values="Reportes",hole=.55,
                   title="Reportes por criticidad",color="Criticidad",
                   color_discrete_map={"Alto":"#f47a2a","Medio":"#1f8cff","Bajo":"#182a96"})
        st.plotly_chart(estilo(fig),use_container_width=True)
    with c:
        x=df.assign(Mes=df["Fecha"].dt.to_period("M").astype(str))
        x=x.groupby("Mes").size().reset_index(name="Reportes")
        fig=px.line(x,x="Mes",y="Reportes",markers=True,title="Evolución mensual")
        fig.update_traces(line_color="#1f8cff")
        st.plotly_chart(estilo(fig),use_container_width=True)

    a,b = st.columns(2)
    with a:
        x=df["Estado"].value_counts().reset_index()
        x.columns=["Estado","Reportes"]
        fig=px.bar(x,x="Estado",y="Reportes",title="Estado de los reportes",
                   color_discrete_sequence=["#1f8cff"])
        st.plotly_chart(estilo(fig),use_container_width=True)
    with b:
        cumplimiento = 100 - altos/max(total,1)*100
        fig=go.Figure(go.Indicator(
            mode="gauge+number",value=cumplimiento,
            number={"suffix":"%"},
            title={"text":"Cumplimiento SST"},
            gauge={"axis":{"range":[0,100]},
                   "bar":{"color":"#1768e5"},
                   "threshold":{"line":{"color":"#f47a2a","width":4},"value":90}}
        ))
        st.plotly_chart(estilo(fig),use_container_width=True)

elif modulo == "Seguridad Operacional":
    st.subheader("Reportes de peligro")
    st.dataframe(df.sort_values("Fecha",ascending=False),use_container_width=True)
    st.download_button("Descargar CSV",df.to_csv(index=False).encode("utf-8"),
                       "reportes_sst.csv","text/csv")

elif modulo == "Salud Ocupacional":
    st.subheader("Estado médico ocupacional")
    x=trabajadores["Estado médico"].value_counts().reset_index()
    x.columns=["Estado","Trabajadores"]
    fig=px.pie(x,names="Estado",values="Trabajadores",hole=.5,
               color_discrete_sequence=["#1f8cff","#f47a2a","#182a96"])
    st.plotly_chart(estilo(fig),use_container_width=True)
    st.dataframe(trabajadores,use_container_width=True)

elif modulo == "Gestión EPP":
    st.subheader("Control de EPP")
    x=epp["Estado"].value_counts().reset_index()
    x.columns=["Estado","Cantidad"]
    fig=px.bar(x,x="Estado",y="Cantidad",color="Estado",title="Vigencia y stock de EPP")
    st.plotly_chart(estilo(fig),use_container_width=True)
    st.dataframe(epp,use_container_width=True)

else:
    st.subheader("Simulacros y emergencias")
    fig=px.bar(simulacros,x="Sede",y=["Tiempo objetivo","Tiempo real"],
               barmode="group",title="Tiempo objetivo vs. tiempo real")
    st.plotly_chart(estilo(fig),use_container_width=True)
    st.dataframe(simulacros,use_container_width=True)