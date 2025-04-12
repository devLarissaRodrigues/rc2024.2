import socket
import configparser
import time


def iniciar_conexao():
    # Etapa 1 - Negociação via UDP
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #Envia a requisição
    mensagem = f"REQUEST,TCP,{arquivo_desejado}"
    udp_socket.sendto(mensagem.encode(), (servidor, porta_udp))

    #Recebe a resosta da requisição
    resposta, _ = udp_socket.recvfrom(1024)
    resposta = resposta.decode()
    print(f"[UDP] Resposta do servidor: {resposta}")

    # Espera algo como "RESPONSE, TCP, 5001, a.txt"
    try:
        #validas dados
        comando, protocolo, porta_transferencia, nome_arquivo = resposta.split(",")
        porta_transferencia = int(porta_transferencia)
        print("[UDP] Resposta válida do servidor")
    except ValueError:
        udp_socket.close()
        print("Resposta inválida do servidor.")
        exit()

    udp_socket.close()
    return porta_transferencia

def receber_dados(porta_transferencia):    
    
    # Etapa 2 - Transferência via TCP
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((servidor, porta_transferencia))
    print(f"[TCP] Conectado ao servidor na porta {porta_transferencia}")

    # Envia comando get
    comando = f"get,{arquivo_desejado}"
    tcp_socket.send(comando.encode())

    # Recebe dados do arquivo
    conteudo = b""
    while True:
        dados = tcp_socket.recv(1024)
        if not dados:
            break
        print(f"Recebido chunk de {len(dados)} bytes")
        ack_segmento = f"Ack de segmento, recebido {len(dados)} dados"
        tcp_socket.send(ack_segmento.encode())
        conteudo += dados

    tamanho_recebido = len(conteudo)

    # Salva arquivo localmente
    with open(f"baixado_{arquivo_desejado}", "wb") as f:
        f.write(conteudo)

    print(f"[TCP] Arquivo recebido ({tamanho_recebido} bytes) e salvo como baixado_{arquivo_desejado}")

    # Envia ACK
    ack = f"[TCP] ftcp_ack,{tamanho_recebido}"
    tcp_socket.sendall(ack.encode())
    print(f"[TCP] ACK enviado: {ack}")

    tcp_socket.close()
    print("[TCP] Conexão encerrada.")

config = configparser.ConfigParser()
config.read("config.ini")

servidor = "127.0.0.1"
porta_udp = int(config["SERVER_CONFIG"]["UDP_PORT"])
arquivo_desejado = "b.txt"

porta_transferencia = iniciar_conexao()
receber_dados(porta_transferencia)