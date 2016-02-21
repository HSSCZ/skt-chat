#!/usr/bin/env python3

import select
import socket
import sys

from skt_chat import MessageHandler
from skt_chat import Settings

class Client(object):
    def __init__(self, host, port):
        '''
        Args:
        host: server host address
        port: server host port
        '''
        self.running = 1
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.settimeout(10)

        self.MsgHandle = MessageHandler(maxLength=1024)

        self.host = host
        self.port = port

        self.Config = Settings('client')

        self.input_buffer = ''

    def acceptData(self):
        ''' Accepts data from self.client_sock and prints to stdout

        Called during main loop when self.client_sock is readable
        '''
        data = self.client_sock.recv(2048)

        if not data:
            print('\nDisconnected from server.')
            exit(1)

        data = data.decode('utf-8')
        print('\r%s' % data, end='')

    def connect(self):
        ''' Attempt to connect to the server at self.host:self.port'''
        try:
            self.client_sock.connect((self.host, self.port))
        except socket.error as e:
            print('Failed to connect to %s:%s - %s' % (self.host, self.port, e))
            exit(1)


    def identify(self):
        ''' Sends client nickname to server on initial connection'''
        if not self.Config.getSetting('nickname'):
            # No nick was specified in the config
            self.Config.editSetting('nickname', 'Generick') 

        # Unique string to identify initial connection from skt-chat client
        identify = 'TU\'3<_f`]kq< %s' % self.Config.getSetting('nickname')
        identify = identify.encode('utf-8')
        self.client_sock.sendall(identify)

    def prompt(self):
        ''' Chat input prompt'''
        sys.stdout.write('\r<You> ')
        sys.stdout.flush()
        
    def run(self):
        ''' Main client function

        Connect to server and identify.
        Checks sockets for new input or new messages from the server.
        '''
        self.connect()
        self.identify()

        sock_list = [sys.stdin, self.client_sock]

        while self.running:
            r_socks, w_socks, err_socks = select.select(sock_list, [], [])

            for rs in r_socks:
                if rs == self.client_sock:
                    # If client socket is readable then we have an incoming message
                    self.acceptData()
                else:
                    # Input from stdin
                    data = sys.stdin.readline()
                    if data.startswith('/exit'):
                        # Let server know we want to disconnect
                        dc = self.MsgHandle.sanitize('/dc')
                        self.client_sock.sendall(dc)
                        self.client_sock.close()
                        print('Goodbye!')
                        exit(0)
                    if data.startswith('/nickname') or data.startswith('/nick'):
                        # Change nickname in config file
                        new_nickname = data.split(' ')[1].strip()
                        self.Config.editSetting('nickname', new_nickname)
                        # Send new nickname to server
                        data = self.MsgHandle.sanitize(data)
                        self.client_sock.sendall(data)
                    else:
                        # Regular message to be broadcast
                        data = self.MsgHandle.sanitize(data)
                        self.client_sock.sendall(data)

            self.prompt()

def main(host, port):
    c1 = Client(host, port)
    c1.run()

if __name__  == '__main__':
    main('localhost', 7676)

