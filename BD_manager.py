import sqlite3
from typing import Optional, Dict, List, Any

db_path = "agenda.db" 

def inserir_acompanhamento(chat_id: int, status: str, nome: str) -> None:
    """
    Insere um registro na tabela usuarios.
    
    :param db_path: Caminho do banco de dados SQLite
    :param chat_id: ID do chat (ex: Telegram)
    :param status: Status do usuário
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        INSERT INTO acompanhamento (chat_id, status, nome)
        VALUES (?, ?, ?)
    """

    cursor.execute(query, (chat_id, status, nome))
    conn.commit()
    conn.close()




def atualizar_acompanhamento(
    chat_id: int,
    campo: str,
    information: str
) -> bool:
    """
    Atualiza o status do último registro (maior id) de um chat_id.
    
    :param db_path: Caminho do banco SQLite
    :param chat_id: Chat ID a ser atualizado
    :param novo_status: Novo status
    :return: True se atualizou, False se não encontrou registro
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Localiza o último registro do chat_id
    cursor.execute(
        """
        SELECT id
        FROM acompanhamento
        WHERE chat_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (chat_id,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return False

    ultimo_id = row[0]

    # Atualiza apenas o registro mais recente
    cursor.execute(
        f"UPDATE acompanhamento SET {campo} = ? WHERE id = ?"
,
        (information, ultimo_id)
    )

    conn.commit()
    conn.close()
    return True

#atualizar_acompanhamento(614413127, "nome","zézé")


def buscar_ultimo_chat(
    chat_id: int
) -> Optional[Dict[str, object]]:
    """
    Retorna o último registro (maior id) de um chat_id.
    
    :param db_path: Caminho do banco SQLite
    :param chat_id: Chat ID a ser consultado
    :return: Dicionário com os dados ou None se não encontrar
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, chat_id, status, nome, data_event, time_event, horarios_disponiveis
        FROM acompanhamento
        WHERE chat_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (chat_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "chat_id": row["chat_id"],
        "status": row["status"],
        "nome": row["nome"],
        "data_event": row["data_event"],
        "time_event": row["time_event"],
        "horarios_disponiveis": row["horarios_disponiveis"],

    }

#print(buscar_ultimo_chat(614413127)['horarios_disponiveis'])

def inserir_evento(event_date, start_time, end_time, title, description, chat_id, name, created_by) -> None:
    """
    Insere um registro na tabela usuarios.
    
    :param db_path: Caminho do banco de dados SQLite
    :param chat_id: ID do chat (ex: Telegram)
    :param status: Status do usuário
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        INSERT INTO events (event_date, start_time, end_time, title, description, chat_id, name, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(query, (event_date, start_time, end_time, title, description, chat_id, name, created_by))
    conn.commit()
    conn.close()

#--- Query agenda
def listar_agenda(campo: str, parametro: Any) -> List[Dict[str, Any]]:
    colunas_permitidas = {"id","periodo", "data", "nome", "status"}  # ajuste conforme sua tabela

    if campo not in colunas_permitidas:
        raise ValueError("Campo inválido para consulta.")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = f"SELECT * FROM agenda WHERE {campo} = ?;"
        cursor.execute(query, (parametro,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except sqlite3.Error as e:
        print(f"Erro na consulta: {e}")
        return []

    finally:
        if conn:
            conn.close()


'''a = listar_agenda("periodo","manhã")
print(a)
print(a[1]['horario'])

for z in a:
    print(z['horario'])'''