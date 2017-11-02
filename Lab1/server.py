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
        ip, port = sock.getpeername()
        response = "HELO {0}\nIP:{1}\nPort:{2}\nStudentID:{3}\n".format(
            original_msg, HARDCODED_IP, port, student_id
        )
        return response
    elif action == "JOIN":
        room = message.split(':')[1].strip(' ').strip('\n')
        print("Connecting client to {0}".format(room))
        CHATROOMS[room].add_client(sock)
    
        sock.send("Connected to {}\n".format(room).encode())
        print(CHATROOMS[room].connected_clients)               
    else:
        sock.send("You wanted to do something else\n".encode())

def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(0)
        server.bind((host, port))
        server.listen(10)
        create_chatroom(name="General", server=server)
        create_chatroom(name="Random", server=server)
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

            if socket_dict.get(sock):
                print(socket_dict[sock])
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

                    response = handle_intent(data, sock)
                    sock.send(response.encode())

                    print(">>>>>>>>>>>>")
                    print(response)
                    print("------------")
                    
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
