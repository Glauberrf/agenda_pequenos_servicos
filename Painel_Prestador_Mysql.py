import streamlit as st
import mysql.connector
import hashlib
from datetime import datetime, time, timedelta, date
from streamlit_calendar import calendar

st.set_page_config(page_title="Agenda Compartilhada", layout="wide")

# =============================
# DATABASE CONFIG
# =============================

DB_CONFIG = {
    "host": st.secrets["db"]["host"],
    "user": st.secrets["db"]["user"],
    "password": st.secrets["db"]["password"],
    "database": st.secrets["db"]["database"],
    "port": st.secrets["db"]["port"]
}

# =============================
# DATABASE
# =============================

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# =============================
# UTILS
# =============================

def timedelta_to_time(td):
    seconds = int(td.total_seconds())
    return time(seconds // 3600, (seconds % 3600) // 60)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =============================
# AUTH
# =============================

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

# =============================
# EVENTS
# =============================

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
        event_date=%s,
        start_time=%s,
        end_time=%s,
        title=%s,
        description=%s,
        chat_id=%s,
        name=%s
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

# =============================
# DISPONIBILIDADE
# =============================

def inserir_disponibilidade(periodo, data, horario, disponibilidade):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO agenda (periodo,data,horario,disponibilidade)
        VALUES (%s,%s,%s,%s)
    """, (periodo, data, horario, disponibilidade))

    conn.commit()

    cur.close()
    conn.close()


def listar_disponibilidade():

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM agenda ORDER BY data, horario")

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

# =============================
# SESSION
# =============================

st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("mode", "idle")
st.session_state.setdefault("selected_event", None)
st.session_state.setdefault("selected_date", None)

# =============================
# LOGIN
# =============================

if not st.session_state.logged_in:

    st.title("Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if authenticate(username, password):

            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()

        else:
            st.error("Usuário ou senha inválidos")

    st.stop()

# =============================
# MENU
# =============================

st.sidebar.title("Menu")

pagina = st.sidebar.selectbox(
    "Selecionar página",
    ["Agenda de Eventos", "Horários Disponíveis"]
)

# =====================================================
# PAGINA 1 - EVENTOS
# =====================================================

if pagina == "Agenda de Eventos":

    st.title("Agenda Compartilhada")

    col_cal, col_form = st.columns([2,1])

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

    with col_cal:

        cal = calendar(
            events=calendar_events,
            options={"initialView": "dayGridMonth","selectable": True}
        )

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

    with col_form:

        st.subheader("Ações")

        if st.session_state.mode == "new":

            st.info(f"Novo evento em {st.session_state.selected_date}")

            with st.form("novo_evento"):

                d = st.date_input("Data", st.session_state.selected_date)

                s = st.time_input("Início", time(9,0))

                e = st.time_input("Fim", time(10,0))

                titulo = st.text_input("Título")

                desc = st.text_area("Descrição")

                chat = st.text_input("Chat ID")

                nome = st.text_input("Nome")

                if st.form_submit_button("Salvar"):

                    add_event({
                        "event_date": d,
                        "start_time": s,
                        "end_time": e,
                        "title": titulo,
                        "description": desc,
                        "chat_id": chat,
                        "name": nome,
                        "created_by": st.session_state.username
                    })

                    st.session_state.mode = "idle"
                    st.rerun()

        elif st.session_state.mode == "edit":

            ev = st.session_state.selected_event

            with st.form("editar_evento"):

                d = st.date_input("Data", ev["event_date"])

                s = st.time_input("Inicio", timedelta_to_time(ev["start_time"]))

                e = st.time_input("Fim", timedelta_to_time(ev["end_time"]))

                titulo = st.text_input("Título", ev["title"])

                desc = st.text_area("Descrição", ev["description"])

                chat = st.text_input("Chat ID", ev["chat_id"])

                nome = st.text_input("Nome", ev["name"])

                if st.form_submit_button("Atualizar"):

                    update_event(ev["id"],{
                        "event_date": d,
                        "start_time": s,
                        "end_time": e,
                        "title": titulo,
                        "description": desc,
                        "chat_id": chat,
                        "name": nome
                    })

                    st.session_state.mode = "idle"
                    st.rerun()

                if st.form_submit_button("Excluir"):

                    delete_event(ev["id"])

                    st.session_state.mode = "idle"
                    st.rerun()

        else:

            st.write("Clique em um dia ou evento no calendário.")

# =====================================================
# PAGINA 2 - DISPONIBILIDADE
# =====================================================

# =====================================================
# UTILS PARA HORARIO
# =====================================================

def timedelta_to_time(td):
    seconds = int(td.total_seconds())
    return time(seconds // 3600, (seconds % 3600) // 60)


def timedelta_to_str(td):
    seconds = int(td.total_seconds())
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h:02}:{m:02}"


# =====================================================
# DISPONIBILIDADE CRUD
# =====================================================

def atualizar_disponibilidade(id, periodo, data, horario, disponibilidade):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE agenda
        SET periodo=%s, data=%s, horario=%s, disponibilidade=%s
        WHERE id=%s
    """,(periodo,data,horario,disponibilidade,id))

    conn.commit()

    cur.close()
    conn.close()


def excluir_disponibilidade(id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM agenda WHERE id=%s",(id,))

    conn.commit()

    cur.close()
    conn.close()


# =====================================================
# PAGINA 2
# =====================================================

if pagina == "Horários Disponíveis":

    st.title("Cadastro de Horários Disponíveis")

    st.session_state.setdefault("edit_disp", None)

    col1, col2 = st.columns([1,1])

    # =========================
    # INSERIR
    # =========================

    with col1:

        if st.session_state.edit_disp is None:

            st.subheader("Inserir horário")

            with st.form("novo_horario"):

                periodo = st.selectbox(
                    "Período",
                    ["manha","tarde","noite"]
                )

                data = st.date_input("Data")

                horario = st.time_input("Horário")

                disponibilidade = st.selectbox(
                    "Disponibilidade",
                    ["sim","nao"]
                )

                if st.form_submit_button("Salvar"):

                    inserir_disponibilidade(
                        periodo,
                        data,
                        horario,
                        disponibilidade
                    )

                    st.success("Horário cadastrado")

                    st.rerun()

        # =========================
        # EDITAR
        # =========================

        else:

            registro = st.session_state.edit_disp

            st.subheader("Editar horário")

            horario_convertido = (
                timedelta_to_time(registro["horario"])
                if isinstance(registro["horario"], timedelta)
                else registro["horario"]
            )

            with st.form("editar_horario"):

                periodo = st.selectbox(
                    "Período",
                    ["manha","tarde","noite"],
                    index=["manha","tarde","noite"].index(registro["periodo"])
                )

                data = st.date_input(
                    "Data",
                    registro["data"]
                )

                horario = st.time_input(
                    "Horário",
                    horario_convertido
                )

                disponibilidade = st.selectbox(
                    "Disponibilidade",
                    ["sim","nao"],
                    index=["sim","nao"].index(registro["disponibilidade"])
                )

                if st.form_submit_button("Atualizar"):

                    atualizar_disponibilidade(
                        registro["id"],
                        periodo,
                        data,
                        horario,
                        disponibilidade
                    )

                    st.session_state.edit_disp = None

                    st.success("Atualizado")

                    st.rerun()

                if st.form_submit_button("Excluir"):

                    excluir_disponibilidade(registro["id"])

                    st.session_state.edit_disp = None

                    st.success("Excluído")

                    st.rerun()

    # =========================
    # LISTA
    # =========================

    with col2:

        st.subheader("Horários cadastrados")

        dados = listar_disponibilidade()

        for row in dados:

            colA, colB = st.columns([4,1])

            with colA:

                horario_txt = (
                    timedelta_to_str(row["horario"])
                    if isinstance(row["horario"], timedelta)
                    else row["horario"].strftime("%H:%M")
                )

                st.write(
                    f"📅 {row['data']} | ⏰ {horario_txt} | {row['periodo']} | {row['disponibilidade']}"
                )

            with colB:

                if st.button("Editar", key=f"edit_{row['id']}"):

                    st.session_state.edit_disp = row

                    st.rerun()