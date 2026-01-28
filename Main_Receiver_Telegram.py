from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)
from datetime import datetime
import streamlit as st

from BD_manager import inserir_acompanhamento, buscar_ultimo_chat, atualizar_acompanhamento, inserir_evento

#from BD_manager_Mysql import inserir_acompanhamento, buscar_ultimo_chat, atualizar_acompanhamento, inserir_evento

#TOKEN = ""
TOKEN = st.secrets["api"]["token"]


# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Eu sou um bot em Python. Envie qualquer mensagem."

        
    )

# Recebe mensagens de texto
async def receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_recebido = update.message.text
    chat_id = update.effective_chat.id
    name = update.effective_chat.full_name
    print(chat_id, name)

    print(texto_recebido)
    if(texto_recebido == "Oi"):
        resposta = f"Olá! você gostaria de agendar um horario?\n Digite\n1-SIM\n2-NÃO"
        inserir_acompanhamento(chat_id, "1", name)


        #resposta = f"Você escreveu: {texto_recebido}"
        #await update.message.reply_text(resposta)
    #print("ultimo Chat: ",buscar_ultimo_chat(chat_id)['status'])
    elif(texto_recebido == "1" and buscar_ultimo_chat(chat_id)['status'] == "1") :
        atualizar_acompanhamento(chat_id, "status", "2")
        resposta = f"Qual o dia você gostaria de agendar ?\nDias disponiveis\n1-27/02/2026\n2-23/04/2026\n3-10/05/2026\nDigite a data neste formato dd/mm/yyyy"
        
    
    elif(buscar_ultimo_chat(chat_id)['status'] == "2") :
        #converter data
        data_original = texto_recebido

        
        try:
            data_convertida = datetime.strptime(data_original, "%d/%m/%Y").strftime("%Y-%m-%d")
            datetime.strptime(data_convertida, "%Y-%m-%d")
            atualizar_acompanhamento(chat_id, "status", "3")
            atualizar_acompanhamento(chat_id, "data_event", data_convertida)
            resposta = f"Agendado para o dia 27/02/2026\nQual o horario ?"            
        except ValueError:
            resposta = f"A data que você digitou não está no formato correto.\nDigite a data no seguinte formato dd/mm/yyyy"  


        

            
        

    elif(buscar_ultimo_chat(chat_id)['status'] == "3") :
        atualizar_acompanhamento(chat_id, "status", "10")
        atualizar_acompanhamento(chat_id, "time_event", texto_recebido)

        resposta = f"Agendado para {buscar_ultimo_chat(chat_id)["data_event"]} as {buscar_ultimo_chat(chat_id)["time_event"]}\n obrigado !"
        
        inserir_evento(buscar_ultimo_chat(chat_id)["data_event"],buscar_ultimo_chat(chat_id)["time_event"],"+ 30 minutos","Padão Titulo","Padrão descrição",chat_id,name,"Telegram")



    elif(texto_recebido == "Quem é você?"):
        resposta = f"Eu sou um Bot de agendamento!"
        #await update.message.reply_text(resposta)
    #resposta = f"Você escreveu: {texto_recebido}"

    else:
        resposta = f"Parece que você não digitou uma opção válida."
    await update.message.reply_text(resposta)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))

    # Mensagens de texto
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receber_mensagem)
    )

    print("Bot em execução...")
    app.run_polling()

if __name__ == "__main__":
    main()
