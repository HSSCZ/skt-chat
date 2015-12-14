# Use to limit messages to 140 characters and encode before sending over socket
class MessageHandler(object):
    def __init__(self, maxLength=140, encoding='utf-8'):
        self.maxLength = maxLength
        self.encoding = encoding

    def sanitize(self, message):
        if len(message) > self.maxLength:
            message = message[:self.maxLength] + '\n'
        # Encode for transmission through sockets
        message = message.encode(self.encoding)
        return message
