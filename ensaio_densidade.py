import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Densidade In Situ - Metrosul", page_icon="🛣️")

# --- FUNÇÃO DE AJUSTE AUTOMÁTICO (KG para G) ---
def ajustar_peso(valor):
    if 0 < valor < 35: # Margem para balanças de até 30kg
        return valor * 1000
    return valor

# --- GERADOR DE PDF PADRÃO AEGEA / CORSAN ---
def gerar_pdf_ensaio(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "RELATORIO DE ENSAIO - DENSIDADE IN SITU", ln=True, align='C')
    pdf.set_font("Arial", "", 9)
    pdf.cell(190, 5, "Padrao Operacional - Ambiental Metrosul", ln=True, align='C')
    pdf.ln(5)

    def criar_tabela(titulo, linhas):
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, f" {titulo}", border=1, ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        for desc, valor in linhas:
            pdf.cell(140, 8, f" {desc}", border=1)
            pdf.cell(50, 8, f" {valor}", border=1, ln=True, align='C')
        pdf.ln(3)

    # Tabela de Umidade (A-G)
    criar_tabela("DETERMINACAO DA UMIDADE", [
        ("A - Tara do recipiente (Bandeja/Capsula)", f"{d['u_a']:.1f} g"),
        ("B - Peso do solo umido + recipiente", f"{d['u_b']:.1f} g"),
        ("C - Peso do solo seco + recipiente", f"{d['u_c']:.1f} g"),
        ("D - Peso solo umido (B - A)", f"{d['u_d']:.1f} g"),
        ("E - Peso solo seco (C - A)", f"{d['u_e']:.1f} g"),
        ("F - Peso agua (D - E)", f"{d['u_f']:.1f} g"),
        ("G - Teor de umidade - w (%)", f"{d['u_g']:.2f} %")
    ])

    # Tabela de Densidade (A-J)
    criar_tabela("DETERMINACAO DA DENSIDADE IN SITU", [
        ("A - Massa inicial (aparelho + areia)", f"{d['d_a']:.1f} g"),
        ("B - Massa final (aparelho + areia)", f"{d['d_b']:.1f} g"),
        ("C - Peso da areia consumida (A - B)", f"{d['d_c']:.1f} g"),
        ("D - Massa areia no cone (Fixo)", f"{d['d_d']:.1f} g"),
        ("E - Massa areia no buraco (C - D)", f"{d['d_e']:.1f} g"),
        ("F - Densidade da areia (g/cm3)", f"{d['d_f']:.3f}"),
        ("G - Volume do buraco (E / F)", f"{d['d_g']:.1f} cm3"),
        ("H - Massa solo umido (Solo + Bandeja - Tara)", f"{d['d_h']:.1f} g"),
        ("I - Massa especifica umida (H / G)", f"{d['d_i']:.3f} g/cm3"),
        ("J - Massa especifica seca (I / (1 + w))", f"{d['d_j']:.3f} g/cm3")
    ])

    pdf.set_font("Arial", "B", 12)
    cor = (0, 100, 0) if d['gc'] >= 95 else (200, 0, 0)
    pdf.set_text_color(*cor)
    pdf.cell(190, 12, f"GRAU DE COMPACTACAO FINAL: {d['gc']:.1f} %", border=1, ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE STREAMLIT ---
st.title("🧪 Ensaio Densidade In Situ")

# PASSO 1: UMIDADE
st.header("1. Determinação da Umidade")
u_col1, u_col2 = st.columns(2)
u_a = u_col1.number_input("A - Tara da Bandeja/Cápsula (g)", value=100.0)
u_b_raw = u_col2.number_input("B - Peso Solo Úmido + Bandeja (g)")
u_c_raw = st.number_input("C - Peso Solo Seco + Bandeja (g)")

u_b = ajustar_peso(u_b_raw)
u_c = ajustar_peso(u_c_raw)

u_d = u_b - u_a
u_e = u_c - u_a
u_f = u_d - u_e
u_g = (u_f / u_e) * 100 if u_e > 0 else 0.0
st.info(f"Umidade Calculada (G): {u_g:.2f}%")

st.divider()

# PASSO 2: DENSIDADE
st.header("2. Determinação da Densidade")
d_col1, d_col2 = st.columns(2)
d_a_raw = d_col1.number_input("A - Massa Inicial (Aparelho+Areia)")
d_b_raw = d_col2.number_input("B - Massa Final (Aparelho+Areia)")
d_d = st.number_input("D - Massa Areia no Cone (g)", value=1540.0)
d_f = st.number_input("F - Densidade da Areia (g/cm³)", value=1.450, format="%.3f")

st.subheader("📦 Solo do Buraco")
d_h_total_raw = st.number_input("H1 - Peso Solo Úmido + Bandeja (g)")
d_h_tara = st.number_input("H2 - Tara da Bandeja do Buraco (g)", value=500.0)

# Cálculos da Densidade
d_a, d_b = ajustar_peso(d_a_raw), ajustar_peso(d_b_raw)
d_h_total = ajustar_peso(d_h_total_raw)
d_h = d_h_total - d_h_tara # Massa líquida da amostra

d_c = d_a - d_b
d_e = d_c - d_d
d_g = d_e / d_f if d_f > 0 else 0
d_i = d_h / d_g if d_g > 0 else 0
d_j = d_i / (1 + (u_g / 100))

st.info(f"Massa Específica Seca (J): {d_j:.3f} g/cm³")

st.divider()

# PASSO 3: CONCLUSÃO
st.header("3. Grau de Compactação")
proctor = st.number_input("Massa Específica Seca Máxima (Proctor)", value=2.050, format="%.3f")
gc = (d_j / proctor) * 100 if proctor > 0 else 0

st.metric("Grau de Compactação (G.C.)", f"{gc:.1f}%")

if gc > 0:
    dados_finais = {
        'u_a': u_a, 'u_b': u_b, 'u_c': u_c, 'u_d': u_d, 'u_e': u_e, 'u_f': u_f, 'u_g': u_g,
        'd_a': d_a, 'd_b': d_b, 'd_c': d_c, 'd_d': d_d, 'd_e': d_e, 'd_f': d_f, 'd_g': d_g, 'd_h': d_h, 'd_i': d_i, 'd_j': d_j,
        'gc': gc
    }
    pdf_bytes = gerar_pdf_ensaio(dados_finais)
    st.download_button("📥 Baixar Relatório In Situ", pdf_bytes, f"Ensaio_InSitu_{datetime.now().day}.pdf", "application/pdf", use_container_width=True)
