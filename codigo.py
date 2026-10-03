# titulo sistemas de vendas 
# seçao  cadastrar vendas
   # campo  data
   # campo  vendedor - ana , Bruno  e carla
  # campo  produto - notebook ,  fone , celular
  # campo  de quantidade 
  # campo valor 
  #  botao cadastrar vendas
   # quando eu clicar no botao -> adicionar a venda na tabela
#secao vendas cadastradas
    # tabela com as vendas 
#seçao dashboard
  # card/metrica -> faturamento  total
    # grafico de barra /coluna -> venda por vendedor 
    # grafico de pizza ->  venda de produto

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Sistema de Vendas",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO = Path("vendas.csv")

# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>

    /* Fundo principal */
    .stApp {
        background-color: #f5f7fb;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    /* Título */
    .titulo {
        font-size: 38px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 5px;
    }

    .subtitulo {
        color: #6b7280;
        font-size: 16px;
        margin-bottom: 30px;
    }

    /* Cards */
    .card {
        background: white;
        padding: 22px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
    }

    .card-titulo {
        color: #6b7280;
        font-size: 14px;
        font-weight: 600;
    }

    .card-valor {
        color: #111827;
        font-size: 28px;
        font-weight: 700;
        margin-top: 8px;
    }

    /* Botões */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Tabelas */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# CARREGAR BASE
# ============================================================

if ARQUIVO.exists():

    tabela_vendas = pd.read_csv(ARQUIVO)

else:

    tabela_vendas = pd.DataFrame(
        columns=[
            "data",
            "vendedor",
            "produto",
            "quantidade",
            "valor"
        ]
    )

# Garantir tipos corretos

if not tabela_vendas.empty:

    tabela_vendas["data"] = pd.to_datetime(
        tabela_vendas["data"],
        errors="coerce"
    )

    tabela_vendas["quantidade"] = pd.to_numeric(
        tabela_vendas["quantidade"],
        errors="coerce"
    ).fillna(0)

    tabela_vendas["valor"] = pd.to_numeric(
        tabela_vendas["valor"],
        errors="coerce"
    ).fillna(0)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    '<div class="titulo">💰 Sistema de Vendas</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">Gerencie suas vendas e acompanhe seus resultados</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR - CADASTRO
# ============================================================

st.sidebar.title("🛒 Nova Venda")

st.sidebar.markdown("---")

data = st.sidebar.date_input(
    "📅 Data",
    value=pd.Timestamp.today()
)

vendedores = ["Ana", "Bruno", "Carla"]

vendedor = st.sidebar.selectbox(
    "👤 Vendedor",
    vendedores
)

produtos = [
    "Notebook",
    "Celular",
    "Fone"
]

produto = st.sidebar.selectbox(
    "📦 Produto",
    produtos
)

quantidade = st.sidebar.number_input(
    "🔢 Quantidade",
    min_value=1,
    value=1,
    step=1
)

valor = st.sidebar.number_input(
    "💰 Valor da venda",
    min_value=0.0,
    value=0.0,
    step=10.0,
    format="%.2f"
)

st.sidebar.markdown("---")

botao_cadastrar = st.sidebar.button(
    "➕ Cadastrar venda",
    use_container_width=True
)


# ============================================================
# CADASTRAR VENDA
# ============================================================

if botao_cadastrar:

    nova_venda = {
        "data": str(data),
        "vendedor": vendedor,
        "produto": produto,
        "quantidade": quantidade,
        "valor": valor
    }

    tabela_vendas.loc[len(tabela_vendas)] = nova_venda

    tabela_vendas.to_csv(
        ARQUIVO,
        index=False
    )

    st.success("✅ Venda cadastrada com sucesso!")

    st.rerun()


# ============================================================
# FILTROS
# ============================================================

st.subheader("🔎 Filtros")

col1, col2, col3 = st.columns(3)

with col1:

    filtro_vendedor = st.multiselect(
        "Vendedor",
        options=sorted(tabela_vendas["vendedor"].dropna().unique()),
        placeholder="Todos"
    )

with col2:

    filtro_produto = st.multiselect(
        "Produto",
        options=sorted(tabela_vendas["produto"].dropna().unique()),
        placeholder="Todos"
    )

with col3:

    filtro_data = st.date_input(
        "Período",
        value=(
            tabela_vendas["data"].min().date()
            if not tabela_vendas.empty and tabela_vendas["data"].notna().any()
            else pd.Timestamp.today().date(),
            tabela_vendas["data"].max().date()
            if not tabela_vendas.empty and tabela_vendas["data"].notna().any()
            else pd.Timestamp.today().date()
        )
    )


# ============================================================
# APLICAR FILTROS
# ============================================================

vendas_filtradas = tabela_vendas.copy()

if filtro_vendedor:

    vendas_filtradas = vendas_filtradas[
        vendas_filtradas["vendedor"].isin(filtro_vendedor)
    ]

if filtro_produto:

    vendas_filtradas = vendas_filtradas[
        vendas_filtradas["produto"].isin(filtro_produto)
    ]

if len(filtro_data) == 2:

    inicio = pd.Timestamp(filtro_data[0])
    fim = pd.Timestamp(filtro_data[1])

    vendas_filtradas = vendas_filtradas[
        (vendas_filtradas["data"] >= inicio)
        &
        (vendas_filtradas["data"] <= fim)
    ]


# ============================================================
# MÉTRICAS
# ============================================================

st.markdown("### 📊 Resumo")

faturamento = vendas_filtradas["valor"].sum()

quantidade_vendas = len(vendas_filtradas)

quantidade_produtos = vendas_filtradas["quantidade"].sum()

ticket_medio = (
    faturamento / quantidade_vendas
    if quantidade_vendas > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-titulo">💰 FATURAMENTO</div>
            <div class="card-valor">
                R$ {faturamento:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-titulo">🛒 VENDAS</div>
            <div class="card-valor">
                {quantidade_vendas}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-titulo">📦 PRODUTOS</div>
            <div class="card-valor">
                {quantidade_produtos:.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-titulo">🎯 TICKET MÉDIO</div>
            <div class="card-valor">
                R$ {ticket_medio:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# GRÁFICOS
# ============================================================

st.markdown("### 📈 Dashboard")

if not vendas_filtradas.empty:

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # VENDAS POR VENDEDOR
    # --------------------------------------------------------

    with col1:

        dados_vendedor = (
            vendas_filtradas
            .groupby("vendedor", as_index=False)["valor"]
            .sum()
        )

        grafico1 = px.bar(
            dados_vendedor,
            x="vendedor",
            y="valor",
            title="💼 Faturamento por vendedor",
            labels={
                "vendedor": "Vendedor",
                "valor": "Faturamento"
            },
            text_auto=".2s"
        )

        grafico1.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified"
        )

        st.plotly_chart(
            grafico1,
            use_container_width=True
        )


    # --------------------------------------------------------
    # VENDAS POR PRODUTO
    # --------------------------------------------------------

    with col2:

        dados_produto = (
            vendas_filtradas
            .groupby("produto", as_index=False)["valor"]
            .sum()
        )

        grafico2 = px.pie(
            dados_produto,
            names="produto",
            values="valor",
            hole=0.55,
            title="📦 Vendas por produto"
        )

        grafico2.update_layout(
            paper_bgcolor="white"
        )

        st.plotly_chart(
            grafico2,
            use_container_width=True
        )


    # --------------------------------------------------------
    # EVOLUÇÃO DAS VENDAS
    # --------------------------------------------------------

    dados_data = (
        vendas_filtradas
        .groupby("data", as_index=False)["valor"]
        .sum()
    )

    grafico3 = px.line(
        dados_data,
        x="data",
        y="valor",
        markers=True,
        title="📅 Evolução do faturamento",
        labels={
            "data": "Data",
            "valor": "Faturamento"
        }
    )

    grafico3.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        grafico3,
        use_container_width=True
    )

else:

    st.info("📭 Nenhuma venda encontrada para os filtros selecionados.")


# ============================================================
# TABELA
# ============================================================

st.markdown("### 📋 Vendas cadastradas")

if not vendas_filtradas.empty:

    tabela_visual = vendas_filtradas.copy()

    tabela_visual["data"] = tabela_visual["data"].dt.strftime(
        "%d/%m/%Y"
    )

    tabela_visual["valor"] = tabela_visual["valor"].apply(
        lambda x: f"R$ {x:,.2f}"
    )

    tabela_visual = tabela_visual.rename(
        columns={
            "data": "Data",
            "vendedor": "Vendedor",
            "produto": "Produto",
            "quantidade": "Quantidade",
            "valor": "Valor"
        }
    )

    st.dataframe(
        tabela_visual,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("Nenhuma venda cadastrada.")


# ============================================================
# EXCLUSÃO
# ============================================================

st.markdown("### 🗑️ Gerenciar vendas")

if not tabela_vendas.empty:

    indice_excluir = st.number_input(
        "Digite o índice da venda que deseja excluir",
        min_value=0,
        max_value=len(tabela_vendas) - 1,
        step=1
    )

    if st.button("🗑️ Excluir venda"):

        tabela_vendas = tabela_vendas.drop(
            index=indice_excluir
        ).reset_index(drop=True)

        tabela_vendas.to_csv(
            ARQUIVO,
            index=False
        )

        st.success("Venda excluída.")

        st.rerun()


# ============================================================
# RODAPÉ
# ============================================================

st.markdown("---")

st.caption(
    "Sistema de Vendas • Desenvolvido com Python, Streamlit, Pandas e Plotly"
)