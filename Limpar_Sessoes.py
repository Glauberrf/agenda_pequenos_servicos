#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from BD_manager_Mysql import limpar_sessoes_expiradas

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "log_limpeza.txt")

def log_msg(msg):
    """Escreve a mensagem no arquivo de log e imprime no console."""
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{msg}\n")
        print(msg)
    except Exception as e:
        print(f"Erro ao escrever no log: {e}")

def limpar_registros_expirados():
    agora = datetime.now()
    limite = agora - timedelta(minutes=2)

    try:
        ids_removidos = limpar_sessoes_expiradas(limite)

        if ids_removidos:
            ids_str = ",".join(map(str, ids_removidos))
            log_msg(f"[{agora.strftime('%Y-%m-%d %H:%M:%S')}] 🗑️ Removidos IDs: {ids_str}")
        else:
            pass
            
    except Exception as e:
        log_msg(f"[{agora.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro: {e}")

if __name__ == "__main__":
    limpar_registros_expirados()