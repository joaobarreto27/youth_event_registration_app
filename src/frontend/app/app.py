import streamlit as st
import requests
import pandas as pd
import time

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Registro de Ideia de Eventos", page_icon="🎯", layout="wide"
)
API_URL = "http://localhost:8000/eventos"

st.title("🎯 Formulário de Registro de Ideia de Eventos Jovens AduPno")
st.divider()


# ==================== FUNÇÕES AUXILIARES ====================
@st.cache_data(
    ttl=5
)  # Cache com TTL curto para equilibrar performance e frescor dos dados
def listar_eventos_registrados():
    try:
        response = requests.get(f"{API_URL}/registered/", timeout=30)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Erro ao buscar eventos: {e}")
        return []


@st.cache_data(ttl=5)  # Cache com TTL curto
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

            # Registrar na tabela registered_events
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
                st.error(
                    f"❌ {nome_criador} Ocorreu um erro ao registrar sua ideia de evento: {response_registered.json().get('detail', 'Erro desconhecido')}"
                )
                return False, None

            # Registrar criador como participante
            requests.post(
                f"{API_URL}/{event_id}/participants",
                json={"participant_name": nome_criador},
                timeout=30,
            )

            return True, event_id
        else:
            st.error(response.json().get("detail", "Erro ao criar sua ideia de evento"))
            return False, None
    except Exception:
        st.error(
            f"❌ {nome_criador} ocorreu um erro ao criar sua ideia **{nome_novo_evento}**, pois esta ideia já foi criada por outro jovem, vote nesta ideia **{nome_novo_evento}** na sessão ao lado **(🗳️ Votar em Ideias de Eventos)**."
        )
        return False, None


def registrar_participante(event_id: int, nome: str):
    try:
        response = requests.post(
            f"{API_URL}/{event_id}/participants",
            json={"participant_name": nome},
            timeout=30,
        )
        if response.status_code == 200:
            return True
        elif response.status_code == 409:
            st.warning(
                f"⚠️ {nome} você já votou nesta ideia de evento, vote em uma outra ideia ou crie uma nova ideia na sessão ao lado **➕ Criar Nova Ideia de Evento**"
            )
            return False
        else:
            st.error(response.json().get("detail", "Erro ao registrar voto"))
            return False
    except Exception as e:
        st.error(f"Erro ao registrar participante: {e}")
        return False


# ==================== CONFIGURAÇÃO DE AUTO-REFRESH ====================
# Auto-refresh sempre ativado por padrão
auto_refresh = True
refresh_interval = 60  # Intervalo em segundos (1 minuto)

# ==================== LAYOUT PRINCIPAL ====================
col1, col2 = st.columns(2)

# -------------------- COLUNA 1 — VOTAR EM EVENTOS --------------------
with col1:
    st.subheader("🗳️ Votar em Ideias de Eventos")
    st.markdown("Vote nas ideias de eventos que você mais gostaria que tivesse!")
    nome_votante = st.text_input(
        "👤 Seu nome", placeholder="Digite seu nome completo", key="nome_votante"
    )

    eventos = listar_eventos_registrados()
    eventos_map = {e["event_name"]: e["id_event"] for e in eventos}

    # Multiselect
    eventos_selecionados = st.multiselect(
        "🎉 Selecione as ideias",
        options=list(eventos_map.keys()),
        placeholder="Escolha uma ou mais ideias",
        key="eventos_selecionados",
    )

    if st.button("✅ Confirmar Voto"):
        if not nome_votante.strip():
            st.error("❌ Informe seu nome")
        elif not eventos_selecionados:
            st.error(f"❌ **{nome_votante}** Selecione ao menos uma ideia para votar!")
        else:
            votos_registrados = False
            for evento in eventos_selecionados:
                if registrar_participante(eventos_map[evento], nome_votante.strip()):
                    votos_registrados = True
            if votos_registrados:
                st.toast("Voto(s) registrado(s) com sucesso!", icon="✅")
                listar_eventos_registrados.clear()
                listar_participantes_unicos.clear()
                time.sleep(0.5)  # Pequeno delay para permitir que o backend processe
                st.rerun()  # Força atualização imediata após ação

# -------------------- COLUNA 2 — CRIAR EVENTO E VOTAR --------------------
with col2:
    st.subheader("➕ Criar Nova Ideia de Evento")
    st.markdown("Proponha novas ideias de eventos e vote nelas!")

    nome_criador = st.text_input(
        "👤 Seu Nome", placeholder="Digite seu nome completo", key="criador_nome"
    )
    nome_novo_evento = st.text_input(
        "🎯 Nome da Ideia",
        placeholder="ex: Boliche, Karaoke...",
        key="novo_evento_nome",
    )

    eventos_registrados = listar_eventos_registrados()
    lista_eventos_existentes = (
        {e["event_name"]: e["id_event"] for e in eventos_registrados}
        if eventos_registrados
        else {}
    )
    outros_eventos_voto = st.multiselect(
        "🎉 Votar em outras ideias de eventos também (opcional)",
        options=list(lista_eventos_existentes.keys()),
        placeholder="Selecione uma ou mais ideias de eventos",
        key="outros_eventos_voto",
    )

    st.markdown("---")

    if st.button("✅ Criar Ideia de Evento e Votar", key="btn_criar_evento"):
        if not nome_criador.strip():
            st.error("❌ Informe seu nome!")
        elif not nome_novo_evento.strip():
            st.error(f"❌ {nome_criador} Informe o nome de sua ideia!")
        else:
            sucesso_criacao, event_id = criar_evento(
                nome_novo_evento.strip(), nome_criador.strip()
            )
            if sucesso_criacao:
                st.success(
                    f"✅ {nome_criador} a sua ideia de evento **{nome_novo_evento}** foi registrada e já votado nesta opção. Muito obrigado!"
                )
                st.write(f"✅ Voto registrado em: **{nome_novo_evento}**")

                # Votar em outros eventos
                votos_adicionais = False
                for evento_nome in outros_eventos_voto:
                    if registrar_participante(
                        lista_eventos_existentes[evento_nome], nome_criador.strip()
                    ):
                        votos_adicionais = True
                    st.write(
                        f"✅ {nome_criador} seu voto foi registrado com sucesso em: **{evento_nome}**"
                    )

                st.toast("Ideia de evento criado e votos registrados!", icon="🎉")
                listar_eventos_registrados.clear()
                listar_participantes_unicos.clear()
                time.sleep(0.5)  # Pequeno delay
                st.rerun()  # Força atualização imediata após ação
            else:
                st.error(
                    f"❌ {nome_criador} ocorreu um erro ao criar sua ideia **{nome_novo_evento}**, pois esta ideia já foi criada por outro jovem, vote nesta ideia **{nome_novo_evento}** na sessão ao lado **(🗳️ Votar em Ideias de Eventos)**."
                )

# -------------------- PARTICIPANTES ÚNICOS --------------------
st.divider()
st.subheader("👥 Lista Geral de Participantes")

participantes = listar_participantes_unicos()

if participantes:
    df = pd.DataFrame(participantes)
    df["participant_name"] = df["participant_name"].str.strip().str.title()
    df_unicos = (
        df.drop_duplicates(subset=["participant_name"])
        .sort_values("participant_name")
        .reset_index(drop=True)
    )

    st.metric("Total de Participantes Únicos", len(df_unicos))
    st.dataframe(
        df_unicos.rename(columns={"participant_name": "Nome"}),
        width="stretch",
        hide_index=True,
    )
    st.toast("Lista de participantes atualizada", icon="👥")
else:
    st.warning("⚠️ Nenhum participante registrado ainda")

# ==================== LÓGICA DE AUTO-REFRESH (POLLING) ====================
# Auto-refresh periódico a cada 1 minuto
if auto_refresh:
    time.sleep(refresh_interval)
    listar_eventos_registrados.clear()
    listar_participantes_unicos.clear()
    st.rerun()
