import queue
import select
import socket
import sys


host = ''
port = 8989

def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(0)
        server.bind((host, port))
        server.listen(5)
        print("Chat server started on {0}".format(server.getsockname()))
    except Exception as e:
        if server:
            server.close()
        print(e)
        sys.exit(1)

    # Sockets to read from
    inputs = [server]

    # Sockets to write to
    outputs = []

    # Stores the messages to be sent to each client socket when they become writable
    message_queues = {}

    while inputs:
        readable, writable, errs = select.select(inputs, outputs, inputs)

        for sock in readable:
            # A new client has connected
            if sock is server:
                clientsock, sock_addr = sock.accept()
                clientsock.setblocking(0)
                inputs.append(clientsock)
                message_queues[clientsock] = queue.Queue()
                print("[{0}:{1}] Connected...".format(clientsock.getpeername()[0], clientsock.getpeername()[1]))
            # A client has sent some data
            else:
                data = sock.recv(4096)
                if data:
                    client_host, client_port = sock.getpeername()
                    print("[{0}:{1}] -> {2}".format(client_host, client_port, data.decode()))
                    message_queues[sock].put(data)
                    if sock not in outputs:
                        outputs.append(sock)
                # Empty data = disconnected
                else:
                    print("[{0}:{1}] Disconnected...".format(sock.getpeername()[0], sock.getpeername()[1]))
                    if sock in outputs:
                        outputs.remove(sock)
                    inputs.remove(sock)
                    sock.close()
                    del message_queues[sock]
        
        for sock in writable:
            try:
                message = message_queues[sock].get_nowait()
            except queue.Empty:
                outputs.remove(sock)
            else:
                sock.send(message)

        for sock in errs:
            inputs.remove(sock)
            if sock in outputs:
                outputs.remove(sock)
            sock.close()
            del message_queues[sock]
            

                

    server.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print("\nExiting server...")
        sys.exit(1)
