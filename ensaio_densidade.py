import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io
from typing import Dict

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Metrosul - Ensaio Frasco de Areia",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================== ESTILOS CSS PERSONALIZADOS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        font-weight: 500;
        color: #374151;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    .result-card {
        background-color: #F0F9FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #0EA5E9;
        margin: 1rem 0;
    }
    .warning-text {
        color: #DC2626;
        font-weight: 500;
    }
    .success-text {
        color: #059669;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES AUXILIARES ====================
def calcular_umidade(a: float, b: float, c: float) -> Dict:
    """Calcula o teor de umidade a partir dos pesos."""
    peso_umido = round(b - a, 3)
    peso_seco = round(c - a, 3)
    agua = round(peso_umido - peso_seco, 3)
    teor = round((agua / peso_seco) * 100, 2) if peso_seco > 0 else 0.0
    return {
        "peso_umido": peso_umido,
        "peso_seco": peso_seco,
        "agua": agua,
        "teor": teor
    }

def calcular_densidade(
    massa_inicial: float, massa_final: float, areia_cone: float,
    densidade_areia: float, solo_bandeja: float, tara_bandeja: float,
    teor_umidade: float
) -> Dict:
    """Calcula a densidade in situ e massa específica seca."""
    areia_consumida = round(massa_inicial - massa_final, 3)
    areia_buraco = round(areia_consumida - areia_cone, 3)
    volume_buraco = round(areia_buraco / densidade_areia, 1) if densidade_areia > 0 else 0.0
    solo_umido = round(solo_bandeja - tara_bandeja, 3)
    densidade_umida = round(solo_umido / volume_buraco, 3) if volume_buraco > 0 else 0.0
    densidade_seca = round(densidade_umida / (1 + (teor_umidade / 100)), 3) if teor_umidade > 0 else 0.0
    
    return {
        "areia_consumida": areia_consumida,
        "areia_buraco": areia_buraco,
        "volume_buraco": volume_buraco,
        "solo_umido": solo_umido,
        "densidade_umida": densidade_umida,
        "densidade_seca": densidade_seca
    }

def gerar_pdf(ensaio: Dict, proctor: float, gc: float) -> bytes:
    """Gera o relatório em PDF com formatação profissional."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(30, 58, 138)  # Azul escuro
    pdf.cell(190, 10, "RELATÓRIO DE ENSAIO - FRASCO DE AREIA", ln=True, align='C')
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(190, 5, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.cell(190, 5, "Padrão Operacional - Ambiental Metrosul", ln=True, align='C')
    pdf.ln(8)
    
    # Função para criar tabelas
    def criar_tabela(titulo, linhas):
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(240, 248, 255)
        pdf.cell(190, 8, f" {titulo}", border=1, ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        for desc, valor in linhas:
            pdf.cell(130, 7, f" {desc}", border=1)
            pdf.cell(60, 7, f" {valor}", border=1, ln=True, align='R')
        pdf.ln(4)
    
    # Umidade
    criar_tabela("1. DETERMINAÇÃO DA UMIDADE", [
        ("A - Tara do recipiente (g)", f"{ensaio['u_a']:.3f}"),
        ("B - Solo úmido + recipiente (g)", f"{ensaio['u_b']:.3f}"),
        ("C - Solo seco + recipiente (g)", f"{ensaio['u_c']:.3f}"),
        ("D - Peso solo úmido (g)", f"{ensaio['u_d']:.3f}"),
        ("E - Peso solo seco (g)", f"{ensaio['u_e']:.3f}"),
        ("F - Peso água (g)", f"{ensaio['u_f']:.3f}"),
        ("G - Teor de umidade - w (%)", f"{ensaio['u_g']:.2f} %")
    ])
    
    # Densidade
    criar_tabela("2. DETERMINAÇÃO DA DENSIDADE IN SITU", [
        ("A - Massa inicial (aparelho + areia) (g)", f"{ensaio['d_a']:.3f}"),
        ("B - Massa final (aparelho + areia) (g)", f"{ensaio['d_b']:.3f}"),
        ("C - Areia consumida (A - B) (g)", f"{ensaio['d_c']:.3f}"),
        ("D - Areia no cone (g)", f"{ensaio['d_d']:.3f}"),
        ("E - Areia no buraco (C - D) (g)", f"{ensaio['d_e']:.3f}"),
        ("F - Densidade da areia (g/cm³)", f"{ensaio['d_f']:.3f}"),
        ("G - Volume do buraco (E / F) (cm³)", f"{ensaio['d_g']:.1f}"),
        ("H - Solo úmido + bandeja (g)", f"{ensaio['d_h_total']:.3f}"),
        ("I - Tara da bandeja (g)", f"{ensaio['d_h_tara']:.3f}"),
        ("J - Massa específica úmida (g/cm³)", f"{ensaio['d_i']:.3f}"),
        ("K - Massa específica seca (g/cm³)", f"{ensaio['d_j']:.3f}")
    ])
    
    # Resultado final
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    cor = (0, 100, 0) if gc >= 95 else (200, 0, 0)
    pdf.set_text_color(*cor)
    pdf.cell(190, 10, f"GRAU DE COMPACTAÇÃO FINAL: {gc:.1f} %", border=1, ln=True, align='C')
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(190, 6, f"Proctor máximo de referência: {proctor:.3f} g/cm³", ln=True, align='C')
    
    # Rodapé
    pdf.ln(10)
    pdf.set_y(-20)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(190, 5, "Relatório gerado automaticamente pelo sistema Metrosul", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# ==================== INTERFACE PRINCIPAL ====================
st.markdown('<div class="main-header">🧪 Ensaio Frasco de Areia</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Metrosul - Controle de Compactação</div>', unsafe_allow_html=True)

# --- SEÇÃO 1: UMIDADE ---
with st.expander("📊 1. Determinação da Umidade", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        tara = st.number_input("Tara da bandeja (g)", format="%.3f", step=0.001, key="tara")
    with col2:
        solo_umido_bandeja = st.number_input("Solo úmido + bandeja (g)", format="%.3f", step=0.001, key="solo_umido")
    with col3:
        solo_seco_bandeja = st.number_input("Solo seco + bandeja (g)", format="%.3f", step=0.001, key="solo_seco")
    
    if tara > 0 and solo_umido_bandeja > 0 and solo_seco_bandeja > 0:
        umidade = calcular_umidade(tara, solo_umido_bandeja, solo_seco_bandeja)
        
        st.markdown("---")
        st.caption("🔍 Verificação dos cálculos")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Peso solo úmido (g)", f"{umidade['peso_umido']:.3f}")
        col_b.metric("Peso solo seco (g)", f"{umidade['peso_seco']:.3f}")
        col_c.metric("Peso água (g)", f"{umidade['agua']:.3f}")
        
        st.info(f"💧 **Teor de umidade (w) = {umidade['teor']:.2f}%**")
    else:
        st.warning("Preencha os três valores acima para calcular a umidade.")

# --- SEÇÃO 2: DENSIDADE ---
with st.expander("⚖️ 2. Determinação da Densidade In Situ", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        massa_inicial = st.number_input("Massa inicial (frasco+areia) (g)", format="%.3f", step=0.001, key="mi")
        areia_cone = st.number_input("Massa de areia no cone (g)", format="%.3f", step=0.001, value=1540.000, key="cone")
        solo_bandeja = st.number_input("Solo úmido + bandeja da cava (g)", format="%.3f", step=0.001, key="solo_cava")
    with col2:
        massa_final = st.number_input("Massa final (frasco+areia) (g)", format="%.3f", step=0.001, key="mf")
        densidade_areia = st.number_input("Densidade da areia (g/cm³)", format="%.3f", step=0.001, value=1.410, key="dens_areia")
        tara_bandeja = st.number_input("Tara da bandeja da cava (g)", format="%.3f", step=0.001, value=0.000, key="tara_cava")
    
    # Verifica se os dados da umidade já foram preenchidos
    if 'umidade' in locals() and umidade['teor'] > 0:
        teor_atual = umidade['teor']
        st.success(f"Teor de umidade utilizado: **{teor_atual:.2f}%**")
    else:
        teor_atual = 0.0
        st.error("⚠️ Preencha primeiro a seção de Umidade com valores válidos.")
    
    # Cálculo da densidade (somente se os campos principais existirem)
    if all([massa_inicial, massa_final, areia_cone, densidade_areia, solo_bandeja, teor_atual > 0]):
        densidade = calcular_densidade(
            massa_inicial, massa_final, areia_cone, densidade_areia,
            solo_bandeja, tara_bandeja, teor_atual
        )
        
        st.markdown("---")
        st.caption("🔍 Verificação dos cálculos")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Areia no buraco (g)", f"{densidade['areia_buraco']:.3f}")
        col_b.metric("Volume do buraco (cm³)", f"{densidade['volume_buraco']:.1f}")
        col_c.metric("Solo úmido da cava (g)", f"{densidade['solo_umido']:.3f}")
        
        st.success(f"🏔️ **Massa específica seca (ρd) = {densidade['densidade_seca']:.3f} g/cm³**")
    else:
        densidade = None
        st.warning("Preencha todos os campos da densidade e certifique-se de que a umidade foi calculada.")

# --- SEÇÃO 3: RESULTADO FINAL ---
st.divider()
st.markdown('<div class="sub-header">📋 Resultado da Compactação</div>', unsafe_allow_html=True)

col_ref, col_gc = st.columns(2)
with col_ref:
    proctor_max = st.number_input("Proctor máximo de referência (g/cm³)", format="%.3f", step=0.001, value=2.050)

if densidade and densidade['densidade_seca'] > 0 and proctor_max > 0:
    gc = round((densidade['densidade_seca'] / proctor_max) * 100, 1)
    with col_gc:
        st.metric("Grau de Compactação", f"{gc}%", delta=None, delta_color="normal")
    
    # Classe de qualidade
    if gc >= 100:
        st.success("✅ **Excelente** - Compactação acima do proctor máximo.")
    elif gc >= 95:
        st.info("📈 **Bom** - Atende aos critérios típicos de aterros.")
    else:
        st.error("❌ **Insatisfatório** - Abaixo do mínimo recomendado (95%).")
    
    # Botão de download do PDF
    if st.button("📄 Gerar Relatório PDF", use_container_width=True):
        # Monta dicionário completo para o PDF
        dados_pdf = {
            'u_a': tara, 'u_b': solo_umido_bandeja, 'u_c': solo_seco_bandeja,
            'u_d': umidade['peso_umido'], 'u_e': umidade['peso_seco'],
            'u_f': umidade['agua'], 'u_g': umidade['teor'],
            'd_a': massa_inicial, 'd_b': massa_final, 'd_c': densidade['areia_consumida'],
            'd_d': areia_cone, 'd_e': densidade['areia_buraco'],
            'd_f': densidade_areia, 'd_g': densidade['volume_buraco'],
            'd_h_total': solo_bandeja, 'd_h_tara': tara_bandeja,
            'd_i': densidade['densidade_umida'], 'd_j': densidade['densidade_seca'],
            'gc': gc
        }
        pdf_bytes = gerar_pdf(dados_pdf, proctor_max, gc)
        st.download_button(
            label="⬇️ Baixar PDF",
            data=pdf_bytes,
            file_name=f"relatorio_compactacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
else:
    st.info("👈 Preencha todas as seções anteriores para calcular o grau de compactação.")
