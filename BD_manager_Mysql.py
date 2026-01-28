import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict
import streamlit as st



DB_CONFIG = {
    "host": st.secrets["db"]["host"],
    "user": st.secrets["db"]["user"],
    "password": st.secrets["db"]["password"],
    "database": st.secrets["db"]["database"],
    "port": st.secrets["db"]["port"]
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def inserir_acompanhamento(chat_id: int, status: str, nome: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO acompanhamento (chat_id, status, nome)
        VALUES (%s, %s, %s)
    """

    cursor.execute(query, (chat_id, status, nome))
    conn.commit()

    cursor.close()
    conn.close()

def atualizar_acompanhamento(chat_id: int, campo: str, information: str) -> bool:
    campos_permitidos = {"status", "nome", "data_event", "time_event"}

    if campo not in campos_permitidos:
        raise ValueError("Campo não permitido")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM acompanhamento
        WHERE chat_id = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (chat_id,)
    )

    row = cursor.fetchone()

    if row is None:
        cursor.close()
        conn.close()
        return False

    ultimo_id = row[0]

    query = f"UPDATE acompanhamento SET {campo} = %s WHERE id = %s"
    cursor.execute(query, (information, ultimo_id))

    conn.commit()
    cursor.close()
    conn.close()
    return True

def buscar_ultimo_chat(chat_id: int) -> Optional[Dict[str, object]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, chat_id, status, nome, data_event, time_event
        FROM acompanhamento
        WHERE chat_id = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (chat_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row

def inserir_evento(
    event_date,
    start_time,
    end_time,
    title,
    description,
    chat_id,
    name,
    created_by
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO events
        (event_date, start_time, end_time, title, description, chat_id, name, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (event_date, start_time, end_time, title, description, chat_id, name, created_by)
    )

    conn.commit()
    cursor.close()
    conn.close()
