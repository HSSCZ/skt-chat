#!/usr/bin/env python

import select
import socket

class Server(object):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __init__(self, name, port, buff):
        self.name = name
        self.port = port
        self.buff = buff
        self.CONN_LIST = []

        self.registered_users = {'127.0.0.1': 'TempAdmin'}
        self.HEADER = ' a p o c a l y p s e \n & @ # $ ! & % # % @ \n' + ' -'*10 + '\n'

    def start(self):
        print self.registered_users
        try:
            self.server_sock.bind(('0.0.0.0', self.port))
        except socket.error, e:
            print 'Failed to bind socket: %s' % e
            return
        self.server_sock.listen(10)
        self.CONN_LIST.append(self.server_sock)
        print 'Chat server started on port %d' % self.port

        while True:
            r_socks, w_socks, err_socks = select.select(self.CONN_LIST, [], [])

            for sock in r_socks:
                if sock == self.server_sock:
                    # If server socket is readable then we have a client trying to connect
                    conn, addr = self.server_sock.accept()
                    self.CONN_LIST.append(conn)
                    print '%s:%d connected' % addr
                    conn.sendall('Welcome to %s hosted by: \n%s' % (self.name, self.HEADER))
                    self.broadcastMsg(conn, '\n[%s:%d] has entered the room.\n' % addr)
                else:
                    # One of our client connections is readable
                    try:
                        data = sock.recv(self.buff)
                        if data:
                            self.broadcastMsg(sock, '\r<%s> %s' % (self.registered_users[sock.getpeername()[0]], data))
                        else:
                            raise Exception
                    except Exception as e:
                        print 'Client error: %s' % e
                        self.broadcastMsg(sock, '[%s:%d] has disconnected.' % addr)
                        print '%s:%d disconnected' % addr
                        self.CONN_LIST.remove(sock)
                        sock.close()
                        continue
        self.shutdown('Server is shutting down.')

    def broadcastMsg(self, sending_sock, message):
        for s in self.CONN_LIST:
            if s != self.server_sock and s != sending_sock:
                try:
                    s.sendall(message)
                except:
                    s.close()
                    self.CONN_LIST.remove(s)

    def directMsg(self, sending_sock, recv_sock, message):
        pass

    def shutdown(self, server_sock, message):
        server_sock.sendall(message)
        server_sock.close()

def main():
    s1 = Server('SktChatServ', 7676, 4096)
    s1.start()

if __name__  == '__main__':
    main()
