import socket

class ChatRoom(object):

    def __init__(self, name, server_sock, id):
        self.name = name
        self.server_sock = server_sock
        self.id = id
        self.next_client_id = 1
        self.connected_clients = [
            {
                "nickname": "Server", 
                "sock": server_sock, 
                "join_id": 0, 
                "status": "online"
            }
        ]

    def __repr__(self):
        return "{0} ({1} online)".format(self.name, len(self.connected_clients))

    def find_client_by_name(self, client_nickname):
        for client in self.connected_clients:
            if client["nickname"] == client_nickname:
                return client
        return None

    def add_client(self, client_sock, client_nickname, broadcast_addition=False):
        try:
            existing_client = self.find_client_by_name(client_nickname)
            if existing_client is None:
                new_client = {
                    "nickname": client_nickname, 
                    "sock": client_sock,
                    "join_id": self.next_client_id,
                    "status": "online"
                    }
                self.connected_clients.append(new_client)
                self.next_client_id += 1
                if broadcast_addition:
                    self.broadcast(client_sock, 
                                    "{0} has joined {1}".format(client_sock.getpeername(), 
                                    self.name))
                return new_client
            else:
                existing_client["status"] = "online"
                #broacast maybe
                return existing_client

        except Exception as e:
            print(e)
            return None

    def remove_client(self, client_nickname):
        for client in self.connected_clients:
            if client["nickname"] == client_nickname:
                client["status"] == "offline"
                leave_message = "CHAT: {0}\nCLIENT_NAME: {1}\nMESSAGE: {1} has left this chatroom\n\n".format(
                    self.id,
                    client["nickname"],
                )   
                #self.broadcast(self.server_sock, leave_message)
                return client

    def broadcast(self, sender, message):
        for client in self.connected_clients:
            if client["sock"] is not self.server_sock and client["status"] == "online":
                try:
                    client["sock"].sendall(message.encode())
                except Exception as e:
                    print("Err in {0}: {1}".format(self.name, e))
                    client["sock"].close()
                    if client in self.connected_clients:
                        connected_clients.remove(client)
