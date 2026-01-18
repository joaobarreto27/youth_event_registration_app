import time
from psycopg2 import IntegrityError
from sqlalchemy import text
import streamlit as st
import pandas as pd

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Registro de Ideia de Eventos", page_icon="🎯", layout="wide"
)

st.header("🎯 Formulário de Registro de Ideia de Eventos Jovens AduPno")
st.divider()

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
        id_event = result.fetchone()[0]  # pyright: ignore[reportOptionalSubscript]

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

# Carrega dados para os selects
eventos = listar_eventos_registrados()
eventos_map = {e["event_name"]: e["id_event"] for e in eventos}

# -------------------- COLUNA VOTAR --------------------

st.subheader("🗳️ Votar em Ideias de Eventos")
st.markdown("Vote nas ideias de eventos que você mais gostaria que tivesse!")
nome_votante = st.text_input(
    "👤 Seu nome", placeholder="Digite seu nome completo", key="nome_votante"
)

eventos_selecionados = st.multiselect(
    "🎉 Selecione as ideias",
    options=list(eventos_map.keys()),
    placeholder="Escolha uma ou mais ideias",
    key="eventos_selecionados",
)

if st.button("✅ Confirmar Voto", width="stretch"):
    if not nome_votante.strip():
        st.error("❌ Por favor, informe seu nome.")
    elif not eventos_selecionados:
        st.error(f"❌ **{nome_votante}** selecione ao menos uma ideia para votar!")
    else:
        votos_com_sucesso = []
        votos_duplicados = []
        erros = []

        for ev_nome in eventos_selecionados:
            status = registrar_participante(eventos_map[ev_nome], nome_votante)
            if status == "sucesso":
                votos_com_sucesso.append(ev_nome)
            elif status == "duplicado":
                votos_duplicados.append(ev_nome)
                lista_formatada = ", ".join(votos_duplicados)
                st.warning(
                    f"⚠️ **{nome_votante}**, você já tinha votado em: {lista_formatada}. Esses votos não foram repetidos."
                )
            else:
                erros.append(f"{ev_nome} ({status})")

        for erro in erros:
            lista_formatada = ", ".join(votos_duplicados)
            st.warning(
                f"⚠️ **{nome_votante}**, você já tinha nestas opções esses votos não foram repetidos."
            )

        if votos_com_sucesso:
            lista_sucesso = ", ".join(votos_com_sucesso)
            st.success(
                f"✅ **{nome_votante}** novo(s) voto(s) registrado(s) com sucesso!"
            )
            st.cache_data.clear()
            time.sleep(5.0)

        elif votos_duplicados:
            st.info(
                "💡 Como você já votou nessas ideias, que tal propor uma nova abaixo?"
            )

# -------------------- COLUNA - CRIAR --------------------
st.divider()
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

outros_eventos = st.multiselect(
    "🎉 Votar em outras ideias de eventos também (opcional)",
    options=list(eventos_map.keys()),
    placeholder="Selecione uma ou mais ideias de eventos",
    key="outros_eventos_voto",
)

if st.button("🚀 Criar Ideia de Evento e Votar", width="stretch"):
    if not nome_criador.strip() or not nome_novo_evento.strip():
        st.error("❌ Preencha seu nome e o nome da ideia.")
    else:
        sucesso, id_novo = criar_evento(nome_novo_evento, nome_criador)

        if sucesso:
            st.success(
                f"✅ {nome_criador} a sua ideia de evento **{nome_novo_evento}** foi registrada e seu voto foi computado. Muito obrigado!"
            )

            # Vota nos adicionais
            for ev_nome in outros_eventos:
                registrar_participante(eventos_map[ev_nome], nome_criador)

            st.success("✅ Sucesso total!", icon="🎉")
            time.sleep(2)
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(
                f"❌ {nome_criador} ocorreu um erro ao criar sua ideia **{nome_novo_evento}**, pois esta ideia já foi criada por outro jovem, vote nesta ideia **{nome_novo_evento}** na sessão abaixo **(🗳️ Votar em Ideias de Eventos)**."
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
        width="stretch",
        hide_index=True,
    )
else:
    st.warning("⚠️ Aguardando primeira contribuição...")
