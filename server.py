#!/usr/bin/env python3

import select
import socket
import sys

from MessageHandler import MessageHandler
from Settings import Settings
from User import User

class Server(object):
    def __init__(self, name, port, buff):
        ''' Server init

        Args:
        name: title of server, sent to user on connect
        port: port to run server on
        buff: buffer size
        '''
        self.RUN = 1
        self.srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.name = name
        self.port = port
        self.buff = buff

        self.Config = Settings('server')

        #  { 'nickname':User object }
        # key should always match User.nickname
        self.user_dict = {}
        # List of connected sockets
        self.conn_list = []

        self.MsgHandle = MessageHandler(maxLength=768)

        # Welcome message sent to users on connect
        self.header = ' -'*7 + '\n -           - \n' + ' -'*7 + '\n'
        self.welcome = 'Welcome to %s hosted by:\n%s' % (self.name, self.header)
        self.welcome = self.welcome.encode('utf-8')

    def acceptConn(self):
        ''' Accept a new connection to the chat server.  Only allows connections
        from skt-chat clients

        Sets up a new user with nickname sent from client and socket user is on
        Users are stored in self.conn_list and self.user_dict

        Called when self.srv_sock is readable
        '''
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
            nickname = self.duplicateNicknameFix(nickname)

            # Add user to user dict
            self.user_dict[nickname] = User(nickname, conn)

            # Send welcome message
            conn.sendall(self.welcome)
        else:
            # Connection attempt from something other than skt-chat client
            invalid_client = self.MsgHandle.sanitize('Connect using skt-chat client.\n')
            conn.sendall(invalid_client)
            conn.close()
            return

        print('\'%s\' %s:%s connected' % (nickname, addr[0], addr[1]))

        user_join = '[%s] has entered the room\n' % nickname
        self.broadcastMsg(self.srv_sock, user_join)


    def acceptData(self, from_sock):
        ''' Accepts messages from clients, handles server commands

            Checks for commands
            If no commands sends data to other clients
        '''
        # Find the user that is sending data
        for k,u in self.user_dict.items():
            if u.sock == from_sock:
                sock_user = self.user_dict[k]
                sock_user_nick = k
                break

        sock_addr = sock_user.sock.getpeername()

        # Recieve data
        data = sock_user.sock.recv(self.buff).decode('utf-8')

        if data:
            # Check for server commands
            if data.startswith('/srvquit'):
                self.RUN = 0
            elif data.startswith('/nickname') or data.startswith('/nick'):
                # Change users nickname
                new_nick = data.split(' ')[1].strip()
                # Don't do anything if user is trying to change to the nick
                # they already have
                if new_nick != sock_user_nick:
                    new_nick = self.duplicateNicknameFix(new_nick)
                    sock_user.nickname = new_nick
                    # Update self.user_dict with new nickname
                    self.user_dict[new_nick] = self.user_dict.pop(sock_user_nick)
                    self.broadcastMsg(self.srv_sock, '[%s changed nickname to %s]\n'%(sock_user_nick, new_nick))

            elif data.startswith('/users'):
                # Send a list of users to sock_user
                user_list = '\n'.join([x for x in self.user_dict])
                self.directMsg(sock_user, user_list)

            elif data.startswith('/dc'):
                # Disconnect sock_user
                self.conn_list.remove(from_sock)
                from_sock.close()
                self.broadcastMsg(self.srv_sock, '[%s] has disconnected\n' % sock_user.nickname)
                print('\'%s\' %s:%s disconnected' % (sock_user.nickname, sock_addr[0], sock_addr[1]))
                self.user_dict.pop(sock_user.nickname)

            else:
                # Regular message, broadcast to everyone
                self.broadcastMsg(from_sock, '<%s> %s\n' % (sock_user.nickname, data.strip()))
        else:
            return False
        return True

    def duplicateNicknameFix(self, nickname):
        ''' Check nickname against self.user_dict keys for duplicates. If dup-
        licate nickname(s) exist then append a number to nickname

        Returns nickname
        '''
        dup_count = 0
        for key in self.user_dict:
            # Nickname will have space if duplicate name ie 'user (1)'
            # Spaces not allowed in nicknames otherwise
            if nickname == key.split(' ')[0]:
                dup_count += 1
        if dup_count:
            nickname += ' (%d)'%dup_count

        return nickname

    def broadcastMsg(self, from_sock, message):
        ''' Encodes message and sends to all clients other than from_sock

        Args:
        from_sock: socket that message was sent from
        message: message text
        '''
        message = self.MsgHandle.sanitize(message)

        for s in self.conn_list:
            if s != self.srv_sock and s != from_sock:
                try:
                    s.sendall(message)
                except:
                    s.close()
                    self.conn_list.remove(s)

    def directMsg(self, to_user, msg, from_user=None):
        ''' Handles sending private messages from one user to another or from
        the server to a single user

        Args:
        to_user: user in self.user_dict that is to receive message
        msg: text message
        from_user: user sending the message, set to None if sent from the server
        '''
        # If from_user == None then message coming from the server
        if from_user:
            direct_msg = '\n<%s> %s' % (from_user.nickname, msg)
        else:
            direct_msg = '\n%s' % msg
        direct_msg = self.MsgHandle.sanitize(direct_msg)
        to_user.sock.sendall(direct_msg)

    def shutdown(self):
        ''' Disconnect clients and shut down server'''
        print('Server is shutting down.')
        self.broadcastMsg(self.srv_sock, 'Server is shutting down.\n')
        for s in self.conn_list:
            s.close()
            self.conn_list.remove(s)
        self.srv_sock.close()
        sys.exit(0)

    def run(self):
        ''' Main server function

        Set up the server socket.  Start listening for connections, handle
        users, broadcast messages
        '''
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
                                self.broadcastMsg(self.srv_sock, '[%s] has disconnected\n' % v.nickname)
                                print('\'%s\' %s:%s disconnected' % (v.nickname, addr[0], addr[1]))
                                self.user_dict.pop(k)
                                break
                        self.conn_list.remove(sock)
                        sock.close()

        self.shutdown()

def main():
    s1 = Server('skt-chat', 7676, 1024)
    s1.run()

if __name__  == '__main__':
    main()

