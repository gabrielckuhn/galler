"""
Requisição de Exame - Tuberculose (GAL) - Preenchimento automático
--------------------------------------------------------------------
Formulário Streamlit que coleta os dados e gera o PDF oficial preenchido,
usando o PDF original (GAL_TUBERCULOSE.pdf) como fundo e sobrepondo o
texto/marcações nas coordenadas corretas.
"""

import io
from datetime import date

import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TEMPLATE_PATH = "GAL_TUBERCULOSE.pdf"   # coloque o PDF original nesta pasta
PAGE_WIDTH = 595.2756
PAGE_HEIGHT = 841.8898

st.set_page_config(page_title="Requisição TB - GAL", layout="centered")

# ---------------------------------------------------------------------------
# Coordenadas (em pontos PDF, origem no canto inferior esquerdo)
# Mapeadas manualmente a partir do layout do formulário oficial.
# Ajuste aqui se algum campo sair um pouco deslocado na impressão.
# ---------------------------------------------------------------------------

TEXT_FIELD_SIZE = 9          # tamanho de fonte padrão para texto digitado
CHECK_FIELD_SIZE = 8         # tamanho de fonte do "X" nas caixinhas

# Campos de texto simples: nome -> (x, y)
TEXT_COORDS = {
    "data_solicitacao": (44, 698),
    "cns_paciente": (94, 668),
    "nome_paciente": (259, 668),
    "data_nascimento": (94, 636),
    "idade_qtd": (158, 633),
    "nacionalidade": (415, 636),
    "etnia": (240, 605),
    "nome_mae": (360, 605),
    "documento1_numero": (165, 579),
    "logradouro": (94, 540),
    "numero_endereco": (534, 538),
    "complemento_logradouro": (44, 505),
    "ponto_referencia": (205, 505),
    "bairro": (393, 505),
    "municipio_residencia": (44, 476),
    "uf_residencia": (548, 476),
    "cep": (44, 444),
    "ddd_telefone": (167, 444),
    "periodo_tratamento_qtd": (362, 376),
    "pesquisas_exames": (44, 185),
    "material_biologico": (122, 185),
}

# Caixinhas de opção (checkbox): marca-se um "X" na posição indicada.
CHECK_COORDS = {
    # Campo 12 - Finalidade
    "finalidade": {
        "Campanha": (170, 705.8),
        "Inquérito": (223, 705.8),
        "Investigação": (268, 706.0),
        "Programa": (158, 696.8),
        "Protocolo": (210, 696.8),
        "Projeto": (248, 696.8),
        "Ignorado": (279, 696.8),
    },
    # Campo 17 - unidade da idade
    "idade_unidade": {
        "Hora(s)": (200, 644.2),
        "Dia(s)": (234, 644.2),
        "Mês(s)": (200, 633.1),
        "Ano(s)": (234, 633.1),
    },
    # Campo 18 - Sexo
    "sexo": {
        "Masculino": (278, 644.8),
        "Feminino": (277, 636.1),
        "Ignorado": (318, 645.1),
    },
    # Campo 20 - Raça/Cor
    "raca_cor": {
        "Branca": (57, 613.1),
        "Preta": (100, 613.1),
        "Parda": (141, 613.1),
        "Amarela": (56, 603.4),
        "Indígena": (98, 603.4),
        "Sem Informação": (138, 603.4),
    },
    # Campo 23 - Documento 1 (sempre CPF)
    "documento1_tipo": {
        "CPF": (82, 579.1),
    },
    # Campo 40 - Finalidade do Exame
    "finalidade_exame": {
        "Diagnóstico": (55, 380.0),
        "Controle": (106, 380.3),
        "Ignorado": (153, 380.2),
    },
    # Campo 41 - Tratamento
    "tratamento": {
        "Nunca Tratou Tuberculose": (222, 386.1),
        "Realizou Tratamento de Tuberculose": (222, 377.3),
    },
    # Campo 42 - unidade do período de tratamento
    "periodo_tratamento_unidade": {
        "Dia": (406, 380.3),
        "Semana": (439, 380.3),
        "Mês": (471, 380.3),
        "Ano": (504, 380.3),
        "Ignorado": (532, 380.7),
    },
    # Campo 43 - População de Risco
    "populacao_risco": {
        "População Prisional": (117, 355.5),
        "População em Situação de Rua": (127, 346.7),
        "Internado/Institucionalizado": (196, 365.6),
        "Profissional de Saúde/Sistema Penitenciário": (196, 356.4),
        "HIV ou Outra Imunodepressão": (196, 347.0),
        "Indígena": (336, 366.1),
        "Imigrante": (336, 356.6),
        "Usuário de Drogas": (336, 347.4),
        "Diabético": (404, 365.2),
        "Tabagista": (404, 356.4),
        "Ignorado": (404, 347.2),
    },
}

UF_LIST = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
]


def fmt_date(d):
    return d.strftime("%d/%m/%Y") if d else ""


def build_overlay(data: dict) -> bytes:
    """Gera uma página PDF (só com o texto/marcações) do tamanho do formulário."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    c.setFillColor(black)

    # Texto simples
    c.setFont("Helvetica", TEXT_FIELD_SIZE)
    for field, (x, y) in TEXT_COORDS.items():
        value = data.get(field)
        if value:
            c.drawString(x, y, str(value))

    # Checkboxes ("X")
    c.setFont("Helvetica-Bold", CHECK_FIELD_SIZE)
    for group, options in CHECK_COORDS.items():
        selected = data.get(group)
        if selected and selected in options:
            x, y = options[selected]
            c.drawString(x, y, "X")

    c.save()
    buf.seek(0)
    return buf.read()


def generate_pdf(data: dict) -> bytes:
    reader = PdfReader(TEMPLATE_PATH)
    writer = PdfWriter()

    overlay_bytes = build_overlay(data)
    overlay_reader = PdfReader(io.BytesIO(overlay_bytes))

    page1 = reader.pages[0]
    page1.merge_page(overlay_reader.pages[0])
    writer.add_page(page1)

    # mantém as páginas seguintes (instruções) sem alteração
    for p in reader.pages[1:]:
        writer.add_page(p)

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.read()


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------

st.title("Requisição de Exame - Tuberculose (GAL)")
st.caption(
    "Preencha os campos abaixo e gere o PDF oficial já preenchido, "
    "pronto para imprimir e assinar."
)

with st.form("gal_form"):

    st.subheader("Requisição")
    col1, col2 = st.columns(2)
    with col1:
        data_solicitacao = st.date_input("Data de Solicitação", value=date.today())
    with col2:
        finalidade = st.selectbox("Finalidade", list(CHECK_COORDS["finalidade"].keys()))

    st.divider()
    st.subheader("Paciente")

    cns_paciente = st.text_input("Cartão Nacional de Saúde (CNS) do Paciente")
    nome_paciente = st.text_input("Nome do Paciente")

    col1, col2, col3 = st.columns(3)
    with col1:
        data_nascimento = st.date_input(
            "Data de Nascimento", value=None, min_value=date(1900, 1, 1)
        )
    with col2:
        idade_qtd = st.text_input("Idade (quantidade)", placeholder="ex: 34")
    with col3:
        idade_unidade = st.selectbox(
            "Unidade da idade", list(CHECK_COORDS["idade_unidade"].keys()), index=3
        )

    col1, col2 = st.columns(2)
    with col1:
        sexo = st.selectbox("Sexo", list(CHECK_COORDS["sexo"].keys()))
    with col2:
        nacionalidade = st.text_input("Nacionalidade", value="Brasileira")

    raca_cor = st.selectbox("Raça/Cor", list(CHECK_COORDS["raca_cor"].keys()))
    etnia = st.text_input("Etnia (se indígena)")
    nome_mae = st.text_input("Nome da Mãe")

    st.markdown("**Documento 1 (CPF)**")
    documento1_numero = st.text_input("Número do CPF")

    st.divider()
    st.subheader("Endereço")

    logradouro = st.text_input("Logradouro (Rua, Avenida...)")
    col1, col2 = st.columns(2)
    with col1:
        numero_endereco = st.text_input("Número")
    with col2:
        complemento_logradouro = st.text_input("Complemento (facultativo)")

    ponto_referencia = st.text_input("Ponto de Referência")
    bairro = st.text_input("Bairro")

    col1, col2 = st.columns(2)
    with col1:
        municipio_residencia = st.text_input("Município de Residência", value="Aracaju")
    with col2:
        uf_residencia = st.selectbox("UF", UF_LIST, index=UF_LIST.index("SE"))

    col1, col2 = st.columns(2)
    with col1:
        cep = st.text_input("CEP")
    with col2:
        ddd_telefone = st.text_input("DDD / Telefone")

    st.divider()
    st.subheader("Informações Clínicas")

    finalidade_exame = st.selectbox(
        "Finalidade do Exame", list(CHECK_COORDS["finalidade_exame"].keys())
    )
    tratamento = st.selectbox("Tratamento", list(CHECK_COORDS["tratamento"].keys()))

    col1, col2 = st.columns(2)
    with col1:
        periodo_tratamento_qtd = st.text_input("Período do Tratamento (quantidade)")
    with col2:
        periodo_tratamento_unidade = st.selectbox(
            "Unidade do período", list(CHECK_COORDS["periodo_tratamento_unidade"].keys())
        )

    populacao_risco = st.selectbox(
        "População de Risco", list(CHECK_COORDS["populacao_risco"].keys())
    )

    st.divider()
    st.subheader("Amostra / Exame")

    pesquisas_exames = st.text_input("Pesquisa(s) / Exame(s) Solicitado(s)")
    material_biologico = st.text_input("Material Biológico")

    submitted = st.form_submit_button("Gerar PDF preenchido")

if submitted:
    data = {
        "data_solicitacao": fmt_date(data_solicitacao),
        "finalidade": finalidade,
        "cns_paciente": cns_paciente,
        "nome_paciente": nome_paciente,
        "data_nascimento": fmt_date(data_nascimento),
        "idade_qtd": idade_qtd,
        "idade_unidade": idade_unidade,
        "sexo": sexo,
        "nacionalidade": nacionalidade,
        "raca_cor": raca_cor,
        "etnia": etnia,
        "nome_mae": nome_mae,
        "documento1_tipo": "CPF",
        "documento1_numero": documento1_numero,
        "logradouro": logradouro,
        "numero_endereco": numero_endereco,
        "complemento_logradouro": complemento_logradouro,
        "ponto_referencia": ponto_referencia,
        "bairro": bairro,
        "municipio_residencia": municipio_residencia,
        "uf_residencia": uf_residencia,
        "cep": cep,
        "ddd_telefone": ddd_telefone,
        "finalidade_exame": finalidade_exame,
        "tratamento": tratamento,
        "periodo_tratamento_qtd": periodo_tratamento_qtd,
        "periodo_tratamento_unidade": periodo_tratamento_unidade,
        "populacao_risco": populacao_risco,
        "pesquisas_exames": pesquisas_exames,
        "material_biologico": material_biologico,
    }

    try:
        pdf_bytes = generate_pdf(data)
        st.success("PDF gerado com sucesso!")
        st.download_button(
            "Baixar PDF preenchido",
            data=pdf_bytes,
            file_name=f"requisicao_tb_{(nome_paciente or 'paciente').strip().replace(' ', '_')}.pdf",
            mime="application/pdf",
        )
    except FileNotFoundError:
        st.error(
            f"Não encontrei o arquivo '{TEMPLATE_PATH}'. Coloque o PDF original "
            "da requisição na mesma pasta do app.py (com esse nome)."
        )
