#!/usr/bin/env python3

import select
import socket
import sys
from time import sleep

from MessageHandler import MessageHandler

class Client(object):
    def __init__(self, host, port):
        self.RUN = 1
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.settimeout(10)

        self.MsgHandle = MessageHandler()

        self.host = host
        self.port = port

        self.settings = {}

    def readConfig(self):
        with open('settings.client', 'r') as settings_file:
            lines = settings_file.readlines()

        for i, curline in enumerate(lines):
            curline = curline.strip('\n').split(':')
            try:
                self.settings[curline[0]] = curline[1]
            except IndexError:
                print('Invalid line in configuration file: %d: "%s"'%(i,''.join(curline)))
        print(self.settings)

    def acceptData(self):
        data = self.client_sock.recv(1024)

        if not data:
            print('\nDisconnected from server.')
            exit(1)

        data = data.decode('utf-8')
        print('\r%s' % data, end=' ')

    def connect(self):
        try:
            self.client_sock.connect((self.host, self.port))
        except socket.error as e:
            print('Failed to connect to %s:%s - %s' % (self.host, self.port, e))
            exit(1)

    def editConfig(self, setting, value):
        with open('settings.client', 'r') as settings_file:
            lines = settings_file.readlines()
        for i, line in enumerate(lines):
            if line.startswith(setting):
                new_line = '%s:%s\n'%(setting,value)
                lines[i] = new_line
                break
        with open('settings.client', 'w') as settings_file:
            settings_file.writelines(lines)

    def identify(self):
        # Sends client nickname to server

        if not 'nickname' in self.settings.keys(): 
            # No nick was specified in the config
            self.settings['nickname'] = 'Generick'

        identify = 'TU\'3<_f`]kq< %s' % self.settings['nickname']
        identify = identify.encode('utf-8')
        self.client_sock.sendall(identify)

    def prompt(self):
        sys.stdout.write('\r<You> ')
        sys.stdout.flush()
        
    def start(self):
        self.readConfig()
        self.connect()
        self.identify()

        while self.RUN:
            sock_list = [sys.stdin, self.client_sock]
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
                        new_nickname = data.split(' ')[1].strip('\n')
                        self.editConfig('nickname', new_nickname)
                        # Send new nickname to server
                        data = self.MsgHandle.sanitize(data)
                        self.client_sock.sendall(data)
                    else:
                        data = self.MsgHandle.sanitize(data)
                        self.client_sock.sendall(data)
            self.prompt()

def main(host, port):
    c1 = Client(host, port)
    c1.start()

if __name__  == '__main__':
    main('localhost', 7676)
