import streamlit as st
import pandas as pd
import time
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Registro de Ideia de Eventos", page_icon="🎯", layout="wide"
)

# ==================== CONEXÃO COM O BANCO ====================
conn = st.connection("my_postgres", type="sql")


@st.cache_resource
def get_session():
    return conn.session


# ==================== FUNÇÕES AUXILIARES ====================
@st.cache_data(ttl=10)
def listar_eventos_registrados():
    query = "SELECT id_event, event_name FROM registered_events ORDER BY event_name"
    return conn.query(query).to_dict(orient="records")


@st.cache_data(ttl=10)
def listar_participantes_unicos():
    query = "SELECT DISTINCT participant_name FROM event_participants ORDER BY participant_name"
    return conn.query(query).to_dict(orient="records")


def criar_evento(nome_evento: str, nome_criador: str):
    session = get_session()
    nome_evento = nome_evento.strip()
    nome_criador = nome_criador.strip()

    try:
        # 1. Tenta inserir na tabela mestra de eventos
        result = session.execute(
            text("INSERT INTO events (event_name) VALUES (:nome) RETURNING id_event"),
            {"nome": nome_evento},
        )
        id_event = result.fetchone()[0]

        # 2. Registra na registered_events (Note: usei created_date conforme seu último código)
        session.execute(
            text("""
                INSERT INTO registered_events (id_event, event_name, created_by, created_date)
                VALUES (:id_event, :nome, :criador, CURRENT_TIMESTAMP)
            """),
            {"id_event": id_event, "nome": nome_evento, "criador": nome_criador},
        )

        # 3. Registra criador como primeiro participante (voto automático)
        session.execute(
            text("""
                INSERT INTO event_participants (id_event, participant_name)
                VALUES (:id_event, :nome)
            """),
            {"id_event": id_event, "nome": nome_criador},
        )

        session.commit()
        return True, id_event
    except IntegrityError:
        session.rollback()
        return False, None
    except Exception as e:
        session.rollback()
        st.error(f"Erro técnico: {e}")
        return False, None


def registrar_participante(id_event: int, nome: str):
    session = get_session()
    try:
        session.execute(
            text(
                "INSERT INTO event_participants (id_event, participant_name) VALUES (:id_event, :nome)"
            ),
            {"id_event": id_event, "nome": nome.strip()},
        )
        session.commit()
        return "sucesso"
    except IntegrityError:
        session.rollback()
        return "duplicado"
    except Exception as e:
        session.rollback()
        return f"erro: {e}"


# ==================== INTERFACE STREAMLIT ====================
st.title("🎯 Formulário de Ideia de Eventos Jovens AduPno")
st.divider()

col1, col2 = st.columns(2)

# Carrega dados para os selects
eventos = listar_eventos_registrados()
eventos_map = {e["event_name"]: e["id_event"] for e in eventos}

# -------------------- COLUNA 1 — VOTAR --------------------
with col1:
    st.subheader("🗳️ Votar em Ideias de Eventos")
    nome_votante = st.text_input("👤 Seu nome", placeholder="Nome completo", key="nv")

    eventos_selecionados = st.multiselect(
        "🎉 Selecione as ideias",
        options=list(eventos_map.keys()),
        placeholder="Escolha uma ou mais ideias",
    )

    if st.button("✅ Confirmar Voto", width='stretch'=True):
        if not nome_votante.strip():
            st.error("❌ Por favor, informe seu nome.")
        elif not eventos_selecionados:
            st.error("❌ Selecione ao menos uma ideia.")
        else:
            votos_com_sucesso = 0
            for ev_nome in eventos_selecionados:
                status = registrar_participante(eventos_map[ev_nome], nome_votante)
                if status == "sucesso":
                    votos_com_sucesso += 1
                elif status == "duplicado":
                    st.warning(f"⚠️ {nome_votante}, você já votou em: {ev_nome}")

            if votos_com_sucesso > 0:
                st.success(f"{votos_com_sucesso} voto(s) registrado(s)!", icon="✅")
                time.sleep(1.5)
                st.cache_data.clear()
                st.rerun()

# -------------------- COLUNA 2 — CRIAR --------------------
with col2:
    st.subheader("➕ Criar Nova Ideia")
    nome_criador = st.text_input("👤 Seu Nome", placeholder="Seu nome", key="nc")
    nome_novo_evento = st.text_input(
        "🎯 Nome da Ideia", placeholder="Ex: Noite da Pizza"
    )

    outros_eventos = st.multiselect(
        "🎉 Aproveite e vote em outros também", options=list(eventos_map.keys())
    )

    if st.button("🚀 Criar e Votar", width='stretch'=True):
        if not nome_criador.strip() or not nome_novo_evento.strip():
            st.error("❌ Preencha seu nome e o nome da ideia.")
        else:
            sucesso, id_novo = criar_evento(nome_novo_evento, nome_criador)

            if sucesso:
                st.success(
                    f"✅ Ideia **{nome_novo_evento}** criada e seu voto foi computado!"
                )

                # Vota nos adicionais
                for ev_nome in outros_eventos:
                    registrar_participante(eventos_map[ev_nome], nome_criador)

                st.toast("Sucesso total!", icon="🎉")
                time.sleep(2)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(
                    f"❌ {nome_criador}, a ideia **{nome_novo_evento}** já existe! Vote nela na coluna ao lado."
                )

# -------------------- TABELA DE PARTICIPANTES --------------------
st.divider()
st.subheader("👥 Participantes que já contribuíram")
participantes = listar_participantes_unicos()

if participantes:
    df = pd.DataFrame(participantes)
    df["participant_name"] = df["participant_name"].str.title()
    st.metric("Total de Jovens", len(df))
    st.dataframe(
        df.rename(columns={"participant_name": "Nome"}),
        width='stretch'=True,
        hide_index=True,
    )
else:
    st.info("Aguardando primeira contribuição...")
