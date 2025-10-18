import streamlit as st
import requests
import json
import re
from pypdf import PdfReader

# Configuração da página
st.set_page_config(page_title="Carbon Due Diligence AI", page_icon="🌳", layout="wide")

# Título profissional
st.title("🌳 Carbon Due Diligence AI")
st.markdown("**Análise Automatizada de Adicionalidade em PDDs de Carbono**")
st.markdown("---")

# Sidebar amigável para clientes
with st.sidebar:
    st.header("🔑 Configuração Rápida")
    st.markdown("""
    ### 🆓 Teste Gratuitamente:
    1. **Acesse** [Groq Console](https://console.groq.com)
    2. **Clique** em 'Sign Up' (crie sua conta)
    3. **Vá em** 'API Keys' → 'Create API Key'
    4. **Cole** a chave abaixo
    5. **Teste** quantas análises quiser!
    
    *💡 100% gratuito - sem cartão de crédito*
    """)
    
    api_key = st.text_input("**Cole sua Groq API Key:**", type="password", placeholder="sk-...")
    
    st.markdown("---")
    
    st.markdown("### 📊 O Que Esta Ferramenta Faz:")
    st.markdown("""
    - ✅ **Analisa adicionalidade** em PDDs
    - ✅ **Identifica riscos** em projetos de carbono  
    - ✅ **Dá score** de 1-10 para qualidade
    - ✅ **Recomenda** aprovar ou rejeitar
    """)
    
    st.markdown("---")
    st.success("**⚡ Análise em 3 segundos**")

# Funções de análise
def extrair_texto_pdf(pdf_file):
    try:
        leitor = PdfReader(pdf_file)
        texto_total = ""
        for pagina in leitor.pages:
            texto = pagina.extract_text()
            if texto:
                texto_total += texto + "\n"
        return texto_total if texto_total else None
    except Exception as e:
        return None

def encontrar_secao_adicionalidade(texto):
    padroes = [
        r'additionalit[y|ie][\s\S]{1,2000}(?=\n\s*\n|\n[A-Z]|$)',
        r'4\.\s*[1-9]?\d?\s*[\.]?\s*Additionalit[y|ie][\s\S]{1,2000}',
    ]
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group().strip()
    return texto[:5000]

def analisar_com_groq(api_key, texto):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Como especialista senior em créditos de carbono, analise a SECÇÃO DE ADICIONALIDADE abaixo.

    TEXTO PARA ANÁLISE:
    {texto[:3500]}

    FORMATO DE RESPOSTA (em português):
    **Score de Risco:** [X]/10
    **Análise Técnica:**
    - **Pontos Fortes:** [lista]
    - **Pontos de Atenção:** [lista] 
    - **Riscos Identificados:** [lista]
    **Recomendação Final:** [🟢 APROVAR / 🟡 ANALISAR MAIS / 🔴 REJEITAR]

    Seja direto e técnico.
    """
    
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "llama-3.1-8b-instant",  # ⭐⭐ MODELO ATUALIZADO ⭐⭐
        "temperature": 0.1,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"❌ Erro na API Groq: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

# Interface principal
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload do PDD")
    uploaded_file = st.file_uploader("**Faça upload do PDF do projeto**", type="pdf")
    
    if uploaded_file:
        st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
        
        with st.expander("📋 Pré-visualização do texto extraído"):
            texto_completo = extrair_texto_pdf(uploaded_file)
            if texto_completo:
                secao = encontrar_secao_adicionalidade(texto_completo)
                st.text_area("Texto da seção de adicionalidade:", secao[:2000] + "..." if len(secao) > 2000 else secao, height=200)

with col2:
    st.subheader("📊 Resultado da Análise")
    
    if uploaded_file and api_key:
        if st.button("🚀 Executar Análise Completa", type="primary"):
            with st.spinner("🔍 Analisando adicionalidade, riscos e viabilidade..."):
                texto_completo = extrair_texto_pdf(uploaded_file)
                
                if texto_completo:
                    secao_adicionalidade = encontrar_secao_adicionalidade(texto_completo)
                    
                    if len(secao_adicionalidade) > 200:
                        resultado = analisar_com_groq(api_key, secao_adicionalidade)
                        
                        # Exibe o resultado formatado
                        st.markdown("### 📋 Relatório de Due Diligence")
                        st.markdown(resultado)
                        
                        # Feedback visual
                        if "🟢 APROVAR" in resultado:
                            st.balloons()
                            st.success("🎉 **PROJETO RECOMENDADO** - Baixo risco identificado")
                        elif "🔴 REJEITAR" in resultado:
                            st.error("🚨 **ALTO RISCO** - Recomendação de rejeição")
                        else:
                            st.warning("⚠️ **RISCO MODERADO** - Análise adicional necessária")
                            
                    else:
                        st.error("❌ Seção de adicionalidade não encontrada no documento")
                else:
                    st.error("❌ Não foi possível extrair texto del PDF")
    
    elif uploaded_file and not api_key:
        st.warning("⚠️ **Cole sua Groq API Key na sidebar para executar a análise**")

# Rodapé profissional
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>Carbon Due Diligence AI</strong> - Ferramenta de análise automatizada para investidores e desenvolvedores de projetos de carbono</p>
    <p>⚡ Análises em tempo real | 🎯 Foco em adicionalidade | 📊 Score de risco quantificado</p>
</div>
""", unsafe_allow_html=True)
