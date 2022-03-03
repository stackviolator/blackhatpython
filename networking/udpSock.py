import socket

targetHost = "127.0.0.1"
targetPort = 9997

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto(b"AAAABBBBCCC", (targetHost,targetPort))

data, addr = client.recvfrom(4096)

print(data.decode())
client.close()


