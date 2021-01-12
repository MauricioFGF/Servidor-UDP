from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import time
import random


class ServidorUDP:
    def __init__(self, endereco, porto):
        print('servidor iniciado')
        self.socket_servidor = socket(AF_INET, SOCK_DGRAM) 
        self.socket_servidor.bind((endereco, porto))
        self.pessoas={}
        self.perguntas=[]
        self.classificacao = []
        self.conexoes_cliente={}
        self.rodadas = 1
        self.resposta = ''
        self.key = 0
        self.jogostarted = False
        self.contador = 1
        self.ja_enviou = 1
        self.acabou_tempo = False

        contador = 4000
        while contador != 0 :
            Thread(target=self.receber_dados).start()
            contador-=1
            
        while True:
            Thread(target=self.envia_perguntas_e_ranque).start()
         

    # Checa se os jogadores que já estão no game optaram por iniciar a
    # partida, se sim, impossibilita qualquer outro jogador de ingressar no game.
    def permissao_entrar_partida(self):
        comprimento = 0
        for pesquisar in self.pessoas:
            if len(self.pessoas[pesquisar][1])==2:
                comprimento = 2
        if comprimento == 2:
            return False
        else: return True
            

    # Onde recebe os dados e apartir deles faz a manipulação para inicar o game.
    def receber_dados(self):
        dados,client_adress = self.socket_servidor.recvfrom(2048)
        if self.permissao_entrar_partida() == False and client_adress not in self.pessoas and self.acabou_tempo==True:
            dialogo = "\nImpossivel Participar, partida ja foi iniciada."
            self.enviar_dados(dialogo, client_adress)
        else:
            if client_adress not in self.conexoes_cliente:
                mensagem = "Bem vindo ao nosso Game de perguntas lindinho!\n\nGostaria de Participar do Game? Responda (sim) para prosseguir."
                self.enviar_dados(mensagem,client_adress)
                self.conexoes_cliente[client_adress] = 0   

            elif self.conexoes_cliente[client_adress] == 0 and dados.decode() == "sim":
                self.armazenar_dados("sim",client_adress)
                if self.conexoes_cliente[client_adress] == 0:
                    for jogador in self.pessoas:
                        self.enviar_dados("\nNumero de Jogadores Online : "+ str(len(self.pessoas)),jogador)
                    mensagem2 = "\nGostaria de Iniciar a partida? Pressione Enter.\nDepois de iniciado não haverá ingresso de mais jogadores. "
                    self.enviar_dados (mensagem2 , client_adress)
                    self.conexoes_cliente[client_adress] +=1
        
            elif self.conexoes_cliente[client_adress] == 0 and dados.decode() != "sim" :
                self.enviar_dados ("\nTudo bem, quando quiser participar digite sim.", client_adress)

            elif self.conexoes_cliente[client_adress] == 1:
                self.armazenar_dados("sim",client_adress)
                self.conexoes_cliente[client_adress] +=1
                #Envia as perguntas aos Jogadores.
                if self.contador == 1:
                    for pessoal in self.pessoas:
                        self.enviar_dados("\nJogo iniciando em 5 segundos. Pressione Enter Caso ainda não tenha pressionado.",pessoal) 
                    self.contador+=1 
                    self.jogostarted = True   

            elif self.key == 1:
                #Recebe a resposta enviada pelos jogadores e contabiliza os pontos.
                self.dar_pontuacao(dados,client_adress)

            elif self.rodadas == 7:
                #Recebe os nomes enviados pelos jogadores no final do jogo e armazena 
                # nos dados do dicionario self.pessoas de cada cliente.
                self.armazenar_dados(dados.decode(),client_adress)
                self.enviar_dados("\nEspere...",client_adress)
                
                
    # Envia as perguntas aos jogadores e no final das rodadas envia os ranques.                    
    def envia_perguntas_e_ranque(self):
        if self.jogostarted == False:
            pass
        elif self.jogostarted == True:
            #Espera 5s depois que o primeiro jogador deu play e checa quem 
            # escolheu inicar tb, se alguem não quis iniciar é removido do jogo.
            self.jogostarted = False
            if self.rodadas == 1:
                tempo = 5
                while tempo >0:
                    for jogadores in self.pessoas:
                        self.enviar_dados(str(tempo) + " Segundos",jogadores)
                    time.sleep(0.84)
                    tempo-=1 
                self.acabou_tempo = True  
                self.quantidade_perguntas() 
                for x in list(self.pessoas):
                    if len(self.pessoas[x][1])<2:
                        self.pessoas.pop(x) 
                for jogador in self.pessoas:
                    self.enviar_dados("\nNumero de Participantes : "+ str(len(self.pessoas)), jogador)
            # Envia a pergunta para todos os clientes que estão no servidor.
            if self.rodadas < 6 and self.pessoas != {}:
                if self.key == 0: 
                    pergunta_e_resposta = self.buscador_pergunta_resposta()
                    pergunta = pergunta_e_resposta[0]
                    self.resposta = pergunta_e_resposta[1]
                    mensagem4 ="\n" + str(self.rodadas) + "º Rodada\n"
                    mensagem_pronta = mensagem4 + pergunta
                    for pessoal in self.pessoas:
                        self.enviar_dados(mensagem_pronta, pessoal)
                    self.tempo = time.time() + 10
                    self.key = 1 
                    while self.tempo > time.time() and self.key == 1:
                        continue
                    # Da a pontuação negativa para quem não respondeu e envia a 
                    # mensagem que o tempo para responder acabou. 
                    if self.tempo < time.time():
                        for jogadores in self.pessoas:
                            self.enviar_dados('\nTempo Esgotado, Ninguem acertou.', jogadores)
                            if len(self.pessoas[jogadores][1])<3:
                                self.pessoas[jogadores][0] -=1
                            else:
                                self.pessoas[jogadores][1].pop(2)
                        self.key = 0 
                        self.rodadas +=1
                        self.ja_enviou =1
                        self.jogostarted =True
            # Cria o Ranking de pontos dos jogadores.
            elif self.rodadas == 6:
                self.rodadas+=1
                for players in self.pessoas:
                    self.enviar_dados("\nVocê tem 10s para digitar seu nome para o ranking!\n",players)
                self.time2 = time.time() + 10
                while self.time2 > time.time():
                    continue
                # Pega o nome dos jogadores que foram armazenados no dicionario self.pessoas e insere ele na 
                # lista de classificação dos jogadores(self.classificacao).
                for participantes in self.pessoas:
                    if len(self.pessoas[participantes][1])==3:
                        self.classificacao.append((self.pessoas[participantes][1][2], self.pessoas[participantes][0]))
                    elif len(self.pessoas[participantes][1])==2:
                        self.classificacao.append(("SemNome", self.pessoas[participantes][0]))
                self.jogostarted = True    
            # Ordena a lista de classificação self.classificacao, transforma ela em str e envia para todos os jogadores. 
            # Depois zera tudo para um novo jogo.   
            elif self.rodadas == 7:
                ranking = ""
                contador = 1
                self.classificacao.sort(key=lambda x: x[1], reverse=True)
                for pontuacoes in self.classificacao:
                    ranking +=  "      " + str(contador) +"º "+ str(pontuacoes[0]) + ": " + str(pontuacoes[1])+ " Pontos\n"
                    contador+=1
                for recebedores_do_ranking in self.pessoas:
                    self.enviar_dados("\n             RANKING\n" + ranking,recebedores_do_ranking)  
                self.pessoas = {}
                self.classificacao = []
                self.perguntas = []
                self.conexoes_cliente = {}
                self.rodadas = 1
                self.key = 0
                self.contador = 1
         

    # Armazena a pontuação dos Jogadores de acordo com a resposta.
    def dar_pontuacao(self,dados,client_adress):
        #Se a a resposta foi certa.
        if self.resposta == dados.decode():
            self.armazenar_dados("enviou", client_adress)
            self.pessoas[client_adress][0]+= 25
            self.rodadas+=1
            mensagem5 = "\nParabens vc acertou!"
            self.enviar_dados(mensagem5, client_adress)
            for jogador in self.pessoas:
                if jogador != client_adress:
                    self.enviar_dados("\nUm adversario acabou de acertar. Proxima Rodada.", jogador)
                if len(self.pessoas[jogador][1])<3:
                    self.pessoas[jogador][0] -=1
                while len(self.pessoas[jogador][1])>2:
                    self.pessoas[jogador][1].pop(2)
            self.key = 0
            self.jogostarted =True
        # Se a resposta foi errada.
        elif self.resposta != dados.decode():
            if self.ja_enviou == 1:
                self.armazenar_dados("enviou",client_adress)
                self.ja_enviou +=1
            self.pessoas[client_adress][0] -= 5
            mensagem6 = "\nResposta Errada, Tente Novamente."
            self.enviar_dados(mensagem6, client_adress)                     
                        
                               
    # Armazena as informações dos clientes em um dicionario.
    def armazenar_dados(self,dados,cliente):
        if len(self.pessoas) == 5:
            if cliente not in self.pessoas:
                resposta = "\nImpossivel Participar, Limite de jogadores atingido."
                self.conexoes_cliente[cliente] = float("-inf")
                self.enviar_dados(resposta,cliente)
            else:
                self.pessoas[cliente][1] +=[dados]
        else:
            if cliente not in self.pessoas:
                    self.pessoas[cliente] = [0,[dados]]
            else:
                self.pessoas[cliente][1] +=[dados]


    # Envia dados para os clientes.
    def enviar_dados(self,pergunta,cliente):
        self.socket_servidor.sendto(pergunta.encode(),cliente) 

 
#ENCONTRAR AS PERGUNTAS QUE ESTÃO NO ARQUIVO TXT.     

     # Cria uma lista contendo os numeros das pergunta [1,2,3...20].   
    def quantidade_perguntas(self):
        qtd_linhas = 1
        arquivos = open('Perguntas.txt', 'r')
        for linha in arquivos:
            self.perguntas.append(qtd_linhas)
            qtd_linhas+=1
            
           
    # Seleciona na lista criada acima um numero aleatorio e busca
    # no arquivo txt a pergunta.
    def buscador_pergunta_resposta(self):
        numero_da_pergunta = random.choice(self.perguntas)
        self.perguntas.remove(numero_da_pergunta)
        arquivos = open('Perguntas.txt', 'r')
        for linha in arquivos:
            if numero_da_pergunta==1:
                linha = linha.split(",")
                pergunta = linha[0]
                resposta = linha[1].rstrip("\n")
            numero_da_pergunta-=1
        return  pergunta, resposta
        
        

servidor_udp = ServidorUDP('', 8080)
