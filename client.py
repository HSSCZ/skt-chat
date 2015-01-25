#!/usr/bin/env python

import select
import socket
import sys

class Client(object):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.settimeout(5)

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        try:
            self.client_sock.connect((self.host, self.port))
        except socket.error, e:
            print 'Failed to connect: %s' % e
            return

        while True:
            sock_list = [sys.stdin, self.client_sock]
            r_socks, w_socks, err_socks = select.select(sock_list, [], [])

            for rs in r_socks:
                if rs == self.client_sock:
                    data = rs.recv(4096)
                    if not data:
                        print 'Disconnected from server.'
                        sys.exit()
                    print '>>> %s' % data
                else:
                    data = raw_input('>>> ')
                    self.client_sock.sendall(data)

def main():
    c1 = Client('localhost', 7676)
    c1.start()

if __name__  == '__main__':
    main()
