import socket

class ChatRoom(object):

    def __init__(self, name, server_sock, id):
        self.name = name
        self.server_sock = server_sock
        self.id = id
        self.connected_clients = [server_sock]

    def add_client(self, client_sock):
        try:
            self.connected_clients.append(client_sock)
            self.broadcast(client_sock, "{0} has joined {1}".format(client_sock.getpeername(), self.name))
            return True
        except Exception as e:
            print(e)
            return False

    def broadcast(self, sender, message):
        for sock in self.connected_clients:
            if sock is not self.server_sock and sock is not sender:
                try:
                    sock.send(message.encode())
                except Exception as e:
                    print("Err in {0}: {1}".format(self.name, e))
                    sock.close()
                    if sock in connected_clients:
                        connected_clients.remove(sock)
