import paramiko

def ssh_command(ip, port, user, passwd, cmd):
    # Create a client and a connection to an ssh server
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    # Get the output of a command
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    # If there is output, display it
    if output:
        print('-----Output-----')
        for line in output:
            print(line.strip())

if __name__ == '__main__':
    import getpass

    # Get params and send to the ssh_command function
    user = input("Enter username: ")
    password = getpass.getpass()
    ip = input('Enter the ip address: ') or 'localhost'
    port = input('Enter port or <CR>: ') or 22
    cmd = input('Enter the command to run or <CR>: ') or 'id'
    ssh_command(ip, port, user, password, cmd)


