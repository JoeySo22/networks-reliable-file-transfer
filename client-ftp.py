#1 /usr/bin/python3

import re
import socket

'''A class for encapsulating a user setting up a connection. Its called a dialogue.'''
class ClientDialogue:

    def __init__(self):
        # The dialogue holds the following messages for prompting. 
        self.dialogue: list[str] = []
        self.dialogue[0] = 'Provide Server IP: '
        self.dialogue[1] = 'Provide Port#: '
        self.dialogue[2] = 'You are now connected. Enter your commands now.\n'
        self.recv = 'Received '
        self.prompt = 'client-ftp>'
        # Connection information for dialogue
        self.server_ip = '127.0.0.1'
        self.server_port = -1
        self.dialoging = True
        # Regular expression for verifying the IP input. 
        self.ip_regex_pattern = re.compile('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]' +
            '?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

    def run(self):
        self.process_user_input('ip')
        self.process_user_input('port')

    def process_user_input(self, part):
        if part == 'ip':
            reg_pattern = self.ip_regex_pattern
            the_part = self.server_ip
        elif part == 'port':
            pass
        
        working = True
        while working:
            working = re.fullmatch(self.ip_regex_pattern, self.server_ip)
            self.server_ip = input(self.dialogue)

    def __str__(self) -> str:
        return 'Server IP: {0}\nServer Port: {1}'.format(self.server_ip, self.server_port)
            


def main():
    dial = ClientDialogue()
    dial.run()
    print(dial)
if __name__ == '__main__':
    main()
