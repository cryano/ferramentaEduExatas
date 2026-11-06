import streamlit as st
import google.generativeai as genai
import re

# -----------------------------------------------------------------------------
# Identidade da ferramenta (mesmo nome usado no relatório do projeto)
# -----------------------------------------------------------------------------
NOME_FERRAMENTA = "Ferramenta Educacional Colaborativa com IA para Apoio em Exatas"

# -----------------------------------------------------------------------------
# Configuração da Página e Tema AVA/UCSAL (Dark Mode)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{NOME_FERRAMENTA} | UCSAL",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta (contraste mínimo WCAG AA = 4.5:1 para texto normal):
#   Fundo #0F172A | Cartões #1E293B | Texto #F8FAFC (17:1) | Texto secundário #CBD5E1 (12:1)
#   Destaque #7DD3FC (azul claro, 11:1) | Botões: fundo #38BDF8 com texto #0F172A (8:1)
# O CSS força cores claras em TODOS os componentes, para que a leitura não dependa
# do tema (claro/escuro) do navegador de quem acessa.
st.markdown("""
    <style>
    :root { color-scheme: dark; }

    /* Fundo e texto principal (baixa especificidade: não sobrescreve cores definidas nas classes abaixo) */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .stApp :where(p, li, label, span, h1, h2, h3, h4, h5, h6, summary, small, th, td) {
        color: #F8FAFC;
    }
    .stApp :where(a) { color: #7DD3FC; }

    /* Header Institucional */
    .ava-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #475569;
        padding: 20px 24px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
    }
    .ava-header .ava-title { font-size: 1.45rem; font-weight: 700; color: #F8FAFC; margin: 0; line-height: 1.3; }
    .ava-header .ava-subtitle { font-size: 0.95rem; color: #CBD5E1; margin-top: 6px; }
    .ava-header .ava-badge {
        background-color: #FACC15;
        color: #0F172A;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 6px 12px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        white-space: nowrap;
    }

    /* Cartões de Conteúdo */
    .ava-card {
        background-color: #1E293B;
        border: 1px solid #475569;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 20px;
    }
    .ava-card .ava-card-title {
        color: #7DD3FC;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    /* Caixas de Referência Bibliográfica */
    .biblio-box {
        background-color: #0F172A;
        border-left: 4px solid #38BDF8;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
        margin-top: 12px;
    }
    .biblio-box, .biblio-box strong, .biblio-box em { color: #E2E8F0; }
    .biblio-box .biblio-title { font-weight: 700; color: #7DD3FC; }

    /* Cards das Sessões Agendadas */
    .session-card {
        background-color: #1E293B;
        border: 1px solid #475569;
        border-left: 4px solid #38BDF8;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .session-card .session-title { color: #7DD3FC; font-size: 1.05rem; font-weight: 700; }
    .session-card .session-meta { font-size: 0.9rem; color: #E2E8F0; margin-top: 6px; line-height: 1.6; }
    .session-card .session-meta strong { color: #F8FAFC; }

    /* Abas: texto legível, aba ativa destacada */
    .stApp [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #475569; }
    .stApp button[data-baseweb="tab"] { background: transparent !important; }
    .stApp button[data-baseweb="tab"] p,
    .stApp button[data-baseweb="tab"] span,
    .stApp button[data-baseweb="tab"] div {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    .stApp button[data-baseweb="tab"][aria-selected="true"] p,
    .stApp button[data-baseweb="tab"][aria-selected="true"] span,
    .stApp button[data-baseweb="tab"][aria-selected="true"] div {
        color: #7DD3FC !important;
    }
    .stApp [data-baseweb="tab-highlight"] { background-color: #38BDF8 !important; height: 3px !important; }
    .stApp [data-baseweb="tab-border"] { background-color: #475569 !important; }

    /* Botões (inclui o "Enviar" e o "Confirmar Agendamento") */
    .stApp .stButton > button,
    .stApp [data-testid="stFormSubmitButton"] > button,
    .stApp [data-testid^="stBaseButton"] {
        background-color: #38BDF8 !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 8px !important;
    }
    .stApp .stButton > button *,
    .stApp [data-testid="stFormSubmitButton"] > button *,
    .stApp [data-testid^="stBaseButton"] * {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    .stApp .stButton > button:hover,
    .stApp [data-testid="stFormSubmitButton"] > button:hover,
    .stApp [data-testid^="stBaseButton"]:hover {
        background-color: #7DD3FC !important;
        border-color: #7DD3FC !important;
    }
    .stApp button:focus-visible, .stApp input:focus-visible { outline: 3px solid #FACC15 !important; outline-offset: 2px; }

    /* Campos de texto e listas de seleção */
    .stApp input, .stApp textarea,
    .stApp [data-baseweb="input"], .stApp [data-baseweb="base-input"],
    .stApp [data-baseweb="select"] > div {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
        border-color: #64748B !important;
    }
    .stApp input::placeholder, .stApp textarea::placeholder {
        color: #A9B6C8 !important;
        -webkit-text-fill-color: #A9B6C8 !important;
        opacity: 1 !important;
    }
    .stApp [data-baseweb="select"] * { color: #F8FAFC !important; }
    [data-baseweb="popover"] [data-baseweb="menu"],
    [data-baseweb="popover"] ul { background-color: #1E293B !important; }
    [data-baseweb="popover"] li, [data-baseweb="popover"] li * { color: #F8FAFC !important; }
    [data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] { background-color: #334155 !important; }

    /* Chat */
    .stApp [data-testid="stChatMessage"] { background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; }
    .stApp [data-testid="stChatMessage"] * { color: #F8FAFC; }
    .stApp [data-testid="stVerticalBlockBorderWrapper"] { border-color: #475569; }

    /* Expanders, formulários e avisos */
    .stApp [data-testid="stExpander"] { border: 1px solid #475569; border-radius: 8px; background-color: #1E293B; }
    .stApp [data-testid="stExpander"] summary, .stApp [data-testid="stExpander"] summary * { color: #F8FAFC !important; }
    .stApp [data-testid="stForm"] { border-color: #475569; }
    .stApp [data-testid="stAlert"] * { color: #F8FAFC !important; }
    .stApp [data-testid="stSpinner"] * { color: #E2E8F0 !important; }
    [data-testid="stSidebar"] { background-color: #1E293B; }
    </style>
""", unsafe_allow_html=True)

# Topo Institucional
st.markdown(f"""
    <div class="ava-header">
        <div>
            <div class="ava-title">{NOME_FERRAMENTA}</div>
            <div class="ava-subtitle">Universidade Católica do Salvador (UCSAL) — Apoio em Matemática Básica, Cálculo I e Cálculo II</div>
        </div>
        <div class="ava-badge">Semestre 2026.2</div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Autenticação da API do Gemini
# -----------------------------------------------------------------------------
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Insira sua API Key do Google Gemini:", type="password")
        if not api_key:
            st.error("⚙️ Configuração Pendente")

# -----------------------------------------------------------------------------
# Extração e Sanitização da Resposta (remove rascunhos / raciocínio interno)
# -----------------------------------------------------------------------------
def extrair_resposta_final(texto):
    """
    O modelo é instruído a escrever a resposta final dentro de <resposta>...</resposta>.
    Tudo que estiver fora dessas tags (rascunhos, análise de regras etc.) é descartado.
    """
    if not texto:
        return ""

    # Caso normal: tags completas (pega a ÚLTIMA ocorrência, que é a resposta definitiva)
    blocos = re.findall(r'<resposta>(.*?)</resposta>', texto, re.DOTALL | re.IGNORECASE)
    blocos = [b.strip() for b in blocos if b.strip()]
    if blocos:
        return blocos[-1]

    # Tag de abertura sem fechamento (resposta cortada)
    partes = re.split(r'<resposta>', texto, flags=re.IGNORECASE)
    if len(partes) > 1 and partes[-1].strip():
        return re.sub(r'</?resposta>', '', partes[-1], flags=re.IGNORECASE).strip()

    # Fallback: sem tags, usa a limpeza heurística
    return tratar_texto_resposta(texto)


def tratar_texto_resposta(texto):
    """Fallback: filtra vazamentos de meta-análise/rascunhos mentais em inglês."""
    if not texto:
        return ""

    # Se houver saudação oficial em português após os metadados, corta tudo que veio antes
    match_ola = re.search(r'(Olá!.*)', texto, re.DOTALL)
    if match_ola and any(kw in texto for kw in ["User question:", "User asks:", "Constraint Check:", "Draft"]):
        texto = match_ola.group(1)

    linhas = texto.splitlines()
    linhas_limpas = []

    for linha in linhas:
        l_lower = linha.strip().lower()
        if any(key in l_lower for key in [
            'user question:', 'user asks:', 'constraint check:', 'constraints:', 'identity:',
            'draft 1:', 'draft:', 'refining for tone', 'expanding on',
            'ensuring latex', 'only final message', 'no planning', 'self-correction',
            'goal:', 'role:', 'greeting:', 'interactive element:', 'theoretical approach:',
            'practical approach:', 'ensure tone'
        ]):
            continue
        if re.match(r'^\s*[-*•]\s*("|\')?(user|constraint|identity|role|scope|guidelines|formatting|who|how|programming|draft|refining|expanding|ensuring|goal|greeting|definition|theoretical|practical|interactive)', l_lower):
            continue
        linhas_limpas.append(linha)

    resultado = "\n".join(linhas_limpas).strip()

    # Remove aspas externas caso a API tenha envelopado a resposta inteira entre aspas
    if len(resultado) > 1 and ((resultado.startswith('"') and resultado.endswith('"')) or (resultado.startswith("'") and resultado.endswith("'"))):
        resultado = resultado[1:-1].strip()

    return resultado

# -----------------------------------------------------------------------------
# Escolha dos modelos (apenas modelos Gemini "normais", sem modelos de raciocínio)
# -----------------------------------------------------------------------------
MODELOS_PREFERIDOS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-1.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-pro",
]
MODELOS_EXCLUIDOS = [
    "gemma", "thinking", "exp", "tts", "image", "vision", "embedding",
    "aqa", "live", "audio", "learnlm", "robotics", "computer-use"
]

@st.cache_data(ttl=3600, show_spinner=False)
def listar_modelos_disponiveis(chave):
    genai.configure(api_key=chave)
    nomes = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                nomes.append(m.name.replace("models/", ""))
    except Exception:
        pass
    return nomes

def montar_candidatos(chave):
    disponiveis = listar_modelos_disponiveis(chave)
    candidatos = []

    # 1) Preferidos, na ordem, se existirem na conta
    for pref in MODELOS_PREFERIDOS:
        if pref in disponiveis:
            candidatos.append(pref)

    # 2) Demais modelos gemini-* que não sejam de raciocínio/experimentais
    for nome in disponiveis:
        if nome in candidatos or not nome.startswith("gemini"):
            continue
        if any(x in nome for x in MODELOS_EXCLUIDOS):
            continue
        candidatos.append(nome)

    # 3) Se a listagem falhou, tenta os preferidos às cegas
    if not candidatos:
        candidatos = list(MODELOS_PREFERIDOS)

    return candidatos

def extrair_texto_sem_pensamento(resposta):
    """Junta apenas as partes que NÃO são 'pensamento' do modelo."""
    try:
        partes_texto = []
        for cand in resposta.candidates:
            for parte in cand.content.parts:
                if getattr(parte, "thought", False):
                    continue
                if getattr(parte, "text", None):
                    partes_texto.append(parte.text)
        if partes_texto:
            return "".join(partes_texto)
    except Exception:
        pass
    return resposta.text

# -----------------------------------------------------------------------------
# Chamada à API com Fallback Real Durante o Envio
# -----------------------------------------------------------------------------
def montar_conteudo_com_historico(mensagens, limite=12):
    """
    Converte o histórico do chat (já incluindo a pergunta atual como última mensagem)
    para o formato do Gemini. Ignora a saudação inicial e mensagens de erro.
    """
    conteudo = []
    for m in mensagens:
        if m["content"].startswith("⚠️"):
            continue
        papel = "user" if m["role"] == "user" else "model"
        # O histórico precisa começar com uma mensagem do aluno (descarta a saudação inicial)
        if not conteudo and papel == "model":
            continue
        conteudo.append({"role": papel, "parts": [m["content"]]})
    return conteudo[-limite:]

def chamar_gemini_com_fallback(chave, instrucao_sistema, prompt):
    genai.configure(api_key=chave)
    candidatos = montar_candidatos(chave)

    ultimo_erro = None
    for nome_modelo in candidatos:
        try:
            modelo = genai.GenerativeModel(
                model_name=nome_modelo,
                system_instruction=instrucao_sistema,
                generation_config={"temperature": 0.4}
            )
            resposta = modelo.generate_content(prompt)  # prompt = lista de mensagens (histórico + pergunta atual)
            bruto = extrair_texto_sem_pensamento(resposta)
            final = extrair_resposta_final(bruto)
            if final:
                return final
        except Exception as e:
            ultimo_erro = e
            continue

    raise RuntimeError(f"Nenhum modelo disponível respondeu à requisição. Detalhes: {ultimo_erro}")

# -----------------------------------------------------------------------------
# Estrutura Principal de Navegação (Abas)
# -----------------------------------------------------------------------------
tab_ia, tab_materiais, tab_grupos = st.tabs([
    "IA Assistente", 
    "Biblioteca & Materiais Didáticos", 
    "Agendamento de Grupos de Estudo"
])

# =============================================================================
# ABA 1: TUTOR DE IA (PEDAGÓGICO)
# =============================================================================
with tab_ia:
    st.markdown("""
        <div class="ava-card">
            <div class="ava-card-title">IA Assistente (Tutor Pedagógico)</div>
            <p style="color: #CBD5E1; font-size: 0.92rem; margin: 0;">
                O Tutor Pedagógico atua como mediador de aprendizagem. De acordo com as diretrizes pedagógicas do curso, 
                ele <strong>não fornece respostas diretas aos exercícios</strong>, auxiliando na compreensão de teoremas, 
                identificação de equívocos de raciocínio e orientação passo a passo.
            </p>
        </div>
    """, unsafe_allow_html=True)

    SYSTEM_PROMPT = f"""Você é o Tutor Pedagógico da {NOME_FERRAMENTA}, da Universidade Católica do Salvador (UCSAL).
Quando precisar se apresentar, use sempre esse nome.

Sua atuação é restrita às disciplinas de Matemática Básica, Cálculo I e Cálculo II.

REGRAS OBRIGATÓRIAS:
1. Responda SEMPRE diretamente ao aluno em português do Brasil.
2. É ESTRITAMENTE PROIBIDO exibir raciocínio interno, análises de regras, rascunhos ou cabeçalhos em inglês (como 'User question:', 'Constraint:', 'Draft:', 'Identity:').
3. JAMAIS forneça soluções prontas ou respostas numéricas finais de exercícios. Explique os conceitos e faça perguntas reflexivas para que o estudante encontre a resposta.
4. Utilize notação LaTeX para termos matemáticos quando necessário ($x^2$, $\\int f(x)dx$).

FORMATO DE SAÍDA (OBRIGATÓRIO):
Escreva TODA a mensagem destinada ao aluno dentro das tags <resposta> e </resposta>.
Nada deve aparecer fora dessas tags: nenhum planejamento, análise, rascunho ou comentário.
Exemplo: <resposta>Olá! ... sua mensagem ao aluno ...</resposta>"""

    if not api_key:
        st.warning("⚠️ Insira a chave de API do Gemini nos Segredos da aplicação para habilitar o atendimento.")
    else:
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [
                {"role": "assistant", "content": f"Olá! Sou o Tutor Pedagógico da {NOME_FERRAMENTA} (UCSAL). Posso ajudar com Matemática Básica, Cálculo I e Cálculo II. Qual conceito ou problema você deseja analisar agora?"}
            ]

        # Histórico em área com rolagem própria (o campo de digitação fica sempre visível logo abaixo)
        # A caixa começa pequena e cresce conforme a conversa, até um limite (depois disso, rola).
        ALTURA_MIN, ALTURA_MAX = 110, 480
        altura_estimada = 30
        for m in st.session_state.chat_messages:
            linhas = max(1, -(-len(m["content"]) // 110))  # ceil(chars / ~110 por linha)
            altura_estimada += 55 + linhas * 24 + m["content"].count("\n") * 24
        if st.session_state.get("resposta_pendente"):
            altura_estimada += 80  # espaço para o indicador "consultando..."
        altura_chat = max(ALTURA_MIN, min(ALTURA_MAX, altura_estimada))
        area_chat = st.container(height=altura_chat, border=True)
        with area_chat:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Pergunta já está na tela; agora busca a resposta da IA
            if st.session_state.get("resposta_pendente"):
                with st.chat_message("assistant"):
                    with st.spinner("Consultando base de conhecimento pedagógica..."):
                        try:
                            conteudo = montar_conteudo_com_historico(st.session_state.chat_messages)
                            resposta_texto = chamar_gemini_com_fallback(api_key, SYSTEM_PROMPT, conteudo)
                            st.session_state.chat_messages.append({"role": "assistant", "content": resposta_texto})
                        except Exception as e:
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": f"⚠️ Erro de conexão com o serviço de Inteligência Artificial: {e}"
                            })
                st.session_state.resposta_pendente = False
                st.rerun()

        # Campo de mensagem: formulário fixo na aba (não depende de st.chat_input, que
        # some/aparece de forma inconsistente quando está dentro de abas)
        with st.form("form_chat_ia", clear_on_submit=True):
            col_input, col_btn = st.columns([6, 1], vertical_alignment="bottom")
            with col_input:
                prompt = st.text_input(
                    "Sua dúvida",
                    placeholder="Digite sua dúvida acadêmica (ex: 'Como aplico a regra da cadeia na derivada de sin(x^2)?')...",
                    label_visibility="collapsed"
                )
            with col_btn:
                enviar = st.form_submit_button("Enviar", use_container_width=True)

        # Ao enviar: só registra a pergunta e recarrega a página. Assim a pergunta já aparece
        # no chat imediatamente, e a chamada à IA acontece no bloco "resposta pendente" acima.
        if enviar and prompt and prompt.strip():
            st.session_state.chat_messages.append({"role": "user", "content": prompt.strip()})
            st.session_state.resposta_pendente = True
            st.rerun()

# =============================================================================
# ABA 2: BIBLIOTECA & MATERIAIS DIDÁTICOS REAIS
# =============================================================================
with tab_materiais:
    st.markdown("""
        <div class="ava-card">
            <div class="ava-card-title">Repositório de Conteúdos e Referências Bibliográficas</div>
            <p style="color: #CBD5E1; font-size: 0.92rem; margin: 0;">
                Materiais estruturados segundo a ementa acadêmica oficial da UCSAL, com indicação direta dos capítulos das obras físicas disponíveis na Biblioteca Central da Universidade.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='color: #F8FAFC;'>Cálculo I</h3>", unsafe_allow_html=True)
        
        with st.expander("1. Limites e Continuidade", expanded=True):
            st.markdown("""
            **Tópicos Principais:**
            * Noção intuitiva de limite e definição formal ($\\varepsilon, \\delta$)
            * Limites laterais, infinitos e no infinito
            * Formas indeterminadas ($\\frac{0}{0}, \\frac{\infty}{\infty}$) e Teorema do Confronto

            **Resumo de Fórmula:**
            $$\lim_{x \\to 0} \\frac{\sin x}{x} = 1$$
            """)
            st.markdown("""
            <div class="biblio-box">
                <span class="biblio-title">Referências Recomendadas:</span><br>
                • <strong>STEWART, James.</strong> <em>Cálculo, Volume 1</em>. 8ª Ed. São Paulo: Cengage Learning, 2016. <strong>Capítulo 2 (Seções 2.2 a 2.6, pp. 83–130)</strong>.<br>
                • <strong>FLEMMING, Diva M.; GONÇALVES, Mirian B.</strong> <em>Cálculo A: Funções, Limite, Derivação e Integração</em>. 6ª Ed. Pearson, 2007. <strong>Capítulo 3 (pp. 67–118)</strong>.
            </div>
            """, unsafe_allow_html=True)

        with st.expander("2. Derivadas e Regras de Derivação"):
            st.markdown("""
            **Tópicos Principais:**
            * Taxa de variação média e instantânea (Reta Tangente)
            * Regra do Produto, Regra do Quociente e Regra da Cadeia
            * Derivação Implícita e Taxas Relacionadas

            **Resumo de Fórmula:**
            $$\\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)$$
            """)
            st.markdown("""
            <div class="biblio-box">
                <span class="biblio-title">Referências Recomendadas:</span><br>
                • <strong>STEWART, James.</strong> <em>Cálculo, Volume 1</em>. 8ª Ed. <strong>Capítulo 3 (Seções 3.1 a 3.9, pp. 170–245)</strong>.<br>
                • <strong>LEITHOLD, Louis.</strong> <em>O Cálculo com Geometria Analítica, Vol. 1</em>. 3ª Ed. Harbra, 1994. <strong>Capítulo 3 (pp. 145–210)</strong>.
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("<h3 style='color: #F8FAFC;'>Cálculo II</h3>", unsafe_allow_html=True)
        
        with st.expander("1. Integrais Definidas e Indefinidas", expanded=True):
            st.markdown("""
            **Tópicos Principais:**
            * Primitivas e Integral Indefinida
            * Teorema Fundamental do Cálculo
            * Métodos de Integração: Substituição e Integração por Partes

            **Resumo de Fórmula:**
            $$\int u \, dv = uv - \int v \, du$$
            """)
            st.markdown("""
            <div class="biblio-box">
                <span class="biblio-title">Referências Recomendadas:</span><br>
                • <strong>STEWART, James.</strong> <em>Cálculo, Volume 1</em>. 8ª Ed. <strong>Capítulo 5 (pp. 353–412)</strong> e <strong>Capítulo 7 (Seções 7.1 a 7.4)</strong>.<br>
                • <strong>THOMAS, George B.</strong> <em>Cálculo, Volume 1</em>. 12ª Ed. Pearson, 2012. <strong>Capítulo 5 e Capítulo 8 (pp. 440–510)</strong>.
            </div>
            """, unsafe_allow_html=True)

        with st.expander("2. Aplicações da Integral Definida"):
            st.markdown("""
            **Tópicos Principais:**
            * Área entre curvas planas
            * Volume de sólidos de revolução (Método dos Discos e Cascas Cilíndricas)
            * Comprimento de arco e Trabalho

            **Resumo de Fórmula:**
            $$V = \pi \int_{a}^{b} [f(x)]^2 \, dx$$
            """)
            st.markdown("""
            <div class="biblio-box">
                <span class="biblio-title">Referências Recomendadas:</span><br>
                • <strong>STEWART, James.</strong> <em>Cálculo, Volume 1</em>. 8ª Ed. <strong>Capítulo 6 (Seções 6.1 a 6.3, pp. 417–445)</strong>.<br>
                • <strong>FLEMMING, Diva M.; GONÇALVES, Mirian B.</strong> <em>Cálculo A</em>. 6ª Ed. <strong>Capítulo 7 (pp. 280–325)</strong>.
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# ABA 3: AGENDAMENTO COLABORATIVO
# =============================================================================
with tab_grupos:
    st.markdown("""
        <div class="ava-card">
            <div class="ava-card-title">Módulo de Aprendizagem Colaborativa</div>
            <p style="color: #CBD5E1; font-size: 0.92rem; margin: 0;">
                Agende sessões de estudo presenciais ou virtuais com colegas da UCSAL, monitores e alunos veteranos. 
                Selecione um dos turnos e horários oficiais abaixo.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if "grupos_agendados" not in st.session_state:
        st.session_state.grupos_agendados = [
            {
                "materia": "Cálculo I", 
                "assunto": "Revisão Geral de Derivadas e Regra da Cadeia", 
                "dia": "Quinta-feira", 
                "horario": "17:00 - 18:30 (Entre-turnos)", 
                "local": "Presencial - Biblioteca Central (Campus Pituaçu)",
                "organizador": "Monitoria de Exatas"
            },
            {
                "materia": "Cálculo II", 
                "assunto": "Resolução de Exercícios de Integração por Partes", 
                "dia": "Sexta-feira", 
                "horario": "14:00 - 15:40 (Tarde)", 
                "local": "Online - Microsoft Teams (Canal da Turma)",
                "organizador": "Lucas Batista (Veterano)"
            }
        ]

    col_esq, col_dir = st.columns([1, 1])

    with col_esq:
        st.markdown("<h4 style='color: #38BDF8; font-weight: 700;'>Sessões Confirmadas</h4>", unsafe_allow_html=True)
        for g in st.session_state.grupos_agendados:
            st.markdown(f"""
            <div class="session-card">
                <div class="session-title">{g['materia']} — {g['assunto']}</div>
                <div class="session-meta">
                    🗓️ <strong>Data/Turno:</strong> {g['dia']} | {g['horario']}<br>
                    📍 <strong>Local:</strong> {g['local']}<br>
                    👤 <strong>Organizado por:</strong> {g['organizador']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_dir:
        st.markdown("<h4 style='color: #38BDF8; font-weight: 700;'>Agendar Nova Sessão</h4>", unsafe_allow_html=True)
        with st.form("form_agendamento_programado", clear_on_submit=True):
            
            disciplina_sel = st.selectbox(
                "Disciplina", 
                ["Cálculo I", "Cálculo II", "Matemática Básica"]
            )
            
            dia_sel = st.selectbox(
                "Dia da Semana", 
                ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]
            )
            
            horario_sel = st.selectbox(
                "Horário Programado", 
                [
                    "08:00 - 09:40 (Turno Matutino)",
                    "10:00 - 11:40 (Turno Matutino)",
                    "14:00 - 15:40 (Turno Vespertino)",
                    "16:00 - 17:40 (Turno Vespertino)",
                    "17:00 - 18:30 (Janela Entre-turnos)",
                    "18:30 - 20:10 (Turno Noturno)"
                ]
            )

            local_sel = st.selectbox(
                "Local / Modalidade",
                [
                    "Presencial - Biblioteca Central (Campus Pituaçu)",
                    "Presencial - Sala de Estudos de Engenharia",
                    "Presencial - Laboratório de Informática",
                    "Online - Microsoft Teams",
                    "Online - Google Meet"
                ]
            )

            assunto_input = st.text_input("Tópico/Assunto Específico (ex: Teorema do Confronto)", placeholder="Digite o tema do estudo...")
            organizador_input = st.text_input("Nome do Aluno / Matrícula UCSAL", placeholder="Ex: Maria Serra (Matrícula: 200040584)")

            btn_submeter = st.form_submit_button("Confirmar Agendamento")

            if btn_submeter:
                if not assunto_input or not organizador_input:
                    st.error("Por favor, preencha o tópico do estudo e seu nome/matrícula.")
                else:
                    st.session_state.grupos_agendados.append({
                        "materia": disciplina_sel,
                        "assunto": assunto_input,
                        "dia": dia_sel,
                        "horario": horario_sel,
                        "local": local_sel,
                        "organizador": organizador_input
                    })
                    st.success("Sessão de estudos agendada e publicada com sucesso!")
                    st.rerun()