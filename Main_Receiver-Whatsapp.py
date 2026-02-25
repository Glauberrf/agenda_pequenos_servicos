	
from flask import Flask, request, jsonify
import requests
from datetime import datetime

###
from BD_manager_Mysql import inserir_acompanhamento, buscar_ultimo_chat, atualizar_acompanhamento, inserir_evento, listar_agenda, atualizar_agenda

###


#Funções de fluxo
def MostrarPeriodos(chat_id, name, status):
    #
    
    if(status == "10" or status == "null"):
        inserir_acompanhamento(chat_id, "2", name)
    
    else:
        atualizar_acompanhamento(chat_id, "status", "2")


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
            atualizar_acompanhamento(chat_id, "status", "3")
            return resposta
                
        elif(texto_recebido == "2"):
            horarios = listar_agenda("periodo","tarde")
            resposta = horarios
            for horario in horarios:                
                z = z + str(horario['id'])+" - "+horario['data'].strftime("%d/%m/%Y")+" as "+str(horario['horario'])+"\n"
            resposta = f"Qual horario você gostaria de agendar ?\n"+z+"\n0 - Voltar"
            atualizar_acompanhamento(chat_id, "status", "3")
            return resposta                
            
        elif(texto_recebido == "3"):
            horarios = listar_agenda("periodo","noite")
            resposta = horarios
            for horario in horarios:                
                z = z + str(horario['id'])+" - "+horario['data'].strftime("%d/%m/%Y")+" as "+str(horario['horario'])+"\n"
            resposta = f"Qual horario você gostaria de agendar ?\n"+z+"\n0 - Voltar"
            atualizar_acompanhamento(chat_id, "status", "3")
            return resposta
            
            

        
        else:
            resposta = "Opção inválida, por favor digite um periodo válido\n1 - manhã\n2 - tarde\n3 - noite"
            return resposta
    except ValueError:
        resposta = f"Você não digitou uma opção válida"
        return resposta

###############



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
        resposta = "Sem problemas, qualquer coisa estou aqui"
        print("ChatID: ", chat_id)
        print("Status: ", status)
        print("Status type: ", type(status))


    
    
    
    #Mostrar periodos Manhã, tarde e Noite
    elif(texto_recebido == "1" and  status == "10" or texto_recebido == "1" and status == "null") :
        print("Mostrar os periodos manhã, tarde e noite")
        resposta = MostrarPeriodos(chat_id, name, status)
        
        '''atualizar_acompanhamento(chat_id, "status", "2")
        resposta = f"Qual periodo você gostaria de agendar ?\n1-Manhã\n2-Tarde\n3-Noite"'''
        

    ##mostrar horarios
    elif(status == "2") :
        print("mostrar os horarios disponiveis")
        resposta = MostrarHorarios(texto_recebido, chat_id)
    
    #Seleção dos horarios disponiveis
    elif(texto_recebido != "0" and status == "3") :

        try:
            #converter data
            id = texto_recebido
            data_horario_agenda = listar_agenda("id",id)
            
            print("Data Agenda: ",data_horario_agenda)
            print("Data agenda data: ",data_horario_agenda[0]['data'])

            #sqlite
            #data_convertida = datetime.strptime(data_horario_agenda[0]['data'], "%d/%m/%Y").strftime("%Y-%m-%d")
            #mysql
            data_convertida = data_horario_agenda[0]['data'].strftime("%Y-%m-%d")
            datetime.strptime(data_convertida, "%Y-%m-%d")
            
            atualizar_acompanhamento(chat_id, "data_event", data_convertida)

            atualizar_acompanhamento(chat_id, "time_event", data_horario_agenda[0]['horario'])

            atualizar_acompanhamento(chat_id, "status", "4")

            #atualizar a disponibilidade da agenda para não aparecer depois da data ser agendada
            atualizar_agenda(int(texto_recebido), "disponibilidade", "1")

            resposta = f"Você gostaria de adicionar algum comentários ?\n1 - Sim\n2 -Não"
            
                       
        except ValueError:
            resposta = f"A data que você digitou não está no formato correto.\nDigite a data no seguinte formato dd/mm/yyyy"
        except IndexError:
            resposta = "Nenhum evento encontrado para esse ID, por favor, selecione uma das datas que lhe enviei."

    #Adicionar comentário caso a resposta seja sim para adicionar
    elif(texto_recebido == "1" and status == "4"):
       atualizar_acompanhamento(chat_id, "status", "5")
       resposta = "Por favor, escreva o seu comentário"

    #Capturando a mensagem para ser inserida no banco
    elif(status == "5"):
        atualizar_acompanhamento(chat_id, "status", "10")
        data_agendada = buscar_ultimo_chat(chat_id)["data_event"]
        #data_agendada = datetime.strptime(data_agendada, "%Y-%m-%d")        
        data_agendada_formatada = data_agendada.strftime("%d/%m/%Y")

        horario_agendado = buscar_ultimo_chat(chat_id)["time_event"]

        inserir_evento(buscar_ultimo_chat(chat_id)["data_event"],buscar_ultimo_chat(chat_id)["time_event"],"00:30:00","Padão Titulo",texto_recebido,chat_id,name,"Telegram")
        resposta = f"Então agendamos para {data_agendada_formatada} as {horario_agendado} !\nObrigado !"

    #Caso a resposta de inserir uma mensagem seja "Não"
    elif(texto_recebido == "2" and status == "4"):
       atualizar_acompanhamento(chat_id, "status", "10")
       data_agendada = buscar_ultimo_chat(chat_id)["data_event"]
       #data_agendada = datetime.strptime(data_agendada, "%Y-%m-%d")        
       data_agendada_formatada = data_agendada.strftime("%d/%m/%Y")

       horario_agendado = buscar_ultimo_chat(chat_id)["time_event"]

       inserir_evento(buscar_ultimo_chat(chat_id)["data_event"],buscar_ultimo_chat(chat_id)["time_event"],"00:30:00","Padão Titulo",texto_recebido,chat_id,name,"Telegram")
       resposta = f"Então agendamos para {data_agendada_formatada} as {horario_agendado} !\nObrigado !"
    

    #voltar para priodo
    elif(texto_recebido == "0" and status == "3"):

        atualizar_acompanhamento(chat_id, "status", "2")
        resposta = MostrarPeriodos(chat_id, name, status)  
        



    #Tratamento de mensagem inválida ao bot
    elif(texto_recebido.lower() == "quem é você?" or texto_recebido.lower() == "quem e você?"):
        resposta = f"Eu sou um Bot de agendamento!"
        #await update.message.reply_text(resposta)
    #resposta = f"Você escreveu: {texto_recebido}"

    elif(texto_recebido.lower() == "2" and status == "null" or texto_recebido.lower() == "2" and status == "10"):
        resposta = f"Então tudo bem !\nSe precisar é só me chamar."

    else:
        resposta = f"Olá, você gostaria de agendar um horario ?\n1 - Sim\n2 - Não"

    

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
