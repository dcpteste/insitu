import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="Densidade In Situ - Metrosul", page_icon="🧪")

# --- GERADOR DE PDF ---
def gerar_pdf_ensaio(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "RELATORIO DE ENSAIO - FRASCO DE AREIA", ln=True, align='C')
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

    criar_tabela("1. DETERMINACAO DA UMIDADE", [
        ("A - Tara do recipiente (g)", f"{d['u_a']:.3f}"),
        ("B - Peso do solo umido + recipiente (g)", f"{d['u_b']:.3f}"),
        ("C - Peso do solo seco + recipiente (g)", f"{d['u_c']:.3f}"),
        ("D - Peso solo umido (B - A) (g)", f"{d['u_d']:.3f}"),
        ("E - Peso solo seco (C - A) (g)", f"{d['u_e']:.3f}"),
        ("F - Peso agua (D - E) (g)", f"{d['u_f']:.3f}"),
        ("G - Teor de umidade - w (%)", f"{d['u_g']:.2f} %")
    ])

    criar_tabela("2. DETERMINACAO DA DENSIDADE IN SITU", [
        ("A - Massa inicial (aparelho + areia) (g)", f"{d['d_a']:.3f}"),
        ("B - Massa final (aparelho + areia) (g)", f"{d['d_b']:.3f}"),
        ("C - Peso da areia consumida (A - B) (g)", f"{d['d_c']:.3f}"),
        ("D - Massa areia no cone (g)", f"{d['d_d']:.3f}"),
        ("E - Massa areia no buraco (C - D) (g)", f"{d['d_e']:.3f}"),
        ("F - Densidade da areia (g/cm3)", f"{d['d_f']:.3f}"),
        ("G - Volume do buraco (E / F) (cm3)", f"{d['d_g']:.4f}"),
        ("H - Massa solo umido + bandeja (g)", f"{d['d_h_total']:.3f}"),
        ("I - Tara da bandeja da cava (g)", f"{d['d_h_tara']:.3f}"),
        ("J - Massa especifica seca (g/cm3)", f"{d['d_j']:.3f}")
    ])

    pdf.set_font("Arial", "B", 12)
    cor = (0, 100, 0) if d['gc'] >= 95 else (200, 0, 0)
    pdf.set_text_color(*cor)
    pdf.cell(190, 12, f"GRAU DE COMPACTACAO FINAL: {d['gc']:.1f} %", border=1, ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE ---
st.title("🧪 Painel de Controle - Metrosul")

# 1. UMIDADE
with st.expander("💧 1. Determinação da Umidade", expanded=True):
    col1, col2 = st.columns(2)
    u_a = col1.number_input("A - Tara da Bandeja Pequena (g)", format="%.3f", step=0.001, key="t_u")
    u_b = col2.number_input("B - Solo Úmido + Bandeja (g)", format="%.3f", step=0.001, key="s_u")
    u_c = st.number_input("C - Solo Seco + Bandeja (g)", format="%.3f", step=0.001, key="s_s")
    
    # Cálculos de Umidade
    u_d = u_b - u_a
    u_e = u_c - u_a
    u_f = u_d - u_e
    u_g = (u_f / u_e) * 100 if u_e > 0 else 0.0
    
    st.write("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Solo Úmido (D)", f"{u_d:.3f}")
    res2.metric("Solo Seco (E)", f"{u_e:.3f}")
    res3.metric("Peso Água (F)", f"{u_f:.3f}")
    st.info(f"**Teor de Umidade (w): {u_g:.2f}%**")

# 2. DENSIDADE
with st.expander("⚖️ 2. Densidade In Situ", expanded=True):
    col_d1, col_d2 = st.columns(2)
    d_a = col_d1.number_input("A - Massa Inicial (Frasco+Areia) (g)", format="%.3f", step=0.001)
    d_b = col_d2.number_input("B - Massa Final (Frasco+Areia) (g)", format="%.3f", step=0.001)
    
    col_d3, col_d4 = st.columns(2)
    d_d = col_d3.number_input("D - Massa Areia no Cone (g)", format="%.3f", step=0.001, value=0.533)
    d_f = col_d4.number_input("F - Densidade da Areia (g/cm³)", format="%.3f", step=0.001, value=1.422)
    
    d_h_total = st.number_input("H - Massa Solo Úmido + Bandeja da Cava (g)", format="%.3f", step=0.001)
    d_h_tara = st.number_input("Tara da Bandeja da Cava (g)", format="%.3f", step=0.001, value=0.240, key="t_c")
    
    # Cálculos de Densidade - PRECISÃO TOTAL
    d_h_liquido = d_h_total - d_h_tara
    d_c = d_a - d_b
    d_e = d_c - d_d
    d_g = d_e / d_f if d_f > 0 else 0.0 # Volume sem arredondar
    
    d_i = d_h_liquido / d_g if d_g > 0 else 0.0
    d_j = d_i / (1 + (u_g / 100)) if u_e > 0 else 0.0
    
    st.write("---")
    rd1, rd2, rd3 = st.columns(3)
    rd1.metric("Areia Buraco (E)", f"{d_e:.3f}")
    rd2.metric("Volume (G)", f"{d_g:.4f}")
    rd3.metric("Solo Líquido", f"{d_h_liquido:.3f}")
    st.success(f"**Massa Seca de Campo (J): {d_j:.3f} g/cm³**")

# 3. GRAU DE COMPACTAÇÃO
st.divider()
proctor = st.number_input("Proctor Máximo Lab (g/cm³)", format="%.3f", step=0.001, value=1.785)
gc = (d_j / proctor) * 100 if proctor > 0 else 0.0

st.metric("GRAU DE COMPACTAÇÃO", f"{gc:.1f}%")

if gc > 0:
    dados_pdf = {
        'u_a':u_a, 'u_b':u_b, 'u_c':u_c, 'u_d':u_d, 'u_e':u_e, 'u_f':u_f, 'u_g':u_g,
        'd_a':d_a, 'd_b':d_b, 'd_c':d_c, 'd_d':d_d, 'd_e':d_e, 'd_f':d_f, 'd_g':d_g, 
        'd_h_total':d_h_total, 'd_h_tara':d_h_tara, 'd_i':d_i, 'd_j':d_j, 'gc':gc
    }
    pdf_output = gerar_pdf_ensaio(dados_pdf)
    st.download_button("📥 Baixar Relatório PDF", pdf_output, "Relatorio_Metrosul.pdf", "application/pdf", use_container_width=True)
