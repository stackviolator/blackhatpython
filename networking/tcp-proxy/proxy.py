import sys
import socket
import threading

# Hex filter with all printable ascii chars or if a char doesnt exists, use a .
HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

'''
Print a dump as hex and with plaintext

Example:
Input:
Python rocks\n and proxies roll

Output:
0000 50 79 74 68 6F 6E 20 72 6F 63 6B 73 0A 20 61 6E  Python rocks. an
0010 64 20 70 72 6F 78 69 65 73 20 72 6F 6C 6C        d proxies roll
'''
def hexdump(src, length=16, show=True):
    # If the string passed in is bytes, decode it
    if isinstance(src, bytes):
        src = src.decode()

    results = list()

    for i in range(0, len(src), length):
        # Get a part of the string
        word = str(src[i:i+length])

        printable = word.translate(HEX_FILTER)

        # Hex representation of the integer value of each char in the raw string
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length * 3
        # Append the hex value of the if the index of the first byte in the word, the hex value of the word and the ascii representation
        results.append(f'{i:04X} {hexa:<{hexwidth}} {printable}')

    if show:
        for line in results:
            print(line)
    else:
        return results

def receive_from(connection):
    # Creates and empty byte string that will be added to
    buffer = b''
    # Setting default timeout to be 5 - may be aggresive for overseas/ lossy networks
    # TODO: add this as a settable param (maybe)
    connection.settimeout(10)
    try:
        # Loop that reads data into the buffer until there is none left or we time out
        while True:
            data = connection.recv(4096)
            if not data:
                print("L + no data + ratio")
                break
            buffer += data
    except Exception as e:
        print(e)
        pass
    return buffer

'''
Both can be modified as the user desires

Examples for BHP:
    if you find plaintext user credentials being sent and want to try to elevate privileges on an
    application by passing in admin instead of your own username
'''
def request_handler(buffer):
    return buffer

def response_handler(buffer):
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # Create the remote connection
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # Check to see if we need to make a remote connection and request data first
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # Send the output to the response handler and then send the received buffer to the local client
        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print('[<==] Sending %d bytes to localhost.' % len(remote_buffer))
            client_socket.send(remote_buffer)

    while True:
        # Read the data from the local client
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = '[<==] Received %d bytes from localhost.' % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            # Process and send it to the remote client
            local_buffer = request_handler(remote_buffer)
            remote_socket.send(local_buffer)
            print('[<== Sent to remote]')

        # Read from the remote client
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print('[<==] Received %d bytes from remtoe' % len(remote_buffer))
            hexdump(remote_buffer)

            # Process and send it to the local client
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print('<== Sent to localhost')

        # If theres no more data, close the connections
        if not len(remote_buffer) or not len(local_buffer):
            client_socket.close()
            remote_socket.close()
            print('[*] No more data, closing connections')
            break

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    # Create a socket that binds tot he local host and listens
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('Count not bind to port %d' % local_port)
        print('[!!] Failed to listen on %s:%d' % (local_host, local_port))
        print('[!!] Check for other listening sockets and correct permissions')
        sys.exit(0)

    print('[*] Listening on %s:%d' % (local_host, local_port))
    server.listen(5)
    # When a new connection comes in, hand it off to the proxy_handler in a new thread
    # proxy_handler will do all the sending and receiving of bits for us
    while True:
        client_socket, addr = server.accept()
        # Print local conn info
        line = '> Received incoming connection from %s:%d' % (addr[0], addr[1])
        print(line)
        # Start a thread to talk to the host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print('Usage: ./proxy.py [local_host] [local_port]', end='')
        print('[remote_host] [remote_port] [receive_first]')
        print('Example: ./proxy.py 127.0.0.1 9001 10.12.132.1 9000 True')
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if 'True' in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()
