# skt-chat

Simple client-server chat program.

Usage: `python3 server.py`, `python3 client.py [host:port]`

By default the server runs on port 7676.

##### User commands:
There are several commands the client can use.

    /users: Get a list of active users from the server.
    /nickname, /nick: Changes the client nickname and sends it to the server.
    /dc, /exit: Lets the server know the client is exiting, exits the client.
    /srvquit: Kills the server.

##### Config files:
Configurations for client and server are stored in the files `settings.client`
and `settings.server` respectively.

Settings are stored in a string `setting:value` and read in to a dict.

Client:

    nickname: The nickname you would like to use
    
Server:

    No settings for server have been implemented.

The client identifies itself to the server by sending an initial message
composed of a unique string followed by a space and the client nickname.

##### Issues:
Any message the client is typing is overwritten (but not lost) when
the client recieves a message.

Issues with the prompt overwriting messages from the server.

