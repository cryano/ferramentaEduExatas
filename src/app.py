import streamlit as st
import google.generativeai as genai

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
# Chamada à API com Fallback Real Durante o Envio
# -----------------------------------------------------------------------------
def chamar_gemini_com_fallback(chave, instrucao_sistema, prompt):
    genai.configure(api_key=chave)
    
    candidatos = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                candidatos.append(m.name)
    except Exception:
        pass

    if not candidatos:
        candidatos = [
            "gemini-1.5-flash",
            "models/gemini-1.5-flash",
            "gemini-1.5-pro",
            "models/gemini-1.5-pro",
            "gemini-1.0-pro"
        ]
        
    ultimo_erro = None
    for nome_modelo in candidatos:
        try:
            modelo = genai.GenerativeModel(
                model_name=nome_modelo,
                system_instruction=instrucao_sistema
            )
            resposta = modelo.generate_content(prompt)
            return resposta.text
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

    SYSTEM_PROMPT = """
    Você é o Assistente Virtual Acadêmico de Exatas da Universidade Católica do Salvador (UCSAL).
    Sua atuação é restrita ao ensino de Matemática Básica, Cálculo I e Cálculo II.

    DIRETRIZES PEDAGÓGICAS OBRIGATÓRIAS:
    1. JAMAIS forneça a solução final, resultado numérico ou resolução completa imediata de um exercício.
    2. Explique os conceitos e teoremas teóricos envolvidos no problema abordado pelo estudante.
    3. Responda fazendo perguntas reflexivas para que o estudante identifique o próximo passo lógico.
    4. Se o aluno apresentar uma resolução errada, aponte a linha/etapa exata do equívoco conceitual e explique o motivo.
    5. Adote postura acadêmica, formal, clara e motivadora. Utilize notação LaTeX quando necessário ($x^2$, $\int f(x)dx$).

    REGRAS RÍGIDAS DE FORMATAÇÃO DA RESPOSTA:
    - Responda DIRETAMENTE ao aluno em português.
    - É ESTRITAMENTE PROIBIDO exibir seu raciocínio interno, análises de tópicos, notas de planejamento ou rascunhos.
    - É ESTRITAMENTE PROIBIDO incluir cabeçalhos ou marcadores em inglês como 'User asks:', 'Constraint:', 'Scope:', 'Role:', 'Goal:', 'Identity:', 'Methodology:' ou notas de auto-correção.
    - Inicie a mensagem imediatamente com a resposta acadêmica direta ao aluno.
    """

    if not api_key:
        st.warning("⚠️ Insira a chave de API do Gemini nos Segredos da aplicação para habilitar o atendimento.")
    else:
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [
                {"role": "assistant", "content": "Olá! Sou o Tutor Virtual de Cálculo da UCSAL. Qual conceito ou problema você deseja analisar agora?"}
            ]

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Digite sua dúvida acadêmica (ex: 'Como aplico a regra da cadeia na derivada de sin(x^2)?')..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Consultando base de conhecimento pedagógica..."):
                    try:
                        resposta_texto = chamar_gemini_com_fallback(api_key, SYSTEM_PROMPT, prompt)
                        st.session_state.chat_messages.append({"role": "assistant", "content": resposta_texto})
                    except Exception as e:
                        st.error(f"⚠️ Erro de conexão com o serviço de Inteligência Artificial: {e}")
            
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