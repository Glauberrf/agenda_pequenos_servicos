import os
from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from datetime import datetime

###
from BD_manager_Mysql import inserir_acompanhamento, buscar_ultimo_chat, atualizar_acompanhamento, inserir_evento, listar_agenda, atualizar_agenda

###

load_dotenv()

app = Flask(__name__)

# Credenciais
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)


#Funções de fluxo
def MostrarPeriodos(chat_id, name, status):
    #
    
    '''if(status == "10" or status == "null"):
        inserir_acompanhamento(chat_id, "2", name)
    
    else:
        atualizar_acompanhamento(chat_id, "status", "2")'''


    resposta = f"Qual periodo você gostaria de agendar ?\n1-Manhã\n2-Tarde\n3-Noite"
    return resposta

def MostrarHorarios(texto_recebido, chat_id):
    print("Entrou na função de consultar os horarios")
    z = ""
    try:        
        if(texto_recebido == "1"):     
            horarios = listar_agenda("periodo","manhã")            
            resposta = horarios            
            for horario in horarios:                
                z = z + str(horario['id'])+" - "+horario['data'].strftime("%d/%m/%Y")+" as "+str(horario['horario'])+"\n"
            resposta = f"Qual horario você gostaria de agendar ?\n"+z+"\n0 - Voltar"
            atualizar_acompanhamento(chat_id, "status", "4")
            print(resposta)
            return resposta
                
        elif(texto_recebido == "2"):
            horarios = listar_agenda("periodo","tarde")
            resposta = horarios
            for horario in horarios:                
                z = z + str(horario['id'])+" - "+horario['data'].strftime("%d/%m/%Y")+" as "+str(horario['horario'])+"\n"
            resposta = f"Qual horario você gostaria de agendar ?\n"+z+"\n0 - Voltar"
            atualizar_acompanhamento(chat_id, "status", "4")
            return resposta                
            
        elif(texto_recebido == "3"):
            horarios = listar_agenda("periodo","noite")
            resposta = horarios
            for horario in horarios:                
                z = z + str(horario['id'])+" - "+horario['data'].strftime("%d/%m/%Y")+" as "+str(horario['horario'])+"\n"
            resposta = f"Qual horario você gostaria de agendar ?\n"+z+"\n0 - Voltar"
            atualizar_acompanhamento(chat_id, "status", "4")
            return resposta
            
            

        
        else:
            resposta.body("Opção inválida, por favor digite um periodo válido\n1 - manhã\n2 - tarde\n3 - noite")
            return resposta
    except ValueError:
        resposta = f"Você não digitou uma opção válida"
        return resposta

###############


# ==========================
# WEBHOOK (receber mensagem)
# ==========================
@app.route("/webhook", methods=["POST"])
def webhook():
    texto_recebido = request.form.get("Body", "").strip().lower()
    name = request.form.get("ProfileName")
    sender = request.form.get("From")

    print(f"Mensagem recebida de {name}: {sender}: {texto_recebido}")

    chat_id = sender

    response = MessagingResponse()
    resposta = response.message()

    

    print(f"Mensagem recebida de {chat_id}: {texto_recebido}")

    # Remove sufixo "@c.us" do número
    #numero_remetente = numero_remetente.replace("@c.us", "")
    chat_id = chat_id.replace("@c.us", "")

    try:
        status = buscar_ultimo_chat(chat_id)['status']
    except:
        status = "null"

    print("Status: ", status)

    #Começo do atendimento (Fluxo iniciado)
    '''if(texto_recebido.lower() == "oi" or texto_recebido.lower() == "sim"):
        resposta = f"Olá! você gostaria de agendar um horário?\n Digite\n1-SIM\n2-NÃO"
        inserir_acompanhamento(chat_id, "1", name)'''
    if(texto_recebido == "2" and status == "10") :
        resposta.body("Sem problemas, qualquer coisa estou aqui")
        print("ChatID: ", chat_id)
        print("Status: ", status)
        print("Status type: ", type(status))

    #solicitar o nome
    elif(texto_recebido == "1" and  status == "10" or texto_recebido == "1" and status == "null") :

        if(status == "10" or status == "null"):
            inserir_acompanhamento(chat_id, "2", name)
            resposta.body("Por favor, informe o seu nome")
    
        else:
            atualizar_acompanhamento(chat_id, "status", "2")
            print("Por favor, informe o seu nome")
            resposta.body("Por favor, informe o seu nome")

    
    
    
    #Mostrar periodos Manhã, tarde e Noite e inserir o nome da pessoa na tabela
    elif(status == "2") :
        atualizar_acompanhamento(chat_id, "nome", texto_recebido)
        atualizar_acompanhamento(chat_id, "status", "3")
        
        print("Mostrar os periodos manhã, tarde e noite")
        resposta.body(MostrarPeriodos(chat_id, name, status))
        
        '''atualizar_acompanhamento(chat_id, "status", "2")
        resposta = f"Qual periodo você gostaria de agendar ?\n1-Manhã\n2-Tarde\n3-Noite"'''
        

    ##mostrar horarios
    elif(status == "3") :
        print("mostrar os horarios disponiveis")
        resposta.body(MostrarHorarios(texto_recebido, chat_id))
    
    #Seleção dos horarios disponiveis
    elif(texto_recebido != "0" and status == "4") :

        try:
            #converter data
            id = texto_recebido
            data_horario_agenda = listar_agenda("id",id)
            
            #print("Data Agenda: ",data_horario_agenda)
            ##print("Data agenda data: ",data_horario_agenda[0]['data'])

            #sqlite
            #data_convertida = datetime.strptime(data_horario_agenda[0]['data'], "%d/%m/%Y").strftime("%Y-%m-%d")
            #mysql
            print("Datatatata", data_horario_agenda)
            data_convertida = data_horario_agenda[0]['data'].strftime("%Y-%m-%d")
            datetime.strptime(data_convertida, "%Y-%m-%d")
            
            atualizar_acompanhamento(chat_id, "data_event", data_convertida)

            atualizar_acompanhamento(chat_id, "time_event", data_horario_agenda[0]['horario'])

            atualizar_acompanhamento(chat_id, "status", "5")

            #atualizar a disponibilidade da agenda para não aparecer depois da data ser agendada
            atualizar_agenda(int(texto_recebido), "disponibilidade", "'nao'")

            resposta.body(f"Por favor, escreva qual será o procedimento.")
            
                       
        except ValueError:
            resposta.body(f"A data que você digitou não está no formato correto.\nDigite a data no seguinte formato dd/mm/yyyy")
        except IndexError:
            resposta.body("Nenhum evento encontrado para esse ID, por favor, selecione uma das datas que lhe enviei.")

    #-----------------------------------------------------------------------------------------------------------------------
    #Adicionar o procedimento
    elif(status == "5"):
        atualizar_acompanhamento(chat_id, "status", "10")
        data_agendada = buscar_ultimo_chat(chat_id)["data_event"]
        #data_agendada = datetime.strptime(data_agendada, "%Y-%m-%d")        
        data_agendada_formatada = data_agendada.strftime("%d/%m/%Y")

        horario_agendado = buscar_ultimo_chat(chat_id)["time_event"]

        inserir_evento(buscar_ultimo_chat(chat_id)["data_event"],buscar_ultimo_chat(chat_id)["time_event"],"00:30:00",buscar_ultimo_chat(chat_id)["nome"],texto_recebido,chat_id,buscar_ultimo_chat(chat_id)["nome"],"Whatsapp")
        resposta.body(f"Então agendamos para {data_agendada_formatada} as {horario_agendado} o seu {texto_recebido}!\nObrigado !")
       

    #voltar para priodo
    elif(texto_recebido == "0" and status == "4"):

        atualizar_acompanhamento(chat_id, "status", "3")
        resposta.body(MostrarPeriodos(chat_id, name, status))

    #Tratamento de mensagem inválida ao bot
    elif(texto_recebido.lower() == "quem é você?" or texto_recebido.lower() == "quem e você?"):
        resposta.body(f"Eu sou um Bot de agendamento!")
        #await update.message.reply_text(resposta)
    #resposta = f"Você escreveu: {texto_recebido}"

    elif(texto_recebido.lower() == "2" and buscar_ultimo_chat(chat_id)['status'] == "1"):
        resposta.body("Então tudo bem !\nSe precisar é só me chamar.")

    else:
        resposta.body("Olá, você gostaria de agendar um horario ?\n1 - Sim\n2 - Não")
    #print("Resposta do BOT: ",response)
    return str(response)


# ==========================
# ENVIO ATIVO (via API REST)
# ==========================
@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    to_number = data.get("to")
    message_text = data.get("message")

    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_text,
            to=f"whatsapp:{to_number}"
        )

        return jsonify({
            "status": "success",
            "sid": message.sid
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
