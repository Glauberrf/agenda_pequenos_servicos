	
from flask import Flask, request, jsonify
import requests
from datetime import datetime

###
from BD_manager_Mysql import inserir_acompanhamento, buscar_ultimo_chat, atualizar_acompanhamento, inserir_evento

###

app = Flask(__name__)

# 🔧 Configurações da sua instância UltraMsg
INSTANCE_ID = ""
TOKEN = ""

# URL da API para enviar mensagens
API_URL = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.json
    print("🔵 DADOS RECEBIDOS:")
    print(payload)

    # Extrai a mensagem de dentro de 'data'
    data = payload.get("data", {})
    texto_recebido = data.get("body", "")
    #numero_remetente = data.get("from", "")
    chat_id = data.get("from", "")
    name = data.get("pushname", "")

    resposta = ""

    print(f"Mensagem recebida de {chat_id}: {texto_recebido}")

    # Remove sufixo "@c.us" do número
    #numero_remetente = numero_remetente.replace("@c.us", "")
    chat_id = chat_id.replace("@c.us", "")

    #Inicio do atndimento cria o registro de atendimento com status 1
    if(texto_recebido.lower() == "oi" or texto_recebido.lower() == "sim" or texto_recebido.lower() == "olá" or texto_recebido.lower() == "ola"):
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

        data = buscar_ultimo_chat(chat_id)["data_event"]
        data_formatada = data.strftime("%d/%m/%Y")

        resposta = f"Agendado para {data_formatada} as {buscar_ultimo_chat(chat_id)["time_event"]}\n obrigado !"
        
        inserir_evento(buscar_ultimo_chat(chat_id)["data_event"],buscar_ultimo_chat(chat_id)["time_event"],"00:30:00","Padão Titulo","Padrão descrição",chat_id,name,"Telegram")



    elif(texto_recebido.lower() == "quem é você?" or texto_recebido.lower() == "quem e você?"):
        resposta = f"Eu sou um Bot de agendamento!"
        #await update.message.reply_text(resposta)
    #resposta = f"Você escreveu: {texto_recebido}"

    else:
        resposta = f"Parece que você não digitou uma opção válida."

    

    # Envia a resposta
    API_URL = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    payload_resposta = {
        "token": TOKEN,
        #"to": numero_remetente,
        "to": chat_id,
        "body": resposta
    }

    r = requests.post(API_URL, data=payload_resposta)
    print("🟢 Enviando resposta:", resposta)
    print("🟡 Status da API:", r.status_code)
    print("🔴 Resposta da API:", r.text)

    return jsonify({"status": "mensagem processada"}), 200


if __name__ == '__main__':
    app.run(port=5000)
