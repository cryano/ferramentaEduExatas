import streamlit as st
import google.generativeai as genai
import re

# -----------------------------------------------------------------------------
# Configuração da Página e Tema AVA/UCSAL (Dark Mode Nativo)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma de Exatas | UCSAL",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS totalmente adaptada para o Tema Escuro Institucional
st.markdown("""
    <style>
    /* Reset de Fundo e Texto Principal */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Header Institucional AVA (Estilo Dark Navy) */
    .ava-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        color: #FFFFFF;
        padding: 20px 24px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ava-title { font-size: 1.7rem; font-weight: 700; color: #F8FAFC; margin: 0; }
    .ava-subtitle { font-size: 0.9rem; color: #94A3B8; margin-top: 4px; }
    .ava-badge {
        background-color: #EAB308;
        color: #0F172A;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 6px 12px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Cartões de Conteúdo Dark */
    .ava-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 20px;
        color: #E2E8F0;
    }
    .ava-card-title {
        color: #38BDF8;
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
        font-size: 0.88rem;
        color: #CBD5E1;
        margin-top: 12px;
    }
    .biblio-title { font-weight: 700; color: #38BDF8; }

    /* Cards das Sessões Agendadas */
    .session-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-left: 4px solid #38BDF8;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
        color: #F1F5F9;
    }
    .session-title { color: #38BDF8; font-size: 1.05rem; font-weight: 700; }
    .session-meta { font-size: 0.85rem; color: #94A3B8; margin-top: 6px; line-height: 1.5; }

    /* Ajuste de Botões de Abas para garantir Visibilidade do Texto */
    button[data-baseweb="tab"] {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #38BDF8 !important;
        border-bottom-color: #38BDF8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Topo Institucional
st.markdown("""
    <div class="ava-header">
        <div>
            <div class="ava-title">Ambiente Virtual de Aprendizagem | Exatas</div>
            <div class="ava-subtitle">Universidade Católica do Salvador — Apoio Integrado em Matemática Básica e Cálculo</div>
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
            resposta = modelo.generate_content(prompt)
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
            <div class="ava-card-title">Assistente Virtual de Apoio</div>
            <p style="color: #94A3B8; font-size: 0.92rem; margin: 0;">
                O Tutor Virtual atua como mediador de aprendizagem. De acordo com as diretrizes pedagógicas do curso, 
                ele <strong>não fornece respostas diretas aos exercícios</strong>, auxiliando na compreensão de teoremas, 
                identificação de equívocos de raciocínio e orientação passo a passo.
            </p>
        </div>
    """, unsafe_allow_html=True)

    SYSTEM_PROMPT = """Você é o Assistente Virtual Acadêmico de Exatas da Universidade Católica do Salvador (UCSAL).

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
                {"role": "assistant", "content": "Olá! Sou o Tutor Virtual de Cálculo da UCSAL. Qual conceito ou problema você deseja analisar agora?"}
            ]

        # Histórico em área com rolagem própria (o campo de digitação fica sempre visível logo abaixo)
        area_chat = st.container(height=480, border=True)
        with area_chat:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

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

        if enviar and prompt and prompt.strip():
            st.session_state.chat_messages.append({"role": "user", "content": prompt.strip()})
            with st.spinner("Consultando base de conhecimento pedagógica..."):
                try:
                    resposta_texto = chamar_gemini_com_fallback(api_key, SYSTEM_PROMPT, prompt.strip())
                    st.session_state.chat_messages.append({"role": "assistant", "content": resposta_texto})
                except Exception as e:
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"⚠️ Erro de conexão com o serviço de Inteligência Artificial: {e}"
                    })
            st.rerun()

# =============================================================================
# ABA 2: BIBLIOTECA & MATERIAIS DIDÁTICOS REAIS
# =============================================================================
with tab_materiais:
    st.markdown("""
        <div class="ava-card">
            <div class="ava-card-title">Repositório de Conteúdos e Referências Bibliográficas</div>
            <p style="color: #94A3B8; font-size: 0.92rem; margin: 0;">
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
            * Nocão intuitiva de limite e definição formal ($\varepsilon, \delta$)
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
            <p style="color: #94A3B8; font-size: 0.92rem; margin: 0;">
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