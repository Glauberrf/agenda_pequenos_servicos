from typing import Optional, Dict, List, Any

import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "seu_usuario",
    "password": "sua_senha",
    "database": "seu_banco",
    "port": 3306
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
        created_by,
        acompanhamento_id
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO events
        (event_date, start_time, end_time, title, description, chat_id, name, created_by, acompanhamento_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (event_date, start_time, end_time, title, description, chat_id, name, created_by, acompanhamento_id)
    )

    conn.commit()
    cursor.close()
    conn.close()


# --- Query agenda
def listar_agenda(campo: str, parametro: Any) -> List[Dict[str, Any]]:
    colunas_permitidas = {"id", "periodo", "data", "nome", "status"}  # ajuste conforme sua tabela

    if campo not in colunas_permitidas:
        raise ValueError("Campo inválido para consulta.")

    try:
        conn = get_connection()

        cursor = conn.cursor(dictionary=True)

        query = f"SELECT * FROM agenda WHERE {campo} = %s;"
        cursor.execute(query, (parametro,))

        rows = cursor.fetchall()
        return rows

    except mysql.connector.Error as e:
        print(f"Erro na consulta: {e}")
        return []

    finally:
        if conn:
            conn.close()


def limpar_sessoes_expiradas(limite: Any) -> List[int]:
    conn = get_connection()
    ids_removidos = []

    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Buscar acompanhamentos vencidos
        sql_select = """
            SELECT id
            FROM acompanhamento
            WHERE status != 10
            AND created_at <= %s
        """
        cursor.execute(sql_select, (limite,))
        registros = cursor.fetchall()

        if not registros:
            cursor.close()
            conn.close()
            return []

        ids = [r["id"] for r in registros]
        ids_removidos = ids

        # Format for IN clause
        format_strings = ','.join(['%s'] * len(ids))

        # 2. Remover eventos relacionados
        # Como existe ON DELETE CASCADE na tabela events, não é estritamente necessário deletar manualmente,
        # mas se quiser garantir ou se o banco não suportar FKs corretamente, pode manter.
        # Com ON DELETE CASCADE, deletar o pai (acompanhamento) já deleta os filhos (events).
        # Vou manter a deleção explicita para garantir compatibilidade com o código anterior,
        # mas a constraint FK já faria isso.
        sql_delete_events = f"DELETE FROM events WHERE acompanhamento_id IN ({format_strings})"
        cursor.execute(sql_delete_events, tuple(ids))

        # 3. Remover acompanhamentos
        sql_delete_acomp = f"DELETE FROM acompanhamento WHERE id IN ({format_strings})"
        cursor.execute(sql_delete_acomp, tuple(ids))

        conn.commit()
        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"Erro: {e}")
        if conn and conn.is_connected():
            conn.rollback()
            conn.close()

    return ids_removidos
