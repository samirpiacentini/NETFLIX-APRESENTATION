import os
import time
from pathlib import Path
import streamlit as st
from groq import Groq

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Netflix AI - Analista Filmográfico",
    page_icon="🍿",
    layout="wide"
)

# Estilização Temática Estilo Netflix (CSS Customizado)
st.markdown("""
<style>
    /* Importação de fonte moderna e limpa estilo interfaces OTT */
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;500;700&display=swap');

    /* Fundo Preto Oficial da Netflix */
    .stApp {
        background-color: #141414;
        color: #FFFFFF;
        font-family: 'Roboto', sans-serif;
    }

    /* Barra Lateral Estilo Menu Netflix */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #222222;
    }

    /* Títulos em Fonte Estilo Logo/Catálogo */
    h1, h2, h3 {
        font-family: 'Bebas Neue', cursive, sans-serif !important;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Logo / Título Principal estilo Netflix */
    .netflix-title {
        font-family: 'Bebas Neue', cursive !important;
        font-size: 3.8rem;
        color: #E50914;
        text-shadow: 0px 4px 15px rgba(229, 9, 20, 0.4);
        margin-bottom: 0px;
        letter-spacing: 3px;
    }

    /* Subtítulo / Slogan de Plataforma */
    .netflix-subtitle {
        font-size: 1.1rem;
        color: #AAAAAA;
        font-weight: 300;
        margin-bottom: 30px;
    }

    /* Badge Estilo 'Original / Top 10' */
    .netflix-badge {
        display: inline-block;
        background-color: #E50914;
        color: white;
        font-size: 0.8rem;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 3px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }

    /* Container do Formulário */
    [data-testid="stForm"] {
        background: #181818;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
    }

    /* Botão Vermelho Oficial da Netflix */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #E50914 !important;
        color: white !important;
        font-family: 'Bebas Neue', cursive !important;
        font-size: 1.4rem !important;
        letter-spacing: 1.5px !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 10px 24px !important;
        transition: background-color 0.2s ease, transform 0.2s ease !important;
        width: 100%;
    }

    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #F6121D !important;
        transform: scale(1.01);
        cursor: pointer;
    }

    /* Botão Secundário para Download */
    .stDownloadButton > button {
        background-color: #333333 !important;
        color: white !important;
        font-family: 'Roboto', sans-serif !important;
        font-weight: 500 !important;
        border: 1px solid #555555 !important;
        border-radius: 4px !important;
        transition: all 0.2s ease !important;
    }

    .stDownloadButton > button:hover {
        background-color: #444444 !important;
        border-color: #ffffff !important;
    }

    /* Linha Divisória Escura */
    hr {
        border-color: #333333;
        margin: 35px 0;
    }

    /* Ajuste de Caixas de Texto */
    input[type="text"], input[type="password"] {
        background-color: #333333 !important;
        color: white !important;
        border: 1px solid #444444 !important;
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

def load_system_prompt() -> str:
    """Carrega o prompt do arquivo .github/copilot-instructions.md ou da variável de ambiente."""
    env_prompt = os.getenv("SYSTEM_PROMPT")
    if env_prompt:
        return env_prompt
    
    try:
        base_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
        prompt_path = base_dir / ".github" / "copilot-instructions.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
    except Exception:
        pass
    
    return """Você é um Analista de Cinema e Teórico Filmográfico Sênior. 
Analise o filme com rigor técnico, sem sinopses superficiais, usando a estrutura em 5 tópicos (Visão Geral, Linguagem Visual, Som/Montagem, Subtexto com Tabela em Markdown e Veredito)."""

# Cabeçalho Estilo Netflix
st.markdown('<div class="netflix-badge">Análise Exclusiva AI</div>', unsafe_allow_html=True)
st.markdown('<h1 class="netflix-title">NETFLIX FILM ANALYSIS</h1>', unsafe_allow_html=True)
st.markdown('<p class="netflix-subtitle">Decupagem técnica, subtexto e crítica acadêmica sob demanda.</p>', unsafe_allow_html=True)

# Input da Chave de API da Groq na Barra Lateral
st.sidebar.markdown("### ⚙️ Configurações da Conta")
api_key = os.getenv("GROQ_API_KEY") or st.sidebar.text_input("Groq API Key", type="password")

if not api_key:
    st.info("💡 Insira sua **Groq API Key** na barra lateral para iniciar a sessão.")
    st.stop()

# Limpa espaços acidentais
api_key = api_key.strip()

# Validação do formato da chave da Groq
if not api_key.startswith("gsk_"):
    st.error("⚠️ A API Key deve começar com 'gsk_...'. Verifique suas credenciais no Groq Console.")
    st.stop()

# Formulário Estilo Player/Busca
with st.form("film_form"):
    film_name = st.text_input("O que você quer analisar hoje?", placeholder="Digite o nome do filme (Ex: Parasita, Taxi Driver, Interstellar)")
    submit_button = st.form_submit_button("▶ REPRODUZIR ANÁLISE")

if submit_button and film_name:
    system_prompt = load_system_prompt()
    user_prompt = f"Realize uma análise rigorosa, técnica e detalhada do filme: {film_name}."

    with st.spinner("Carregando análise... Por favor, aguarde."):
        client = Groq(api_key=api_key)
        
        # Modelos válidos da Groq
        candidate_models = [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-120b",
        ]
        
        response_text = None
        last_error = None

        for model_name in candidate_models:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        }
                    ],
                    model=model_name,
                )
                if chat_completion.choices and chat_completion.choices[0].message.content:
                    response_text = chat_completion.choices[0].message.content
                    break
            except Exception as e:
                last_error = e
                err_msg = str(e).lower()
                
                if "invalid api key" in err_msg or "authentication" in err_msg:
                    break
                
                time.sleep(1)

        if response_text:
            st.success("Análise pronta para exibição!")
            st.markdown("---")
            
            # Exibição da Resposta
            st.markdown(response_text)
            
            st.markdown("---")
            file_slug = "".join(c if c.isalnum() else "_" for c in film_name.lower())
            st.download_button(
                label="⬇ BAIXAR ANÁLISE COMPLETA (.MD)",
                data=response_text.encode('utf-8'),
                file_name=f"analise_{file_slug}.md",
                mime="text/markdown; charset=utf-8"
            )
        else:
            st.error(f"Ocorreu um erro ao carregar a análise: {last_error}")