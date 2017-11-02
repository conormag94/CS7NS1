"""
Contains some functions to generate responses in the correct formats
"""

def join(chatroom, ip, port, join_id):
    response = "JOINED_CHATROOM: {0}\nSERVER_IP: {1}\nPORT: {2}\nROOM_REF: {3}\nJOIN_ID: {4}\n".format(
        chatroom.name,
        ip,
        port,
        chatroom.id,
        join_id
    )
    return response

def chat(chatroom, client_name, message):
    response = "CHAT: {0}\nCLIENT_NAME: {1}\nMESSAGE: {2}\n\n".format(
        chatroom.name,
        client_name,
        message
    )
    return response