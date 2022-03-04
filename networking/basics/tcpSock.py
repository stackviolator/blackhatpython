import socket

targetHost = '127.0.0.1'
targetPort = 9998

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# establish a connection
client.connect((targetHost, targetPort))

# send data
client.send(b'balllssss')

response = client.recv(4096)

print(response.decode())
client.close()
