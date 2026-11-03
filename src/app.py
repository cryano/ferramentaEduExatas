import streamlit as st
import google.generativeai as genai

# -----------------------------------------------------------------------------
# Configuração da Página e Tema AVA/UCSAL
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AVA Exatas | UCSAL",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS inspirada no ambiente virtual acadêmico (AVA / Moodle)
st.markdown("""
    <style>
    /* Estilo Geral */
    .stApp {
        background-color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header Institucional AVA */
    .ava-header {
        background: linear-gradient(135deg, #002B49 0%, #005691 100%);
        color: #FFFFFF;
        padding: 24px 32px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 43, 73, 0.15);
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ava-title { font-size: 1.8rem; font-weight: 700; margin: 0; }
    .ava-subtitle { font-size: 0.95rem; color: #E2E8F0; margin-top: 4px; }
    .ava-badge {
        background-color: #FFB800;
        color: #002B49;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 6px 12px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Cartões de Conteúdo */
    .ava-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .ava-card-title {
        color: #002B49;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    /* Caixas de Referência Bibliográfica */
    .biblio-box {
        background-color: #F1F5F9;
        border-left: 4px solid #005691;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        font-size: 0.88rem;
        color: #334155;
        margin-top: 10px;
    }
    .biblio-title { font-weight: 700; color: #002B49; }

    /* Customização de Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #FFFFFF;
        border-radius: 6px 6px 0 0;
        color: #475569;
        font-weight: 600;
        padding: 10px 20px;
        border: 1px solid #E2E8F0;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #005691 !important;
        color: #FFFFFF !important;
        border-color: #005691 !important;
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
# Gestão de Autenticação da API do Gemini (Com Tratamento Fallback de Modelos)
# -----------------------------------------------------------------------------
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.error("⚙️ Configuração Pendente")
        api_key = st.text_input("Insira sua API Key do Google Gemini:", type="password")

def inicializar_modelo_gemini(chave, instrucao_sistema):
    """Inicializa a API testando nomes de modelos compatíveis para evitar erro 404."""
    genai.configure(api_key=chave)
    
    # Lista de identificadores de modelo em ordem de prioridade
    modelos_candidatos = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    ultimo_erro = None
    for nome_modelo in modelos_candidatos:
        try:
            modelo = genai.GenerativeModel(
                model_name=nome_modelo,
                system_instruction=instrucao_sistema
            )
            return modelo, nome_modelo
        except Exception as e:
            ultimo_erro = e
            continue
            
    raise RuntimeError(f"Não foi possível conectar aos modelos Gemini. Detalhe: {ultimo_erro}")

# -----------------------------------------------------------------------------
# Estrutura em Abas (Estilo Moodle / AVA)
# -----------------------------------------------------------------------------
tab_ia, tab_materiais, tab_grupos = st.tabs([
    "💬 Tutor de IA (Pedagógico)", 
    "📚 Biblioteca & Materiais Didáticos", 
    "🗓️ Agendamento de Grupos de Estudo"
])

# =============================================================================
# ABA 1: TUTOR DE IA (PEDAGÓGICO - REGRAS ESTRITAS)
# =============================================================================
with tab_ia:
    st.markdown("""
        <div class="ava-card">
            <div class="ava-card-title">🤖 Assistente Virtual de Apoio ao Estudante</div>
            <p style="color: #475569; font-size: 0.92rem; margin: 0;">
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
    """

    if not api_key:
        st.warning("⚠️ Insira a chave de API do Gemini nos Segredos da aplicação para habilitar o atendimento.")
    else:
        try:
            model, model_name_used = inicializar_modelo_gemini(api_key, SYSTEM_PROMPT)

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
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response.text})

        except Exception as e:
            st.error(f"⚠️ Erro de conexão com o serviço de Inteligência Artificial: {e}")

# =============================================================================
# ABA 2: BIBLIOTECA & MATERIAIS DIDÁTICOS REAIS
# =============================================================================
with tab_materiais:
    st.markdown("""
        <div class="ava-card">
            <div class="ava-card-title">📖 Repositório de Conteúdos e Referências Bibliográficas</div>
            <p style="color: #475569; font-size: 0.92rem; margin: 0;">
                Materiais estruturados segundo a ementa acadêmica oficial da UCSAL, com indicação direta dos capítulos das obras físicas disponíveis na Biblioteca Central da Universidade.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📘 Cálculo I")
        
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
                <span class="biblio-title">📚 Referências Recomendadas:</span><br>
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
                <span class="biblio-title">📚 Referências Recomendadas:</span><br>
                • <strong>STEWART, James.</strong> <em>Cálculo, Volume 1</em>. 8ª Ed. <strong>Capítulo 3 (Seções 3.1 a 3.9, pp. 170–245)</strong>.<br>
                • <strong>LEITHOLD, Louis.</strong> <em>O Cálculo com Geometria Analítica, Vol. 1</em>. 3ª Ed. Harbra, 1994. <strong>Capítulo 3 (pp. 145–210)</strong>.
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 📙 Cálculo II")
        
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
                <span class="biblio-title">📚 Referências Recomendadas:</span><br>
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
                <span class="biblio-title">📚 Referências Recomendadas:</span><br>
                • <strong>STEWART, James.</strong> <em>Cálculo, Volume 1</em>. 8ª Ed. <strong>Capítulo 6 (Seções 6.1 a 6.3, pp. 417–445)</strong>.<br>
                • <strong>FLEMMING, Diva M.; GONÇALVES, Mirian B.</strong> <em>Cálculo A</em>. 6ª Ed. <strong>Capítulo 7 (pp. 280–325)</strong>.
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# ABA 3: AGENDAMENTO COLABORATIVO (OPÇÕES PROGRAMADAS)
# =============================================================================
with tab_grupos:
    st.markdown("""
        <div class="ava-card">
            <div class="ava-card-title">🤝 Módulo de Aprendizagem Colaborativa</div>
            <p style="color: #475569; font-size: 0.92rem; margin: 0;">
                Agende sessoes de estudo presenciais ou virtuais com colegas da UCSAL, monitores e alunos veteranos. 
                Selecione um dos turnos e horários oficiais abaixo.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Dados em sessão para simulador
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
        st.markdown("#### 📅 Sessões Confirmadas")
        for g in st.session_state.grupos_agendados:
            st.markdown(f"""
            <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-left: 4px solid #005691; padding: 14px; border-radius: 6px; margin-bottom: 12px;">
                <strong style="color: #002B49; font-size: 1.05rem;">{g['materia']}</strong> — <span style="color: #334155;">{g['assunto']}</span><br>
                <div style="font-size: 0.85rem; color: #64748B; margin-top: 6px;">
                    🗓️ <strong>Data/Turno:</strong> {g['dia']} | {g['horario']}<br>
                    📍 <strong>Local:</strong> {g['local']}<br>
                    👤 <strong>Organizado por:</strong> {g['organizador']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_dir:
        st.markdown("#### ➕ Agendar Nova Sessão")
        with st.form("form_agendamento_programado", clear_on_submit=True):
            
            # Opções totalmente preprogramadas para padronização
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

            # Apenas 2 campos abertos (tópico e identificação)
            assunto_input = st.text_input("Tópico/Assunto Específico (ex: Teorema do Confronto)", placeholder="Digite o tema do estudo...")
            organizador_input = st.text_input("Nome do Aluno / Matrícula UCSAL", placeholder="Ex: Maria Serra (Matrícula: 200040584)")

            btn_submeter = st.form_submit_button("Confirmar Agendamento no AVA")

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