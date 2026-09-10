import io
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="GAL - Requisição TB", layout="wide")

st.title("Sistema GAL - Requisição de Exame de Tuberculose")
st.write("Preencha os campos abaixo para gerar o PDF da ficha oficial.")

# --- FORMULÁRIO COMPLETO ---
with st.form("form_gal"):
    
    st.subheader("1. Dados da Solicitação")
    col1, col2 = st.columns([1, 2])
    with col1:
        data_solicitacao = st.date_input("11 - Data de Solicitação*", format="DD/MM/YYYY")
    with col2:
        finalidade_req = st.selectbox(
            "12 - Finalidade*",
            [
                "1 - Campanha",
                "2 - Inquérito",
                "3 - Investigação",
                "4 - Programa",
                "5 - Protocolo",
                "6 - Projeto",
                "9 - Ignorado"
            ]
        )

    st.subheader("2. Identificação do Paciente")
    col1, col2 = st.columns(2)
    with col1:
        cns_paciente = st.text_input("14 - CNS do Paciente", max_chars=15)
        nome_paciente = st.text_input("15 - Nome do Paciente*")
        data_nascimento = st.date_input("16 - Data de Nascimento*", format="DD/MM/YYYY")
    with col2:
        nome_mae = st.text_input("22 - Nome da Mãe*")
        cpf_paciente = st.text_input("23 - Documento 1 (CPF)*", max_chars=14)
        nacionalidade = st.text_input("19 - Nacionalidade", value="BRASILEIRA")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        idade_valor = st.number_input("17 - Idade", min_value=0, max_value=120, value=0)
    with col2:
        complemento_idade = st.selectbox(
            "Complemento de Idade",
            ["4 - Ano(s)", "3 - Mês(es)", "2 - Dia(s)", "1 - Hora(s)"]
        )
    with col3:
        sexo = st.radio("18 - Sexo*", ["M - Masculino", "F - Feminino", "1 - Ignorado"])
    with col4:
        raca_cor = st.selectbox(
            "20 - Raça/Cor",
            ["1 - Branca", "2 - Preta", "3 - Parda", "4 - Amarela", "5 - Indígena", "99 - Sem Informação"]
        )

    etnia = st.text_input("21 - Etnia (se indígena)")

    st.subheader("3. Endereço / Residência")
    col1, col2, col3 = st.columns([3, 1, 2])
    with col1:
        logradouro = st.text_input("25 - Logradouro (Rua, Av...)*")
    with col2:
        numero = st.text_input("26 - Número*")
    with col3:
        complemento_end = st.text_input("27 - Complemento (Opcional)")

    col1, col2, col3 = st.columns(3)
    with col1:
        ponto_ref = st.text_input("28 - Ponto de Referência")
    with col2:
        bairro = st.text_input("29 - Bairro*")
    with col3:
        municipio_res = st.text_input("30 - Município de Residência*", value="ARACAJU")

    col1, col2, col3 = st.columns(3)
    with col1:
        uf_res = st.selectbox("32 - UF*", ["SE", "AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE", "SP", "RJ", "MG", "ES", "PR", "SC", "RS", "MS", "MT", "GO", "DF", "AM", "PA", "AC", "RO", "RR", "AP", "TO"])
    with col2:
        cep = st.text_input("33 - CEP", max_chars=9)
    with col3:
        telefone = st.text_input("34 - DDD/Telefone")

    st.subheader("4. Informações Clínicas")
    col1, col2, col3 = st.columns(3)
    with col1:
        finalidade_exame = st.radio("40 - Finalidade do Exame*", ["1 - Diagnóstico", "2 - Controle", "9 - Ignorado"])
    with col2:
        tratamento = st.radio("41 - Tratamento*", ["1 - Nunca Tratou Tuberculose", "2 - Realizou Tratamento de Tuberculose"])
    with col3:
        populacao_risco = st.selectbox(
            "43 - População de Risco*",
            [
                "1 - População Prisional",
                "2 - População em Situação de Rua",
                "3 - Internado/Institucionalizado",
                "4 - Profissional de Saúde/Sistema Penitenciário",
                "5 - HIV ou Outra Imunodepressão",
                "6 - Indígena",
                "7 - Imigrante",
                "8 - Usuário de Drogas",
                "9 - Diabético",
                "10 - Tabagista",
                "11 - Ignorado"
            ]
        )

    periodo_tratamento = st.text_input("42 - Período do Tratamento (ex: 2 Mês(es))")

    st.subheader("5. Exames e Amostra")
    pesquisa_solicitada = st.text_input("Pesquisas / Exames Solicitados*", value="BAAR / CULTURA PARA TUBERCULOSE")
    material_biologico = st.text_input("54 - Material Biológico*", value="ESCURRO")

    submitted = st.form_submit_button("Gerar PDF Oficial (GAL)")

# --- GERADOR DE PDF FIDELIZADO (REPORTLAB) ---
def gerar_pdf(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15,
        rightMargin=15,
        topMargin=15,
        bottomMargin=15
    )

    styles = getSampleStyleSheet()
    
    style_header_title = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=1,
        leading=11
    )
    style_header_sub = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        alignment=1,
        leading=10
    )
    style_field_title = ParagraphStyle(
        'FieldTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6,
        leading=7
    )
    style_field_val = ParagraphStyle(
        'FieldVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=9
    )

    def celula(num, titulo, valor=""):
        txt_num = f"<b>{num}</b> " if num else ""
        content = [Paragraph(f"{txt_num}{titulo}".upper(), style_field_title)]
        if valor:
            content.append(Paragraph(str(valor).upper(), style_field_val))
        return content

    elements = []

    # Cabeçalho Oficial
    header_data = [
        [
            Paragraph("República Federativa do Brasil<br/>Ministério da Saúde<br/><b>Sistema Gerenciador de Ambiente Laboratorial - GAL</b>", style_header_title),
            Paragraph("<b>Requisição de Exame - Tuberculose</b>", style_header_title),
            Paragraph("Nº Requisição:<br/><br/><b>[GERADO PELO SISTEMA]</b>", style_header_sub)
        ]
    ]
    t_header = Table(header_data, colWidths=[200, 220, 145])
    t_header.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 4))

    # Tabela Completa do Formulário
    table_data = [
        # Linha 1: Unidade de Saúde
        [
            celula("2", "Unidade de Saúde:", "SANTA TEREZINHA"),
            celula("3", "CNES:", "0025682"),
            celula("4", "Município de Atendimento:", "ARACAJU"),
            celula("5", "Código IBGE:", "280030"),
            celula("6", "UF:", "SE")
        ],
        # Linha 2: Profissional e Solicitação
        [
            celula("7", "CNS Profissional:", "706303772575170"),
            celula("8", "Nome do Profissional:", "MARCOS OLIVEIRA SUZUKI"),
            celula("9", "Conselho/Matrícula:", "2623"),
            celula("11", "Data Solicitação:", dados['data_solicitacao']),
            celula("12", "Finalidade:", dados['finalidade_req_num'])
        ],
        # Linha 3: Cabeçalho Paciente
        [Paragraph("<b>PACIENTE</b>", style_header_title), "", "", "", ""],
        # Linha 4: Paciente Dados Basicos
        [
            celula("14", "CNS do Paciente:", dados['cns_paciente']),
            celula("15", "Nome do Paciente:", dados['nome_paciente']),
            celula("16", "Data Nascimento:", dados['data_nascimento']),
            celula("17", "Idade:", f"{dados['idade_valor']} ({dados['complemento_idade_num']})"),
            celula("18", "Sexo:", dados['sexo_num'])
        ],
        # Linha 5: Raça / Mãe / Doc
        [
            celula("19", "Nacionalidade:", dados['nacionalidade']),
            celula("20", "Raça/Cor:", dados['raca_cor_num']),
            celula("21", "Etnia:", dados['etnia']),
            celula("22", "Nome da Mãe:", dados['nome_mae']),
            celula("23", "Doc 1 (CPF):", dados['cpf_paciente'])
        ],
        # Linha 6: Endereço
        [
            celula("25", "Logradouro:", dados['logradouro']),
            celula("26", "Número:", dados['numero']),
            celula("27", "Complemento:", dados['complemento_end']),
            celula("28", "Ponto de Referência:", dados['ponto_ref']),
            celula("29", "Bairro:", dados['bairro'])
        ],
        # Linha 7: Município / Contato
        [
            celula("30", "Município Residência:", dados['municipio_res']),
            celula("31", "Código IBGE:", "280030"),
            celula("32", "UF:", dados['uf_res']),
            celula("33", "CEP:", dados['cep']),
            celula("34", "DDD/Telefone:", dados['telefone'])
        ],
        # Linha 8: Cabeçalho Clínico
        [Paragraph("<b>INFORMAÇÕES CLÍNICAS / AGRAVO</b>", style_header_title), "", "", "", ""],
        # Linha 9: Clinica
        [
            celula("37", "Agravo/Doença:", "TUBERCULOSE"),
            celula("40", "Finalidade Exame:", dados['finalidade_exame_num']),
            celula("41", "Tratamento:", dados['tratamento_num']),
            celula("42", "Período Tratamento:", dados['periodo_tratamento']),
            celula("43", "População Risco:", dados['populacao_risco_num'])
        ],
        # Linha 10: Exame e Amostra
        [
            celula("", "Pesquisa(s) / Exame(s) Solicitado(s):", dados['pesquisa_solicitada']),
            "", "",
            celula("54", "Material Biológico:", dados['material_biologico']),
            ""
        ]
    ]

    # Dimensões das colunas (Soma = 565 pt, largura exata da página A4 útil)
    col_widths = [113, 113, 113, 113, 113]
    t_form = Table(table_data, colWidths=col_widths)

    t_form.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (0,2), (4,2)),  # Banner Paciente
        ('SPAN', (0,7), (4,7)),  # Banner Clínico
        ('SPAN', (0,9), (2,9)),  # Pesquisa Solicitada ocupa 3 colunas
        ('SPAN', (3,9), (4,9)),  # Material Biológico ocupa 2 colunas
        ('BACKGROUND', (0,2), (4,2), colors.HexColor("#EAEAEA")),
        ('BACKGROUND', (0,7), (4,7), colors.HexColor("#EAEAEA")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))

    elements.append(t_form)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- PROCESSAMENTO DO ENVIO ---
if submitted:
    # Extração apenas dos códigos numéricos exigidos pela ficha
    dados_processados = {
        'data_solicitacao': data_solicitacao.strftime("%d/%m/%Y"),
        'finalidade_req_num': finalidade_req.split(" - ")[0],
        'cns_paciente': cns_paciente,
        'nome_paciente': nome_paciente,
        'data_nascimento': data_nascimento.strftime("%d/%m/%Y"),
        'idade_valor': idade_valor,
        'complemento_idade_num': complemento_idade.split(" - ")[0],
        'sexo_num': sexo.split(" - ")[0],
        'raca_cor_num': raca_cor.split(" - ")[0],
        'etnia': etnia,
        'nome_mae': nome_mae,
        'cpf_paciente': cpf_paciente,
        'logradouro': logradouro,
        'numero': numero,
        'complemento_end': complemento_end,
        'ponto_ref': ponto_ref,
        'bairro': bairro,
        'municipio_res': municipio_res,
        'uf_res': uf_res,
        'cep': cep,
        'telefone': telefone,
        'finalidade_exame_num': finalidade_exame.split(" - ")[0],
        'tratamento_num': tratamento.split(" - ")[0],
        'periodo_tratamento': periodo_tratamento,
        'populacao_risco_num': populacao_risco.split(" - ")[0],
        'pesquisa_solicitada': pesquisa_solicitada,
        'material_biologico': material_biologico,
    }

    pdf_buffer = gerar_pdf(dados_processados)

    st.success("Requisicão gerada com sucesso!")
    st.download_button(
        label="📄 Baixar Requisição GAL (PDF)",
        data=pdf_buffer,
        file_name=f"Requisicao_GAL_{nome_paciente.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
