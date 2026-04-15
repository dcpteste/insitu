import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Densidade In Situ - Metrosul", page_icon="🛣️")

# --- AJUSTE DE PESO (KG PARA G) ---
def ajustar_peso(valor):
    if 0 < valor < 35: 
        return round(valor * 1000, 3)
    return round(valor, 3)

# --- GERADOR DE PDF ---
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
            pdf.cell(50, 8, f" {valor}", border=1, ln=True, align='R')
        pdf.ln(3)

    criar_tabela("DETERMINACAO DA UMIDADE", [
        ("A - Tara do recipiente (g)", f"{d['u_a']:.3f} g"),
        ("B - Peso do solo umido + recipiente (g)", f"{d['u_b']:.3f} g"),
        ("C - Peso do solo seco + recipiente (g)", f"{d['u_c']:.3f} g"),
        ("D - Peso solo umido (B - A) (g)", f"{d['u_d']:.3f} g"),
        ("E - Peso solo seco (C - A) (g)", f"{d['u_e']:.3f} g"),
        ("F - Peso agua (D - E) (g)", f"{d['u_f']:.3f} g"),
        ("G - Teor de umidade - w (%)", f"{d['u_g']:.2f} %")
    ])

    criar_tabela("DETERMINACAO DA DENSIDADE IN SITU", [
        ("A - Massa inicial (aparelho + areia) (g)", f"{d['d_a']:.3f} g"),
        ("B - Massa final (aparelho + areia) (g)", f"{d['d_b']:.3f} g"),
        ("C - Peso da areia consumida (A - B) (g)", f"{d['d_c']:.3f} g"),
        ("D - Massa areia no cone (g)", f"{d['d_d']:.3f} g"),
        ("E - Massa areia no buraco (C - D) (g)", f"{d['d_e']:.3f} g"),
        ("F - Densidade da areia (g/cm3)", f"{d['d_f']:.3f}"),
        ("G - Volume do buraco (E / F) (cm3)", f"{d['d_g']:.1f}"),
        ("H - Massa solo umido (Liquido) (g)", f"{d['d_h']:.3f} g"),
        ("I - Massa especifica umida (H / G) (g/cm3)", f"{d['d_i']:.3f}"),
        ("J - Massa especifica seca (I / (1 + w)) (g/cm3)", f"{d['d_j']:.3f}")
    ])

    pdf.set_font("Arial", "B", 12)
    cor = (0, 100, 0) if d['gc'] >= 95 else (200, 0, 0)
    pdf.set_text_color(*cor)
    pdf.cell(190, 12, f"GRAU DE COMPACTACAO FINAL: {d['gc']:.1f} %", border=1, ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE ---
st.title("🧪 Densidade In Situ (Padrão Balança)")

# SEÇÃO 1: UMIDADE
with st.expander("💧 1. Umidade", expanded=True):
    col1, col2 = st.columns(2)
    u_a = col1.number_input("A - Tara (g)", format="%.3f", step=0.001, value=0.250)
    u_b_in = col2.number_input("B - Solo Úmido + Recipiente (g)", format="%.3f", step=0.001)
    u_c_in = st.number_input("C - Solo Seco + Recipiente (g)", format="%.3f", step=0.001)
    
    u_b, u_c = ajustar_peso(u_b_in), ajustar_peso(u_c_in)
    u_d = round(u_b - u_a, 3)
    u_e = round(u_c - u_a, 3)
    u_f = round(u_d - u_e, 3)
    u_g = round((u_f / u_e) * 100, 2) if u_e > 0 else 0.0
    st.info(f"Umidade (G): {u_g}%")

# SEÇÃO 2: DENSIDADE
with st.expander("⚖️ 2. Densidade", expanded=True):
    d1, d2 = st.columns(2)
    d_a_in = d1.number_input("A - Massa Inicial (Aparelho+Areia)", format="%.3f", step=0.001)
    d_b_in = d2.number_input("B - Massa Final (Aparelho+Areia)", format="%.3f", step=0.001)
    d_d = st.number_input("D - Massa Areia no Cone (g)", format="%.3f", step=0.001, value=1540.000)
    d_f = st.number_input("F - Densidade da Areia (g/cm³)", format="%.3f", step=0.001, value=1.410)
    d_h_in = st.number_input("H - Massa Solo Úmido do Buraco (g)", format="%.3f", step=0.001)

    d_a, d_b, d_h = ajustar_peso(d_a_in), ajustar_peso(d_b_in), ajustar_peso(d_h_in)
    
    d_c = round(d_a - d_b, 3)
    d_e = round(d_c - d_d, 3)
    d_g = round(d_e / d_f, 1) if d_f > 0 else 0
    d_i = round(d_h / d_g, 3) if d_g > 0 else 0
    d_j = round(d_i / (1 + (u_g / 100)), 3)
    
    st.info(f"Densidade Seca (J): {d_j}")

# SEÇÃO 3: RESULTADO
proctor = st.number_input("Densidade Máxima (Proctor)", format="%.3f", step=0.001, value=2.050)
gc = round((d_j / proctor) * 100, 1) if proctor > 0 else 0
st.metric("Grau de Compactação", f"{gc}%")

if gc > 0:
    dados = {'u_a':u_a, 'u_b':u_b, 'u_c':u_c, 'u_d':u_d, 'u_e':u_e, 'u_f':u_f, 'u_g':u_g,
             'd_a':d_a, 'd_b':d_b, 'd_c':d_c, 'd_d':d_d, 'd_e':d_e, 'd_f':d_f, 'd_g':d_g, 'd_h':d_h, 'd_i':d_i, 'd_j':d_j, 'gc':gc}
    pdf_b = gerar_pdf_ensaio(dados)
    st.download_button("📩 Baixar Relatório", pdf_b, "Relatorio_Densidade.pdf", "application/pdf", use_container_width=True)
