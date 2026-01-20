import time
import streamlit as st
import requests
import pandas as pd

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Registro de Ideia de Eventos", page_icon="🎯", layout="wide"
)
API_URL = st.secrets.get("api_base_url", "http://localhost:8000") + "/eventos"

st.header("🎯 Formulário de Registro de Ideia de Eventos Jovens AduPno")
st.divider()


# ==================== FUNÇÕES AUXILIARES ====================
@st.cache_data(ttl=5)
def listar_eventos_registrados():
    try:
        response = requests.get(f"{API_URL}/registered/", timeout=30)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        st.error("📡 Erro de conexão: O servidor está demorando para responder.")
        return None


@st.cache_data(ttl=5)
def listar_participantes_unicos():
    try:
        response = requests.get(f"{API_URL}/participants/unique", timeout=30)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Erro ao buscar participantes únicos: {e}")
        return []


def criar_evento(nome_evento: str, nome_criador: str):
    try:
        payload = {"event_name": nome_evento}
        response = requests.post(f"{API_URL}/", json=payload, timeout=30)

        if response.status_code == 200:
            evento = response.json()
            event_id = evento["id_event"]

            response_registered = requests.post(
                f"{API_URL}/registered/",
                params={
                    "event_id": event_id,
                    "event_name": nome_evento,
                    "created_by": nome_criador,
                },
                timeout=30,
            )

            if response_registered.status_code != 200:
                return False, None

            requests.post(
                f"{API_URL}/{event_id}/participants",
                json={"participant_name": nome_criador},
                timeout=30,
            )

            return True, event_id
        else:
            return False, None
    except Exception:
        return False, None


def registrar_participante(event_id: int, nome: str):
    try:
        response = requests.post(
            f"{API_URL}/{event_id}/participants",
            json={"participant_name": nome},
            timeout=30,
        )
        if response.status_code == 200:
            return "sucesso"
        elif response.status_code == 409:
            return "duplicado"
        else:
            return "erro"
    except Exception:
        return "erro"


def check_api_health():
    """Tenta acordar a API se estiver dormindo."""
    try:
        response = requests.get(API_URL.replace("/eventos", "/"), timeout=5)  # noqa: F841
        return True
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
        return False
    except Exception:
        return False


# ==================== VERIFICAÇÃO DE SAÚDE DA API ====================
if "api_awake" not in st.session_state:
    st.session_state.api_awake = False

if not st.session_state.api_awake:
    placeholder = st.empty()

    with placeholder.container():
        with st.status("🚀 Acordando o servidor...", expanded=True) as status:
            if check_api_health():
                st.session_state.api_awake = True
                status.update(
                    label="✅ Servidor Online!", state="complete", expanded=False
                )
                time.sleep(0.5)
                placeholder.empty()
            else:
                st.warning(
                    "😴 A API está em modo de espera. Isso pode levar até 30 segundos."
                )
                time.sleep(2)
                st.rerun()

# ==================== INTERFACE STREAMLIT ====================

# Carrega dados para os selects
eventos = listar_eventos_registrados()

if not isinstance(eventos, list):
    eventos = []

eventos_map = {e["event_name"]: e["id_event"] for e in eventos}

# -------------------- COLUNA - CRIAR --------------------
st.subheader("➕ Criar Nova Ideia de Evento")
st.markdown("Proponha novas ideias de eventos e vote nelas!")

nome_criador = st.text_input(
    "👤 Seu Nome", placeholder="Digite seu nome completo", key="criador_nome"
)
nome_novo_evento = st.text_input(
    "🎯 Qual sua Ideia? (Mande uma por vez)",
    placeholder="ex: Boliche...",
    key="novo_evento_nome",
    help="Para manter a votação organizada, envie uma ideia de cada vez.",
)

outros_eventos = st.multiselect(
    "🎉 Aproveite para votar em outras ideias já sugeridas! (opcional)",
    options=list(eventos_map.keys()),
    placeholder="Clique aqui e escolha quantas quiser",
    key="outros_eventos_voto",
)

if st.button("🚀 Criar Ideia de Evento e Votar", width="stretch"):
    if not nome_criador.strip():
        st.error("❌ Por favor, informe seu **nome** para continuar.")

    elif not nome_novo_evento.strip():
        st.warning(
            f"💡 {nome_criador} **Você quer apenas votar em ideias existentes?**"
        )
        st.info(
            "Para **apenas votar**, utilize a seção logo abaixo: **🗳️ Votar em Ideias de Eventos**."
        )
    else:
        sucesso_criacao, id_novo = criar_evento(nome_novo_evento, nome_criador)

        votos_ad_sucesso = []
        votos_ad_duplicados = []

        for ev_nome in outros_eventos:
            status = registrar_participante(eventos_map[ev_nome], nome_criador)
            if status == "sucesso":
                votos_ad_sucesso.append(ev_nome)
            elif status == "duplicado":
                votos_ad_duplicados.append(ev_nome)

        if not sucesso_criacao:
            st.error(
                f"❌ {nome_criador}, a ideia **{nome_novo_evento}** já foi criada por outro jovem. Para votar nesta ideia utilize a seção logo abaixo: **🗳️ Votar em Ideias de Eventos**!"
            )
            st.info(
                f"💡 Que tal tentar propor uma ideia diferente de **{nome_novo_evento}**?"
            )
        else:
            st.success(
                f"✅ {nome_criador}, ideia **{nome_novo_evento}** foi registrada com sucesso. Obrigado por sua contribuição!"
            )

        if votos_ad_duplicados:
            lista_dup = ", ".join(votos_ad_duplicados)
            st.warning(
                f"⚠️ Você já tinha votado em: **{lista_dup}**. Esses votos não foram repetidos."
            )

        if votos_ad_sucesso:
            lista_suc = ", ".join(votos_ad_sucesso)
            st.success(f"🎉 {nome_criador}, voto(s) registrado(s) em: **{lista_suc}**!")

        if sucesso_criacao or votos_ad_sucesso:
            st.cache_data.clear()
            time.sleep(10)
            st.rerun()

# -------------------- COLUNA VOTAR -------------------
st.divider()
st.subheader("🗳️ Votar em Ideias de Eventos")
st.markdown("Vote nas ideias de eventos que você mais gostaria que tivesse!")
nome_votante = st.text_input(
    "👤 Seu nome", placeholder="Digite seu nome completo", key="nome_votante"
)

eventos_selecionados = st.multiselect(
    "🎉 Selecione as ideias que deseja votar",
    options=list(eventos_map.keys()),
    placeholder="Clique aqui e escolha quantas quiser",
    key="eventos_selecionados",
)

if st.button("✅ Confirmar Voto", width="stretch"):
    if not nome_votante.strip():
        st.error("❌ Por favor, informe seu **nome** para continuar.")
    elif not eventos_selecionados:
        st.error(f"❌ **{nome_votante}** selecione ao menos uma ideia para votar!")
    else:
        votos_com_sucesso = []
        votos_duplicados = []
        erros_tecnicos = []

        for ev_nome in eventos_selecionados:
            status = registrar_participante(eventos_map[ev_nome], nome_votante)
            if status == "sucesso":
                votos_com_sucesso.append(ev_nome)
            elif status == "duplicado":
                votos_duplicados.append(ev_nome)
            else:
                erros_tecnicos.append(f"{ev_nome} ({status})")

        if votos_duplicados:
            lista_dup = ", ".join(votos_duplicados)
            st.warning(
                f"⚠️ **{nome_votante}**, você já tinha votado em: **{lista_dup}**. Esses votos não foram repetidos."
            )

        if erros_tecnicos:
            st.error(
                "❌ Ops! Tivemos um problema técnico ao registrar alguns de seus votos. Por favor, tente novamente."
            )
            for erro in erros_tecnicos:
                print(f"Log de Erro: {erro}")

        if votos_com_sucesso:
            lista_suc = ", ".join(votos_com_sucesso)
            st.success(
                f"✅ **{nome_votante}**, voto(s) registrado(s) com sucesso para: **{lista_suc}**. Obrigado por sua contribuição!"
            )
            st.cache_data.clear()
            time.sleep(10)
            st.rerun()

        elif votos_duplicados:
            st.info(
                "💡 Como você já votou nessas ideias, que tal propor uma nova na seção logo acima: **➕ Criar Nova Ideia de Evento**?"
            )

# -------------------- TABELA DE PARTICIPANTES --------------------
st.divider()
st.subheader("👥 Participantes que já contribuíram")
participantes = listar_participantes_unicos()

if participantes:
    df = pd.DataFrame(participantes)
    if "participant_name" in df.columns:
        df["participant_name"] = df["participant_name"].str.title()
        st.metric("Total de Jovens", len(df))
        st.dataframe(
            df.rename(columns={"participant_name": "Nome"}),
            width="stretch",
            hide_index=True,
        )
    else:
        st.error("Erro no formato dos dados de participantes.")
else:
    st.warning("⚠️ Aguardando primeira contribuição...")
