from datetime import datetime, timedelta
from BD_manager_Mysql import limpar_sessoes_expiradas

def limpar_registros_expirados():
    agora = datetime.now()
    limite = agora - timedelta(minutes=2)

    ids_removidos = limpar_sessoes_expiradas(limite)

    if not ids_removidos:
        print(f"[{agora}] Nenhum registro para remover.")
    else:
        ids_str = ",".join(map(str, ids_removidos))
        print(f"[{agora}] Removendo acompanhamentos: {ids_str}")
        print(f"[{agora}] Remoção concluída.")

if __name__ == "__main__":
    limpar_registros_expirados()