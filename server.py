#!/usr/bin/env python

import select
import socket
import sys

class Server(object):
    RUN = 1
    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __init__(self, name, port, buff):
        self.name = name
        self.port = port
        self.buff = buff
        self.users = {}
        self.conn_list = []

        self.header = ' -'*7 + '\n - H S S C Z - \n' + ' -'*7 + '\n'
        self.welcome = 'Welcome to %s hosted by:\n%s' % (self.name, self.header)

    def acceptConn(self):
        conn, addr = self.srv_sock.accept()
        self.conn_list.append(conn)
        conn.sendall(self.welcome)

        self.broadcastMsg(conn, '[%d] has entered the room.\n' % addr[1])
        print '%s:%d connected' % addr
        return addr

    def acceptData(self, from_sock):
        sock_user = from_sock.getpeername()[1] # Using port number as user id for now
        data = from_sock.recv(self.buff)
        if data:
            if data.startswith('/srvquit'):
                self.RUN = 0
            self.broadcastMsg(from_sock, '<%s> %s\n' % (sock_user, data.strip('\n')))
        else:
            raise Exception

    def broadcastMsg(self, from_sock, message):
        for s in self.conn_list:
            if s != self.srv_sock and s != from_sock:
                try:
                    s.sendall(message)
                except:
                    s.close()
                    self.conn_list.remove(s)

    def directMsg(self, from_sock, to_sock, msg):
        # to_sock errors, not connected
        to_sock.sendall('<%s> %s' % (from_sock.getpeername()[1], msg))

    def shutdown(self, message):
        print 'Server is shutting down.'
        self.broadcastMsg(self.srv_sock, 'Server is shutting down.\n')
        for s in self.conn_list:
            s.close()
            self.conn_list.remove(s)
        self.srv_sock.close()
        sys.exit(0)

    def start(self):
        try:
            self.srv_sock.bind(('0.0.0.0', self.port))
        except socket.error, e:
            print 'Failed to bind socket: %s' % e
            return
        self.srv_sock.listen(10)
        self.conn_list.append(self.srv_sock)

        print 'Chat server started on port %d' % self.port

        while self.RUN == 1:
            r_socks, w_socks, err_socks = select.select(self.conn_list, [], [])

            for sock in r_socks:
                if sock == self.srv_sock:
                    addr = self.acceptConn()
                else:
                    try:
                        self.acceptData(sock)
                    except Exception as e:
                        print 'Error: %s' % e
                        self.conn_list.remove(sock)
                        sock.close()

                        self.broadcastMsg(sock, '[%d] has disconnected.\n' % addr[1])
                        print '%s:%d disconnected' % addr
                        continue

        self.shutdown('Server is shutting down.')

def main():
    s1 = Server('TheGrove', 7676, 4096)
    s1.start()

if __name__  == '__main__':
    main()
