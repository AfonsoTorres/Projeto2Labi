import socket
import random
import csv

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('127.0.0.1',9000))

Hello="Hello"

s.send((Hello +"\r\n").encode())

greetings=s.recv(10000).decode()
print(greetings)

game = "Guess Game Please"
s.send((game + "\r\n") .encode())

game = s.recv(10000).decode()
print(game)


running=1
while running:
    maxtrys = random.randint(10, 30)
    print("Tem "+str(maxtrys)+" tentativas!")
    trys=0
    user = input("Insira o seu Nome:")
    while(trys<maxtrys and running==1):
        guess = input("\nEnter your guess: ")
        s.send(guess.encode())
        trys += 1

        response = s.recv(10000).decode()
        print(response)

        if response.startswith("Correct"):
            running = 0
    else:
        if(trys>=maxtrys):
            print("Excedeu o numero de tentativas!")
            running = 0

with open('report.csv', 'a', newline='') as file:
    file.write("\nUser: "+str(user)+", Trys: "+str(trys)+", Max Trys: "+str(maxtrys))

s.close()
