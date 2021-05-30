# encoding=utf-8
import socket
import json
import base64
import csv
import random

from common_comm import send_dict, recv_dict, sendrecv_dict
from Crypto.Cipher import AES

# Dicionário com a informação relativa aos clientes
gammers = {"socket":[],"cipher":[],"guess":[],"max_attempts":[],"attempts":[]}

def main ():
    tcp_s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    tcp_s.bind (("127.0.0.1", 1244))

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

    if str(user) in gammers:
        
    else:
        gammers["User"] = str(user)
        print(gammers)

    #gammers = {"socket":[],"cipher":[],"guess":[],"max_attempts":[],"attempts":[]}

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
    ntrys = 0
    while 1:
        print(secret_number)
        print(ntrys)
        request = recv_dict (client_s)
        print(request)

        op = request['op'] 

        if op == "QUIT":
            #{ "op": "QUIT", "status": True }
            response = { 'op' : "QUIT",
                "status" : True
            }
            send_dict(client_s,response)
        elif op == "STOP":
            attempts = request['attempts']
            #attempts = cipher.decrypt (attempts)
            #attempts = int (str (attempts, 'utf8'))

            number = request['number']
            #number = cipher.decrypt (number)
            #number = int (str (number, 'utf8'))

            if int(ntrys) == int(attempts):
                if int(number) == int(secret_number):
                    print("SUCCESS")
                    number_secret = cipher.encrypt (bytes("%16d" % (secret_number), 'utf8'))
                    number_secret_tosend = str (base64.b64encode (number_secret), 'utf8')
                    response = { "op": "STOP", "status": True, "guess": number_secret_tosend }
                    send_dict(client_s,response)
                else:
                    print("FAILURE")
                    number_secret = cipher.encrypt (bytes("%16d" % (secret_number), 'utf8'))
                    number_secret_tosend = str (base64.b64encode (number_secret), 'utf8')
                    response = { "op": "STOP", "status": True, "guess": number_secret_tosend }
                    send_dict(client_s,response)
            else:
                print(ntrys)
                print(attempts)
                print("FAILURE")
                number_secret = cipher.encrypt (bytes("%16d" % (secret_number), 'utf8'))
                number_secret_tosend = str (base64.b64encode (number_secret), 'utf8')
                response = { "op": "STOP", "status": True, "guess": number_secret_tosend }
                send_dict(client_s,response)
        elif op == "GUESS":
            #{ "op": "GUESS", "status": True, "result": "smaller"/"larger"/"equals" }
            guessNum = -1
            if 'number' in request.keys():
                ntrys += 1
                guessNum = base64.b64decode (request['number'])
                guessNum = cipher.decrypt (guessNum)
                guessNum = int (str (guessNum, 'utf8'))

                if guessNum < secret_number:
                    response = { 'op' : "GUESS",
                    "status" : True,
                    'result' : "smaller"
                    }
                    send_dict(client_s,response)
                    print("send")

                if guessNum > secret_number:
                    response = { 'op' : "GUESS",
                        "status" : True,
                        'result' : "larger"
                    }
                    send_dict(client_s,response)

                if guessNum == secret_number:
                    response = { 'op' : "GUESS",
                        "status" : True,
                        'result' : "equals"
                    }
                    send_dict(client_s,response)
            else:
                print("Waiting for jogada")
            
        #if op == ""
            #data = base64.b64decode (request['value'])
            #data = cipher.decrypt (data)
            #data = int (str (data, 'utf8'))
            #print ("SERVER - Valor Recebido %d" % (data))

            #data = data * 10

            #print ("SERVER - Valor Enviado %d" % (data))
            #data = cipher.encrypt (bytes("%16d" % (data), 'utf8'))
            #data_tosend = str (base64.b64encode (data), 'utf8')
            #response = { 'value': data_tosend }
            #response = send_dict (client_s, response)
        else:
            print("Waiting for jogada")
            print(response)
            send_dict(client_s,response)
    client_s.close ()
    tcp_s.close ()
main ()