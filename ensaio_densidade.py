import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Densidade In Situ - Metrosul", page_icon="🛣️")

# --- FUNÇÃO DE AJUSTE AUTOMÁTICO (KG para G) ---
def ajustar_peso(valor):
    if 0 < valor < 30:
        return valor * 1000
    return valor

# --- GERADOR DE PDF PADRÃO AEGEA ---
def gerar_pdf_ensaio(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "RELATORIO DE ENSAIO - DENSIDADE IN SITU", ln=True, align='C')
    pdf.set_font("Arial", "", 9)
    pdf.cell(190, 5, "Padrao Aegea / Corsan", ln=True, align='C')
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

    # Dados conforme a foto enviada
    criar_tabela("UMIDADE", [
        ("A - Massa da capsula", f"{d['u_a']:.1f} g"),
        ("B - Peso do solo umido + capsula", f"{d['u_b']:.1f} g"),
        ("C - Peso do solo seco + capsula", f"{d['u_c']:.1f} g"),
        ("D - Peso solo umido (B - A)", f"{d['u_d']:.1f} g"),
        ("E - Peso solo seco (C - A)", f"{d['u_e']:.1f} g"),
        ("F - Peso agua (D - E)", f"{d['u_f']:.1f} g"),
        ("G - Teor de umidade - w (%)", f"{d['u_g']:.2f} %")
    ])

    criar_tabela("DENSIDADE", [
        ("A - Massa inicial (aparelho + areia)", f"{d['d_a']:.1f} g"),
        ("B - Massa final (aparelho + areia)", f"{d['d_b']:.1f} g"),
        ("C - Peso da areia consumida (A - B)", f"{d['d_c']:.1f} g"),
        ("D - Massa cone", f"{d['d_d']:.1f} g"),
        ("E - Massa buraco (C - D)", f"{d['d_e']:.1f} g"),
        ("F - Densidade da areia (g/cm3)", f"{d['d_f']:.3f}"),
        ("G - Volume buraco (E / F)", f"{d['d_g']:.1f} cm3"),
        ("H - Massa da amostra (Solo Umido)", f"{d['d_h']:.1f} g"),
        ("I - Massa especifica umida (H / G)", f"{d['d_i']:.3f} g/cm3"),
        ("J - Massa especifica seca (I / (1 + w))", f"{d['d_j']:.3f} g/cm3")
    ])

    # Resultado Final
    pdf.set_font("Arial", "B", 12)
    cor = (0, 100, 0) if d['gc'] >= 95 else (200, 0, 0)
    pdf.set_text_color(*cor)
    pdf.cell(190, 12, f"GRAU DE COMPACTACAO: {d['gc']:.1f} %", border=1, ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE ---
st.title("🧪 Ensaio Densidade In Situ")

with st.expander("💧 Passo 1: Umidade", expanded=True):
    u_a = st.number_input("A - Massa da cápsula", value=100.0)
    u_b = ajustar_peso(st.number_input("B - Peso solo úmido + cápsula"))
    u_c = ajustar_peso(st.number_input("C - Peso solo seco + cápsula"))
    
    u_d = u_b - u_a
    u_e = u_c - u_a
    u_f = u_d - u_e
    u_g = (u_f / u_e) * 100 if u_e > 0 else 0.0
    st.write(f"**G - Teor de Umidade: {u_g:.2f}%**")

with st.expander("⚖️ Passo 2: Densidade", expanded=True):
    col1, col2 = st.columns(2)
    d_a = ajustar_peso(col1.number_input("A - Massa Inicial (Aparelho+Areia)"))
    d_b = ajustar_peso(col2.number_input("B - Massa Final (Aparelho+Areia)"))
    d_d = st.number_input("D - Massa do Cone (Fixo)", value=1540.0)
    d_f = st.number_input("F - Densidade da Areia (Calibrada)", value=1.450, format="%.3f")
    d_h = ajustar_peso(st.number_input("H - Massa da Amostra (Solo Úmido do Buraco)"))

    d_c = d_a - d_b
    d_e = d_c - d_d
    d_g = d_e / d_f if d_f > 0 else 0
    d_i = d_h / d_g if d_g > 0 else 0
    d_j = d_i / (1 + (u_g / 100))
    st.write(f"**J - Massa Específica Seca: {d_j:.3f} g/cm³**")

with st.expander("📈 Passo 3: Compactação", expanded=True):
    proctor = st.number_input("Densidade Ótima (Proctor)", value=2.050, format="%.3f")
    gc = (d_j / proctor) * 100 if proctor > 0 else 0
    st.metric("Grau de Compactação", f"{gc:.1f}%")

if gc > 0:
    dados = {
        'u_a': u_a, 'u_b': u_b, 'u_c': u_c, 'u_d': u_d, 'u_e': u_e, 'u_f': u_f, 'u_g': u_g,
        'd_a': d_a, 'd_b': d_b, 'd_c': d_c, 'd_d': d_d, 'd_e': d_e, 'd_f': d_f, 'd_g': d_g, 'd_h': d_h, 'd_i': d_i, 'd_j': d_j,
        'gc': gc
    }
    pdf = gerar_pdf_ensaio(dados)
    st.download_button("📥 Gerar Relatório Completo", pdf, "Ensaio_Densidade.pdf", "application/pdf", use_container_width=True)
