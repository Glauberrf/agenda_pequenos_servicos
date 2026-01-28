import streamlit as st
import mysql.connector
import hashlib
from datetime import date, time

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Agenda Compartilhada", layout="centered")

DB_CONFIG = {
    "host": st.secrets["db"]["host"],
    "user": st.secrets["db"]["user"],
    "password": st.secrets["db"]["password"],
    "database": st.secrets["db"]["database"],
    "port": st.secrets["db"]["port"]
}


# =========================
# DATABASE
# =========================
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# =========================
# AUTH
# =========================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (username, hash_password(password))
    )
    conn.commit()
    cur.close()
    conn.close()

def authenticate(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM users WHERE username=%s AND password_hash=%s",
        (username, hash_password(password))
    )
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None

# =========================
# EVENTS
# =========================
def add_event(event_date, start_time, end_time, title, description, chat_id, name, created_by):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events
        (event_date, start_time, end_time, title, description, chat_id, name, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        event_date, start_time, end_time, title, description, chat_id, name, created_by
    ))
    conn.commit()
    cur.close()
    conn.close()

def delete_event(event_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id=%s", (event_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_events():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, event_date, start_time, end_time, title, description,
               chat_id, name, created_by
        FROM events
        ORDER BY event_date, start_time
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# =========================
# SESSION
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# LOGIN
# =========================
if not st.session_state.logged_in:
    st.title("Login")

    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])

    with tab1:
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

    with tab2:
        new_user = st.text_input("Novo usuário")
        new_pass = st.text_input("Nova senha", type="password")

        if st.button("Cadastrar"):
            try:
                create_user(new_user, new_pass)
                st.success("Usuário criado com sucesso")
            except mysql.connector.errors.IntegrityError:
                st.error("Usuário já existe")

    st.stop()

# =========================
# APP
# =========================
st.title("📅 Agenda Compartilhada")
st.write(f"Usuário logado: **{st.session_state.username}**")

# =========================
# ADD EVENT
# =========================
with st.expander("➕ Novo Evento"):
    col1, col2 = st.columns(2)

    with col1:
        event_date = st.date_input("Data", value=date.today())
        start_time = st.time_input("Hora início", value=time(9, 0))
        end_time = st.time_input("Hora fim", value=time(10, 0))

    with col2:
        title = st.text_input("Título")
        description = st.text_area("Descrição")
        chat_id = st.text_input("Chat ID")
        name = st.text_input("Nome")

    if st.button("Salvar evento"):
        if title and chat_id and name:
            add_event(
                event_date,
                start_time,
                end_time,
                title,
                description,
                chat_id,
                name,
                st.session_state.username
            )
            st.success("Evento criado")
            st.rerun()
        else:
            st.warning("Preencha todos os campos obrigatórios")

# =========================
# LIST EVENTS
# =========================
st.subheader("📌 Eventos")

events = get_events()

if not events:
    st.info("Nenhum evento cadastrado.")
else:
    for ev in events:
        ev_id, ev_date, start, end, title, desc, chat_id, name, creator = ev

        with st.container(border=True):
            st.markdown(f"""
            **{title}**  
            📅 {ev_date} ⏰ {start} - {end}  
            👤 Nome: {name}  
            💬 Chat ID: {chat_id}  
            ✍ Criado por: {creator}
            """)
            if desc:
                st.caption(desc)

            if st.button("Excluir", key=f"del_{ev_id}"):
                delete_event(ev_id)
                st.rerun()
