import streamlit as st
import google.generativeai as genai


# -----------------------------------------------------------------------------
# Configuração Inicial da Página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma de Cálculo - UCSAL",
    page_icon="📐",
    layout="wide"
)

# Estilo visual simples
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: bold; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📐 Plataforma Educacional de Cálculo (UCSAL)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Apoio colaborativo e inteligência artificial para estudantes de Exatas</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Gestão da Chave de API do Gemini
# -----------------------------------------------------------------------------
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.warning("⚙️ Configuração Local")
        api_key = st.text_input("Insira sua API Key do Google Gemini:", type="password")
        st.caption("No Streamlit Cloud, adicione em Secrets como GEMINI_API_KEY.")

# -----------------------------------------------------------------------------
# Navegação Principal (As 3 Funcionalidades Obrigatórias do Relatório)
# -----------------------------------------------------------------------------
tab_ia, tab_materiais, tab_grupos = st.tabs([
    "🤖 Assistente de IA (Tutor)", 
    "📚 Central de Materiais", 
    "👥 Aprendizagem Colaborativa"
])

# =============================================================================
# ABA 1: ASSISTENTE VIRTUAL COM IA (REGRAS PEDAGÓGICAS ESTRITAS)
# =============================================================================
with tab_ia:
    st.subheader("🤖 Tutor Virtual de Cálculo I & II")
    st.info("💡 **Como funciona:** Tire suas dúvidas conceituais ou peça ajuda em exercícios. A IA não entregará a resposta pronta, mas guiará seu raciocínio passo a passo.")

    # Prompt do Sistema (Regra de Ouro do Relatório)
    SYSTEM_INSTRUCTION = """
    Você é o Tutor de Exatas especializado na comunidade acadêmica da UCSAL (Universidade Católica do Salvador).
    Sua área de atuação compreende exclusivamente Matemática Básica, Cálculo I e Cálculo II.

    REGRA DE OURO IMPRESCINDÍVEL:
    1. NUNCA forneça a resposta final ou o cálculo resolvido de forma direta para o estudante.
    2. Explique os conceitos teóricos por trás da dúvida (ex: definição de limite, regra da cadeia, integração por partes).
    3. Faça perguntas orientadoras para que o próprio aluno descubra o próximo passo da resolução.
    4. Se o estudante enviar uma tentativa de resolução incorreta, identifique a etapa exata do erro e incentive-o a refazer aquele ponto.
    5. Mantenha uma linguagem acolhedora, clara, didática e motivadora.
    """

    if not api_key:
        st.error("⚠️ Insira a chave da API do Gemini para ativar o assistente.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )

            # Histórico da conversa na sessão
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = [
                    {"role": "assistant", "content": "Olá! Sou seu Tutor de Cálculo na UCSAL. Qual conceito ou exercício você gostaria de revisar hoje?"}
                ]

            # Exibir histórico de mensagens
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Input do usuário
            if prompt := st.chat_input("Digite sua dúvida de Cálculo..."):
                st.session_state.chat_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Analisando sua dúvida pedagógica..."):
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response.text})

        except Exception as e:
            st.error(f"Erro ao conectar com a API: {e}")

# =============================================================================
# ABA 2: CENTRAL DE MATERIAIS DIDÁTICOS CENTRALIZADOS
# =============================================================================
with tab_materiais:
    st.subheader("📚 Repositório Central de Materiais Didáticos")
    st.write("Conteúdos selecionados e alinhados à ementa das disciplinas da UCSAL.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📘 Cálculo I")
        with st.expander("1. Limites e Continuidade"):
            st.write("• Formulas fundamentais de limites")
            st.write("• Teorema do Confronto")
            st.write("• Exercícios recomendados: Lista 01 - UCSAL")
        with st.expander("2. Derivadas e Aplicações"):
            st.write("• Tabela de Derivadas Rápida")
            st.write("• Regra da Cadeia e Derivação Implícita")
            st.write("• Aplicações: Taxas Relacionadas e Máximos/Mínimos")

    with col2:
        st.markdown("### 📙 Cálculo II")
        with st.expander("1. Integrais Definidas e Indefinidas"):
            st.write("• Tabela de Integrais Imediatas")
            st.write("• Métodos: Substituição e Integração por Partes")
        with st.expander("2. Aplicações da Integral"):
            st.write("• Cálculo de Áreas entre curvas")
            st.write("• Volumes de Sólidos de Revolução")

# =============================================================================
# ABA 3: APRENDIZAGEM COLABORATIVA (AGENDAMENTO DE ESTUDOS)
# =============================================================================
with tab_grupos:
    st.subheader("👥 Agendamento de Grupos de Estudo & Monitoria")
    st.write("Espaço para integração entre calouros, veteranos e monitores da UCSAL.")

    # Simulador de armazenamento em sessão
    if "grupos_agendados" not in st.session_state:
        st.session_state.grupos_agendados = [
            {"materia": "Cálculo I", "assunto": "Revisão para P1 (Derivadas)", "dia": "Quinta-feira", "horario": "17:00", "organizador": "Monitoria Acadêmica"},
            {"materia": "Cálculo II", "assunto": "Técnicas de Integração por Partes", "dia": "Sexta-feira", "horario": "14:00", "organizador": "Grupo de Estudos Eng. Software"}
        ]

    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("#### 📅 Próximos Grupos Confirmados")
        for g in st.session_state.grupos_agendados:
            st.info(f"**{g['materia']}** — {g['assunto']}\n\n🕒 **Quando:** {g['dia']} às {g['horario']}\n\n👤 **Organizado por:** {g['organizador']}")

    with c2:
        st.markdown("#### ➕ Propor Novo Horário de Estudo")
        with st.form("form_grupo"):
            mat = st.selectbox("Disciplina", ["Matemática Básica", "Cálculo I", "Cálculo II"])
            assunto = st.text_input("Assunto / Tópico de estudo")
            dia = st.text_input("Dia da Semana (ex: Terça-feira)")
            horario = st.text_input("Horário (ex: 16:00)")
            autor = st.text_input("Seu Nome / Matrícula")
            submit = st.form_submit_button("Criar Grupo de Estudo")

            if submit and assunto and dia and horario and autor:
                st.session_state.grupos_agendados.append({
                    "materia": mat, "assunto": assunto, "dia": dia, "horario": horario, "organizador": autor
                })
                st.success("Grupo de estudo cadastrado com sucesso! Atualize a página se necessário.")
                st.rerun()