# encoding=utf-8
import socket
import json
import base64
import csv
import random

from common_comm import send_dict, recv_dict, sendrecv_dict
from Crypto.Cipher import AES

def main ():
    tcp_s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    tcp_s.bind (("127.0.0.2", 1244))

    tcp_s.listen ()

    # aceitar novos clientes
    client_s, client_addr = tcp_s.accept ()
    
    request = recv_dict (client_s)
    cipherkey = base64.b64decode (request['cipher'])
    cipher = AES.new (cipherkey, AES.MODE_ECB)
    
    #a um número aleatório entre 0 e 100
    secret_number = random.randint(0, 100) 
    #um número máximo aleatório de jogadas entre 10 e 30
    max_trys = random.randint(10,30)

    msg = "Name:"
    send_dict(client_s,msg)

    request = recv_dict (client_s)
    user = base64.b64decode (request['client_id'])
    user = cipher.decrypt (user)
    user = (str (user, 'utf8'))

    with open('report.csv', 'r', newline='') as file:
        nuser = 0
        for x in file:
            if user in x:
                nuser += 1
        if nuser>0:
            print("User Already in the System!")
            response = { "op" : "START",
                        "status" : False,
                        "error": "Cliente existente"
            }
            response = send_dict(client_s, response)
        else:
            with open('report.csv', 'a',newline='') as f:
                f.write("\nUser: "+str(user)+", Max Trys: "+str(max_trys))
                max_tryss = cipher.encrypt (bytes("%16d" % (max_trys), 'utf8'))
                max_trys_tosend = str (base64.b64encode (max_tryss), 'utf8')
                response = { 'op': "START",
                            "status": True,
                            "max_attempts": max_trys_tosend,
                            }
                response = send_dict (client_s, response)

    # { "op": "START", "status": False, "error": "Cliente existente" }
   # { "op": "START", "status": True, "max_attempts": nº máximo de jogadas }

    while 1:
        request = recv_dict (client_s)
        data = base64.b64decode (request['value'])
        data = cipher.decrypt (data)
        data = int (str (data, 'utf8'))
        print ("SERVER - Valor Recebido %d" % (data))

        data = data * 10

        print ("SERVER - Valor Enviado %d" % (data))
        data = cipher.encrypt (bytes("%16d" % (data), 'utf8'))
        data_tosend = str (base64.b64encode (data), 'utf8')
        response = { 'value': data_tosend }
        response = send_dict (client_s, response)

    client_s.close ()
    tcp_s.close ()
main ()