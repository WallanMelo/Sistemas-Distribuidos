import socket
import json
import PySimpleGUI as ui
import datetime

#============ FUNÇÕES PARA CRIAÇÃO DA INTERFACE GRAFICA ========================================================================================

###============ Função p TELA DE MENU INICIAL c OPÇÔES
def screenHome():
    return [
        [ui.Text("Cliente E-mail Service BSI Online", font=("Times New Roman", 20, "bold"), text_color = "black")],
        [ui.Button("1) Conectar no Servidor")],
        [ui.Button("2) Cadastrar Conta E-mail")],
        [ui.Button("3) Acessar E-mail")],
        [ui.Text("", key="-MENU_STATUS-", size=(100, 1))]
    ]

###============ Função p Gerar TELA DE REGISTRO DE CONTA EMAIL
def screenRegister():
    return [
        [ui.Text("Cadastrar E-mail", font=("Times New Roman", 18))],
        [ui.Text("Nome Completo:"), ui.Input(key="-NOME-")],
        [ui.Text("Username:"), ui.Input(key="-USERNAME-")],
        [ui.Text("Senha:"), ui.Input(key="-SENHA-", password_char="*")],
        [ui.Button("Cadastrar E-mail"), ui.Button("Voltar")],
        [ui.Text("", key="-STATUS_REGISTER-", size=(100, 1))]
    ]

###============ Função p Gerar TELA DE LOGIN EM UMA CONTA DE EMAIL EXISTENTE
def screenLogin():
    return [
        [ui.Text("Acessar E-mail", font=("Times New Roman", 18))],
        [ui.Text("Nome Usuario:"), ui.Input(key="-USERNAME-")],
        [ui.Text("Senha:"), ui.Input(key="-SENHA-", password_char="*")],
        [ui.Button("Login"), ui.Button("Voltar")],
        [ui.Text("", key="-STATUS_LOGIN-", size=(100, 1))]
    ]

###============ Função p Gerar TELA DE BOAS VINDAS AO LOGAR EM UMA CONTA DE EMAIL EXISTENTE
def screenWelcome(username):
    return [
        [ui.Text(f"Seja Muito Bem - Vindo, {username}!!!", font=("Times New Roman", 18), key="-WELCOME-")],
        [ui.Button("Enviar E-mail")],
        [ui.Button("Receber E-mails")],
        [ui.Button("Logout")],
        [ui.Text("", key="-STATUS_EMAIL-", size=(100, 1))]
    ]


#============ FUNÇÕES DE CONECAR COM O SERVIDOR E ENVIAR MSG ================================================================================================================

#============ Enviar MSGs p Servidor ================================================================================================================
def sendMessage(conexao, comando, **info):#**info são informacões "extrass" p server sobre a MSG
    try:
        mensagem = {"comando": comando, **info}#**info são informacões "extrass" p server sobre a MSG
        conexao.send(json.dumps(mensagem).encode())
        resposta = conexao.recv(4096).decode()
        return json.loads(resposta)
    except Exception as excp:
        ui.popup(f"ERRO!!! ao ENVIAR/RECEBER MSGs: {excp}")
        return {"status": "ERRO", "mensagem": "Falha na comunicação com o servidor."}

#============ Conectar c Servidor ================================================================================================================
def conectar_servidor(ip, porta):
    try:
        conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conexao.connect((ip, int(porta)))
        return conexao
    except Exception as e:
        ui.popup(f"ERRO p Conectar c servidor: {e}")
        return None


#============ FUNÇÃO MAIN ================================================================================================================
def main():
    window = ui.Window("", screenHome()) #JANALE INICIAL
    conexao = None #Variavel de conexão p conectar com o server
    username = "" 

    try:
        while True: ##loop com todos os eventos possiveis
            button, values = window.read()

            if button == ui.WIN_CLOSED: ###Fechar a JANELA
                break

            ###============ Opção de buscar Servidor
            if button == "1) Conectar no Servidor":
                ip = ui.popup_get_text("IP d SERVER:", default_text="wallanmelo.ddns.net") #IP recebe os DADOS inseridos pelo USUARIO
                porta = ui.popup_get_text("PORTA d SERVER:", default_text="8080") #PORTA
                if ip and porta:
                    conexao = conectar_servidor(ip, porta) #Recebendo porta e ip do server
                    if conexao:
                        window["-MENU_STATUS-"].update("Serviço Disponível")
                    else:
                        window["-MENU_STATUS-"].update("Conexão c servidor DEU RUIM")

            ###============ Opção de Cadastrar conta de email
            if button == "2) Cadastrar Conta E-mail":
                window.close()
                window = ui.Window("", screenRegister())

            ###============ Opção de Acessar e-mail p fzr Login
            if button == "3) Acessar E-mail":
                window.close()
                window = ui.Window("", screenLogin())

            ###============ Interface de Cadastro de Email
            if button == "Cadastrar E-mail":
                nome = values["-NOME-"]
                username = values["-USERNAME-"]
                senha = values["-SENHA-"]
                if not nome or not username or not senha:
                    ui.popup("Todos campos são obrigatórios.")
                elif conexao:
                    resposta = sendMessage(conexao, "CADASTRAR", username=username, nome=nome, senha=senha)
                    window["-STATUS_REGISTER-"].update(resposta["mensagem"]) #Atualiza o element de text da chave STATUS_REGISTER - SE O CADSATRO TEV SUCESSO OU N

            ###============ INterface de Login
            if button == "Login":
                username = values["-USERNAME-"]
                senha = values["-SENHA-"]
                if not username or not senha:
                    ui.popup("Todos os campos são obrigatórios.")
                elif conexao:
                    resposta = sendMessage(conexao, "LOGIN", username=username, senha=senha)
                    if resposta["status"] == "SUCESSO":
                        window.close()
                        window = ui.Window("", screenWelcome(username))
                    else:
                        window["-STATUS_LOGIN-"].update(resposta["mensagem"]) #Atualiza o element de text da chave STATUS_LOGIN - SE O LOGIN TEV SUCESSO OU N

            ###============ INterface de Enviar e-mail
            if button == "Enviar E-mail":
                destinatario = ui.popup_get_text("Destinatário:")
                assunto = ui.popup_get_text("Assunto:")
                body = ui.popup_get_text("Body:")
                if not destinatario or not assunto or not body:
                    ui.popup("Todos os campos são obrigatórios.")
                elif conexao:
                    resposta = sendMessage(conexao, "ENVIAR_EMAIL", remetente=username, destinatario=destinatario, assunto=assunto, body=body)
                    window["-STATUS_EMAIL-"].update(resposta["mensagem"])

            ###============ Interface de Receber e-mails
            if button == "Receber E-mails":
                if conexao:
                    resposta = sendMessage(conexao, "RECEBER_EMAILS", username=username)
                    if resposta["status"] == "SUCESSO":
                        emails = resposta.get("emails", [])
                        if emails:
                            lista_emails = [f"{email['remetente']}: {email['assunto']} ({email['data']})" for email in emails]
                            escolha = ui.popup_get_text("E-mails recebidos:\n" + "\n".join(lista_emails) + "\n\nQual e-mail deseja ler? (Digite o número):")
                            if escolha and escolha.isdigit():
                                email = emails[int(escolha) - 1]
                                ui.popup(f"De: {email['remetente']}\nPara: {email['destinatario']}\nData: {email['data']}\nAssunto: {email['assunto']}\n\n{email['body']}")
                        else:
                            window["-STATUS_EMAIL-"].update("Nenhum e-mail!!!")

            ###============ Interface de sair do eimail ou fzr logout
            if button == "Logout":
                if conexao:
                    conexao.close() #fechando a conecxao
                    conexao = None #Atribui a conecxao
                username = ""
                window.close()
                window = ui.Window("", screenHome())
                ui.popup("Logout com SUCESSO.")

            ###============ Opção de voltar para o menu de opções inicial
            if button == "Voltar":
                window.close() ###Fechar JANELA atual e abre a JANELA inicial
                window = ui.Window("", screenHome())

    finally:
        ### SE Sair fecha a janela
        window.close()
        if conexao:
            conexao.close()


# Ponto de entrada do programa
if __name__ == "__main__":
    main()