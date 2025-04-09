import socket
import os
import configparser

# Lê o arquivo de configuração
config = configparser.ConfigParser()
config.read("config.ini")

TCP_PORT = int(config["SERVER_CONFIG"]["TCP_PORT"])
UDP_PORT = int(config["SERVER_CONFIG"]["UDP_PORT"])
FILE_A = config["SERVER_CONFIG"]["FILE_A"]
FILE_B = config["SERVER_CONFIG"]["FILE_B"]

# Etapa 1 - Negociação via UDP
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("", UDP_PORT))
print(f"[UDP] Servidor ouvindo na porta {UDP_PORT}...")

# Etapa 2 - Transferência via TCP
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind(("", TCP_PORT))
tcp_socket.listen(1)
print(f"[TCP] Servidor ouvindo na porta {TCP_PORT}...")

# Função para lidar com a transferência do arquivo
def handle_transfer(conn, addr):
    print(f"[TCP] Conexão estabelecida com {addr}")
    
    # Recebe o comando "get,arquivo"
    comando = conn.recv(1024).decode()
    print(f"[TCP] Comando recebido: {comando}")
    
    if comando.startswith("get,"):
        _, nome_arquivo = comando.split(",")
        caminho_arquivo = FILE_A if nome_arquivo == "a.txt" else FILE_B

        # Verifica se o arquivo existe
        if not os.path.exists(caminho_arquivo):
            erro = "Erro: arquivo não encontrado."
            print(f"[TCP] {erro}")
            conn.send(erro.encode('utf-8'))
        else:
            # Envia o conteúdo do arquivo em segmentos
            with open(caminho_arquivo, "rb") as f:
                bytes_enviados = 0
                while True:
                    dados = f.read(1024)
                    if not dados:
                        break
                    conn.sendall(dados)
                    bytes_enviados += len(dados)
            
            # Fecha o lado de escrita para sinalizar fim do envio
            conn.shutdown(socket.SHUT_WR)  # <--- Adicione esta linha
            print(f"[TCP] Enviado {bytes_enviados} bytes")

    # Recebe o ACK
    try:
        ack = conn.recv(1024).decode()
        print(f"[TCP] ACK recebido do cliente: {ack}")
    except:
        print("[TCP] Erro ao receber ACK")
    finally:
        conn.close()
        print("[TCP] Conexão encerrada com o cliente")

    
# Loop principal do servidor
while True:
    # Aguarda requisição UDP
    mensagem, endereco = udp_socket.recvfrom(1024)
    mensagem = mensagem.decode()
    print(f"[UDP] Recebido de {endereco}: {mensagem}")
    
    if mensagem.startswith("REQUEST,TCP,"):
        _, protocolo, nome_arquivo = mensagem.split(",")
        resposta = f"RESPONSE:{TCP_PORT},{nome_arquivo}"
        udp_socket.sendto(resposta.encode(), endereco)
        print(f"[UDP] Enviado: {resposta}")
    
    # Aguarda conexão TCP
    conn, addr = tcp_socket.accept()
    handle_transfer(conn, addr)
