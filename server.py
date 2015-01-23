#!/usr/bin/env python

import socket
import sys
import threading

class Server(object):
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.HEADER = ' a p o c a l y p s e \n & @ # $ ! & % # % @ \n' + ' -'*9 + '\n'

    def Start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            server_sock.bind(('localhost', self.port))
        except socket.error, e:
            print 'Failed to bind socket: %s' % e
            return

        server_sock.listen(5)
        while True:
            (conn, addr) = server_sock.accept()
            print '%s:%d connected' % (addr[0], addr[1])
            t = threading.Thread(target=self.ClientThread, args=(conn, addr))
            t.start()
        server_sock.close()

    def ClientThread(self, conn, addr):
        conn.sendall(self.HEADER)

        while True:
            data = conn.recv(1024)
            if not data:
                break
            if data.startswith('/exit'):
                conn.sendall('goodbye\n')
                break
            reply = r'%s' % data
            conn.sendall(reply)

        conn.close()
        print '%s:%d disconnected' % (addr[0], addr[1])

class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def Start(self):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client_sock.connect((self.host, self.port))
        except socket.error, e:
            print 'Failed to connect: %s' % e

        while True:
            client_sock.send(raw_input('>>> '))

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '-s':
            s1 = Server('SktChatServ', 7676)
            s1.Start()
        elif sys.argv[1] == '-c':
            c1 = Client('localhost', 7676)
            c1.Start()
        else:
            print 'Invalid argument'
            sys.exit(0)
    else:
        print 'Please provide an argument'
        sys.exit(0)

if __name__  == '__main__':
    main()
