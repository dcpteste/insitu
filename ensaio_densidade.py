import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="Densidade In Situ - Metrosul", page_icon="🧪")

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
        ("G - Volume do buraco (E / F) (cm3)", f"{d['d_g']:.1f}"),
        ("H - Massa solo umido (Liquido) (g)", f"{d['d_h']:.3f}"),
        ("I - Massa especifica umida (H / G) (g/cm3)", f"{d['d_i']:.3f}"),
        ("J - Massa especifica seca (I / (1 + w)) (g/cm3)", f"{d['d_j']:.3f}")
    ])

    pdf.set_font("Arial", "B", 12)
    cor = (0, 100, 0) if d['gc'] >= 95 else (200, 0, 0)
    pdf.set_text_color(*cor)
    pdf.cell(190, 12, f"GRAU DE COMPACTACAO FINAL: {d['gc']:.1f} %", border=1, ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE ---
st.title("🧪 Controle de Compactação")

# 1. UMIDADE
with st.expander("💧 1. Determinação da Umidade", expanded=True):
    u_c1, u_c2 = st.columns(2)
    u_a = u_c1.number_input("A - Tara da Bandeja (g)", format="%.3f", step=0.001)
    u_b_in = u_c2.number_input("B - Solo Úmido + Bandeja (g)", format="%.3f", step=0.001)
    u_c_in = st.number_input("C - Solo Seco + Bandeja (g)", format="%.3f", step=0.001)
    
    u_
