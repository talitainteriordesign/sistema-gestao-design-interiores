import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

st.set_page_config(page_title="Gestão Design", layout="centered")
st.markdown("""
<style>
body {
    background-color: #F8F6F3;
}
.main {
    background-color: #F8F6F3;
}
h1 {
    color: #2C2C2C;
    font-weight: 600;
}
h2, h3 {
    color: #5A5A5A;
}
.stButton>button {
    background-color: #8B5CF6;
    color: white;
    border-radius: 12px;
    padding: 8px 16px;
    border: none;
}
.stButton>button:hover {
    background-color: #7C3AED;
}
</style>
""", unsafe_allow_html=True)

st.title("💼 Sistema Estratégico de Gestão - Design de Interiores")
st.caption("Desenvolvido por Talita Freitas")

arquivo = "dados.csv"

# Criar arquivo se não existir
if not os.path.exists(arquivo):
    df_inicial = pd.DataFrame(columns=[
        "Data",
        "Cliente",
        "Valor_Obra",
        "Percentual_Honorarios",
        "Honorarios",
        "Custo_Estimado",
        "Custo_Real",
        "Lucro"
    ])
    df_inicial.to_csv(arquivo, index=False)

# AGORA sempre carregamos o arquivo
df = pd.read_csv(arquivo)

st.header("Cadastrar Novo Projeto")

data_projeto = st.date_input("Data do Projeto")
cliente = st.text_input("Nome do Cliente")
valor_obra = st.number_input("Valor Total da Obra", min_value=0.0)
percentual = st.number_input("Percentual de Honorários (%)", min_value=0.0)
custo_estimado = st.number_input("Custo Estimado", min_value=0.0)
custo_real = st.number_input("Custo Real", min_value=0.0)

if st.button("Salvar Projeto"):
    honorarios = valor_obra * (percentual / 100)
    lucro = honorarios - custo_real

    novo_projeto = pd.DataFrame([{
        "Data": data_projeto,
        "Cliente": cliente,
        "Valor_Obra": valor_obra,
        "Percentual_Honorarios": percentual,
        "Honorarios": honorarios,
        "Custo_Estimado": custo_estimado,
        "Custo_Real": custo_real,
        "Lucro": lucro
    }])

    novo_projeto.to_csv(arquivo, mode="a", header=False, index=False)
    st.success("Projeto salvo com sucesso!")
    st.rerun()

st.header("📊 Projetos Cadastrados")

df = pd.read_csv(arquivo)

if not df.empty:
    df["Data"] = pd.to_datetime(df["Data"])

    st.subheader("🔎 Filtro por Mês")

    mes_selecionado = st.selectbox(
        "Selecione o mês",
        df["Data"].dt.to_period("M").astype(str).unique()
    )

    df_filtrado = df[df["Data"].dt.to_period("M").astype(str) == mes_selecionado]

    st.dataframe(df_filtrado)
    st.subheader("🗑 Excluir Projeto")

cliente_excluir = st.selectbox(
    "Selecione o cliente para excluir",
    df["Cliente"].unique()
)

if st.button("Excluir Projeto"):
    df = df[df["Cliente"] != cliente_excluir]
    df.to_csv(arquivo, index=False)
    st.success("Projeto excluído com sucesso!")
    st.rerun()
else:
    st.info("Nenhum projeto cadastrado ainda.")

st.header("📈 Custos")

if not df.empty:
    total_faturado = df["Honorarios"].sum()
    total_lucro = df["Lucro"].sum()

    # 👇 COLOQUE AQUI
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Honorários", f"R$ {total_faturado:,.2f}")

    with col2:
        st.metric("Lucro Total", f"R$ {total_lucro:,.2f}")

    with col3:
        st.metric("Projetos", len(df))


st.header("📈 Dashboard")

if not df.empty:
    total_faturado = df["Honorarios"].sum()
    total_lucro = df["Lucro"].sum()

    st.write(f"Total Honorários: R$ {total_faturado:,.2f}")
    st.write(f"Lucro Total: R$ {total_lucro:,.2f}")

    df["Mes"] = df["Data"].dt.to_period("M").astype(str)
    lucro_mensal = df.groupby("Mes")["Lucro"].sum()

    fig, ax = plt.subplots()
    ax.bar(lucro_mensal.index, lucro_mensal.values)
    ax.set_title("Lucro por Mês")
    ax.set_ylabel("Lucro (R$)")
    plt.xticks(rotation=45)

    st.pyplot(fig)

    st.subheader("📄 Exportar Relatório")

if st.button("Gerar Relatório PDF"):

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch

    doc = SimpleDocTemplate("relatorio.pdf")
    elements = []

    styles = getSampleStyleSheet()

    # 🎨 Estilo personalizado
    titulo_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph("Relatório Executivo de Gestão", titulo_style))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(f"Total Honorários: R$ {total_faturado:,.2f}", normal_style))
    elements.append(Paragraph(f"Lucro Total: R$ {total_lucro:,.2f}", normal_style))
    elements.append(Paragraph(f"Projetos cadastrados: {len(df)}", normal_style))
    elements.append(Spacer(1, 0.5 * inch))

    # 📊 Tabela com todos os projetos
    dados_tabela = [["Data", "Cliente", "Honorários", "Lucro"]]

    for _, row in df.iterrows():
        dados_tabela.append([
            row["Data"].strftime("%d/%m/%Y"),
            row["Cliente"],
            f"R$ {row['Honorarios']:,.2f}",
            f"R$ {row['Lucro']:,.2f}"
        ])

    tabela = Table(dados_tabela)

    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (2,1), (-1,-1), "RIGHT"),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
    ]))

    elements.append(tabela)

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Desenvolvido por Talita Freitas", styles["Italic"]))

    doc.build(elements)

    st.success("Relatório gerado com sucesso!")
else:
    st.info("Nenhum projeto cadastrado ainda.")