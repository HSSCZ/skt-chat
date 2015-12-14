#!/usr/bin/env python3

import select
import socket
import sys

from MessageHandler import MessageHandler
from User import User

class Server(object):
    def __init__(self, name, port, buff):
        self.RUN = 1
        self.srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.name = name
        self.port = port
        self.buff = buff
        self.user_dict = {}
        self.conn_list = []

        self.MsgHandle = MessageHandler()

        # Welcome message sent to users on connect
        self.header = ' -'*7 + '\n -           - \n' + ' -'*7 + '\n'
        self.welcome = 'Welcome to %s hosted by:\n%s' % (self.name, self.header)
        self.welcome = self.welcome.encode('utf-8')

    def acceptConn(self):
        conn, addr = self.srv_sock.accept() # Socket object, address info (ip, port)

        # Identify user
        data = conn.recv(self.buff).decode('utf-8')
        if not data:
            print('acceptConn data recv error')
            return

        # Unique string to identify initial client connection
        if data.startswith('TU\'3<_f`]kq<'):
            self.conn_list.append(conn)
            # Client nick comes after unique string
            nickname = data.split(' ')[1]
            # Add number to nick if user with nickname already exists
            dup_count = 0
            for key in self.user_dict:
                # Nickname will have space if duplicate name ie 'user (1)'
                # Spaces not allowed in nicknames otherwise
                if nickname == key.split(' ')[0]:
                    dup_count += 1
            if dup_count:
                nickname += ' (%d)'%dup_count
            # Add user to user dict
            self.user_dict[nickname] = User(nickname, conn)
            # Send welcome message
            conn.sendall(self.welcome)
            print(self.user_dict)
        else:
            invalid_client = self.MsgHandle.sanitize('Connect using skt-chat client.\n')
            conn.sendall(invalid_client)
            conn.close()
            return

        print('\'%s\' %s:%s connected' % (nickname, addr[0], addr[1]))

        user_join = '[%s] has entered the room.\n' % nickname
        self.broadcastMsg(self.srv_sock, user_join)


    def acceptData(self, from_sock):
        ''' Accepts messages from clients, handles server commands

            Checks for commands
            If no commands sends data to other clients
        '''

        # Find which user is sending data
        for k,u in self.user_dict.items():
            if u.sock == from_sock:
                sock_user = self.user_dict[k]
                break

        sock_addr = from_sock.getpeername()

        # Recieve data
        data = from_sock.recv(self.buff).decode('utf-8')

        if data:
            # Check for server commands
            if data.startswith('/srvquit'):
                self.RUN = 0
            elif data.startswith('/nickname') or data.startswith('/nick'):
                # Need to update user dict with new nick
                sock_user.nickname = data.split(' ')[1].strip('\n')
            elif data.startswith('/users'):
                user_list = '\n'.join([x for x in self.user_dict])
                self.directMsg(sock_user, user_list)
            elif data.startswith('/dc'):
                self.conn_list.remove(from_sock)
                from_sock.close()
                self.broadcastMsg(self.srv_sock, '[%s] has disconnected.\n' % sock_user.nickname)
                print('\'%s\' %s:%s disconnected' % (sock_user.nickname, sock_addr[0], sock_addr[1]))
                self.user_dict.pop(sock_user.nickname)
            else:
                self.broadcastMsg(from_sock, '<%s> %s\n' % (sock_user.nickname, data.strip('\n')))
        else:
            return False
        return True

    def broadcastMsg(self, from_sock, message):
        # Encodes message and sends to all clients other than from_sock
        message = self.MsgHandle.sanitize(message)

        for s in self.conn_list:
            if s != self.srv_sock and s != from_sock:
                try:
                    s.sendall(message)
                except:
                    s.close()
                    self.conn_list.remove(s)

    def directMsg(self, to_user, msg, from_user=None):
        # If from_user == None then message one from the server
        if from_user:
            direct_msg = '\n<%s> %s' % (from_user.nickname, msg)
        else:
            direct_msg = '\n%s' % msg
        direct_msg = self.MsgHandle.sanitize(direct_msg)
        to_user.sock.sendall(direct_msg)

    def shutdown(self, message):
        print('Server is shutting down.')
        self.broadcastMsg(self.srv_sock, 'Server is shutting down.\n')
        for s in self.conn_list:
            s.close()
            self.conn_list.remove(s)
        self.srv_sock.close()
        sys.exit(0)

    def run(self):
        try:
            self.srv_sock.bind(('0.0.0.0', self.port))
        except socket.error as e:
            print('Failed to bind socket: %s' % e)
            return

        self.srv_sock.listen(10)
        self.conn_list.append(self.srv_sock)

        print('Chat server started on port %d' % self.port)

        while self.RUN == 1:
            # Get sockets
            r_socks, w_socks, err_socks = select.select(self.conn_list, [], [])

            for sock in r_socks:
                if sock == self.srv_sock:
                    # If server socket is readable we have an incoming connection
                    self.acceptConn()
                else:
                    if not self.acceptData(sock):
                        # User disconnected
                        addr = sock.getpeername()
                        for k,v in self.user_dict.items():
                            if v.sock == sock:
                                self.broadcastMsg(self.srv_sock, '[%s] has disconnected.\n' % v.nickname)
                                print('\'%s\' %s:%s disconnected' % (v.nickname, addr[0], addr[1]))
                                self.user_dict.pop(k)
                                break
                        self.conn_list.remove(sock)
                        sock.close()

        self.shutdown('Server is shutting down.')

def main():
    s1 = Server('skt-chat', 7676, 1024)
    s1.run()

if __name__  == '__main__':
    main()
