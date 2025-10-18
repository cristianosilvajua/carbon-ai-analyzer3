import streamlit as st
import requests
import json
import re
from pypdf import PdfReader

# Configuração da página
st.set_page_config(page_title="Carbon Due Diligence AI", page_icon="🌳")

# Título do seu site
st.title("🌳 Carbon Due Diligence AI")
st.markdown("**Analise PDDs de créditos de carbono em 60 segundos**")

# Sidebar para a chave da API
with st.sidebar:
    st.header("🔑 Configuração")
    api_key = st.text_input("Cole sua Groq API Key:", type="password")
    st.markdown("[Obtenha sua chave GRATUITA aqui](https://console.groq.com/keys)")
    st.markdown("---")
    st.info("Use Groq API - é gratuita e rápida!")

# Função para extrair PDF
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
        st.error(f"Erro ao ler PDF: {str(e)}")
        return None

def encontrar_secao_adicionalidade(texto):
    padroes = [
        r'additionalit[y|ie][\s\S]{1,1500}(?=\n\s*\n|\n[A-Z]|$)',
        r'adicionalidade[\s\S]{1,1500}(?=\n\s*\n|\n[A-Z]|$)',
    ]
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group().strip()
    return texto[:4000]

# ⭐⭐ FUNÇÃO COM GROQ API (GRATUITA) ⭐⭐
def analisar_adicionalidade_groq(api_key, texto):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Analise esta seção de ADICIONALIDADE de um projeto de carbono e responda em PORTUGUÊS:

    TEXTO: {texto[:3000]}

    FORMATO DA RESPOSTA:
    **Score:** X/10
    **Pontos Fortes:** 
    - ...
    **Pontos Fracos:**
    - ...
    **Recomendação:** [APROVAR/ANALISAR MAIS/REJEITAR]
    """
    
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "llama3-8b-8192",
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Erro na API: {response.text}"
    except Exception as e:
        return f"Erro: {str(e)}"

# Área principal do site
st.subheader("📤 Faça upload do PDD (PDF)")

uploaded_file = st.file_uploader("Escolha o arquivo PDF do projeto", type="pdf")

if uploaded_file is not None and api_key:
    
    with st.spinner("🔍 Analisando o documento..."):
        
        texto_completo = extrair_texto_pdf(uploaded_file)
        
        if texto_completo:
            secao_adicionalidade = encontrar_secao_adicionalidade(texto_completo)
            
            if len(secao_adicionalidade) > 100:
                
                # ⭐⭐ CHAMA A GROQ API ⭐⭐
                resultado = analisar_adicionalidade_groq(api_key, secao_adicionalidade)
                
                st.success("✅ Análise concluída!")
                st.subheader("📊 Resultado:")
                st.markdown(resultado)
                
                # Mostra um resumo visual do score
                if "**Score:**" in resultado:
                    try:
                        score_texto = resultado.split("**Score:**")[1].split("/")[0].strip()
                        score = int(score_texto)
                        if score <= 3:
                            st.balloons()
                            st.success("🎉 Projeto de Baixo Risco!")
                        elif score <= 7:
                            st.warning("⚠️ Projeto de Risco Moderado")
                        else:
                            st.error("🚨 Projeto de Alto Risco")
                    except:
                        pass
            else:
                st.error("Seção de adicionalidade não encontrada.")
        else:
            st.error("Não foi possível ler o PDF.")

elif uploaded_file and not api_key:
    st.warning("⚠️ Cole sua Groq API Key na sidebar")

else:
    st.markdown("""
    ### 🤔 Como usar:
    1. **Obtenha uma API Key GRATUITA** da [Groq](https://console.groq.com/keys)
    2. **Cole a API Key** na sidebar
    3. **Faça upload do PDD** em PDF
    4. **Receba a análise em segundos**
    
    *100% GRATUITO - sem limites para teste!*
    """)