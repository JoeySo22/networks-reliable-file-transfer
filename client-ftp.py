#1 /usr/bin/python3

import re
from select import select
import socket
from tkinter import W
# Implemented by Jose Eduardo Soto
from reliable_data_transfer import ReliableDataTransferProtocol

'''A class for encapsulating a user setting up a connection. Its called a dialogue.'''
class ClientDialogue:

    def __init__(self):
        # The dialogue holds the following messages for prompting. 
        self.dialogue = []
        self.dialogue.append('Provide Server IP: ')
        self.dialogue.append('Provide Port#: ')
        self.dialogue.append('You are now connected. Enter your commands now.\n')
        self.recv = 'Received '
        self.prompt = 'client-ftp>'
        # Connection information for dialogue
        self.server_ip = '127.0.0.1'
        self.server_port = 0
        self.dialoging = True
        # Regular expression for verifying the input. 
        self.ip_regex_pattern = re.compile('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]' +
            '?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
        self.port_regex_pattern = re.compile('^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4]'+
            '[0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$')

    def run(self):
        # Process loops for input
        self.process_user_input('ip')
        self.process_user_input('port')
        # Print for debugging
        print(str(self))
        # Start connection
        self.start_connection()
        # Start dialogue
        self.dial()
        # close connection
        self.close_connection()

    def process_user_input(self, input_type):
        user_input = ''
        valid_input = False 
        while not valid_input:
            if input_type == 'ip':
                # Prompt for ip
                user_input = input(self.dialogue[0])
                # Validates with regex expression
                valid_input = self._validate_ip(user_input)
                # Sets the IP for the session
                self.server_ip = '' if not valid_input else user_input
            if input_type == 'port':
                # Prompt for ip
                user_input = input(self.dialogue[1])
                # Validates with regex expression
                valid_input = self._validate_port(user_input)
                # Sets the port for the session
                self.server_port = int('0') if not valid_input else int(user_input)

    def start_connection(self):
        # Change to UDP. NOW IN UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket = ReliableDataTransferProtocol(sock)
        # We connect to our server
        self.socket.connect((self.server_ip, self.server_port))
        # Timeout for testing and debugging
        self.socket.settimeout(4)
        print(self.dialogue[2])

    def dial(self):
        # Loop for client cli interface
        while True:
            user_input = input(self.prompt)
            # User might input some arguments.
            command = user_input.split(' ')
            # Handle retrieve command by user. This gets the file. 
            if command[0] == 'RETR':
                # Puts together the command again for sending
                self.socket.sendall(' '.join(command).encode())
                # Process the file
                self._process_file(command[1])
            # Handle the close command
            elif command[0] == 'CLOSE':
                self.socket.sendall(' '.join(command).encode())
                # Breaks the loop and allows for the rest of the commands to complete
                break
    
    def _process_file(self, filename):
        # Signal for no such file existing
        if self.socket.recv(2) == b'NO':
            print('No such file')
            # Go back to the dialogue since there is no file. 
            return
        '''Directory for where the files should be saved. We also require to 
        write with bytes. This is what allows us to work with all possible
        file types.'''
        _file = open('./client_repo/' + filename, 'wb')
        # Flag for task below
        file_done = False
        # Length of file from server.
        header = self.socket.recv(10).decode('utf-8')
        # Keep track of the length of the file from the server
        bytes_count = int(header)
        # Keep track of the amount of data received. 
        bytes_counter = 0
        # Main retrieve loop logic 
        while not file_done:            
            # Get application data from socket
            data = self.socket.recv(1000)
            # Increment the counter.
            bytes_counter += len(data)
            '''The reasoning of these conditions is as follows: if the counter
            matches the count then we have all of the data of the file. If the
            length of the data is shorter than 1000 then it is the remaining
            data of the file. This is based on the assumption of the reliable
            data transfer.'''
            if (bytes_counter == bytes_count) or (len(data) < 1000):
                file_done = True
            # Writting the data to the file.
            _file.write(data)
        _file.flush()
        _file.close()
        print('Received ' + filename)

    def close_connection(self):
        self.socket.close()

    def _validate_ip(self, ip):
        return re.fullmatch(self.ip_regex_pattern, ip) 

    def _validate_port(self, port):
        return re.fullmatch(self.port_regex_pattern, port)

    def __str__(self) -> str:
        return 'Server IP: {0}\nServer Port: {1}'.format(self.server_ip, self.server_port)
            


def main():
    dial = ClientDialogue()
    dial.run()
    print(dial)
if __name__ == '__main__':
    main()
