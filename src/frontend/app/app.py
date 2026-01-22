import time
from sqlalchemy.exc import IntegrityError
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
    except Exception:
        session.rollback()
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
    help="Para manter a votação organizada, envie uma ideia de cada vez. Você pode enviar quantas quiser!",
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
        st.warning("💡 **Você quer apenas votar em ideias existentes?**")
        st.info(
            f"Olá **{nome_criador}**, notamos que você não propôs uma ideia nova. "
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
                f"❌ {nome_criador}, a ideia **{nome_novo_evento}** já foi criada por outro jovem. Utilize a seção logo abaixo: **🗳️ Votar em Ideias de Eventos**!"
            )
            st.info(
                f"💡 {nome_criador} Que tal tentar propor uma ideia diferente de **{nome_novo_evento}**?"
            )

        if votos_ad_duplicados:
            lista_dup = ", ".join(votos_ad_duplicados)
            st.warning(
                f"⚠️ {nome_criador}, você já tinha votado em: **{lista_dup}**. Esses votos não foram repetidos."
            )

        if sucesso_criacao:
            st.success(
                f"✅ {nome_criador}, a ideia **{nome_novo_evento}** foi registrada com sucesso. Obrigado por sua contribuição!"
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
    "🎉 Selecione as ideias",
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
                f"✅ **{nome_votante}**, novo(s) voto(s) registrado(s) para: **{lista_suc}**!"
            )
            st.cache_data.clear()
            time.sleep(10.0)
            st.rerun()

        elif votos_duplicados:
            st.info(
                f"💡 {nome_votante} como você já votou nessas ideias, que tal propor uma nova na sessão logo acima: **➕ Criar Nova Ideia de Evento**?"
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
