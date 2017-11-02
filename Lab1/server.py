import queue
import select
import socket
import sys

from chatroom import ChatRoom
import responder


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

        response = responder.join(chatroom=chatroom, ip=HARDCODED_IP, port=port, join_id=new_client["join_id"])
        
        sock.sendall(response.encode())   

        chat_msg = "{0} has joined this chatroom".format(new_client["nickname"])
        join_notification = responder.chat(chatroom=chatroom, 
                                            client_name=new_client["nickname"], 
                                            message=chat_msg)

        print(join_notification)
        chatroom.broadcast(sender=new_client["sock"], message=join_notification)           
    else:
        print("Intent Unknown")
        sock.sendall("ERRRROROROR".encode())

def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(0)
        server.bind((host, port))
        server.listen(10)
        create_chatroom(name="General", server=server)
        create_chatroom(name="room1", server=server)
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
