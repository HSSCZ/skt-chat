#!/usr/bin/env python

import select
import socket
import sys

class Client(object):
    RUN = 1
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.settimeout(5)

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def acceptData(self):
        data = self.client_sock.recv(4096)
        if not data:
            print '\nDisconnected from server.'
            sys.exit()
        print '\r%s' % data,
        self.prompt()

    def prompt(self):
        sys.stdout.write('\r<You> ')
        sys.stdout.flush()
        
    def start(self):
        try:
            self.client_sock.connect((self.host, self.port))
        except socket.error, e:
            print 'Failed to connect: %s' % e
            return

        while self.RUN == 1:
            sock_list = [sys.stdin, self.client_sock]
            r_socks, w_socks, err_socks = select.select(sock_list, [], [])

            for rs in r_socks:
                if rs == self.client_sock:
                    # If client socket is readable then we have an incoming message
                    self.acceptData()
                else:
                    data = sys.stdin.readline()
                    self.client_sock.sendall(data)
                    self.prompt()

def main():
    c1 = Client('localhost', 7676)
    c1.start()

if __name__  == '__main__':
    main()
