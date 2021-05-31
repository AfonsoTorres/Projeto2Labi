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

def write_on_csv(user,secret_number,max_trys,trys,result):
    #cliente; número secreto; número máximo de jogadas; número de jogadas
    #efectuadas; e o resultado obtido pelo cliente (desistência ou sucessso ou insucessso).
    with open('report.csv', 'a',newline='') as f:
                    f.write("User: "+str(user)+", Secret Number: "+str(secret_number)+", Max Trys: "+str(max_trys)+", Trys: "+str(trys)+", Result: "+str(result)+"\n")


def main():
    tcp_s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    tcp_s.bind (("127.0.0.1", 1244))

    tcp_s.listen ()
    main2(tcp_s)
def main2(tcp_s):
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

    user = user.lstrip()

    if str(user) in gammers:
        print("User already connected")
        response = { "op" : "START",
                    "status" : False,
                    "error": "Cliente existente"
            }
        response = send_dict(client_s, response)
        client_s.Close()
    else:
        max_trys_tosend = cipher.encrypt (bytes("%16d" % (max_trys), 'utf8'))
        max_trys_tosend = str (base64.b64encode (max_trys_tosend), 'utf8')
        gammers["User"] = str(user)
        response = { 'op': "START",
                    "status": True,
                    "max_attempts": max_trys_tosend,
                    }
        response = send_dict (client_s, response)
        print(gammers)

    #gammers = {"socket":[],"cipher":[],"guess":[],"max_attempts":[],"attempts":[]}

    # { "op": "START", "status": False, "error": "Cliente existente" }
   # { "op": "START", "status": True, "max_attempts": nº máximo de jogadas }
    ntrys = 0
    while 1:
        request = recv_dict (client_s)

        if request is not None:
            op = request['op']

        if op == "QUIT":
            #{ "op": "QUIT", "status": True }
            response = { 'op' : "QUIT",
                "status" : True
            }
            send_dict(client_s,response)
            write_on_csv(user,secret_number,max_trys,ntrys,"QUIT") 
            main2(tcp_s)
        elif op == "STOP":
            attempts = request['attempts']

            number = request['number']

            if int(ntrys) == int(attempts):
                if int(number) == int(secret_number):
                    print("SUCCESS")
                    number_secret = cipher.encrypt (bytes("%16d" % (secret_number), 'utf8'))
                    number_secret_tosend = str (base64.b64encode (number_secret), 'utf8')
                    response = { "op": "STOP", "status": True, "guess": number_secret_tosend }
                    send_dict(client_s,response)
                    write_on_csv(user,secret_number,max_trys,ntrys,"SUCCESS")      #user,secret_number,max_trys,trys,result)
                    main2(tcp_s)
                else:
                    print("FAILURE")
                    number_secret = cipher.encrypt (bytes("%16d" % (secret_number), 'utf8'))
                    number_secret_tosend = str (base64.b64encode (number_secret), 'utf8')
                    response = { "op": "STOP", "status": True, "guess": number_secret_tosend }
                    send_dict(client_s,response)
                    write_on_csv(user,secret_number,max_trys,ntrys,"FAILURE") 
                    main2(tcp_s)
            else:
                print(ntrys)
                print(attempts)
                print("FAILURE")
                number_secret = cipher.encrypt (bytes("%16d" % (secret_number), 'utf8'))
                number_secret_tosend = str (base64.b64encode (number_secret), 'utf8')
                response = { "op": "STOP", "status": True, "guess": number_secret_tosend }
                send_dict(client_s,response)
                write_on_csv(user,secret_number,max_trys,ntrys,"FAILURE")
                main2(tcp_s) 
        elif op == "GUESS":
            #{ "op": "GUESS", "status": True, "result": "smaller"/"larger"/"equals" }
            guessNum = -1
            if request is not None:
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
                    write_on_csv(user,secret_number,max_trys,ntrys,"SUCCESS") 
            else:
                print("Waiting for Client")
                main2(tcp_s)
        else:
            print("Waiting for jogada")
            send_dict(client_s,response)        
    client_s.close ()
    tcp_s.close ()
main ()