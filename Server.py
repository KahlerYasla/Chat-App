from base64 import decode
from email import message
from email.base64mime import header_length
from http import client
from logging import exception
from math import fabs
import os
import socket
import select

os.system('color 3')

HEADER_LENGTH=10
IP="127.0.0.1"
PORT=3755

serverSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

serverSocket.bind((IP,PORT))

serverSocket.listen()

socketList=[serverSocket]

clientsList = {}


def receiveMessage(client_socket):
    try:
        message_header=client_socket.recv(HEADER_LENGTH)
        
        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return {"header":message_header,"data":client_socket.recv(message_length)}

    except:
        return False


while True:
    read_sockets, _,exception_sockets = select.select(socketList, [], socketList)

    for notified_socket in read_sockets:
        if notified_socket == serverSocket:
            client_socket, client_address = serverSocket.accept()

            user = receiveMessage(client_socket)
            if user is False:
                continue

            socketList.append(client_socket)

            clientsList[client_socket] = user

            print(f"accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")
        
        else:
            message=receiveMessage(notified_socket)

            if message is False:
                print(f"closed connection from {clientsList[notified_socket]['data'].decode('utf-8')}")
                socketList.remove(notified_socket)
                del clientsList[notified_socket]
                continue

            user=clientsList[notified_socket]
            print(f"received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for client_socket in clientsList:
                if client_socket is not notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
    
        for notified_socket in exception_sockets:
            socketList.remove(notified_socket)
            del clientsList[notified_socket]