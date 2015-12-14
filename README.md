# skt-chat

Simple client-server chat program.

Simply run 'python server.py' and connect with 'python client.py'

By default the server runs on port 7676.  The client attempts to connect to
localhost on port 7676.

For now server port and client target and port must be changed in the source.

User commands:
    There are several commands the client can use.

    /users: Get a list of active users from the server.
    /nickname, /nick: Changes the client nickname and sends it to the server.
    /dc, /exit: Lets the server know the client is exiting, exits the client.
    /srvquit: Kills the server.

Config files:
    Configurations for client and server are stored in settings.client and
    settings.server respectively.  

    Settings are stored in a string 'setting:value' and read in to a dict.

    Server:
        No settings for server have been implemented.

    Client:
        nickname: The nickname you would like to use

The client identifies itself to the server by sending an initial message
composed of a unique strong followed by a space and the client nickname.

Issues:
    Any message the client is tpying is overwritten (but not lost) when
    the client recieves a message.

    Issues with the prompt overwriting messages from the server.

