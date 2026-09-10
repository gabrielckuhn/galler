import io
import os
import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter # O GAL original geralmente está no formato Letter/A4

st.set_page_config(page_title="Preenchedor GAL - Tuberculose", layout="wide")

st.title("Sistema GAL - Preenchimento sobre PDF Original")
st.write("Preencha o formulário abaixo para sobrepor as informações na ficha oficial do GAL.")

# Verifica se o arquivo PDF de referência existe na pasta
PDF_MODELO_PATH = "GAL_TUBERCULOSE.pdf"

if not os.path.exists(PDF_MODELO_PATH):
    st.error(f"Arquivo '{PDF_MODELO_PATH}' não encontrado na raiz do projeto! Adicione o PDF ao repositório.")
    st.stop()

# --- FORMULÁRIO DO STREAMLIT ---
with st.form("form_gal"):
    
    st.subheader("1. Dados da Solicitação")
    col1, col2 = st.columns([1, 2])
    with col1:
        data_solicitacao = st.date_input("11 - Data de Solicitação*", format="DD/MM/YYYY")
    with col2:
        finalidade_req = st.selectbox(
            "12 - Finalidade*",
            ["1 - Campanha", "2 - Inquérito", "3 - Investigação", "4 - Programa", "5 - Protocolo", "6 - Projeto", "9 - Ignorado"]
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
        complemento_idade = st.selectbox("Complemento de Idade", ["4 - Ano(s)", "3 - Mês(es)", "2 - Dia(s)", "1 - Hora(s)"])
    with col3:
        sexo = st.radio("18 - Sexo*", ["M - Masculino", "F - Feminino", "1 - Ignorado"])
    with col4:
        raca_cor = st.selectbox("20 - Raça/Cor", ["1 - Branca", "2 - Preta", "3 - Parda", "4 - Amarela", "5 - Indígena", "99 - Sem Informação"])

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
        uf_res = st.selectbox("32 - UF*", ["SE", "AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SP", "RJ", "MG", "ES", "PR", "SC", "RS", "MS", "MT", "GO", "DF", "AM", "PA", "AC", "RO", "RR", "AP", "TO"])
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
            ["1 - População Prisional", "2 - População em Situação de Rua", "3 - Internado/Institucionalizado", "4 - Profissional de Saúde/Sistema Penitenciário", "5 - HIV ou Outra Imunodepressão", "6 - Indígena", "7 - Imigrante", "8 - Usuário de Drogas", "9 - Diabético", "10 - Tabagista", "11 - Ignorado"]
        )

    periodo_tratamento = st.text_input("42 - Período do Tratamento (ex: 2 Mês(es))")

    st.subheader("5. Exames e Amostra")
    pesquisa_solicitada = st.text_input("Pesquisas / Exames Solicitados*", value="BAAR / CULTURA PARA TUBERCULOSE")
    material_biologico = st.text_input("54 - Material Biológico*", value="ESCARRO")

    submitted = st.form_submit_button("Gerar PDF Preenchido")


# --- FUNÇÃO DE SOBREPOSIÇÃO NO PDF ORIGINAL ---
def preencher_pdf_original(dados):
    # 1. Cria a camada transparente com o ReportLab contendo os textos
    packet = io.BytesIO()
    # Usando o tamanho do PDF padrão
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 8)

    # Função auxiliar para desenhar o texto numa posição X, Y (em pontos)
    def escrever(texto, x, y):
        if texto:
            can.drawString(x, y, str(texto).upper())

    # COORDENADAS (X, Y) DAS CAIXAS DO GAL
    # Observação: O ponto (0,0) é o canto inferior esquerdo da página.
    
    # 1. Solicitação
    escrever(dados['data_solicitacao'], 430, 688) # Campo 11
    escrever(dados['finalidade_req_num'], 520, 688) # Campo 12

    # 2. Paciente
    escrever(dados['cns_paciente'], 35, 625)       # Campo 14
    escrever(dados['nome_paciente'], 200, 625)     # Campo 15
    escrever(dados['data_nascimento'], 430, 625)   # Campo 16
    escrever(f"{dados['idade_valor']} {dados['complemento_idade_num']}", 510, 625) # Campo 17

    escrever(dados['nacionalidade'], 35, 590)      # Campo 19
    escrever(dados['raca_cor_num'], 170, 590)       # Campo 20
    escrever(dados['etnia'], 230, 590)              # Campo 21
    escrever(dados['nome_mae'], 300, 590)           # Campo 22
    escrever(f"CPF: {dados['cpf_paciente']}", 470, 590) # Campo 23

    # Endereço
    escrever(dados['logradouro'], 35, 555)         # Campo 25
    escrever(dados['numero'], 350, 555)             # Campo 26
    escrever(dados['complemento_end'], 420, 555)    # Campo 27
    escrever(dados['bairro'], 35, 525)              # Campo 29
    escrever(dados['municipio_res'], 200, 525)      # Campo 30
    escrever(dados['uf_res'], 430, 525)             # Campo 32
    escrever(dados['cep'], 470, 525)                # Campo 33
    escrever(dados['telefone'], 530, 525)           # Campo 34

    # Clinica
    escrever(dados['finalidade_exame_num'], 140, 460)  # Campo 40
    escrever(dados['tratamento_num'], 230, 460)        # Campo 41
    escrever(dados['periodo_tratamento'], 370, 460)    # Campo 42
    escrever(dados['populacao_risco_num'], 470, 460)   # Campo 43

    # Exames e Material
    escrever(dados['pesquisa_solicitada'], 35, 330)    # Exames Solicitados
    escrever(dados['material_biologico'], 35, 290)     # Campo 54

    can.save()
    packet.seek(0)

    # 2. Mescla o texto gerado com a primeira página do PDF Original
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(PDF_MODELO_PATH)
    output = PdfWriter()

    # Pega a primeira página do PDF original
    page = existing_pdf.pages[0]
    # Sobrepõe o texto por cima
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # Se o PDF original tiver 2 páginas (as instruções), mantém a 2ª página intacta
    if len(existing_pdf.pages) > 1:
        output.add_page(existing_pdf.pages[1])

    # 3. Retorna o buffer final do PDF mesclado
    output_stream = io.BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    return output_stream


# --- PROCESSAMENTO DO ENVIO ---
if submitted:
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

    pdf_preenchido = preencher_pdf_original(dados_processados)

    st.success("PDF da GAL preenchido com sucesso por cima do modelo original!")
    st.download_button(
        label="📄 Baixar Ficha GAL Preenchida (PDF)",
        data=pdf_preenchido,
        file_name=f"GAL_Preenchido_{nome_paciente.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
