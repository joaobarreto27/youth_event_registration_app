import streamlit as st
import pandas as pd
import time
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# ==================== CONEXÃO COM O BANCO ====================
# Usa st.connection (cache automático, retries, secrets gerenciados)
conn = st.connection(
    "my_postgres", type="sql"
)  # nome deve bater com [connections.my_postgres] nos secrets


# Helper para obter uma sessão SQLAlchemy (para transações/inserts)
@st.cache_resource
def get_session():
    return conn.session


# ==================== FUNÇÕES AUXILIARES ====================
@st.cache_data(ttl=10)  # Cache curto para frescor
def listar_eventos_registrados():
    query = """
    SELECT id_event AS id_event, event_name
    FROM registered_events  -- ou events, dependendo da sua tabela principal
    ORDER BY id_event
    """
    df = conn.query(query)
    return df.to_dict(orient="records")


@st.cache_data(ttl=10)
def listar_participantes_unicos():
    query = """
    SELECT DISTINCT participant_name
    FROM event_participants
    ORDER BY participant_name
    """
    df = conn.query(query)
    return df.to_dict(orient="records")


def criar_evento(nome_evento: str, nome_criador: str):
    session = get_session()
    try:
        # Cria o evento (assume tabela 'events' com UNIQUE em event_name)
        result = session.execute(
            text("INSERT INTO events (event_name) VALUES (:nome) RETURNING id"),
            {"nome": nome_evento},
        )
        event_id = result.fetchone()[0]

        # Registra na registered_events
        session.execute(
            text("""
                INSERT INTO registered_events (event_id, event_name, created_by, created_at)
                VALUES (:event_id, :nome, :criador, CURRENT_TIMESTAMP)
            """),
            {"event_id": event_id, "nome": nome_evento, "criador": nome_criador},
        )

        # Registra criador como participante
        session.execute(
            text("""
                INSERT INTO event_participants (event_id, participant_name)
                VALUES (:event_id, :nome)
            """),
            {"event_id": event_id, "nome": nome_criador},
        )

        session.commit()
        return True, event_id
    except IntegrityError:
        session.rollback()
        # Já existe → pega o ID existente
        result = session.execute(
            text("SELECT id FROM events WHERE event_name = :nome"),
            {"nome": nome_evento},
        )
        event_id = result.fetchone()[0]
        return False, event_id  # False indica "já existia"
    except Exception as e:
        session.rollback()
        st.error(f"Erro ao criar evento: {e}")
        return False, None


def registrar_participante(event_id: int, nome: str) -> bool:
    session = get_session()
    try:
        session.execute(
            text("""
                INSERT INTO event_participants (event_id, participant_name)
                VALUES (:event_id, :nome)
            """),
            {"event_id": event_id, "nome": nome},
        )
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False  # Já votou
    except Exception as e:
        session.rollback()
        st.error(f"Erro ao registrar voto: {e}")
        return False


# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Registro de Ideia de Eventos", page_icon="🎯", layout="wide"
)

st.title("🎯 Formulário de Registro de Ideia de Eventos Jovens AduPno")
st.divider()

# ==================== LAYOUT PRINCIPAL ====================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🗳️ Votar em Ideias de Eventos")
    st.markdown("Vote nas ideias de eventos que você mais gostaria que tivesse!")
    nome_votante = st.text_input(
        "👤 Seu nome", placeholder="Digite seu nome completo", key="nome_votante"
    )

    eventos = listar_eventos_registrados()
    eventos_map = {e["event_name"]: e["id_event"] for e in eventos}

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
                st.cache_data.clear()  # Limpa caches
                st.rerun()

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

    outros_eventos_voto = st.multiselect(
        "🎉 Votar em outras ideias de eventos também (opcional)",
        options=list(eventos_map.keys()),
        placeholder="Selecione uma ou mais ideias",
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
                    f"✅ {nome_criador} a sua ideia de evento **{nome_novo_evento}** foi registrada e votada!"
                )
                # Votos adicionais
                for evento_nome in outros_eventos_voto:
                    if registrar_participante(
                        eventos_map[evento_nome], nome_criador.strip()
                    ):
                        st.write(f"✅ Voto em: **{evento_nome}**")
                st.toast("Ideia criada e votos registrados!", icon="🎉")
                st.cache_data.clear()
                st.rerun()
            else:
                st.warning(
                    f"⚠️ A ideia **{nome_novo_evento}** já existe! Vote nela na seção ao lado (🗳️ Votar em Ideias de Eventos)."
                )

# ==================== PARTICIPANTES ÚNICOS ====================
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
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("⚠️ Nenhum participante registrado ainda")

# Auto-refresh a cada 60s
time.sleep(60)
st.cache_data.clear()
st.rerun()
