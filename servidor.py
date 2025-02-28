import sys
sys.path.append("/home/jupyter-admin/.local/lib/python3.12/site-packages")
import bcrypt

import socket
import json
import concurrent.futures
from datetime import datetime

#=========== GLOBAL ATTRIBUTES =====================================================================================
clients = {}  
emailsList = []   

#=========== FUNCTIONS =====================================================================================

###=========== Messages function for the console
def console_Logs(mensagem):
    print(f"{mensagem}")

###=========== Messages function for the conecction wwith CLIENT
def handle_client(connection):
    while True:
        try:
            messageClient = connection.recv(4096).decode()
            if not messageClient:
                break  

            msg_json = json.loads(messageClient)
            comando = msg_json.get("comando")

            if comando == "CADASTRAR":
                username = msg_json.get("username")
                nome = msg_json.get("nome")
                senha = msg_json.get("senha")

                if not username or not nome or not senha:
                    reply = {"status": "ERRO", "mensagem": "All fields are required!"} #Msg de campos obrigatorios
                elif username in clients:
                    reply = {"status": "ERRO", "mensagem": "User already exists!"} #client já existe
                else:
                    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
                    clients[username] = {"nome": nome, "senha": senha_hash}
                    reply = {"status": "SUCESSO", "mensagem": "User Registered Sucessfully."}#client cadastrado c sucesso
                    console_Logs(f"New User Registered: {username}")

            elif comando == "LOGIN":
                username = msg_json.get("username")
                senha = msg_json.get("senha")

                if not username or not senha:
                    reply = {"status": "ERRO", "mensagem": "All fields are required!"} #Msg de campos obrigatorios
                elif username in clients and bcrypt.checkpw(senha.encode(), clients[username]["senha"]):
                    reply = {"status": "SUCESSO", "mensagem": "Logged Sucessfully."} #login c Sucesso
                    console_Logs(f"User {username} logged in!") #msg n console d server do USER logado
                else:
                    reply = {"status": "ERRO", "mensagem": "Incorrect USERNAME or PASSWORD!"}

            elif comando == "ENVIAR_EMAIL":
                remetente = msg_json.get("remetente")
                destinatario = msg_json.get("destinatario")
                assunto = msg_json.get("assunto")
                body = msg_json.get("body")

                if not remetente or not destinatario or not assunto or not body:
                    reply = {"status": "ERRO", "mensagem": "All fields are required!"} #Msg de campos obrigatorios
                elif destinatario not in clients:
                    reply = {"status": "ERRO", "mensagem": "Non-existent recipient."}#Destinatario INEXISTE
                else:
                    emailsList.append({"remetente": remetente, "destinatario": destinatario, "assunto": assunto, "corpo": body})
                    reply = {"status": "SUCESSO", "mensagem": "E-mail enviado com sucesso."}
                    clients(f"E-mail enviado de {remetente} para {destinatario}")

            elif comando == "RECEBER_EMAILS":
                username = msg_json.get("username")

                if not username:
                    reply = {"status": "ERRO", "mensagem": "Username is  required!"}
                else:
                    emails_usuario = [email for email in emailsList if email["destinatario"] == username]
                    reply = {"status": "SUCESSO", "emails": emails_usuario}
                    clients(f"User {username} recebeu {len(emails_usuario)} e-mails.")

            else:
                reply = {"status": "ERRO", "mensagem": "Command Invalid."} #commando invalido

            connection.send(json.dumps(reply).encode())

        except Exception as excp:
            clients(f"Error processing client message: {excp}")
            break

    connection.close()

#========== FUNÇÂO MAIN ===========================================================================================================
def main():
    #========== Endpoint(IP,PORTA) d SEVVER ============================================================
    ENDPOINT = ('0.0.0.0', 8080) #Recebe(Lá ele) de qualquer IP do MUNDO nessa PORTA

    #========== STARTANDO SERVER ============================================================
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as endpoint:
        endpoint.bind(ENDPOINT)
        endpoint.listen()
        console_Logs(f"Server started and listening on {ENDPOINT}...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as workers:
            while True:
                connection, address = endpoint.accept()
                console_Logs(f"New Client Conected: {address}")
                workers.submit(handle_client, connection)

#========== EXECUTANDO MAIN ===========================================================================================================
if __name__ == "__main__":
    main()