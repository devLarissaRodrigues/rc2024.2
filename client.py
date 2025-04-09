import socket

# Etapa 1 - Negociação via UDP
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

servidor = "localhost"
porta_udp = 5002
arquivo_desejado = input("Digite o nome do arquivo (a.txt ou b.txt): ")

mensagem = f"REQUEST,TCP,{arquivo_desejado}"
udp_socket.sendto(mensagem.encode(), (servidor, porta_udp))
resposta, _ = udp_socket.recvfrom(1024)
resposta = resposta.decode()
print(f"[UDP] Resposta do servidor: {resposta}")

# Espera algo como "RESPONSE:5001,a.txt"
try:
    _, dados = resposta.split(":")
    porta_transferencia, nome_arquivo = dados.split(",")
    porta_transferencia = int(porta_transferencia)
except ValueError:
    print("Resposta inválida do servidor.")
    udp_socket.close()
    exit()

udp_socket.close()

# Etapa 2 - Transferência via TCP
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect((servidor, porta_transferencia))
print(f"[TCP] Conectado ao servidor na porta {porta_transferencia}")

# Envia comando get
comando = f"get,{nome_arquivo}"
tcp_socket.send(comando.encode())

# Recebe dados do arquivo
conteudo = b""
while True:
    dados = tcp_socket.recv(1024)
    if not dados:
        break
    print(f"Recebido chunk de {len(dados)} bytes")
    conteudo += dados

tamanho_recebido = len(conteudo)

# Salva arquivo localmente
with open(f"baixado_{nome_arquivo}", "wb") as f:
    f.write(conteudo)

print(f"[TCP] Arquivo recebido ({tamanho_recebido} bytes) e salvo como baixado_{nome_arquivo}")

# Envia ACK
ack = f"ftcp_ack,{tamanho_recebido}"
tcp_socket.sendall(ack.encode())
print(f"[TCP] ACK enviado: {ack}")

tcp_socket.close()
print("[TCP] Conexão encerrada.")