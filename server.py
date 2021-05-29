import socket
import random


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("127.0.0.1",9000))
s.listen(5)

(c,a) = s.accept()
print ("Received connection from", a)

Hello=c.recv(10000).decode()

print(Hello)

greetings="Greetings!"
c.send((greetings+"\r\n").encode())

game=c.recv(10000).decode()
print (game)

ready="Ready For The Guess Game!"
c.send((ready+"\r\n").encode())

random_number = random.randint(1, 20)

running = 1

while running:
    guess=c.recv(10000).decode()
    guess=int(guess)
    print(guess)

    if guess <= random_number - 3:

        far_message="Far!"
        c.send((far_message+"\r\n").encode())

    if guess >= random_number + 3:

        far_message="Far!"
        c.send((far_message+"\r\n").encode())

    if guess == random_number - 2 or guess == random_number + 2 or guess == random_number + 1 or guess == random_number - 1:

        close_message="close!"
        c.send((close_message+"\r\n").encode())


    if (guess==random_number):

        correct_message="Correct!"
        c.send((correct_message+"\r\n").encode())
        running=0

c.close()