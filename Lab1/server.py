import queue
import select
import socket
import sys

from chatroom import ChatRoom


host = '0.0.0.0'
port = 8080
student_id = "13323317"

# TODO: Change this to read the server sock ip
HARDCODED_IP = "10.62.0.18"

SOCKET_LIST = []
socket_dict = {}

CHATROOMS = {}

class TerminateServerException(Exception):
    """
    Raised when a client requests the server to shutdown.
    """
    pass

def create_chatroom(name, server):
    new_id = len(CHATROOMS)
    new_room = ChatRoom(name=name, server_sock=server, id=new_id)
    CHATROOMS[name] = new_room

def get_room_by_id(id):
    """
    Return Chatroom object with specified id
    """
    for name, room in CHATROOMS.items():
        if room.id == id:
            return room
    return None

def disconnect_client(client_name):
    for name, room in CHATROOMS.items():
        for client in room.connected_clients:
            if client["nickname"] == client_name:
                room.remove_client(client_name)

                disconnect_msg = "CHAT: {0}\nCLIENT_NAME: {1}\nMESSAGE: {1} has left this chatroom\n\n".format(
                    room.id,
                    client_name
                )
                room.broadcast(sender=room.server_sock, message=disconnect_msg)

def determine_intent(message):
    """
    Determine which action the user intends to perform.
    """
    decoded_msg = message.decode()
    if "HELO" in decoded_msg:
        return "HELO"
    elif "KILL_SERVICE" in decoded_msg:
        return "KILL"
    elif "JOIN_CHATROOM" in decoded_msg:
        return "JOIN"
    elif "LEAVE_CHATROOM" in decoded_msg:
        return "LEAVE"
    elif "CHAT" in decoded_msg:
        return "CHAT"
    elif "DISCONNECT" in decoded_msg:
        return "DISCONNECT"
    else:
        return "OTHER"

def handle_intent(data, sock):
    """
    Carry out intended client action
    """
    action = determine_intent(data)
    message = data.decode()

    if action == "KILL":
        raise TerminateServerException("Kill request received")
    elif action == "HELO":
        original_msg = message.split("HELO ")[1].strip('\n')
        response = "HELO {0}\nIP:{1}\nPort:{2}\nStudentID:{3}\n".format(
            original_msg, HARDCODED_IP, port, student_id
        )
        sock.sendall(response.encode())
    elif action == "JOIN":
        lines = message.split('\n')
        room = lines[0].split(": ")[1].strip('\n')
        nickname = lines[3].split(": ")[1].strip('\n')

        print("Connecting {0} to {1}".format(nickname, room))
        
        new_client = CHATROOMS[room].add_client(client_sock=sock, client_nickname=nickname)
        chatroom = CHATROOMS[room]

        response = "JOINED_CHATROOM: {0}\nSERVER_IP: {1}\nPORT: {2}\nROOM_REF: {3}\nJOIN_ID: {4}\n".format(
            chatroom.name,
            HARDCODED_IP,
            port,
            chatroom.id,
            new_client["join_id"]
        )

        print(response)
        sock.sendall(response.encode())   

        broadcast_msg = "CHAT: {0}\nCLIENT_NAME: {1}\nMESSAGE: {1} has joined this chatroom\n\n".format(
            chatroom.id,
            new_client["nickname"],
        )

        print(broadcast_msg)
        chatroom.broadcast(sender=new_client["sock"], message=broadcast_msg)
    elif action == "LEAVE":
        lines = message.split('\n')
        room_ref = lines[0].split(": ")[1].strip('\n')
        client_name = lines[2].split(": ")[1].strip('\n')

        room = get_room_by_id(int(room_ref))
        client_who_left = room.remove_client(client_name)
        
        leave_confirmation = "LEFT_CHATROOM: {0}\nJOIN_ID: {1}\n".format(
            room.id,
            client_who_left["join_id"]
        )

        print(leave_confirmation)
        sock.sendall(leave_confirmation.encode())

        broadcast_msg = "CHAT: {0}\nCLIENT_NAME: {1}\nMESSAGE: {1} has left this chatroom\n\n".format(
                    room.id,
                    client_who_left["nickname"],
        )

        print(broadcast_msg)
        sock.sendall(broadcast_msg.encode())
        room.broadcast(sender=room.server_sock, message=broadcast_msg)
    elif action == "CHAT":
        lines = message.split('\n')

        room_ref = lines[0].split(": ")[1].strip('\n')
        client_name = lines[2].split(": ")[1].strip('\n')
        message = lines[3].split(": ")[1].strip('\n')

        chat_msg = "CHAT: {0}\nCLIENT_NAME: {1}\nMESSAGE: {2}\n\n".format(
            room_ref,
            client_name,
            message
        )

        print(chat_msg)
        room = get_room_by_id(int(room_ref))
        room.broadcast(sender=room.server_sock, message=chat_msg)
    elif action == "DISCONNECT":
        lines = message.split('\n')
        client_name = lines[2].split(": ")[1].strip('\n')

        disconnect_client(client_name)
        SOCKET_LIST.remove(sock)
        sock.close()
    else:
        print("ERROR_CODE: 22\nERROR_DESCRIPTION: ERROR\n")
        sock.sendall("ERROR_CODE: 22\nERROR_DESCRIPTION: ERROR\n".encode())

def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(0)
        server.bind((host, port))
        server.listen(10)
        create_chatroom(name="room1", server=server)
        create_chatroom(name="room2", server=server)
        print("Chat server started on {0}".format(server.getsockname()))
        print("Available chatrooms: {0}".format(CHATROOMS))     
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

            # A new client has connected
            if sock is server:
                clientsock, sock_addr = sock.accept()
                clientsock.setblocking(0)
                SOCKET_LIST.append(clientsock)
                socket_dict[clientsock] = "{0}".format(clientsock.getpeername())
                message = "[{0}:{1}] connected...".format(clientsock.getpeername()[0], clientsock.getpeername()[1])
                print(message)
            # A client has sent some data
            else:
                data = sock.recv(4096)
                if data:
                    client_host, client_port = sock.getpeername()
                    print("------------")
                    print("<<<<<<<<<<<<")
                    print(data.decode())

                    print(">>>>>>>>>>>>")
                    handle_intent(data, sock)

                    print("------------\n")
                    
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
                sock.sendall(message.encode())
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
