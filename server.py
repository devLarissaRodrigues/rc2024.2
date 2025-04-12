import socket
import os
import configparser
import threading

def handle_transfer(conn, addr):
    print(f"[TCP] Conexão estabelecida com {addr}")
    
    # Recebe o comando "get,arquivo"
    mensagem = conn.recv(1024).decode()
    print(f"[TCP] Comando recebido: {mensagem}")
    comando, nome_arquivo = comando.split(",")
    
    if mensagem.startswith("get,") and nome_arquivo in ['a.txt', 'b.txt']:
        
        if nome_arquivo == "a.txt":
            caminho_arquivo = FILE_A 
        else:
            caminho_arquivo = FILE_B
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
    else:
        error = "ERROR "
        
        if comando != 'get':
            error += "COMANDO INVÁLIDO"
        elif nome_arquivo not in ['a.txt', 'b.txt']:
            error += "ARQUIVO INVÁLIDO"    
        print(f"[TCP] ERROR Enviado para {addr}: {error}")
        conn.send(error.encode())
        
    try:
        ack = conn.recv(1024).decode()
        print(f"[TCP] ACK recebido do cliente: {ack}")
    except:
        print("[TCP] Erro ao receber ACK")
    finally:
        conn.close()
        print("[TCP] Conexão encerrada com o cliente")
        
def handle_connection():
        
    while True:
        mensagem_codificada, endereco = udp_socket.recvfrom(1024)
        mensagem = mensagem_codificada.decode()
        print(f"[UDP] Recebido de {endereco}: {mensagem}")
        
        
        response = ""
        comando, protocolo, nome_arquivo = mensagem.split(",")
        
        if mensagem.startswith("REQUEST,TCP,") and nome_arquivo in ['a.txt', 'b.txt']:
            resposta = f"RESPONSE:,TCP,{TCP_PORT},{nome_arquivo}"
            udp_socket.sendto(resposta.encode(), endereco)
            print(f"[UDP] Enviado: {resposta}")
            
            conn, endereco_tcp = tcp_socket.accept()
            
            #Thread TCP
            tcp_thread = threading.Thread(target=handle_transfer,  args=(conn, endereco_tcp))
            tcp_thread.daemon = True
            tcp_thread.start()
                    
        else:
            
            error = "ERROR, "
            if comando != "REQUEST":
                error += "COMANDO INVÁLIDO,,"
            elif protocolo != "TCP":
                error += "PROTOCOLO INVÁLIDO,,"
            else:
                error += "ARQUIVO INVÁLIDO,,"
            print(f"[UDP] ERROR | Enviado para {endereco}: {error}")
            udp_socket.sendto(error.encode(), endereco)

# Lê o arquivo de configuração
config = configparser.ConfigParser()
config.read("config.ini")

TCP_PORT = int(config["SERVER_CONFIG"]["TCP_PORT"])
UDP_PORT = int(config["SERVER_CONFIG"]["UDP_PORT"])
FILE_A = config["SERVER_CONFIG"]["FILE_A"]
FILE_B = config["SERVER_CONFIG"]["FILE_B"]

#Socket UDP
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("0.0.0.0", UDP_PORT))
print(f"[UDP] Servidor ouvindo na porta {UDP_PORT}...")

#Socket TCP
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind(("0.0.0.0", TCP_PORT))
tcp_socket.listen(5)
print(f"[TCP] Servidor ouvindo na porta {TCP_PORT}...")


#Thread UDP
udp_thread = threading.Thread(target=handle_connection)
udp_thread.daemon = True
udp_thread.start()

print("SERIVDOR RODANDO")


try:
    # Mantém o programa principal em execução
    while True:
        pass
except KeyboardInterrupt:
    print("CONEXÃO COM SERVIDOR ENCERRADA")
    
