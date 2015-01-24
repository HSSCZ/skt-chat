#!/usr/bin/env python

import select
import socket
import sys
import threading

class Server(object):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, name, port, buff):
        self.name = name
        self.port = port
        self.buff = buff
        self.HEADER = ' a p o c a l y p s e \n & @ # $ ! & % # % @ \n' + ' -'*9 + '\n'
        self.CONN_LIST = []

    def start(self):
        try:
            self.server_sock.bind(('localhost', self.port))
        except socket.error, e:
            print 'Failed to bind socket: %s' % e
            return
        self.server_sock.listen(10)
        self.CONN_LIST.append(self.server_sock)
        print 'Chat server started on port %d' % self.port

        while True:
            read_socks, write_socks, err_socks = select.select(self.CONN_LIST, [], [])

            for sock in read_socks:
                if sock == self.server_sock:
                    (conn, addr) = self.server_sock.accept()
                    self.CONN_LIST.append(conn)
                    print '%s:%d connected' % addr
                    self.broadcastMsg(conn, '[%s:%d] has entered the room.\n' % addr)
                    # t = threading.Thread(target=self.clientThread, args=(conn, addr))
                    # t.start()
                else:
                    try:
                        data = sock.recv(self.buff)
                        if data:
                            if data.startswith('/exit'):
                                raise Exception
                            self.broadcastMsg(sock, '\r<%s> %s' % (str(sock.getpeername()), data))
                    except:
                        self.broadcastMsg(sock, 'Client [%s:%d] is offline.' % addr)
                        print '%s:%d disconnected' % addr
                        sock.close()
                        self.CONN_LIST.remove(sock)
                        continue

        self.server_sock.close()

    def broadcastMsg(self, sock, message):
        for s in self.CONN_LIST:
            if s != self.server_sock and s != sock:
                try:
                    sock.sendall(message)
                except:
                    sock.close()
                    self.CONN_LIST.remove(sock)

    def clientThread(self, conn, addr):
        conn.sendall('Welcome to %s, hosted by:' % self.name) 
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
        return

class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
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
            s1 = Server('SktChatServ', 7676, 4096)
            s1.start()
        elif sys.argv[1] == '-c':
            c1 = Client('localhost', 7676)
            c1.start()
        else:
            print 'Invalid argument'
            sys.exit(0)
    else:
        print 'Please provide an argument'
        sys.exit(0)

if __name__  == '__main__':
    main()
