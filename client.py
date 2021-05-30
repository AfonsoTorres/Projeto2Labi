# encoding=utf-8
import os
import socket
import select
import json
import base64
import random

from common_comm import send_dict, recv_dict, sendrecv_dict
from Crypto.Cipher import AES

def main():
    tcp_s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    tcp_s.bind (("127.0.0.1", 0))

    # Ligar ao servidor
    tcp_s.connect (("127.0.0.1", 1244))

    cipherkey = os.urandom(16)
    cipherkey_tosend = str (base64.b64encode (cipherkey), 'utf8')
    cipher = AES.new (cipherkey, AES.MODE_ECB)

    request = { 'op': 'START', 'cipher': cipherkey_tosend }
    send_dict (tcp_s, request)

    name = recv_dict(tcp_s)

    user = (input ("Name: "))


    print("\nWelcome "+str(user)+"\n>>How To Play<<\nQUIT - to quit\nSTOP - to do a last guess and then quit\nInsert a Number to GUESS")

    user = cipher.encrypt (bytes("%16s" % (user), 'utf8'))
    user_tosend = str (base64.b64encode (user), 'utf8')

    request = { 'op': "START",
        'client_id': user_tosend }

    response = send_dict(tcp_s, request)

    # operação de registo deste cliente foi feita com sucesso e indicando-lhe quantas jogadas ele dispõe
    response = sendrecv_dict (tcp_s, request)

    if response['status'] == True:
        max_trys = base64.b64decode(response['max_attempts'])
        max_trys = cipher.decrypt(max_trys)
        max_trys = int (str (max_trys, 'utf-8'))

        print("\nYou have "+str(max_trys)+" trys\n")
    else:
        running = 0

    running = 1
    response = recv_dict(tcp_s)
    trys = 0
    while running:
        if(trys == max_trys):
            print("Excedeu o numero Maximo de tentativas")
            break

        data = (input ("Guess: "))

        # { "op": "QUIT" }
        if data == "QUIT":
            quit_dic = { "op" : "QUIT"}
            send_dict(tcp_s, quit_dic)

            response = recv_dict (tcp_s)

            if response['op'] == "QUIT":
                if response['status'] == True:
                    running = 0
                else:
                    print(response['error'])
        elif data == "STOP":

            number = (input ("Last Guess: "))

            stop_dict = { "op": "STOP", 
            "number": number, 
            "attempts": trys
             }

            send_dict (tcp_s, stop_dict)

            response = recv_dict (tcp_s)
            
            if response['op'] == "STOP":
                if response['status'] == True:
                    guess = base64.b64decode (response['guess'])
                    guess = cipher.decrypt (guess)
                    guess = int (str (guess, 'utf8'))

                    print("\nThe Secret Number was "+str(guess)+"\nYou did "+str(trys)+" trys")

                    running = 0  
            else:
                    print(response['error'])
            print(response)
        else:
            #{ "op": "GUESS", "number": valor numérico entre 0 e 100 }
            trys += 1           # aumenta o numero de tentativas
            data = int(data)
            data = cipher.encrypt (bytes("%16d" % (data), 'utf8'))
            data_tosend = str (base64.b64encode (data), 'utf8')

            guess_dict = { "op" : "GUESS",
                            'number' : data_tosend
            }

            send_dict (tcp_s, guess_dict)

            response = recv_dict (tcp_s)

            if response['op'] == "GUESS":

                result = response['result']

                if result == "smaller":
                    print("Too low\n")
                if result == "larger":
                    print("Too big\n")
                if result == "equals":
                    print(">You guessed right! In "+str(trys)+" trys<")
                    running = 0
    tcp_s.close()
    
main ()

            
        #print ("CLIENT - Valor Enviado %d" % (data))
        #data = cipher.encrypt (bytes("%16d" % (data), 'utf8'))
        #data_tosend = str (base64.b64encode (data), 'utf8')

        #request = { 'value': data_tosend }
        #response = sendrecv_dict (tcp_s, request)

        #data = base64.b64decode (response['value'])
        #data = cipher.decrypt (data)
        #data = int (str (data, 'utf-8'))
        #print ("CLIENT - Valor Recebido %d" % (data))