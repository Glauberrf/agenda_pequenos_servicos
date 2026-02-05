import streamlit as st
import mysql.connector
import hashlib
from datetime import date, time, datetime, timedelta
from streamlit_calendar import calendar

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Agenda Compartilhada", layout="wide")

DB_CONFIG = {
    "host": st.secrets["db"]["host"],
    "user": st.secrets["db"]["user"],
    "password": st.secrets["db"]["password"],
    "database": st.secrets["db"]["database"],
    "port": st.secrets["db"]["port"]
}

# =========================
# UTILS
# =========================
def timedelta_to_time(td):
    seconds = int(td.total_seconds())
    return time(seconds // 3600, (seconds % 3600) // 60)

# =========================
# DATABASE
# =========================
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# =========================
# AUTH
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
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
def get_events():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM events")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def add_event(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events
        (event_date,start_time,end_time,title,description,chat_id,name,created_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, tuple(data.values()))
    conn.commit()
    cur.close()
    conn.close()

def update_event(event_id, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE events SET
        event_date=%s,start_time=%s,end_time=%s,
        title=%s,description=%s,chat_id=%s,name=%s
        WHERE id=%s
    """, (*data.values(), event_id))
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

# =========================
# SESSION
# =========================
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("mode", "idle")
st.session_state.setdefault("selected_event", None)
st.session_state.setdefault("selected_date", None)

# =========================
# LOGIN
# =========================
if not st.session_state.logged_in:
    st.title("🔐 Login")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if authenticate(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            st.rerun()
        else:
            st.error("Credenciais inválidas")
    st.stop()

# =========================
# APP
# =========================
st.title("📅 Agenda Compartilhada")

col_cal, col_form = st.columns([2, 1])

events_db = get_events()

calendar_events = []
for ev in events_db:
    calendar_events.append({
        "id": ev["id"],
        "title": ev["title"],
        "start": datetime.combine(
            ev["event_date"],
            timedelta_to_time(ev["start_time"])
        ).isoformat(),
        "end": datetime.combine(
            ev["event_date"],
            timedelta_to_time(ev["end_time"])
        ).isoformat(),
    })

# =========================
# CALENDAR (LEFT)
# =========================
with col_cal:
    cal = calendar(
        events=calendar_events,
        options={"initialView": "dayGridMonth", "selectable": True},
        custom_css=".fc { font-size: 0.85rem; }"
    )

# =========================
# CALENDAR INTERACTIONS
# =========================
if cal.get("dateClick"):
    st.session_state.mode = "new"
    st.session_state.selected_date = datetime.fromisoformat(
        cal["dateClick"]["date"]
    ).date()

if cal.get("eventClick"):
    st.session_state.mode = "edit"
    st.session_state.selected_event = next(
        e for e in events_db if e["id"] == int(cal["eventClick"]["event"]["id"])
    )

# =========================
# SIDE PANEL (RIGHT)
# =========================
with col_form:
    st.subheader("🛠 Ações")

    # -------------------------
    # NEW EVENT
    # -------------------------
    if st.session_state.mode == "new":
        st.info(f"Novo evento em {st.session_state.selected_date}")

        with st.form("new_event"):
            d = st.date_input("Data", st.session_state.selected_date)
            s = st.time_input("Início", time(9, 0))
            e = st.time_input("Fim", time(10, 0))
            t = st.text_input("Título")
            desc = st.text_area("Descrição")
            chat = st.text_input("Chat ID")
            name = st.text_input("Nome")

            if st.form_submit_button("Salvar"):
                add_event({
                    "event_date": d,
                    "start_time": s,
                    "end_time": e,
                    "title": t,
                    "description": desc,
                    "chat_id": chat,
                    "name": name,
                    "created_by": st.session_state.username
                })
                st.session_state.mode = "idle"
                st.rerun()

    # -------------------------
    # EDIT EVENT
    # -------------------------
    elif st.session_state.mode == "edit":
        ev = st.session_state.selected_event
        st.info(f"Editando: {ev['title']}")

        with st.form("edit_event"):
            d = st.date_input("Data", ev["event_date"])
            s = st.time_input("Início", timedelta_to_time(ev["start_time"]))
            e = st.time_input("Fim", timedelta_to_time(ev["end_time"]))
            t = st.text_input("Título", ev["title"])
            desc = st.text_area("Descrição", ev["description"])
            chat = st.text_input("Chat ID", ev["chat_id"])
            name = st.text_input("Nome", ev["name"])

            if st.form_submit_button("Atualizar"):
                update_event(ev["id"], {
                    "event_date": d,
                    "start_time": s,
                    "end_time": e,
                    "title": t,
                    "description": desc,
                    "chat_id": chat,
                    "name": name
                })
                st.session_state.mode = "idle"
                st.rerun()

            if st.form_submit_button("Excluir"):
                delete_event(ev["id"])
                st.session_state.mode = "idle"
                st.rerun()

    else:
        st.write("⬅️ Clique em um dia ou evento no calendário")

