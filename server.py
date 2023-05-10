import socket
import threading
import time


class Server:
    def __init__(self, host='127.0.0.1', port=55555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.clients = []
        self.nicknames = []
        self.scores = {}
        self.questions = [('What is the capital of India?', 'delhi'),
                          ('Who is the host of KBC?', 'bacchan')]
        self.current_question = -1
        self.num_players = int(input("Enter the number of players: "))

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def broadcast_question(self, question):
        for client in self.clients:
            client.send('QUESTION'.encode('ascii'))
            client.send(question.encode('ascii'))

    def handle(self, client):
        while True:
            try:
                answer = client.recv(1024).decode('ascii').lower()
                nickname = self.nicknames[self.clients.index(client)]
                if self.questions[self.current_question][1] == answer:
                    self.scores[nickname] += 1
                    self.broadcast(
                        f'{nickname} answered correctly!'.encode('ascii'))
                else:
                    self.broadcast(
                        f'{nickname} answered incorrectly!'.encode('ascii'))
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.nicknames.remove(nickname)
                self.scores.pop(nickname)
                self.broadcast(f'{nickname} left the game!'.encode('ascii'))
                break

    def receive(self):
        while len(self.clients) < self.num_players:
            client, address = self.server.accept()
            print(f"Connected with {str(address)}")

            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            self.nicknames.append(nickname)
            self.clients.append(client)
            self.scores[nickname] = 0

            print(f"Nickname of the client is {nickname}!")
            self.broadcast(f"{nickname} joined the game!".encode('ascii'))
            client.send('Connected to the server!'.encode('ascii'))

            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()

    def start_game(self):
        for question, answer in self.questions:
            self.current_question += 1
            self.broadcast_question(question)
            time.sleep(20)  # wait for answers

        winner = max(self.scores, key=self.scores.get)
        self.broadcast(
            f'The winner is {winner} with {self.scores[winner]} points'.encode('ascii'))

    def start(self):
        print("Server Started...")
        self.receive()

        print("All players connected. Starting game...")
        self.start_game()


server = Server()
server.start()
