from BD_manager_Mysql import get_events
from datetime import datetime
from time import sleep
import asyncio
from telegram import Bot
import os
from twilio.rest import Client
from dotenv import load_dotenv
from BD_manager_Mysql import update_events



# ==========================
# Enviar mensagem WhatsApp
# ==========================
def enviar_whatsapp(numero_destino, mensagem):

    # Carrega variáveis do arquivo .env
    load_dotenv()

    # Credenciais Twilio
    ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")




    # Cria cliente Twilio
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    numero_destino = numero_destino.replace("whatsapp:", "")
    message = client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=mensagem,
        to=f"whatsapp:{numero_destino}"
    )

    return message.sid


TOKEN = ""

def enviar_mensagem_telegram(chat_id, mensagem):
    async def enviar_mensagem(chat_id, mensagem):
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=chat_id, text=mensagem)

    # chamada da função
    asyncio.run(enviar_mensagem(chat_id, mensagem))


while True:
    sleep(3600)  # Espera 10 segundos antes de verificar novamente
    events = get_events()

    for event in events:
        #print(f"ID: {event['id']}, Date: {event['event_date']}, Start: {event['start_time']}, End: {event['end_time']}, Title: {event['title']}, Description: {event['description']}, Chat ID: {event['chat_id']}, Name: {event['name']}, Created By: {event['created_by']}")
        #print(event['event_date'],event['start_time'])
        id_envent = event['id']
        event_date = event['event_date']
        start_time = event['start_time']
        name = event['name']
        chat_id = event['chat_id']
        avisos = event['avisos']
        created_by = event['created_by']
        
        # Juntar data + hora em um único datetime
        evento_datetime = datetime.strptime(
            f"{event_date} {start_time}",
            "%Y-%m-%d %H:%M:%S"
        )
        
        agora = datetime.now()  # horário atual

        diferenca = evento_datetime - agora
        horas_faltando = diferenca.total_seconds() / 3600

        #quando faltar 24 horas um aviso será enviado
        if(horas_faltando <= 24 and horas_faltando > 0 and avisos == "0"):

            print(f"Evento em {evento_datetime} - faltam {horas_faltando:.2f} horas")
            if(created_by == "Telegram"):
                mensagem = f"Olá {name}, voce tem um horario agendado dia {event_date} as {start_time}"
                update_events(id_envent, "avisos", "1")
                enviar_mensagem_telegram(str(chat_id), mensagem)
            if(created_by == "Whatsapp"):
                mensagem = f"Olá {name}, voce tem um horario agendado dia {event_date} as {start_time}"
                update_events(id_envent, "avisos", "1")
                enviar_whatsapp(chat_id, mensagem)

        #quando faltar 12 horas um aviso será enviado
        if(horas_faltando <= 12 and horas_faltando > 0 and avisos == "1"):

            print(f"Evento em {evento_datetime} - faltam {horas_faltando:.2f} horas")
            if(created_by == "Telegram"):
                mensagem = f"Olá {name}, voce tem um horario agendado dia {event_date} as {start_time}"
                update_events(id_envent, "avisos", "2")
                enviar_mensagem_telegram(str(chat_id), mensagem)
            if(created_by == "Whatsapp"):
                mensagem = f"Olá {name}, voce tem um horario agendado dia {event_date} as {start_time}"
                update_events(id_envent, "avisos", "2")
                enviar_whatsapp(chat_id, mensagem)


        #quando faltar 3 horas um aviso será enviado
        if(horas_faltando <= 3 and horas_faltando > 0 and avisos == "2"):

            print(f"Evento em {evento_datetime} - faltam {horas_faltando:.2f} horas")
            if(created_by == "Telegram"):
                mensagem = f"Olá {name}, voce tem um horario agendado dia {event_date} as {start_time}"
                update_events(id_envent, "avisos", "3")
                enviar_mensagem_telegram(str(chat_id), mensagem)
            if(created_by == "Whatsapp"):
                mensagem = f"Olá {name}, voce tem um horario agendado dia {event_date} as {start_time}"
                update_events(id_envent, "avisos", "3")
                enviar_whatsapp(chat_id, mensagem)
