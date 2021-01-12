from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread


class ClienteUDP:

    def __init__(self, endereco, porta):
        sock = socket(AF_INET, SOCK_DGRAM)
        print("Pressione Enter")
        while True:
            mensagem = input()
            sock.sendto(mensagem.encode(), (endereco,porta))
            Thread(target=self.receber_dados, args=(sock,)).start()

    
    def receber_dados(self,sock):
        while True:
            dados = sock.recv(2048)
            print(dados.decode())


cliente_tcp = ClienteUDP('', 8080)
