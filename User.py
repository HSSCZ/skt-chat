class User(object):
    def __init__(self, nickname, sock):
        ''' User init

        Args:
        nickname: user nickname
        sock: connected socket
        '''
        self.nickname = nickname
        self.sock = sock

