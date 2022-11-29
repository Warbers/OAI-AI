import socket
import json
import math
from AI import ai
from fuzzywuzzy import fuzz
from AI_loader import load_stop_words, load_model

BUFFER_SIZE = 1024

#with open("dataconfig.json") as conf:
#    config = json.load(conf)


def handle_question(conn):
    data = conn.recv(BUFFER_SIZE)
    question = json.loads(data)["question"]

    print(question)

    answer = oai.get_answer(question)
    
    jsonResponse = json.dumps(answer)

    conn.send(bytes(jsonResponse, "utf8"))
    conn.close()

listen_ip = "0.0.0.0" #'192.168.1.135'
listen_port = 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listen_ip, listen_port))
s.listen(1)

model = load_model()

stop_words = load_stop_words()

oai = ai(model, stop_words)

while True:
    print('Listening for client...')
    sockval = s.accept()
    conn, addr = sockval
    print('Connection address:', addr)
    handle_question(conn)