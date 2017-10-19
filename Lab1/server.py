import queue
import select
import socket
import sys

import chatroom


host = '0.0.0.0'
port = 8989

SOCKET_LIST = []
socket_dict = {}

def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(0)
        server.bind((host, port))
        server.listen(10)
        print("Chat server started on {0}".format(server.getsockname()))
        random = chatroom.ChatRoom(name="random", server_sock=server, id=69)
        two = chatroom.ChatRoom(name="two", server_sock=server, id=2)
    except Exception as e:
        if server:
            server.close()
        print(e)
        sys.exit(1)

    # Sockets to read from
    SOCKET_LIST.append(server)

    while 1:
        readable, writable, errs = select.select(SOCKET_LIST, [], [], 0)
        
        for sock in readable:

            if socket_dict.get(sock):
                print(socket_dict[sock])
            # A new client has connected
            if sock is server:
                clientsock, sock_addr = sock.accept()
                clientsock.setblocking(0)
                SOCKET_LIST.append(clientsock)
                socket_dict[clientsock] = "{0}".format(clientsock.getpeername())
                # random.add_client(clientsock)
                message = "[{0}:{1}] connected...".format(clientsock.getpeername()[0], clientsock.getpeername()[1])
                print(message)
                # broadcast(server, clientsock, message)
            # A client has sent some data
            else:
                data = sock.recv(4096)
                if data:
                    client_host, client_port = sock.getpeername()
                    if data.decode() == "JOIN random\n":
                        print("Connecting client to random")
                        random.add_client(sock)
                        sock.send("Connected to random".encode())
                    elif data.decode() == "JOIN two\n":
                        print("Connecting client to two")
                        two.add_client(sock)
                        sock.send("Connected to two".encode())
                    else:
                        sock.send("Couldn't connect you for some reason".encode())
                    # message = "[{0}:{1}] -> {2}".format(client_host, client_port, data.decode())
                    # print(message)
                    # print(data.decode() == "HELO\n")
                    # broadcast(server, sock, message)
                # Empty data = disconnected
                else:
                    print("[{0}:{1}] Disconnected...".format(sock.getpeername()[0], sock.getpeername()[1]))
                    if sock in SOCKET_LIST:
                        SOCKET_LIST.remove(sock)
                    broadcast(server, sock, "Client offline")   

    server.close()

def broadcast(server_sock, client_sock, message):
    """
    Broadcast to every connection except the server and the one sending the message
    """
    for sock in SOCKET_LIST:
        if sock is not server_sock and sock is not client_sock:
            try:
                sock.send(message.encode())
            except Exception as e:
                sock.close()
                if sock in SOCKET_LIST:
                    SOCKET_LIST.remove(sock)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print("\nExiting server...")
        sys.exit(1)
