import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

# How to run a command
def execute(cmd):
    # Get all bad chars out of the command
    cmd = cmd.strip()
    # If command is empty, return
    if not cmd:
        return
    # Create a new process and format with shlex, UNIX style formatting
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    # Return a decoded version of the output (raw)
    return output.decode()

# Netcat class
class NetCat:
    def __init__(self, args, buffer=None):
        # Attributes of the class
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Handler to do any action
    def run(self):
        # Two options, listen or send
        # Listen flag
        if self.args.listen:
            self.listen()
        # No listen flag
        else:
            self.send()

    # How to send data over a network
    def send(self):
        # Creating a socket object with the defined arguments
        self.socket.connect((self.args.target, self.args.port))
        # Is there anything in the buffer? If there is, send it
        if self.buffer:
            self.socket.send(self.buffer)

        # While loop with added error handling
        try:
            # Infinite loop, will be stopped with Cntl+C
            while True:
                # Initializing the bytes received and the response itself
                recv_len = 1
                response = ''
                # If there is still data left
                while recv_len:
                    # Get first 4 mb worth of data
                    data = self.socket.recv(4096)
                    # make the length received the actual length received
                    recv_len = len(data)
                    # Add what we got in the first buffer to the response
                    response += data.decode()
                    # If there is NO more data, break from the loop
                    if recv_len < 4096:
                        break

                # If we got any response
                if response:
                    # Print the output (response)
                    print(response)
                    # Prompt for user to input and send it
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())

        # When the user hits Cntl+C handle the stoppage
        except KeyboardInterrupt:
            print('User terminated')
            self.socket.close()
            sys.exit()

    # Listening (act as a server)
    def listen(self):
        # Bind the IP with the port (like a bind shell)
        self.socket.bind((self.args.target, self.args.port))
        # 5 = the amount of backlogged connections available
        # Will allow 5 connections before refusing new ones
        self.socket.listen(5)

        # When a new connection is made
        while True:
            # Accept the connection and create a new thread (multiple processes at once)
            client_socket, _ = self.socket.accept()
            # specify the handle() function as what the thread should do
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    # How to handle a connection (WE are the server)
    def handle(self, client_socket):
        # If we want to run one command, run it and send the output back to the client
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        # Dont do in class
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break

                with open(self.args.upload, 'wb') as f:
                    f.write(file_buffer)
                message = f'Saved file {self.args.upload}'
                client_socket.send(message.encode())

        # If we want to create a shell
        elif self.args.command:
            cmd_buffer = b''
            # Create an infinite loop
            while True:
                # Error handling
                try:
                    # Send the prompt to the client
                    client_socket.send(b'BHP: #> ')
                    # Read the client response until a new line
                    while not '\n' in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    # Repeatedly call the execute() function and decode the output
                    response = execute(cmd_buffer.decode())
                    # Send the output back to the client
                    if response:
                        client_socket.send(response.encode())
                    # Reset the buffer (clear the old output)
                    cmd_buffer = b''
                # Handle the error
                except Exception as e:
                    print(f'Server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BHP Net Tool', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''Example:
        netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
        netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
        netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
        echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
        netcat.py -t 192.168.1.108 -p 5555 # connect to server
    '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')

    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    nc.run()

