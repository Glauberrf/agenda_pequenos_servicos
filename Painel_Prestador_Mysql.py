import streamlit as st
import mysql.connector
import hashlib
from datetime import datetime, time, timedelta
from streamlit_calendar import calendar
import unicodedata

# ================= CONFIG =================
st.set_page_config("Agenda Profissional", layout="wide")

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

def conn():
    return mysql.connector.connect(**DB_CONFIG)

# ================= UTILS =================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def td_to_time(td):
    sec = int(td.total_seconds())
    return time(sec//3600, (sec%3600)//60)

def td_to_str(td):
    sec = int(td.total_seconds())
    return f"{sec//3600:02}:{(sec%3600)//60:02}"

def norm_periodo(p):
    p = unicodedata.normalize("NFKD",(p or "").lower()).encode("ASCII","ignore").decode("ASCII")
    return p if p in ["manha","tarde","noite"] else "manha"

def gerar_cor(nome):
    cores = ["#FF6B6B","#4ECDC4","#1A535C","#FFA600","#6A4C93","#2EC4B6"]
    return cores[hash(nome) % len(cores)]

# ================= AUTH =================
def login(u,p):
    c=conn();cur=c.cursor()
    cur.execute("SELECT id FROM users WHERE username=%s AND password_hash=%s",(u,hash_password(p)))
    r=cur.fetchone()
    cur.close();c.close()
    return r

def create_user(u,p):
    c=conn();cur=c.cursor()
    cur.execute("INSERT INTO users (username,password_hash) VALUES (%s,%s)",(u,hash_password(p)))
    c.commit();cur.close();c.close()

# ================= EVENTS =================
def get_events():
    c=conn();cur=c.cursor(dictionary=True)
    cur.execute("SELECT * FROM events")
    r=cur.fetchall()
    cur.close();c.close()
    return r

def add_event(d):
    c=conn();cur=c.cursor()
    cur.execute("""INSERT INTO events
    (event_date,start_time,end_time,title,description,chat_id,name,created_by)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",tuple(d.values()))
    c.commit();cur.close();c.close()

def upd_event(id,d):
    c=conn();cur=c.cursor()
    cur.execute("""UPDATE events SET
    event_date=%s,start_time=%s,end_time=%s,
    title=%s,description=%s,chat_id=%s,name=%s
    WHERE id=%s""",(*d.values(),id))
    c.commit();cur.close();c.close()

def del_event(id):
    c=conn();cur=c.cursor()
    cur.execute("DELETE FROM events WHERE id=%s",(id,))
    c.commit();cur.close();c.close()

# ================= DISP =================
def list_disp():
    c=conn();cur=c.cursor(dictionary=True)
    cur.execute("SELECT * FROM agenda ORDER BY data, horario")
    r=cur.fetchall()
    cur.close();c.close()
    return r

def add_disp(p,d,h,s):
    c=conn();cur=c.cursor()
    cur.execute("INSERT INTO agenda VALUES (NULL,%s,%s,%s,%s)",(p,d,h,s))
    c.commit();cur.close();c.close()

def upd_disp(id,p,d,h,s):
    c=conn();cur=c.cursor()
    cur.execute("UPDATE agenda SET periodo=%s,data=%s,horario=%s,disponibilidade=%s WHERE id=%s",(p,d,h,s,id))
    c.commit();cur.close();c.close()

def del_disp(id):
    c=conn();cur=c.cursor()
    cur.execute("DELETE FROM agenda WHERE id=%s",(id,))
    c.commit();cur.close();c.close()

# ================= SESSION =================
st.session_state.setdefault("logado",False)
st.session_state.setdefault("modo","idle")
st.session_state.setdefault("evento_sel",None)
st.session_state.setdefault("data_sel",None)
st.session_state.setdefault("edit_disp_data",None)

# ================= LOGIN =================
if not st.session_state.logado:

    tab1,tab2=st.tabs(["Entrar","Cadastrar"])

    with tab1:
        u=st.text_input("Usuário",key="l_u")
        p=st.text_input("Senha",type="password",key="l_p")

        if st.button("Entrar",key="btn_l"):
            if login(u,p):
                st.session_state.logado=True
                st.session_state.user=u
                st.rerun()
            else:
                st.error("Login inválido")

    with tab2:
        u=st.text_input("Novo usuário",key="c_u")
        p=st.text_input("Senha",type="password",key="c_p")

        if st.button("Cadastrar",key="btn_c"):
            try:
                #Esse funnção está comentada para que não seja possivel cadastrar no momento, para evitar que pessoas criem usuários sem autorização. Para criar um usuário, descomente a linha abaixo e rode o código, depois comente novamente.
                #create_user(u,p)
                st.success("Usuário criado")
            except:
                st.error("Já existe")

    st.stop()

# ================= MENU =================
pg=st.sidebar.selectbox("Menu",["Agenda","Disponibilidade"])

# ================= AGENDA =================
if pg=="Agenda":

    col1,col2=st.columns([2,1])
    events_db=get_events()

    def conflito(n_ini,n_fim):
        for ev in events_db:
            ini=datetime.combine(ev["event_date"],td_to_time(ev["start_time"]))
            fim=datetime.combine(ev["event_date"],td_to_time(ev["end_time"]))
            if n_ini < fim and n_fim > ini:
                return True
        return False

    cal_events=[{
        "id":e["id"],
        "title":f"{e['title']} - {e['name']}",
        "start":datetime.combine(e["event_date"],td_to_time(e["start_time"])).isoformat(),
        "end":datetime.combine(e["event_date"],td_to_time(e["end_time"])).isoformat(),
        "color":gerar_cor(e["name"])
    } for e in events_db]

    with col1:
        cal=calendar(
            events=cal_events,
            options={
                "initialView":"dayGridMonth",
                "locale":"pt-br",
                "firstDay":1,
                "height":650,
                "editable":True,
                "selectable":True
            }
        )

    if cal.get("dateClick"):
        st.session_state.modo="new"
        st.session_state.data_sel=datetime.fromisoformat(cal["dateClick"]["date"]).date()

    if cal.get("eventClick"):
        st.session_state.modo="edit"
        st.session_state.evento_sel=next(e for e in events_db if e["id"]==int(cal["eventClick"]["event"]["id"]))

    # DRAG DROP
    if cal.get("eventChange"):
        ev_id=int(cal["eventChange"]["event"]["id"])
        ns=datetime.fromisoformat(cal["eventChange"]["event"]["start"])
        ne=datetime.fromisoformat(cal["eventChange"]["event"]["end"])

        if conflito(ns,ne):
            st.error("Conflito de horário")
        else:
            ev=next(e for e in events_db if e["id"]==ev_id)
            upd_event(ev_id,{
                "event_date":ns.date(),
                "start_time":ns.time(),
                "end_time":ne.time(),
                "title":ev["title"],
                "description":ev["description"],
                "chat_id":ev["chat_id"],
                "name":ev["name"]
            })
            st.rerun()

    with col2:

        if st.session_state.modo=="new":
            with st.form("f_new"):
                nome=st.text_input("Nome",key="n1")
                d=st.date_input("Data",st.session_state.data_sel,key="d1")
                s=st.time_input("Inicio",key="s1")
                e=st.time_input("Fim",key="e1")
                t = nome#replica o nome no título para facilitar a visualização no calendário
                #t=st.text_input("Nome",key="t1")
                desc=st.text_area("Procedimento",key="ds1")
                chat=st.text_input("Chat",key="c1")

                if st.form_submit_button("Salvar"):
                    ini=datetime.combine(d,s)
                    fim=datetime.combine(d,e)

                    if conflito(ini,fim):
                        st.error("Já existe evento nesse horário")
                    else:
                        add_event({
                            "event_date":d,"start_time":s,"end_time":e,
                            "title":t,"description":desc,
                            "chat_id":chat,"name":nome,
                            "created_by":st.session_state.user
                        })
                        st.session_state.modo="idle"
                        st.rerun()

        elif st.session_state.modo=="edit":

            ev=st.session_state.evento_sel

            with st.form("f_edit"):
                nome=st.text_input("Nome",ev["name"],key="n2")
                d=st.date_input("Data",ev["event_date"],key="d2")
                s=st.time_input("Inicio",td_to_time(ev["start_time"]),key="s2")
                e=st.time_input("Fim",td_to_time(ev["end_time"]),key="e2")
                t = nome#replica o nome no título para facilitar a visualização no calendário
                #t=st.text_input("Nome",ev["title"],key="t2")
                desc=st.text_area("Procedimento",ev["description"],key="ds2")
                chat=st.text_input("Chat",ev["chat_id"],key="c2")

                if st.form_submit_button("Atualizar"):
                    upd_event(ev["id"],{
                        "event_date":d,"start_time":s,"end_time":e,
                        "title":t,"description":desc,"chat_id":chat,"name":nome
                    })
                    st.session_state.modo="idle"
                    st.rerun()

                if st.form_submit_button("Excluir"):
                    del_event(ev["id"])
                    st.session_state.modo="idle"
                    st.rerun()

# ================= DISP =================
if pg=="Disponibilidade":

    col1,col2=st.columns(2)

    with col1:

        if st.session_state.edit_disp_data is None:

            with st.form("disp_new"):
                p=st.selectbox("Periodo",["manha","tarde","noite"],key="p1")
                d=st.date_input("Data",key="d3")
                h=st.time_input("Hora",key="h1")
                s=st.selectbox("Disponível",["sim","nao"],key="s3")

                if st.form_submit_button("Salvar"):
                    add_disp(p,d,h,s)
                    st.rerun()

        else:

            r=st.session_state.edit_disp_data

            with st.form("disp_edit"):
                lista=["manha","tarde","noite"]
                p=st.selectbox("Periodo",lista,index=lista.index(norm_periodo(r["periodo"])),key="p2")
                d=st.date_input("Data",r["data"],key="d4")
                h=st.time_input("Hora",
                    td_to_time(r["horario"]) if isinstance(r["horario"],timedelta) else r["horario"],
                    key="h2")
                s=st.selectbox("Disponível",["sim","nao"],
                    index=["sim","nao"].index(r["disponibilidade"]),key="s4")

                if st.form_submit_button("Atualizar"):
                    upd_disp(r["id"],p,d,h,s)
                    st.session_state.edit_disp_data=None
                    st.rerun()

                if st.form_submit_button("Excluir"):
                    del_disp(r["id"])
                    st.session_state.edit_disp_data=None
                    st.rerun()

    with col2:

        for row in list_disp():

            colA,colB=st.columns([4,1])

            with colA:
                h=td_to_str(row["horario"]) if isinstance(row["horario"],timedelta) else row["horario"].strftime("%H:%M")
                st.write(f"{row['data']} | {h} | {row['periodo']} | {row['disponibilidade']}")

            with colB:
                if st.button("Editar",key=f"ed_{row['id']}"):
                    st.session_state.edit_disp_data=row
                    st.rerun()